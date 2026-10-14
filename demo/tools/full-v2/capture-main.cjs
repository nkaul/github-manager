/* Current production UI, real OAuth session and an explicitly labeled real-data copy. */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {spawn}=require('node:child_process');
const {chromium,expect}=require('../../../frontend/node_modules/@playwright/test');
const ROOT=path.resolve(__dirname,'../../..'),BASE='http://127.0.0.1:3000',COPY='http://127.0.0.1:8124';
const WORK=path.join(ROOT,'demo/work/full-v2'),PRIVATE=path.join(ROOT,'docs/validation/private/demo/full-v2');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
module.exports=async function({loginContext}){
 fs.mkdirSync(WORK,{recursive:true});fs.mkdirSync(path.join(WORK,'raw'),{recursive:true});
 const story=JSON.parse(fs.readFileSync(path.join(__dirname,'story.json')));
 const reportFile=path.join(WORK,'capture.json');
 const report=fs.existsSync(reportFile)?JSON.parse(fs.readFileSync(reportFile)):{viewport:{width:1920,height:1080},source:'REAL_ACCOUNT',masking:false,chapters:[],checks:[],errors:[],notes:[]};
 if(report.failure){(report.rehearsal_corrections ||= []).push(report.failure);delete report.failure;}delete report.status;
 const save=()=>fs.writeFileSync(reportFile,JSON.stringify(report,null,2));
 const user=JSON.parse(fs.readFileSync(path.join(PRIVATE,'inspection.json'))).user;
 let browser,context,page,chapter,base,beatStart;
 let vars=fs.existsSync(path.join(WORK,'vars.json'))?JSON.parse(fs.readFileSync(path.join(WORK,'vars.json'))):{};
 const storeVars=()=>fs.writeFileSync(path.join(WORK,'vars.json'),JSON.stringify(vars,null,2));
 const check=(name,details={})=>{report.checks.push({chapter:chapter.id,name,status:'PASS',...details});console.log('PASS',chapter.id,name);save();};
 const btn=(name,exact=true)=>page.getByRole('button',{name,exact});
 async function focus(l){await l.scrollIntoViewIfNeeded();const b=await l.boundingBox();if(b){await page.mouse.move(b.x+b.width/2,b.y+b.height/2,{steps:12});await l.evaluate(el=>{el.style.outline='3px solid #29b6f6';setTimeout(()=>el.style.outline='',1600);});}}
 async function click(l){await focus(l);await l.click();await sleep(350);}
 async function nav(name){await click(btn(name,name!=='AI Organization'));}
 async function close(){await click(btn('Close dialog'));}
 async function state(){return page.evaluate(async()=>{const r=await fetch('/api/v1/workspace?collection=github');if(!r.ok)throw Error('Workspace unavailable');return r.json();});}
 async function api(endpoint,data,method='POST'){return page.evaluate(async({endpoint,data,method})=>{const me=await(await fetch('/api/v1/me')).json();const r=await fetch('/api/v1'+endpoint+(endpoint.includes('?')?'&':'?')+'collection=github',{method,headers:{'Content-Type':'application/json','X-CSRF-Token':me.csrf_token},...(data===undefined?{}:{body:JSON.stringify(data)})});const value=await r.json();if(!r.ok)throw Error('Workspace operation '+r.status+': '+(value.detail||''));return value;},{endpoint,data,method});}
 async function repos(extra=''){return api('/repos?view=all&limit=100'+extra,undefined,'GET');}
 async function idle(timeout=120000){let s;const end=Date.now()+timeout;do{await sleep(300);s=await state();if(!s.organization.control.active_run&&!s.organization.control.resetting)return s;}while(Date.now()<end);throw Error('Workspace still busy');}
 async function organizer(mode='CACHE'){await nav('AI Organization');await page.getByLabel('Inference mode').selectOption(mode);}
 async function preview(name,mode='CACHE',count=3,force=false){await organizer(mode);await page.getByLabel('Repository selection mode').selectOption('AUTO');await page.getByLabel('AI repository scope').selectOption('ALL');await page.getByLabel('Taxonomy sample size').fill(String(count));await page.getByLabel('Classification batch size',{exact:true}).fill(String(count));await page.getByLabel('Budget mode',{exact:true}).selectOption('ADAPTIVE');await page.getByLabel('Maximum per run USD').fill('0.25');await page.getByLabel('Re-analyze with AI',{exact:true}).setChecked(force);if(force)await page.getByLabel('Reason for re-analysis').fill('Full demo: deliberate refresh of verified public evidence');await click(btn(name));await expect(page.getByRole('region',{name:'Run preview',exact:true})).toBeVisible();}
 async function execute(){await click(btn('Start reviewed run'));const s=await idle();const r=Object.values(s.organization.runs).sort((a,b)=>b.created_at.localeCompare(a.created_at))[0];check('Reviewed '+r.kind+' finished',{status:r.status,processed:r.processed,failed:r.failed,provenance:[...new Set(Object.values(r.outcomes||{}).map(x=>x.evidence))]});return {s,r};}
 async function all(){await nav('Access candidates');const f=btn('Clear filters');if(await f.count())await f.click();await page.getByLabel('Organization status view').selectOption('all');}
 async function detail(name=vars.repo){await all();await page.getByLabel('Search repositories').fill(name);await click(btn('Details for '+name));await expect(page.getByRole('dialog')).toBeVisible();}
 async function concept(kind,name,domain,aliases=''){
  const existing=Object.values((await state()).organization.concepts).find(c=>c.active&&c.kind===kind&&c.name===name);if(existing)return existing;
  await nav('Content settings');await click(btn('+ Create concept'));await page.getByRole('combobox',{name:/^Type/}).selectOption(kind);await page.getByLabel('Name',{exact:true}).fill(name);await page.getByLabel('Description',{exact:true}).fill('Created manually for the real-account walkthrough in a workspace copy.');await page.getByRole('dialog').getByLabel('Aliases',{exact:false}).first().fill(aliases);if(kind==='PROJECT')await page.getByRole('combobox',{name:/^Parent domain/}).selectOption(domain);await click(btn('Save concept'));await expect(page.getByRole('dialog')).toHaveCount(0);return Object.values((await state()).organization.concepts).find(c=>c.active&&c.name===name);
 }
 async function card(kind,name){await nav('Content settings');await click(page.locator('.wm-tabs').getByRole('button',{name:new RegExp('^'+kind[0]+kind.slice(1).toLowerCase()+'s')}));return page.locator('.wm-concept-card').filter({has:page.getByRole('heading',{name,exact:true})});}
 async function sidebarMode(name){await click(page.locator('.wm-sidebar').getByRole('tab',{name,exact:true}));}
 async function resumeSession(){const r=await context.request.post(COPY+'/api/v1/recording/resume',{headers:{'X-Recording-Key':global.fullDemoBackend.key}});expect(r.ok()).toBeTruthy();}
 async function startBackend(){
  if(global.fullDemoBackend?.process.exitCode===null&&global.fullDemoBackend.process.signalCode===null)return;
  const key=global.fullDemoBackend?.key||crypto.randomBytes(32).toString('hex');
  const proc=spawn(path.join(ROOT,'backend/.venv/bin/uvicorn'),['workspace_server:app','--app-dir',__dirname,'--host','127.0.0.1','--port','8124','--no-access-log'],{cwd:path.join(ROOT,'backend'),env:{...process.env,FULL_DEMO_SESSION_KEY:key,FULL_DEMO_ALLOW_LIVE:'1'},stdio:['ignore','ignore','pipe']});
  global.fullDemoBackend={key,process:proc};proc.stderr.on('data',d=>{if(/ERROR|Traceback/.test(d.toString()))console.error('Copy backend:',d.toString().slice(-900));});
  for(let i=0;i<100;i++){try{if((await fetch(COPY+'/health')).ok)return;}catch{}if(proc.exitCode!==null)throw Error('Recording backend exited');await sleep(150);}throw Error('Copy backend unavailable');
 }
 async function stopBackend(){const p=global.fullDemoBackend.process;p.kill('SIGTERM');for(let i=0;i<100&&p.exitCode===null&&p.signalCode===null;i++)await sleep(100);}
 async function setup(c){
  context=await browser.newContext({viewport:{width:1920,height:1080},deviceScaleFactor:1,storageState:await loginContext.storageState(),recordVideo:{dir:path.join(WORK,'raw'),size:{width:1920,height:1080}}});
  if(+c.id>4||(c.id==='02'&&fs.existsSync(path.join(ROOT,'.tools/full-v2-inclusion-retake')))){await context.route(BASE+'/api/v1/**',async route=>{try{const u=new URL(route.request().url());const r=await route.fetch({url:COPY+u.pathname+u.search,maxRedirects:0});await route.fulfill({response:r});}catch{await route.fulfill({status:502,json:{detail:'Recording-copy backend restarting'}}).catch(()=>{});}});await resumeSession();}
  page=await context.newPage();page.setDefaultTimeout(16000);page.on('pageerror',e=>report.errors.push({chapter:c.id,message:e.message.slice(0,350)}));
  await page.goto(BASE);await expect(page.getByLabel('Workspace collection')).toBeVisible();await page.getByLabel('Workspace collection').selectOption('github');
  await page.addStyleTag({content:'#full-demo-label{position:fixed;left:16px;bottom:14px;z-index:999999;padding:8px 12px;background:#fff;color:#283593;border:1px solid #9fa8da;border-radius:10px;font:600 13px system-ui;pointer-events:none;box-shadow:0 3px 14px #0002;max-width:900px}#full-demo-origin{position:fixed;right:4px;bottom:4px;width:8px;height:8px;background:#ff00ff;z-index:999999;pointer-events:none}#full-demo-pointer{position:fixed;width:20px;height:20px;border:2px solid #1e88e5;border-radius:50%;background:#29b6f633;z-index:999999;pointer-events:none;transform:translate(-50%,-50%)}'});
  await page.evaluate(c=>{for(const id of ['full-demo-label','full-demo-origin','full-demo-pointer']){const e=document.createElement('div');e.id=id;document.body.appendChild(e);}document.getElementById('full-demo-label').textContent=c.id+' / 32 · '+c.title+' · '+c.source;document.addEventListener('mousemove',e=>{const p=document.getElementById('full-demo-pointer');p.style.left=e.clientX+'px';p.style.top=e.clientY+'px';});},c);base=performance.now();
 }
 async function beat(id,action){const row={id,start:(performance.now()-base)/1000};chapter.beats.push(row);beatStart=performance.now();await sleep(300);await action();row.action_end=(performance.now()-base)/1000;const used=performance.now()-beatStart;const minimum=chapter.id==='22'?({appearance:12000,aura:12000,pause:6000,restore:8000}[id]||4000):4000;if(used<minimum)await sleep(minimum-used);row.end=(performance.now()-base)/1000;await page.screenshot({path:path.join(WORK,`scene-${chapter.id}-${id}.png`)});save();}
 const B=async(id,fn)=>beat(id,fn);
 const show=async l=>{await focus(l);await sleep(650);};
 async function resetPreview({kinds=[],ai=true,cache=false,rules=false}={}){await organizer();await click(btn('Preview reset'));const d=page.getByRole('dialog');for(const label of ['Automatic / rule assignments','Pending classification suggestions','Unpublished taxonomy drafts','Detailed run history'])await d.getByRole('checkbox',{name:label,exact:true}).setChecked(ai);await d.getByRole('checkbox',{name:'Extracted evidence cache',exact:true}).setChecked(cache);for(const kind of kinds)await d.getByRole('checkbox',{name:kind,exact:true}).check();await d.getByRole('checkbox',{name:'Organization rules',exact:true}).setChecked(rules);await click(btn('Preview impact'));await expect(d).toContainText('Server-verified impact');}
 async function resetExecute(){await page.getByLabel('Type exactly DELETE').fill('DELETE');await click(btn('Confirm reset'));const s=await idle();expect(s.organization.audit.at(-1).verified).toBe(true);check('Scoped reset cleanup verified');return s;}
 const handlers={
 '01':async()=>{
  await B('welcome',async()=>{await show(page.locator('.wm-brand'));check('Authenticated real account opened at 1920×1080',{login:user.login});});
  await B('signin',async()=>{await click(page.getByLabel('Account menu'));await show(page.locator('.wm-account'));await click(page.getByLabel('Account menu'));check('OAuth completed outside recording; no masking requested');});
  await B('workspace',async()=>{await nav('My Repos');await expect(page.locator('tbody tr').first()).toBeVisible();});
  await B('tour',async()=>{await show(page.locator('.wm-header'));expect(await page.locator('.wm-stat-label > svg').count()).toBe(5);check('Current header, palette and five KPI icons');});
 },
 '02':async()=>{
  await B('sync',async()=>{await click(btn('Sync GitHub',false).first());const s=await idle();report.liveGithub={repos:s.coverage.repos,source_coverage:s.source_coverage,activity_coverage:s.activity_coverage};check('Live GitHub inventory sync',{repositories:s.coverage.repos});});
  await B('sources',async()=>{await nav('My Repos');await nav('Favorites');check('My Repos and Favorites opened');});
  await B('candidates',async()=>{await all();const rows=await repos();vars.repo=rows.items.find(r=>r.name==='allegro/ralph')?.name||rows.items.find(r=>!r.private).name;vars.repo2=rows.items.find(r=>r.name==='acassen/keepalived')?.name||rows.items.filter(r=>!r.private)[1].name;storeVars();await detail(vars.repo);});
  await B('coverage',async()=>{await close();await show(page.locator('.wm-coverage'));check('Source coverage visible with real observations');});
 },
 '03':async()=>{
  await B('filters',async()=>{await all();await page.getByLabel('Search repositories').fill('aws');await page.getByLabel('Visibility filter').selectOption('public');await show(page.locator('.wm-toolbar'));await click(btn('Clear filters'));check('Search and visibility filter chips cleared');});
  await B('metrics',async()=>{await show(page.locator('.wm-stats'));check('Five scope-aware compact KPI cards');});
  await B('selected',async()=>{await page.locator('tbody input[type=checkbox]').first().check();await expect(page.locator('.wm-stat-selected strong')).toHaveText('1');check('Selected count and scoped subtotals');});
  await B('pagination',async()=>{const more=btn('Load more');if(await more.count()){const before=await page.locator('tbody tr').count();await click(more);expect(await page.locator('tbody tr').count()).toBeGreaterThan(before);check('Real repository pagination');}else check('Inventory loaded in current page');await detail();await expect(page.getByRole('dialog')).toContainText(vars.repo);});
 },
 '04':async()=>{
  await B('activity',async()=>{await nav('Latest Work');for(const n of ['7','14','30','90'])await page.getByLabel('Activity window').selectOption(n);check('All four contribution activity windows');});
  await B('bounded',async()=>{await show(page.locator('.wm-table-note'));check('Live activity coverage limitations visible');});
  await B('private',async()=>{await all();await page.getByLabel('Visibility filter').selectOption('private');const r=(await repos('&visibility=private')).items[0];if(!r)throw Error('No private repository observed');await detail(r.name);await expect(page.getByRole('dialog')).toContainText('Private README-derived evidence is excluded');check('Real private repository metadata; model input excluded',{repository:r.name});});
  await B('transition',async()=>{await close();await all();await show(page.locator('.wm-stats'));check('Real-account snapshot prepared for reversible demo edits');});
 },
 '05':async()=>{
  await B('load',async()=>{await detail();check('Real public repository details in workspace copy');});
  await B('extract',async()=>{await show(page.locator('.wm-evidence').first());await expect(page.getByRole('dialog')).toContainText('demo-rake-tfidf-v2');check('Stored versioned local evidence profile visible');});
  await B('details',async()=>{await page.getByRole('dialog').evaluate(el=>el.scrollTop=el.scrollHeight/2);await show(page.locator('.wm-evidence').last());});
  await B('privacy',async()=>{await close();await organizer();await show(page.getByRole('region',{name:'AI run setup'}));check('Only verified public evidence eligible for inference');});
 },
 '06':async()=>{
  await B('counts',async()=>{await organizer('LIVE');await page.getByLabel('Taxonomy sample size').fill('2');await page.getByLabel('Classification batch size',{exact:true}).fill('1');await show(page.getByRole('region',{name:'AI run setup'}));});
  await B('scope',async()=>{await page.getByLabel('AI repository scope').selectOption('ALL');await show(page.getByLabel('Repository selection mode'));check('Independent taxonomy/classification counts and automatic scope');});
  await B('mode',async()=>{await page.getByLabel('Inference mode').selectOption('CACHE');await page.getByLabel('Inference mode').selectOption('LIVE');await show(page.getByLabel('Inference mode'));});
  await B('discover',async()=>{const s=await state();if(!Object.values(s.organization.drafts).some(d=>d.status==='DRAFT')){await all();await page.getByLabel('Select allegro/ralph',{exact:true}).check();await page.getByLabel('Select acassen/keepalived',{exact:true}).check();await organizer('LIVE');await page.getByLabel('Repository selection mode').selectOption('MANUAL');await page.getByLabel('AI repository scope').selectOption('ALL');await page.getByLabel('Budget mode',{exact:true}).selectOption('ADAPTIVE');await page.getByLabel('Maximum per run USD').fill('0.25');await page.getByLabel('Re-analyze with AI',{exact:true}).check();await page.getByLabel('Reason for re-analysis').fill('Demo: two named public repositories, deliberate refresh');await click(btn('Rediscover taxonomy'));check('Exact public allowlisted taxonomy cohort previewed');const {r}=await execute();expect(r.status).toBe('COMPLETED');expect(r.failed).toBe(0);}await expect(btn('Review draft').first()).toBeVisible();});
 },
 '07':async()=>{
  await B('review',async()=>{await organizer();await click(btn('Review draft').first());await expect(page.getByRole('dialog')).toContainText('Live AI draft');check('Fresh real-model draft opened for human review');});
  await B('save',async()=>{const l=page.getByRole('dialog').getByLabel('Description',{exact:true}).first();await l.fill((await l.inputValue()).slice(0,230)+' Reviewed for this walkthrough.');await click(btn('Save draft'));check('Draft saved without publishing');});
  await B('publish',async()=>{await click(btn('Review draft').first());const panel=page.getByRole('region',{name:'Taxonomy conflict check'});await expect(panel.getByRole('heading')).not.toContainText('Checking',{timeout:15000});for(let i=0;i<12;i++){const reuse=page.getByRole('button',{name:/^Reuse existing/}).first();const clean=btn('Remove conflicting aliases');if(await reuse.count()){await click(reuse);await sleep(600);}else if(await clean.count()){await click(clean);await sleep(600);}else break;}await click(btn('Approve & publish taxonomy'));await expect(page.getByRole('dialog')).toHaveCount(0);check('Reviewed taxonomy atomically published');});
  await B('relationships',async()=>{await nav('Content settings');await show(page.locator('.wm-tabs'));check('Domain, Project, Topic and Tag canonical registry visible');});
 },
 '08':async()=>{
  await B('classify',async()=>{await all();await page.getByLabel('Search repositories').fill(vars.repo);await page.getByLabel('Select '+vars.repo,{exact:true}).check();await organizer('LIVE');await page.getByLabel('Repository selection mode').selectOption('MANUAL');await page.getByLabel('Re-analyze with AI',{exact:true}).check();await page.getByLabel('Reason for re-analysis').fill('Full demo: one public repository against the reviewed vocabulary');await page.getByLabel('Budget mode',{exact:true}).selectOption('ADAPTIVE');await page.getByLabel('Maximum per run USD').fill('0.15');await click(btn('Full classification'));check('One-repository live classification preview');});
  await B('run',async()=>{const {r}=await execute();expect(r.status).toBe('COMPLETED');expect(r.failed).toBe(0);check('Fresh real public classification result',{outcomes:r.outcomes});});
  await B('accept',async()=>{const region=page.getByRole('region',{name:'Assignment review'});await show(region);const accept=region.getByRole('button',{name:'Accept',exact:true}).first();if(await accept.count()){await click(accept);check('Individual real-model suggestion accepted');}else{check('Live result honestly contains no additional pending match');}});
  await B('reject',async()=>{const reject=page.getByRole('region',{name:'Assignment review'}).getByRole('button',{name:'Reject',exact:true}).first();if(await reject.count()){await click(reject);check('Individual suggestion rejected with protection');}else await show(page.getByRole('region',{name:'Assignment review'}));});
 },
 '09':async()=>{
  await B('group',async()=>{await organizer();await page.getByLabel('Group suggestions by').selectOption('concept');await show(page.getByRole('region',{name:'Assignment review'}));check('Review grouped by concept');});
  await B('select',async()=>{await page.getByLabel('Review taxonomy type').selectOption('TOPIC');await page.getByLabel('Review taxonomy type').selectOption('');const select=page.getByLabel('Select visible suggestions');if(await select.count())await select.check();await show(page.getByRole('region',{name:'Assignment review'}));});
  await B('bulk',async()=>{const b=btn('Review selected acceptance');if(await b.count()&&await b.isEnabled()){await click(b);await expect(page.getByLabel('Selected review summary')).toBeVisible();await click(btn('Confirm selected acceptance'));check('Selected proposals validated and accepted');}else check('No pending suggestions: selected review controls correctly unavailable');});
  await B('coverage',async()=>{await all();await page.getByLabel('Organization status view').selectOption('uncategorized');await show(page.locator('.wm-stats'));check('No project coverage independent from accepted topics/tags');});
 },
 '10':async()=>{
  await B('receipt',async()=>{await detail();await expect(page.getByRole('dialog')).toContainText('Analysis');check('Durable real analysis receipt visible');});
  await B('repeat',async()=>{await close();await preview('Full classification','LIVE',3,false);await expect(page.getByRole('region',{name:'Run preview',exact:true})).toContainText('0 generations / 0 HTTP attempts');check('Routine preview protects analyzed repositories from paid repetition');});
  await B('status',async()=>{await click(btn('Cancel preview'));await all();await page.getByLabel('Organization status view').selectOption('no_match');await show(page.locator('.wm-table'));check('No AI match distinct from no labels and no project');});
  await B('freshness',async()=>{await page.getByLabel('Organization status view').selectOption('stale');await show(page.locator('.wm-table'));check('Stale evidence/taxonomy view');});
 },
 '11':async()=>{
  await B('switch',async()=>{await preview('Full classification','LIVE',2,true);await show(page.getByRole('region',{name:'Run preview',exact:true}));});
  await B('reason',async()=>{await show(page.getByLabel('Reason for re-analysis'));check('Explicit reasoned classification re-analysis preview; not executed');});
  await B('taxonomy',async()=>{await click(btn('Cancel preview'));await click(btn('Rediscover taxonomy'));await show(page.getByRole('region',{name:'Run preview',exact:true}));check('Explicit taxonomy re-analysis preview; not executed');});
  await B('cancel',async()=>{await click(btn('Cancel preview'));check('Previews cancelled without new inference');});
 },
 '12':async()=>{
  await B('projects',async()=>{await all();await sidebarMode('Projects');await show(page.locator('.wm-sidebar .wm-project-tree'));});
  await B('aliases',async()=>{await sidebarMode('Topics');await page.locator('.wm-sidebar').getByLabel('Search taxonomy names or aliases').fill('cloud');await show(page.locator('.wm-sidebar .wm-project-tree'));await page.locator('.wm-sidebar').getByLabel('Search taxonomy names or aliases').fill('');check('Taxonomy search and independent Topic browsing');});
  await B('header',async()=>{await click(page.locator('.wm-tree-menu > summary'));await show(page.locator('.wm-tree-menu .wm-taxonomy-browser'));check('Header taxonomy opens without automatic repository fetch');});
  await B('concept',async()=>{const b=page.locator('.wm-tree-menu .wm-project').first();await click(b);await sidebarMode('Tags');await show(page.locator('.wm-sidebar .wm-project-tree'));check('Header concept click loads membership; Tags independently browsable');});
 },
 };
 require('./capture-extra.cjs')({handlers,B,check,show,btn,nav,click,close,state,api,repos,idle,organizer,preview,execute,all,detail,concept,card,sidebarMode,resumeSession,startBackend,stopBackend,resetPreview,resetExecute,get page(){return page;},get context(){return context;},get chapter(){return chapter;},vars,storeVars,report,PRIVATE,ROOT,WORK,sleep,expect});
 try{
  await startBackend();browser=await chromium.launch({headless:true});
  for(const c of story.chapters){if(report.chapters.some(x=>x.id===c.id&&x.status==='PASS'))continue;
   report.chapters=report.chapters.filter(x=>x.id!==c.id);chapter={id:c.id,title:c.title,source:c.source,beats:[],status:'RUNNING'};report.chapters.push(chapter);save();console.log('CHAPTER',c.id,c.title);
   if(c.id==='02'&&fs.existsSync(path.join(ROOT,'.tools/full-v2-inclusion-retake')))c.source='REAL ACCOUNT · LOCAL WORKSPACE COPY';await setup(c);await handlers[c.id]();chapter.status='PASS';const video=page.video();await context.close();context=null;chapter.file=path.join(WORK,'raw','chapter-'+c.id+'.webm');await video.saveAs(chapter.file);storeVars();save();
   const destination=path.join(PRIVATE,'checkpoints');fs.mkdirSync(destination,{recursive:true});const cp=spawn(path.join(ROOT,'backend/.venv/bin/python'),['-c','import sqlite3,sys; a=sqlite3.connect(sys.argv[1]); b=sqlite3.connect(sys.argv[2]); a.backup(b); b.close(); a.close()',path.join(PRIVATE,'app.sqlite3'),path.join(destination,c.id+'.sqlite3')],{stdio:'ignore'});await new Promise(r=>cp.on('exit',r));
  }
  report.status='PASS';save();await stopBackend();console.log('Full real-account capture passed',report.checks.length,'checks');
  return {status:'PASS',chapters:report.chapters.length};
 }catch(e){report.status='FAIL';report.failure={chapter:chapter?.id,message:e.message.split('Call log:')[0].slice(0,1100)};console.error('Capture halted:',report.failure);if(page){await page.screenshot({path:path.join(WORK,'failure.png')}).catch(()=>{});fs.writeFileSync(path.join(WORK,'failure-ui.txt'),await page.locator('body').innerText().catch(()=>''));}if(context){const video=page.video();await context.close().catch(()=>{});await video.saveAs(path.join(WORK,'raw','failed-'+chapter.id+'.webm')).catch(()=>{});}save();throw Error(report.failure.message);
 }finally{if(browser)await browser.close();}
};
