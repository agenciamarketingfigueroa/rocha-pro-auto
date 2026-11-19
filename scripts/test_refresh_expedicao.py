"""Confere que a atualização conserva as fichas e usa a busca nova."""
import json
import tempfile
import unittest
from pathlib import Path

from refresh_expedicao import refresh


class RefreshTest(unittest.TestCase):
    def test_preserves_embedded_kits_and_updates_search(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = root / "expedicao.html"
            template = root / "template.html"
            kits = [{"codigo": "KIT10089", "descricao": "Kit de teste", "composicao": "9015: 02 PC", "imagens": [], "pastas_fotos": []}]
            old.write_text(f"<script>const KITS = {json.dumps(kits)};\nconst OLD = true;</script>", encoding="utf-8")
            template.write_text("<script>const KITS = /*__KITS__*/ [];\nconst NEW_SEARCH = true;</script>", encoding="utf-8")
            self.assertEqual(refresh(old, template), 1)
            result = old.read_text(encoding="utf-8")
            self.assertIn('"codigo": "KIT10089"', result)
            self.assertIn("const NEW_SEARCH = true", result)
            self.assertNotIn("const OLD = true", result)

    def test_missing_source_fails_without_creating_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(FileNotFoundError):
                refresh(root / "expedicao.html", root / "template.html")
            self.assertFalse((root / "expedicao.html").exists())


if __name__ == "__main__":
    unittest.main()
