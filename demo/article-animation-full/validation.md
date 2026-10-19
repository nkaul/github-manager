# Full animated companion — validation

Date: October 15, 2026. Result: **PASS — ready for editorial review**.

Authorization: the user requested the remaining animated videos, with slower pacing and announced sections that introduce each topic and its purpose. The original pilot, articles, diagrams, app and readiness records were preserved. No public publishing was requested or performed.

## Delivered media

| Property | Result |
|---|---|
| Complete companion | 41:32 / 2492.233 seconds |
| Picture | 1920×1080, 30 fps, 74,767 frames |
| Encoding | H.264 / YUV420p / AAC; fast-start MP4 |
| Master file | 125,108,234 bytes |
| Standalone narrated chapters | 18, each with a spoken section name and purpose |
| Slower product overview | 1:53; chapter one also exported separately |
| Additional references | Eight silent 32-second animated summaries plus complete original figures |
| Narration | AI-generated Cedar, speed configuration 0.82, calm delivery |
| Script | 3,760 words |
| Mean pace over speech intervals | 108.15 words/minute |
| Individual beat pace range | 92.2–118.7 words/minute; the mean is not a per-sentence guarantee |
| Reading holds | ≥3.5 seconds per result; introductions receive an extra four seconds |
| Caption cues | 682 master VTT/SRT cues; separate chapter captions |
| Integrated loudness | -16.15 LUFS |
| True peak | -1.88 dBTP |
| Full master decode | PASS; every frame and audio stream decoded |
| Preserved files | 490 unchanged |

The mean spoken pace is about fourteen percent slower than the original pilot's 125.7 words/minute. Whole-video pace also includes section and reading holds. The resulting runtime is longer than the earlier proposal's estimate; content is chaptered rather than compressed into a faster fixed-length film.

## Timing, repairs and voice consistency

Seven coherent Cedar takes used identical voice, model, speed and delivery instructions. Two word-timing requests covered those takes. Alignment caught an omitted context passage and missing augmentation passages. One combined targeted take restored those five beats; a further alignment request checked the repair. Raw original responses, the repair and timing metadata remain under ignored `demo/work/article-animation-full/`.

The final 3,760 caption words exactly preserve the authored script order. Thirty-eight individual words use neighboring ASR envelopes after number/acronym normalization; they are not described as exact recognized word boundaries. The poor raw take alignment that triggered repair is retained for provenance and is not presented as the final narration's quality score.

Approximately 85.52 seconds of silence were inserted at existing sentence boundaries. Every voiced PCM sample in the selected passages is preserved; pitch and speech speed were not digitally stretched. One-second visual leads, result holds and longer introduction holds are added outside the narration. Loudness normalization applies a common measured gain strategy before AAC encoding.

All seventy-four beat layouts passed font loading and text-bound checks. Cards reveal at staged word positions; request tokens, phrase scoring and receipt transitions provide motion beyond the original diagram images. Four encoded-region comparisons verify visible keyword, request, receipt and reservation changes after encoding; see [motion QA](motion-qa.json). This establishes visible change, not comprehension. The renderer samples active motion intervals at 30 fps and holds a rendered frame during deliberate reading pauses; the final output is constant 30 fps. Original raster illustrations are never rewritten.

See [synchronization QA](sync-qa.json), [media QA](media-qa.json) and the [measured storyboard](../../eval/ai-system-design/animation/full/storyboard.md). Automated alignment, audio meters and muted playback do not establish listener preference, accent consistency or comprehension. Those remain editorial review judgments.

## Player and encoded-media verification

Player status: **PASS**. The installed Chrome check covers master playback/pause, full screen, caption controls, optional pace, all eighteen chapter files, all eight silent summaries, overview selection, master seeking with current-topic updates, and desktop/phone layout. HTTP byte ranges support seeking; out-of-package paths are denied. No external requests are needed for playback.

The master was fully decoded and matched all 74,767 expected frames. Every standalone chapter/reference received a header, duration, stream-presence and last-second decode check. Standalone chapters copy the already decoded master source video; the player also checks their opening-frame decode. This is the stated verification scope rather than a claim of independent full decoding of each duplicate export.

## Content, coverage and limitations

The source map covers all twenty academic article sections and twenty-four mechanism-inventory rows across eighteen chapters. The narrative follows Orion's source evidence, RAKE phrases, taxonomy discovery, lexical candidates, augmented request, structured answer, human review and durable receipt. It explains privacy, counterexamples, automatic thresholds, fences, exact request counting, reservations, tokenomics and evaluation separately.

The six candidate scores, four chosen IDs, E1 evidence, historical token counts and small-benchmark results remain grounded in the preserved worked examples and article. Discovery output and classification registry are separate historical fixtures. Libraries sharing a framework are not presented as the same initiative. Current implementation, historical measurements, offline BM25 comparisons, illustrative actions and future experiments are labeled.

Dense retrieval, reranking, contextual retrieval, agentic/adaptive RAG and Jev remain research options rather than claimed implemented features. No new Jev experiment, taxonomy/classification run, repository access check, GitHub login, AWS operation or app regression suite was performed for this media change. Historical results are explained, not rerun. Large exact payloads and formulas remain in the source article and worked examples.

The eight silent reference summaries use four excerpts each; they are navigation aids rather than exhaustive animation of every original diagram label. All eight original illustrations are available alongside them, copied byte-for-byte.

## Provider accounting

This revision used **11 HTTP requests**: seven narration takes, two alignment batches, one targeted repair take and one repair alignment. All succeeded. Including the pilot, animation totals **16 requests** and **$1.97 retained conservative reservations** under the shared sixteen-request/$2 animation allowance.

The new revision accounts for $1.68. Its recorded admission snapshot plus these reservations is approximately **$4.183029** under the existing $5 cumulative ceiling. Binary speech responses do not reconcile invoice usage; these are retained bounds, not a billed-cost assertion. Prior ledgers were not reset. Only the fixed public/synthetic narration and its generated audio went to speech/timing endpoints. No private repository content was sent.

## Preservation and local reproducibility

The pre-production baseline confirms **490 files unchanged**, including prior article editions, original diagrams, pilot/full demo media, readiness reports and protected accounting data. All new work is confined to `demo/article-animation-full/`, `demo/tools/article-animation-full/`, `eval/ai-system-design/animation/full/` and ignored media intermediates. [Preservation audit](../../eval/ai-system-design/animation/full/preservation-qa.json), [asset manifest](../../eval/ai-system-design/animation/full/assets-manifest.json) and [export checksums](checksums.json).

See the [media guide](README.md) for local restart/render commands. Further media generation or public upload is outside this completed local production. The original pilot and its documentation remain historical records, including their earlier statements that a full version was deferred.
