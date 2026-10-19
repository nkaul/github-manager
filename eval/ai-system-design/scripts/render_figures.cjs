/* Render exact SVG labels with the existing local Playwright installation. No network. */
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const root = path.resolve(__dirname, '../../..');
const { chromium } = require(path.join(root, 'frontend/node_modules/@playwright/test'));

(async () => {
  const dir = path.join(root, 'eval/ai-system-design/figures');
  const browser = await chromium.launch({headless: true});
  try {
    const page = await browser.newPage({viewport: {width: 1800, height: 1080}, deviceScaleFactor: 2});
    await page.route('http://**/*', route => route.abort());
    await page.route('https://**/*', route => route.abort());
    const audit = [];
    for (const name of fs.readdirSync(dir).filter(n => n.endsWith('.svg')).sort()) {
      await page.goto(pathToFileURL(path.join(dir, name)).href);
      await page.evaluate(() => document.fonts.ready);
      const failures = await page.evaluate(() => {
        const errors = [];
        for (const group of document.querySelectorAll('[data-card]')) {
          const rect = group.querySelector('rect').getBBox();
          for (const text of group.querySelectorAll('text')) {
            const b = text.getBBox();
            if (b.x < rect.x + 10 || b.x + b.width > rect.x + rect.width - 10 || b.y < rect.y + 4 || b.y + b.height > rect.y + rect.height - 8)
              errors.push({card: group.getAttribute('data-card'), text: text.textContent, box: [b.x, b.y, b.width, b.height]});
          }
        }
        for (const text of document.querySelectorAll('text')) {
          const b = text.getBBox();
          if (b.x < 0 || b.y < 0 || b.x + b.width > 1800 || b.y + b.height > 1080)
            errors.push({outsideCanvas: text.textContent});
        }
        return errors;
      });
      audit.push({figure: name, failures});
      if (failures.length) throw new Error(JSON.stringify(audit));
      await page.screenshot({path: path.join(dir, name.replace('.svg', '.png')), animations: 'disabled'});
    }
    fs.writeFileSync(path.join(dir, 'layout-audit.json'), JSON.stringify({status: 'PASS', viewport: [1800,1080], png: [3600,2160], network: 'blocked', figures: audit}, null, 2) + '\n');
    console.log(JSON.stringify({status: 'PASS', figures: audit.length, png: [3600,2160]}));
  } finally { await browser.close(); }
})().catch(error => { console.error(error.message); process.exitCode = 1; });
