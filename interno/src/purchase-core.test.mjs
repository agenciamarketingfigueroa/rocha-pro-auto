import test from 'node:test';
import assert from 'node:assert/strict';
import { parsePart, compositionParts, addToOrder, findSupplier, resolveKit, purchaseMessage, purchaseUrl } from './purchase-core.mjs';
const kits = [
  {codigo:'KIT10051',descricao:'Kit L200',composicao:'0811: 06 PC / 3013: 04 PC'},
  {codigo:'KIT10110',descricao:'Kit Pampa',composicao:'3010: 02 PC / 0811: 02 PC'},
];
test('whole kits multiply every component and repeated supplier codes accumulate',()=>{
  const first=addToOrder([],compositionParts(kits[0].composicao).map(parsePart),3);
  const order=addToOrder(first,compositionParts(kits[1].composicao).map(parsePart),2);
  assert.deepEqual(order,[{code:'0811',quantity:22,unit:'PC'},{code:'3013',quantity:12,unit:'PC'},{code:'3010',quantity:4,unit:'PC'}]);
  assert.equal(first[0].quantity,18);
});
test('supplier lookup preserves leading zeros and does not add every kit containing a part',()=>{
  assert.equal(findSupplier(' 0811 ',kits).length,2);
  assert.equal(findSupplier('811',kits).length,0);
  const order=addToOrder([],[{code:'0811',quantity:10,unit:'PC'}]);
  assert.equal(order[0].quantity,10);
  assert.equal(resolveKit('51',kits).codigo,'KIT10051');
  assert.equal(resolveKit('kit 110',kits).codigo,'KIT10110');
});
test('piece units normalize but pairs and supplier kits remain separate',()=>{
  assert.equal(parsePart('0811: 04 PEÇAS').unit,'PC');
  assert.equal(parsePart('9004: 01 KIT (C/ 06 PEÇAS)').quantity,1);
  const result=addToOrder([],[parsePart('0811: 02 PC'),parsePart('0811: 01 PAR')]);
  assert.equal(result.length,2);
});
test('missing or ambiguous amounts and placeholder codes require review',()=>{
  for(const raw of ['0811','0811: 04','0811: 02 PC ou 3013: 02 PC','0913/0914: 04 PC CADA','0000: 02 PC (SOB MEDIDA)']){
    assert.throws(()=>addToOrder([],[parsePart(raw)]),/Confira/);
  }
  assert.equal(parsePart('PN13423: 12 PC').code,'PN13423');
  assert.equal(parsePart('PN13423: 12 PC').external,true);
});
test('invalid amounts and overflow do not partially modify the order',()=>{
  const order=[{code:'0811',quantity:999998,unit:'PC'}];
  for(const quantity of [0,-1,1.5,NaN,Infinity]) assert.throws(()=>addToOrder(order,[{code:'3013',quantity,unit:'PC'}]));
  assert.throws(()=>addToOrder(order,[{code:'3013',quantity:4,unit:'PC'},{code:'0811',quantity:2,unit:'PC'}]));
  assert.deepEqual(order,[{code:'0811',quantity:999998,unit:'PC'}]);
});
test('WhatsApp message contains only remaining supplier codes and amounts, addressed to Tigrinho',()=>{
  const order=addToOrder([],compositionParts(kits[0].composicao).map(parsePart),2).filter(item=>item.code!=='3013');
  order[0].quantity=25;
  const message=purchaseMessage(order),url=new URL(purchaseUrl(order));
  assert.match(message,/Fala, Tigrinho!/);
  assert.match(message,/25 PC — código 0811/);
  assert.doesNotMatch(message,/3013|KIT10051|L200|Pampa/);
  assert.equal(url.pathname,'/5531971606904');
  assert.equal(url.searchParams.get('text'),message);
  assert.equal(purchaseUrl([]),'');
  assert.equal(purchaseUrl([{code:'0811',quantity:null,unit:'PC'}]),'');
});
