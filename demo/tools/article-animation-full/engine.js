/* Illustrated state changes; no remote assets or autonomous model activity. */
for(let i=1;i<=8;i++){
 const names=['actual-system','retrieval-and-generation','evidence-and-chunking','controlled-analysis-loop','harness-and-tokenomics','evaluation-evidence','contextual-retrieval-comparison','future-experiment-roadmap'];
 files['detail'+i]=asset(`ai-system-design/illustrated/figures/0${i}-${names[i-1]}.png`);
}
const measure=document.createElement('canvas').getContext('2d');
function wrap(s,size,max){measure.font=`${size}px Ink`;const out=[];let row='';for(const word of String(s).split(/\s+/)){const next=row?row+' '+word:word;if(measure.measureText(next).width>max&&row){out.push(row);row=word}else row=next}if(row)out.push(row);return out}
function fit(s,max,size=64,min=44){while(size>min&&wrap(s,size,max).length>1)size--;return size}
function fullHeader(b){const n=Number(b.chapter_id.slice(0,2));let titleSize=fit(b.title,1710,64,48);return txt(96,57,`SECTION ${String(n).padStart(2,'0')} / 18 · ${b.chapter_title.toUpperCase()}`,24,C.indigo,'start','small')+txt(1820,94,b.layout==='intro'&&n>=16?'Current boundary / proposed research':b.status,22,C.muted,'end','small')+txt(96,167,b.title,titleSize,C.indigo)+wash(96,183,Math.min(1690,measure.measureText(b.title).width),10,C.lav)+lines(98,238,wrap('Purpose: '+b.purpose,30,1710),30,41,C.muted)}
function fullRibbon(b){const names=['Purpose','Context','Vocabulary','Retrieve','Augment','Generate','Review','Remember','Evaluate','Research'];const n=Number(b.chapter_id.slice(0,2));const active=({1:0,2:2,3:1,4:1,5:1,6:2,7:3,8:4,9:5,10:6,11:7,12:7,13:5,14:5,15:8,16:9,17:9,18:0})[n];let out='';names.forEach((s,i)=>{let x=100+i*172;out+=wash(x,983,158,43,i===active?C.lav:'#f5f6fa')+txt(x+79,1013,s,23,i===active?C.indigo:C.muted,'middle')});return out}
function paper(x,y,w,h,data,i,phase,layout){const p=ease(phase);let titleRows=wrap(data.title,35,w-138);let size=33;let body=[];do{body=data.lines.flatMap(s=>wrap(s,size,w-64));if(body.length<=7)break;size--}while(size>=26);
 let content=box(x,y,w,h,i===1?C.lav:(i===2?C.light:'#fff'));
 content+=`<path d="M${x+w-62},${y+4} L${x+w-62},${y+49} L${x+w-5},${y+49}" fill="none" stroke="${C.ink}" stroke-width="2" opacity=".35"/>`;
 content+=icon(data.icon||'receipt',x+25,y+27,1.05,i===1?C.purple:C.indigo);
 content+=lines(x+112,y+62,titleRows,35,44,C.indigo);
 content+=lines(x+32,y+165,body,size,43,C.ink);
 if(layout==='metrics')content+=`<path d="M${x+26},${y+h-54} L${x+45},${y+h-18} H${x+w-45} L${x+w-26},${y+h-54}" fill="${C.light}" stroke="${C.indigo}" stroke-width="3"/>`;
 return group(content,0,24*(1-p),1,0,p);
}
function introScene(b){let out=fullHeader(b);out+=reveal(lines(116,403,wrap(b.purpose,48,790),48,69,C.indigo),progress(.35,1.4));out+=reveal(person(112,660,330,210)+txt(475,772,'Start with the question.',36,C.indigo),progress(1.7,1.4));out+=reveal(box(961,330,850,493,'#fff')+`<image href="${files['detail'+b.figure]}" x="976" y="343" width="818" height="459" preserveAspectRatio="xMidYMid meet"/>`,progress(2.8,1.7));out+=txt(1380,863,'Reference illustration · details unfold next',26,C.muted,'middle','small');return out+fullRibbon(b)}
function flowScene(b){let out=fullHeader(b);const events=b.reveal_times||[.4,10,20];
 b.cards.forEach((data,i)=>{const p=(local-events[i])/1.5;out+=paper(100+i*580,337,525,463,data,i,p,b.layout);if(i<2&&b.layout==='pipeline')out+=arrow(642+i*580,566,666+i*580,566,ease((local-events[i+1])/.9),C.blue)});
 if(b.layout==='request'){
  const p=ease((local-events[2])/1.5);out+=reveal(`<path d="M885 843 L960 885 L1035 843 M885 843 V918 H1035 V843Z" fill="white" stroke="${C.indigo}" stroke-width="3"/>`,p);out+=travel('E1',365,771,960,860,events[2],1.5)+travel('IDs',945,771,960,860,events[2]+.2,1.5)+travel('Policy',1525,771,960,860,events[2]+.4,1.5);
 }else if(b.layout==='budget'){
  const p=ease((local-events[2])/1.5);for(let i=0;i<3;i++){const x=b.id==='13-harness-02'?lerp(950,1120,p):960,y=842-i*11;out+=`<ellipse cx="${x}" cy="${y}" rx="28" ry="10" fill="#ffdf72" stroke="#7c6322" stroke-width="2"/>`}
  out+=reveal(icon('receipt',1300,818,.8,C.indigo)+txt(1375,856,'Recorded',27,C.indigo),ease((local-events[2])/1.5));
 }else if(b.layout==='receipt'||b.layout==='state'||b.layout==='timeline'){
  out+=reveal(icon('receipt',b.layout==='receipt'?1160:125,824,.8,C.indigo)+txt(b.layout==='receipt'?1225:190,862,b.layout==='receipt'?'Receipt retained':'State and history remain visible',29,C.indigo),ease((local-events[2])/1.5));
 }else if(b.layout==='keywords'){
  out+=travel('phrase',358,750,930,840,events[1],1.5)+travel('rank',930,840,1530,750,events[2],1.5)+reveal(txt(110,878,'patient + intake + api → 3 + 3 + 3 = 9',31,C.indigo),ease((local-events[2])/1.5));
 }else if(b.layout==='selection'){
  out+=reveal(icon('check',115,823,.75,C.green)+txt(178,860,'Supported IDs remain proposals until review.',29,C.indigo),ease((local-events[2])/1.5));
 }else out+=reveal(robot(1553,815,120,133)+txt(110,858,b.layout==='retrieval'?'Six candidates · three independent kinds':'Read the evidence. Inspect the consequence.',30,C.indigo),ease((local-events[2])/1.5));
 if(b.layout==='receipt')out+=reveal(pill(110,816,530,'Orion Project removed',C.lav,29)+`<path d="M132 846 H616" stroke="${C.purple}" stroke-width="4"/>`,ease((local-events[1])/1.5));
 if(b.note){const rows=wrap(b.note,24,1690).slice(0,2);out+=lines(106,927,rows,24,31,C.muted)}
 return out+fullRibbon(b);
}
window.setTimeline=value=>{timeline=value;window.seek(0)};
window.seek=t=>{if(!timeline)return;now=clamp(t,0,timeline.duration-.00001);let i=timeline.beats.findIndex(b=>now>=b.start&&now<b.end);if(i<0)i=timeline.beats.length-1;scene=timeline.beats[i];local=now-scene.start;uid=0;const body=scene.layout==='intro'?introScene(scene):flowScene(scene);const opacity=clamp(local/.35)*clamp((scene.end-now)/.35);document.getElementById('scene').innerHTML=`<g opacity="${opacity}">${body}</g>`;window.frameState={time:now,beat:scene.id,chapter:scene.chapter_id,index:i,local};return window.frameState};
window.audit=()=>{const bad=[];document.querySelectorAll('text').forEach(el=>{const b=el.getBoundingClientRect();if(b.width&&b.height&&(b.left<35||b.right>1885||b.top<18||b.bottom>1045))bad.push({text:el.textContent,box:{x:b.x,y:b.y,width:b.width,height:b.height}})});return {bad,state:window.frameState,font:document.fonts.check('40px Ink')}};
window.ready=false;
Promise.all([document.fonts.load('40px Ink'),...Object.values(files).map(src=>new Promise((resolve,reject)=>{const i=new Image();i.onload=resolve;i.onerror=reject;i.src=src}))]).then(()=>window.ready=true);
