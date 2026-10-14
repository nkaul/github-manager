# GitHub Manager — Marin/Cedar voice pilot validation

Date: October 13, 2026. Technical status: **PASS**. Subjective voice preference/naturalness: **awaiting user audition**. The full walkthrough is pending that choice and final storyboard review.

## Watch and compare

Open **http://127.0.0.1:8122** for the [comparison player](../../demo/voice-preview-v2/index.html). If needed, restart it with `python3 demo/tools/voice-preview-v2/serve.py` from the repository root. The app remains at http://127.0.0.1:3000.

| Sample | Voice/direction | Measured source narration pace | MP4 |
|---|---|---|---|
| A | Marin, conversational | 147.8 words/minute | [A](../../demo/voice-preview-v2/A-marin-conversational-1080p.mp4) |
| B | Cedar, conversational | 155.5 words/minute | [B](../../demo/voice-preview-v2/B-cedar-conversational-1080p.mp4) |
| C | Marin, calm | 130.8 words/minute | [C](../../demo/voice-preview-v2/C-marin-calm-1080p.mp4) |
| D | Cedar, calm direction | 146.7 words/minute | [D](../../demo/voice-preview-v2/D-cedar-calm-1080p.mp4) |

Each video is **60.0 seconds, 1920×1080, 25fps, H.264/AAC**, with 15 English caption cues, eight feature chapters and a separate audio-only M4A. Spoken rates measure source narration before added UI-reading rests, including Cedar's closing repair; they are not the video's overall words/minute. Cedar followed the requested pace less closely than Marin. The player displays measured rates so the user can compare the delivered performances.

## What was demonstrated

All four recordings exercised the same real current frontend and actual local application services, with a disposable fixture backend and isolated test identities. Every browser API request was routed to port 8100; the normal frontend/backend continued on 3000/8000. Test-only login routes were not added to the product. The fixture backend was stopped after capture.

Ten checks passed in each recording: true 1080p/isolation, fixture taxonomy/analysis setup, all five KPI icons, Topics/Tags browsing, search narrowing three samples to two, selected/scoped KPI updates, adaptive three-repository preview with zero provider attempts, offline protection for prior analysis, native drag/drop membership addition, and changing the header logo through Appearance. Suggestion review was shown without accepting new decisions during the timed preview.

No fresh repository-model inference, live GitHub sync, AWS operation, production taxonomy edit, allowance renewal or user workspace reset was performed. Fixture classification outcomes are visibly marked Test fixture. The one-minute preview provides interface orientation and a voice audition; it is not the full feature/readiness validation requested for the next recording.

## Synchronization and media checks

The script was generated with `gpt-4o-mini-tts` using the selected stock voices. Speech was aligned from `whisper-1` word timestamps. UI actions were placed against specific phrases, with ordinary pointer/scroll/action speed and explicit reading rests. Neither speech nor video was time-stretched. Final trim positions were measured from a frame marker in the actual browser capture, rather than inferred from navigation clocks.

| Check | Result |
|---|---|
| Rehearsal | PASS; complete local sequence before paid narration. |
| Recorded workflow assertions | PASS; ten checks per variant, no browser page errors or horizontal document overflow. |
| Spoken action cues | PASS; eight sampled word/action anchors per clip. Maximum absolute deltas: A 0.138s, B 0.112s, C 0.107s, D 0.206s, before up to one 25fps frame of video quantization. |
| Final media | PASS; all four decode with the expected resolution/duration and consistent normalized speech. AAC headroom is checked after encoding against the −1.5dBTP maximum. |
| Comparison player | PASS; all four videos play, captions load, eight scenes seek per variant and byte-range requests return 206. No page errors at 1440/1280/390px widths; no horizontal overflow at the tested narrow widths. |
| Source checks | PASS; Ruff checks/format and Node syntax checks for new media tooling. Product code/dependencies were unchanged, so unrelated product suites were not repeated. |
| Human listening | Pending user feedback. Automated playback runs muted and establishes technical playback only; it does not certify naturalness or pronunciation. |

See [media results](../../demo/voice-preview-v2/media-qa.json), [player results](../../demo/voice-preview-v2/player-qa.json) and [cue audit](../../demo/voice-preview-v2/synchronization-qa.json). Final frames were visually inspected for the protected/offline preview and Appearance controls. [Desktop player](../../demo/voice-preview-v2/comparison-desktop.png) and [phone player](../../demo/voice-preview-v2/comparison-phone.png) previews are saved.

## Corrections and limits

One timing request failed with HTTP 400 after a local streaming-WAV-header conversion bug. The original successful audio was retained; its PCM samples were recovered and its seekable header validated. That failed request was not automatically repeated. The two successful timing requests each processed a pair of verified tracks.

Both Cedar takes lacked an aligned closing Appearance sentence. A short same-voice completion was generated once and reused in both versions. It uses a measured sentence caption envelope rather than invented per-word timestamps; a short pause and low-level edge fades handle the join. The unchanged original takes and complete call history remain locally available. Normalized ASR/reference agreement for the retained main narration is approximately 97–100%; minor recognition differences remain for human audition. No claim of a perfect speech transcription or automated listening review is made.

## Requests, budget and preservation

**Eight API requests total**: four original speech generations, one short Cedar speech completion, two successful batched word-timing requests and one failed word-timing request. No further paid calls were made after the cap was reached. Only the sanitized product script and generated narration audio were sent to OpenAI.

The separate media manifest retains **$0.500000 in conservative accounting**: $0.10 per original generation, $0.04 for the closing repair and $0.02 per timing attempt, including the failed request. These are retained allowances, not confirmed invoice charges; binary speech responses did not provide billing-token usage. Application ledger accounting was $0.127619 with zero outstanding run holds. Combined accounting is **$0.627619 of the original $5 ceiling**. The app UI reports its own ledger and does not include this separate media allowance; future media work must carry it forward when checking the combined ceiling.

Pricing references checked for execution: [TTS model](https://developers.openai.com/api/docs/models/gpt-4o-mini-tts), [Whisper model](https://developers.openai.com/api/docs/models/whisper-1). Speech instructions and word timing follow the [speech guide](https://developers.openai.com/api/docs/guides/text-to-speech) and [transcription guide](https://developers.openai.com/api/docs/guides/speech-to-text). Actual invoice cost remains unverified.

The preflight preservation verifier passed for **163 protected files**, the original 34 call rows/29 cache rows, and the unchanged preflight UI. Live application tables and all current ledger tables matched the pre-pilot SQLite backups: 91 generation rows and 114 application HTTP rows were unchanged. Original video/audio/captions/player/check files retain their prior hashes. `demo-video.md` only gains a new preview section; its historical body is retained verbatim. See [preservation audit](../../demo/voice-preview-v2/preservation-qa.json).

Original media/scripts and all Phase 0/0.5 readiness/benchmark evidence remain available. New reproducible sources are in `demo/tools/voice-preview-v2/`; raw audio, ASR and capture diagnostics are ignored under `demo/work/voice-preview-v2/`. New packaged media is ignored separately; captions, audit records, player and Markdown reports remain reviewable.

## Next decision

Choose A/B/C/D, or a voice with a requested pace adjustment. Start with A, then compare C if you prefer more deliberate speech. After that choice, review the complete scene/script/check matrix in the [v2 plan](../planning/demo-video-v2.md) before full-length narration. No upload or submission has been performed.
