"""Build the operator guide and a local chapter player from actual capture results."""

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "demo"
chapters = json.loads((DEMO / "chapters.json").read_text())
validation = json.loads((DEMO / "validation.json").read_text())
qa = json.loads((DEMO / "media-qa.json").read_text())


def clock(seconds):
    value = int(seconds)
    return f"{value // 60:02}:{value % 60:02}"


rows = "\n".join(f"| {c['id']} | {clock(c['start'])} | {c['title']} | {c['source']} |" for c in chapters)
checks = "\n".join(f"- PASS — {c['name']}" for c in validation["checks"])
before, after = validation["budget"]["before"], validation["budget"]["after"]
live = validation["live_github"]
source_rows = "\n".join(f"| {s['source']} | {s['status']} |" for s in live["source_statuses"])
fixture_rows = "\n".join(f"| {name} | {value['exact_name_matches']} | {value['private_matches']} | {value['query_complete']} |" for name, value in live.get("named_fixture_verification", {}).items())
guide = f"""# GitHub Manager — video and audio walkthrough

Created October 12, 2026. **Completed recording: {clock(qa['duration_seconds'])}, 26 chapters, 1920×1080 at 25 fps, H.264 video with AAC narration.** All {len(validation['checks'])} recorded workflow checks passed. This is actual browser footage of the local application, with a visible pointer and action highlights. The narration is a synthetic Samantha voice generated locally, with no paid speech service.

## Watch or listen

- [Open the chapter player](demo/index.html) — play fullscreen, use chapter buttons, enable captions and read the transcript beside the video.
- [1080p narrated video](demo/github-manager-walkthrough-1080p.mp4)
- [Audio-only narration](demo/github-manager-narration.m4a)
- [English captions](demo/github-manager-walkthrough.vtt)
- [Recorded checks](demo/validation.json) and [media verification](demo/media-qa.json)

The browser used for sign-in was larger than your physical display. The final capture ran headlessly with an independent 1920×1080 viewport; it is not a cropped desktop recording or an upscale. Scrolls in the video reveal content below the viewport. The password and authorization screen were excluded. Real repository identifiers/descriptions and the real account display are masked in the GitHub segment; sample names remain readable.

Some visible actions are slowed to give you time to follow the narration, and long idle periods are cut. Playback timing is instructional; the tests themselves used the application's normal timings. The automation chapter identifies the actual scheduler interval separately.

The MP4 works in a normal video player and contains chapter markers and an English subtitle track. The HTML player also uses the external WebVTT captions. If opening the HTML file directly prevents captions from loading, serve the folder locally:

```bash
python3 demo/tools/serve.py
```

Then open **http://127.0.0.1:8120**. This server supports chapter seeking and only serves the packaged walkthrough files. It does not start the application. The app remains at **http://127.0.0.1:3000**.

## Follow the workflow

Watch chapters 1–12 first for the everyday path: **GitHub sync → explore → sample evidence → discover draft → review/publish → classify → accept/reject**. Pause after each chapter and repeat that action in your own app.

Chapters 13–22 cover manual controls, taxonomy maintenance, rules, reorganization, automation, persistence and activity. Chapters 23–25 test reset dependencies and rebuilding; perform those tests only in Public + synthetic demo. Chapter 26 closes with the saved validation and remaining local-MVP boundaries.

Use the three areas consistently:

- **Repository explorer:** browse/filter, inspect details, select repositories and assign memberships.
- **Content settings:** create/edit/merge/archive canonical concepts and preview/approve rules.
- **AI Organization:** extract evidence, discover/review drafts, classify/review suggestions, inspect runs, configure automation and preview reset.

A draft is a proposal, publication creates the vocabulary, classification proposes memberships, and acceptance makes them your decisions. Those are separate steps. Neither taxonomy publication nor a pending suggestion automatically organizes a repository.

## Chapter timestamps

| Chapter | Start | Feature/test | Evidence source |
|---|---|---|---|
{rows}

## What was actually tested

{checks}

The real account sync observed **{live['repositories']} repositories**. Accessible private details were checked for AI exclusion, and the live explorer exercised filtering and pagination. Activity windows were checked against the actual upstream observation; the following source statuses describe the observed scope, not a promise of exhaustive access.

| Live source | Observed status |
|---|---|
{source_rows}

Live activity statuses: {', '.join(s['status'] for s in live['activity_statuses'])}. The account's activity can be empty or bounded/partial; separately labeled synthetic activity is shown later.

Supplemental read-only exact-name lookups were performed after recording using global filtering, rather than assuming the first inventory page contained every fixture. These checks are separate from the recorded UI assertions and do not disclose owner names:

| Expected fixture name | Exact matches | Private matches | Query complete |
|---|---|---|---|
{fixture_rows}

## Provider provenance and safety boundaries

- **Chapters 1–4:** real operator-authenticated GitHub session and real application sync/explorer/activity. Authentication was completed before recording. The working account's taxonomy/mappings were not reset or edited by the recording.
- **Chapters 5–26:** disposable SQLite workspace and explicit fixture identity/inventory, with actual product UI, authorization/session/CSRF routes, domain services, jobs, persistence and reset logic. This keeps destructive tests away from your working workspace.
- **Taxonomy discovery/rediscovery:** validated cached real OpenAI output, visibly labeled REPLAY. No new paid taxonomy generation was needed.
- **Chapter 11 classification:** fresh real OpenAI/LangChain calls on the three approved public/synthetic samples. Returned model/provenance appears in saved run outcomes; cached/fixture output is not claimed as fresh inference.
- **Chapter 20 automation:** actual significant-edit threshold and actual 90-second quiet period, with explicitly labeled fixture AI. The long idle portion is removed from the final video; the scheduler itself was not accelerated. A 30-minute cooldown remains configured. This tests scheduling and protected-decision behavior without spending beyond the existing allowance.
- **Reset tests:** isolated samples only. AI-only preservation, exact DELETE, cleanup verification, domain dependencies, full-epoch reset and cached rebuild are asserted. Old classification identifiers are not blindly reused after full reset.

The original Phase 0/0.5 reports, benchmark corpus, references, algorithms and cost history remain separate. The [preservation audit](docs/validation/phase-0-9-preservation.md) and [prior regression/real-AI results](docs/validation/phase-0-9-results.md) remain available. The captured UI checks complement the earlier 111 backend and eight browser tests; they do not replace security/concurrency/failure-case coverage in those suites.

## API allowance after recording

Subsequent app update: operator-managed renewal and selective limit overrides are now available in **AI Organization → Manage API allowance**. See the [allowance guide](docs/development/ai-allowance.md). The counters below and in the video preserve the completed recording's historical window.

The recording began its isolated AI workflow at **{before['http']['used']}/20 HTTP requests** and ended at **{after['http']['used']}/20**: **{after['http']['used']-before['http']['used']} new HTTP requests**, including token counts. Estimated cumulative spending is **${after['estimated_usd']:.6f}/$5**, with **${after['reserved_usd']:.6f} outstanding reservation**. The earlier snapshot was 8/20; the ledger had reached 14/20 before this final recording began.

Remaining HTTP requests: **{after['http']['remaining']}**. Manual organization, extraction, rules and matching cached taxonomy remain usable. Rehearsing does not require rerunning fresh inference. A cache miss is explicit. Additional fresh calls require a separately approved allowance change; reset/restart cannot replenish it.

## Remaining limits

This walkthrough covers the complete bounded local feature set. Cloud deployment/runtime integration, distributed workers, production-scale claims and exhaustive GitHub/team/watch/SSO/activity coverage remain deferred. The automatic-run provider in the video is explicitly a fixture; broad AI quality/confidence guarantees are not inferred from the small real sample check. Private model inputs remain unauthorized, and unknown branch counts are displayed honestly.

No upload, publication or submission was performed. The generated video and audio are local files under demo and ignored by Git; the guide, captions, chapter data, validation summaries and recording scripts remain reviewable. Do not publish the raw/work directories or private application diagnostics.

For exact manual instructions and recovery, see the [runbook](docs/development/phase-0-9-demo-runbook.md) and [ordered acceptance checklist](docs/development/phase-0-9-acceptance-checklist.md).

## Recording references

The capture uses [Playwright video recording](https://playwright.dev/docs/api/class-video); chapter/subtitle packaging uses [FFmpeg's media formats](https://ffmpeg.org/ffmpeg-formats.html). Recording sources are in demo/tools. Reproducing live calls remains subject to the existing allowance and input policy; the fixture rehearsal makes no paid calls.
"""
(ROOT / "demo-video.md").write_text(guide)

