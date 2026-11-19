import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFile } from 'node:fs/promises';

const template=await readFile(new URL('../pedido-compra.html',import.meta.url),'utf8');
const core=await readFile(new URL('./purchase-core.mjs',import.meta.url),'utf8');
const kits=[
 {codigo:'KIT10051',descricao:'Buchas L200',composicao:'0811: 06 PC / 3013: 04 PC'},
 {codigo:'KIT10003',descricao:'Kit com anotação pendente',composicao:'0301A: 02 / PN13423: 12 PC'},
];
function setup(storage=new Map()){
 class Element {
  constructor(tag){this.tag=tag;this.children=[];this.events={};this.value='';this.id='';this.text='';this.attributes={};}
  set textContent(value){this.text=String(value);this.children=[]}
  get textContent(){return this.text+this.children.map(c=>c.textContent).join('')}
  append(...children){this.children.push(...children)}
  replaceChildren(...children){this.children=children;this.text=''}
  addEventListener(name,fn){this.events[name]=fn}
  setAttribute(key,value){this.attributes[key]=String(value)}
  removeAttribute(key){delete this.attributes[key];delete this[key]}
  focus(){}
 }
 const roots=[];
 for(const match of template.matchAll(/<([a-z]+)\b([^>]*\bid="([^"]+)"[^>]*)>/g)){
  const node=new Element(match[1]);node.id=match[3];node.value=match[2].match(/\bvalue="([^"]*)"/)?.[1]||'';roots.push(node);
 }
 const get=id=>{const visit=node=>node.id===id?node:node.children.map(visit).find(Boolean);return roots.map(visit).find(Boolean)||null};
 get('purchase-mode').value='kit';
 const context=vm.createContext({document:{querySelector:selector=>get(selector.slice(1)),createElement:tag=>new Element(tag)},localStorage:{getItem:key=>storage.get(key)||null,setItem:(key,value)=>storage.set(key,value)},window:{confirm:()=>true},console});
 const source=template.replace('/*__KITS__*/ []',JSON.stringify(kits)).replace('/*__PURCHASE_CORE__*/',core.replace(/^export /gm,''));
 vm.runInContext(source.match(/<script>([\s\S]*?)<\/script>/)[1],context);
 const search=(code,qty)=>{get('purchase-code').value=code;get('purchase-quantity').value=String(qty);get('purchase-search').events.submit({preventDefault(){}})};
 const order=()=>JSON.parse(vm.runInContext('JSON.stringify(order)',context));
 return {get,search,order,context,storage};
}
test('operator adds a kit, excludes another supplier, edits quantity, adds a single part and keeps the draft',()=>{
 const ui=setup();ui.search('51',3);assert.equal(ui.get('add-purchase').disabled,false);ui.get('add-purchase').onclick();
 assert.deepEqual(ui.order(),[{code:'0811',quantity:18,unit:'PC'},{code:'3013',quantity:12,unit:'PC'}]);
 ui.get('order-list').children[1].children[2].onclick();
 const quantity=ui.get('order-list').children[0].children[1];quantity.value='25';quantity.events.input();
 ui.get('purchase-mode').value='supplier';ui.get('purchase-mode').events.change();ui.search('0811',5);ui.get('add-purchase').onclick();
 assert.deepEqual(ui.order(),[{code:'0811',quantity:30,unit:'PC'}]);
 const url=new URL(ui.get('send-order').href),message=url.searchParams.get('text');
 assert.equal(url.pathname,'/5531971606904');assert.match(message,/30 PC — código 0811/);assert.doesNotMatch(message,/3013|KIT10051|Buchas|L200/);
 assert.deepEqual(setup(ui.storage).order(),ui.order());
});
test('an incomplete kit needs manual review, and excluded pieces are not added',()=>{
 const ui=setup();ui.search('3',2);assert.equal(ui.get('add-purchase').disabled,true);
 const qty=ui.get('candidate-qty-0');qty.value='2';qty.oninput();const unit=ui.get('candidate-unit-0');unit.value='PC';unit.onchange();
 assert.equal(ui.get('add-purchase').disabled,false);
 const result=ui.get('purchase-result');const candidates=result.children.filter(c=>c.className==='candidate');
 candidates[1].children.at(-1).children[1].onclick();ui.get('add-purchase').onclick();
 assert.deepEqual(ui.order(),[{code:'0301A',quantity:4,unit:'PC'}]);
});
test('empty and invalid orders cannot open WhatsApp, and clearing resets the saved draft',()=>{
 const ui=setup();assert.equal(ui.get('send-order').href,undefined);ui.search('51',1);ui.get('add-purchase').onclick();
 const qty=ui.get('order-list').children[0].children[1];qty.value='-2';qty.events.input();
 assert.equal(ui.get('send-order').href,undefined);let prevented=false;ui.get('send-order').events.click({preventDefault(){prevented=true}});assert.equal(prevented,true);
 ui.get('clear-order').onclick();assert.deepEqual(ui.order(),[]);assert.deepEqual(setup(ui.storage).order(),[]);
});
test('searching an unknown code does not create a purchase item',()=>{
 const ui=setup();ui.search('9999',1);assert.equal(ui.get('add-purchase'),null);assert.deepEqual(ui.order(),[]);
});
