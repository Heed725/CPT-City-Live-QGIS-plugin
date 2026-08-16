"""Safe archive discovery and replacement helpers."""
import html
import io
import json
import re
import shutil
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import urljoin

PACKAGE_PAGE = "https://phillips.shef.ac.uk/pub/cpt-city/pkg"


def discover_svg_package(page_html):
    links = re.findall(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', page_html, re.I | re.S)
    href = next(html.unescape(h) for h, label in links if re.sub(r"<[^>]+>", "", label).strip().lower() == "svg")
    match = re.search(r"version\s+([0-9]+(?:\.[0-9]+)+)", page_html, re.I)
    return urljoin(PACKAGE_PAGE + "/", href), match.group(1) if match else "unknown"


def installed_version(plugin_dir):
    path = Path(plugin_dir) / "archives" / "bundle.json"
    if not path.exists():
        return "unknown"
    return json.loads(path.read_text(encoding="utf-8")).get("cpt_city_version", "unknown")


def install_zip(payload, plugin_dir, version):
    """Validate/extract first, then replace the independent archive."""
    plugin_dir = Path(plugin_dir)
    archives = plugin_dir / "archives"
    destination = archives / "cpt-city-new"
    staging = archives / "cpt-city-new-update"
    backup = archives / "cpt-city-new-backup"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    ramps = []
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as source:
            files = [item for item in source.infolist() if not item.is_dir()]
            roots = {PurePosixPath(item.filename).parts[0] for item in files}
            strip_root = len(roots) == 1
            for item in files:
                parts = PurePosixPath(item.filename).parts
                if item.filename.startswith("/") or ".." in parts:
                    raise ValueError("Unsafe path in downloaded archive")
                relative = Path(*parts[1:]) if strip_root else Path(*parts)
                target = staging / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read(item))
                if target.suffix.lower() == ".svg":
                    ramps.append(target.relative_to(staging).as_posix())
        if not ramps:
            raise ValueError("The downloaded package contains no SVG ramps")
        if backup.exists():
            shutil.rmtree(backup)
        if destination.exists():
            destination.rename(backup)
        staging.rename(destination)
        if backup.exists():
            shutil.rmtree(backup)
        ramps.sort()
        (plugin_dir / "catalog.json").write_text(json.dumps({"version": version, "ramps": ramps}, separators=(",", ":")), encoding="utf-8")
        (archives / "bundle.json").write_text(json.dumps({"cpt_city_version": version, "palette_count": len(ramps), "archive_name": "cpt-city-new"}, indent=2), encoding="utf-8")
        return len(ramps)
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        if backup.exists() and not destination.exists():
            backup.rename(destination)
        raise
