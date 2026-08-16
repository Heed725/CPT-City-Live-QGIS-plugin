import io, tempfile, unittest, zipfile
from pathlib import Path
from cpt_city_live.core import build_index, build_index_from_zip, discover_qgs_package

class CoreTests(unittest.TestCase):
    def test_discovers_dynamic_qgs_link(self):
        package = discover_qgs_package('<p>collections (version 9.8.7)</p><a href="resource/packages/111">cpt</a><a href="resource/packages/999">qgs</a>')
        self.assertEqual(package.version, "9.8.7")
        self.assertTrue(package.url.endswith("/pub/cpt-city/resource/packages/999"))
        self.assertEqual(package.resource_id, "999")

    def test_indexes_qgis_style(self):
        xml = '<qgis_style version="1"><colorramps><colorramp type="gradient" name="ocean"><prop k="color1" v="1,2,3,255"/><prop k="color2" v="4,5,6,255"/><prop k="stops" v="0.5;9,8,7,255"/><prop k="discrete" v="0"/></colorramp></colorramps></qgis_style>'
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "author"; path.mkdir()
            (path / "ocean.qgs").write_text(xml, encoding="utf-8")
            palettes = build_index(Path(tmp))
        self.assertEqual(palettes[0].key, "author/ocean")

    def test_indexes_zip_without_extracting(self):
        xml = '<qgis_style version="1"><colorramps><colorramp type="gradient" name="fast"><prop k="color1" v="1,2,3,255"/><prop k="color2" v="4,5,6,255"/></colorramp></colorramps></qgis_style>'
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w") as archive:
            archive.writestr("cpt-city-qgs-9.9/author/fast.qgs", xml)
        palettes = build_index_from_zip(payload.getvalue())
        self.assertEqual(palettes[0].key, "author/fast")

if __name__ == "__main__": unittest.main()
