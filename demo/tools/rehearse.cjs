const { chromium } = require('../../frontend/node_modules/playwright');
const path = require('node:path');
(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: path.resolve(__dirname, '../../.tools/playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-x64/chrome-headless-shell') });
  try {
    console.log(await require('./capture-workflows.cjs')({ browser, dry: true }));
  } finally { await browser.close(); }
})().catch(error => { console.error(error.message.split('Call log:')[0]); process.exitCode = 1; });
