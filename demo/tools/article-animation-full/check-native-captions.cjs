/* Focused 1080p full-screen caption visibility check, after broad player QA. */
const fs=require('fs'),path=require('path');
const ROOT=path.resolve(__dirname,'../../..'),OUT=path.join(ROOT,'demo/article-animation-full');
const {chromium}=require(path.join(ROOT,'frontend/node_modules/@playwright/test'));
const timing=JSON.parse(fs.readFileSync(path.join(OUT,'timing.json')));
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1920,height:1080}});
  await page.goto('http://127.0.0.1:8125');
  await page.waitForFunction(()=>document.querySelector('video').readyState>=2);
  const beat=timing.beats.find(b=>b.id==='07-retrieval-03');
  await page.locator('video').evaluate(async(v,t)=>{v.muted=true;v.currentTime=t;await v.play()},beat.audio_end-12);
  await page.getByRole('button',{name:'Full screen',exact:true}).click();
  await page.waitForFunction(()=>document.fullscreenElement===document.querySelector('video')&&document.querySelector('video').textTracks[0].mode==='showing');
  await page.mouse.move(1,1);await page.waitForTimeout(3500);
  await page.waitForFunction(()=>document.querySelector('video').textTracks[0].activeCues?.length>0);
  await page.screenshot({path:path.join(OUT,'player-fullscreen.png')});
  const state=await page.locator('video').evaluate(v=>({width:v.videoWidth,height:v.videoHeight,time:v.currentTime,caption_mode:v.textTracks[0].mode,active_caption:Array.from(v.textTracks[0].activeCues).map(c=>c.text).join(' ')}));
  if(state.width!==1920||state.height!==1080)throw Error('Full-screen source resolution mismatch');
  await page.evaluate(()=>document.exitFullscreen());
  await page.waitForFunction(()=>document.querySelector('video').textTracks[0].mode==='hidden');
  const qa=JSON.parse(fs.readFileSync(path.join(OUT,'player-qa.json')));qa.fullscreen_1080p_native_captions={status:'PASS',...state};
  fs.writeFileSync(path.join(OUT,'player-qa.json'),JSON.stringify(qa,null,2));
  console.log(JSON.stringify(qa.fullscreen_1080p_native_captions,null,2));
 }finally{await browser.close()}
})().catch(e=>{console.error(e.stack);process.exitCode=1});
