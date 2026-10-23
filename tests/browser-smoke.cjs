// Isolated headless browser; never touches the user's browser profile.
const {chromium}=require('playwright');
const fs=require('node:fs');const path=require('node:path');const http=require('node:http');const assert=require('node:assert/strict');
async function main(){
 const root=path.resolve(__dirname,'../assets/open-cowart-canvas');
 const out=path.resolve(process.argv[2]);fs.mkdirSync(out,{recursive:true});
 const server=http.createServer((req,res)=>{const file=path.resolve(root,'.'+decodeURIComponent(req.url.split('?')[0]));if(!file.startsWith(root+path.sep)){res.writeHead(403).end();return;}fs.readFile(file,(err,data)=>{if(err){res.writeHead(404).end();return;}res.setHeader('Content-Type',file.endsWith('.js')?'application/javascript':file.endsWith('.css')?'text/css':'text/html');res.end(data);});});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 let browser;const errors=[];const dialogs=[];
 try{
  const binaries=['C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe','C:/Program Files/Google/Chrome/Application/chrome.exe'];
  const executablePath=binaries.find(f=>fs.existsSync(f));
  browser=await chromium.launch({headless:true,...(executablePath?{executablePath}:{})});
  const context=await browser.newContext({acceptDownloads:true});const page=await context.newPage();
  page.on('pageerror',e=>errors.push(e.message));page.on('dialog',async d=>{dialogs.push(d.message());await d.dismiss();});
  await page.goto(`http://127.0.0.1:${server.address().port}/nine-grid.html`);
  await page.locator('#durationInput').waitFor();
  const fixture=await page.evaluate(()=>{
   const p=createDefaultProject();p.script_name='v8-isolated-test';const b=p.segments[0];
   b.events_complete=true;b.source_coverage_checked=true;b.video_master_prompt='完整主稿，包括未入格对白。';
   b.events=Array.from({length:12},(_,i)=>({id:'E'+i,start:i,end:i+1,body:'原事件'+i,source_ids:['S1'],dialogues:i===10?[{text:'未入格对白'}]:[]}));
   b.panels.forEach((x,i)=>{x.event_ids=['E'+i];x.sample_time=i+.5;});return p;
  });
  const file=path.join(out,'fixture.json');fs.writeFileSync(file,JSON.stringify(fixture));
  await page.locator('#packageInput').setInputFiles(file);
  await page.waitForFunction(()=>project.script_name==='v8-isolated-test');
  assert.equal(await page.evaluate(()=>project.segments[0].events.length),12);
  await page.locator('#durationInput').fill('9');await page.locator('#durationInput').blur();
  assert.equal(await page.locator('#totalDuration').textContent(),'12.00s');
  assert.deepEqual(await page.evaluate(()=>project.segments[0].events),fixture.segments[0].events);
  const downloadPromise=page.waitForEvent('download');await page.locator('#saveProject').click();const download=await downloadPromise;const saved=path.join(out,'saved-project.json');await download.saveAs(saved);
  assert.deepEqual(JSON.parse(fs.readFileSync(saved,'utf8')).segments[0].events,fixture.segments[0].events);
  const htmlPromise=page.waitForEvent('download');await page.locator('#exportReviewHtml').click();const htmlDownload=await htmlPromise;const savedHtml=path.join(out,'saved-page.html');await htmlDownload.saveAs(savedHtml);
  const offline=await context.newPage();offline.on('pageerror',e=>errors.push(e.message));await offline.goto('file:///'+savedHtml.replaceAll('\\','/'));await offline.locator('#durationInput').waitFor();
  assert.equal(await offline.evaluate(()=>project.segments[0].events.length),12);
  assert.equal(await offline.evaluate(()=>typeof NineGridEvents.refresh),'function');
  // A legacy project may still be saved, but UI must not let it finalize.
  const legacy=structuredClone(fixture);delete legacy.segments[0].events;delete legacy.segments[0].events_complete;legacy.script_name='legacy';fs.writeFileSync(file,JSON.stringify(legacy));
  await page.locator('#packageInput').setInputFiles(file);await page.waitForFunction(()=>project.script_name==='legacy');await page.locator('#toggleComplete').click();
  assert.ok(dialogs.some(d=>d.includes('完整事件')));assert.equal(await page.evaluate(()=>project.segments[0].completed),false);
  assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(out,'browser-result.json'),JSON.stringify({passed:true,checks:['import preserves 12 events','panel edit retains events','duration from events','JSON export retains events','saved HTML reload embeds event core','legacy finalize blocked'],dialogs,errors},null,2));
  console.log('PASS: 6 isolated browser smoke scenarios. No image/video generation tested.');
 }finally{if(browser)await browser.close();await new Promise(r=>server.close(r));}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
