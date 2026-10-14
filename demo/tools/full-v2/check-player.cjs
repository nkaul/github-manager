/* Technical playback only: muted automation does not assess subjective voice quality. */
const fs=require('node:fs'),path=require('node:path');
const {chromium,expect}=require('../../../frontend/node_modules/@playwright/test');
const ROOT=path.resolve(__dirname,'../../..'),OUT=path.join(ROOT,'demo/full-v2');
(async()=>{
 const browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8123');await expect(page.locator('#chapters button')).toHaveCount(32);const video=page.locator('#video');
 await video.evaluate(v=>{v.muted=true;});await video.evaluate(v=>v.play());await page.waitForFunction(()=>document.getElementById('video').currentTime>.2);
 const properties=await video.evaluate(v=>({width:v.videoWidth,height:v.videoHeight,duration:v.duration,audioTracks:v.audioTracks?.length,readyState:v.readyState,captions:v.textTracks.length}));
 expect(properties.width).toBe(1920);expect(properties.height).toBe(1080);expect(properties.captions).toBe(1);
 const chapters=JSON.parse(fs.readFileSync(path.join(OUT,'chapters.json')));const seeks=[];
 for(const c of chapters){await page.locator('#chapters button[data-id="'+c.id+'"]').click();await page.waitForFunction(t=>Math.abs(document.getElementById('video').currentTime-t)<1.5&&document.getElementById('video').readyState>=2,c.start);seeks.push({id:c.id,target:c.start,actual:await video.evaluate(v=>v.currentTime),status:'PASS'});}
 await video.evaluate(v=>{v.pause();v.currentTime=3;});await page.waitForFunction(()=>document.getElementById('video').readyState>=2);await page.screenshot({path:path.join(OUT,'player-desktop.png')});
 await page.getByRole('button',{name:'Fullscreen',exact:true}).click();await page.waitForFunction(()=>!!document.fullscreenElement);await page.screenshot({path:path.join(OUT,'player-fullscreen.png')});await page.evaluate(()=>document.exitFullscreen());
 await page.getByText('Listen without video',{exact:true}).click();await page.locator('#audio').evaluate(a=>{a.muted=true;return a.play();});await page.waitForFunction(()=>document.getElementById('audio').currentTime>.2);const audioProperties=await page.locator('#audio').evaluate(a=>({duration:a.duration,readyState:a.readyState}));expect(Math.abs(audioProperties.duration-properties.duration)).toBeLessThan(.2);await page.locator('#audio').evaluate(a=>a.pause());
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(OUT,'player-phone.png')});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
 const range=await page.request.get('http://127.0.0.1:8123/github-manager-full-cedar-calm-1080p.mp4',{headers:{Range:'bytes=0-1023'}});expect(range.status()).toBe(206);expect((await range.body()).length).toBe(1024);
 for(const disallowed of ['../tools/full-v2/workspace_server.py','speech.py','aligned.wav']){expect((await page.request.get('http://127.0.0.1:8123/'+disallowed)).status()).toBe(404);}
 expect(errors).toEqual([]);const result={status:'PASS',properties,audioProperties,chapter_seeks:seeks,range_status:206,desktop_viewport:{width:1440,height:1000},phone_viewport:{width:390,height:844},phone_overflow:false,fullscreen:'PASS',errors,note:'Playback is muted during automation. Subjective naturalness remains based on the user-selected Cedar pilot and final listening review.'};fs.writeFileSync(path.join(OUT,'player-qa.json'),JSON.stringify(result,null,2));await browser.close();console.log(JSON.stringify({status:'PASS',chapters:seeks.length,...properties}));
})().catch(e=>{console.error(e.message.split('Call log:')[0]);process.exitCode=1;});
