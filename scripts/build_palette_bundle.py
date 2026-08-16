"""Build one offline QGIS style XML from the current cpt-city qgs package."""
import argparse, html, io, json, re, urllib.parse, urllib.request, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

PACKAGE_PAGE = "https://phillips.shef.ac.uk/pub/cpt-city/pkg"
AGENT = "CPT-City-Offline-QGIS-Builder/2.0"

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": AGENT}), timeout=120) as response: return response.read()

def discover():
    page = get(PACKAGE_PAGE).decode("utf-8", "replace")
    links = re.findall(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', page, re.I | re.S)
    href = next(html.unescape(h) for h, label in links if re.sub(r"<[^>]+>", "", label).strip().lower() == "qgs")
    match = re.search(r"version\s+([0-9]+(?:\.[0-9]+)+)", page, re.I)
    return urllib.parse.urljoin(PACKAGE_PAGE, href), match.group(1) if match else "unknown"

def build(payload, output):
    root = ET.Element("qgis_style", {"version": "1"}); ET.SubElement(root, "symbols"); ramps = ET.SubElement(root, "colorramps"); count = 0
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = sorted(n for n in archive.namelist() if n.lower().endswith(".qgs")); prefix = names[0].split("/", 1)[0] if names else ""
        for name in names:
            try:
                ramp = ET.fromstring(archive.read(name)).find("./colorramps/colorramp")
                if ramp is None: continue
                relative = name.split("/", 1)[1] if name.startswith(prefix + "/") else name
                ramp.set("name", "cpt-city/" + relative[:-4]); ramps.append(ramp); count += 1
            except (ET.ParseError, KeyError): pass
    ET.ElementTree(root).write(output, encoding="utf-8", xml_declaration=True); return count

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--archive"); parser.add_argument("--output-dir", default="cpt_city_live"); args = parser.parse_args()
    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    if args.archive: payload, version = Path(args.archive).read_bytes(), "3.3.2"
    else: url, version = discover(); payload = get(url)
    count = build(payload, out / "palettes.xml")
    (out / "bundle.json").write_text(json.dumps({"cpt_city_version": version, "palette_count": count}, indent=2), encoding="utf-8")
    print(f"Bundled {count} palettes from cpt-city {version}")

if __name__ == "__main__": main()
