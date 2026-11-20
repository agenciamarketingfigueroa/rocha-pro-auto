"""Reproducible strategy report, using dated research records and the verified article inventory."""
import json
from collections import Counter
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/pdf'
OUT.mkdir(parents=True,exist_ok=True)
TARGET=OUT/'RochaPro - Comunidades automotivas e estrategia de conteudo.pdf'
data=json.loads((ROOT/'docs/serie-blog-comunidades.json').read_text(encoding='utf-8'))
research=[]
for name in ['4x4','picapes']:
    research.extend(json.loads((ROOT/f'docs/pesquisa-comunidades-{name}.json').read_text(encoding='utf-8'))['models'])
by_model={m['model']:m for m in research}
refs=[]
def source(model,index=0):
    s=by_model[model]['sources'][index]
    if s['url'] not in [r['url'] for r in refs]: refs.append(s)
    return len(refs) if refs[-1]['url']==s['url'] else next(i+1 for i,r in enumerate(refs) if r['url']==s['url'])

profiles=[
 {'model':'Pajero TR4','key':'tr4','priority':'Núcleo inicial','evidence':'Encontro específico anunciado para 12/11/2026 em Brasília; resultado oficial de Goiânia identifica TR4 entre participantes em 11/04/2026. São dois sinais diferentes: intenção de mobilização e participação documentada.','limit':'O anúncio não confirma público realizado. Uma categoria de uma etapa não representa todos os donos. Não há taxa de engajamento comparável.','angle':'Pertencimento, primeiro encontro, diário de viagens e organização do histórico. Abrir conversa com “qual história fez você manter a sua TR4?”.','action':'Testar primeiro conteúdo de história e conteúdo de aplicação. Comparar consultas com ano e versão informados, além dos acessos.','refs':[source('Pajero TR4'),source('Pajero TR4',1)]},
 {'model':'Ranger','key':'ranger','priority':'Núcleo inicial','evidence':'O presidente do Ranger Clube Brasil publicou relato no portal Ford em 16/11/2026: encontros de famílias, conservação e mais de 420 picapes vinculadas ao clube, segundo o autor.','limit':'Contagem autodeclarada, não auditada; picapes não equivalem a pessoas ativas, seguidores ou alcance mensal. Datas dos encontros narrados não são informadas.','angle':'Memória familiar, conservação de Rangers antigas e identificação de aplicação. A comunidade cobre gerações que exigem consultas distintas.','action':'Usar uma história e um guia prático como teste inicial. O catálogo tem opções para diferentes conjuntos, mas isso não comprova cobertura de toda geração.','refs':[source('Ranger')]},
 {'model':'Troller','key':'troller','priority':'Núcleo de afinidade','evidence':'A programação oficial de um festival no RJ incluiu exposição do Troller Clube RJ em fevereiro de 2025. Já o site T4 Clube Brasil informa que o projeto está em pausa.','limit':'Programação não mede presença efetiva; público do festival não pode ser atribuído ao clube. Não usar o acervo ou os contadores do projeto pausado como atividade atual.','angle':'Encontros, conservação, histórias de expedição e nomes dos conjuntos. Diferenciar o interesse cultural pelo Troller da aplicação específica de cada kit.','action':'Confirmar atividade e regras de grupos antes de propor colaboração. Conteúdo com códigos de 2002–2014 não deve sugerir cobertura automática de veículos posteriores.','refs':[source('Troller'),source('Troller',2)]},
 {'model':'L200 / Triton','key':'l200','priority':'Núcleo de afinidade','evidence':'O Triton 4x4 Club mantém narrativa própria de origem, encontros e viagens. Resultado oficial de Goiânia, em abril de 2026, identifica versões da L200 em atividade organizada.','limit':'História do clube não informa atividade mensal atual. Participação em prova não comprova que peças comerciais sirvam a carros de competição.','angle':'Histórias dos proprietários e identificação de GL, GLS, Sport, Outdoor e Triton. Usar a diversidade de versões como oportunidade de esclarecimento.','action':'Registrar a versão nas consultas e separar as dúvidas recorrentes. Avaliar resposta comercial por aplicação, sem somar todos os interessados em Mitsubishi.','refs':[source('L200'),source('L200',2)]},
 {'model':'Hilux','key':'hilux','priority':'Núcleo de utilidade','evidence':'A Mercosul Toyota publicou registro posterior do Hilux Expedition de 2025. Um anúncio de edição Weiand em março de 2026 apresenta proposta de convivência, mas explicita formato multimarca.','limit':'São iniciativas de concessionárias, não um único clube independente. Não há base comparável de participantes ativos ou conversão; a edição multimarca inclui outros veículos.','angle':'Trabalho e lazer, estrada rural e compra informada. Separar Hilux picape de SW4 e explicitar posição e medidas dos componentes.','action':'Comparar conteúdo de rotina com conteúdo de aplicação. Contar somente consultas qualificadas para a picape atendida, sem atribuir toda audiência Toyota à Hilux.','refs':[source('Hilux'),source('Hilux',1)]},
 {'model':'Frontier','key':'frontier','priority':'Núcleo de utilidade','evidence':'O Clube da Nissan Frontier mantém publicações de 2025 e organização por geração. A produção própria é uma pista de interesse em informação detalhada sobre o veículo.','limit':'A última publicação exibida na consulta era de novembro de 2025. Data dinâmica de cabeçalho não é publicação nova; enquetes abertas não representam todos os proprietários.','angle':'Perguntas por geração, descrição de ruídos e leitura de aplicação. Produzir respostas claras para quem já está tentando identificar uma necessidade.','action':'Medir quais gerações chegam ao atendimento e quais dados faltam. Melhorar os artigos com dúvidas reais, sem reproduzir opiniões de fórum como diagnóstico.','refs':[source('Frontier')]},
 {'model':'S10 / Blazer','key':'s10','priority':'Teste de conservação','evidence':'O Clube do Vortec reúne memória de proprietários de S10, Blazer e outros modelos V6, com histórico de encontros de 2009–2011.','limit':'A página histórica não confirma atividade em 2025–2026. O recorte V6 não representa toda a família S10/Blazer nem confirma aplicação dos kits em todas as versões.','angle':'Memória da garagem, leitura de orçamento e diferenças de período. O valor inicial está na utilidade do conteúdo e na conexão com conservação.','action':'Validar canais atuais antes de investir em parceria. Medir resposta orgânica dos três artigos e separar S10 de Blazer nas consultas recebidas.','refs':[source('S10 / Blazer')]},
 {'model':'Jimny','key':'jimny','priority':'Teste pequeno e específico','evidence':'A página oficial Suzuki Day apresenta calendário 2026 e diferentes propostas de passeio. Jimny e Jimny Sierra são listados separadamente entre os modelos.','limit':'É um programa da marca, não medição de clube independente. O catálogo RochaPro tem somente KIT10452 para Jimny 2010–2021, sem foto; não confirma Sierra.','angle':'Escolha do primeiro passeio e diferença entre comunidade e aplicação. A limitação comercial deve aparecer de forma clara.','action':'Usar os dois artigos como teste de demanda pelo código existente. Antes de ampliar o investimento, validar dúvidas de aplicação e melhorar a informação/fotografia do item.','refs':[]},
 {'model':'D20','key':'d20','priority':'Exploração de memória','evidence':'A Prefeitura de Caxias registrou D20 entre veículos de passeio cultural em setembro de 2025, em parceria com clube de antigos.','limit':'Evento multimarcas; não informa quantidade de D20 ou força de comunidade exclusiva. Oportunidade editorial não equivale a alcance comprovado.','angle':'História familiar e documentação de intervenções. Mostrar por que ano e conjunto importam em veículos conservados por longo tempo.','action':'Testar um artigo e recolher, mediante autorização, relatos de proprietários. Conferir separadamente aplicações até 1992 e a partir de 1993.','refs':[source('D20')]},
 {'model':'F1000','key':'f1000','priority':'Exploração de memória','evidence':'A Casa de Metal lista F1000 entre modelos expostos no encontro O Barão, em março de 2025. É presença documentada em cultura de antigos.','limit':'Números totais de visitantes ou carros do encontro não são da F1000. A fonte não mede uma comunidade exclusiva do modelo.','angle':'Conservação e mudanças de aplicação por período. Valorizar o histórico sem sugerir resistência ilimitada ou dispensar avaliação.','action':'Testar um artigo, registrar ano e configuração das consultas e avaliar resposta antes de ampliar a série.','refs':[source('F1000')]},
]
suzuki={'title':'Suzuki — Suzuki Day, calendário 2026','url':'https://www.suzukiveiculos.com.br/suzuki-day/','eventDate':'Calendário: 23–24/05 e 18–19/09/2026. Consulta: 20/11/2026.','limitations':'Calendário e propostas do programa; não comprova presença efetiva ou engajamento de clube independente.'}
refs.append(suzuki);profiles[7]['refs']=[len(refs)]

pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialBold','C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='ArialBold',italic='Arial',boldItalic='ArialBold')
RED=colors.HexColor('#d90a0a'); INK=colors.HexColor('#161616'); MUTED=colors.HexColor('#54585d'); LIGHT=colors.HexColor('#f0f1f2')
styles={
 'body':ParagraphStyle('body',fontName='Arial',fontSize=10.3,leading=15,textColor=INK,spaceAfter=9),
 'small':ParagraphStyle('small',fontName='Arial',fontSize=8.4,leading=11.5,textColor=MUTED,spaceAfter=7),
 'h1':ParagraphStyle('h1',fontName='ArialBold',fontSize=26,leading=29,textColor=INK,spaceAfter=15),
 'h2':ParagraphStyle('h2',fontName='ArialBold',fontSize=16,leading=20,textColor=INK,spaceBefore=9,spaceAfter=9),
 'label':ParagraphStyle('label',fontName='ArialBold',fontSize=9,leading=12,textColor=RED,spaceAfter=9),
 'cell':ParagraphStyle('cell',fontName='Arial',fontSize=9,leading=12,textColor=INK),
 'white':ParagraphStyle('white',fontName='ArialBold',fontSize=9,leading=12,textColor=colors.white),
}
story=[]
def p(text,style='body'):return Paragraph(text,styles[style])
def add(text,style='body'):story.append(p(text,style))
def page(label,title):
    if story:story.append(PageBreak())
    add(label.upper(),'label');add(title,'h1')
