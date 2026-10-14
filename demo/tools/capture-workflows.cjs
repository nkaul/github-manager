/* Actual 1080p UI recording. No private source text, OAuth secrets or cookies are written. */
const fs = require('node:fs');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { performance } = require('node:perf_hooks');
const { expect } = require('../../frontend/node_modules/@playwright/test');
const { chromium } = require('../../frontend/node_modules/playwright');
const ROOT = path.resolve(__dirname, '../..');
const BASE = 'http://127.0.0.1:3000';
const UPSTREAM = 'http://127.0.0.1:8119';
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

module.exports = async function record({ browser, loginContext, dry = false, headlessReady = false, resume = null }) {
  let captureBrowser;
  if (!dry && !headlessReady) {
    captureBrowser = await chromium.launch({ headless: true, executablePath: path.join(ROOT, '.tools/playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-x64/chrome-headless-shell') });
    browser = captureBrowser;
    // The visible sign-in window may be smaller than the recording viewport.
    await loginContext.pages()[0]?.setViewportSize({ width: 1100, height: 720 });
  }
  const story = JSON.parse(fs.readFileSync(path.join(ROOT, 'demo/work/story-audio.json')));
  const stamp = new Date().toISOString().replace(/[:.]/g, '-');
  const out = path.join(ROOT, 'demo', dry ? 'work/rehearsal' : 'raw', stamp);
  fs.mkdirSync(out, { recursive: true });
  const database = resume?.database || path.join(ROOT, 'docs/validation/private/demo', `recording-${stamp}.sqlite3`);
  const evidence = resume ? JSON.parse(fs.readFileSync(path.join(resume.capture, 'capture.json'))) : { date: new Date().toISOString(), dry, viewport: { width: 1920, height: 1080 }, checks: [], chapters: [], notes: [] };
  if (resume) {
    evidence.chapters = evidence.chapters.filter(c => c.end && c.id < resume.start);
    const priorVideo = resume.priorVideo || fs.readdirSync(resume.capture).filter(n => /^(?:page@)?[a-f0-9]{32}\.webm$/.test(n))
      .map(n => path.join(resume.capture, n)).sort((a,b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs)[0];
    for (const chapter of evidence.chapters) if (!chapter.file) chapter.file = priorVideo;
    evidence.notes.push('Capture resumed at chapter ' + resume.start + ' after correcting a recording-only selector. Earlier paid inference was not repeated.');
    delete evidence.status; delete evidence.error;
  }
  let backend;
  let context;
  let page;
  let rawStart;
  let isolated = false;
  const pause = () => delay(dry ? 30 : 450);
  const check = (name, details = {}) => { evidence.checks.push({ name, status: 'PASS', ...details }); console.log('PASS:', name); };
  async function startBackend() {
    backend = spawn(path.join(ROOT, 'backend/.venv/bin/uvicorn'), ['recording_server:app', '--app-dir', path.join(ROOT, 'demo/tools'), '--host', '127.0.0.1', '--port', '8119', '--no-access-log'], {
      cwd: path.join(ROOT, 'backend'), env: { ...process.env, RECORDING_DATABASE: database, RECORDING_FIXTURE_AI: dry ? '1' : '0' }, stdio: ['ignore', 'ignore', 'pipe'],
    });
    backend.stderr.on('data', data => {
      const text = data.toString();
      if (/ERROR|Traceback/.test(text)) console.error('Isolated backend:', text.slice(0, 1000));
    });
    for (let i = 0; i < 100; i++) {
      if (backend.exitCode !== null) throw new Error('Isolated recording backend exited');
      try { if ((await fetch(UPSTREAM + '/health')).ok) return; } catch {}
      await delay(100);
    }
    throw new Error('Isolated recording backend did not become healthy');
  }
  async function stopBackend() {
    if (!backend || backend.exitCode !== null || backend.signalCode !== null) return;
    backend.kill('SIGTERM');
    for (let i = 0; i < 100 && backend.exitCode === null && backend.signalCode === null; i++) await delay(100);
    if (backend.exitCode === null && backend.signalCode === null) throw new Error('Owned recording backend did not stop cleanly');
  }
  async function setupContext(state, privateMask) {
    context = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1,
      storageState: state, ...(dry ? {} : { recordVideo: { dir: out, size: { width: 1920, height: 1080 } } }) });
    await context.addInitScript(({ privateMask }) => {
      const style = document.createElement('style');
      style.textContent = `#demo-coach{position:fixed;z-index:999999;right:22px;top:12px;padding:10px 18px;border-radius:9px;background:#0f213a;color:white;font:600 17px/1.4 system-ui;box-shadow:0 3px 20px #0003;pointer-events:none;max-width:780px}#demo-coach small{display:block;font:500 12px/1.4 system-ui;color:#aaccec;letter-spacing:.5px}#demo-pointer{position:fixed;z-index:9999999;width:20px;height:20px;border:3px solid #1f77ff;background:#b4d8ff66;border-radius:50%;pointer-events:none;transform:translate(-50%,-50%)}.demo-private .wm-repo-name a,.demo-private .wm-repo-name button,.demo-private .wm-description,.demo-private .wm-user,.demo-private .wm-modal-head h2,.demo-private .wm-detail-meta p,.demo-private .wm-detail-meta small{filter:blur(12px)!important}.demo-private .wm-search input{color:transparent!important;text-shadow:0 0 12px #555}`;
      const install = () => {
        document.documentElement.appendChild(style);
        if (privateMask) document.documentElement.classList.add('demo-private');
      };
      if (document.documentElement) install();
      else document.addEventListener('DOMContentLoaded', install, { once: true });
      const pointer = document.createElement('div'); pointer.id = 'demo-pointer';
      document.addEventListener('DOMContentLoaded', () => document.body.appendChild(pointer));
      document.addEventListener('mousemove', e => { pointer.style.left = e.clientX + 'px'; pointer.style.top = e.clientY + 'px'; });
      document.addEventListener('mousedown', () => { pointer.style.background = '#ffad32bb'; });
      document.addEventListener('mouseup', () => { pointer.style.background = '#b4d8ff66'; });
    }, { privateMask });
    page = await context.newPage();
    page.setDefaultTimeout(20000);
    rawStart = performance.now();
  }
  async function click(locator) {
    await locator.scrollIntoViewIfNeeded();
    if (!dry) await locator.evaluate(el => { const old = el.style.outline; el.style.outline = '3px solid #2675ed'; setTimeout(() => { el.style.outline = old; }, 1500); });
    const box = await locator.boundingBox();
    if (box) await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: dry ? 1 : 18 });
    await locator.click(); await pause();
  }
  async function fill(locator, value) { await locator.fill(value); await pause(); }
  async function select(locator, value) { await locator.selectOption(value); await pause(); }
  const button = (name, exact = true) => page.getByRole('button', { name, exact });
  async function nav(name) { await click(button(name, name !== 'AI Organization')); }
  async function close() { await click(button('Close dialog')); }
  async function samples() { await select(page.getByLabel('Workspace collection'), 'samples'); }
  async function state(collection = 'samples') {
    return page.evaluate(async c => {
      const response = await fetch('/api/v1/workspace?collection=' + c);
      if (!response.ok) throw new Error('Workspace read failed: ' + response.status);
      return response.json();
    }, collection);
  }
  async function repoList(collection, view = 'all', extras = '') {
    return page.evaluate(async ({ collection, view, extras }) => {
      const response = await fetch(`/api/v1/repos?collection=${collection}&view=${view}&limit=100${extras}`);
      if (!response.ok) throw new Error('Repository read failed: ' + response.status);
      return response.json();
    }, { collection, view, extras });
  }
  async function waitIdle(collection = 'samples', timeout = 120000) {
    const limit = Date.now() + timeout;
    let current;
    do {
      current = await state(collection);
      if (!current.organization.control.active_run && !current.organization.control.resetting) return current;
      await delay(300);
    } while (Date.now() < limit);
    throw new Error('Run did not become idle');
  }
  async function run(name, mode = null) {
    if (mode) await select(page.getByLabel('Inference mode'), mode);
    await click(button(name, !name.includes('taxonomy')));
    const current = await waitIdle();
    const latest = Object.values(current.organization.runs).sort((a, b) => b.created_at.localeCompare(a.created_at))[0];
    if (!latest || latest.status !== 'COMPLETED' || latest.failed) throw new Error(`${name} did not pass: ${latest?.status}; ${latest?.message}; failures=${latest?.failed}`);
    check(name, { kind: latest.kind, processed: latest.processed, failures: latest.failed,
      provenance: [...new Set(Object.values(latest.outcomes || {}).map(o => o.evidence))] });
    await delay(dry ? 50 : 1700);
    return current;
  }
  async function scene(id, action) {
    if (resume && id < resume.start) return;
    const chapter = story.find(c => c.id === id);
    const start = (performance.now() - rawStart) / 1000;
    await page.evaluate(c => {
      let hud = document.getElementById('demo-coach');
      if (!hud) { hud = document.createElement('div'); hud.id = 'demo-coach'; document.body.appendChild(hud); }
      hud.replaceChildren();
      const small = document.createElement('small'); small.textContent = c.source;
      const heading = document.createElement('div'); heading.textContent = `${c.id} / 26   ${c.title}`;
      hud.append(small, heading);
    }, chapter);
    const row = { ...chapter, start, cuts: [] };
    evidence.chapters.push(row);
    console.log(`CHAPTER ${id}: ${chapter.title}`);
    await action(row);
    const target = dry ? 0 : chapter.audio_seconds + 2;
    const used = (performance.now() - rawStart) / 1000 - start;
    if (used < target) await delay((target - used) * 1000);
    row.end = (performance.now() - rawStart) / 1000;
    await page.screenshot({ path: path.join(out, `chapter-${id}.png`) });
    fs.writeFileSync(path.join(out, 'capture.json'), JSON.stringify(evidence, null, 2));
  }
  async function finishContext(group) {
    const groupRows = evidence.chapters.filter(c => !c.file);
    const video = page.video();
    await context.close();
    context = null;
    if (!dry) {
      const name = path.join(out, `${group}.webm`);
      await video.saveAs(name);
      for (const row of groupRows) row.file = name;
    } else for (const row of groupRows) row.file = 'DRY';
  }
  async function createConcept(kind, name, parent, aliases = '') {
    await nav('Content settings'); await click(button('+ Create concept'));
    await select(page.getByRole('combobox', { name: /^Type/ }), kind);
    await fill(page.getByLabel('Name', { exact: true }), name);
    await fill(page.getByLabel('Description', { exact: true }), 'Walkthrough test: ' + name);
    if (aliases) await fill(page.getByLabel('Aliases', { exact: false }).first(), aliases);
    if (kind === 'PROJECT') await select(page.getByRole('combobox', { name: /^Parent domain/ }), { label: parent });
    await click(button('Save concept')); await expect(page.getByRole('dialog')).toHaveCount(0);
    const current = await state();
    return Object.values(current.organization.concepts).find(c => c.name === name && c.active);
  }
  async function conceptCard(kind, name) {
    await nav('Content settings'); await click(page.locator('.wm-tabs').getByRole('button', { name: new RegExp('^' + kind.toLowerCase() + 's') }));
    return page.locator('.wm-concept-card').filter({ has: page.getByRole('heading', { name, exact: true }) });
  }
  async function reset({ kinds = [], ai = true, cache = false, rules = false, restart = 'NONE', badConfirmation = false }) {
    await nav('AI Organization'); await click(button('Preview reset'));
    const dialog = page.getByRole('dialog');
    for (const label of ['Automatic / rule assignments', 'Pending classification suggestions', 'Unpublished taxonomy drafts', 'Detailed run history']) {
      await dialog.getByRole('checkbox', { name: label, exact: true }).setChecked(ai);
    }
    await dialog.getByRole('checkbox', { name: 'Extracted evidence cache', exact: true }).setChecked(cache);
    for (const kind of kinds) await dialog.getByRole('checkbox', { name: kind.toLowerCase() + 's', exact: true }).check();
    await dialog.getByRole('checkbox', { name: 'Organization rules', exact: true }).setChecked(rules);
    await select(page.getByRole('combobox', { name: /^After verified cleanup/ }), restart);
    await click(button('Preview impact'));
    await expect(dialog).toContainText('Server-verified impact'); await delay(dry ? 20 : 1800);
    if (badConfirmation) {
      await fill(page.getByLabel('Type exactly DELETE'), 'DELETE ');
      await expect(button('Confirm reset')).toBeDisabled(); check('Reset requires exact DELETE');
    }
    await fill(page.getByLabel('Type exactly DELETE'), 'DELETE'); await click(button('Confirm reset'));
    const current = await waitIdle();
    expect(current.organization.audit.at(-1)?.verified).toBe(true);
    await expect(page.locator('.wm-reset-card').getByText('Cleanup verified', { exact: false }).first()).toBeVisible();
    return current;
  }
  const userEdges = current => Object.fromEntries(Object.entries(current.organization.edges).map(([key, edges]) => [key, Object.fromEntries(Object.entries(edges).filter(([, e]) => e.source === 'USER'))]).filter(([, edges]) => Object.keys(edges).length));
  let primaryProject, primaryDomain, reviewProject, temporaryProject, temporaryDomain;
  let beforeBudget, afterBudget;
  try {
    if (!dry && !resume) {
      const identity = await loginContext.request.get(BASE + '/api/v1/me');
      if (identity.status() !== 200) throw new Error('Operator GitHub authentication is required');
      await setupContext(await loginContext.storageState(), true);
      await page.goto(BASE); await expect(page.getByLabel('Workspace collection')).toBeVisible();
      await scene('01', async () => check('Authenticated real product UI opened at 1920x1080'));
      await scene('02', async () => {
        const sync = button('Sync GitHub', false);
        await click(await sync.count() ? sync.first() : button('Start GitHub sync'));
        const current = await waitIdle('github');
        const latest = Object.values(current.organization.runs).sort((a, b) => b.created_at.localeCompare(a.created_at))[0];
        expect(latest.status).toBe('COMPLETED');
        evidence.liveGithub = { repositories: current.coverage.repos, source_coverage: current.source_coverage, activity_coverage: current.activity_coverage };
        const repos = await repoList('github');
        evidence.liveGithub.expected_name_matches = Object.fromEntries(['avimla', 'workshops'].map(name => [name, repos.items.filter(r => r.name.split('/').at(-1).toLowerCase() === name).length]));
        evidence.liveGithub.private_count_on_first_100 = repos.items.filter(r => r.private).length;
        check('Real GitHub sync completed', { repositories: current.coverage.repos });
        await page.locator('.wm-coverage').scrollIntoViewIfNeeded();
      });
      await scene('03', async () => {
        await nav('Favorites'); await expect(page.getByLabel('Search repositories')).toBeVisible();
        await nav('Access candidates'); await select(page.getByLabel('Visibility filter'), 'private');
        const privateRows = await repoList('github', 'all', '&visibility=private');
        if (privateRows.items.length) {
          await click(button('Details for ' + privateRows.items[0].name));
          await expect(page.getByRole('dialog')).toContainText('Private README-derived evidence is excluded');
          await close(); check('Live accessible private repository remains AI-blocked');
        }
        await select(page.getByLabel('Visibility filter'), 'public');
        const publicRows = await repoList('github', 'all', '&visibility=public');
        if (publicRows.items.length) {
          await fill(page.getByLabel('Search repositories'), publicRows.items[0].name.split('/').at(-1));
          await expect(page.locator('.wm-table tbody tr')).not.toHaveCount(0);
          await fill(page.getByLabel('Search repositories'), '');
          if (publicRows.items[0].language) { await fill(page.getByLabel('Language filter'), publicRows.items[0].language); await pause(); await fill(page.getByLabel('Language filter'), ''); }
        }
        await select(page.getByLabel('Visibility filter'), 'all');
        await nav('My Repos');
        if (await button('Load more').count()) { await click(button('Load more')); check('Real inventory pagination load-more'); }
        else evidence.notes.push('Pagination UI not applicable: no next page in the observed view; original backend pagination tests remain supporting evidence.');
        check('Real explorer navigation and filters');
      });
      await scene('04', async () => {
        await nav('Latest Work');
        for (const days of ['7', '14', '30', '90']) await select(page.getByLabel('Activity window'), days);
        await expect(page.locator('.wm-table-note')).toContainText('User-authored contribution dates');
        check('Real Latest Work window controls and disclosed coverage');
      });
      await finishContext('live-github');
    }
    isolated = true;
    try { if ((await fetch(UPSTREAM + '/health')).ok) throw new Error('Port 8119 is already occupied; will not replace another process'); } catch (error) { if (error.message.includes('occupied')) throw error; }
    await startBackend();
    await setupContext(undefined, false);
    await context.route('**/api/v1/**', async route => {
      try {
      const original = new URL(route.request().url());
      if (original.pathname === '/api/v1/auth/github/start') {
        // Handle the fixture redirect on the isolated server. Browser redirects from
        // a fulfilled route otherwise bypass interception and reach the working app.
        const start = await context.request.get(UPSTREAM + original.pathname, { maxRedirects: 0 });
        const location = start.headers().location;
        if (!location?.startsWith('/api/v1/auth/github/callback?')) throw new Error('Unexpected fixture OAuth destination');
        const callback = await context.request.get(UPSTREAM + location, { maxRedirects: 0 });
        if (callback.status() !== 303) throw new Error('Isolated fixture OAuth callback failed');
        await route.fulfill({ response: callback });
        return;
      }
      const response = await route.fetch({ url: UPSTREAM + original.pathname + original.search, maxRedirects: 0 });
      if (response.status() >= 400) console.log('Isolated HTTP:', original.pathname, response.status());
      await route.fulfill({ response });
      } catch {
        // Backend restart is an expected test. Never let Playwright's network
        // exception (which can contain Cookie headers) escape into diagnostics.
        await route.fulfill({ status: 502, json: { detail: 'Isolated backend restarting; sign in again shortly' } }).catch(() => {});
      }
    });
    await page.goto(BASE);
    if (resume) {
      await click(page.getByRole('link', { name: 'Continue with GitHub' })); await samples();
      const current = await state();
      primaryDomain = Object.values(current.organization.concepts).find(c => c.active && c.kind === 'DOMAIN' && !c.protected);
      primaryProject = Object.values(current.organization.concepts).find(c => c.active && c.kind === 'PROJECT' && /orion/i.test(c.name));
      beforeBudget = resume.beforeBudget;
    }
    await scene('05', async () => {
      await click(page.getByRole('link', { name: 'Continue with GitHub' }));
      await expect(page.getByText('Demo Test Fixture', { exact: true })).toBeVisible();
      await click(button('Start GitHub sync')); await waitIdle('github');
      await click(button('Details for fixture/private'));
      await expect(page.getByRole('dialog')).toContainText('Private README-derived evidence is excluded');
      await close(); check('Isolated fixture sign-in, sync and private evidence exclusion');
    });
    await scene('06', async () => {
      await samples(); await click(button('Load demo samples').first());
      await expect(button('Details for orion-api')).toBeVisible();
      expect((await repoList('samples')).total).toBe(3);
      await nav('My Repos'); await expect(page.locator('.wm-table tbody tr')).toHaveCount(0);
      await nav('Favorites'); await expect(page.locator('.wm-table tbody tr')).toHaveCount(0);
      await nav('Demo samples'); check('Three samples isolated from ownership and Favorites');
      beforeBudget = (await state()).budget;
      evidence.budget = { before: beforeBudget };
    });
    await scene('07', async () => {
      await click(button('AI Organizer', false)); await run('Extract evidence');
      await nav('Demo samples'); await click(button('Details for orion-api'));
      await expect(page.getByRole('dialog')).toContainText('demo-rake-tfidf-v2');
      await expect(page.locator('.wm-evidence').first()).toBeVisible(); await delay(dry ? 10 : 2500); await close();
      check('Versioned evidence profile and source sections visible');
    });
    await scene('08', async () => { await nav('AI Organization'); await run('Discover taxonomy', 'CACHE'); await expect(button('Review draft')).toBeVisible(); });
    await scene('09', async () => {
      await click(button('Review draft')); await expect(page.getByRole('dialog')).toContainText(dry ? 'Test fixture draft' : 'Reused AI result');
      const description = page.getByRole('dialog').getByLabel('Description', { exact: true }).first();
      await fill(description, (await description.inputValue()).slice(0, 240) + ' Reviewed in the walkthrough.');
      await click(button('Save draft')); await expect(page.getByRole('dialog')).toHaveCount(0);
      expect((await state()).organization.control.revision).toBe(0); check('Draft edits saved without publication');
    });
    await scene('10', async () => {
      await click(button('Review draft')); await click(button('Approve & publish taxonomy'));
      await expect(page.getByRole('dialog')).toHaveCount(0);
      const current = await state(); expect(current.organization.control.revision).toBe(1);
      primaryProject = Object.values(current.organization.concepts).find(c => c.kind === 'PROJECT' && /orion/i.test(c.name)) || Object.values(current.organization.concepts).find(c => c.kind === 'PROJECT');
      primaryDomain = Object.values(current.organization.concepts).find(c => c.kind === 'DOMAIN' && !c.protected);
      expect(primaryProject).toBeTruthy(); expect(primaryDomain).toBeTruthy();
      await nav('Content settings'); check('Reviewed taxonomy atomically published');
    });
    await scene('11', async () => {
      await nav('Demo samples'); await page.getByLabel('Select visible repositories').check();
      await click(button('AI Organizer', false));
      await expect(page.getByText('3 selected repositories', { exact: false })).toBeVisible();
      const current = await run('Full classification', 'LIVE');
      const latest = Object.values(current.organization.runs).sort((a,b) => b.created_at.localeCompare(a.created_at))[0];
      if (!dry) expect(Object.values(latest.outcomes).every(o => o.evidence === 'LIVE_PROVIDER')).toBe(true);
      expect(Object.keys(current.organization.suggestions).length).toBeGreaterThan(1);
      check(dry ? 'Fixture classification rehearsal' : 'Fresh real three-repository classification');
    });
    await scene('12', async () => {
      const projectSuggestion = page.locator('.wm-suggestion').filter({ has: page.locator('.wm-kind', { hasText: 'PROJECT' }) }).first();
      await click(projectSuggestion.getByRole('button', { name: 'Accept', exact: true }));
      await click(button('Reject').first());
      const current = await state(); expect(Object.keys(userEdges(current)).length).toBeGreaterThan(0); expect(Object.keys(current.organization.rejections).length).toBeGreaterThan(0);
      check('Accept creates USER mapping; reject records protection');
    });
    await scene('13', async () => {
      reviewProject = await createConcept('PROJECT', 'Demo Review', primaryDomain.name);
      await nav('Demo samples'); await page.getByLabel('Select orion-api', { exact: true }).check(); await page.getByLabel('Select orion-ui', { exact: true }).check();
      await select(page.getByLabel('Bulk assignment concept'), { label: 'Demo Review' }); await click(button('Add membership')); await click(button('Clear'));
      const row = page.getByRole('row').filter({ has: page.getByLabel('Select orion-ui', { exact: true }) });
      await row.dragTo(page.locator('.wm-project').filter({ hasText: primaryProject.name }).first()); await pause();
      await click(button('Details for orion-ui')); await expect(button('Remove Demo Review')).toBeVisible(); await expect(button('Remove ' + primaryProject.name)).toBeVisible();
      await click(button('Remove ' + primaryProject.name)); await expect(button('Remove Demo Review')).toBeVisible(); await expect(button('Remove ' + primaryProject.name)).toHaveCount(0); await close();
      check('Bulk and native drag/drop add memberships; removing one preserves another');
    });
    await scene('14', async () => {
      temporaryDomain = await createConcept('DOMAIN', 'Demo Operations');
      temporaryProject = await createConcept('PROJECT', 'Demo Console', temporaryDomain.name, 'demo dashboard');
      expect(temporaryProject.domain).toBe(temporaryDomain.id); check('Domain and parented project creation');
    });
    await scene('15', async () => {
      let card = await conceptCard('PROJECT', 'Demo Console'); await click(card.getByRole('button', { name: 'Edit', exact: true }));
      await fill(page.getByLabel('Name', { exact: true }), 'Demo Console Renamed');
      await fill(page.getByLabel('Aliases', { exact: false }).first(), 'demo dashboard, demo cockpit');
      await select(page.getByRole('combobox', { name: /^Parent domain/ }), { label: primaryDomain.name });
      await click(button('Save concept')); await expect(page.getByRole('dialog')).toHaveCount(0);
      let current = await state(); expect(current.organization.concepts[temporaryProject.id].name).toBe('Demo Console Renamed');
      expect(current.organization.concepts[temporaryProject.id].domain).toBe(primaryDomain.id);
      await click(button('+ Create concept')); await select(page.getByRole('combobox', { name: /^Type/ }), 'PROJECT');
      await fill(page.getByLabel('Name', { exact: true }), 'Demo Duplicate'); await fill(page.getByLabel('Aliases', { exact: false }).first(), 'demo cockpit');
      await select(page.getByRole('combobox', { name: /^Parent domain/ }), { label: primaryDomain.name }); await click(button('Save concept'));
      await expect(page.getByRole('dialog').getByRole('alert')).toBeVisible(); await close(); check('Rename preserves ID; domain edit works; duplicate alias rejected');
    });
    await scene('16', async () => {
      const source = await createConcept('PROJECT', 'Demo Console Legacy', temporaryDomain.name);
      let card = await conceptCard('PROJECT', source.name); await click(card.getByRole('button', { name: 'Merge', exact: true }));
      await select(page.getByRole('combobox', { name: /^Merge into/ }), { label: 'Demo Console Renamed' }); await click(button('Confirm merge'));
      let current = await state(); expect(current.organization.concepts[source.id].active).toBe(false); expect(current.organization.concepts[temporaryProject.id].active).toBe(true);
      const child = await createConcept('PROJECT', 'Demo Archive Survivor', temporaryDomain.name);
      card = await conceptCard('DOMAIN', temporaryDomain.name); await click(card.getByRole('button', { name: 'Archive', exact: true })); await expect(page.getByRole('dialog')).toContainText('Unassigned'); await click(button('Archive concept'));
      current = await state(); const parent = current.organization.concepts[current.organization.concepts[child.id].domain]; expect(parent.name).toBe('Unassigned');
      check('Merge retains target; domain archive reparents surviving project');
    });
    await scene('17', async () => {
      const expectedMatches = (await repoList('samples')).items.filter(r => (r.language || '').toLowerCase() === 'python').length;
      await createConcept('TAG', 'Demo Python'); await click(button('+ Create rule'));
      await fill(page.getByLabel('Rule name'), 'Demo Python repositories'); await fill(page.getByLabel('Value', { exact: true }), 'Python');
      await select(page.getByRole('combobox', { name: /^Assign concept/ }), { label: 'TAG · Demo Python' }); await click(button('Preview matches'));
      await expect(page.getByRole('dialog')).toContainText(`${expectedMatches} matching repositories`); await delay(dry ? 20 : 1700); await click(button('Approve rule'));
      check('Rule preview and explicit approval');
    });
    await scene('18', async () => {
      await nav('AI Organization'); await run('Reorganize incremental', 'RULES'); await run('Full classification', 'RULES');
      await page.locator('.wm-run').first().locator('summary').click();
      const pythonRepo = (await repoList('samples')).items.find(r => (r.language || '').toLowerCase() === 'python');
      await nav('Demo samples'); await click(button('Details for ' + pythonRepo.name)); await expect(page.getByRole('dialog')).toContainText('Demo Python'); await close();
      check('Rules-only incremental and full runs preserve manual organization');
    });
    await scene('19', async () => {
      const before = (await state()).organization.control.revision;
      await nav('AI Organization'); await run('Rediscover taxonomy', 'CACHE'); await click(button('Review draft'));
      await expect(page.getByRole('dialog')).toContainText(dry ? 'Test fixture draft' : 'Reused AI result'); await close(); await click(button('Reject draft'));
      expect((await state()).organization.control.revision).toBe(before); check('Rediscovery is proposal-only; rejected draft leaves active taxonomy unchanged');
    });
    await scene('20', async chapter => {
      if (!dry) fs.writeFileSync(database.replace(/\.sqlite3$/, '.fixture-ai'), 'Explicit fixture AI for the real scheduler test.\n');
      await click(page.getByRole('checkbox', { name: 'Automatic organization after significant edits' }));
      await expect(page.getByRole('checkbox', { name: 'Automatic organization after significant edits' })).toBeChecked();
      await createConcept('PROJECT', 'Demo Automation Alpha', primaryDomain.name);
      await createConcept('PROJECT', 'Demo Automation Beta', primaryDomain.name);
      await nav('AI Organization');
      if (!dry) {
        const from = (performance.now() - rawStart) / 1000;
        let current;
        const deadline = Date.now() + 180000;
        do { await delay(700); current = await state(); } while (!Object.values(current.organization.runs).some(r => r.reason === 'AUTO' && r.status === 'COMPLETED') && Date.now() < deadline);
        const auto = Object.values(current.organization.runs).find(r => r.reason === 'AUTO' && r.status === 'COMPLETED');
        expect(auto).toBeTruthy(); expect(auto.failed).toBe(0); expect(current.organization.control.quiet_seconds).toBe(90);
        expect(Object.values(auto.outcomes).every(o => o.evidence === 'FIXTURE')).toBe(true);
        const until = (performance.now() - rawStart) / 1000;
        if (until - from > 12) chapter.cuts.push([from + 3, until - 5]);
        check('Real 90-second automatic scheduler completed with labeled fixture AI', { elapsed_wait_seconds: Number((until - from).toFixed(2)), processed: auto.processed, provenance: 'FIXTURE' });
      } else evidence.notes.push('Dry rehearsal skips the scheduler wait; final capture must verify the real interval.');
      await click(page.getByRole('checkbox', { name: 'Automatic organization after significant edits' }));
      await expect(page.getByRole('checkbox', { name: 'Automatic organization after significant edits' })).not.toBeChecked();
      if (!dry) fs.unlinkSync(database.replace(/\.sqlite3$/, '.fixture-ai'));
      afterBudget = (await state()).budget;
      if (!dry) { expect(afterBudget.http.used - beforeBudget.http.used).toBeLessThanOrEqual(12); expect(afterBudget.estimated_usd).toBeLessThanOrEqual(5); }
    });
    await scene('21', async () => {
      const before = await state(); const beforeUser = userEdges(before); const beforeConcepts = before.organization.concepts;
      await page.reload(); await samples(); expect(userEdges(await state())).toEqual(beforeUser);
      await click(page.getByLabel('Sign out')); await expect(page.getByRole('heading', { name: 'Connect your GitHub account' })).toBeVisible();
      await click(page.getByRole('link', { name: 'Continue with GitHub' })); await samples();
      await stopBackend(); await startBackend(); await page.reload();
      await expect(page.getByRole('heading', { name: 'Connect your GitHub account' })).toBeVisible();
      await click(page.getByRole('link', { name: 'Continue with GitHub' })); await samples();
      const after = await state(); expect(userEdges(after)).toEqual(beforeUser); expect(after.organization.concepts).toEqual(beforeConcepts);
      check('Reload, logout/relogin and backend restart preserve application state');
    });
    await scene('22', async () => {
      await nav('Latest Work'); await expect(page.getByText('FIXTURE: Synthetic Orion activity', { exact: false })).toBeVisible();
      for (const days of ['7', '90', '14']) await select(page.getByLabel('Activity window'), days);
      check('Synthetic activity remains visibly labeled with window controls');
    });
    await scene('23', async () => {
      const before = await state();
      const after = await reset({ ai: true, cache: true, restart: 'DISCOVER_AND_RECONCILE', badConfirmation: true });
      expect(userEdges(after)).toEqual(userEdges(before)); expect(after.organization.rejections).toEqual(before.organization.rejections);
      expect(after.coverage.repos).toBe(3); expect(after.organization.control.revision).toBe(before.organization.control.revision);
      await expect(button('Review draft')).toBeVisible(); check('AI-only verified reset preserves USER/rejections/Core; cached restart creates draft');
    });
    await scene('24', async () => {
      const before = await state(); const after = await reset({ ai: false, kinds: ['DOMAIN'] });
      const projects = Object.values(after.organization.concepts).filter(c => c.active && c.kind === 'PROJECT'); expect(projects.length).toBeGreaterThan(0);
      expect(projects.every(p => after.organization.concepts[p.domain]?.name === 'Unassigned')).toBe(true);
      expect(after.coverage.repos).toBe(before.coverage.repos); check('Domain-only reset reparents surviving projects to Unassigned');
    });
    await scene('25', async () => {
      const before = await state(); const priorIds = Object.values(before.organization.concepts).filter(c => !c.protected).map(c => c.id);
      const after = await reset({ ai: true, cache: true, rules: true, kinds: ['DOMAIN', 'PROJECT', 'TOPIC', 'TAG'] });
      expect(after.organization.control.revision).toBe(0); expect(after.organization.control.taxonomy_epoch).toBeGreaterThan(before.organization.control.taxonomy_epoch); expect(after.coverage.repos).toBe(3);
      await run('Discover taxonomy', 'CACHE'); await click(button('Review draft')); await click(button('Approve & publish taxonomy'));
      const rebuilt = await state(); expect(Object.values(rebuilt.organization.concepts).filter(c => !c.protected && c.active).every(c => !priorIds.includes(c.id))).toBe(true);
      check('Full reset advances epoch, retains Core and rebuilds with new IDs');
    });
    await scene('26', async () => {
      await nav('AI Organization');
      const current = await state(); evidence.budget = { before: beforeBudget, after: current.budget };
      const checks = evidence.checks.length;
      await page.evaluate(({ checks, budget }) => {
        const panel = document.createElement('section');
        panel.style.cssText = 'margin:20px 0;padding:30px;border:1px solid #b8dfd3;border-radius:14px;background:#effbf6;color:#124938;font:18px/1.7 system-ui';
        const heading = document.createElement('h2'); heading.textContent = 'Walkthrough validation';
        const body = document.createElement('p'); body.textContent = `${checks} recorded assertions passed. Real GitHub observations, isolated test identity, cached taxonomy and fresh model inference are identified separately. Cloud deployment remains deferred.`;
        const cost = document.createElement('p'); cost.textContent = `OpenAI allowance: ${budget.http?.used}/20 HTTP requests. Estimated cumulative spend: $${budget.estimated_usd?.toFixed(6)} / $5. Earlier benchmarks and reports are preserved.`;
        panel.append(heading, body, cost); document.querySelector('.wm-content').prepend(panel);
      }, { checks, budget: current.budget });
      check('Recording completed within unchanged request and spending caps');
    });
    await finishContext('isolated-workflows');
    evidence.status = 'PASS';
    fs.writeFileSync(path.join(out, 'capture.json'), JSON.stringify(evidence, null, 2));
    fs.writeFileSync(path.join(ROOT, 'demo/work', dry ? 'latest-rehearsal.txt' : 'latest-capture.txt'), out);
    return { status: 'PASS', checks: evidence.checks.length, capture: out };
  } catch (error) {
    evidence.status = 'FAIL'; evidence.error = error.message;
    fs.writeFileSync(path.join(out, 'capture.json'), JSON.stringify(evidence, null, 2));
    if (page && !page.isClosed()) await page.screenshot({ path: path.join(out, 'failure.png') }).catch(() => {});
    if (context) await context.close().catch(() => {});
    throw error;
  } finally {
    if (isolated) await stopBackend();
    if (captureBrowser) await captureBrowser.close();
  }
};
