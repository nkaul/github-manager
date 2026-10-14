/* Authenticated inspection and subsequent capture; credentials stay in memory. */
const fs = require('node:fs');
const path = require('node:path');
const ROOT = path.resolve(__dirname, '../../..');
module.exports = async ({loginContext}) => {
  if (fs.existsSync(path.join(__dirname, 'capture-main.cjs'))) {
    for (const name of ['./capture-main.cjs','./capture-extra.cjs']) delete require.cache[require.resolve(name)];
    return require('./capture-main.cjs')({loginContext});
  }
  const me = await (await loginContext.request.get('http://127.0.0.1:3000/api/v1/me')).json();
  const state = await (await loginContext.request.get('http://127.0.0.1:3000/api/v1/workspace?collection=github')).json();
  const out = path.join(ROOT, 'docs/validation/private/demo/full-v2'); fs.mkdirSync(out,{recursive:true});
  fs.writeFileSync(path.join(out,'inspection.json'),JSON.stringify({user:me.user,state},null,2));
  const org=state.organization;
  console.log(JSON.stringify({authenticated:!!me.user,concepts:Object.values(org.concepts).map(c=>({name:c.name,kind:c.kind,status:c.status})),organization_keys:Object.keys(org),state_keys:Object.keys(state),repo_count:Object.keys(state.repos||{}).length,runs:Object.values(org.runs).slice(-4).map(r=>({kind:r.kind,status:r.status,processed:r.processed,failed:r.failed})),draft:!!org.draft,analysis:Object.keys(org.analysis||{}).length},null,2));
  return {status:'INSPECTED',chapters:0};
};
