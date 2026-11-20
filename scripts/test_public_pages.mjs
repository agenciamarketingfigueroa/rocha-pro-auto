import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import {models,selectProducts} from '../content/models.mjs';
import {posts} from '../content/posts.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const catalogScope={window:{}};
vm.runInNewContext(read('data/catalogo-publico.js'),catalogScope);
class Element {
  constructor(dataset={}){this.dataset=dataset;this.events={};this.attributes={};this.hidden=false;this.value='';this.textContent='';this.classes=new Set();this.classList={toggle:(name,value)=>value?this.classes.add(name):this.classes.delete(name)};}
  setAttribute(k,v){this.attributes[k]=v;}
  addEventListener(k,fn){this.events[k]=fn;}
  click(){this.events.click();}
  focus(){this.focused=true;}
}
const storage=new Map();
function boot(slug,brokenStorage=false){
  const scope={window:{}};
  vm.runInNewContext(read(`${slug}/products.js`),scope);
  const {products}=scope.window.ROCHAPRO_MODEL;
  const cards=products.map(p=>new Element({code:p.codigo}));
  const buttons=products.map(p=>new Element({select:p.codigo}));
  const filters=['all',...new Set(products.map(p=>p.category))].map(filter=>new Element({filter}));
  const ids=Object.fromEntries(['product-search','result-count','no-results','selected-count','selected-help','clear-selection','quote-link','selection-status'].map(id=>['#'+id,new Element()]));
  const contacts=[new Element()];
  const document={querySelector:s=>{assert.ok(ids[s],s);return ids[s];},querySelectorAll:s=>({'.product-card':cards,'[data-select]':buttons,'[data-filter]':filters,'[data-contact]':contacts})[s]};
  vm.runInNewContext(read('assets/site/models.js'),{...scope,document,sessionStorage:{getItem:k=>{if(brokenStorage)throw Error('unavailable');return storage.get(k);},setItem:(k,v)=>{if(brokenStorage)throw Error('unavailable');storage.set(k,v);}}});
  return {products,cards,buttons,filters,ids,contacts};
}
for(const model of models){
  const ui=boot(model.slug);
  assert.deepEqual([...ui.products.map(p=>p.codigo)].sort(),[...selectProducts(model,catalogScope.window.ROCHAPRO_CATALOG).map(p=>p.codigo)].sort());
  ui.buttons[0].click();ui.buttons[1].click();
  const link=new URL(ui.ids['#quote-link'].href);
  assert.equal(link.hostname,'wa.me');assert.equal(link.pathname,'/5531973589165');
  assert.ok(link.searchParams.get('text').includes(ui.products[0].codigo));
  assert.ok(link.searchParams.get('text').includes(ui.products[1].codigo));
  assert.equal(ui.ids['#selected-count'].textContent,'2 kits selecionados');
  ui.filters[1].click();
  assert.equal(ui.cards.filter(c=>!c.hidden).length,ui.products.filter(p=>p.category===ui.filters[1].dataset.filter).length);
  assert.equal(ui.ids['#selected-count'].textContent,'2 kits selecionados');
  ui.filters[0].click();
  ui.ids['#product-search'].value=ui.products[0].codigo.toLowerCase();ui.ids['#product-search'].events.input();
  assert.equal(ui.cards.filter(c=>!c.hidden).length,1);
  ui.ids['#product-search'].value='buchas inexistentes xyz';ui.ids['#product-search'].events.input();
  assert.equal(ui.ids['#no-results'].hidden,false);
  ui.ids['#product-search'].value='amortecedor';ui.ids['#product-search'].events.input();
  assert.ok(ui.cards.some(c=>!c.hidden));
  assert.equal(boot(model.slug).ids['#selected-count'].textContent,'2 kits selecionados');
  ui.buttons[0].click();
  assert.ok(!new URL(ui.ids['#quote-link'].href).searchParams.get('text').includes(ui.products[0].codigo));
  ui.ids['#clear-selection'].click();assert.equal(ui.ids['#clear-selection'].hidden,true);
  assert.ok(ui.ids['#quote-link'].focused);
  storage.set(`rochapro-${model.slug}-selection`,'["KIT_INVALIDO"]');
  assert.equal(boot(model.slug).ids['#selected-count'].textContent,'Monte sua cotação');
  storage.set(`rochapro-${model.slug}-selection`,'not-json');boot(model.slug);boot(model.slug,true);
}
storage.clear();const troller=boot('troller');troller.buttons[0].click();assert.equal(boot('hilux').ids['#selected-count'].textContent,'Monte sua cotação');
const filters=['all','tr4','troller','hilux','frontier','expedicao'].map(topic=>new Element({topic}));
const articleCards=posts.map(p=>new Element({postTopics:p.topics.join(' ')}));
const status=new Element();
vm.runInNewContext(read('assets/site/editorial.js'),{document:{querySelector:s=>{assert.equal(s,'#post-count');return status;},querySelectorAll:s=>s==='[data-topic]'?filters:articleCards}});
for(const button of filters){button.click();assert.equal(articleCards.filter(p=>!p.hidden).length,posts.filter(p=>button.dataset.topic==='all'||p.topics.includes(button.dataset.topic)).length);assert.equal(button.attributes['aria-pressed'],'true');}
console.log('OK: catálogo completo por modelo; filtros, busca, cotação, remoção, persistência isolada, armazenamento indisponível e filtros do blog.');
