from pathlib import Path
import json,html,csv,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from pypdf import PdfReader
HERE=Path(__file__).resolve().parent;OUT=HERE.parent;ROOT=HERE.parents[2]
posts=json.loads((HERE/'posts.json').read_text('utf-8'));H=html.escape;TITLE='Posts Instagram 01 a 50'
base='https://rochaproauto.com.br';labels={'original':'Original aprovado','hero':'Automotive Hero','product':'Industrial Product','detail':'Engineering View','editorial':'Conteúdo do blog','compare':'Comparativo de aplicações','mix':'Seleção da linha'}
md=[f'# {TITLE}','', 'RochaPro Auto Peças · @rochaproauto · Contagem, MG','', '**50 publicações: 3 artes aprovadas preservadas + 47 novas.** Imagens em 1080 × 1350 px (4:5), nas pastas PNG e JPG. A numeração é exclusiva dos arquivos e deste controle; não identifica posts dentro das artes.','',f'**Link da bio:** {base}/links','', 'Cada seção contém a legenda pronta para copiar, já com CTA e hashtags. Os campos de arquivo, texto alternativo e destino são apenas orientações de publicação. As cenas de veículos e estrada são ilustrativas; as peças são fotografias reais do catálogo.','']
for p in posts:
 title=p['titulo'].replace('/',' ');file=p['arquivo']
 md += [f'## {p["numero"]:02d} — {title}','',f'**Imagem:** [JPG/{file}.jpg](<JPG/{file}.jpg>) · [PNG/{file}.png](<PNG/{file}.png>)',f'**Linha:** {labels[p["layout"]]}',f'**Kits citados:** {", ".join(p["kits"]) or "Institucional"}','', '### Legenda','',p['legenda'],'','### Apoio para publicação','',f'**Texto alternativo:** {p["alt"]}',f'**Destino do CTA:** {base}/blog/{p["blog"]}/' if p['blog'] else f'**Destino do CTA:** {base}/links','', '---','']
md += ['## Referências de conteúdo','', 'Aplicações, códigos e fotos: catálogo público RochaPro e acervo de fotografias dos kits. O arquivo Fontes/assets/origens.json registra a origem das fotografias utilizadas.','', 'Os textos informativos adaptam os artigos já existentes no blog:','']
for slug in dict.fromkeys(p['blog'] for p in posts if p['blog']):md.append(f'- {base}/blog/{slug}/')
md+=['','Os kits mencionados nos conteúdos de viagem são referências de manutenção, não kits de adaptação ou promessa de capacidade fora de estrada. Aplicações e disponibilidade devem ser confirmadas no atendimento.','']
(OUT/f'{TITLE}.md').write_text('\n'.join(md),'utf-8')
# Browsable local gallery: search, preview, copy captions and open full images.
cards=[]
for p in posts:
 file=p['arquivo'];cards.append(f'<article data-search="{H(str(p).lower(),quote=True)}"><a href="PNG/{file}.png"><img loading="lazy" src="Previa/{file}.jpg" alt="{H(p["alt"],quote=True)}"></a><div class="body"><small>{p["numero"]:02d} · {labels[p["layout"]]}</small><h2>{H(p["titulo"].replace("/"," "))}</h2><details><summary>Legenda e arquivos</summary><pre>{H(p["legenda"])}</pre><button onclick="copyCaption(this)">Copiar legenda</button><a href="JPG/{file}.jpg" download>Baixar JPG</a> · <a href="PNG/{file}.png" download>Baixar PNG</a></details></div></article>')
