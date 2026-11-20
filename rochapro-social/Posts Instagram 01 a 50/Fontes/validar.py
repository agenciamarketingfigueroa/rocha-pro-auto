from pathlib import Path
from PIL import Image
from pypdf import PdfReader
import json,re,hashlib
HERE=Path(__file__).resolve().parent;OUT=HERE.parent;ROOT=HERE.parents[2]
posts=json.loads((HERE/'posts.json').read_text('utf-8'));assert len(posts)==50
assert [p['numero'] for p in posts]==list(range(1,51))
md=(OUT/'Posts Instagram 01 a 50.md').read_text('utf-8');pdf=PdfReader(OUT/'Posts Instagram 01 a 50.pdf')
assert len(pdf.pages)==51
normalize=lambda s:re.sub(r'\s+',' ',s).strip()
records=[]
originals=['01-automotive-hero','02-industrial-product','03-engineering-view']
for ext in ['png','jpg']:
 files=list((OUT/ext.upper()).glob('*.'+ext));assert len(files)==50
 for p in posts:
  f=OUT/ext.upper()/f'{p["arquivo"]}.{ext}';im=Image.open(f);assert im.size==(1080,1350);assert im.mode=='RGB';assert im.info.get('icc_profile')
  digest=hashlib.sha256(f.read_bytes()).hexdigest()
  if p['numero']<=3:
   source=ROOT/'rochapro-social/posts'/f'{originals[p["numero"]-1]}.{ext}';assert digest==hashlib.sha256(source.read_bytes()).hexdigest()
  records.append({'arquivo':str(f.relative_to(OUT)),'sha256':digest,'tamanho':f.stat().st_size})
for p in posts:
 assert p['cta'] and p['cta'] in p['legenda'];assert p['legenda'] in md
 text=normalize(pdf.pages[p['numero']].extract_text())
 assert normalize(p['legenda']) in text,p['numero']
 assert len(p['legenda'])<2200
 if p['numero']>3:
  h=(HERE/f'{p["arquivo"]}.html').read_text('utf-8');assert not re.search(r'\bpost\s*0?\d',h,re.I)
report={'posts':50,'originais_preservados':3,'novos':47,'formatos':['50 PNG','50 JPG'],'dimensoes':[1080,1350],'perfil':'sRGB','legendas_com_cta':50,'paginas_pdf':51,'posts_blog':sum(bool(p['blog']) for p in posts),'arquivos':records}
(OUT/'Fontes/validacao-final.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='arquivos'},ensure_ascii=False))
