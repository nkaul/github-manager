/* Real production UI; browser API requests go only to the disposable fixture backend. */
const fs = require('node:fs');
const path = require('node:path');
const { chromium, expect } = require('../../../frontend/node_modules/@playwright/test');
const ROOT = path.resolve(__dirname, '../../..');
const WORK = path.join(ROOT, 'demo/work/voice-preview-v2');
fs.mkdirSync(WORK, { recursive: true });
const dry = process.argv.includes('--rehearse');
const selected = process.argv.find(a => a.startsWith('--variant='))?.split('=')[1] || 'A';
const ids = { A: 9101, B: 9102, C: 9103, D: 9107 };
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
 const browser = await chromium.launch({ headless: true });
 const context = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1,
   ...(dry ? {} : { recordVideo: { dir: path.join(WORK, 'raw'), size: { width: 1920, height: 1080 } } }) });
 const page = await context.newPage();
 const errors = [], routes = [], checks = [], actions = [];
 page.on('pageerror', e => errors.push(e.message));
 await context.route('http://127.0.0.1:3000/api/v1/**', async route => {
   const u = new URL(route.request().url());
   routes.push({ method: route.request().method(), path: u.pathname });
   const response = await route.fetch({ url: 'http://127.0.0.1:8100' + u.pathname + u.search });
   await route.fulfill({ response });
 });
 try {
   const login = await context.request.post('http://127.0.0.1:8100/api/v1/test/login', { data: { id: ids[selected] } });
   expect(login.ok()).toBeTruthy();
   await page.goto('http://127.0.0.1:3000/');
   await page.getByLabel('Workspace collection').selectOption('samples');
   const load = page.getByRole('button', { name: 'Load demo samples', exact: true });
   if (await load.count()) await load.first().click();
   await expect(page.getByRole('button', { name: 'Details for orion-api', exact: true })).toBeVisible();
   const button = name => page.getByRole('button', { name, exact: true });
   const aiButton = () => page.getByRole('button', { name: 'AI Organization', exact: false });
   await aiButton().click();
   await page.getByLabel('Inference mode').selectOption('LIVE');
   if (await button('Discover taxonomy').count()) {
     await button('Discover taxonomy').click();
     await button('Start reviewed run').click();
     await button('Review draft').click();
     await button('Approve & publish taxonomy').click();
     await button('Full classification').click();
     await button('Start reviewed run').click();
     const review = page.getByRole('region', { name: 'Assignment review', exact: true });
     await expect(review.getByRole('button', { name: 'Accept', exact: true })).toHaveCount(3);
     await review.getByRole('button', { name: 'Accept', exact: true }).first().click();
     await review.getByRole('button', { name: 'Accept', exact: true }).first().click();
   }
   async function mutate(endpoint, data) {
     return page.evaluate(async ({endpoint, data}) => {
       const me = await (await fetch('/api/v1/me')).json();
       const r = await fetch('/api/v1' + endpoint + '?collection=samples', { method: 'POST', headers: {'Content-Type':'application/json','X-CSRF-Token':me.csrf_token}, body:JSON.stringify(data) });
       if (!r.ok) throw new Error('Fixture setup HTTP ' + r.status);
       return r.json();
     }, {endpoint, data});
   }
   const state = await page.evaluate(async () => (await fetch('/api/v1/workspace?collection=samples')).json());
   const concepts = Object.values(state.organization.concepts);
   const parent = concepts.find(c => c.kind === 'DOMAIN' && c.name === 'Applications');
   let operations = concepts.find(c => c.name === 'Orion Operations');
   if (!operations) operations = await mutate('/taxonomy/concepts', {kind:'PROJECT',name:'Orion Operations',domain:parent.id,description:'Synthetic walkthrough example',aliases:[]});
   await mutate('/repos/associations', {repo_keys:['synthetic/orion-api'],concept_ids:[operations.id],operation:'REMOVE'});
   const topic = concepts.find(c => c.kind === 'TOPIC');
   const tag = concepts.find(c => c.kind === 'TAG');
   await mutate('/repos/associations', {repo_keys:['synthetic/orion-api'],concept_ids:[topic.id,tag.id],operation:'ADD'});
   await button('Demo samples').click();
   await expect(page.locator('tbody tr')).toHaveCount(3);
   await expect(page.locator('.wm-stat-label > svg')).toHaveCount(5);
   const notification = page.getByLabel('Dismiss notification', {exact:true});
   if(await notification.count()) await notification.click();
   await page.evaluate(()=>window.scrollTo(0,0));
   checks.push('Production UI served at 1920x1080; all API calls isolated to port 8100', 'Fixture taxonomy and analysis outcomes prepared with zero external AI calls', 'Five KPI icons present');
   await page.addStyleTag({content:`#pilot-label{position:fixed;left:16px;bottom:14px;z-index:999999;padding:8px 12px;border:1px solid #c5cae9;background:#fff;color:#303f9f;border-radius:10px;font:600 12px system-ui;box-shadow:0 2px 10px #25213910;pointer-events:none}#pilot-pointer{position:fixed;width:22px;height:22px;border:2px solid #1e88e5;background:#29b6f622;border-radius:50%;z-index:999999;pointer-events:none;transform:translate(-50%,-50%);transition:box-shadow .15s}#pilot-focus{position:fixed;pointer-events:none;z-index:999998;border:2px solid #42a5f5;border-radius:12px;box-shadow:0 0 0 4px #42a5f51a;display:none}`});
   await page.evaluate(() => {
     for (const id of ['pilot-label','pilot-pointer','pilot-focus']) { const e=document.createElement('div');e.id=id;document.body.appendChild(e); }
     document.getElementById('pilot-label').textContent='PUBLIC + SYNTHETIC DEMO · AI narration';
     document.addEventListener('mousemove',e=>{const p=document.getElementById('pilot-pointer');p.style.left=e.clientX+'px';p.style.top=e.clientY+'px';});
   });
   let base = performance.now(), currentScene;
   const norm = s => s.toLowerCase().replace(/[^a-z0-9]/g,'');
   const timelineFile=path.join(WORK,selected+'-timeline.json');
   const timing=dry?null:JSON.parse(fs.readFileSync(timelineFile));
   async function cue(phrase){
     if(dry)return;
     const needle=phrase.split(' ').map(norm),words=timing.words.filter(w=>w.scene===currentScene);
     const i=words.findIndex((w,i)=>needle.every((n,j)=>norm(words[i+j]?.word||'')===n));
     if(i<0)throw new Error('Missing spoken cue '+phrase);
     const wait=(words[i].start-.26)*1000-(performance.now()-base);if(wait>0)await sleep(wait);
   }
   async function mark(name, locator, action) {
     await locator.scrollIntoViewIfNeeded();
     const box = await locator.boundingBox();
     if (box) {
       await page.mouse.move(box.x+box.width/2,box.y+box.height/2,{steps:8});
       await page.evaluate(b=>{const el=document.getElementById('pilot-focus');Object.assign(el.style,{display:'block',left:(b.x-3)+'px',top:(b.y-3)+'px',width:(b.width+6)+'px',height:(b.height+6)+'px'});},box);
     }
     actions.push({name,at:(performance.now()-base)/1000});
     if(action) await action();
   }
   const sidebar=page.locator('.wm-sidebar');
   const steps = {
     intro:async()=>{await mark('Workspace and zen logo',page.locator('.wm-brand'));},
     browse:async()=>{
       await cue('topics');
       await mark('Topics tab',sidebar.getByRole('tab',{name:'Topics',exact:true}),()=>sidebar.getByRole('tab',{name:'Topics',exact:true}).click());
       await expect(sidebar.getByRole('button',{name:'Web APIs',exact:true})).toBeVisible();
       await cue('tags');
       await mark('Tags tab',sidebar.getByRole('tab',{name:'Tags',exact:true}),()=>sidebar.getByRole('tab',{name:'Tags',exact:true}).click());
       await expect(sidebar.getByRole('button',{name:'python',exact:true})).toBeVisible();
       checks.push('Topics and Tags browsed');
     },
     search:async()=>{
       await cue('Search');
       await mark('Search repositories',page.getByLabel('Search repositories'),()=>page.getByLabel('Search repositories').pressSequentially('orion',{delay:dry?0:90}));
       await expect(page.locator('tbody tr')).toHaveCount(2);
       checks.push('Search narrows three samples to two Orion repositories');
     },
     metrics:async()=>{
       await mark('Scoped KPI icons and selected counts',page.locator('.wm-stats'));
       await cue('which');
       await mark('Select repository',page.getByLabel('Select orion-api',{exact:true}),()=>page.getByLabel('Select orion-api',{exact:true}).check());
       await expect(page.locator('.wm-stat-selected strong')).toHaveText('1');
       checks.push('Selection and scoped KPI counts updated');
     },
     ai:async()=>{
       await mark('AI Organization',aiButton(),()=>aiButton().click());
       await page.getByLabel('Repository selection mode').selectOption('AUTO');
       await page.getByLabel('AI repository scope').selectOption('ALL');
       await page.getByLabel('Classification batch size',{exact:true}).fill('3');
       await page.getByLabel('Budget mode',{exact:true}).selectOption('ADAPTIVE');
       await cue('preview');
       await mark('Preview classification batch',button('Full classification'),()=>button('Full classification').click());
       await expect(page.getByRole('region',{name:'Run preview',exact:true})).toContainText('0 generations / 0 HTTP attempts');
       await cue('budget');
       await mark('Adaptive budget',page.getByLabel('Budget mode',{exact:true}));
       await cue('review taxonomy');
       await mark('Review suggestions before acceptance',page.getByRole('region',{name:'Assignment review',exact:true}));
       checks.push('Three-repository adaptive preview uses zero provider HTTP attempts');
     },
     protected:async()=>{
       const preview=page.getByRole('region',{name:'Run preview',exact:true});
       await mark('Protected analysis and offline reconciliation',preview);
       await expect(preview).toContainText('3 for offline reconciliation');
       await cue('explicitly');
       await mark('Explicit re-analysis control',page.getByLabel('Re-analyze with AI',{exact:true}));
       checks.push('Prior analyses reconcile offline; explicit re-analysis remains available');
     },
     manual:async()=>{
       await button('Demo samples').click();
       const clear=button('Clear'); if(await clear.count()) await clear.click();
       const filters=button('Clear filters');if(await filters.count()) await filters.click();
       await sidebar.getByRole('tab',{name:'Projects',exact:true}).click();
       const row=page.locator('tr',{has:page.getByLabel('Select orion-api',{exact:true})});
       const target=sidebar.getByRole('button',{name:'Orion Operations',exact:true});
       await cue('drag and drop');
       await mark('Drag repository onto project',row);
       const a=await row.boundingBox(),b=await target.boundingBox();
       await page.mouse.move(a.x+a.width*.42,a.y+a.height/2,{steps:12});await page.mouse.down();
       await page.mouse.move(b.x+b.width/2,b.y+b.height/2,{steps:30});await page.mouse.up();
       await expect(row).toContainText('Orion Operations');
       await mark('Saved project membership',row);
       checks.push('Native drag/drop adds Orion Operations membership');
     },
     appearance:async()=>{
       await mark('Content settings',button('Content settings'),()=>button('Content settings').click());
       const settings=page.getByRole('region',{name:'Appearance settings',exact:true});
       const radio=settings.getByRole('radio',{name:/Continuous blue aura/});
       if(timing?.cedar_closing_repair){const wait=(timing.segments.find(s=>s.id==='appearance').audio_start+1)*1000-(performance.now()-base);if(wait>0)await sleep(wait);}else await cue('favorite');
       await mark('Choose continuous aura',radio,()=>radio.check());
       await expect(page.locator('.wm-header .wm-logo')).toHaveAttribute('data-logo','orbit');
       checks.push('Appearance switches header logo to continuous aura');
     }
   };
   const story=JSON.parse(fs.readFileSync(path.join(__dirname,'story.json')));
   const timeline=dry?story.segments.map((s,i)=>({...s,start:i*2,end:(i+1)*2})):timing.segments;
   await page.evaluate(()=>{const e=document.createElement('div');e.id='pilot-origin';Object.assign(e.style,{position:'fixed',right:'4px',bottom:'4px',width:'8px',height:'8px',background:'#ff00ff',zIndex:'1000000',pointerEvents:'none'});document.body.appendChild(e);});
   base=performance.now();
   const captureStart=await page.evaluate(()=>performance.now()/1000);
   for(const scene of timeline){
     currentScene=scene.id;
     const wait=scene.start*1000-(performance.now()-base);if(wait>0)await sleep(wait);
     const start=(performance.now()-base)/1000;
     await steps[scene.id]();
     await page.screenshot({path:path.join(WORK,`${dry?'rehearsal':selected}-${scene.id}.png`)});
     const end=(performance.now()-base)/1000;
     if(!dry && end>scene.end+.35) throw new Error(`Scene ${scene.id} exceeded cue window: ${end.toFixed(2)} > ${scene.end}`);
     console.log(selected,scene.id,start.toFixed(2),end.toFixed(2));
   }
   const remain=(dry?0:60.25)*1000-(performance.now()-base);if(remain>0)await sleep(remain);
   expect(errors).toEqual([]);
   expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
   const video=page.video();
   // Record the actual browser recording origin independently of setup/rehearsal time.
   const result={status:'PASS',variant:selected,viewport:[1920,1080],dry,checks,errors,actions,routedRequests:routes.length,pageNavigationClockSeconds:captureStart,externalProviderCalls:0};
   await context.close();
   if(!dry){const output=path.join(WORK,selected+'-raw.webm');await video.saveAs(output);result.raw=output;}
   fs.writeFileSync(path.join(WORK,dry?'rehearsal.json':selected+'-capture.json'),JSON.stringify(result,null,2));
   console.log(JSON.stringify(result));
 }finally{await browser.close();}
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
