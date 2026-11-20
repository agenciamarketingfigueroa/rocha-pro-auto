import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const scope={window:{}};
vm.runInNewContext(read('data/catalogo-publico.js'),scope);
vm.runInNewContext(read('tr4/products.js'),scope);
const products=scope.window.TR4_PRODUCTS;
const expected=scope.window.ROCHAPRO_CATALOG.filter(p=>/\bTR\s*4\b/i.test(p.nome));
assert.deepEqual([...products.map(p=>p.codigo)].sort(),[...expected.map(p=>p.codigo)].sort());
const html=read('tr4/index.html');
assert.equal((html.match(/class="product-card"/g)||[]).length,products.length);
assert.ok(!html.includes('<!--__PRODUCTS__-->'));
assert.ok(!html.includes('__KIT55_'));
assert.ok(!html.includes('�'));
for(const match of html.matchAll(/(?:src|href)="(\/[^"#]*)"/g)) {
  if(match[1]==='/') continue;
  assert.ok(fs.existsSync(path.join(root,match[1])),`Recurso ausente: ${match[1]}`);
}
assert.ok(!/private\/|fornecedor|10116|1508|1971606904/.test(html));
class Element {
  constructor(dataset={}){this.dataset=dataset;this.events={};this.attributes={};this.hidden=false;this.value='';this.textContent='';this.classes=new Set();this.classList={toggle:(name,value)=>value?this.classes.add(name):this.classes.delete(name)};}
  setAttribute(k,v){this.attributes[k]=v;}
  addEventListener(k,fn){this.events[k]=fn;}
  click(){this.events.click();}
  focus(){}
}
function boot(now,stored='[]'){
  const cards=products.map(p=>new Element({code:p.codigo}));
  const buttons=products.map(p=>new Element({select:p.codigo}));
  const filters=['all','estabilizadora','bracos','suspensao','transmissao'].map(filter=>new Element({filter}));
  const contacts=[new Element()];
  const expired=[new Element({campaignText:'Texto sem promoção'})];
  const ids=Object.fromEntries(['product-search','result-count','no-results','selected-count','selected-help','clear-selection','quote-link','selection-status'].map(id=>['#'+id,new Element()]));
  ids['.hero-actions [data-contact]']=new Element();ids['.campaign-box [data-contact]']=new Element();
  const document={querySelector:s=>{assert.ok(ids[s],s);return ids[s];},querySelectorAll:s=>({'.product-card':cards,'[data-select]':buttons,'[data-filter]':filters,'[data-contact]':contacts,'[data-campaign-text]':expired})[s]};
  const clock=class extends Date { static now(){return Date.parse(now);} };
  vm.runInNewContext(read('tr4/app.js'),{window:{TR4_PRODUCTS:products},document,Date:clock,sessionStorage:{getItem:()=>stored,setItem:(_,v)=>{stored=v;}}});
  return {cards,buttons,filters,contacts,expired,ids};
}
const ui=boot('2026-11-30T23:59:00-03:00');
ui.buttons[0].click();ui.buttons[1].click();
let link=new URL(ui.ids['#quote-link'].href);
assert.equal(link.hostname,'wa.me');assert.equal(link.pathname,'/5531973589165');
assert.ok(link.searchParams.get('text').includes(products[0].codigo));
assert.ok(link.searchParams.get('text').includes(products[1].codigo));
assert.equal(ui.ids['#selected-count'].textContent,'2 kits selecionados');
ui.filters[2].click();
assert.equal(ui.cards.filter(c=>!c.hidden).length,products.filter(p=>p.category==='bracos').length);
assert.equal(ui.ids['#selected-count'].textContent,'2 kits selecionados','Filtro não deve apagar a cotação');
ui.filters[0].click();ui.ids['#product-search'].value='cambio';ui.ids['#product-search'].events.input();
assert.equal(ui.cards.filter(c=>!c.hidden).length,1,'Busca sem acento encontra câmbio');
ui.ids['#product-search'].value='inexistente';ui.ids['#product-search'].events.input();
assert.equal(ui.ids['#no-results'].hidden,false);
ui.buttons[0].click();assert.ok(!new URL(ui.ids['#quote-link'].href).searchParams.get('text').includes(products[0].codigo));
ui.ids['#clear-selection'].click();assert.equal(ui.ids['#clear-selection'].hidden,true);
assert.ok(new URL(ui.contacts[0].href).searchParams.get('text').includes('campanha'));
const after=boot('2026-12-01T00:00:00-03:00','["KIT10055","KIT_INVALIDO"]');
assert.equal(after.expired[0].textContent,'Texto sem promoção');
assert.ok(!new URL(after.contacts[0].href).searchParams.get('text').includes('campanha'));
assert.equal(after.ids['#selected-count'].textContent,'1 kit selecionado');
boot('2026-11-20T00:00:00-03:00','invalid-json');
console.log(`OK: ${products.length} kits, recursos locais, filtros, cotação, remoção, persistência e término da campanha no horário de Brasília.`);