chapter_buttons = "\n".join(f'<button data-time="{c["start"]}"><time>{clock(c["start"])}</time><span>{c["id"]}. {html.escape(c["title"])}</span></button>' for c in chapters)
transcript = "\n".join(f'<details><summary>{c["id"]}. {html.escape(c["title"])}</summary><p class="source">{html.escape(c["source"])}</p><p>{html.escape(c["narration"])}</p></details>' for c in chapters)
player = f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>GitHub Manager · narrated walkthrough</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#f4f7fa;color:#10263a;font:16px/1.55 system-ui,sans-serif}}header{{padding:28px 4vw;background:#102b3e;color:white}}header p{{color:#bcd3df;margin:5px 0}}h1{{font-size:28px;margin:0}}main{{padding:28px 4vw;max-width:1800px;margin:auto}}.layout{{display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:24px}}video{{width:100%;background:#0b1720;aspect-ratio:16/9;border-radius:10px}}.panel{{background:white;border:1px solid #dce5ec;border-radius:12px;padding:20px}}.chapters{{max-height:78vh;overflow:auto}}.chapters button{{display:flex;align-items:baseline;gap:12px;width:100%;border:0;background:white;color:#183a4a;text-align:left;padding:10px 6px;cursor:pointer;font:inherit;border-bottom:1px solid #edf1f4}}.chapters button:hover,.chapters button.active{{background:#e4f2ee}}time{{font:13px ui-monospace;flex:none;color:#54757b}}h2{{font-size:20px;margin:0 0 12px}}a{{color:#156956}}.downloads{{display:flex;flex-wrap:wrap;gap:18px;margin:15px 0}}.note{{padding:16px;background:#eaf5f1;border-radius:8px}}.source{{font-size:13px;color:#4f7175}}details{{padding:14px 0;border-bottom:1px solid #e2e9ed}}summary{{cursor:pointer;font-weight:600}}audio{{width:100%;margin:10px 0}}@media(max-width:1300px){{.layout{{grid-template-columns:1fr}}.chapters{{max-height:400px}}}}
video::cue{{font-size:18px;color:white;background:rgba(6,20,30,.82)}}
</style>
<header><h1>GitHub Manager · complete local walkthrough</h1><p>{clock(qa['duration_seconds'])} · 26 chapters · 1080p · narrated and captioned</p></header>
<main><div class="layout"><section><video id="video" controls preload="metadata" poster="poster.png"><source src="github-manager-walkthrough-1080p.mp4" type="video/mp4"><track kind="captions" src="github-manager-walkthrough.vtt" srclang="en" label="English" default></video>
<div class="downloads"><button id="fullscreen" style="background:#156956;color:white;border:0;border-radius:6px;padding:7px 14px;font:inherit;cursor:pointer">Fullscreen video</button><a href="github-manager-walkthrough-1080p.mp4" download>Download video</a><a href="github-manager-narration.m4a" download>Download audio</a><a href="github-manager-walkthrough.vtt" download>Download captions</a></div>
<p class="note">Use Fullscreen video to read the controls clearly. Start with chapters 1–12, pausing to repeat each step in your app. Use the sample collection for experiments and leave resets until last. Provider sources are labeled throughout.</p>
<div class="panel"><h2>Audio-only narration</h2><audio controls src="github-manager-narration.m4a"></audio><p class="source">Local synthetic Samantha narration. No password or authorization screen is included.</p></div></section>
<aside class="panel chapters"><h2>Jump to a chapter</h2>{chapter_buttons}</aside></div>
<section class="panel" style="margin-top:24px"><h2>Transcript and provenance</h2>{transcript}</section></main>
<script>
const video=document.getElementById('video');const buttons=[...document.querySelectorAll('[data-time]')];
document.getElementById('fullscreen').onclick=()=>video.requestFullscreen();
for(const button of buttons)button.onclick=()=>{{video.currentTime=Number(button.dataset.time);video.play();video.scrollIntoView({{behavior:'smooth',block:'center'}})}};
video.ontimeupdate=()=>{{for(let i=0;i<buttons.length;i++)buttons[i].classList.toggle('active',video.currentTime>=Number(buttons[i].dataset.time)&&(i===buttons.length-1||video.currentTime<Number(buttons[i+1].dataset.time)))}};
video.addEventListener('loadedmetadata',()=>{{const t=Number(location.hash.replace('#t=',''));if(Number.isFinite(t)&&t>0)video.currentTime=t}});
</script></html>"""
(DEMO / "index.html").write_text(player)
print(f"Created demo-video.md and demo/index.html; {len(chapters)} chapters, {len(validation['checks'])} passed checks")
