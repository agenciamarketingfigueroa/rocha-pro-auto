"""Prepare faithful, padded catalog photographs for the community article series."""
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
raw = (ROOT / 'data/catalogo-publico.js').read_text(encoding='utf-8')
catalog = json.loads(raw[raw.index('['):].strip().rstrip(';'))
by_code = {p['codigo']: p for p in catalog}
out = ROOT / 'assets/blog'
out.mkdir(exist_ok=True)
provenance = []
for model, code in [('l200','KIT10002'),('ranger','KIT10088'),('s10','KIT10006'),('d20','KIT10012'),('f1000','KIT10025')]:
    source = by_code[code]['imagens'][0]
    im = Image.open(ROOT / source).convert('RGB')
    im.thumbnail((1450, 820), Image.Resampling.LANCZOS)
    canvas = Image.new('RGB', (1600, 900), 'white')
    canvas.paste(im, ((1600-im.width)//2, (900-im.height)//2))
    target = out / f'{model}-kits.webp'
    canvas.save(target, 'WEBP', quality=88)
    provenance.append({'model':model,'code':code,'source':source,'output':str(target.relative_to(ROOT)).replace('\\','/'),'processing':'Resized proportionally and padded; no part added or altered.'})
(out / 'origens.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Prepared 5 covers from real catalog photographs.')
