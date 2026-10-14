# GitHub Manager — narration pilot and complete walkthrough v2

Date: October 13, 2026. Status: **Stage A complete; Option D (Cedar, calmer delivery) selected. Full walkthrough approved and completed; validation PASS.** Four one-minute previews and their [validation report](../validation/demo-voice-preview-v2.md) are available. The user authorized the full walkthrough on October 13 and subsequently authorized unmasked real-account footage. Product code was unchanged.

## Objective and approval sequence

Create a complete demonstration of the current local app with natural, consistent AI narration synchronized to the actual interface. First produce four approximately one-minute previews for the user to choose a voice and pace. Full-length narration/recording follows that selection and approval of the final storyboard. Preserve the original walkthrough, recording sources, readiness reports, benchmark evidence and budget history.

The one-minute preview evaluates presentation quality and interface orientation. It does not claim to test or explain every feature. The full walkthrough has a feature-to-scene/check matrix and covers the earlier capabilities plus the October 13 changes.

## Findings from the existing pipeline

- [prepare-audio.py](../../demo/tools/prepare-audio.py) uses macOS `say`, Samantha, rate 158, independently for each chapter. There are no expressive delivery instructions or pronunciation controls. Measured narration averages about 135 words/minute, ranging from 121.1 to 150.5 across chapters; the configured rate does not describe actual delivery reliably.
- [capture-workflows.cjs](../../demo/tools/capture-workflows.cjs) executes a chapter's actions and then waits for the chapter's audio duration. It has no sentence/action cue alignment.
- [pace-video.py](../../demo/tools/pace-video.py) spreads scene changes across narration by globally slowing a chapter's active footage. Saved results show 19 of 26 chapters slowed, from 83.2% down to 6.5% of normal speed. This can make a quick click take many seconds while the voice describes another detail. Scene-change detection is also sensitive to incidental animation and status updates.
- [render-video.py](../../demo/tools/render-video.py) estimates subtitle times from sentence word counts rather than the spoken timestamps. Chapter alignment and equal overall duration do not establish synchronization within a chapter.
- Existing media QA established decode, playback, chapter seeking and technical audio levels. The playback script mutes audio; those checks do not establish naturalness, pronunciation or perceived synchronization. The user's feedback is the perceptual evidence this iteration must address.
- The old recording predates header navigation, independent Topic/Tag browsing, clearer coverage/status, durable AI analysis protection, adaptive budgets, conflict remediation, configurable triggers and the selectable logos/KPI icons. These require current footage and revised narration.

## Voice/provider choices

| Option | Proposed use | Dependencies and rationale |
|---|---|---|
| **OpenAI `gpt-4o-mini-tts` — recommended first pilot** | Two voices, each at two paces, directed as an approachable product guide | An OpenAI key is already configured locally; TTS entitlement is not yet tested. Official documentation supports delivery instructions and recommends `marin` and `cedar` for quality. Auditioning decides suitability; no claim that either will sound best before hearing it. |
| **Gemini scripted TTS — optional fifth comparison** | A single conversational narrator using the exact pilot script; candidate `Sulafat` (documented as Warm) | No Gemini/Google API key is currently configured. The current official guide lists `gemini-3.8-flash-tts` with explicit script and style controls. Requires a locally configured Gemini key or user-assisted Google AI Studio access before generation. Recheck availability at execution. |
| **NotebookLM / Gemini Notebook Audio Overview** | Optional separate podcast-style product introduction | The service supports discussion formats and a single-speaker Brief. Its documentation describes summary, length and topic preferences rather than exact action timestamps. Therefore, my recommendation is to use scripted TTS for precise screen instruction. An Overview could be a companion after the demo. User-assisted browser sign-in would be needed if chosen. |
| **ElevenLabs** | Alternative if the first audition is unsatisfactory | No local key is configured. Its speech-with-timestamps endpoint returns alignment information, useful for captions. Requires a chosen voice/account entitlement and its own cost review. No subscription or setup is necessary for the recommended first pilot. |

