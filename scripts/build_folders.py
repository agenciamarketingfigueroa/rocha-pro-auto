"""Print masters and four-up A4 sheets for RochaPro. Run from any directory."""
from pathlib import Path
import json
import zipfile
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from pypdf import PdfReader, PdfWriter, Transformation
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf/folders-rochapro'
OUT.mkdir(parents=True, exist_ok=True)
TMP = ROOT / '.tmp/pdfs/folders'
TMP.mkdir(parents=True, exist_ok=True)
URL = 'https://rochaproauto.com.br/links/'
RED = '#E10606'
BLACK = '#080808'
GRAY = '#666666'
LIGHT = '#E3E3E3'
WHITE = '#FFFFFF'
FONTDIR = Path('C:/Windows/Fonts')
for name, filename in [('Body','arial.ttf'),('Bold','arialbd.ttf'),('Condensed','ARIALNB.TTF')]:
    pdfmetrics.registerFont(TTFont(name, str(FONTDIR / filename)))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='Bold', italic='Body', boldItalic='Bold')
LOGOS = ROOT / 'assets/identidade-visual/05-exportacoes/logos-png-transparentes'

def rect(c, x, y, w, h, fill, stroke=None, lw=.25):
    c.setFillColor(colors.HexColor(fill))
    c.setStrokeColor(colors.HexColor(stroke or fill))
    c.setLineWidth(lw * mm)
    c.rect(x*mm, (150-y-h)*mm, w*mm, h*mm, fill=1, stroke=bool(stroke))

def line(c,x,y,x2,y2,color=LIGHT,lw=.2):
    c.setStrokeColor(colors.HexColor(color)); c.setLineWidth(lw*mm)
    c.line(x*mm,(150-y)*mm,x2*mm,(150-y2)*mm)

def text(c,x,y,s,size=8,font='Body',color=BLACK):
    c.setFillColor(colors.HexColor(color)); c.setFont(font,size)
    c.drawString(x*mm,(150-y)*mm,s)

def para(c,x,y,w,s,size=8,leading=10,color=BLACK,font='Body'):
    p=Paragraph(s,ParagraphStyle('p',fontName=font,fontSize=size,leading=leading,
        textColor=colors.HexColor(color),spaceAfter=0))
    _,h=p.wrap(w*mm,150*mm)
    p.drawOn(c,x*mm,(150-y)*mm-h)
    return h/mm

def polygon(c,points,color):
    p=c.beginPath(); p.moveTo(points[0][0]*mm,(150-points[0][1])*mm)
    for x,y in points[1:]:p.lineTo(x*mm,(150-y)*mm)
    p.close();c.setFillColor(colors.HexColor(color));c.drawPath(p,fill=1,stroke=0)

def image(c,path,x,y,w,h):
    c.drawImage(ImageReader(str(path)),x*mm,(150-y-h)*mm,w*mm,h*mm,mask='auto')

def logo(c,home):
    image(c,LOGOS / ('logo-horizontal-escuro.png' if home else 'logo-horizontal-claro.png'),5,4.8,53,13.35)
    text(c,70,10,'PEÇA CERTA.',6,'Bold',RED)
    text(c,70,13.3,'NOVOS CAMINHOS.',5.1,'Bold',GRAY if home else '#DDDDDD')

def qr(c,x,y,size):
    # Preserve all modules, square finders and a four-module quiet zone.
    rect(c,x,y,size,size,WHITE,RED,.15)
    widget=QrCodeWidget(URL,barLevel='H',barBorder=4)
    b=widget.getBounds(); d=Drawing(size*mm,size*mm,transform=[size*mm/(b[2]-b[0]),0,0,size*mm/(b[3]-b[1]),0,0])
    d.add(widget); renderPDF.draw(d,c,x*mm,(150-y-size)*mm)
    c.linkURL(URL,(x*mm,(150-y-size)*mm,(x+size)*mm,(150-y)*mm),relative=0)

def contact(c,home,y=120):
    # QR panel uses the same white background in both versions for reliable scanning.
    rect(c,5,y,90,24,WHITE)
    qr(c,5.5,y+.5,23)
    text(c,31,y+4.1,'CONHEÇA A ROCHAPRO',8,'Bold',BLACK)
    para(c,31,y+6,61,'Aponte a câmera para mais informações,<br/>conheça a RochaPro, nossos kits e contatos.',6.8,8.5)
    text(c,31,y+16.1,'WhatsApp  (31) 99198-3462',8.2,'Bold')
    text(c,31,y+20.1,'rochaproauto.com.br/links/',6.7)
    c.linkURL('https://wa.me/5531991983462',(31*mm,(150-y-18)*mm,94*mm,(150-y-13)*mm),relative=0)

