import io
import tempfile
import unittest
import zipfile
from pathlib import Path

from cpt_city_live.updater import discover_svg_package, install_zip, installed_version


class UpdaterTests(unittest.TestCase):
    def test_discovery(self):
        page = '<p>version 4.5.6</p><a href="files/cpt-svg.zip">svg</a>'
        url, version = discover_svg_package(page)
        self.assertEqual(version, "4.5.6")
        self.assertTrue(url.endswith("/pkg/files/cpt-svg.zip"))

    def test_install(self):
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w") as archive:
            archive.writestr("cpt/a/test.svg", "<svg/>")
        with tempfile.TemporaryDirectory() as folder:
            plugin = Path(folder)
            count = install_zip(payload.getvalue(), plugin, "4.5.6")
            self.assertEqual(count, 1)
            self.assertEqual(installed_version(plugin), "4.5.6")
            self.assertTrue((plugin / "archives/cpt-city-new/a/test.svg").exists())


if __name__ == "__main__":
    unittest.main()
