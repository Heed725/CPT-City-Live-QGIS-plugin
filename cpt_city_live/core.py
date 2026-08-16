"""Network, package and catalogue logic without QGIS dependencies."""
from __future__ import annotations

import hashlib, html, json, os, re, shutil, tempfile, urllib.parse, urllib.request, zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

BASE_URL = "https://phillips.shef.ac.uk/pub/cpt-city/"
PACKAGE_URL = urllib.parse.urljoin(BASE_URL, "pkg")
USER_AGENT = "QGIS-CPT-City-Live/1.0 (+https://phillips.shef.ac.uk/pub/cpt-city/)"

@dataclass(frozen=True)
class RemotePackage:
    version: str
    url: str
    resource_id: str

@dataclass(frozen=True)
class Palette:
    key: str
    name: str
    collection: str
    relative_path: str
    color1: str
    color2: str
    stops: str
    discrete: bool

    @property
    def search_text(self):
        return f"{self.name} {self.collection} {self.relative_path}".lower()

def request_bytes(url: str, timeout: int = 90):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read(), dict(response.headers.items())

def discover_qgs_package(page_html: str, page_url: str = PACKAGE_URL) -> RemotePackage:
    """Find the qgs download by label, never by a hard-coded resource number."""
    links = re.findall(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', page_html, re.I | re.S)
    qgs_href = None
    for href, label in links:
        clean = re.sub(r"<[^>]+>", "", html.unescape(label)).strip().lower()
        if clean == "qgs":
            qgs_href = html.unescape(href)
            break
    if not qgs_href:
        raise ValueError("The cpt-city package page did not contain a qgs download link.")
    match = re.search(r"version\s+([0-9]+(?:\.[0-9]+)+)", page_html, re.I)
    version = match.group(1) if match else "unknown"
    url = urllib.parse.urljoin(page_url, qgs_href)
    match = re.search(r"/resource/packages/([^/?#]+)", url)
    return RemotePackage(version, url, match.group(1) if match else url)

def fetch_remote_package():
    body, _ = request_bytes(PACKAGE_URL, timeout=30)
    return discover_qgs_package(body.decode("utf-8", errors="replace"))

def safe_extract(zip_path: Path, destination: Path) -> Path:
    destination = destination.resolve()
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            if os.path.commonpath([destination, target]) != str(destination):
                raise ValueError("Unsafe path found in downloaded archive")
        archive.extractall(destination)
    roots = [p for p in destination.iterdir() if p.is_dir()]
    return roots[0] if len(roots) == 1 else destination

def parse_palette(path: Path, root: Path):
    ramp = ET.parse(path).find("./colorramps/colorramp")
    if ramp is None:
        return None
    props = {p.get("k", ""): p.get("v", "") for p in ramp.findall("prop")}
    relative = path.relative_to(root).as_posix()
    collection = relative.rsplit("/", 1)[0] if "/" in relative else "root"
    return Palette(relative[:-4], ramp.get("name") or path.stem, collection, relative,
                   props.get("color1", "0,0,0,255"), props.get("color2", "255,255,255,255"),
                   props.get("stops", ""), props.get("discrete", "0") == "1")

def build_index(root: Path):
    palettes = []
    for path in sorted(root.rglob("*.qgs")):
        try:
            palette = parse_palette(path, root)
            if palette:
                palettes.append(palette)
        except (ET.ParseError, OSError):
            continue
    return palettes

def sync_catalogue(data_dir: Path, force=False, progress=None):
    data_dir.mkdir(parents=True, exist_ok=True)
    state_path, index_path = data_dir / "state.json", data_dir / "index.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        state = {}
    if progress: progress("Checking the cpt-city package page…")
    remote = fetch_remote_package()
    catalogue_root = data_dir / "catalogue"
    unchanged = state.get("resource_id") == remote.resource_id and catalogue_root.exists() and index_path.exists()
    if unchanged and not force:
        palettes = [Palette(**row) for row in json.loads(index_path.read_text(encoding="utf-8"))]
        return remote, palettes, False
    if progress: progress(f"Downloading cpt-city QGIS package {remote.version}…")
    payload, headers = request_bytes(remote.url)
    digest = hashlib.sha256(payload).hexdigest()
    with tempfile.TemporaryDirectory(prefix="cpt-city-live-") as temp:
        tmp = Path(temp)
        archive_path = tmp / "catalogue.zip"
        archive_path.write_bytes(payload)
        extracted = safe_extract(archive_path, tmp / "extract")
        palettes = build_index(extracted)
        if not palettes:
            raise ValueError("No QGIS colour ramps were found in the downloaded package.")
        staged = tmp / "catalogue"
        shutil.copytree(extracted, staged)
        if catalogue_root.exists(): shutil.rmtree(catalogue_root)
        shutil.move(str(staged), str(catalogue_root))
    index_path.write_text(json.dumps([asdict(p) for p in palettes], indent=2, ensure_ascii=False), encoding="utf-8")
    state_path.write_text(json.dumps({"version": remote.version, "resource_id": remote.resource_id,
        "url": remote.url, "sha256": digest, "etag": headers.get("ETag", ""),
        "last_modified": headers.get("Last-Modified", ""), "palette_count": len(palettes)}, indent=2), encoding="utf-8")
    return remote, palettes, True

def load_local_index(data_dir: Path):
    try:
        return [Palette(**row) for row in json.loads((data_dir / "index.json").read_text(encoding="utf-8"))]
    except (OSError, ValueError, TypeError):
        return []
