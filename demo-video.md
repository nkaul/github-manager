# GitHub Manager — video and audio walkthrough

Created October 12, 2026. **Completed recording: 14:41, 26 chapters, 1920×1080 at 25 fps, H.264 video with AAC narration.** All 35 recorded workflow checks passed. This is actual browser footage of the local application, with a visible pointer and action highlights. The narration is a synthetic Samantha voice generated locally, with no paid speech service.

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
| 01 | 00:00 | Start here: the workflow | REAL APP · authenticated GitHub session |
| 02 | 00:31 | Sync your real GitHub inventory | LIVE GITHUB · read-only inventory |
| 03 | 01:03 | Explore, search and filter | LIVE GITHUB · private names masked |
| 04 | 01:37 | Latest Work and honest coverage | LIVE GITHUB · bounded contribution observation |
| 05 | 02:09 | Switch to an isolated test workspace | ISOLATED APP · explicit test identity |
| 06 | 02:47 | Load public and synthetic samples | APP SAMPLES · public FastAPI + synthetic Orion |
| 07 | 03:18 | Inspect reusable evidence | LOCAL EXTRACTION · zero model calls |
| 08 | 03:53 | Discover taxonomy using validated cache | CACHED REAL AI · REPLAY provenance |
| 09 | 04:26 | Review and save the draft | HUMAN REVIEW · unpublished proposal |
| 10 | 04:58 | Approve and publish taxonomy | HUMAN APPROVAL · atomic taxonomy revision |
| 11 | 05:31 | Run real AI classification once | LIVE OPENAI · approved public/synthetic inputs |
| 12 | 06:06 | Accept and reject suggestions | HUMAN DECISIONS · protected USER mappings |
| 13 | 06:40 | Bulk assignment and multiple memberships | MANUAL ORGANIZATION · zero model calls |
| 14 | 07:14 | Create domains and projects | CONTENT MANAGEMENT · canonical registry |
| 15 | 07:46 | Rename, aliases and duplicate validation | CONTENT MANAGEMENT · stable IDs and validation |
| 16 | 08:18 | Merge and archive safely | CONTENT MANAGEMENT · dependency handling |
| 17 | 08:53 | Preview and approve a rule | LOCAL RULES · zero model calls |
| 18 | 09:22 | Incremental and full reorganization | RULES ONLY · persisted runs, no paid inference |
| 19 | 09:58 | Rediscovery remains a proposal | CACHED REAL AI · no automatic publication |
| 20 | 10:31 | Automatic organization and real debounce | REAL SCHEDULER · explicitly labeled fixture AI |
| 21 | 11:08 | Reload, logout and backend restart | PERSISTENCE TEST · isolated database retained |
| 22 | 11:42 | Labeled sample activity | SYNTHETIC ACTIVITY · fixture, not live evidence |
| 23 | 12:12 | AI-only reset and cached restart | SAFE RESET · isolated samples only |
| 24 | 12:51 | Partial taxonomy reset | SAFE RESET · domain dependencies |
| 25 | 13:24 | Full taxonomy reset and rebuild | SAFE RESET · new epoch, cached draft |
| 26 | 14:00 | What passed and what comes next | VALIDATION SUMMARY · local MVP scope |

## What was actually tested

- PASS — Authenticated real product UI opened at 1920x1080
- PASS — Real GitHub sync completed
- PASS — Live accessible private repository remains AI-blocked
- PASS — Real inventory pagination load-more
- PASS — Real explorer navigation and filters
- PASS — Real Latest Work window controls and disclosed coverage
- PASS — Isolated fixture sign-in, sync and private evidence exclusion
- PASS — Three samples isolated from ownership and Favorites
- PASS — Extract evidence
- PASS — Versioned evidence profile and source sections visible
- PASS — Discover taxonomy
- PASS — Draft edits saved without publication
- PASS — Reviewed taxonomy atomically published
- PASS — Full classification
- PASS — Fresh real three-repository classification
- PASS — Accept creates USER mapping; reject records protection
- PASS — Bulk and native drag/drop add memberships; removing one preserves another
- PASS — Domain and parented project creation
- PASS — Rename preserves ID; domain edit works; duplicate alias rejected
- PASS — Merge retains target; domain archive reparents surviving project
- PASS — Rule preview and explicit approval
- PASS — Reorganize incremental
- PASS — Full classification
- PASS — Rules-only incremental and full runs preserve manual organization
- PASS — Rediscover taxonomy
- PASS — Rediscovery is proposal-only; rejected draft leaves active taxonomy unchanged
- PASS — Real 90-second automatic scheduler completed with labeled fixture AI
- PASS — Reload, logout/relogin and backend restart preserve application state
- PASS — Synthetic activity remains visibly labeled with window controls
- PASS — Reset requires exact DELETE
- PASS — AI-only verified reset preserves USER/rejections/Core; cached restart creates draft
- PASS — Domain-only reset reparents surviving projects to Unassigned
- PASS — Discover taxonomy
- PASS — Full reset advances epoch, retains Core and rebuilds with new IDs
- PASS — Recording completed within unchanged request and spending caps

The real account sync observed **310 repositories**. Accessible private details were checked for AI exclusion, and the live explorer exercised filtering and pagination. Activity windows were checked against the actual upstream observation; the following source statuses describe the observed scope, not a promise of exhaustive access.

