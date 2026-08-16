"""Download and prepare the native SVG cpt-city archive for QGIS."""
import argparse, html, io, json, re, shutil, urllib.parse, urllib.request, zipfile
from pathlib import Path, PurePosixPath

PACKAGE_PAGE = "https://phillips.shef.ac.uk/pub/cpt-city/pkg"
AGENT = "CPT-City-QGIS-Catalog-Builder/2.1"
ARCHIVE_NAME = "cpt-city-new"

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": AGENT}), timeout=120) as response: return response.read()

def discover():
    page = get(PACKAGE_PAGE).decode("utf-8", "replace")
    links = re.findall(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', page, re.I | re.S)
    href = next(html.unescape(h) for h, label in links if re.sub(r"<[^>]+>", "", label).strip().lower() == "svg")
    match = re.search(r"version\s+([0-9]+(?:\.[0-9]+)+)", page, re.I)
    return urllib.parse.urljoin(PACKAGE_PAGE, href), match.group(1) if match else "unknown"

def extract(payload, destination):
    if destination.exists(): shutil.rmtree(destination)
    destination.mkdir(parents=True)
    count = 0
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        files = [i for i in archive.infolist() if not i.is_dir()]
        roots = {PurePosixPath(i.filename).parts[0] for i in files}
        strip_root = len(roots) == 1
        for info in files:
            parts = PurePosixPath(info.filename).parts
            if info.filename.startswith("/") or ".." in parts: raise ValueError("Unsafe path in archive")
            relative = Path(*parts[1:]) if strip_root else Path(*parts)
            target = destination / relative; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(archive.read(info))
            if target.suffix.lower() == ".svg": count += 1
    return count

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--archive"); parser.add_argument("--output-dir", default="cpt_city_live/archives"); args = parser.parse_args()
    if args.archive: payload, version = Path(args.archive).read_bytes(), "3.3.2"
    else: url, version = discover(); payload = get(url)
    destination = Path(args.output_dir) / ARCHIVE_NAME
    count = extract(payload, destination)
    ramps = sorted(p.relative_to(destination).as_posix() for p in destination.rglob("*.svg"))
    (destination / "VERSION.xml").write_text(f'<version><name>{ARCHIVE_NAME}</name><version>{version}</version><ramps>{count}</ramps></version>', encoding="utf-8")
    (Path(args.output_dir) / "bundle.json").write_text(json.dumps({"cpt_city_version": version, "palette_count": count, "archive_name": ARCHIVE_NAME}, indent=2), encoding="utf-8")
    (Path(args.output_dir).parent / "catalog.json").write_text(json.dumps({"version": version, "ramps": ramps}, separators=(",", ":")), encoding="utf-8")
    print(f"Bundled {count} native SVG ramps from cpt-city {version}")

if __name__ == "__main__": main()