Sources checked October 13: [OpenAI speech guide](https://developers.openai.com/api/docs/guides/text-to-speech), [Gemini speech generation](https://ai.google.dev/gemini-api/docs/speech-generation), [Google Audio Overview help](https://support.google.com/gemininotebook/answer/16212820?hl=en), [ElevenLabs speech with timestamps](https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps).

All voices are AI-generated, with a clear disclosure in the player/credits. Use standard voices and a warm, professional delivery. Accent default: clear US English; the user can request a different accent before generation.

## Stage A — four one-minute pilot videos

Use two voices and two paces so the user can distinguish voice preference from speed preference. Voice adjectives below are performance directions, not unverified descriptions of the stock voices.

| ID | Voice | Direction | Target spoken pace |
|---|---|---|---|
| A | `marin` | Warm, conversational guide; recommended starting point | About 145–150 words/minute |
| B | `cedar` | Same conversational direction, different voice | About 145–150 words/minute |
| C | `marin` | Calm, deliberate tutorial with more space between ideas | About 130–135 words/minute |
| D | `cedar` | Same calm direction, different voice | About 130–135 words/minute |

Each clip targets **60 seconds, within one second**, at 1920×1080 with the actual current app. The script and action sequence are shared; visual holds and cue placements adapt to the generated speech. Spoken rate is measured and reported, not assumed from a speed parameter. Use a short script with room for clicks, visual reading and pauses. Do not stretch speech or slow all actions to force a duration.

### Proposed pilot storyboard

These are initial scene windows; final cuts follow the measured audio cues in each version.

| Approximate time | Interface shot/action | Main point |
|---|---|---|
| 00–08 | Current explorer and tail-free zen logo | One workspace for repositories |
| 08–19 | Sidebar Domain/Project structure, Topics and Tags | Browse the different organization dimensions |
| 19–28 | Filtered table and one row selection | Compact KPI icons and selected count |
| 28–43 | AI Organization reviewed run preview | Batch size, budget and prior-analysis protection; review remains explicit |
| 43–52 | One manual assignment/drop with visible resulting membership | Everyday organization stays under user control |
| 52–60 | Appearance selector, rays/aura choice | New logo preference; return to explorer to close |

### Draft common narration

> GitHub Manager brings your repositories into one clear workspace, with a calmer interface and a little zen.
>
> Use the sidebar to browse projects, topics, and tags. Search and filters help you narrow the list.
>
> The compact cards show what is labeled, what still needs a project, and which repositories you've selected.
>
> AI Organization lets you preview a repository batch and its budget, then review taxonomy and classification suggestions. Approve suggestions to apply them.
>
> Already analyzed repositories stay protected from repeated AI calls. You can explicitly re-analyze when something important changes.
>
> Keep control with manual assignments, drag and drop, and local rules. In Appearance, choose your favorite zen cat.

Record public/synthetic samples in a disposable workspace. Do not require GitHub login or live classification for this audition. Only the sanitized narration text is sent to the speech provider. No screenshots, private metadata, README text or credentials are needed by TTS.

### Production and synchronization

1. Rehearse the exact current UI workflow without speech calls. Assert every displayed outcome. Prepare clean fixture state so retakes repeat deterministically.
2. Freeze the common script and pronunciation guide: GitHub, taxonomy, OAuth (in the full video), FastAPI and the difference between local labels and GitHub topics.
3. Generate one continuous narration per pilot with consistent delivery instructions. Measure duration, silence and pace. Keep originals for retakes rather than generating on every render.
4. Align spoken phrases to explicit screen cues. Use provider timestamps when available; otherwise derive/verify phrase boundaries locally against the audio, with manual review as the fallback. Never substitute proportional sentence-length estimates for verified alignment. Any new alignment tool/download must be identified before use.
5. Keep clicks, pointer movements and scrolling at natural speed. Place actions at the corresponding spoken cue; leave the result visible for roughly 1–2 seconds where the scene permits. Use discrete cuts or result holds for longer waits. Captions and highlights use the same cue sheet. Do not globally slow a chapter.
6. Capture at a true 1920×1080 viewport; existing 25fps capture is adequate for this UI. Review complete modal content, scrolling, font readability and a laptop-size playback view. Pointer/highlights must not cover controls or labels.
7. Normalize speech consistently (target around −16 LUFS, true peak at or below −1.5dBTP), check joins for clicks/truncation and leave music off for fair voice comparison.
8. Validate the final muxed videos, not only raw clips: decode, browser playback, captions, duration and action-cue agreement. Target key pointer/click cues within 0.5 seconds of the intended phrase. Record any edit that changes apparent elapsed time. Human listening/selection is the final naturalness gate; automated playback is insufficient.

### Pilot cost and dependencies

Propose a **$0.50 maximum incremental speech budget** and **at most eight speech requests**: four initial clips plus up to four targeted retakes. Do not retry unknown outcomes automatically. Check current model pricing and a conservative per-call bound before dispatch; stop if a defensible bound cannot fit the cap.

The existing app ledger handles classification/generation, not speech. Maintain a separate speech request/cost manifest and coordinate its reserved/estimated cost against the remaining original **$5 total ceiling**, including app outstanding holds. Do not replenish the app allowance or treat speech as free because it is outside that ledger. Keep app paid jobs idle during the short generation window. Report speech usage separately and in the combined total. No live repository-model call is needed for the pilot.

The current frontend API proxy targets backend port 8000, and the existing browser tests use 3000/8000. Do not attach a disposable fixture to a live user database. At execution, use an isolated recording environment that preserves the running app, or arrange a short controlled stop/restart after checking for active jobs; restore normal service afterward. A backend restart requires GitHub sign-in again. Do not promise side-by-side ports without first adapting/testing that routing.

### Pilot deliverables and user selection

Save new assets under `demo/voice-preview-v2/`: four named MP4s, separate audio copies, captions/transcript, a comparison player, cue/timing manifest and request/cost metadata without secrets. Add generated nested media to ignore rules when implementing so raw audio/video is not accidentally committed. Save a Markdown validation/review report under `docs/validation/`, and link the previews from a new section in `demo-video.md` without replacing historical results.

Ask the user to select A/B/C/D and note any pronunciation or timing issues, with optional 1–5 ratings for naturalness, clarity, pace and synchronization. A user can choose one voice with the other pace. Do not produce the full-length paid narration before that choice.

## Stage B — complete current-feature storyboard

Target approximately **20–25 minutes**, chaptered; determine the final duration from the selected pace and rehearsed actions. Retain useful original workflow ordering: inventory → evidence → taxonomy → classification/review → manual controls/rules → automation/recovery → resets. Build a mapping from all 35 historical recorded checks to current scene IDs, add the new checks below, and explicitly mark any unperformed live check. Earlier PASS records are historical evidence, not new-run results.

| Coverage group | Required content and demonstrated checks |
|---|---|
| Onboarding and trusted inventory | OAuth App login completed outside capture; actual read-only GitHub sync if the user supplies a session; My Repos, Favorites, Access candidates and explicit inclusion; source coverage, partial/unavailable access and private-input exclusion. Mask identifying/private account details. |
| Explorer and presentation | Current Material palette, header actions, compact/collapsible Collections, five KPI icons/scoped/selected counts, search/language/visibility chips, sorting, pagination, details and links. Header taxonomy fetches repositories only after a concept click. |
| All four taxonomy dimensions | Explain Domain → Project and independent Topics/Tags; alias search, accepted versus pending counts, zero-member concepts, concept-card navigation. Topic/tag-only repos can be Labeled while having No project. |
| Evidence | Local RAKE/TF-IDF evidence, phrases, sections, provenance/version, public access recheck, metadata-only fallback and private restriction. Earlier BM25/YAKE/model-readiness reports remain available; do not present them as new product inference or rerun their benchmark. |
| Discovery and review | Automatic/manual cohort selection, separate taxonomy/classification counts, exact preview/start, cache versus live provenance, saved drafts and explicit publication; conflict details, archived reservations, aliases, reuse/rename/remove/exclude, undo and atomic validation. |
| Classification and decisions | Reviewed batch/cost preview, progress/history/outcomes, filtered/grouped suggestion review, existing memberships, individual/selected accept/reject, protected USER decisions and honest No match/blocked/unknown states. |
| Durable analysis and local reconciliation | Show previously analyzed repos excluded from routine paid requests, including No match; taxonomy/mapping changes reconciled locally; analysis versus label coverage versus freshness; extraction can mark stale; explicit reasoned re-analysis for taxonomy and classification. Show previews without forcing repeat paid calls. |
| Manual and drag/drop | Single/bulk additions and removals; multiple memberships; Project/Topic/Tag targets in sidebar/header; selected-row set confirmation; Domain drop opens a Project choice; keyboard/touch alternatives; no exclusive move implied. |
| Canonical content and rules | Create/edit/rename aliases, stable IDs, project parent editing, merge/archive, Unassigned dependencies; rule preview/approval, Rules only, incremental/full reconciliation and unpublished rediscovery. |
| Budgets | Fixed window usage, selective limit overrides versus renewal, adaptive per-run bound, finite grants, unchanged cumulative ceiling and zero-call local work. Use isolated fixtures for renewal/override demonstrations so the user's real allowance remains intact. |
| Automatic organization | Saved scope/count/budget defaults, weighted/distinct/new-project thresholds and eligible types, window, quiet period, cooldown and current trigger explanation; one actual scheduler run with clearly labeled fixture AI, offline reconciliation of analyzed repos and no retry loop. Disclose any removed idle wait. |
| Latest Work and continuity | 7/14/30/90-day contribution-based windows, honest empty/partial live observations versus labeled synthetic activity; reload, sign-out/in and isolated backend restart; durable records and interrupted-call handling. |
| Appearance and responsive use | Tail-free rays versus continuously rotating aura, saved browser preference, animation off, reduced motion and matching static favicon; desktop and phone navigation/assignment alternatives. |
| Reset and recovery, last | Independent AI/content scopes, exact preview/counts and DELETE, expiry/change validation, AI-only preservation, domain-only dependencies, full epoch/ID reset, cleanup and cached restart; core/report/budget/analysis-receipt preservation and no silent paid resend. Disposable fixtures only. |
| Readiness and boundaries | Link Phase 0/0.5 evidence, preservation and current checks; local SQLite/one-worker scope, cloud runtime deferred, bounded GitHub coverage and review-based AI. Retained AWS scratch validation is evidence, not a cloud deployment demonstration. |

Use current successful cached outcomes and existing real-model evidence where compatible. Label LIVE GITHUB, CACHED REAL AI, LOCAL RULES and FIXTURE separately. Do not manufacture a fresh live result or replay invalid old IDs. A genuinely new classification proof, if useful, gets an explicit small call/spend plan before it runs; approval of the voice pilot does not authorize it.

## Stage C — full recording and handoff

After voice selection: approve the final scene/script/coverage matrix, record the current UI, generate narration in coherent chapter-sized segments with the same voice profile, and align each segment's actions before packaging. Use the selected pilot as a consistency reference. Re-record failed/stale UI scenes; never narrate success over a failed action.

Deliver versioned full MP4, audio-only file, accurate captions, chapter player, transcript, feature/check matrix and Markdown validation/cost report. Preserve the old video/audio and all original readiness evidence. Review actual audio and representative final frames, test seek/captions/fullscreen, and compare protected evidence/media hashes. Upload/publication/submission is a separate user action.

## Decision requested now

**Stage A was approved with Marin and Cedar and is complete.** It used eight API requests and retains $0.50 in conservative media accounting within the original $5 ceiling. No further paid pilot requests are authorized by that exhausted cap. Choose A/B/C/D or a voice plus pace adjustment from the [comparison](../../demo/voice-preview-v2/README.md). The full video waits for that choice and storyboard review; any new voice generation needs a fresh bounded media budget that carries the existing media accounting forward.


## Full walkthrough execution update — October 13

The user selected **Option D: Cedar, calmer delivery** and authorized the full demo, then signed in and requested real-account data without masking. The updated storyboard is `demo/tools/full-v2/story.json`: 32 chapters, four narration/action paragraphs per chapter. The beginning uses the actual signed-in workspace and a fresh GitHub inventory sync. Remaining edits, allowance changes, backend restart and destructive resets operate on a clearly labeled SQLite copy of that same account’s real inventory and organization. No synthetic repositories or deterministic fixture AI are introduced. The original OAuth session and credentials remain in memory.

Two narrowly bounded live intelligence operations use only **allegro/ralph** and **acassen/keepalived**, both public repositories from the account’s inventory. The recording-only provider verifies their public metadata immediately before extracting input and checks the exact repository allowlist again before provider invocation. Private input is denied. A hard four-HTTP-attempt limit includes token counting; retries are disabled. This restriction resolved an automatic approval review rejection of the initial broader capture launch. The initial rejected launch did not execute.

Narration uses the selected Cedar voice and speed 0.93, with consistent warm, deliberate directions. Three chapters share each speech take to preserve delivery continuity while limiting requests. Planned media use is eleven TTS calls and two batched word-timing calls, leaving up to three targeted retakes inside **16 media calls / 20 total new OpenAI HTTP requests**. The **$2.50 media reservation cap** remains inside the original **$5 combined ceiling**, including the earlier $0.50 voice pilot, original app accounting and any new real-model costs in the recording copy. Binary TTS responses have no invoice token usage; conservative reservations are retained rather than reported as actual charges.

Actual spoken word timestamps define narration paragraphs and captions. Each paragraph maps to a recorded action/result sequence at normal speed. Discrete cuts shorten waits or setup; result holds provide reading time. Speech and pointer footage are never globally slowed to fill a duration. The actual 90-second scheduler wait is verified independently, with the edit disclosed.

The full recording, audio, captions, chapter player, transcript and machine-readable checks will be saved under `demo/full-v2/`, with sources under `demo/tools/full-v2/` and a Markdown report at `docs/validation/demo-full-v2.md`. The original demo guide will receive an appended entry. Earlier media and 163 protected readiness files remain preservation gates.
