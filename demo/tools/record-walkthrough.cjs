const fs = require('node:fs');
const path = require('node:path');
const { fork } = require('node:child_process');
module.exports = async options => {
 const verificationFlag = path.join(__dirname, '../work/verify-live-fixtures.flag');
 if (fs.existsSync(verificationFlag)) {
   const root = path.resolve(__dirname, '../..');
   const capturePath = path.join(fs.readFileSync(path.join(root, 'demo/work/latest-capture.txt'), 'utf8').trim(), 'capture.json');
   const evidence = JSON.parse(fs.readFileSync(capturePath));
   const observations = {};
   for (const name of ['avimla', 'workshops']) {
     const response = await options.loginContext.request.get('http://127.0.0.1:3000/api/v1/repos?collection=github&view=all&limit=100&q=' + encodeURIComponent(name));
     if (!response.ok()) throw new Error('Supplemental fixture lookup failed');
     const body = await response.json();
     const matches = body.items.filter(repo => repo.name.split('/').at(-1).toLowerCase() === name);
     observations[name] = { exact_name_matches: matches.length, private_matches: matches.filter(repo => repo.private).length, query_complete: !body.next_cursor };
   }
   evidence.liveGithub.named_fixture_verification = observations;
   evidence.liveGithub.expected_name_matches_scope = 'Original counts describe the first 100 inventory rows; named_fixture_verification uses separate globally filtered exact-name lookups.';
   fs.writeFileSync(capturePath, JSON.stringify(evidence, null, 2));
   fs.unlinkSync(verificationFlag);
   return { status: 'PASS', supplemental_read_only_fixture_checks: observations };
 }
 const dry = options.dry || fs.existsSync(path.join(__dirname, '../work/dry-rehearsal.flag'));
 if (!dry) {
   const state = await options.loginContext.storageState();
   await options.loginContext.pages()[0]?.setViewportSize({ width: 1100, height: 720 });
   return new Promise((resolve, reject) => {
     const worker = fork(path.join(__dirname, 'capture-worker.cjs'), [], {
       env: { ...process.env, PLAYWRIGHT_BROWSERS_PATH: path.resolve(__dirname, '../../.tools/playwright') },
       stdio: ['ignore', 'inherit', 'inherit', 'ipc'],
     });
     worker.on('message', result => result.status === 'PASS' ? resolve(result) : reject(new Error(result.message)));
     worker.on('error', reject);
     worker.on('exit', code => { if (code) reject(new Error('Headless recording worker exited')); });
     worker.send(state); // Memory-only IPC; no cookies or credentials are written to disk.
   });
 }
 const entry = path.join(__dirname, 'capture-workflows.cjs');
 delete require.cache[require.resolve(entry)];
 const capture = require(entry);
 return capture({ ...options, dry });
};
