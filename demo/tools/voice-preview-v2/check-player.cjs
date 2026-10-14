const fs=require('node:fs');
const path=require('node:path');
const {chromium,expect}=require('../../../frontend/node_modules/@playwright/test');
const ROOT=path.resolve(__dirname,'../../..'),OUT=path.join(ROOT,'demo/voice-preview-v2');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:8122/');
  await expect(page.locator('#rate-A')).toContainText('words/min');
  const qa=JSON.parse(fs.readFileSync(path.join(OUT,'media-qa.json')));const checks=[];
  for(const v of qa.variants){
   await page.locator(`button[data-id="${v.variant}"]`).click();
   await expect(page.locator('#current')).toContainText(v.voice[0].toUpperCase()+v.voice.slice(1));
   await expect.poll(()=>page.locator('video').evaluate(e=>e.readyState)).toBeGreaterThanOrEqual(1);
   const meta=await page.locator('video').evaluate(v=>({width:v.videoWidth,height:v.videoHeight,duration:v.duration,error:v.error?.message}));
   expect(meta).toEqual({width:1920,height:1080,duration:60,error:undefined});
   const timings=JSON.parse(fs.readFileSync(path.join(OUT,v.variant+'-timing.json')));
   for(const s of timings.segments){
    await page.locator('video').evaluate((v,t)=>new Promise(resolve=>{v.addEventListener('seeked',resolve,{once:true});v.currentTime=t;}),s.start+1);
   }
   await page.locator('video').evaluate(v=>{v.muted=true;v.currentTime=1;return v.play();});
   await page.waitForTimeout(1100);
   expect(await page.locator('video').evaluate(v=>v.currentTime)).toBeGreaterThan(1.5);
   await page.locator('video').evaluate(v=>v.pause());
   await expect.poll(()=>page.locator('video').evaluate(v=>v.textTracks[0]?.cues?.length||0)).toBeGreaterThan(10);
   const range=await page.request.get('http://127.0.0.1:8122/'+v.video,{headers:{Range:'bytes=0-99'}});
   expect(range.status()).toBe(206);expect((await range.body()).length).toBe(100);
   checks.push({variant:v.variant,...meta,chapterSeeks:8,captionCues:await page.locator('video').evaluate(v=>v.textTracks[0].cues.length),rangeStatus:range.status(),playbackAdvances:true});
  }
  await page.locator('button[data-id="A"]').click();
  await expect.poll(()=>page.locator('video').evaluate(v=>v.readyState)).toBeGreaterThanOrEqual(2);
  await page.locator('video').evaluate(v=>{v.muted=false;v.pause();v.currentTime=0;});
  await page.screenshot({path:path.join(OUT,'comparison-desktop.png'),fullPage:true});
  for(const width of [1280,390]){
   await page.setViewportSize({width,height:900});
   expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
  }
  await page.screenshot({path:path.join(OUT,'comparison-phone.png'),fullPage:true});
  expect(errors).toEqual([]);
  const result={status:'PASS',checks,errors,responsiveWidths:[1440,1280,390],auditoryQuality:'Awaiting user audition; muted playback checks validate technical playback only'};
  fs.writeFileSync(path.join(OUT,'player-qa.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
 }finally{await browser.close();}
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
