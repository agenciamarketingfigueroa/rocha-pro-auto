import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {communityPosts, blogVehicles} from '../content/posts-community.mjs';
import {posts,sources} from '../content/posts.mjs';
import {models,selectProducts} from '../content/models.mjs';
const scope={window:{}};
vm.runInNewContext(fs.readFileSync('data/catalogo-publico.js','utf8'),scope);
const catalog=scope.window.ROCHAPRO_CATALOG;
const selections={tr4:catalog.filter(p=>/\btr\s*4\b/i.test(p.nome))};
for(const m of models) selections[m.slug]=selectProducts(m,catalog);
for(const m of blogVehicles) selections[m.slug]=catalog.filter(p=>m.pattern.test(p.nome));
assert.equal(communityPosts.length,30);
assert.equal(posts.length,36);
assert.equal(new Set(posts.map(p=>p.slug)).size,36);
for(const p of communityPosts){
  assert.ok(p.kits.length>0,p.slug);
  assert.ok(p.sections.length>=4,p.slug);
  const text=p.intro+' '+p.sections.map(s=>s.title+' '+s.html.replace(/<[^>]+>/g,' ')).join(' ');
  assert.ok(text.split(/\s+/).length>=260,p.slug+' must contain a complete article');
  assert.match(p.sections.at(-1).html,/RochaPro/);
  for(const id of p.sources) assert.ok(sources[id],id);
  for(const [model,code] of p.kits) assert.ok(selections[model]?.some(p=>p.codigo===code),`${p.slug}: ${code} / ${model}`);
  assert.ok(fs.existsSync('.'+p.image),p.image);
}
fs.writeFileSync('docs/serie-blog-comunidades.json',JSON.stringify({date:'2026-11-20',articles:communityPosts.map((p,i)=>({number:i+7,title:p.title,model:p.topics[0],category:p.category,url:'/blog/'+p.slug+'/',kits:p.kits.map(k=>k[1])})),catalogCounts:Object.fromEntries(Object.entries(selections).map(([m,p])=>[m,p.length]))},null,2)+'\n');
console.log('OK: 30 artigos novos, conteúdo completo, CTAs, fontes e todos os kits correspondentes aos modelos.');
