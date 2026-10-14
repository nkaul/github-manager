/** Check the actual GIF decoding and review the output in a browser. */
import { chromium } from "../../../../frontend/node_modules/@playwright/test/index.mjs";
import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const directory = dirname(fileURLToPath(import.meta.url));
const root = resolve(directory, "../../../..");
const ffmpeg = resolve(root, ".tools/video-python/imageio_ffmpeg/binaries/ffmpeg-macos-x86_64-v7.1");
const metadata = JSON.parse(readFileSync(resolve(directory,"gif-info.json"),"utf8"));
const audit = { actualGifChecks: [], preview: {} };
for (const kind of ["orbit","rays"]) {
  const file = resolve(directory,`zen-loop-${kind}-256.gif`);
  const result = spawnSync(ffmpeg,["-hide_banner","-loglevel","error","-ignore_loop","1","-i",file,"-vsync","0","-f","rawvideo","-pix_fmt","rgba","pipe:1"],{maxBuffer:80*1024*1024});
  if (result.status !== 0) throw new Error(result.stderr.toString());
  const frameBytes = 256*256*4;
  if (result.stdout.length % frameBytes) throw new Error("Truncated decoded GIF");
  const count = result.stdout.length/frameBytes;
  const expected = metadata.variants.find(v => v.kind === kind && v.dimensions[0] === 256);
  if (count !== expected.frames) throw new Error("Decoded frame count mismatch");
  const unique = new Set();
  let clearBorders = true;
  const changes = [];
  for (let i=0;i<count;i++) {
    const frame = result.stdout.subarray(i*frameBytes,(i+1)*frameBytes);
    unique.add(createHash("sha256").update(frame).digest("hex"));
    for (let p=0;p<256;p++) {
      if (frame[(p*256)*4+3] || frame[(p*256+255)*4+3] || frame[p*4+3] || frame[((255*256)+p)*4+3]) clearBorders=false;
    }
    const previous = result.stdout.subarray(((i+count-1)%count)*frameBytes,((i+count-1)%count+1)*frameBytes);
    let pixels=0;
    for (let p=0;p<frameBytes;p+=4) {
      if (frame[p]!==previous[p] || frame[p+1]!==previous[p+1] || frame[p+2]!==previous[p+2] || frame[p+3]!==previous[p+3]) pixels++;
    }
    changes.push(pixels);
  }
  console.log(JSON.stringify({kind,count,distinctFrames:unique.size,clearBorders}));
  if (!clearBorders || unique.size < (kind === "orbit" ? 90 : 25)) throw new Error("Clipped frames or insufficient motion");
  if (kind === "orbit" && changes.some(n => n === 0)) throw new Error("Aura animation contains an unintended pause");
  const info = {kind, decodedFrames:count, distinctFrames:unique.size, transparentUnclippedBorders:clearBorders, seamChangedPixels:changes[0], smallestFrameChange:Math.min(...changes), largestFrameChange:Math.max(...changes)};
  audit.actualGifChecks.push(info);
}

const browser = await chromium.launch({ headless:true });
try {
  const page = await browser.newPage({viewport:{width:1600,height:1000}});
  const errors=[];
  page.on("pageerror",e=>errors.push(e.message));
  const response = await page.goto("http://127.0.0.1:8121/animated/");
  await page.evaluate(()=>Promise.all([...document.images].map(img=>img.decode())));
  if (response.status()!==200) throw new Error("Review page unavailable");
  for (const card of await page.locator("article").all()) {
    await card.getByRole("button").click();
    if (await card.getByRole("button").textContent()!=="Play animation") throw new Error("Pause failed");
    if (!(await card.locator(".stage img").getAttribute("src")).endsWith("-poster.png")) throw new Error("Pause did not show static poster");
  }
  // Still review capture uses the intentionally paused posters; the page opens playing.
  await page.screenshot({path:resolve(directory,"animation-review.png"),fullPage:true});
  for (const card of await page.locator("article").all()) {
    await card.getByRole("button").click();
    if (!(await card.locator(".stage img").getAttribute("src")).endsWith(".gif")) throw new Error("Resume failed");
  }
  const desktop = await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,brokenImages:[...document.images].filter(img=>!img.naturalWidth).length}));
  await page.setViewportSize({width:390,height:844});
  const mobile = await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth}));
  if (desktop.brokenImages || desktop.scrollWidth>desktop.width || mobile.scrollWidth>mobile.width || errors.length) throw new Error(JSON.stringify({desktop,mobile,errors}));
  audit.preview = {status:response.status(),desktop,mobile,errors,pauseResumeControls:2};
} finally {await browser.close();}
writeFileSync(resolve(directory,"animation-qa.json"),JSON.stringify(audit,null,2));
console.log(JSON.stringify(audit));