def base(c,home):
    rect(c,0,0,100,150,WHITE if home else BLACK)
    logo(c,home)
    line(c,5,20,95,20,RED,.45)
    if home:
        line(c,5,146.5,95,146.5,LIGHT,.2)
    else:
        polygon(c,[(86,146),(94,146),(90,150),(82,150)],RED)
        polygon(c,[(96,146),(100,146),(100,150),(92,150)],'#A90000')
    text(c,5,148,'ROCHAPRO AUTO PEÇAS',5.5,'Bold',GRAY if home else '#BBBBBB')

def clamp(c,x,y,w):
    # Schematic front view: comparison only, without implying an exact scale.
    c.saveState();c.translate(x*mm,(150-y)*mm);c.scale(w*mm/30,w*mm/30)
    p=c.beginPath();p.moveTo(0,-10);p.lineTo(5,-10);p.curveTo(6,5,24,5,25,-10);p.lineTo(30,-10)
    c.setLineWidth(3);c.setStrokeColor(colors.HexColor('#313131'));c.drawPath(p)
    c.setLineWidth(.8);c.setStrokeColor(colors.HexColor('#999999'));c.drawPath(p)
    c.restoreState()
    yy=y+w/30*14
    line(c,x+2,yy,x+w-2,yy,RED,.3)
    polygon(c,[(x+2,yy),(x+4,yy-1),(x+4,yy+1)],RED)
    polygon(c,[(x+w-2,yy),(x+w-4,yy-1),(x+w-4,yy+1)],RED)

def bushing(c,x,y,label):
    # Vector cross-section with the nominal internal diameter identified.
    c.setFillColor(colors.HexColor('#313131'))
    p=c.beginPath();p.moveTo(x*mm,(150-y-9)*mm);p.lineTo(x*mm,(150-y-4)*mm)
    p.curveTo(x*mm,(150-y+3)*mm,(x+12)*mm,(150-y+3)*mm,(x+12)*mm,(150-y-4)*mm)
    p.lineTo((x+12)*mm,(150-y-9)*mm);p.close();c.drawPath(p,fill=1,stroke=0)
    c.setFillColor(colors.white);c.circle((x+6)*mm,(150-y-4)*mm,2.3*mm,fill=1,stroke=0)
    line(c,x+3.7,y+4,x+8.3,y+4,RED,.35)
    text(c,x-.2,y+13.5,label,7.3,'Bold')

def instruction(c,home):
    base(c,home)
    text(c,5,25,'ORIENTAÇÕES PARA O SEU KIT',6.6,'Bold',RED)
    text(c,5,32,'ATENÇÃO À APLICAÇÃO.',17,'Condensed',BLACK if home else WHITE)
    rect(c,0,36,100,76.8,WHITE)
    text(c,5,41.5,'01',10,'Bold',RED)
    text(c,13,41.5,'CONFIRA A ABRAÇADEIRA',9,'Bold')
    para(c,5,44,90,'Há dois modelos de abraçadeira: <b>maior ou menor.</b>',8.2,10.5)
    clamp(c,10,53,31);clamp(c,59,54,24)
    text(c,18,72.6,'MAIOR',7.5,'Bold');text(c,62,72.6,'MENOR',7.5,'Bold')
    line(c,5,75.5,95,75.5)
    text(c,5,80.5,'02',10,'Bold',RED)
    text(c,13,80.5,'CONFIRME A MEDIDA DA BUCHA',9,'Bold')
    bushing(c,12,86,'27,0 mm');bushing(c,44,86,'30,0 mm');bushing(c,76,86,'33,0 mm')
    para(c,5,102,90,'Consulte seu mecânico de confiança para medir o <b>diâmetro da barra estabilizadora</b> e confirmar a abraçadeira e a bucha corretas.',8.2,10.2)
    rect(c,5,113.8,1,10.5,RED)
    para(c,8,113.8,86,'<b>SE NECESSÁRIO, ENVIE UMA FOTO</b><br/>Após a compra, envie uma foto da abraçadeira <b>(no caso da 515)</b> para identificarmos as buchas conforme a necessidade do veículo.',7.4,9.2,BLACK if home else WHITE)
    # Compact contact block below the technical instructions.
    qr(c,5,125,21)
    text(c,29,129.3,'MAIS INFORMAÇÕES E KITS',7.5,'Bold',BLACK if home else WHITE)
    para(c,29,131,66,'Aponte a câmera para conhecer a RochaPro,<br/>nossos kits e contatos.',6.8,8.5,BLACK if home else WHITE)
    text(c,29,140,'WhatsApp: (31) 99198-3462',7.4,'Bold',BLACK if home else WHITE)
    text(c,29,144.6,'rochaproauto.com.br/links/',6.7,'Body',GRAY if home else '#CCCCCC')
    c.linkURL('https://wa.me/5531991983462',(29*mm,7*mm,95*mm,14*mm),relative=0)

