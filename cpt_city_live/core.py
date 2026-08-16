"""Pure-Python catalog indexing and CPT-City SVG parsing."""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


RGB = re.compile(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)")


def load_index(plugin_dir):
    plugin_dir = Path(plugin_dir)
    index_file = plugin_dir / "catalog.json"
    if index_file.exists():
        data = json.loads(index_file.read_text(encoding="utf-8"))
        return data.get("ramps", [])
    root = plugin_dir / "archives" / "cpt-city-new"
    return [p.relative_to(root).as_posix() for p in root.rglob("*.svg")]


def parse_offset(value):
    value = (value or "0").strip()
    return max(0.0, min(1.0, float(value[:-1]) / 100 if value.endswith("%") else float(value)))


def parse_color(value):
    value = (value or "#000000").strip()
    match = RGB.match(value)
    if match:
        return tuple(int(v) for v in match.groups())
    if value.startswith("#"):
        raw = value[1:]
        if len(raw) == 3:
            raw = "".join(c * 2 for c in raw)
        if len(raw) >= 6:
            return tuple(int(raw[i:i + 2], 16) for i in (0, 2, 4))
    raise ValueError("Unsupported SVG colour: " + value)


def parse_svg(path):
    root = ET.parse(str(path)).getroot()
    result = []
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] != "stop":
            continue
        attrs = dict(node.attrib)
        for item in attrs.get("style", "").split(";"):
            if ":" in item:
                key, value = item.split(":", 1)
                attrs.setdefault(key.strip(), value.strip())
        result.append((parse_offset(attrs.get("offset")), parse_color(attrs.get("stop-color"))))
    result.sort(key=lambda item: item[0])
    if not result:
        raise ValueError("No gradient stops were found")
    if result[0][0] > 0:
        result.insert(0, (0.0, result[0][1]))
    if result[-1][0] < 1:
        result.append((1.0, result[-1][1]))
    return result


def display_name(relative_path):
    return Path(relative_path).stem

