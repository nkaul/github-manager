# GitHub Manager — full illustrated companion

Watch the [local chapter player](http://127.0.0.1:8125), open the [complete 1080p video](complete-1080p.mp4), or start with the [slower product overview](overview-slower-1080p.mp4).

The complete video runs **41:32**. It contains eighteen standalone narrated chapters, each beginning with its section name and purpose. Eight additional **32-second silent animated reference summaries** link back to complete original illustrations. All picture is 1920×1080 at 30 fps, in the established paper, handwritten ink and blue/purple marker style.

This revision incorporates the pilot feedback: **108.2 spoken words/minute on average**, compared with approximately 125.7 in the preserved pilot; pauses between sentences; a one-second visual lead; at least 3.5 seconds to read each result; and an extra four-second hold after section introductions. Voiced samples are not time-stretched. The longer runtime follows speech and reading time rather than forcing the material into the earlier estimate.

Narration uses the selected **AI-generated Cedar voice**. English VTT/SRT captions, a transcript, optional playback pace, full screen and separate chapter downloads are included. In the normal player captions sit below the animation; in full screen they use native video captions. Reference summaries are intentionally silent and loop in the player.

## Choose a topic

| Chapter | Duration | Purpose |
|---|---|---|
| [1. The problem and the product](chapters/01-purpose.mp4) | 1:53 | Find repositories by their purpose and relationships, then keep your decisions. |
| [2. Organization vocabulary](chapters/02-vocabulary.mp4) | 1:58 | Give initiative, subject and technology different meanings. |
| [3. Context engineering](chapters/03-context.mp4) | 2:12 | Select, authorize and structure the information needed for a decision. |
| [4. Evidence and chunking](chapters/04-evidence.mp4) | 2:14 | Preserve source-linked purpose text while keeping the request bounded. |
| [5. Local algorithms](chapters/05-keywords.mp4) | 2:18 | Extract useful signals without confusing keyword scores with meaning. |
| [6. Taxonomy intelligence](chapters/06-taxonomy.mp4) | 2:11 | Propose a useful collection vocabulary, then publish only reviewed concepts. |
| [7. Retrieval](chapters/07-retrieval.mp4) | 2:13 | Find plausible approved concepts before deciding which relationships hold. |
| [8. Augmentation](chapters/08-augmentation.mp4) | 2:10 | Assemble evidence, candidate meaning and decision policy into the model request. |
| [9. Generation and validation](chapters/09-generation.mp4) | 2:09 | Return supported IDs, then check whether a proposal is safe and useful. |
| [10. Counterexamples and failure cases](chapters/10-counterexamples.mp4) | 2:09 | Use awkward inputs to distinguish matching words from supported meaning. |
| [11. Memory and user authority](chapters/11-memory.mp4) | 2:10 | Preserve completed work and corrections independently of current labels. |
| [12. Loop engineering](chapters/12-loops.mp4) | 2:26 | Control when work runs, skips, reconciles, retries or becomes stale. |
| [13. Harness engineering](chapters/13-harness.mp4) | 2:16 | Make every admitted request measurable, authorized and finite. |
| [14. Tokenomics and optimization](chapters/14-tokenomics.mp4) | 2:15 | Measure the total useful outcome, not merely a smaller prompt. |
| [15. Evaluation and evidence](chapters/15-evaluation.mp4) | 3:20 | Evaluate retrieval, decisions and workflow separately, with honest limits. |
| [16. Stronger retrieval and contextual retrieval](chapters/16-future-retrieval.mp4) | 3:13 | Add a retrieval layer only when its errors and costs justify the change. |
| [17. Decision models: the Jev research question](chapters/17-jev.mp4) | 2:15 | Test bounded semantic judgments without changing multi-label meaning or user authority. |
| [18. The complete trace and next steps](chapters/18-complete-trace.mp4) | 2:11 | Reconnect each mechanism to the repository the user wanted to find. |

## Read alongside the videos

- [Full narration](transcript.md), [validation](validation.md), [measured timeline](timing.json), [player checks](player-qa.json), [media checks](media-qa.json), and [synchronization checks](sync-qa.json).
- [V2 article](../../ai-system-design/publication/v2/article.md) and [exact worked examples](../../ai-system-design/publication/v2/workflow-examples.md).
- [Academic edition](../../ai-system-design/github-manager-ai-system-design.md) and [illustrated detailed edition](../../ai-system-design/illustrated/github-manager-ai-system-design-illustrated.md).
- [Source coverage](../../ai-system-design/animation/full/coverage.json), [storyboard](../../ai-system-design/animation/full/storyboard.md), [asset provenance](../../ai-system-design/animation/full/assets-manifest.json) and [preservation audit](../../ai-system-design/animation/full/preservation-qa.json).

Repository links above open as local files from this Markdown document. The HTTP preview deliberately serves only the media package, so it cannot expose application files, environment variables or intermediate work.

## Playback and local reproduction

From the repository root:

```bash
backend/.venv/bin/python demo/tools/article-animation-full/serve.py
```

Then open **http://127.0.0.1:8125**. Keep that terminal running. A local preview instance may already be running. The original pilot remains available in `demo/article-animation/`; its own preview uses port 8124.

Tools live in `demo/tools/article-animation-full/`. Saved raw speech, alignment responses, repair provenance, rendered motion frames and assembly intermediates remain in ignored `demo/work/article-animation-full/`. Rendering and packaging use those saved artifacts and need no further paid model call:

```bash
.tools/node/bin/node demo/tools/article-animation-full/render.cjs
backend/.venv/bin/python demo/tools/article-animation-full/finalize.py assemble
backend/.venv/bin/python demo/tools/article-animation-full/finalize.py verify
.tools/node/bin/node demo/tools/article-animation-full/check-player.cjs
backend/.venv/bin/python demo/tools/article-animation-full/reports.py
```

The renderer uses installed Chrome, the local Chalkboard font and repository-local FFmpeg. It caches completed beats. Font binaries are not redistributed. Run player checks while the localhost server is running. Speech generation is complete; the shared request allowance has been used and should not be reset or rerun for reproduction.

## Scope and interpretation

Orion is an authored synthetic example; its displayed classification is a preserved real API result. The FastAPI contrast is public. Current runtime, offline comparisons, historical evaluation, illustrative user actions and proposed research have distinct labels. No benchmark, repository classification, AWS operation, private-content upload or publication was performed during this media revision. The original pilot, earlier articles, diagrams, app code and readiness evidence remain preserved.

The silent references summarize a few animated states; they are not complete animated reproductions of every label in each earlier raster diagram. The full series and linked original illustrations provide that detail. The coverage map connects all twenty academic source sections and twenty-four inventory mechanisms to chapter explanations; it does not claim every source sentence is spoken.
