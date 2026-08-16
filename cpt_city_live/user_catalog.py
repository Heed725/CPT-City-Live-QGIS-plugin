"""Persistent user-owned catalog stored outside the plugin directory."""
import hashlib
import json
import shutil
from pathlib import Path


def catalog_directory(qgis_profile_directory):
    return Path(qgis_profile_directory) / "cpt-city-new-my-catalog"


def load_catalog(qgis_profile_directory):
    root = catalog_directory(qgis_profile_directory)
    index = root / "catalog.json"
    if not index.exists():
        return []
    try:
        records = json.loads(index.read_text(encoding="utf-8")).get("ramps", [])
        return [record for record in records if (root / record["file"]).exists()]
    except (OSError, ValueError, KeyError, TypeError):
        return []


def save_ramps(qgis_profile_directory, sources):
    """Copy (display path, SVG path) pairs into the persistent user catalog."""
    root = catalog_directory(qgis_profile_directory)
    ramps_dir = root / "ramps"
    ramps_dir.mkdir(parents=True, exist_ok=True)
    records = load_catalog(qgis_profile_directory)
    known = {record["source"]: record for record in records}
    added = 0
    for source_name, svg_path in sources:
        if source_name in known:
            continue
        digest = hashlib.sha256(source_name.encode("utf-8")).hexdigest()[:16]
        relative = f"ramps/{digest}-{Path(source_name).name}"
        shutil.copy2(str(svg_path), str(root / relative))
        record = {"name": Path(source_name).stem, "source": source_name, "file": relative}
        records.append(record)
        known[source_name] = record
        added += 1
    records.sort(key=lambda record: record["source"].lower())
    (root / "catalog.json").write_text(json.dumps({"ramps": records}, indent=2), encoding="utf-8")
    return added, len(records)

