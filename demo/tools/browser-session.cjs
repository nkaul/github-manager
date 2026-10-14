// Opens an ephemeral browser for operator sign-in. Credentials are never recorded or saved.
const { chromium } = require('../../frontend/node_modules/playwright');
const http = require('node:http');
const path = require('node:path');

(async () => {
  const browser = await chromium.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: false,
    args: ['--window-size=1920,1080', '--disable-session-crashed-bubble'],
  });
  const context = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  await page.goto('http://127.0.0.1:3000');
  let busy = false;
  let result = null;
  const server = http.createServer(async (request, response) => {
    response.setHeader('content-type', 'application/json');
    try {
      if (request.url === '/status') {
        const identity = await context.request.get('http://127.0.0.1:3000/api/v1/me');
        response.end(JSON.stringify({ authenticated: identity.status() === 200, recording: busy, result }));
      } else if (['/record', '/rehearse'].includes(request.url) && request.method === 'POST' && !busy) {
        busy = true;
        response.end(JSON.stringify({ started: true }));
        try {
          const modulePath = path.join(__dirname, 'record-walkthrough.cjs');
          delete require.cache[require.resolve(modulePath)];
          const record = require(modulePath);
          result = await record({ browser, loginContext: context, dry: request.url === '/rehearse' });
        } catch (error) {
          result = { status: 'FAIL', message: error.message };
          console.error('Recording stopped:', error.message.split('Call log:')[0]);
        } finally {
          busy = false;
        }
      } else if (request.url === '/close' && request.method === 'POST' && !busy) {
        response.end(JSON.stringify({ closed: true }));
        await browser.close();
        server.close();
      } else {
        response.statusCode = 404;
        response.end(JSON.stringify({ error: 'Unknown operation or recording is active' }));
      }
    } catch (error) {
      response.statusCode = 500;
      response.end(JSON.stringify({ error: error.message }));
    }
  });
  server.listen(9129, '127.0.0.1', () => console.log('Sign-in browser ready. Recording has not started.'));
})().catch(error => { console.error(error.message); process.exitCode = 1; });