BRANDS = ['Chevrolet','Ford','Volkswagen','Fiat','Toyota','Mitsubishi','Nissan','Renault','Hyundai','Mercedes-Benz','Honda','Kia','Troller','Iveco','Peugeot','Citroën']

def promotion(c,home):
    base(c,home)
    fg=BLACK if home else WHITE
    text(c,5,25,'KITS DE BUCHAS E REPAROS',6.9,'Bold',RED)
    text(c,5,32.7,'SEU PRÓXIMO CUIDADO',17,'Condensed',fg)
    text(c,5,40.1,'COMEÇA COM A PEÇA CERTA.',16,'Condensed',fg)
    if home:
        line(c,5,45,95,45,LIGHT)
        text(c,5,52,'PASSEIO  /  PICAPES  /  4×4',11,'Condensed')
        text(c,5,59,'DA CIDADE AO TRABALHO PESADO.',9.5,'Condensed',RED)
        line(c,5,63,95,63,LIGHT)
    else:
        # Use the existing web hero; keep the complete vehicles visible.
        hero=ROOT/'assets/home/hero-tr4-caminhao.webp'
        im=Image.open(hero).convert('RGB')
        # Full image proportion, with a 100 mm wide crop of its vertical blank area.
        im=im.crop((0,140,1920,660)); crop=TMP/'hero-print.jpg';im.save(crop,quality=94)
        image(c,crop,0,43.5,100,27.08)
    text(c,5,74.4 if not home else 68.6,'DESTAQUES DO NOSSO BLOG',6.2,'Bold',RED)
    model_y=76 if not home else 70.2
    para(c,5,model_y,90,'<b>Pajero TR4 · Troller · Hilux · Frontier · L200<br/>Ranger · S10 / Blazer · Jimny · D20 · F1000</b>',7.7,10.3,fg)
    by=87 if not home else 83
    text(c,5,by,'APLICAÇÕES PARA AS MARCAS',6.2,'Bold',RED)
    # Name grid avoids tiny or distorted third-party logos at this paper size.
    for i,name in enumerate(BRANDS):
        x=5+(i%4)*23;y=by+4+(i//4)*4
        text(c,x,y,name,6.1,'Bold',fg)
    text(c,5,by+20,'E Suzuki, com aplicações para Jimny.',6.4,'Body',GRAY if home else '#CCCCCC')
    hy=110.5 if not home else 107
    if home:
        line(c,5,hy-1.5,95,hy-1.5,RED,.35)
    else:
        rect(c,5,hy-1.7,90,9.2,RED)
    text(c,7 if not home else 5,hy+2.3,'TAMBÉM TRABALHAMOS COM LINHA PESADA.',8.2,'Condensed',fg if home else WHITE)
    text(c,7 if not home else 5,hy+5.8,'Consulte a aplicação para o seu veículo com a equipe.',6.2,'Body',GRAY if home else WHITE)
    contact(c,home,120)

def master(kind,home):
    name=f'{kind}-10x15-{"casa" if home else "normal"}.pdf'
    dest=OUT/name
    c=canvas.Canvas(str(dest),pagesize=(100*mm,150*mm),pageCompression=1)
    c.setTitle('RochaPro | '+('Orientações do kit' if kind=='orientacoes' else 'Divulgação')+' | '+('Impressão em casa' if home else 'Normal'))
    c.setAuthor('RochaPro Auto Peças')
    (instruction if kind=='orientacoes' else promotion)(c,home)
    c.showPage();c.save()
    return dest

def sheet(src):
    dest=OUT/src.name.replace('10x15','A4-4-unidades')
    guide=TMP/'cut-guides.pdf'
    c=canvas.Canvas(str(guide),pagesize=(210*mm,297*mm))
    # 94 x 141 mm, uniform 94% scaling; 4 mm horizontal, 5 mm vertical gutter.
    # Outer margins: 9 mm left/right and 5 mm top/bottom.
    c.setStrokeColor(colors.HexColor('#999999'));c.setLineWidth(.2)
    for x in [9,103,107,201]:
        for ya,yb in [(2,4),(147,149),(293,295)]:c.line(x*mm,ya*mm,x*mm,yb*mm)
    for y in [5,146,151,292]:
        for xa,xb in [(6,8),(104,106),(202,204)]:c.line(xa*mm,y*mm,xb*mm,y*mm)
    c.setFont('Body',5);c.setFillColor(colors.HexColor('#666666'))
    c.drawCentredString(105*mm,1.6*mm,'A4 | 4 unidades de 94 x 141 mm | Imprimir em tamanho real / 100%')
    c.save()
    w=PdfWriter();page=w.add_blank_page(210*mm,297*mm)
    source=PdfReader(str(src)).pages[0]
    for x,y in [(9,151),(107,151),(9,5),(107,5)]:
        page.merge_transformed_page(source,Transformation().scale(.94).translate(x*mm,y*mm))
    page.merge_page(PdfReader(str(guide)).pages[0])
    w.add_metadata({'/Title':'RochaPro | A4 com quatro folders | 94 x 141 mm','/Author':'RochaPro Auto Peças'})
    with dest.open('wb') as f:w.write(f)
    return dest

def bleed(src):
    """Additional shop master: 3 mm bleed, true 100 x 150 mm TrimBox."""
    from pypdf.generic import RectangleObject
    dest=OUT/src.name.replace('-normal.pdf','-grafica-sangria-3mm.pdf')
    bg=TMP/'bleed.pdf'
    c=canvas.Canvas(str(bg),pagesize=(106*mm,156*mm))
    c.setFillColor(colors.HexColor(BLACK));c.rect(0,0,106*mm,156*mm,fill=1,stroke=0)
    if src.name.startswith('orientacoes'):
        c.setFillColor(colors.white);c.rect(0,(156-3-112.8)*mm,106*mm,76.8*mm,fill=1,stroke=0)
    c.save()
    w=PdfWriter();p=w.add_page(PdfReader(str(bg)).pages[0])
    p.merge_transformed_page(PdfReader(str(src)).pages[0],Transformation().translate(3*mm,3*mm))
    p.trimbox=RectangleObject([3*mm,3*mm,103*mm,153*mm]);p.bleedbox=p.mediabox
    with dest.open('wb') as f:w.write(f)
    return dest

def main():
    files=[]
    for kind in ['orientacoes','divulgacao']:
        for home in [False,True]:
            m=master(kind,home);files.extend([m,sheet(m)])
            if not home:files.append(bleed(m))
    readme=OUT/'LEIA-ME.txt'
    readme.write_text('ROCHAPRO | FOLDERS PARA IMPRESSÃO\n\n'
        'Individuais: 100 x 150 mm (10 x 15 cm), página única, frente.\n'
        'A4: quatro unidades de 94 x 141 mm (redução proporcional a 94%).\n'
        'Quatro peças de 100 x 150 mm somam 200 x 300 mm: não cabem numa A4 de 210 x 297 mm.\n'
        'A montagem tem 5 mm de margem superior/inferior, 9 mm nas laterais,\n'
        '4 mm entre colunas e 5 mm entre linhas, com marcas discretas de corte.\n\n'
        'CASA: fundo branco, sem fotografia, poucos detalhes vermelhos.\n'
        'NORMAL: identidade preta, vermelha e branca; divulgação com imagem do site.\n'
        'GRÁFICA: dois arquivos extras com sangria de 3 mm; página 106 x 156 mm,\n'
        'TrimBox 100 x 150 mm. PDFs RGB, fontes incorporadas, sem certificação PDF/X.\n'
        'A gráfica deve definir o perfil de cor conforme o equipamento/papel.\n\n'
        'Imprima os arquivos A4 em TAMANHO REAL / 100%. Desative ajuste à página.\n'
        'Para manter 10 x 15 cm exatos, use os individuais em papel maior ou duas peças por A4.\n'
        'QR: https://rochaproauto.com.br/links/ | WhatsApp: +55 31 99198-3462.\n'
        'O QR preserva módulos pretos e área branca de respiro. A identidade está na moldura e no texto.\n'
        'As medidas dos desenhos técnicos são esquemáticas, sem escala.\n'
        'O texto original sobre buchas foi esclarecido para listar as três medidas: 27, 30 e 33 mm.\n'
        'Marcas/modelos descrevem aplicações do catálogo, sem promessa de todas as versões.\n',encoding='utf-8')
    manifest={'qr_url':URL,'phone':'+5531991983462','individual_mm':[100,150],
        'a4_mm':[210,297],'a4_piece_mm':[94,141],'a4_copies':4,
        'pdfs':[p.name for p in files]}
    (OUT/'especificacoes.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    package=OUT.parent/'RochaPro-folders-impressao.zip'
    with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
        for p in [*files,readme,OUT/'especificacoes.json']:z.write(p,p.name)
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
