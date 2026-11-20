from pathlib import Path
import json,html,shutil
HERE=Path(__file__).resolve().parent; OUT=HERE.parent;ROOT=HERE.parents[2]
posts=json.loads((HERE/'posts.json').read_text('utf-8')); esc=html.escape
original=['01-automotive-hero','02-industrial-product','03-engineering-view']
for p in posts:
 n=p['numero'];layout=p['layout'];kits=p['kits'];code=kits[0] if kits else '';name=p['arquivo'];photo=f'assets/{code}.jpg'
 if n<=3:
  for ext in ['png','jpg']:shutil.copy2(ROOT/'rochapro-social'/'posts'/f'{original[n-1]}.{ext}',OUT/ext.upper()/f'{name}.{ext}')
  continue
 light=layout in ['product','compare'];logo='dark' if light else 'light'
 eyebrow={'product':'Kits em destaque','detail':'Olhar técnico','hero':'Seu carro. Sua história.','editorial':'No blog RochaPro','compare':'Confira a aplicação','mix':'Nossa linha'}[layout]
 footer='Leia no blog' if p['blog'] else ('Conheça nossa linha' if layout=='mix' else 'Consulte pelo link da bio')
 content=f'<header class="top"><img class="logo" src="assets/logo-{logo}.png" alt="RochaPro Auto Peças"><span class="eyebrow">{eyebrow}</span></header><section class="headline"><div class="rule"></div><h1>'+''.join('<span>'+esc(x)+'</span>' for x in p['titulo'].split('/'))+f'</h1><p>{esc(p["apoio"])}</p></section>'
 if layout=='product':
  content+=f'<span class="code">{code}</span><div class="stage"><img class="kitphoto" src="{photo}" alt="Fotografia real de {code}"></div><div class="diagonal"></div><div class="bottom-copy">Cada aplicação tem seu kit.<small>Consulte a compatibilidade com nossa equipe.</small></div>'
 elif layout=='detail':
  content+=f'<div class="drawing"><span class="label micro">Fotografia real do produto</span><img class="main" src="{photo}" alt="{code}"><svg viewBox="0 0 936 535"><path d="M220 300 L580 300 L655 240" fill="none" stroke="#e10606" stroke-width="1.5"/><circle cx="220" cy="300" r="5" fill="#e10606"/></svg><div class="zoom"><img src="{photo}" alt="Detalhe ampliado"></div><div class="detail-label"><span class="micro" style="color:#e10606">Detalhe ampliado</span><strong>{code}</strong><p>Conheça a peça.<br>Confira a aplicação.</p></div></div><div class="bottom-copy"><div><small>Identificação</small>{code}</div><div><small>Antes do pedido</small>Confirme ano e versão.</div></div>'
 elif layout in ['hero','editorial']:
  scene=p['cenario'];ext='png' if scene=='s10' else 'webp';content+=f'<img class="vehicle" src="assets/{scene}.{ext}" alt="Cena ilustrativa"><div class="shade"></div><div class="kit-card"><img src="{photo}" alt="Foto real de {code}">'
  if layout=='editorial':content+=f'<span class="code">NO CATÁLOGO · {code}</span>'
  content+='</div>'
  if layout=='hero':content+=f'<div class="kit-tag"><div class="code">{code}</div><p>Conheça os kits para o seu veículo.<br>Confirme a aplicação com nossa equipe.</p></div><div class="bottom-copy">RochaPro Auto Peças · Contagem, MG</div>'
  else:
   messages={7:('Investigue a origem.','O diagnóstico orienta a reposição.'),15:('A geração faz diferença.','Confira o ano e o conjunto do veículo.'),30:('Informação antes do pedido.','Modelo, ano, versão e especificação.'),41:('A preparação começa no roteiro.','Avalie o percurso e revise o veículo.'),42:('Planeje com informação atual.','Confira os trechos antes da saída.'),43:('Conte à oficina como você roda.','O manual orienta o plano de manutenção.')}
   a,b=messages[n];content+=f'<div class="insight">{a}<small>{b}</small></div>'
 elif layout in ['mix','compare']:
  labels={13:['35 mm','38 mm','40 mm'],34:['27 mm','30 mm','33 mm'],40:['TR4','Ranger','Sprinter'],49:['Hilux','Frontier','TR4']}[n]
  content+='<div class="comparison">'
  for k,label in zip(kits,labels):content+=f'<div class="tile"><div class="pic"><img src="assets/{k}.jpg" alt="{k}"></div><div class="measure">{label}</div><div class="code">{k}</div></div>'
  content+='</div><div class="bottom-copy">'+('Medidas distintas. Confira a referência.<small>Imagem ilustrativa da comparação, sem escala dimensional.</small>' if layout=='compare' else 'Seu veículo também faz parte da conversa.<small>Consulte as opções para a sua aplicação.</small>')+'</div>'
 content+=f'<footer class="footer"><span>@rochaproauto</span><strong>{footer}<span class="arrow">↗</span></strong></footer>'
 (HERE/f'{name}.html').write_text(f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{esc(p["titulo"].replace("/"," "))}</title><link rel="stylesheet" href="colecao.css"></head><body><main class="art {layout}">{content}</main></body></html>','utf-8')
print('47 artes montadas; 3 originais preservados.')
