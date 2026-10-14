/* Real-account workflows, with destructive checks restricted to the copy. */
const fs=require('node:fs'),path=require('node:path');
module.exports=function(h){
 const {handlers,B,check,show,btn,nav,click,close,state,api,idle,organizer,preview,execute,all,detail,concept,card,sidebarMode,resumeSession,startBackend,stopBackend,resetPreview,resetExecute,vars,storeVars,report,sleep,expect}=h;
 const p=()=>h.page;
 const users=s=>Object.fromEntries(Object.entries(s.organization.edges).map(([k,v])=>[k,Object.fromEntries(Object.entries(v).filter(([,e])=>e.source==='USER'))]).filter(([,v])=>Object.keys(v).length));
 async function projectSetup(){vars.domain=(await concept('DOMAIN','Walkthrough Operations')).id;vars.project=(await concept('PROJECT','Walkthrough Console',vars.domain,'walkthrough cockpit')).id;vars.project2=(await concept('PROJECT','Walkthrough Services',vars.domain)).id;vars.topic=(await concept('TOPIC','Walkthrough Review')).id;vars.tag=(await concept('TAG','Walkthrough Favorite')).id;storeVars();}
 async function selectTwo(){await all();await p().getByLabel('Search repositories').fill('');for(const name of [vars.repo,vars.repo2]){await p().getByLabel('Search repositories').fill(name);await p().getByLabel('Select '+name,{exact:true}).check();}await p().getByLabel('Search repositories').fill('');}
 async function drop(name,target){
  await p().evaluate(()=>{window.demoDragEvents=[];for(const type of ['dragstart','dragenter','dragover','drop','dragend'])document.addEventListener(type,e=>{if(type!=='dragover')window.demoDragEvents.push({type,tag:e.target.tagName,data:e.dataTransfer?.getData('text/plain')});});});
  const browser=target.locator('xpath=ancestor::*[contains(@class,"wm-taxonomy-browser")][1]');
  await browser.getByLabel('Search taxonomy names or aliases').fill('Walkthrough');
  const row=p().locator('tr',{has:p().getByLabel('Select '+name,{exact:true})});
  await row.dragTo(target,{sourcePosition:{x:700,y:45}});await sleep(700);
  fs.writeFileSync(path.join(h.WORK,'drag-diagnostics.json'),JSON.stringify(await p().evaluate(()=>window.demoDragEvents),null,2));
 }
 if(fs.existsSync(path.join(h.ROOT,'.tools/full-v2-inclusion-retake')))handlers['02']=async()=>{
  await B('candidates',async()=>{
   await detail();await expect(btn('Include in My Repos')).toBeVisible();await click(btn('Include in My Repos'));await close();await nav('My Repos');await p().getByLabel('Search repositories').fill(vars.repo);await expect(btn('Details for '+vars.repo)).toBeVisible();await show(p()['locator']('tbody tr'));check('Explicit inclusion adds a real access candidate to My Repos in the workspace copy');
  });
  await detail();await click(btn('Remove explicit inclusion'));await close();check('Demo inclusion reversed in the copy after the recorded action');
 };
 handlers['05']=async()=>{
  await B('load',async()=>{await detail();check('Real public repository in copied workspace');});
  await B('extract',async()=>{await close();await all();await p().getByLabel('Search repositories').fill(vars.repo);await p().getByLabel('Select '+vars.repo,{exact:true}).check();await organizer('CACHE');await p().getByLabel('Repository selection mode').selectOption('MANUAL');await click(btn('Extract evidence'));await execute();await detail();await expect(p().getByRole('dialog')).toContainText('demo-rake-tfidf-v2');check('Actual local evidence extraction revalidates a real public README with no model request');});
  await B('details',async()=>{await show(p()['locator']('.wm-evidence').first());await p().getByRole('dialog').evaluate(el=>el.scrollTop=el.scrollHeight/2);await show(p()['locator']('.wm-evidence').last());});
  await B('privacy',async()=>{await close();await organizer();await show(p().getByRole('region',{name:'AI run setup'}));check('Public evidence policy and extractor version visible');});
 };
 handlers['09']=async()=>{
  for(const name of ['Asset Management','Data Center','Back Office Hardware'])await concept('TOPIC',name);
  await all();await p().getByLabel('Search repositories').fill(vars.repo);await p().getByLabel('Select '+vars.repo,{exact:true}).check();await organizer('CACHE');
  await p().getByLabel('Repository selection mode').selectOption('MANUAL');await p().getByLabel('Re-analyze with AI',{exact:true}).uncheck();await click(btn('Full classification'));await execute();
  await B('group',async()=>{await p().getByLabel('Group suggestions by').selectOption('concept');await show(p().getByRole('region',{name:'Assignment review'}));const reject=p().getByRole('region',{name:'Assignment review'}).getByRole('button',{name:'Reject',exact:true}).first();await expect(reject).toBeVisible();await click(reject);check('Individual locally supported proposal rejected with protection');});
  await B('select',async()=>{await p().getByLabel('Select visible suggestions').check();await show(p().getByRole('region',{name:'Assignment review'}));check('Filtered real-repository proposals selected');});
  await B('bulk',async()=>{await click(btn('Review selected acceptance'));await expect(p().getByLabel('Selected review summary')).toBeVisible();await click(btn('Confirm selected acceptance'));check('Selected offline proposals validated and accepted');});
  await B('coverage',async()=>{await all();await p().getByLabel('Organization status view').selectOption('uncategorized');await show(p()['locator']('.wm-stats'));check('Topic labels and Project coverage remain distinct');});
 };
 handlers['13']=async()=>{
  await projectSetup();
  await B('single',async()=>{
   await all();await sidebarMode('Topics');await p().getByLabel('Search repositories').fill(vars.repo);
   const target=p()['locator']('.wm-sidebar').getByRole('button',{name:'Walkthrough Review',exact:true});
   await drop(vars.repo,target);await expect(p()['locator']('tbody tr')).toContainText('Walkthrough Review');
   check('Single native drop onto Topic adds membership');
  });
  await B('multi',async()=>{
   await all();await p().getByLabel('Search repositories').fill('');await expect(p()['locator']('tbody tr')).not.toHaveCount(1);await p().getByLabel('Select '+vars.repo,{exact:true}).check();await p().getByLabel('Select '+vars.repo2,{exact:true}).check();await expect(p()['locator']('.wm-stat-selected strong')).toHaveText('2');
   const names='Select '+vars.repo;
   await sidebarMode('Tags');await drop(names.slice(7),p()['locator']('.wm-sidebar').getByRole('button',{name:'Walkthrough Favorite',exact:true}));
   await expect(p().getByRole('dialog')).toContainText('2 repositories');await click(btn('Confirm membership addition'));check('Two-repository selected set native drop confirmed');
  });
  await B('domain',async()=>{
   await all();const clear=btn('Clear');if(await clear.count())await clear.click();await p().getByLabel('Search repositories').fill(vars.repo);await sidebarMode('Projects');
   await drop(vars.repo,p()['locator']('.wm-sidebar').getByRole('button',{name:'Walkthrough Operations',exact:true}));
   await p().getByLabel('Project for domain drop').selectOption(vars.project);await click(btn('Confirm membership addition'));check('Domain drop requires child Project selection');
  });
  await B('headerdrop',async()=>{
   await click(p()['locator']('.wm-tree-menu > summary'));await drop(vars.repo,p()['locator']('.wm-tree-menu').getByRole('button',{name:'Walkthrough Services',exact:true}));
   if(await p().getByRole('dialog').count())await click(btn('Confirm membership addition'));await detail();await expect(p().getByRole('dialog')).toContainText('Walkthrough Services');check('Header taxonomy drop adds another membership');
  });
 };
 handlers['14']=async()=>{
  await B('bulkadd',async()=>{await all();await p().getByLabel('Search repositories').fill(vars.repo);await p().getByLabel('Select '+vars.repo,{exact:true}).check();await p().getByLabel('Bulk assignment concept').selectOption(vars.project2);await click(btn('Add membership'));check('Bulk selector adds reviewed membership');});
  await B('details',async()=>{await detail();await show(p().getByRole('dialog'));await expect(btn('Remove Walkthrough Console')).toBeVisible();});
  await B('remove',async()=>{await click(btn('Remove Walkthrough Services'));await expect(btn('Remove Walkthrough Console')).toBeVisible();await expect(btn('Remove Walkthrough Services')).toHaveCount(0);check('Removing one membership preserves others and rejection protection');});
  await B('selection',async()=>{await close();await all();await p().getByLabel('Search repositories').fill(vars.repo);await p().getByLabel('Select '+vars.repo,{exact:true}).check();await p().getByLabel('Search repositories').fill('aws');await expect(p()['locator']('.wm-stat-selected strong')).toHaveText('0');check('Filter changes clear selection');});
 };
 handlers['15']=async()=>{
  await B('create',async()=>{await concept('PROJECT','Walkthrough Temporary',vars.domain,'walkthrough legacy');check('Manual canonical concept creation');});
  await B('edit',async()=>{const c=await card('PROJECT','Walkthrough Temporary');await click(c.getByRole('button',{name:'Edit',exact:true}));await p().getByLabel('Name',{exact:true}).fill('Walkthrough Renamed');await p().getByRole('dialog').getByLabel('Aliases',{exact:false}).first().fill('walkthrough legacy, walkthrough spare');await click(btn('Save concept'));vars.temporary=Object.values((await state()).organization.concepts).find(c=>c.name==='Walkthrough Renamed').id;storeVars();check('Rename and aliases preserve canonical identity');});
  await B('duplicate',async()=>{await click(btn('+ Create concept'));await p().getByRole('combobox',{name:/^Type/}).selectOption('PROJECT');await p().getByLabel('Name',{exact:true}).fill('Walkthrough Collision');await p().getByRole('dialog').getByLabel('Aliases',{exact:false}).first().fill('walkthrough spare');await p().getByRole('combobox',{name:/^Parent domain/}).selectOption(vars.domain);await click(btn('Save concept'));await expect(p().getByRole('dialog')).toContainText('Walkthrough Renamed');await expect(p().getByRole('dialog').getByRole('alert')).toBeVisible();check('Reserved alias error identifies existing owner');});
  await B('reserved',async()=>{await click(p().getByRole('button',{name:/^Remove alias/}).first());await click(btn('Save concept'));await expect(p().getByRole('dialog')).toHaveCount(0);check('Opt-in alias remediation saves distinct concept');});
 };
 handlers['16']=async()=>{
  await B('merge',async()=>{await concept('PROJECT','Walkthrough Prior Console',vars.domain);const c=await card('PROJECT','Walkthrough Prior Console');await click(c.getByRole('button',{name:'Merge',exact:true}));await p().getByRole('combobox',{name:/^Merge into/}).selectOption(vars.temporary);await click(btn('Confirm merge'));expect((await state()).organization.concepts[vars.temporary].active).toBe(true);check('Merge preserves chosen target identity');});
  await B('distinct',async()=>{await show(await card('PROJECT','Walkthrough Renamed'));});
  await B('archive',async()=>{const c=await card('DOMAIN','Walkthrough Operations');await click(c.getByRole('button',{name:'Archive',exact:true}));await expect(p().getByRole('dialog')).toContainText('Unassigned');await click(btn('Archive concept'));check('Domain archive explains dependent Projects');});
  await B('verify',async()=>{const s=await state();expect(s.organization.concepts[s.organization.concepts[vars.project].domain].name).toBe('Unassigned');await show(await card('PROJECT','Walkthrough Console'));check('Surviving Project reparented to Unassigned');});
 };
 handlers['17']=async()=>{
  await api('/recording/reopen',{});await p().reload();await organizer();
  await B('conflicts',async()=>{await click(btn('Review draft').first());const boxes=p().getByRole('dialog')['locator']('fieldset input[type=checkbox]');for(let i=1;i<await boxes.count();i++)await boxes.nth(i).uncheck();await p().getByLabel('Proposal 1 name').fill('AI - Artificial Intelligence');await p().getByLabel('Proposal 1 aliases').fill('AI, Cloud Applications');await expect(p().getByRole('region',{name:'Taxonomy conflict check'})).toContainText('Archived — reservation retained Domain: AI');check('Manually edited saved real draft exposes actual archived AI and active Domain reservations');});
  await B('reuse',async()=>{await click(p().getByRole('button',{name:'Reuse existing “Cloud Applications”',exact:true}));await expect(p().getByLabel('Proposal 1 name')).toHaveValue('Cloud Applications');check('Reuse retains actual active canonical term');});
  await B('undo',async()=>{await click(btn('Undo last repair'));await expect(p().getByLabel('Proposal 1 name')).toHaveValue('AI - Artificial Intelligence');check('Undo restores previous form');});
  await B('repair',async()=>{await click(btn('Remove conflicting aliases'));await expect(p().getByRole('region',{name:'Taxonomy conflict check'})).toContainText('Names and aliases are ready');await click(btn('Save draft'));check('Alias repair saved without publication');});
 };
 handlers['18']=async()=>{
  await B('rule',async()=>{await nav('Content settings');await click(btn('+ Create rule'));await p().getByLabel('Rule name').fill('Walkthrough Python repositories');await p().getByLabel('Value',{exact:true}).fill('Python');await p().getByRole('combobox',{name:/^Assign concept/}).selectOption(vars.tag);await click(btn('Preview matches'));await expect(p().getByRole('dialog')).toContainText('matching repositories');check('Rule preview checks real metadata');});
  await B('approve',async()=>{await click(btn('Approve rule'));check('Deterministic rule explicitly approved');});
  await B('incremental',async()=>{await preview('Reorganize incremental','RULES',3,false);await execute();check('Rules-only incremental run uses no model calls');});
  await B('full',async()=>{await all();await p().getByLabel('Search repositories').fill(vars.repo);await p().getByLabel('Select '+vars.repo,{exact:true}).check();await organizer('RULES');await p().getByLabel('Repository selection mode').selectOption('MANUAL');await click(btn('Full classification'));await execute();await detail();await expect(p().getByRole('dialog')).toContainText('Walkthrough Favorite');check('Rules-only full cohort preserves USER memberships');});
 };
 handlers['19']=async()=>{
  await B('usage',async()=>{await organizer();await show(p()['locator']('.wm-budget'));check('Window limits and cumulative money distinguished');});
  await B('renew',async()=>{await click(btn('Manage API allowance'));await p().getByLabel('HTTP requests in window').fill('20');await p().getByLabel('Reason for allowance change').fill('Recording copy only: demonstrate allowance renewal');await click(btn('Renew allowance window'));expect((await state()).budget.http.used).toBe(0);check('Copied allowance renewed; original ledger untouched');});
  await B('override',async()=>{const before=(await state()).budget;await click(btn('Manage API allowance'));await p().getByLabel('Allowance action').selectOption('SET_LIMITS');await p().getByLabel('HTTP requests in window').fill('24');await p().getByLabel('Reason for allowance change').fill('Recording copy only: change HTTP independently');await click(btn('Save selected limits'));const after=(await state()).budget;expect(after.http.limit).toBe(24);expect(after.generations.limit).toBe(before.generations.limit);check('Selective HTTP override preserves generation limit');});
  await B('money',async()=>{await show(p()['locator']('.wm-budget'));expect((await state()).budget.cap_usd).toBe(5);check('Five-dollar cumulative cap retained');});
 };
 handlers['20']=async()=>{
  await B('adaptive',async()=>{await organizer();await p().getByLabel('Budget mode',{exact:true}).selectOption('ADAPTIVE');await p().getByLabel('Maximum per run USD').fill('0.15');await show(p().getByLabel('Budget mode',{exact:true}));});
  await B('bound',async()=>{await preview('Full classification','LIVE',3,false);await show(p().getByRole('region',{name:'Run preview',exact:true}));check('Adaptive preview has finite cohort and cost bound');});
  await B('defaults',async()=>{await click(btn('Cancel preview'));await p().getByLabel('Taxonomy sample size').fill('2');await p().getByLabel('Classification batch size',{exact:true}).fill('3');await click(btn('Save defaults'));expect((await state()).preferences.classification_count).toBe(3);check('Run defaults saved without starting work');});
  await B('local',async()=>{await click(btn('Full classification'));await expect(p().getByRole('region',{name:'Run preview',exact:true})).toContainText('0 generations / 0 HTTP attempts');await click(btn('Cancel preview'));check('Adaptive mode retains offline protection');});
 };
 handlers['21']=async()=>{
  await B('thresholds',async()=>{await organizer();await click(p()['locator']('.wm-automation > summary'));await p().getByLabel('Weighted changes').fill('100');await p().getByLabel('Distinct entities').fill('100');await p().getByLabel('New projects (0 disables)').fill('2');await show(p().getByLabel('Weighted changes'));check('Weighted, distinct and Project thresholds configurable');});
  await B('types',async()=>{await p().getByLabel('Quiet period (seconds)').fill('90');await p().getByLabel('Cooldown (seconds)').fill('1800');const field=p()['locator']('.wm-automation fieldset');for(const l of ['Create','Edit','Archive','Merge','Rule','Evidence']){const b=field.getByRole('checkbox',{name:l,exact:true});if(await b.count())await b.uncheck();}await field.getByRole('checkbox',{name:'Create Project',exact:true}).check();await p().getByRole('checkbox',{name:'Automatic organization after significant edits',exact:true}).uncheck();await click(btn('Save automatic settings'));check('Automatic policy saved with actual 90-second quiet interval');});
  await B('scheduler',async()=>{const parent=Object.values((await state()).organization.concepts).find(c=>c.active&&c.kind==='DOMAIN').id;await concept('PROJECT','Walkthrough Automatic Alpha',parent);await concept('PROJECT','Walkthrough Automatic Beta',parent);vars.autoStarted=Math.max(...(await state()).organization.changes.map(e=>e.at))*1000;await organizer();await click(p()['locator']('.wm-automation > summary'));await p().getByRole('checkbox',{name:'Automatic organization after significant edits',exact:true}).check();await click(btn('Save automatic settings'));await show(p()['locator']('.wm-automation'));storeVars();});
  await B('automatic',async()=>{let s;const deadline=Date.now()+135000;do{await sleep(700);s=await state();}while(!Object.values(s.organization.runs).some(r=>r.reason==='AUTO'&&r.status==='COMPLETED')&&Date.now()<deadline);const auto=Object.values(s.organization.runs).find(r=>r.reason==='AUTO'&&r.status==='COMPLETED');expect(auto).toBeTruthy();expect(auto.failed).toBe(0);expect(Date.parse(auto.created_at)-vars.autoStarted).toBeGreaterThanOrEqual(89000);expect(Object.values(auto.outcomes).every(v=>['LOCAL_MATCH','STORED_ANALYSIS','LOCAL_RULES'].includes(v.evidence))).toBe(true);check('Actual automatic scheduler reconciles real repositories locally',{wait_seconds:(Date.now()-vars.autoStarted)/1000,processed:auto.processed,provenance:Object.values(auto.outcomes).map(o=>o.evidence)});await api('/organizer/settings',{auto_enabled:false},'PATCH');await p().reload();await organizer();await show(p()['locator']('.wm-run').first());report.notes.push('Actual 90-second scheduler wait shortened by a discrete edit; scheduler not accelerated.');});
 };
 handlers['22']=async()=>{
  await B('appearance',async()=>{await nav('Content settings');await p().getByRole('radio',{name:/Blue zen rays/}).check();await show(p().getByRole('region',{name:'Appearance settings'}));check('Tail-free rays logo selected');});
  await B('aura',async()=>{await p().getByRole('radio',{name:/Continuous blue aura/}).check();await expect(p()['locator']('.wm-header .wm-logo')).toHaveAttribute('data-logo','orbit');check('Aura preference updates header');});
  await B('pause',async()=>{await p().getByRole('checkbox',{name:'Animate logo',exact:true}).uncheck();await expect(p()['locator']('.wm-header .wm-logo img')).toHaveAttribute('src',/poster\.svg/);await p().emulateMedia({reducedMotion:'reduce'});check('Animation-off and reduced-motion static presentation');});
  await B('restore',async()=>{await p().emulateMedia({reducedMotion:'no-preference'});await click(btn('Restore default logo'));check('Restore default clears browser override');});
 };
 handlers['23']=async()=>{
  await p().setViewportSize({width:390,height:844});h.chapter.mobile=true;
  await B('phone',async()=>{await expect(p().getByLabel('Open navigation',{exact:true})).toBeVisible();await show(p()['locator']('.wm-brand'));check('Actual 390×844 phone viewport');});
  await B('drawer',async()=>{await click(p().getByLabel('Open navigation',{exact:true}));await expect(p()['locator']('.wm-sidebar')).toHaveClass(/is-open/);await click(btn('Access candidates'));check('Phone drawer opens and closes on selection');});
  await B('keyboard',async()=>{await p().getByLabel('Search repositories').fill(vars.repo);await click(btn('Details for '+vars.repo));await p().getByRole('dialog').getByRole('combobox').focus();check('Phone details assignment is keyboard focusable');});
  await B('responsive',async()=>{await close();await show(p()['locator']('.wm-stats'));expect(await p().evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);check('No page-level phone overflow');});
 };
 handlers['24']=async()=>{
  let before;
  await B('reload',async()=>{before=await state();await p().reload();const after=await state();expect(users(after)).toEqual(users(before));expect(after.preferences).toEqual(before.preferences);check('Reload preserves organization and defaults');});
  await B('signout',async()=>{await click(p().getByLabel('Account menu'));await click(p().getByLabel('Sign out',{exact:true}));await expect(p().getByRole('heading',{name:'Connect your GitHub account'})).toBeVisible();await resumeSession();await p().reload();expect(users(await state())).toEqual(users(before));check('Sign-out and recording-copy session restoration preserve records');});
  await B('restart',async()=>{await stopBackend();await startBackend();await p().reload();await expect(p().getByRole('heading',{name:'Connect your GitHub account'})).toBeVisible();await resumeSession();await p().reload();const after=await state();expect(users(after)).toEqual(users(before));expect(after.organization.concepts).toEqual(before.organization.concepts);check('Actual copied backend process restart preserves data and requires new session');});
  await B('recover',async()=>{await organizer();await show(p()['locator']('.wm-budget'));check('Completed history and money preserved after restart');});
 };
 handlers['25']=async()=>{
  await B('rediscover',async()=>{await preview('Rediscover taxonomy','LIVE',2,true);await show(p().getByRole('region',{name:'Run preview',exact:true}));await click(btn('Cancel preview'));check('Intentional taxonomy refresh preview only');});
  await B('draft',async()=>{if(!await btn('Review draft').count()){await api('/recording/reopen',{});await p().reload();await organizer();}await click(btn('Review draft').first());await show(p().getByRole('dialog'));check('Saved draft review leaves registry untouched');});
  await B('rejectdraft',async()=>{await close();const before=(await state()).organization.control.revision;await click(btn('Reject draft').first());expect((await state()).organization.control.revision).toBe(before);check('Draft rejection preserves published revision');});
  await B('separate',async()=>{await nav('Content settings');await show(p()['locator']('.wm-concept-grid'));});
 };
 handlers['26']=async()=>{
  await B('scope',async()=>{await resetPreview();await show(p().getByRole('dialog'));check('Independent scopes and server reset impact');});
  await B('impact',async()=>{await show(p().getByRole('dialog').getByText('Server-verified impact',{exact:false}).first());});
  await B('confirm',async()=>{await p().getByLabel('Type exactly DELETE').fill('DELETE ');await expect(btn('Confirm reset')).toBeDisabled();await p().getByLabel('Type exactly DELETE').fill('DELETE');await expect(btn('Confirm reset')).toBeEnabled();check('Exact DELETE required; trailing space rejected');});
  await B('safe',async()=>{await close();check('First reset preview cancelled without removal');});
 };
 handlers['27']=async()=>{
  let before;
  await B('witness',async()=>{before=await state();expect(Object.keys(users(before)).length).toBeGreaterThan(0);expect(Object.keys(before.organization.rejections).length).toBeGreaterThan(0);await detail();check('USER memberships and rejection witnesses recorded');});
  await B('execute',async()=>{await close();await resetPreview({ai:true});await resetExecute();});
  await B('preserve',async()=>{const after=await state();expect(users(after)).toEqual(users(before));expect(after.organization.rejections).toEqual(before.organization.rejections);expect(after.coverage.repos).toBe(before.coverage.repos);expect(after.organization.control.revision).toBe(before.organization.control.revision);expect(Object.keys(after.organization.analysis)).toEqual(Object.keys(before.organization.analysis));await detail();check('AI reset preserves inventory, USER decisions, rejections and receipts');});
  await B('restartdraft',async()=>{await close();await preview('Rediscover taxonomy','CACHE',2,false);await show(p().getByRole('region',{name:'Run preview',exact:true}));await click(btn('Cancel preview'));check('Cached restart preview retains taxonomy analysis protection');});
 };
 handlers['28']=async()=>{
  await B('domainreset',async()=>{await resetPreview({kinds:['Domains'],ai:false});await show(p().getByRole('dialog'));});
  await B('depend',async()=>{await resetExecute();const s=await state();expect(Object.values(s.organization.concepts).filter(c=>c.active&&c.kind==='PROJECT').every(c=>s.organization.concepts[c.domain].name==='Unassigned')).toBe(true);check('Domain reset reparents surviving Projects to Unassigned');});
  await B('projects',async()=>{await all();await sidebarMode('Projects');await show(p()['locator']('.wm-sidebar .wm-project-tree'));});
  await B('scoped',async()=>{await sidebarMode('Topics');await show(p()['locator']('.wm-sidebar .wm-project-tree'));check('Independent Topics retained after Domain-only reset');});
 };
 handlers['29']=async()=>{
  let old;
  await B('fullreset',async()=>{old=await state();await resetPreview({kinds:['Domains','Projects','Topics','Tags'],ai:true,cache:false,rules:true});await show(p().getByRole('dialog'));});
  await B('verifyreset',async()=>{const s=await resetExecute();expect(s.coverage.repos).toBe(old.coverage.repos);expect(s.organization.control.taxonomy_epoch).toBeGreaterThan(old.organization.control.taxonomy_epoch);check('Full taxonomy reset advances epoch while retaining real inventory');});
  await B('rebuild',async()=>{const d=await concept('DOMAIN','Cloud Applications');const project=await concept('PROJECT','Serverless Stack Guide Demo',d.id);expect(Object.keys(old.organization.concepts)).not.toContain(project.id);await show(await card('PROJECT',project.name));check('Manual rebuild uses new canonical identifiers');});
  await B('norepeat',async()=>{await preview('Full classification','LIVE',3,false);await expect(p().getByRole('region',{name:'Run preview',exact:true})).toContainText('0 generations / 0 HTTP attempts');await click(btn('Cancel preview'));check('Full reset still protects compact prior-analysis receipts');});
 };
 handlers['30']=async()=>{
  const r=await h.context.request.post('http://127.0.0.1:8124/api/v1/recording/restore',{headers:{'X-Recording-Key':global.fullDemoBackend.key}});expect(r.ok()).toBeTruthy();await p().reload();report.notes.push('After the verified reset tests, the recording copy was restored from the unchanged real-account snapshot for the closing chapters.');
  await B('history',async()=>{await organizer();await click(p()['locator']('.wm-run').first()['locator']('summary'));await show(p()['locator']('.wm-run').first());check('Persisted real run history and provenance inspected');});
  await B('nomatch',async()=>{await all();for(const view of ['no_match','failed','stale']){await p().getByLabel('Organization status view').selectOption(view);await sleep(400);}check('No match, failed and stale status views browsed');});
  await B('cachemiss',async()=>{await preview('Rediscover taxonomy','CACHE',2,false);await show(p().getByRole('region',{name:'Run preview',exact:true}));await click(btn('Cancel preview'));check('Cached preview starts no paid fallback');});
  await B('provenance',async()=>{await organizer();await show(p()['locator']('.wm-run').first());check('Actual history distinguished from fresh live and local operations');});
 };
 handlers['31']=async()=>{
  await B('evidence',async()=>{await detail();await show(p().getByRole('dialog'));check('Earlier readiness evidence retained separately');});
  await B('preservation',async()=>{await close();await organizer();await show(p()['locator']('.wm-budget'));});
  await B('cloud',async()=>{await all();await show(p()['locator']('.wm-sidebar-status'));check('Local runtime accurately identified');});
  await B('limits',async()=>{await show(p()['locator']('.wm-coverage'));check('Bounded GitHub coverage disclosed');});
 };
 handlers['32']=async()=>{
  await B('sequence',async()=>{await nav('My Repos');await show(p()['locator']('.wm-stats'));});
  await B('reviewagain',async()=>{await sidebarMode('Topics');await show(p()['locator']('.wm-sidebar .wm-project-tree'));});
  await B('advanced',async()=>{await organizer();await show(p().getByRole('region',{name:'AI run setup'}));});
  await B('close',async()=>{await nav('My Repos');await p().evaluate(()=>window.scrollTo(0,0));await show(p()['locator']('.wm-brand'));check('Complete chaptered real-account walkthrough finished');});
 };
};
