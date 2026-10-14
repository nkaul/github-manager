/* Reload only our recording modules while retaining the user's in-memory login. */
const {execFileSync}=require('node:child_process');
(async()=>{
 const pid=Number(execFileSync('/usr/sbin/lsof',['-tiTCP:9130','-sTCP:LISTEN'],{encoding:'utf8'}).trim());
 if(!pid)throw Error('Recording coordinator unavailable');
 process.kill(pid,'SIGUSR1');
 await new Promise(r=>setTimeout(r,350));
 const targets=await(await fetch('http://127.0.0.1:9229/json/list')).json();
 const ws=new WebSocket(targets[0].webSocketDebuggerUrl);
 await new Promise(r=>ws.addEventListener('open',r,{once:true}));
 const expression="(()=>{const cache=process.mainModule.require('node:module')._cache;let n=0;for(const k of Object.keys(cache)){if(k.includes('/demo/tools/full-v2/capture-')){delete cache[k];n++;}}return n;})()";
 ws.send(JSON.stringify({id:1,method:'Runtime.evaluate',params:{expression}}));
 await new Promise((resolve,reject)=>ws.addEventListener('message',e=>{const r=JSON.parse(e.data);if(r.id===1){if(r.result?.exceptionDetails)reject(Error('Coordinator reload failed'));else{console.log('Recording modules reloaded:',r.result.result.value);resolve();}}}));
 ws.send(JSON.stringify({id:2,method:'Runtime.evaluate',params:{expression:"setTimeout(()=>process.mainModule.require('node:inspector').close(),100); 'closed'"}}));
 ws.close();
})().catch(e=>{console.error(e.message);process.exitCode=1;});
