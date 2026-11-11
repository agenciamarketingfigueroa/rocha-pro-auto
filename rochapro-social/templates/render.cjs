// npm install playwright sharp (or set NODE_PATH to an existing installation).
const fs=require('node:fs/promises');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require('playwright');
const sharp=require('sharp');
const root=path.resolve(__dirname,'..');
const names=['01-automotive-hero','02-industrial-product','03-engineering-view'];
(async()=>{
 const executablePath=process.env.CHROME_PATH || (process.platform==='win32'?'C:/Program Files/Google/Chrome/Application/chrome.exe':undefined);
 const browser=await chromium.launch({headless:true,executablePath,args:['--force-color-profile=srgb']});
 const page=await browser.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:1});
 const report=[];
 for(const name of names){
  await page.goto(pathToFileURL(path.join(root,'posts',name+'.html')).href);
  await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()));});
  const checks=await page.evaluate(()=>({font:document.fonts.check('800 80px Montserrat'),art:{width:document.querySelector('.art').offsetWidth,height:document.querySelector('.art').offsetHeight},images:[...document.images].every(i=>i.naturalWidth>0),textOutside:[...document.querySelectorAll('h1,h2,p,.eyebrow,.code,.footer')].filter(e=>{let r=e.getBoundingClientRect();return r.left<0||r.top<0||r.right>1080||r.bottom>1350}).map(e=>e.textContent)}));
  if(!checks.font||!checks.images||checks.textOutside.length)throw Error(JSON.stringify(checks));
  const pixels=await page.screenshot({type:'png'});
  await sharp(pixels).withIccProfile('srgb').png().toFile(path.join(root,'posts',name+'.png'));
  await sharp(pixels).withIccProfile('srgb').jpeg({quality:94,chromaSubsampling:'4:4:4'}).toFile(path.join(root,'posts',name+'.jpg'));
  await sharp(pixels).resize(432,540).png().toFile(path.join(root,'previews',name+'.png'));
  const meta=await sharp(path.join(root,'posts',name+'.png')).metadata();
  report.push({name,...checks,width:meta.width,height:meta.height,space:meta.space,icc:!!meta.icc});
 }
 await page.goto(pathToFileURL(path.join(root,'previews','conceitos.html')).href);await page.setViewportSize({width:1680,height:1080});
 await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()));});
 await sharp(await page.screenshot({type:'png',fullPage:true})).withIccProfile('srgb').png().toFile(path.join(root,'previews','tres-conceitos.png'));
 await fs.writeFile(path.join(root,'previews','export-checks.json'),JSON.stringify(report,null,2));
 await browser.close();console.log(JSON.stringify(report,null,2));
})().catch(e=>{console.error(e);process.exit(1)});