def bullets(items):
    for item in items:add('• '+item)
def cite(ids):return ' '.join(f'<link href="#ref-{i}" color="#b50000">[{i}]</link>' for i in ids)
def table(rows,widths):
    items=[[p(str(v),'white' if i==0 else 'cell') for v in row] for i,row in enumerate(rows)]
    t=Table(items,colWidths=widths,hAlign='LEFT',repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),INK),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LIGHT]),('LINEBELOW',(0,-1),(-1,-1),.5,colors.HexColor('#d7d7d7'))]))
    story.append(t);story.append(Spacer(1,12))

page('Pesquisa e plano editorial | 20 novembro 2026','Comunidades que viram\nconversa. Conteúdo que\nabre relacionamento.'.replace('\n','<br/>'))
add('ROCHAPRO AUTO PEÇAS · CONTAGEM / MG','label')
im=Image(str(ROOT/'tr4/assets/tr4-road.webp'),width=507,height=253.5)
story.append(im);story.append(Spacer(1,15))
add('<b>30 novos artigos de blog</b>, conectados a kits cadastrados. Pesquisa qualitativa para escolher testes de conteúdo, com fontes, datas e limites explícitos.')
add('A recomendação é começar por <b>TR4 e Ranger</b> para histórias de comunidade; trabalhar Troller, L200, Hilux e Frontier com afinidade e utilidade; explorar os demais em escala menor. É uma prioridade editorial proposta, não um ranking nacional de engajamento.')
add('O que foi entregue: 30 artigos preparados no projeto, total de 36 no blog, CTAs e links para kits correspondentes. Não foram produzidos novos posts de Instagram nesta etapa.','small')

page('01 / Como interpretar','Evidência pública + encaixe no catálogo')
add('Pesquisa consultada em <b>20/11/2026</b>, priorizando clubes, organizadores, marcas e órgãos envolvidos. A janela principal foi 2025–2026; fontes antigas estão identificadas como históricas. Não houve contato com comunidades nem acesso a métricas privadas.')
add('<b>Engajamento não foi medido.</b> Encontro anunciado, relato posterior, resultado esportivo e arquivo histórico são evidências diferentes. Contagem de seguidores, total de festival e frota de um clube não são métricas equivalentes.')
counts=Counter(a['model'] for a in data['articles'])
rows=[['Modelo / recorte','Kits cadastrados*','Novos artigos','Uso proposto']]
for m in profiles:rows.append([m['model'],data['catalogCounts'][m['key']],counts[m['key']],m['priority']])
table(rows,[139,95,78,195])
add('* Contagem de códigos do catálogo público por nome/seleção, não estoque nem cobertura de todos os anos. Hilux exclui cinco códigos exclusivos de SW4; S10/Blazer é a união dos dois nomes (33 códigos). Há produtos que podem citar mais de um modelo; não somar as linhas como itens únicos.','small')
add('A distribuição dos artigos equilibra variedade, encaixe comercial e hipóteses de interesse. Ela não foi calculada como proporção de audiência. A linha Jimny é propositalmente restrita a um código.','small')

