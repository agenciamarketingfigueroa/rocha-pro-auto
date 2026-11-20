const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const inventory=JSON.parse(fs.readFileSync('docs/serie-blog-comunidades.json','utf8'));
const base='http://127.0.0.1:4173';
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base+'/blog/',{waitUntil:'networkidle'});
 assert.equal(await page.locator('[data-post-topics]').count(),36);
 const topics=await page.locator('[data-topic]').evaluateAll(ns=>ns.map(n=>n.dataset.topic));
 for(const topic of topics){
  await page.locator(`[data-topic="${topic}"]`).click();
  const expected=await page.locator('[data-post-topics]').evaluateAll((ns,t)=>ns.filter(n=>t==='all'||n.dataset.postTopics.split(' ').includes(t)).length,topic);
  assert.equal(await page.locator('[data-post-topics]:visible').count(),expected,topic);
 }
 await page.locator('[data-topic="ranger"]').click();
 await page.locator('.blog-filter').scrollIntoViewIfNeeded();
 await page.screenshot({path:'.tmp/community-report/blog-desktop.png'});
 const catalogLinks=new Map();
 for(const article of inventory.articles){
  await page.goto(base+article.url,{waitUntil:'domcontentloaded'});
  assert.equal(await page.locator('h1').innerText(),article.title);
  assert.equal(await page.locator('#kits-relacionados .kit-link').count(),article.kits.length);
  const hrefs=await page.locator('#kits-relacionados .kit-link a').evaluateAll(ns=>ns.map(n=>n.getAttribute('href')));
  hrefs.forEach((h,i)=>{if(h.startsWith('/catalogo'))catalogLinks.set(h,article.kits[i]);});
  await page.setViewportSize({width:390,height:844});
  await page.evaluate(()=>document.fonts.ready);
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1),article.url+' mobile overflow');
  if(article.model==='jimny'&&article.url.includes('sierra')){
   await page.locator('#kits-relacionados').scrollIntoViewIfNeeded();
   await page.screenshot({path:'.tmp/community-report/jimny-mobile-kits.png'});
  }
  if(article.model==='tr4'&&article.url.includes('comunidade')){
   await page.screenshot({path:'.tmp/community-report/article-mobile.png'});
  }
  await page.setViewportSize({width:1440,height:1000});
 }
 for(const [href,code] of catalogLinks){
  await page.goto(base+href,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>document.querySelector('#result-count')?.textContent!=='—');
  assert.ok((await page.locator('#products .code').allTextContents()).includes(code),href);
 }
 await page.goto(base+'/blog/',{waitUntil:'domcontentloaded'});
 await page.setViewportSize({width:390,height:844});
 await page.locator('[data-topic="jimny"]').click();
 assert.equal(await page.locator('[data-post-topics]:visible').count(),2);
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1),'blog mobile overflow');
 assert.deepEqual(errors,[]);
 await browser.close();
 console.log(`OK: 30 articles, ${topics.length} filters, mobile layout and ${catalogLinks.size} kit destinations.`);
})().catch(e=>{console.error(e);process.exit(1)});
