import tempfile
import unittest
from pathlib import Path

from cpt_city_live.user_catalog import catalog_directory, load_catalog, save_ramps


class UserCatalogTests(unittest.TestCase):
    def test_saved_catalog_is_separate_and_deduplicated(self):
        with tempfile.TemporaryDirectory() as folder:
            profile = Path(folder) / "profile"
            source = Path(folder) / "source.svg"
            source.write_text("<svg/>", encoding="utf-8")
            added, total = save_ramps(profile, [("author/source.svg", source)])
            self.assertEqual((added, total), (1, 1))
            added, total = save_ramps(profile, [("author/source.svg", source)])
            self.assertEqual((added, total), (0, 1))
            records = load_catalog(profile)
            self.assertEqual(records[0]["source"], "author/source.svg")
            self.assertTrue((catalog_directory(profile) / records[0]["file"]).exists())


if __name__ == "__main__":
    unittest.main()
