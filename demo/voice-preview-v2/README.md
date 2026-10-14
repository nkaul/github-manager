# GitHub Manager — one-minute voice comparison

Four **60-second, 1920×1080** previews of the current interface, with AI-generated Marin and Cedar narration. The script and feature sequence are shared; pauses/clicks follow each track's actual speech. Music is off.

Open **http://127.0.0.1:8122** for the comparison player. If it is stopped, run this from the repository root:

```bash
python3 demo/tools/voice-preview-v2/serve.py
```

| Sample | Voice and direction | Measured narration pace before added UI pauses | Video |
|---|---|---|---|
| A | Marin · conversational | 147.8 words/minute | [Watch A](A-marin-conversational-1080p.mp4) |
| B | Cedar · conversational | 155.5 words/minute | [Watch B](B-cedar-conversational-1080p.mp4) |
| C | Marin · calm | 130.8 words/minute | [Watch C](C-marin-calm-1080p.mp4) |
| D | Cedar · calm direction | 146.7 words/minute | [Watch D](D-cedar-calm-1080p.mp4) |

Try A/B for voice and A/C or B/D for pace. Cedar did not follow the requested spoken rates as closely; these are measured results. Tell Codex your preferred letter or voice plus pace adjustment. The full walkthrough waits for that selection.

The previews show the current logo, Projects/Topics/Tags, search, KPI icons and selection, adaptive batch preview, prior-analysis protection, suggestion review, drag/drop and Appearance. All app data here is isolated public/synthetic fixture data. No fresh repository classification or GitHub sync was performed for this audition. This one-minute sample is not the complete feature validation video.

Captions use recognized word timestamps. Cedar's closing Appearance sentence was restored with a short, same-voice take; its caption uses a measured sentence envelope. The main delivery is not time-stretched. Original speech, inputs, ASR results and cue logs are retained locally under `demo/work/voice-preview-v2/`.

Eight API requests total: five successful speech requests (four original tracks plus one shared Cedar closing repair), two successful batched word-timing requests and one failed timing request following a locally corrected WAV-header bug. No automatic retries. The [audit](speech-requests.json) retains **$0.50 in conservative media accounting**, within the approved limit. This is a retained allowance/reservation, not a confirmed invoice; binary speech responses did not return billing token usage. The app's classification allowance was not changed.

See [media verification](media-qa.json), [player verification](player-qa.json), and the [Markdown validation report](../../docs/validation/demo-voice-preview-v2.md). The original narrated walkthrough, reports, budgets and benchmark evidence remain preserved. The normal app remains at **http://127.0.0.1:3000**.