for pair in range(5):
    page(f'02 / Perfis · {pair+1} de 5','Onde começar a conversa')
    for m in profiles[pair*2:pair*2+2]:
        add(m['model'],'h2')
        add(f"{m['priority'].upper()} · {data['catalogCounts'][m['key']]} CÓDIGOS · {counts[m['key']]} ARTIGOS",'label')
        add('<b>O que encontramos.</b> '+m['evidence']+' '+cite(m['refs']))
        add('<b>Limite da leitura.</b> '+m['limit'])
        add('<b>Conversa proposta.</b> '+m['angle'])
        add('<b>Próximo teste.</b> '+m['action'])
        story.append(Spacer(1,7))

page('03 / Estratégia regional','Contagem como ponto de partida')
add('A localização em Contagem pode aproximar a marca de proprietários da Grande BH e de Minas Gerais. Isso é uma hipótese de distribuição, não evidência de que as comunidades pesquisadas tenham base local ou já sejam clientes RochaPro.')
add('Dias 1–30 · conhecer a resposta','h2')
bullets(['Publicar os artigos preparados no fluxo habitual do site e verificar indexação, páginas de entrada e cliques para kits. Estabelecer uma linha de base antes de comparar modelos.','Escolher um artigo de comunidade e um de utilidade de TR4 e Ranger. Manter janela de observação equivalente; não comparar um texto recém-publicado com outro já consolidado.','Registrar dúvidas recebidas no atendimento: modelo, ano, versão, conjunto procurado e origem informada pelo cliente. Usar esses dados para melhorar clareza e aplicação.'])
add('Dias 31–60 · validar interlocutores','h2')
bullets(['Mapear administradores e organizadores com atividade recente. Perguntar regras e pedir autorização antes de propor divulgação ou colaboração. Nenhum contato ou parceria foi feito nesta pesquisa.','Propor relatos voluntários de proprietários: primeira viagem, história da família, organização da manutenção. Combinar autorização de texto e imagem antes de usar o material.','Testar pautas de Troller, L200, Hilux e Frontier conforme consultas reais. Evitar ampliar Jimny antes de esclarecer aplicação e obter fotografia do código disponível.'])
add('Dias 61–90 · repetir o que trouxe interesse qualificado','h2')
add('Revisar conteúdos que atraem dúvidas de modelos ou anos não atendidos. Priorizar artigos que geram consultas compatíveis e perguntas úteis. Só então planejar desdobramentos para Instagram, com arte e legenda próprias; não copiar o artigo inteiro para a rede.')
add('<b>Ideia de ação local:</b> uma conversa sobre identificação de peças e histórico de manutenção, com convidados e autorização do espaço. Tratar como proposta a validar, sem anunciar evento, parceria ou atendimento técnico ainda não acordados.')

page('04 / Medição','O que observar antes de ampliar')
table([
 ['Pergunta','Indicador proposto','Como interpretar'],
 ['O conteúdo foi encontrado?','Impressões e cliques por URL no Search Console','Comparar mesma janela, tempo de publicação e intenção de busca.'],
 ['A leitura levou ao catálogo?','Cliques no kit / sessões do artigo','Usar o mesmo sistema e definição. Clique não é pedido.'],
 ['Chegou uma necessidade atendida?','Consultas com modelo, ano e conjunto identificados','Separar aplicação compatível, dúvida pendente e veículo não atendido.'],
 ['A consulta avançou?','Orçamentos emitidos / consultas qualificadas','Registrar resultado e motivo de não avanço; não prometer conversão.'],
 ['Uma futura parceria ajudou?','Sessões e consultas por UTM autorizado','Distinguir origem, artigo e período; não somar audiências sobrepostas.'],
 ],[127,175,205])
