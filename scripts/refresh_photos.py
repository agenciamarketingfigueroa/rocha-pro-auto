"""Refresh kit photos using the existing catalog and private records, without XLS files."""
import argparse
import csv
import json
import re

from build_catalog import ROOT, THUMBS, PRIVATE, photo_map, make_thumbnails


def refresh(only_codes=None):
    catalog_path = ROOT / "data" / "catalogo-publico.js"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8")
                         .removeprefix("window.ROCHAPRO_CATALOG = ").rstrip(";\n"))
    private_path = PRIVATE / "expedicao.html"
    old_html = private_path.read_text(encoding="utf-8")
    match = re.search(r"const KITS = (.*);", old_html)
    if not match:
        raise ValueError("Consulta interna sem dados de kits")
    kits = json.loads(match[1])
    template = (ROOT / "expedicao" / "template.html").read_text(encoding="utf-8")
    if template.count("/*__KITS__*/ []") != 1:
        raise ValueError("Modelo interno inválido")
    audit_path = PRIVATE / "auditoria-importacao.json"
    report = json.loads(audit_path.read_text(encoding="utf-8"))
    photos, folders, preferred = photo_map()
    public_codes = {p["codigo"] for p in catalog}
    all_codes = {k["codigo"] for k in kits}
    if only_codes and not only_codes.issubset(all_codes):
        raise ValueError(f"Códigos não cadastrados: {sorted(only_codes - all_codes)}")
    if not any(code in public_codes for code in photos):
        raise ValueError("Nenhuma pasta de fotos corresponde ao catálogo; atualização cancelada")
    public_urls = make_thumbnails({c: g for c, g in photos.items() if c in public_codes}, THUMBS, "assets/catalogo", refresh_codes=only_codes)
    private_urls = make_thumbnails({c: g for c, g in photos.items() if c in all_codes}, PRIVATE / "fotos", "private/fotos", public_urls, refresh_codes=only_codes)
    for records, urls in ((catalog, public_urls), (kits, private_urls)):
        for item in records:
            groups = photos.get(item["codigo"], [])
            item["imagens"] = list(dict.fromkeys(urls[str(p)] for _, files in groups for p in files))
            if records is kits:
                item["pastas_fotos"] = [folder.name for folder, _ in groups]
    catalog_path.write_text("window.ROCHAPRO_CATALOG = " + json.dumps(catalog, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c") + ";\n", encoding="utf-8")
    private_path.write_text(template.replace("/*__KITS__*/ []", json.dumps(kits, ensure_ascii=False).replace("<", "\\u003c")), encoding="utf-8")
    report.update({
        "pastas_fotos": len(folders), "fotos_originais": sum(f["fotos"] for f in folders),
        "fotos_publicas_geradas": len(public_urls), "fotos_privadas_geradas": len(private_urls),
        "pastas_sem_codigo": [f for f in folders if not f["codigos"]],
        "pastas_compartilhadas_nao_usadas_por_preferencia": preferred,
        "codigos_em_multiplas_pastas": {c: [f.name for f, _ in g] for c, g in photos.items() if len(g) > 1},
        "pastas_codigo_ausente_xls": {f["pasta"]: [c for c in f["codigos"] if c not in all_codes] for f in folders if any(c not in all_codes for c in f["codigos"])},
        "fotos_por_codigo": {c: sum(len(files) for _, files in groups) for c, groups in photos.items()},
        "produtos_ativos_com_foto": sum(bool(p["imagens"]) for p in catalog),
    })
    audit_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    without_xls = set(report["codigos_produtos_sem_kit_xls"])
    with (PRIVATE / "mapeamento-fotos.csv").open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.writer(output, delimiter=";")
        writer.writerow(["codigo_kit", "pasta_origem", "quantidade_fotos", "vinculo", "presente_csv", "presente_xls"])
        for folder in folders:
            for code in folder["codigos"]:
                chosen = folder["pasta"] in [source.name for source, _ in photos.get(code, [])]
                status = "aguarda_cadastro" if code not in all_codes else ("pasta_vazia" if not folder["fotos"] else "usado" if chosen else "substituido_por_pasta_especifica")
                writer.writerow([code, folder["pasta"], folder["fotos"], status, code in all_codes, code in all_codes - without_xls])
    print(json.dumps({k: v for k, v in report.items() if k != "fotos_por_codigo"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit", action="append", help="Regenera somente este código completo; use apenas quando os demais originais não mudaram.")
    args = parser.parse_args()
    refresh(set(args.kit) if args.kit else None)
