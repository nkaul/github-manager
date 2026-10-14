/* User sign-in only; cookies remain in memory and login is never recorded. */
const {chromium}=require('../../../frontend/node_modules/@playwright/test');
const http=require('node:http'),path=require('node:path');
(async()=>{
 const browser=await chromium.launch({headless:false,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--window-size=1100,760','--disable-session-crashed-bubble']});
 const context=await browser.newContext({viewport:{width:1080,height:650},deviceScaleFactor:1});
 const page=await context.newPage();await page.goto('http://127.0.0.1:3000');let busy=false,result=null;
 const server=http.createServer(async(req,res)=>{
  res.setHeader('content-type','application/json');
  try{
   if(req.url==='/status'){
    const identity=await context.request.get('http://127.0.0.1:3000/api/v1/me');
    res.end(JSON.stringify({authenticated:identity.status()===200,busy,result:result?{status:result.status,chapters:result.chapters}:null}));
   }else if(req.url==='/capture'&&req.method==='POST'&&!busy&&req.headers['content-type']==='application/json'){
    busy=true;res.end(JSON.stringify({started:true}));
    try{result=await require('./capture-live.cjs')({loginContext:context});}catch(e){result={status:'FAIL'};console.error('Live capture stopped:',e.message.split('Call log:')[0]);}finally{busy=false;}
   }else{res.statusCode=404;res.end(JSON.stringify({error:'Unknown operation or busy'}));}
  }catch{res.statusCode=500;res.end(JSON.stringify({error:'Sign-in browser unavailable'}));}
 });
 server.listen(9130,'127.0.0.1',()=>console.log('Full v2 sign-in browser ready at 1080x650; recording has not started.'));
})().catch(e=>{console.error(e.message);process.exitCode=1;});
