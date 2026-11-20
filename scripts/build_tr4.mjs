import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const scope = { window: {} };
vm.runInNewContext(fs.readFileSync(path.join(root, 'data/catalogo-publico.js'), 'utf8'), scope);
const labels = { estabilizadora: 'Estabilizadora', bracos: 'Braços e tensor', suspensao: 'Suspensão e amortecedor', transmissao: 'Câmbio e diferencial' };
const featured = ['KIT10055', 'KIT10273', 'KIT10170', 'KIT10082'];
const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const products = scope.window.ROCHAPRO_CATALOG.filter(p => /\bTR\s*4\b/i.test(p.nome)).map(p => {
  const category = /estabilizadora/i.test(p.nome) ? 'estabilizadora' : /braço|tensor/i.test(p.nome) ? 'bracos' : /diferencial|câmbio/i.test(p.nome) ? 'transmissao' : 'suspensao';
  return { codigo: p.codigo, nome: p.nome, category, title: p.nome.replace(/\s*-?\s*Pajero\s+TR4.*$/i, '').replace(/^Kit (de |do )?/i, ''), image: p.codigo === 'KIT10055' ? (p.imagens[5] || p.imagens[0] || '') : p.imagens[0] || '', fitment: /2002.*2015/.test(p.nome) || p.codigo === 'KIT10055' ? 'TR4 · 2002 a 2015' : 'TR4 · confirme ano e versão' };
}).sort((a,b) => (featured.includes(a.codigo) ? featured.indexOf(a.codigo) : 99) - (featured.includes(b.codigo) ? featured.indexOf(b.codigo) : 99));
if (!products.length) throw new Error('Nenhum produto TR4 no catálogo público');
for (const p of products) if (p.image && !fs.existsSync(path.join(root,p.image))) throw new Error(`Foto ausente: ${p.image}`);
const cards = products.map(p => `<article id="kit-${esc(p.codigo)}" class="product-card" data-code="${esc(p.codigo)}" data-category="${p.category}"><div class="product-visual${p.image ? '' : ' no-photo'}"><span class="product-code">${esc(p.codigo)}</span>${p.image ? `<img src="/${p.image}" width="900" height="900" alt="Foto real do ${esc(p.codigo)} — ${esc(p.title)}" loading="lazy">` : `<span class="part-reference" aria-hidden="true">${esc(p.codigo)}</span><span class="photo-note">Foto sob consulta</span>`}</div><div class="product-body"><p class="product-category">${labels[p.category]}</p><h3>${esc(p.title)}</h3><p class="fitment">${esc(p.fitment)}</p><div class="product-actions"><button class="select-kit" data-select="${esc(p.codigo)}" aria-pressed="false" aria-label="Adicionar ${esc(p.codigo)} à cotação">Adicionar à cotação</button><a class="single-quote" href="https://wa.me/5531973589165?text=${encodeURIComponent(`Olá! Quero cotar o ${p.codigo} — ${p.nome}. Pode confirmar a aplicação e as condições?`)}" target="_blank" rel="noopener noreferrer">Cotar este kit</a></div></div></article>`).join('\n');
const template = fs.readFileSync(path.join(root,'tr4/page.template.html'),'utf8');
if (!template.includes('<!--__PRODUCTS__-->')) throw new Error('Marcador de produtos ausente');
const featuredPhotos = scope.window.ROCHAPRO_CATALOG.find(p => p.codigo === 'KIT10055')?.imagens || [];
if (!featuredPhotos.length) throw new Error('Kit em destaque KIT10055 sem fotos');
const seo = {'@context':'https://schema.org','@graph':[
  {'@type':'CollectionPage','@id':'https://rochaproauto.com.br/tr4/#page',url:'https://rochaproauto.com.br/tr4/',name:'Kits de buchas para Pajero TR4',inLanguage:'pt-BR',mainEntity:{'@id':'https://rochaproauto.com.br/tr4/#kits'}},
  {'@type':'BreadcrumbList',itemListElement:[{'@type':'ListItem',position:1,name:'In?cio',item:'https://rochaproauto.com.br/'},{'@type':'ListItem',position:2,name:'Pajero TR4',item:'https://rochaproauto.com.br/tr4/'}]},
  {'@type':'ItemList','@id':'https://rochaproauto.com.br/tr4/#kits',name:'Kits para Pajero TR4',numberOfItems:products.length,itemListElement:products.map((p,i)=>({'@type':'ListItem',position:i+1,name:p.nome,url:'https://rochaproauto.com.br/tr4/#kit-'+p.codigo}))}
]};
fs.writeFileSync(path.join(root,'tr4/index.html'), template.replace('<!--__PRODUCTS__-->',cards)
  .replaceAll('__KIT55_MAIN__', esc('/' + (featuredPhotos[5] || featuredPhotos[0])))
  .replaceAll('__KIT55_DETAIL__', esc('/' + (featuredPhotos[10] || featuredPhotos[0])))
  .replace('<!--__SEO__-->', '<script type="application/ld+json">' + JSON.stringify(seo).replaceAll('<', '\\u003c') + '</script>'));
fs.writeFileSync(path.join(root,'tr4/products.js'), `// Gerado por scripts/build_tr4.mjs a partir do catálogo público.\nwindow.TR4_PRODUCTS = ${JSON.stringify(products.map(({codigo,nome,category})=>({codigo,nome,category})),null,2)};\n`);
console.log(`TR4: ${products.length} kits, ${products.filter(p=>p.image).length} com fotos reais.`);
