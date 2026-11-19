"""Build a safe public catalog and a local-only expedition file from the supplied data.

Usage: python scripts/build_catalog.py PRODUCTS.xls KITS.xls
The source workbooks and the expedition output are never copied into the public site.
"""
from __future__ import annotations

import csv
import html
import json
import re
import shutil
import sys
import unicodedata
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image, ImageOps

from read_xls import load_xls

ROOT = Path(__file__).resolve().parents[1]
PHOTOS = ROOT / "assets" / "img" / "Fotos dos Kits"
THUMBS = ROOT / "assets" / "catalogo"
PRIVATE = ROOT / "private"


class DescriptionText(HTMLParser):
    """Turn the export's optional rich-text descriptions into readable plain text."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"br", "p", "div", "li", "ul", "ol", "hr"}:
            self.parts.append("\n")
        if tag == "li":
            self.parts.append("• ")

    def handle_endtag(self, tag):
        if tag in {"p", "div", "li", "ul", "ol"}:
            self.parts.append("\n")

    def handle_data(self, data):
        self.parts.append(data)


def readable_description(value):
    parser = DescriptionText()
    cleaned = (value or "").translate(str.maketrans({"\x91": "‘", "\x92": "’", "\x96": "–", "\x97": "—"}))
    parser.feed(cleaned)
    lines = [re.sub(r"[ \t\xa0]+", " ", line).strip(" _-") for line in "".join(parser.parts).splitlines()]
    result = "\n".join(line for line in lines if line)
    # Old listing FAQs contain time-sensitive claims about stock and warranty.
    return re.split(r"PRINCIPAIS\s+D[ÚU]VIDAS\s*:?", result, maxsplit=1, flags=re.I)[0].strip()


def load_products(path):
    path = Path(path)
    if path.suffix.lower() == ".xls":
        sheets = load_xls(path)
        rows = next(iter(sheets.values()))
        required = {"Código", "Descrição", "Situação"}
        if not rows or not required.issubset(set(rows[0])):
            raise ValueError(f"XLS sem as colunas obrigatórias: {sorted(required)}")
        headers = rows[0]
        return [dict(zip(headers, row + [""] * (len(headers) - len(row)))) for row in rows[1:] if row]
    with path.open(encoding="utf-8-sig", newline="") as source:
        products = list(csv.DictReader(source, delimiter=";"))
    if not products or not {"Código", "Descrição", "Situação"}.issubset(products[0]):
        raise ValueError("CSV sem Código, Descrição ou Situação")
    return products
def normalized(value):
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", value).strip()


MAKE_PATTERNS = {
    "Chevrolet": r"\b(chevrolet|gm|s10|blazer|silverado|monza|corsa|celta|montana|onix|spin|cruze|d20|d10|omega|astra|vectra|opala|chevette|agile|meriva|zafira|tracker|prisma)\b",
    "Ford": r"\b(ford|ranger|pampa|ecosport|fiesta|courier|focus|cargo|ka|f1000|f250|f350|f4000|f12000|f14000|f16000|f-1000|f-250|f-350)\b",
    "Volkswagen": r"\b(volkswagen|vw|gol|saveiro|fox|kombi|amarok|delivery|constellation|worker|polo|virtus|parati|voyage|santana|quantum|passat|fusca|golf|up)\b",
    "Mercedes-Benz": r"\b(mercedes|benz|mb|sprinter|actros|accelo|atego|axor|atego|atego|atego)\b",
    "Fiat": r"\b(fiat|strada|fiorino|ducato|uno|palio|toro|mobi|argo|siena|doblo|idea|bravo|punto|tempra|tipo)\b",
    "Renault": r"\b(renault|master|duster|sandero|logan|kwid|fluence|clio|megane|scenic|kangoo|symbol)\b",
    "Toyota": r"\b(toyota|hilux|corolla|etios|bandeirante|rav4|sw4|yaris)\b",
    "Mitsubishi": r"\b(mitsubishi|l200|pajero|outlander|triton|asx)\b",
    "Hyundai": r"\b(hyundai|h100|hr|santa fe|tucson|hb20|ix35|creta|azera|elantra)\b",
    "Honda": r"\b(honda|fit|civic|crv|cr-v|city|hr-v)\b",
    "Nissan": r"\b(nissan|kicks|frontier|versa|march|sentra|livina)\b",
    "Iveco": r"\b(iveco|daily|vertis|tector|stralis|cavallino)\b",
    "Scania": r"\b(scania)\b", "Volvo": r"\b(volvo)\b",
    "Kia": r"\b(kia|bongo|sportage|sorento)\b",
    "Peugeot": r"\b(peugeot|partner|boxer|hoggar)\b",
    "Citroën": r"\b(citroen|jumper|berlingo|c3|c4|c5)\b",
    "Audi": r"\b(audi)\b", "Troller": r"\b(troller)\b",
    "Volare": r"\b(volare)\b", "Randon": r"\b(randon)\b",
    "Engesa": r"\b(engesa|marrua)\b",
    "Dodge": r"\b(dodge|ram)\b", "Jeep": r"\b(jeep|renegade|compass|cherokee)\b",
    "Suzuki": r"\b(suzuki|jimny|vitara)\b", "Agrale": r"\b(agrale)\b",
    "Effa": r"\b(effa|towner)\b", "Jac": r"\b(jac|t40|t50|t60)\b",
}


def makes(description):
    name = normalized(description)
    return [make for make, pattern in MAKE_PATTERNS.items() if re.search(pattern, name)]


def functions(description):
    name = normalized(description)
    labels = []
    def add(label):
        if label not in labels:
            labels.append(label)
    if "barra estabilizadora" in name:
        if "dianteir" in name:
            add("Barra Estabilizadora Dianteira")
        if "traseir" in name:
            add("Barra Estabilizadora Traseira")
    if "anti ruido" in name or "antirruido" in name:
        add("Calço anti ruído")
    for word, label in (
        ("bieleta", "Bieleta"),
        ("amortecedor", "Amortecedor"), ("cabine", "Cabine"),
        ("feixe", "Feixe de Mola"), ("batente", "Batente"),
        ("escapamento", "Escapamento"), ("silencioso", "Escapamento"),
        ("braco tensor", "Braço tensor"), ("carroceria", "Carroceria"),
        ("bandeja", "Bandeja"), ("tirante", "Tirante"),
    ):
        if word in name:
            add(label)
    return labels or ["Outras funções"]


def photo_map():
    mapping = defaultdict(list)
    folder_details = []
    for folder in sorted(PHOTOS.iterdir()):
        if not folder.is_dir():
            continue
        endings = [int(n) for n in re.findall(r"\d+", folder.name)]
        codes = [f"KIT{10000 + n}" for n in endings if 0 < n < 10000]
        files = sorted(p for p in folder.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})
        folder_details.append({"pasta": folder.name, "codigos": codes, "fotos": len(files)})
        for code in codes:
            mapping[code].append((folder, files))
    preferred = {}
    for code, groups in mapping.items():
        specific = [group for group in groups if len(re.findall(r"\d+", group[0].name)) == 1]
        if len(groups) > 1 and specific:
            preferred[code] = [group[0].name for group in groups if group not in specific]
            mapping[code] = specific
    return mapping, folder_details, preferred


def make_thumbnails(photo_groups, target_dir, url_prefix, reuse=None):
    target_dir.mkdir(parents=True, exist_ok=True)
    thumbs = {}
    expected = set()
    for folder, files in {str(group[0]): group for groups in photo_groups.values() for group in groups}.values():
        for number, original in enumerate(files):
            relative = f"{normalized(folder.name).replace(' ', '-')}-{number + 1:02}.webp"
            expected.add(relative)
            target = target_dir / relative
            if not target.exists() or target.stat().st_mtime < original.stat().st_mtime:
                try:
                    if reuse and str(original) in reuse and (ROOT / reuse[str(original)]).is_file():
                        shutil.copyfile(ROOT / reuse[str(original)], target)
                    else:
                        with Image.open(original) as image:
                            image = ImageOps.exif_transpose(image)
                            image.thumbnail((900, 900))
                            image.convert("RGB").save(target, "WEBP", quality=76, method=5)
                except Exception as exc:
                    print(f"Imagem ignorada: {original}: {exc}", file=sys.stderr)
                    continue
            thumbs[str(original)] = f"{url_prefix}/{relative}"
    for stale in target_dir.glob("*.webp"):
        if stale.name not in expected:
            stale.unlink()
    return thumbs


def main(product_file, kit_file):
    source_products = load_products(product_file)
    codes = [row["Código"].strip() for row in source_products]
    if not all(codes) or len(codes) != len(set(codes)):
        raise ValueError("CSV contém código vazio ou duplicado")
    rows = next(iter(load_xls(Path(kit_file)).values()))
    if not rows or len(rows[0]) < 14 or normalized(rows[0][2]) != "codigo" or normalized(rows[0][13]) != "cod. no fornecedor":
        raise ValueError("XLS não tem as colunas C e N esperadas")
    kits = {}
    for source_row, row in enumerate(rows[1:], start=2):
        if len(row) < 14 or not row[2].strip():
            continue
        code = row[2].strip()
        if code in kits:
            raise ValueError(f"Código de kit duplicado no XLS: {code}")
        kits[code] = {"codigo": code, "descricao": row[3].strip(), "composicao": row[13].strip(), "linha": source_row}
    csv_without_xls = []
    product_by_code = {row["Código"].strip(): row for row in source_products}
    for row in source_products:
        code = row["Código"].strip()
        if code not in kits:
            csv_without_xls.append(code)
            kits[code] = {"codigo": code, "descricao": row["Descrição"].strip(), "composicao": "", "linha": None}
    photos, folders, preferred = photo_map()
    active_codes = {row["Código"].strip() for row in source_products if row["Situação"].strip().lower() == "ativo"}
    public_urls = make_thumbnails({code: groups for code, groups in photos.items() if code in active_codes}, THUMBS, "assets/catalogo")
    private_urls = make_thumbnails({code: groups for code, groups in photos.items() if code in kits}, PRIVATE / "fotos", "private/fotos", public_urls)
    public = []
    for source_row, row in enumerate(source_products, start=2):
        if row["Situação"].strip().lower() != "ativo":
            continue
        code = row["Código"].strip()
        description = row["Descrição"].strip()
        details = "\n".join(filter(None, dict.fromkeys(
            readable_description(row.get(column, "")) for column in (
                "Descrição Curta", "Descrição Complementar", "Descrição do Produto no Fornecedor"
            )
        )))
        if normalized(details) == normalized(description):
            details = ""
        images = list(dict.fromkeys(public_urls[str(p)] for _, files in photos.get(code, []) for p in files if str(p) in public_urls))
        public.append({
            "codigo": code, "nome": description, "descricao": details,
            "montadoras": makes(description + " " + details),
            "funcoes": functions(description), "imagens": images,
        })
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "catalogo-publico.js").write_text("window.ROCHAPRO_CATALOG = " + json.dumps(public, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c") + ";\n", encoding="utf-8")
    PRIVATE.mkdir(exist_ok=True)
    private_kits = []
    for kit in kits.values():
        code = kit["codigo"]
        images = list(dict.fromkeys(private_urls[str(p)] for _, files in photos.get(code, []) for p in files if str(p) in private_urls))
        product_note = product_by_code.get(code, {}).get("Cód. no fornecedor", "").strip()
        private_kits.append({**kit, "imagens": images, "pastas_fotos": [folder.name for folder, _ in photos.get(code, [])],
                             "anotacao_csv": product_note if not kit["composicao"] else ""})
    payload = json.dumps(private_kits, ensure_ascii=False).replace("<", "\\u003c")
    shell = (ROOT / "expedicao" / "template.html").read_text(encoding="utf-8")
    (PRIVATE / "expedicao.html").write_text(shell.replace("/*__KITS__*/ []", payload), encoding="utf-8")
    report = {
        "produtos_fonte": len(source_products), "produtos_ativos_publicados": len(public),
        "kits_xls": len(kits) - len(csv_without_xls), "codigos_produtos_sem_kit_xls": csv_without_xls,
        "produtos_ativos_com_descricao_adicional": sum(bool(p["descricao"]) for p in public),
        "kits_sem_composicao": sum(not k["composicao"] for k in kits.values()),
        "pastas_fotos": len(folders), "fotos_originais": sum(f["fotos"] for f in folders),
        "fotos_publicas_geradas": len(public_urls), "fotos_privadas_geradas": len(private_urls),
        "pastas_sem_codigo": [f for f in folders if not f["codigos"]],
        "pastas_compartilhadas_nao_usadas_por_preferencia": preferred,
        "codigos_em_multiplas_pastas": {code: [f.name for f, _ in groups] for code, groups in photos.items() if len(groups) > 1},
        "pastas_codigo_ausente_xls": {f["pasta"]: [code for code in f["codigos"] if code not in kits] for f in folders if any(code not in kits for code in f["codigos"])},
        "fotos_por_codigo": {code: len([p for _, files in groups for p in files]) for code, groups in photos.items()},
        "funcoes": Counter(label for p in public for label in p["funcoes"]),
        "montadoras_nao_identificadas": sum(not p["montadoras"] for p in public),
        "produtos_ativos_com_foto": sum(bool(p["imagens"]) for p in public),
    }
    with (PRIVATE / "mapeamento-fotos.csv").open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.writer(output, delimiter=";")
        writer.writerow(["codigo_kit", "pasta_origem", "quantidade_fotos", "vinculo", "presente_csv", "presente_xls"])
        for folder in folders:
            for code in folder["codigos"]:
                chosen = folder["pasta"] in [source.name for source, _ in photos.get(code, [])]
                status = "aguarda_cadastro" if code not in kits else ("usado" if chosen else "substituido_por_pasta_especifica")
                writer.writerow([code, folder["pasta"], folder["fotos"], status, code in product_by_code, code in kits and code not in csv_without_xls])
    old_audit = ROOT / "data" / "auditoria-importacao.json"
    if old_audit.is_file():
        old_audit.unlink()
    (PRIVATE / "auditoria-importacao.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, default=dict), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "fotos_por_codigo"}, ensure_ascii=False, indent=2, default=dict))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Uso: python scripts/build_catalog.py produtos.csv kits.xls")
    main(sys.argv[1], sys.argv[2])
