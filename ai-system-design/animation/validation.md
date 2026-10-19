# Two-minute animated overview — validation

Date: October 15, 2026. Result: **PASS for media, synchronization, factual-source and playback checks. Ready for user presentation feedback.**

The user authorized the two-minute version first to assess alignment and make adjustments. The full companion, detailed reference clips and public publication remain deferred.

## Delivered result

Watch the [local player](http://127.0.0.1:8124), open the [MP4](../../demo/article-animation/overview-1080p.mp4), or read the [transcript](transcript.md). The [storyboard](storyboard.md) records measured scene and phrase-cue times.

| Property | Verified result |
|---|---|
| Duration | 120.000 seconds |
| Picture | 1920×1080, 30 fps, 3,600 frames |
| Encoding | H.264, YUV420p, AAC audio, fast-start MP4 |
| Video size | 8,070,793 bytes, approximately 7.7 MiB |
| Narration | AI-generated Cedar, selected Option D calmer delivery |
| Spoken script | 239 words, approximately 125.7 words/minute over assembled speech intervals |
| Speech stretching | None; viewing pauses added between narration segments |
| Captions | 43 VTT/SRT cues; caption words exactly match script word order |
| Spoken-token agreement | 99.59% after targeted ending repair |
| Audio loudness | −16.13 LUFS integrated |
| Audio true peak | −1.95 dBTP |
| Longest detected silence | Approximately 1.78 seconds at the stated detector threshold |
| Full audio/video decode | PASS |

The video uses original illustrated characters and the existing zen logo in browser compositions, with new SVG cards, text highlights, drawn arrows, moving request tokens and state changes. Source PNG pixels were not rewritten. No new raster image generation or generative-video service was used.

## Content and provenance

The eight scenes explain discovery, organization dimensions, taxonomy review, evidence selection, candidate retrieval, structured classification, durable analysis and execution budgets. The source mapping is in [coverage-pilot.json](coverage-pilot.json).

The Orion fixture's E1 text, six candidate IDs and four selected IDs were checked against the [preserved worked example](../publication/v2/examples/orion-api.json). All four saved assignments cite E1. The video labels the fixture synthetic and its displayed answer a saved test result. The taxonomy scene explains the architectural relationship between discovery and classification; it does not claim the saved discovery draft supplied the separate classification benchmark registry. The Project-removal scene is an illustrative user action, not recorded account activity.

No fresh repository classification, taxonomy benchmark, Jev test, GitHub login, AWS operation or application test was performed. Local Next.js/FastAPI/SQLite behavior is the scope; cloud infrastructure is not depicted as a current deployment. This overview does not claim to explain every algorithm in the longer article. The full coverage plan remains available in the [production proposal](../publication/v2/animation-plan.md).

## Synchronization and repair

The initial continuous Cedar take ended after “Understand why it belongs,” omitting the final sentence. The original audio and recognized text are retained under ignored `demo/work/article-animation/`. A short, same-voice/same-speed closing paragraph was generated with a separate spoken timing marker. Alignment recognized the final word `yours`; the marker was removed before assembly. The entire main narration was not regenerated.

Scene durations, source selection, highlights and named transitions follow recognized spoken timestamps. The original script is used for caption text. One ASR `save` versus scripted `saved` word uses a neighboring timing envelope; that exception is explicitly retained in the timing metadata. Missing closing words are not assigned invented timestamps in the final version.

The encoded video was also sampled around the moving request-card sequence to confirm that information-carrying motion survived encoding. [Synchronization QA](../../demo/article-animation/synchronization-qa.json) records the sampled times and pixel-change check. That check establishes visible change, not comprehension or engagement.

All scene layouts were inspected, followed by representative actual encoded frames and player captures. Minor style judgments, the perceived naturalness of the voice, and preferred animation density remain the purpose of the user's pilot review. Muted browser automation and audio meters do not establish those preferences.

## Playback checks

The installed Chrome browser successfully checked duration/resolution, playback and pause, full screen, eight chapter buttons, seeking, 43 caption cues, caption controls and desktop/phone layout. The normal player displays captions below the animation to preserve the workflow ribbon; full screen uses native captions. Phone viewers can use full screen for small diagram labels.

The localhost server supports byte-range requests and denies paths outside the packaged artifacts. The browser check recorded no page errors or external requests. See [player QA](../../demo/article-animation/player-qa.json) and [media QA](../../demo/article-animation/media-qa.json).

The browser-control integration was unavailable for opening a visible tab automatically. The preview server is running at the link above; the user can open it directly. This does not affect the successful installed-Chrome playback checks.

## API accounting

Five HTTP requests were made: one model-availability check, the original speech take, its timing request, the targeted ending take and its timing request. All succeeded; no automatic retries occurred. The narrowed pilot admission limits were five requests and $0.40 in conservative media reservations, inside the proposed animation plan's broader limits.

**$0.29 remains accounted as conservative reservations**, within the pilot cap and existing $5 cumulative ceiling. Binary speech responses do not provide reconciled invoice usage, so this amount is not described as an actual bill. Prior media reservations and application accounting were carried into admission checks without resetting any ledger. [Sanitized request manifest](../../demo/article-animation/speech-requests.json).

Only the fixed public narration and its generated audio were sent to speech/timing endpoints. No private repository content was included. No new repository-model calls occurred.

## Preservation and reproducibility

The [preservation comparison](preservation-qa.json) confirms **455 pre-existing files unchanged**, including prior article editions, illustrations, final demo/voice media, Markdown/JSON readiness records and the protected inference ledgers. The baseline predates production. App source, real workspace state, model configuration and cloud resources were not changed.

New tools are under `demo/tools/article-animation/`; final media are under `demo/article-animation/`; sources/intermediates are retained under ignored `demo/work/article-animation/`. [Checksums](../../demo/article-animation/checksums.json) bind the exported media, captions and measured timeline. Re-rendering uses saved narration and does not require another provider request.

To restart playback from the repository root:

```bash
backend/.venv/bin/python demo/tools/article-animation/serve.py
```

The next decision is editorial: adjust the motion style, pace, information density or voice before extending these scenes into the longer companion.
