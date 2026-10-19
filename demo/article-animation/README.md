# GitHub Manager — two-minute illustrated overview

Open **[http://127.0.0.1:8124](http://127.0.0.1:8124)** for the review player. It includes playback, full screen, captions, eight chapter buttons and an MP4 download.

If the player is stopped, run from the repository root:

```bash
backend/.venv/bin/python demo/tools/article-animation/serve.py
```

- [Video](overview-1080p.mp4): exactly 120 seconds, 1920×1080, 30 fps; H.264/AAC.
- [Audio only](narration.m4a): AI-generated Cedar, Option D calmer delivery.
- [Captions](captions.vtt) and [SRT](captions.srt).
- [Transcript](transcript.md), [chapters](chapters.json) and [measured timing](timing.json).
- [Media validation](media-qa.json), [player checks](player-qa.json) and [API accounting](speech-requests.json).
- [Markdown report](../../ai-system-design/animation/validation.md).

The script has 239 words. The assembled speech measures approximately 126 words/minute, with added viewing pauses and no speech stretching. The original take omitted the closing sentence; a targeted same-voice paragraph repair restored it. Spoken word timing defines the transitions and captions. One recognized `save`/scripted `saved` word uses its neighboring timing envelope; the final sentence is explicitly recognized.

Five provider HTTP requests: one model-availability check, two speech takes and two timing requests. **$0.29** is retained as conservative media accounting within the $0.40 pilot cap and existing $5 cumulative ceiling; it is not reconciled invoice spending. No automatic retries or new repository model calls occurred.

The video explains public product behavior and an authored synthetic Orion fixture using a saved real API answer. Existing diagrams remain read-only; the new renderer supplies moving cards, text highlights, drawn arrows and state changes. No new raster image generation was required. Previous article editions, illustrations, videos, reports and protected ledgers are preserved.

Sources and intermediate renders are under `demo/tools/article-animation/` and ignored `demo/work/article-animation/`. The [article companion index](../../ai-system-design/animation/README.md) links the source mapping and preservation audit. Long-form production and publication await user feedback.
