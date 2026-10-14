# GitHub Manager · full Cedar demo validation

Date: October 13, 2026. **PASS — recording, media, playback and preservation checks.**

The user selected Option D (Cedar, calmer delivery), authenticated the real account, and authorized unmasked real-account footage. The full demo is available at [the local player](http://127.0.0.1:8123).

## Deliverables

- Video: `demo/full-v2/github-manager-full-cedar-calm-1080p.mp4` — 24:12, 1920×1080, 25fps, H.264/AAC.
- Separate narration, 32 embedded chapters, English WebVTT/SRT and embedded captions, transcript, poster and chapter player.
- 117 recorded feature assertions; 128 narration paragraphs; 390 caption cues. Sources: `demo/tools/full-v2/`.

## Evidence and boundaries

The opening contains a fresh sync of the signed-in account’s 310 repositories. The remaining workflows use a labeled copy of that account’s real SQLite workspace. No synthetic inventory or deterministic fixture AI is introduced. Original OAuth sign-in occurs outside capture. Copy-session restoration after sign-out/restart is labeled and is not presented as another OAuth verification.

Fresh taxonomy and classification use only the allowlisted public repositories `allegro/ralph` and `acassen/keepalived`, with public metadata revalidated against GitHub before input extraction and checked again before provider invocation. Private input is denied. One taxonomy generation and one single-repository classification used four OpenAI HTTP requests including token counting, with automatic retries disabled. Accepted model suggestions and local canonical/alias matches are distinguished in the recording.

The initial broader launch was rejected by automatic approval review for possible private-data export. It did not execute. A public-only allowlist and export check resolved the concern before the revised launch was approved.

The actual automatic scheduler waited at least the configured 90-second quiet interval after the new Project event, then reconciled real previously analyzed repositories locally. Existing copy-only edit events were acknowledged as the test baseline before generating the two new Project events. No fixture AI or accelerated scheduler clock was used. Idle/long setup is shortened by disclosed discrete cuts; pointer footage and speech are never slowed globally.

All destructive resets, allowance renewal/overrides, manual edits and process-restart checks operated on the copied workspace. Its snapshot was restored for the closing history/readiness chapters. The original account’s concepts, memberships, suggestions, rules, rejections, drafts and compact analysis records are unchanged.

## Audio and synchronization

Cedar voice, speed 0.93, consistent warm and deliberate directions. Measured spoken rate: **132.4 words/minute** before added reading holds. Final AAC: **-16.2 LUFS**, **-1.93 dBTP**. No music or speech time stretching.

Whisper word timestamps establish paragraph boundaries and caption times. Each paragraph maps to its actual UI action/result clip. Native drag events and saved memberships were checked. Result holds provide reading time. This verifies paragraph/scene synchronization; it does not claim that every individual control click falls on an exact spoken word. Automated playback is muted and establishes technical playback only. The user’s Option D audition choice supplies voice preference; final full-length listening remains a subjective review.

All 12 Cedar takes pass the source-level consistency check: 2.17 LU loudness spread. Numeric, hyphen and compound differences were normalized for alignment. One short sentence was retaken to remove the ASR ambiguity between ‘on weighted’ and ‘unweighted’; the retake has 100% word agreement and uses the same voice/pace. Its two requests are included in the 19-request total. The standalone paragraph synchronization audit is `demo/full-v2/synchronization-qa.json`.

## Playback and preservation

All 32 chapter seeks, 1080p decode, English caption loading, fullscreen, responsive 1440px/390px player layouts, and HTTP 206 byte ranges passed. The phone product chapter uses an actual 390×844 viewport centered in the 1080p frame. 0 product JavaScript page errors were recorded.

42 earlier media/player artifacts are byte-identical. The original demo-guide prefix is preserved, with a new appended full-demo entry. All 163 protected readiness files and the original 34 benchmark call rows / 29 cache rows passed the established preservation verifier. The original app ledger’s calls, cache, HTTP history and allowance controls/audit are unchanged.

## API and spending accounting

15 new media requests + 4 intelligence HTTP requests = **19/20** new OpenAI HTTP attempts. Media conservative accounting: **$1.580000 / $2.50**. Combined accounting including the prior voice pilot and original app: **$2.213029 / $5**.

Binary TTS responses do not return invoice token usage; media reservations are conservative accounting, not invoiced charges. The complete audit is `demo/full-v2/speech-requests.json`. No original allowance was renewed or original budget history rewritten.

## Chapter and feature evidence

| Time | Chapter | Recorded assertions |
|---|---|---|
| 00:00 | 01 · Welcome and GitHub sign-in | 3 |
| 00:43 | 02 · Sync inventory and understand access | 5 |
| 01:31 | 03 · Search, filters, pagination and KPIs | 4 |
| 02:14 | 04 · Latest Work and private evidence | 4 |
| 02:57 | 05 · Inspect real repository evidence | 4 |
| 03:44 | 06 · Choose a taxonomy cohort and preview | 3 |
| 04:28 | 07 · Review, save and publish taxonomy | 4 |
| 05:14 | 08 · Classify and review individual suggestions | 4 |
| 05:59 | 09 · Grouped and selected review | 5 |
| 06:44 | 10 · Durable analysis and offline reconciliation | 4 |
| 07:30 | 11 · Explicit taxonomy and classification re-analysis | 3 |
| 08:16 | 12 · Browse all taxonomy facets | 3 |
| 09:00 | 13 · Drag one or several repositories | 4 |
| 09:48 | 14 · Bulk edits and accessible alternatives | 3 |
| 10:34 | 15 · Create and edit canonical content | 4 |
| 11:19 | 16 · Merge and archive with dependencies | 3 |
| 11:59 | 17 · Repair taxonomy conflicts before publication | 4 |
| 12:47 | 18 · Rules and both reorganization modes | 6 |
| 13:29 | 19 · Fixed allowance and selective overrides | 4 |
| 14:15 | 20 · Adaptive budgets and saved run defaults | 3 |
| 14:58 | 21 · Configure and verify automatic organization | 3 |
| 15:42 | 22 · Choose your zen logo and motion | 4 |
| 16:29 | 23 · Phone navigation and keyboard use | 4 |
| 17:10 | 24 · Reload, sign-out and backend restart | 4 |
| 17:58 | 25 · Rediscovery remains a reviewed proposal | 3 |
| 18:50 | 26 · Reset preview and exact confirmation | 3 |
| 19:35 | 27 · AI-only reset and preserved decisions | 4 |
| 20:21 | 28 · Partial Domain reset | 3 |
| 21:04 | 29 · Full taxonomy reset and rebuild | 4 |
| 21:54 | 30 · Run history, exclusions and honest outcomes | 4 |
| 22:39 | 31 · Readiness evidence and boundaries | 3 |
| 23:26 | 32 · The everyday workflow | 1 |

## Historical check mapping

All 35 earlier checks are mapped in `demo/full-v2/historical-coverage.json`. Earlier PASS values are historical evidence, not relabeled fresh results. Synthetic sample loading/activity were replaced or omitted following the real-account instruction. Fresh classification is intentionally one public repository. Post-reset rebuild is manual; optional cached restart is previewed with prior-analysis protection. Distributed/cloud runtime, exhaustive GitHub completeness, broad model-quality evaluation, and live interrupted-provider billing recovery are outside this recording. Prior readiness and regression reports remain the evidence for those separately tested capabilities.

## Reproduce and review

Serve the packaged player with `backend/.venv/bin/python demo/tools/full-v2/serve.py`. The recording server is temporary, loopback-only, and stopped after capture. Its SQLite copy, raw footage and intermediate audio stay in ignored local storage. Do not replace the original working databases to reproduce a reset scene.

Speech behavior/timing references: [OpenAI speech generation](https://developers.openai.com/api/docs/guides/text-to-speech) and [speech-to-text word timestamps](https://developers.openai.com/api/docs/guides/speech-to-text).