(OUT/'Previa.html').write_text('<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+TITLE+'</title><style>*{box-sizing:border-box}body{margin:0;background:#101010;color:#eee;font:16px Arial,sans-serif}header{padding:45px 5vw;border-bottom:3px solid #e10606}h1{font-size:clamp(28px,4vw,48px);margin:0 0 20px}p{color:#bbb;line-height:1.6}input{padding:15px;width:min(500px,100%);background:#222;border:1px solid #555;color:white;border-radius:0}main{padding:35px 5vw;display:grid;grid-template-columns:repeat(auto-fill,minmax(245px,1fr));gap:25px;align-items:start}article{background:#1d1d1d;border:1px solid #333}img{display:block;width:100%;height:auto}.body{padding:20px}h2{font-size:19px;line-height:1.3}small{color:#bbb}pre{font:15px/1.6 Arial;white-space:pre-wrap}button{display:block;background:#e10606;color:white;border:0;padding:12px;cursor:pointer;margin-bottom:18px}a{color:#ddd}summary{cursor:pointer;font-size:14px}[hidden]{display:none}</style><header><h1>Posts Instagram 01 a 50</h1><p>50 artes · 1080 × 1350 px · 3 originais preservados + 47 novas<br>Numeração apenas para controle. Clique na arte para abrir o PNG.</p><input aria-label="Buscar posts" placeholder="Buscar por modelo, kit ou tema" oninput="filterPosts(this.value)"></header><main>'+''.join(cards)+'</main><script>function filterPosts(v){document.querySelectorAll("article").forEach(a=>a.hidden=!a.dataset.search.includes(v.toLowerCase()))}async function copyCaption(b){const t=b.previousElementSibling.textContent;try{await navigator.clipboard.writeText(t);b.textContent="Legenda copiada"}catch(e){const a=document.createElement("textarea");a.value=t;document.body.append(a);a.select();document.execCommand("copy");a.remove();b.textContent="Legenda copiada"}}</script></html>','utf-8')
with (OUT/'Controle dos posts.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Número','Arquivo','Título','Linha','Kits','CTA','Blog','Publicação'])
 for p in posts:w.writerow([f'{p["numero"]:02d}',p['arquivo'],p['titulo'].replace('/',' '),labels[p['layout']],', '.join(p['kits']),p['cta'],p['blog'],'Não publicado'])
# Contact sheets for visual QA and human review.
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for start in range(0,50,10):
 sheet=Image.new('RGB',(1500,830),'#ddd');draw=ImageDraw.Draw(sheet)
 for j,p in enumerate(posts[start:start+10]):
  im=Image.open(OUT/'JPG'/f'{p["arquivo"]}.jpg');im=im.resize((288,360));x=j%5*300+6;y=j//5*415+6;sheet.paste(im,(x,y));draw.text((x,y+370),f'{p["numero"]:02d} · {labels[p["layout"]]}',fill='#222',font=font)
 sheet.save(OUT/'Previa'/f'Contato {start+1:02d} a {start+10:02d}.jpg',quality=94)
# One caption per page; preview and publishing metadata are separate from copy.
pdfmetrics.registerFont(TTFont('R', 'C:/Windows/Fonts/arial.ttf'));pdfmetrics.registerFont(TTFont('B','C:/Windows/Fonts/arialbd.ttf'))
W,HT=A4;c=canvas.Canvas(str(OUT/f'{TITLE}.pdf'),pagesize=A4);c.setTitle(TITLE);c.setAuthor('RochaPro Auto Peças')
styles={k:ParagraphStyle(k,fontName=font,fontSize=size,leading=leading,textColor=HexColor(color)) for k,font,size,leading,color in [('body','R',11,16,'#222222'),('small','R',9,13,'#555555'),('title','B',22,25,'#111111'),('label','B',9,12,'#e10606')]}
def para(text,x,y,width,style='body'):
 obj=Paragraph(text,styles[style]);_,h=obj.wrap(width,HT);obj.drawOn(c,x,y-h);return y-h
def footer(page):
 c.setStrokeColor(HexColor('#dddddd'));c.line(42,45,W-42,45);c.setFont('R',8);c.setFillColor(HexColor('#666666'));c.drawString(42,29,'ROCHAPRO AUTO PEÇAS  |  CONTROLE INTERNO');c.drawRightString(W-42,29,str(page))
c.setFillColor(HexColor('#101010'));c.rect(0,0,W,HT,fill=1,stroke=0)
c.drawImage(str(HERE/'assets/logo-light.png'),42,HT-115,width=260,height=80,preserveAspectRatio=True,mask='auto')
c.setFillColor(HexColor('#e10606'));c.rect(42,HT-153,50,4,fill=1,stroke=0)
c.setFillColor(white);c.setFont('B',34);c.drawString(42,HT-205,'Posts Instagram');c.drawString(42,HT-245,'01 a 50')
c.setFont('R',12);c.setFillColor(HexColor('#cccccc'));c.drawString(42,HT-278,'Artes, legendas e orientações para publicação.');c.drawString(42,HT-300,'3 originais preservados + 47 novas publicações.')
for i,idx in enumerate([0,1,2,8,12,40]):
 p=posts[idx];x=42+(i%3)*174;y=HT-328-(i//3)*210-200;c.drawImage(str(OUT/'Previa'/f'{p["arquivo"]}.jpg'),x,y,width=160,height=200)
c.setFillColor(HexColor('#cccccc'));c.setFont('R',10);c.drawString(42,55,'@rochaproauto · Contagem, MG · Imagens em 4:5');c.drawString(42,37,'Numeração interna: não faz parte das artes.');c.showPage()
for p in posts:
 n=p['numero'];file=p['arquivo'];c.setFillColor(HexColor('#e10606'));c.rect(42,HT-50,34,4,fill=1,stroke=0)
 y=para(f'POST {n:02d} · {H(labels[p["layout"]].upper())}',42,HT-68,W-84,'label')
 y=para(H(p['titulo'].replace('/',' ')),42,y-13,W-84,'title')
 top=min(y-24,HT-160)
 c.drawImage(str(OUT/'Previa'/f'{file}.jpg'),42,top-225,width=180,height=225)
 my=para('ARQUIVO DA ARTE',242,top, W-284,'label');my=para(H(file)+'.jpg',242,my-8,W-284,'small')
 my=para('KITS CITADOS',242,my-24,W-284,'label');my=para(H(', '.join(p['kits']) or 'Institucional'),242,my-8,W-284,'body')
 my=para('PUBLICAÇÃO',242,my-24,W-284,'label');my=para('1080 × 1350 px · 4:5<br/>PNG e JPG nas pastas da coleção.<br/>Link da bio: rochaproauto.com.br/links',242,my-8,W-284,'small')
 if p['blog']:
  url=base+'/blog/'+p['blog']+'/'
  my=para(f'<a href="{url}" color="#e10606">Abrir artigo relacionado no blog</a>',242,my-18,W-284,'small')
 y=top-253;y=para('LEGENDA PRONTA PARA COPIAR',42,y,W-84,'label')-12
 for section in p['legenda'].split('\n\n'):
  y=para(H(section),42,y,W-84,'small' if section.startswith('#') else 'body')-12
 y-=4;y=para('TEXTO ALTERNATIVO',42,y,W-84,'label')-7;y=para(H(p['alt']),42,y,W-84,'small')
 assert y>63,(n,y)
 footer(n+1);c.showPage()
c.save()
pdf=PdfReader(OUT/f'{TITLE}.pdf');assert len(pdf.pages)==51
for p,page in zip(posts,pdf.pages[1:]):
 text=page.extract_text();assert f'POST {p["numero"]:02d}' in text;assert p['cta'].split()[0] in text
print('MD, PDF (51 páginas), galeria, controle CSV e 5 folhas de contato criados.')