| Live source | Observed status |
|---|---|
| CONTRIBUTOR | OBSERVED |
| DIRECT | OBSERVED |
| ORG_GENERAL | OBSERVED |
| ORG_MEMBERSHIP | OBSERVED |
| OWNER | OBSERVED |
| STAR | OBSERVED |
| TEAM | OBSERVED |
| TEAM_MEMBERSHIP | OBSERVED |
| WATCH | OBSERVED |

Live activity statuses: OBSERVED. The account's activity can be empty or bounded/partial; separately labeled synthetic activity is shown later.

Supplemental read-only exact-name lookups were performed after recording using global filtering, rather than assuming the first inventory page contained every fixture. These checks are separate from the recorded UI assertions and do not disclose owner names:

| Expected fixture name | Exact matches | Private matches | Query complete |
|---|---|---|---|
| avimla | 1 | 1 | True |
| workshops | 1 | 1 | True |

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

The recording began its isolated AI workflow at **14/20 HTTP requests** and ended at **20/20**: **6 new HTTP requests**, including token counts. Estimated cumulative spending is **$0.060911/$5**, with **$0.000000 outstanding reservation**. The earlier snapshot was 8/20; the ledger had reached 14/20 before this final recording began.

Remaining HTTP requests: **0**. Manual organization, extraction, rules and matching cached taxonomy remain usable. Rehearsing does not require rerunning fresh inference. A cache miss is explicit. Additional fresh calls require a separately approved allowance change; reset/restart cannot replenish it.

## Remaining limits

This walkthrough covers the complete bounded local feature set. Cloud deployment/runtime integration, distributed workers, production-scale claims and exhaustive GitHub/team/watch/SSO/activity coverage remain deferred. The automatic-run provider in the video is explicitly a fixture; broad AI quality/confidence guarantees are not inferred from the small real sample check. Private model inputs remain unauthorized, and unknown branch counts are displayed honestly.

No upload, publication or submission was performed. The generated video and audio are local files under demo and ignored by Git; the guide, captions, chapter data, validation summaries and recording scripts remain reviewable. Do not publish the raw/work directories or private application diagnostics.

For exact manual instructions and recovery, see the [runbook](docs/development/phase-0-9-demo-runbook.md) and [ordered acceptance checklist](docs/development/phase-0-9-acceptance-checklist.md).

## Recording references

The capture uses [Playwright video recording](https://playwright.dev/docs/api/class-video); chapter/subtitle packaging uses [FFmpeg's media formats](https://ffmpeg.org/ffmpeg-formats.html). Recording sources are in demo/tools. Reproducing live calls remains subject to the existing allowance and input policy; the fixture rehearsal makes no paid calls.

## October 13 — new Marin/Cedar voice previews

The complete walkthrough above is retained as the historical October 12 recording. Four new **one-minute 1080p interface previews** use the current UI and AI-generated Marin/Cedar voices, with spoken action cues and captions. Open the comparison at **http://127.0.0.1:8122**, or see the [preview player](demo/voice-preview-v2/index.html) and [preview guide](demo/voice-preview-v2/README.md).

- [A — Marin, conversational](demo/voice-preview-v2/A-marin-conversational-1080p.mp4)
- [B — Cedar, conversational](demo/voice-preview-v2/B-cedar-conversational-1080p.mp4)
- [C — Marin, calm](demo/voice-preview-v2/C-marin-calm-1080p.mp4)
- [D — Cedar, calm direction](demo/voice-preview-v2/D-cedar-calm-1080p.mp4)

The player includes audio-only copies and measured pacing. See the [validation/cost report](docs/validation/demo-voice-preview-v2.md). These are isolated public/synthetic interface auditions; the full updated feature walkthrough follows the user's voice/pace selection and storyboard review. The original full video, narration and readiness evidence remain preserved.


## October 13 — complete Cedar walkthrough v2

The new full walkthrough uses **Option D: Cedar, calmer delivery** and the connected real GitHub account, unmasked as requested. **24:12 · 1920×1080 · 32 chapters · 117 recorded assertions.**

- [Watch the chaptered local player](http://127.0.0.1:8123).
- Video: [github-manager-full-cedar-calm-1080p.mp4](demo/full-v2/github-manager-full-cedar-calm-1080p.mp4).
- [Recording notes and downloads](demo/full-v2/README.md).
- [Full validation report](docs/validation/demo-full-v2.md).

The live opening refreshes the real account inventory. Demo edits, budget controls, backend restart and destructive reset scenes use an explicitly labeled copy of that account’s real workspace. Two bounded public-repository intelligence checks are fresh; saved results and local reconciliation are labeled. No synthetic inventory or fixture AI is introduced. Captions follow spoken word timestamps; normal-speed actions use reading holds and disclosed discrete cuts. Earlier walkthroughs, voice pilots and readiness reports are preserved.


## October 13 — public GitHub Pages demo

The complete Cedar walkthrough is now available at **[GitHub Manager Demo](https://nkaul.github.io/github-manager-demo/)**. The site includes 32 shareable chapters, English captions, a readable transcript, video/audio downloads, feature navigation and recording notes.

The public demo-only repository is [nkaul/github-manager-demo](https://github.com/nkaul/github-manager-demo), cloned separately at /Users/nkaul/Documents/repos/github-manager-demo. The user approved public release of the unmasked real-account recording. Original media, this guide's earlier sections, readiness evidence and the working app remain preserved. Cloud application runtime remains deferred.

Hosted playback, all 32 chapter seeks, 1080p decoding, 390 captions, HTTP 206 ranges, downloads and desktop/phone layouts passed. See the [publication report](docs/validation/github-pages-demo-publication.md) for actual results and browser-coverage limits.
