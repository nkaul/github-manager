const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
const ROOT=path.resolve(__dirname,'../../..');const {chromium}=require(path.join(ROOT,'frontend/node_modules/@playwright/test'));
const WORK=path.join(ROOT,'demo/work/article-animation-full');const OUT=path.join(ROOT,'demo/article-animation-full');
const timing=JSON.parse(fs.readFileSync(path.join(WORK,'rehearsal-timing.json')));
(async()=>{const browser=await chromium.launch({channel:'chrome',headless:true,args:['--allow-file-access-from-files','--force-color-profile=srgb']});try{
 const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});await page.route('http://**/*',r=>r.abort());await page.route('https://**/*',r=>r.abort());
 const errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(pathToFileURL(path.join(__dirname,'scene.html')).href);await page.waitForFunction(()=>window.ready);await page.evaluate(t=>window.setTimeline(t),timing);
 const reviews=[];fs.mkdirSync(path.join(WORK,'rehearsal'),{recursive:true});
 for(const b of timing.beats){await page.evaluate(t=>window.seek(t),b.start+(b.end-b.start)*.85);const audit=await page.evaluate(()=>window.audit());reviews.push({beat:b.id,...audit});await page.screenshot({path:path.join(WORK,'rehearsal',b.id+'.png')});}
 const report={status:!errors.length&&reviews.every(r=>!r.bad.length&&r.font)?'PASS':'FAIL',frames:reviews.length,errors,reviews};fs.writeFileSync(path.join(WORK,'visual-rehearsal.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({status:report.status,frames:reviews.length,failures:reviews.filter(r=>r.bad.length)},null,2));if(report.status!=='PASS')process.exitCode=1;
}finally{await browser.close()}})().catch(e=>{console.error(e.stack);process.exitCode=1});
