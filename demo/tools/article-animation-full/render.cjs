/* Render only motion intervals; hold source frames during deliberate reading pauses. */
const fs=require('fs'),path=require('path'),crypto=require('crypto'),{pathToFileURL}=require('url'),{spawn}=require('child_process');
const ROOT=path.resolve(__dirname,'../../..');const {chromium}=require(path.join(ROOT,'frontend/node_modules/@playwright/test'));
const WORK=path.join(ROOT,'demo/work/article-animation-full'),OUT=path.join(ROOT,'demo/article-animation-full');
const FF=path.join(ROOT,'.tools/video-python/imageio_ffmpeg/binaries/ffmpeg-macos-x86_64-v7.1');
const timing=JSON.parse(fs.readFileSync(path.join(OUT,'timing.json'))),fps=30;
const hash=v=>crypto.createHash('sha256').update(v).digest('hex');
const fingerprint=hash(fs.readFileSync(path.join(__dirname,'scene.html'))+fs.readFileSync(path.join(__dirname,'engine.js')));
const selected=process.argv.includes('--first')?timing.beats.slice(0,1):timing.beats;
const quote=p=>p.replace(/'/g,"'\\''");
function run(args){return new Promise((resolve,reject)=>{const p=spawn(FF,['-hide_banner','-loglevel','error','-nostdin',...args]);let out='',err='';p.stdout.on('data',d=>out+=d);p.stderr.on('data',d=>err+=d);p.on('close',c=>c?reject(new Error(err.slice(-1500))):resolve(out));p.on('error',reject)})}
function framePoints(b){const n=b.frames,points=new Set([0,n-1]);let windows=b.layout==='intro'?[[0,4.6]]:[[0,2.2],[b.reveal_times[1],b.reveal_times[1]+2.2],[b.reveal_times[2],b.reveal_times[2]+2.4]];windows.push([(n/fps)-.4,n/fps]);for(const [a,z] of windows){for(let i=Math.max(0,Math.floor(a*fps));i<Math.min(n,Math.ceil(z*fps));i++)points.add(i)}return [...points].sort((a,b)=>a-b)}
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true,args:['--allow-file-access-from-files','--force-color-profile=srgb']});let next=0;const results=[];
 try{
  async function worker(id){const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});await page.route('http://**/*',r=>r.abort());await page.route('https://**/*',r=>r.abort());const errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(pathToFileURL(path.join(__dirname,'scene.html')).href);await page.waitForFunction(()=>window.ready);await page.evaluate(t=>window.setTimeline(t),timing);
   while(next<selected.length){const b=selected[next++],dir=path.join(WORK,'frames',b.id),clip=path.join(WORK,'clips',b.id+'.mp4'),metaFile=clip+'.json';fs.mkdirSync(dir,{recursive:true});fs.mkdirSync(path.dirname(clip),{recursive:true});const signature=hash(JSON.stringify(b)+fingerprint);
    if(fs.existsSync(metaFile)&&fs.existsSync(clip)){const old=JSON.parse(fs.readFileSync(metaFile));if(old.signature===signature&&old.frames===b.frames){results.push(old);console.log('Cached',b.id);continue}}
    const points=framePoints(b);let concat='ffconcat version 1.0\n';
    for(let j=0;j<points.length;j++){const frame=points[j],t=b.start+frame/fps;await page.evaluate(t=>window.seek(t),t);const file=path.join(dir,String(frame).padStart(6,'0')+'.jpg');await page.screenshot({path:file,type:'jpeg',quality:92});const duration=((points[j+1]??b.frames)-frame)/fps;concat+=`file '${quote(file)}'\noption framerate 30\nduration ${duration.toFixed(9)}\n`}
    concat+=`file '${quote(path.join(dir,String(points.at(-1)).padStart(6,'0')+'.jpg'))}'\noption framerate 30\n`;
    const list=path.join(dir,'frames.ffconcat');fs.writeFileSync(list,concat);
    const progress=await run(['-y','-f','concat','-safe','0','-i',list,'-an','-fps_mode','cfr','-r','30','-frames:v',String(b.frames),'-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-threads','2','-video_track_timescale','90000','-progress','pipe:1',clip]);
    const encoded=[...progress.matchAll(/^frame=(\d+)$/gm)].at(-1)?.[1];if(Number(encoded)!==b.frames)throw new Error(`Frame mismatch ${b.id}: ${encoded} / ${b.frames}`);
    await page.evaluate(t=>window.seek(t),b.start+(b.end-b.start)*.85);const audit=await page.evaluate(()=>window.audit());if(audit.bad.length||errors.length)throw new Error('Layout or page error '+b.id);
    const result={id:b.id,chapter:b.chapter_id,signature,frames:b.frames,sampled_frames:points.length,duration:b.frames/fps,clip,errors:[...errors]};fs.writeFileSync(metaFile,JSON.stringify(result,null,2));results.push(result);console.log(`Rendered ${b.id} · ${points.length} motion frames / ${b.frames} output frames · worker ${id}`);
   }await page.close()}
  await Promise.all([worker(1),worker(2)]);
  results.sort((a,b)=>timing.beats.findIndex(x=>x.id===a.id)-timing.beats.findIndex(x=>x.id===b.id));
  fs.writeFileSync(path.join(WORK,process.argv.includes('--first')?'first-render.json':'render.json'),JSON.stringify({status:'PASS',fps:30,results,total_frames:results.reduce((n,r)=>n+r.frames,0),sampled_frames:results.reduce((n,r)=>n+r.sampled_frames,0),network:'blocked',deterministic:true,held_frames:'Original rendered picture held during deliberate reading pauses'},null,2));
  console.log('Render complete',results.length,'illustrated beats');
 }finally{await browser.close()}
})().catch(e=>{console.error(e.stack);process.exitCode=1});
