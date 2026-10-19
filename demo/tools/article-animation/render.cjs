/* Deterministic local SVG animation: each encoded frame has an explicit timeline time. */
const fs=require('fs');
const path=require('path');
const {pathToFileURL}=require('url');
const {spawn}=require('child_process');
const {once}=require('events');
const ROOT=path.resolve(__dirname,'../../..');
const {chromium}=require(path.join(ROOT,'frontend/node_modules/@playwright/test'));
const WORK=path.join(ROOT,'demo/work/article-animation');
const OUT=path.join(ROOT,'demo/article-animation');
const FF=path.join(ROOT,'.tools/video-python/imageio_ffmpeg/binaries/ffmpeg-macos-x86_64-v7.1');
const rehearsal=process.argv.includes('--rehearse');
const timing=JSON.parse(fs.readFileSync(path.join(rehearsal?WORK:OUT,rehearsal?'rehearsal-timing.json':'timing.json')));
fs.mkdirSync(path.join(WORK,'frames'),{recursive:true});
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true,args:['--allow-file-access-from-files','--force-color-profile=srgb']});
 try{
  const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.route('http://**/*',r=>r.abort());await page.route('https://**/*',r=>r.abort());
  await page.goto(pathToFileURL(path.join(__dirname,'scene.html')).href);
  await page.waitForFunction(()=>window.ready===true);
  await page.evaluate(t=>window.setTimeline(t),timing);
  const reviews=[];
  for(const s of timing.segments){
   for(const phase of ['early','late']){
    const time=s.start+(s.end-s.start)*(phase==='early'?.35:.82);
    await page.evaluate(t=>window.seek(t),time);
    const audit=await page.evaluate(()=>window.audit());
    await page.screenshot({path:path.join(WORK,'frames',`${s.id}-${phase}.png`)});
    reviews.push({scene:s.id,phase,time,...audit});
   }
  }
  if(errors.length||reviews.some(r=>r.bad.length||!r.font)){
   fs.writeFileSync(path.join(WORK,'visual-rehearsal.json'),JSON.stringify({status:'FAIL',errors,reviews},null,2));
   throw new Error('Visual rehearsal failed; inspect the audit');
  }
  fs.writeFileSync(path.join(WORK,rehearsal?'visual-rehearsal.json':'visual-review.json'),JSON.stringify({status:'PASS',viewport:[1920,1080],network:'blocked',errors,reviews},null,2));
  if(rehearsal){console.log(`PASS: ${reviews.length} offline scene frames, handwriting font loaded, no clipping or page errors`);return}
  const encode=spawn(FF,['-hide_banner','-loglevel','error','-nostdin','-y','-f','image2pipe','-vcodec','mjpeg','-framerate','30','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-r','30','-movflags','+faststart',path.join(WORK,'picture.mp4')],{stdio:['pipe','ignore','pipe']});
  let encodeErrors='';encode.stderr.on('data',d=>encodeErrors+=d);
  const done=once(encode,'close');
  const frames=Math.round(timing.duration*30);const probes=[];
  for(let i=0;i<frames;i++){
   const state=await page.evaluate(t=>window.seek(t),i/30);
   const b=await page.screenshot({type:'jpeg',quality:92});
   if(!encode.stdin.write(b))await once(encode.stdin,'drain');
   if(i%300===0){console.log(`Rendered ${i}/${frames} frames · ${state.scene}`);probes.push({frame:i,...state})}
  }
  encode.stdin.end();const [code]=await done;
  if(code)throw new Error(encodeErrors);
  fs.writeFileSync(path.join(WORK,'render.json'),JSON.stringify({status:'PASS',frames,fps:30,duration:timing.duration,viewport:[1920,1080],deterministic:true,probes,errors},null,2));
  await page.evaluate(t=>window.seek(t),timing.segments[0].start+(timing.segments[0].end-timing.segments[0].start)*.85);
  await page.screenshot({path:path.join(OUT,'poster.png')});
  console.log('Picture render complete.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e.message);process.exitCode=1});
