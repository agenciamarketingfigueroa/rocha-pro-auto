"""Atualiza a tela interna com os dados já embutidos, sem reler as planilhas XLS.

Uso: python3 scripts/refresh_expedicao.py
O arquivo private/expedicao.html precisa existir neste computador.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "private" / "expedicao.html"
TEMPLATE = ROOT / "expedicao" / "template.html"
ASSIGNMENT = "const KITS = "
PLACEHOLDER = "/*__KITS__*/ []"


def refresh(source: Path = SOURCE, template: Path = TEMPLATE) -> int:
    if not source.is_file():
        raise FileNotFoundError(
            f"Arquivo interno não encontrado: {source}\n"
            "Copie a pasta private/ do computador que já tem a consulta ou gere-a com as planilhas originais."
        )
    old_html = source.read_text(encoding="utf-8")
    if ASSIGNMENT not in old_html:
        raise ValueError("O arquivo interno não contém os dados de kits esperados.")
    tail = old_html.split(ASSIGNMENT, 1)[1]
    kits, end = json.JSONDecoder().raw_decode(tail)
    if not tail[end:].lstrip().startswith(";") or not isinstance(kits, list) or not kits:
        raise ValueError("Os dados de kits do arquivo interno estão incompletos.")
    if not all(isinstance(kit, dict) and isinstance(kit.get("codigo"), str) for kit in kits):
        raise ValueError("Os dados de kits do arquivo interno não têm o formato esperado.")
    shell = template.read_text(encoding="utf-8")
    if shell.count(PLACEHOLDER) != 1:
        raise ValueError("O modelo de expedição não contém o marcador de dados esperado.")
    payload = json.dumps(kits, ensure_ascii=False).replace("<", "\\u003c")
    updated = shell.replace(PLACEHOLDER, payload)
    descriptor, temporary = tempfile.mkstemp(prefix="expedicao-", suffix=".html", dir=source.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            output.write(updated)
        os.replace(temporary, source)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return len(kits)


if __name__ == "__main__":
    try:
        count = refresh()
    except (FileNotFoundError, ValueError) as error:
        raise SystemExit(str(error)) from error
    print(f"Área interna atualizada com {count} kits. Abra private/expedicao.html novamente no navegador.")
