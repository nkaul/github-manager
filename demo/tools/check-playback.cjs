// Read-only verification of the packaged media, using a fresh browser with no app session.
const { chromium } = require('../../frontend/node_modules/playwright');
const fs = require('node:fs');
const path = require('node:path');

(async () => {
  const root = path.resolve(__dirname, '../..');
  const chapters = JSON.parse(fs.readFileSync(path.join(root, 'demo/chapters.json')));
  const browser = await chromium.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true, args: ['--mute-audio'],
  });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    await page.goto('http://127.0.0.1:8120', { waitUntil: 'networkidle' });
    await page.waitForFunction(() => document.querySelector('video').readyState >= 1);
    const initial = await page.locator('video').evaluate(v => ({
      width: v.videoWidth, height: v.videoHeight, duration: v.duration,
      captionTracks: v.textTracks.length, captionCues: v.textTracks[0]?.cues?.length,
    }));
    if (initial.width !== 1920 || initial.height !== 1080 || Math.abs(initial.duration - 881.6) > 1) {
      throw new Error(`Unexpected media dimensions/duration: ${JSON.stringify(initial)}`);
    }
    if (initial.captionTracks !== 1 || initial.captionCues < 26) throw new Error('Missing captions');
    const count = await page.locator('[data-time]').count();
    if (count !== 26) throw new Error(`Expected 26 chapters, found ${count}`);
    const seeks = [];
    for (const n of [1, 9, 11, 13, 20, 23, 25, 26]) {
      const chapter = chapters[n - 1];
      await page.locator('[data-time]').nth(n - 1).click();
      await page.waitForFunction(start => {
        const v = document.querySelector('video');
        return !v.seeking && v.readyState >= 2 && !v.paused && Math.abs(v.currentTime - start) < 4;
      }, chapter.start);
      await page.waitForTimeout(1200);
      await page.locator('video').evaluate(v => v.pause());
      const actual = await page.locator('video').evaluate(v => v.currentTime);
      seeks.push({ chapter: n, expected: chapter.start, actual, pass: true });
      await page.screenshot({ path: path.join(root, `demo/work/playback-${String(n).padStart(2, '0')}.png`) });
    }
    const audio = await page.locator('audio').evaluate(a => ({
      readyState: a.readyState, duration: a.duration, error: a.error?.message || null,
    }));
    if (audio.error || !Number.isFinite(audio.duration)) throw new Error(`Audio metadata failed: ${JSON.stringify(audio)}`);
    await page.locator('audio').evaluate(a => a.play());
    await page.waitForTimeout(1200);
    audio.playback_seconds = await page.locator('audio').evaluate(a => { a.pause(); return a.currentTime; });
    if (audio.playback_seconds < 0.5) throw new Error('Audio did not advance');
    await page.locator('#fullscreen').click();
    await page.waitForFunction(() => document.fullscreenElement?.id === 'video');
    await page.screenshot({ path: path.join(root, 'demo/work/playback-fullscreen.png') });
    await page.evaluate(() => document.exitFullscreen());
    const result = {
      browser: 'Google Chrome, headless, fresh unauthenticated context',
      player_viewport: '1280x900', metadata: initial, chapter_buttons: count,
      seeks, audio, fullscreen_pass: true, pass: true,
    };
    fs.writeFileSync(path.join(root, 'demo/work/browser-playback-qa.json'), JSON.stringify(result, null, 2) + '\n');
    const qaPath = path.join(root, 'demo/media-qa.json');
    const qa = JSON.parse(fs.readFileSync(qaPath));
    qa.browser_playback_pass = true;
    qa.chapter_seek_checks = seeks.length;
    qa.caption_cues = initial.captionCues;
    qa.audio_duration_seconds = audio.duration;
    qa.fullscreen_pass = true;
    fs.writeFileSync(qaPath, JSON.stringify(qa, null, 2) + '\n');
    console.log(JSON.stringify(result, null, 2));
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error.message); process.exitCode = 1; });
