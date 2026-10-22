"""Check imported counts, privacy boundary, and representative photo links."""
import json
import sys
from pathlib import Path

from build_catalog import load_products

root = Path(__file__).resolve().parents[1]
products = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\Users\Felipe\Desktop\Lista de Produtos (Rocha Pro Auto).xls")
original = load_products(products)
expected = {p["Código"].strip() for p in original if p["Situação"].strip() == "Ativo"}
js = (root / "data" / "catalogo-publico.js").read_text(encoding="utf-8")
catalog = json.loads(js.removeprefix("window.ROCHAPRO_CATALOG = ").removesuffix(";\n"))
assert {p["codigo"] for p in catalog} == expected
assert len(catalog) == len(expected)
assert all(set(p) == {"codigo", "nome", "descricao", "montadoras", "funcoes", "imagens"} for p in catalog)
assert sum(bool(p["descricao"]) for p in catalog) == 19
tracker = next(p for p in catalog if p["codigo"] == "KIT10438")
assert "sidekick" in tracker["descricao"].lower() and "Suzuki" in tracker["montadoras"]
assert "PRINCIPAIS DÚVIDAS" not in tracker["descricao"]
assert all((root / image).is_file() for p in catalog for image in p["imagens"])
referenced_public = {image for p in catalog for image in p["imagens"]}
generated_public = {"assets/catalogo/" + image.name for image in (root / "assets" / "catalogo").glob("*.webp")}
assert referenced_public == generated_public
assert not (root / "data" / "auditoria-importacao.json").exists()
assert all(p["funcoes"] and isinstance(p["montadoras"], list) for p in catalog)
assert {"Feixe de Mola", "Calço anti ruído"}.issubset(next(p["funcoes"] for p in catalog if p["codigo"] == "KIT10061"))
html = (root / "private" / "expedicao.html").read_text(encoding="utf-8")
kit_data = json.loads(html.split("const KITS = ", 1)[1].split(";\n", 1)[0])
assert len(kit_data) == len(original)
assert all((root / image).is_file() for k in kit_data for image in k["imagens"])
lookup = {k["codigo"]: k for k in kit_data}
assert lookup["KIT10006"]["composicao"].lower() == "9015: 02 pc"
assert lookup["KIT10006"]["imagens"]
assert lookup["KIT10972"]["imagens"]
assert not lookup["KIT10972"]["composicao"] and lookup["KIT10972"]["linha"] is None
assert lookup["KIT10972"]["pastas_fotos"] == ["KIT 972"]
assert lookup["KIT10021"]["pastas_fotos"] == ["21"]
print(f"OK: {len(catalog)} produtos ativos, {len(kit_data)} kits, imagens vinculadas e campos públicos verificados")
