/** Render native SVG frames locally, then encode real infinitely looping GIF files. */
import { chromium } from "../../../../frontend/node_modules/@playwright/test/index.mjs";
import { mkdirSync, writeFileSync, readFileSync, statSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { spawnSync } from "node:child_process";

const directory = dirname(fileURLToPath(import.meta.url));
const root = resolve(directory, "../../../..");
const scratch = resolve(root, ".tools/logo-animation-20261013");
const ffmpeg = resolve(root, ".tools/video-python/imageio_ffmpeg/binaries/ffmpeg-macos-x86_64-v7.1");
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
await page.goto(pathToFileURL(resolve(directory, "render.html")).href);
await page.waitForFunction(() => typeof window.renderLogo === "function");
const report = { fps: 25, infiniteLoop: true, background: "transparent", variants: [] };

function run(args) {
  const result = spawnSync(ffmpeg, ["-hide_banner", "-loglevel", "error", "-y", ...args], { encoding: "utf8", maxBuffer: 8*1024*1024 });
  if (result.status !== 0) throw new Error(result.stderr || "GIF encoder failed");
}

function inspectGif(path) {
  const b = readFileSync(path);
  if (b.toString("ascii",0,6) !== "GIF89a") throw new Error("Not an animated GIF89a file");
  const dimensions = [b.readUInt16LE(6),b.readUInt16LE(8)];
  let offset = 13 + ((b[10]&128) ? 3*(2**((b[10]&7)+1)) : 0);
  let frames = 0, centiseconds = 0, transparent = false, loop = null;
  const disposals = new Set();
  function blocks() {
    const parts = [];
    while (b[offset]) { const n = b[offset++]; parts.push(b.subarray(offset,offset+n)); offset += n; }
    offset++;
    return Buffer.concat(parts);
  }
  while (offset < b.length) {
    const marker = b[offset++];
    if (marker === 0x3b) break;
    if (marker === 0x21) {
      const label = b[offset++];
      if (label === 0xf9) {
        const length = b[offset++];
        transparent ||= !!(b[offset]&1);
        disposals.add((b[offset] >> 2)&7);
        centiseconds += b.readUInt16LE(offset+1);
        offset += length+1;
      } else if (label === 0xff) {
        const n = b[offset++], app = b.toString("ascii",offset,offset+n); offset += n;
        const data = blocks();
        if (app === "NETSCAPE2.0" && data[0] === 1) loop = data.readUInt16LE(1);
      } else blocks();
    } else if (marker === 0x2c) {
      const packed = b[offset+8]; offset += 9;
      if (packed&128) offset += 3*(2**((packed&7)+1));
      offset++; blocks(); frames++;
    } else throw new Error(`Unexpected GIF block ${marker}`);
  }
  if (!frames || loop !== 0 || !transparent) throw new Error("Missing animation, infinite loop or transparency");
  return { dimensions, frames, seconds: centiseconds/100, loop, transparent, disposals: [...disposals], bytes: statSync(path).size };
}

try {
  for (const [kind, seconds] of [["orbit",4],["rays",6]]) {
    const frames = resolve(scratch,kind);
    mkdirSync(frames,{ recursive: true });
    for (let i = 0; i < seconds*25; i++) {
      const frame = await page.evaluate(async ({kind,time}) => window.renderLogo(kind,time),{kind,time:i/25});
      writeFileSync(resolve(frames,`frame-${String(i).padStart(4,"0")}.png`),Buffer.from(frame.png,"base64"));
    }
    const poster = await page.evaluate(async ({kind,time}) => window.renderLogo(kind,time),{kind,time:kind === "orbit" ? 0 : 2});
    writeFileSync(resolve(directory,`zen-loop-${kind}-poster.png`),Buffer.from(poster.png,"base64"));
    writeFileSync(resolve(directory,`zen-loop-${kind}-poster.svg`),poster.svg);
    for (const size of [256,512]) {
      const name = `zen-loop-${kind}-${size}.gif`;
      const output = resolve(directory,name);
      run(["-framerate","25","-i",resolve(frames,"frame-%04d.png"),"-filter_complex",`[0:v]scale=${size}:${size}:flags=lanczos,split[a][b];[a]palettegen=max_colors=256:reserve_transparent=1:stats_mode=full[p];[b][p]paletteuse=dither=sierra2_4a:alpha_threshold=128`,"-loop","0",output]);
      const metadata = inspectGif(output);
      if (metadata.frames !== seconds*25 || metadata.seconds !== seconds) throw new Error("Incorrect GIF frame timing");
      report.variants.push({kind,file:name,...metadata});
    }
    console.log(`${kind}: rendered ${seconds*25} vector frames; 256px and 512px GIFs encoded.`);
  }
  writeFileSync(resolve(directory,"gif-info.json"),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report));
} finally { await browser.close(); }
