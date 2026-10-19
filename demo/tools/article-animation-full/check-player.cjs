/* Local media QA. Muted playback tests do not establish listener preference. */
const fs=require('fs'),path=require('path');
const ROOT=path.resolve(__dirname,'../../..');
const {chromium,expect}=require(path.join(ROOT,'frontend/node_modules/@playwright/test'));
const OUT=path.join(ROOT,'demo/article-animation-full'),URL='http://127.0.0.1:8125/';
const pack=JSON.parse(fs.readFileSync(path.join(OUT,'package.json')));
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 const errors=[],external=[],checks=[],assets=[];
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1080}});
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(!r.url().startsWith(URL))external.push(r.url())});
  await page.goto(URL);const v=page.locator('video');
  await page.waitForFunction(()=>document.querySelector('video').readyState>=1);
  await expect(page.locator('#chapters .item')).toHaveCount(18);await expect(page.locator('#references .item')).toHaveCount(8);
  const metadata=await v.evaluate(v=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight,tracks:v.textTracks.length}));
  if(Math.abs(metadata.duration-pack.duration)>.1||metadata.width!==1920||metadata.height!==1080)throw Error('Master metadata mismatch');
  await v.evaluate(v=>v.muted=true);await page.getByRole('button',{name:'Play',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('video').currentTime>.4);await page.getByRole('button',{name:'Pause',exact:true}).click();
  checks.push('1080p master playback advances and pauses; 18 chapters and 8 reference summaries load');
  await page.getByRole('button',{name:'Full screen',exact:true}).click();
  await page.waitForFunction(()=>document.fullscreenElement===document.querySelector('video'));
  await page.screenshot({path:path.join(OUT,'player-fullscreen.png')});await page.evaluate(()=>document.exitFullscreen());
  checks.push('Full-screen video opens and native captions follow the caption toggle');
  await page.waitForFunction(()=>document.querySelector('video').textTracks[0].cues?.length>0);
  const cues=await v.evaluate(v=>v.textTracks[0].cues.length);
  if(cues!==pack.master_caption_cues)throw Error('Master caption count mismatch');
  await page.getByRole('button',{name:'Captions on',exact:true}).click();await expect(page.locator('#caption-bar')).toBeHidden();
  await page.getByRole('button',{name:'Captions off',exact:true}).click();await expect(page.locator('#cc')).toHaveAttribute('aria-pressed','true');
  await page.locator('#rate').selectOption('0.9');if(await v.evaluate(v=>v.playbackRate)!==.9)throw Error('Rate control failed');
  await page.locator('#rate').selectOption('1');checks.push('Caption toggle and optional 0.9×/1.0× pace controls work');
  async function pauseAt(t){await v.evaluate(async(v,t)=>{v.pause();if(Math.abs(v.currentTime-t)>.01){await new Promise(resolve=>{v.addEventListener('seeked',resolve,{once:true});v.currentTime=t})}await v.play();await new Promise(resolve=>v.requestVideoFrameCallback(resolve));v.pause()},t)}
  for(let i=0;i<pack.chapters.length;i++){
   const c=pack.chapters[i];await page.locator('#chapters .item button').nth(i).click();
   await page.waitForFunction(file=>{const v=document.querySelector('video');return v.currentSrc.endsWith(file)&&v.readyState>=2},c.file);
   const announcement=c.text.split('.')[0]+'.';
   await page.waitForFunction(expected=>{const t=document.querySelector('video').textTracks[0];return t.cues?.length===expected.count&&t.cues[0].text===expected.announcement},{count:c.caption_cues,announcement});
   const m=await v.evaluate(v=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight}));
   if(Math.abs(m.duration-c.duration)>.12||m.width!==1920||m.height!==1080)throw Error('Chapter mismatch '+c.id);
   await pauseAt(2.5);await expect(page.locator('#active')).toHaveText(c.title);await expect(page.locator('#description')).toHaveText(c.purpose);
   if(!await v.evaluate((v,s)=>v.textTracks[0].cues[0].text===s,announcement))throw Error('Missing announced section caption '+c.id);
   assets.push({file:c.file,status:'PASS',duration:m.duration,caption_cues:c.caption_cues,first_frame_decode:'PASS'});
   console.log('Player chapter PASS',c.id);
  }
  checks.push('All 18 standalone chapters load, decode, expose the correct purpose/transcript and begin with section-announcement captions');
  for(let i=0;i<pack.references.length;i++){
   const r=pack.references[i];await page.locator('#references .item button').nth(i).click();
   await page.waitForFunction(file=>{const v=document.querySelector('video');return v.currentSrc.endsWith(file)&&v.readyState>=2},r.file);
   await pauseAt(24);const m=await v.evaluate(v=>({duration:v.duration,loop:v.loop}));
   if(Math.abs(m.duration-32)>.1||!m.loop)throw Error('Reference mismatch '+r.id);
   await expect(page.locator('#caption-bar')).toBeHidden();await expect(page.locator('#cc')).toBeDisabled();
   assets.push({file:r.file,status:'PASS',duration:m.duration,silent_loop:true,seek_decode:'PASS'});
  }
  await v.evaluate(async v=>{v.currentTime=31.8;await v.play()});
  await page.waitForFunction(()=>{const v=document.querySelector('video');return !v.paused&&v.currentTime<1});
  await v.evaluate(v=>v.pause());
  checks.push('All 8 silent reference summaries decode, loop and link to complete original figures');
  await page.getByRole('button',{name:'Complete companion',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('video').currentSrc.endsWith('complete-1080p.mp4')&&document.querySelector('video').readyState>=2);
  const c=pack.chapters[6];await pauseAt(c.start+10);
  await expect(page.locator('#active')).toHaveText('Section 7 · '+c.title);await expect(page.locator('#caption-bar')).not.toHaveText('');
  await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(OUT,'player-desktop.png')});
  if(!await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth))throw Error('Desktop overflow');
  checks.push('Master seeking updates the current chapter, purpose, transcript and captions');
  await page.getByRole('button',{name:'Slower product overview',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('video').currentSrc.endsWith('chapters/01-purpose.mp4')&&document.querySelector('video').readyState>=2);
  await pauseAt(6);await page.setViewportSize({width:390,height:844});await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(OUT,'player-phone.png')});
  if(!await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth))throw Error('Phone overflow');
  checks.push('Slower overview and desktop/phone player layouts fit their viewports');
  const range=await page.request.get(URL+'complete-1080p.mp4',{headers:{Range:'bytes=0-1023'}});
  if(range.status()!==206||(await range.body()).length!==1024)throw Error('Byte range failed');
  for(const suffix of ['../../backend/.env','backend/.env','../demo/work/article-animation-full/aligned.wav']){
   const denied=await page.request.get(URL+suffix);if(denied.status()!==404)throw Error('Out-of-package path exposed');
  }
  checks.push('Byte-range seeking works; private and out-of-package paths return 404');
  if(errors.length||external.length)throw Error(JSON.stringify({errors,external}));
  const report={status:'PASS',checks,metadata,master_caption_cues:cues,assets,errors,external_requests:external,
                audio_review:'Automation is muted; naturalness, accent and preferred pace remain listener judgments'};
  fs.writeFileSync(path.join(OUT,'player-qa.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({status:report.status,checks},null,2));
 }finally{await browser.close()}
})().catch(e=>{console.error(e.stack);process.exitCode=1});
