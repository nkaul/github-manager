# GitHub Manager Demo — publication report

Date: October 13, 2026 (America/New_York).

**PASS — public deployment, hosted playback and media preservation verified.**

## Published destination

- Site: [GitHub Manager Demo](https://nkaul.github.io/github-manager-demo/)
- Repository: [nkaul/github-manager-demo](https://github.com/nkaul/github-manager-demo), public.
- Publishing source: main → repository root, with .nojekyll and HTTPS enforced.
- Tested content commit: 2217dbccf83815447ece9f1976b8e2a9c90f2b6f.
- Successful content deployment: [Pages run 38495001866](https://github.com/nkaul/github-manager-demo/actions/runs/38495001866).

The final follow-up commit records these results in this report and verification.json; it does not change the player, branding, captions or media that passed browser validation.

## Public deliverables

The site contains the 24:12 Cedar · calmer delivery walkthrough at 1920×1080, 32 shareable chapters, chapter search, English captions, a readable/downloadable transcript, standalone narration, media downloads, feature links and recording notes. Narration is clearly identified as AI-generated.

The site is a static recorded showcase. GitHub Manager’s live application and cloud runtime are not deployed here. Application credentials, SQLite databases, raw footage, private validation reports and provider ledgers were not copied into this repository.

## Fresh hosted checks

| Check | Result |
|---|---|
| Signed-out public HTTPS page and correct project subpath | PASS |
| All 18 intended public files return HTTP 200 | PASS |
| Video decodes at 1920×1080; duration 1451.64 seconds | PASS |
| Every one of the 32 chapter seeks and corresponding URL hashes | PASS |
| Direct chapter link when metadata loads before chapter data | PASS |
| Feature links scroll to the player and seek to their chapter | PASS |
| Chapter search and no-results feedback | PASS |
| English caption track loads all 390 cues | PASS |
| Fullscreen and keyboard chapter selection | PASS |
| Standalone audio playback and mutual video/audio pausing | PASS |
| Video range request returns HTTP 206 and exactly 1,024 requested bytes | PASS |
| Video content type video/mp4; linked downloads resolve | PASS |
| 1440×1000 desktop and 390×844 phone layout without horizontal overflow | PASS |
| Logo motion preference persists; reduced-motion preference uses static art | PASS |
| Excluded credentials, Git internals, backend source and provider audit paths return 404 | PASS |
| All 32 transcript sections and links | PASS |
| Browser page errors | 0 |
| Six downloaded recording assets match approved SHA-256 values | PASS |

Technical browser checks use installed Chromium and muted playback. Safari/WebKit was not installed and was not tested. Responsive viewport checks do not establish physical iPhone/Safari playback, and automated checks do not grade subjective voice quality.

## Recording evidence and boundaries

The 117 recorded feature assertions are existing local validation evidence, not 117 newly repeated production tests. The opening uses the real connected account and a live GitHub sync. Edits, allowance overrides, restart and reset use a labeled copy of that real workspace. Fresh AI checks cover only the two named public repositories; saved model results and local matching remain identified separately. The unmasked account and visible private-repository metadata are publicly released with the owner’s approval. OAuth/password screens are excluded.

All 65 original packaged demo files checked for this publication remain byte-identical. The protected readiness verifier passed for 163 files and the historical ledger’s 1 experiment, 34 call rows and 29 cache rows. No OpenAI calls, allowance renewals, AWS changes or application-data operations were performed for publishing. Older recordings, voice auditions and benchmark/readiness evidence remain preserved in the source workspace.

The six copied recording assets total 87,896,125 bytes. The MP4 is 59.67 MiB and the M4A is 23.96 MiB; the whole initial site is approximately 84.1 MiB. Git accepted the video with its expected over-50-MiB advisory; it remains below the 100 MiB file limit. Git LFS is not used.

## Reproduce and maintain

See [README](../README.md) for local preview and Pages settings, [recording notes](../recordings/cedar-v2/recording-notes.html) for scope, [verification data](../recordings/cedar-v2/verification.json), and [media manifest](media-manifest.json) for exact sizes/hashes.

Use normal commits and pushes to main for future approved site updates. To roll back a broken change, revert that commit and let Pages redeploy the previous content. Retain the original local recordings and evidence. Recheck cumulative media size before adding recording versions.

## Local execution evidence

The user created and cloned the repository before execution. Its clean main checkout and expected origin were verified. Publishing used the existing Git credential in memory; the application’s OAuth token was not used. No extra login, tool installation or new hosting account was required.

Local clone: /Users/nkaul/Documents/repos/github-manager-demo.

Detailed fresh browser checks, snapshots, hosted asset responses and SHA-256 download verification are retained in the source workspace’s ignored .tools/pages-publishing/ directory. Local preview and hosted browser checks each passed all 32 seeks. The original extra blank line at the Markdown transcript’s end was retained to preserve its exact hash; the Git whitespace check disabled only the blank-at-EOF advisory.

The original demo-video.md body is preserved as a prefix, with an appended public-site entry. The original application code, runtime state and pretest artifacts were not edited.

## Final release confirmation

Reporting commit `7c6feb3f6b32e525b6f968dfbdf9da6bca45eb42` deployed successfully in [Pages run 38495620631](https://github.com/nkaul/github-manager-demo/actions/runs/38495620631). A fresh signed-out browser confirmed that the page displays “Hosted playback verified · 2026-10-13 · 32 chapter seeks” and the completed report returns HTTP 200. The demo repository working tree is clean. The temporary publication preview server was stopped; existing app and recording servers were left intact.