add('Definição sugerida de consulta qualificada','h2')
add('Uma conversa em que seja possível identificar modelo, ano/versão e o conjunto procurado, permitindo verificar se há aplicação cadastrada. Uma curtida, visita ou mensagem genérica não entra automaticamente nessa contagem.')
add('Comparação sem números inventados','h2')
add('Não há meta de conversão calculada nesta pesquisa. Primeiro medir o comportamento real e a qualidade das perguntas. Se futuramente houver métricas sociais autorizadas, comparar interações por alcance na mesma janela e com formatos semelhantes; seguidores acumulados não medem resposta a um conteúdo.')
add('O que ficou fora do núcleo','h2')
add('Strada não apresentou evidência suficiente de comunidade organizada recente nesta amostra. Civic teve pistas de evento específico, mas exige um cruzamento editorial mais restrito com as aplicações antes de ampliar o lote. F250 e Gol ficaram como pistas secundárias. A ausência neste lote não significa ausência de público ou de kits.')
add('As medições acima são recomendações. Este trabalho não instalou rastreadores nem configurou contas de analytics. As fontes documentais não permitem estimar receita, retorno de mídia ou tamanho nacional das comunidades.','small')

labels={m['key']:m['model'] for m in profiles}
for batch in range(3):
    page(f'05 / Mapa dos artigos · {batch+1} de 3',f'Novos artigos {batch*10+1:02d} a {batch*10+10:02d}')
    add('Os títulos abaixo correspondem às páginas preparadas no projeto. Os links apontam para as URLs finais previstas; a disponibilidade pública depende da publicação do site. A numeração identifica este lote, não posts de Instagram.','small')
    for i,a in enumerate(data['articles'][batch*10:batch*10+10],batch*10+1):
        url='https://rochaproauto.com.br'+a['url']
        story.append(KeepTogether([p(f'<b>{i:02d} · {escape(a["title"])}</b>'),p(f'{labels[a["model"]]} · {escape(a["category"])} · {", ".join(a["kits"])}<br/><link href="{url}" color="#b50000">Abrir URL prevista do artigo</link>','small')]))

for start in range(0,len(refs),5):
    page(f'06 / Fontes · {start//5+1}','Referências para conferir')
    add('Consulta em 20/11/2026. Links clicáveis levam às páginas de origem. Data de evento, data de publicação e data de consulta são tratadas separadamente.','small')
    for i,s in enumerate(refs[start:start+5],start+1):
        add(f'<a name="ref-{i}"/><b>[{i}] {escape(s["title"])}</b>')
        add(escape(str(s.get('eventDate') or s.get('publicationDate') or 'Sem data recente identificada.')),'small')
        add(f'<link href="{escape(s["url"],quote=True)}" color="#b50000">{escape(s["url"])}</link>','small')
        add('<b>Limite:</b> '+escape(s['limitations']),'small')
        story.append(Spacer(1,12))
    if start+5>=len(refs):
        add('Catálogo e rastreabilidade','h2')
        add('Aplicações e contagens extraídas de data/catalogo-publico.js em 20/11/2026. O inventário dos 30 artigos e códigos está em docs/serie-blog-comunidades.json. Os registros de pesquisa completos estão em docs/pesquisa-comunidades-4x4.json e docs/pesquisa-comunidades-picapes.json.','small')
        add('Algumas fontes foram acessadas pelo índice de busca após falha de abertura direta; essas limitações estão registradas acima e nos arquivos de pesquisa. Não houve auditoria de membros, público ou métricas privadas.','small')

logo=ROOT/'assets/identidade-visual/05-exportacoes/logos-png-transparentes/logo-horizontal-escuro.png'
def frame(canvas,doc):
    w,h=A4
    canvas.setStrokeColor(RED);canvas.setLineWidth(2);canvas.line(44,h-35,w-44,h-35)
    canvas.setFont('ArialBold',8);canvas.setFillColor(INK);canvas.drawString(44,h-25,'ROCHAPRO  /  INTELIGÊNCIA DE CONTEÚDO')
    canvas.setFont('Arial',8);canvas.setFillColor(MUTED);canvas.drawRightString(w-44,h-25,'20 NOV 2026')
    canvas.setStrokeColor(colors.HexColor('#dddddd'));canvas.setLineWidth(.5);canvas.line(44,37,w-44,37)
    canvas.drawString(44,24,'Comunidades, aplicações e oportunidades editoriais')
    canvas.drawRightString(w-44,24,f'{doc.page:02d}')

doc=SimpleDocTemplate(str(TARGET),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=55,bottomMargin=50,title='RochaPro | Comunidades automotivas e estratégia de conteúdo',author='RochaPro Auto Peças',subject='Pesquisa qualitativa e plano para 30 novos artigos de blog')
doc.build(story,onFirstPage=frame,onLaterPages=frame)
print(TARGET)
