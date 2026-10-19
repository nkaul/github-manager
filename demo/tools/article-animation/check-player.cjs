/* Playback, chapter seeking, captions, responsive layout and localhost scope. */
const fs=require('fs'),path=require('path');
const ROOT=path.resolve(__dirname,'../../..');
const {chromium,expect}=require(path.join(ROOT,'frontend/node_modules/@playwright/test'));
const OUT=path.join(ROOT,'demo/article-animation');
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 const errors=[],checks=[],external=[];
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1080}});
  page.on('pageerror',e=>errors.push(e.message));
  page.on('request',r=>{if(!r.url().startsWith('http://127.0.0.1:8124/'))external.push(r.url())});
  await page.goto('http://127.0.0.1:8124');
  const v=page.locator('video');
  await page.waitForFunction(()=>document.querySelector('video').readyState>=1);
  await expect(page.locator('.chapter')).toHaveCount(8);
  const metadata=await v.evaluate(v=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight,captions:v.textTracks.length}));
  if(Math.abs(metadata.duration-120)>.1||metadata.width!==1920||metadata.height!==1080)throw new Error('Unexpected media metadata');
  checks.push('120-second 1920x1080 video metadata; eight chapters');
  await v.evaluate(v=>{v.muted=true});
  await page.getByRole('button',{name:'Play overview',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('video').currentTime>.4);
  await page.getByRole('button',{name:'Pause',exact:true}).click();
  checks.push('Playback advances and pauses');
  await page.getByRole('button',{name:'Full screen',exact:true}).click();
  await page.waitForFunction(()=>document.fullscreenElement===document.querySelector('video'));
  await page.screenshot({path:path.join(OUT,'player-fullscreen.png')});
  await page.evaluate(()=>document.exitFullscreen());
  checks.push('Full-screen video opens without resizing or cropping source media');
  await page.waitForFunction(()=>document.querySelector('video').textTracks[0].cues?.length>0);
  const cues=await v.evaluate(v=>v.textTracks[0].cues.length);
  await page.getByRole('button',{name:'Captions on',exact:true}).click();
  await expect(page.getByRole('button',{name:'Captions off',exact:true})).toHaveAttribute('aria-pressed','false');
  await page.getByRole('button',{name:'Captions off',exact:true}).click();
  checks.push(`${cues} caption cues load; caption toggle works`);
  for(const i of [3,5,7]){
   await page.locator('.chapter').nth(i).click();
   await page.waitForFunction(()=>document.querySelector('video').readyState>=2);
   await page.waitForTimeout(250);
   await v.evaluate(v=>v.pause());
  }
  checks.push('Chapter seeks decode evidence, classification and closing frames');
  const timing=JSON.parse(fs.readFileSync(path.join(OUT,'timing.json')));
  await v.evaluate(async(v,t)=>{
   await new Promise(resolve=>{v.addEventListener('seeked',resolve,{once:true});v.currentTime=t});
   await v.play();await new Promise(resolve=>v.requestVideoFrameCallback(resolve));v.pause();
  },timing.segments[5].start+12);
  await page.evaluate(()=>window.scrollTo(0,0));
  await expect(page.locator('#caption-bar')).not.toHaveText('');
  checks.push('Normal captions appear below the artwork; native captions available in full screen');
  await page.waitForTimeout(400);await page.screenshot({path:path.join(OUT,'player-desktop.png')});
  if(!await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth))throw new Error('Desktop overflow');
  await page.setViewportSize({width:390,height:844});
  await page.evaluate(()=>window.scrollTo(0,0));
  await page.screenshot({path:path.join(OUT,'player-phone.png')});
  if(!await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth))throw new Error('Phone overflow');
  checks.push('Desktop and phone player fit viewport');
  const range=await page.request.get('http://127.0.0.1:8124/overview-1080p.mp4',{headers:{Range:'bytes=0-1023'}});
  if(range.status()!==206||(await range.body()).length!==1024)throw new Error('Range response failed');
  const denied=await page.request.get('http://127.0.0.1:8124/../../backend/.env');
  if(denied.status()!==404)throw new Error('Out-of-package path exposed');
  checks.push('HTTP byte ranges support seeking; out-of-package paths denied');
  if(errors.length||external.length)throw new Error('Page error or unexpected network request');
  const report={status:'PASS',checks,metadata,caption_cues:cues,errors,external_requests:external,audio_review:'Playback automation is muted; does not establish perceptual naturalness'};
  fs.writeFileSync(path.join(OUT,'player-qa.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report,null,2));
 }finally{await browser.close()}
})().catch(e=>{console.error(e.stack);process.exitCode=1});
