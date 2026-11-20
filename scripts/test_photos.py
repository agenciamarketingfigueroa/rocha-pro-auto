"""Regression checks for folder corrections and replaced photo originals."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from build_catalog import folder_codes, photo_map, make_thumbnails


class PhotosTest(unittest.TestCase):
    def test_annotations_are_not_kit_numbers(self):
        self.assertEqual(folder_codes("KIT320 (Foto com 2)"), ["KIT10320"])
        self.assertEqual(folder_codes("KIT60 (=KIT59)"), ["KIT10060", "KIT10059"])
        self.assertEqual(folder_codes("Kit 21 e 35"), ["KIT10021", "KIT10035"])
        self.assertEqual(folder_codes("KIT 115 - 116 - 117 - 554 - 555"), ["KIT10115", "KIT10116", "KIT10117", "KIT10554", "KIT10555"])
        self.assertEqual(folder_codes("KIT10022"), ["KIT10022"])
        for name in ["10-11-2026", "0. Kits-20261022T134400Z-1-001-comprimidas", "KIT234 (Conferir nome do kit)"]:
            self.assertEqual(folder_codes(name), [])

    def test_specific_folder_wins_and_nested_batches_are_not_reimported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ["Kit 21", "Kit 21 e 35", "10-11-2026/KIT02", "KIT234 (Conferir nome do kit)"]:
                folder = root / name
                folder.mkdir(parents=True)
                Image.new("RGB", (2, 2)).save(folder / "photo.jpg")
            with patch("build_catalog.PHOTOS", root):
                mapping, _, preferred = photo_map()
            self.assertEqual(set(mapping), {"KIT10021", "KIT10035"})
            self.assertEqual(mapping["KIT10021"][0][0].name, "Kit 21")
            self.assertEqual(preferred["KIT10021"], ["Kit 21 e 35"])

    def test_older_replacement_is_regenerated_and_url_is_safe(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / "KIT320 (Foto com 2)"
            folder.mkdir()
            original = folder / "photo.jpg"
            Image.new("RGB", (10, 10), "red").save(original)
            groups = {"KIT10320": [(folder, [original])]}
            output = root / "output"
            urls = make_thumbnails(groups, output, "assets/catalogo")
            name = Path(urls[str(original)]).name
            self.assertRegex(name, r"^[a-z0-9-]+\.webp$")
            before = (output / name).read_bytes()
            Image.new("RGB", (10, 10), "blue").save(original)
            os.utime(original, (1, 1))
            (output / "obsolete.webp").write_bytes(before)
            make_thumbnails(groups, output, "assets/catalogo")
            self.assertNotEqual((output / name).read_bytes(), before)
            self.assertFalse((output / "obsolete.webp").exists())


if __name__ == "__main__":
    unittest.main()
