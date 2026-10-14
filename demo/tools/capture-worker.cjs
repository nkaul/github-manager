const { chromium } = require('../../frontend/node_modules/playwright');
const path = require('node:path');
const fs = require('node:fs');
process.once('message', async storageState => {
  let browser;
  try {
    browser = await chromium.launch({ headless: true, executablePath: path.resolve(__dirname, '../../.tools/playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-x64/chrome-headless-shell') });
    const loginContext = await browser.newContext({ storageState });
    const resumePath = path.resolve(__dirname, '../work/resume.json');
    const resume = fs.existsSync(resumePath) ? JSON.parse(fs.readFileSync(resumePath)) : null;
    const result = await require('./capture-workflows.cjs')({ browser, loginContext, headlessReady: true, resume });
    process.send(result);
  } catch (error) {
    process.send({ status: 'FAIL', message: error.message.split('Call log:')[0] });
  } finally {
    if (browser) await browser.close();
    process.disconnect();
  }
});
