"""Write the media guide, storyboard, validation and artifact checksums locally."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'demo/article-animation-full'
WORK = ROOT / 'demo/work/article-animation-full'
DOC = ROOT / 'eval/ai-system-design/animation/full'
HERE = Path(__file__).parent


def load(p):
    return json.loads(p.read_text())


def save(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n')


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for data in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def label(t):
    t = round(t)
    return f'{t // 60}:{t % 60:02}'


timing = load(OUT / 'timing.json')
package = load(OUT / 'package.json')
media = load(OUT / 'media-qa.json')
player = load(OUT / 'player-qa.json') if (OUT / 'player-qa.json').exists() else {'status': 'PENDING'}
render = load(WORK / 'render.json')
coverage = load(DOC / 'coverage.json')
manifest = load(OUT / 'speech-requests.json')
prior = manifest['requests'][-1]['prior_budget']['prior_accounted_usd']
current_budget = prior + media['retained_reservations_new_usd']
status = 'PASS — ready for editorial review' if player['status'] == 'PASS' else 'Media PASS — player checks pending'

guide = f'''# GitHub Manager — full illustrated companion

Watch the [local chapter player](http://127.0.0.1:8125), open the [complete 1080p video](complete-1080p.mp4), or start with the [slower product overview](overview-slower-1080p.mp4).

The complete video runs **{package['duration_label']}**. It contains eighteen standalone narrated chapters, each beginning with its section name and purpose. Eight additional **32-second silent animated reference summaries** link back to complete original illustrations. All picture is 1920×1080 at 30 fps, in the established paper, handwritten ink and blue/purple marker style.

This revision incorporates the pilot feedback: **{timing['measured_spoken_wpm']:.1f} spoken words/minute on average**, compared with approximately 125.7 in the preserved pilot; pauses between sentences; a one-second visual lead; at least 3.5 seconds to read each result; and an extra four-second hold after section introductions. Voiced samples are not time-stretched. The longer runtime follows speech and reading time rather than forcing the material into the earlier estimate.

Narration uses the selected **AI-generated Cedar voice**. English VTT/SRT captions, a transcript, optional playback pace, full screen and separate chapter downloads are included. In the normal player captions sit below the animation; in full screen they use native video captions. Reference summaries are intentionally silent and loop in the player.

## Choose a topic

| Chapter | Duration | Purpose |
|---|---|---|
'''
for c in package['chapters']:
    guide += f"| [{c['number']}. {c['title']}]({c['file']}) | {c['duration_label']} | {c['purpose']} |\n"
guide += '''
## Read alongside the videos

- [Full narration](transcript.md), [validation](validation.md), [measured timeline](timing.json), [player checks](player-qa.json), [media checks](media-qa.json), and [synchronization checks](sync-qa.json).
- [V2 article](../../eval/ai-system-design/publication/v2/article.md) and [exact worked examples](../../eval/ai-system-design/publication/v2/workflow-examples.md).
- [Academic edition](../../eval/ai-system-design/github-manager-ai-system-design.md) and [illustrated detailed edition](../../eval/ai-system-design/illustrated/github-manager-ai-system-design-illustrated.md).
- [Source coverage](../../eval/ai-system-design/animation/full/coverage.json), [storyboard](../../eval/ai-system-design/animation/full/storyboard.md), [asset provenance](../../eval/ai-system-design/animation/full/assets-manifest.json) and [preservation audit](../../eval/ai-system-design/animation/full/preservation-qa.json).

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
'''
(OUT / 'README.md').write_text(guide)

chapter_rows = '\n'.join(f"| {c['number']} | [{c['title']}](../../../../demo/article-animation-full/{c['file']}) | {c['duration_label']} |" for c in package['chapters'])
(DOC / 'README.md').write_text(f'''# Full illustrated AI system design companion

The [complete local player](http://127.0.0.1:8125) is ready: **{package['duration_label']}**, eighteen narrated chapters and eight silent animated reference summaries. Cedar now averages **{timing['measured_spoken_wpm']:.1f} spoken words/minute**, with explicit spoken section names, purposes and longer reading holds.

This is the new edition authorized after the user's pilot pacing feedback. The earlier [pilot documentation](../README.md) and its “full version deferred” statements remain unchanged as historical records of that stage.

| Section | Video | Runtime |
|---|---|---|
{chapter_rows}

See the [media guide](../../../../demo/article-animation-full/README.md), [validation](validation.md), [transcript](transcript.md), [storyboard](storyboard.md), [source coverage](coverage.json), [production brief](production-brief.md), [asset manifest](assets-manifest.json) and [preservation audit](preservation-qa.json).

All earlier source articles, raster illustrations, app source, protected ledgers and readiness reports remain unchanged. This is a local media package, not a public upload or a fresh application benchmark.
''')

storyboard = ['# Measured storyboard — full illustrated companion', '',
              'Date: October 15, 2026. Times are measured from the final assembled audio; all durations are rounded to 30 fps.', '',
              'Each chapter opens with its section name and purpose. Cards follow approximately the 30% and 63% authored-word positions within a beat. These are word-aligned visual staging cues, not a claim that every individual graphic is semantically timed to a named word.', '',
              '| Beat | Master start | End | Speech interval | Visual operation | Status |', '|---|---|---|---|---|---|']
for b in timing['beats']:
    storyboard.append(f"| {b['id']} — {b['title']} | {label(b['start'])} | {label(b['end'])} | {label(b['audio_start'])}–{label(b['audio_end'])} | {b['layout']} | {b['status']} |")
storyboard += ['', '## Animated reference summaries', '', '| Reference | Source beats |', '|---|---|']
for r in package['references']:
    storyboard.append(f"| {r['title']} | {', '.join(r['source_beats'])} |")
storyboard += ['', 'Each silent summary uses four eight-second excerpts. They are editorial summaries of chapter motion, with original complete diagrams linked separately. Exact payloads, formulas and wider experimental qualifications remain available in the source article and worked examples.']
(DOC / 'storyboard.md').write_text('\n'.join(storyboard) + '\n')

assets = []
source_paths = ['eval/ai-system-design/publication/figures/01-evidence-to-decisions.png',
                'eval/ai-system-design/publication/v2/figures/01-two-ai-phases.png',
                'eval/ai-system-design/publication/v2/figures/02-data-through-classification.png',
                'docs/design/logo-variants-20261013/animated-v2/zen-loop-orbit-poster.png']
source_paths += [str(p.relative_to(ROOT)) for p in sorted((ROOT / 'eval/ai-system-design/illustrated/figures').glob('*.png'))]
for p in source_paths:
    assets.append({'source': p, 'sha256': sha(ROOT / p),
                   'use': 'Read-only original illustration; selected browser composition or reference copy. Some inherited assets are preloaded but not displayed.'})
for r in package['references']:
    copy = OUT / r['figure']
    original = ROOT / 'eval/ai-system-design/illustrated/figures' / copy.name
    assert sha(copy) == sha(original)
save(DOC / 'assets-manifest.json', {'assets': assets, 'reference_copies': 'Eight source PNGs copied byte-for-byte',
                                   'new_image_generation_requests': 0, 'new_video_generation_service_calls': 0,
                                   'animation': 'Code-native SVG paper cards, illustrations, request tokens, highlights, receipts, metrics and state changes',
                                   'font': 'Locally installed Chalkboard; font binary not distributed'})

low = min(len(b['text'].split()) / (b['audio_end'] - b['audio_start']) * 60 for b in timing['beats'])
high = max(len(b['text'].split()) / (b['audio_end'] - b['audio_start']) * 60 for b in timing['beats'])
validation = f'''# Full animated companion — validation

Date: October 15, 2026. Result: **{status}**.

Authorization: the user requested the remaining animated videos, with slower pacing and announced sections that introduce each topic and its purpose. The original pilot, articles, diagrams, app and readiness records were preserved. No public publishing was requested or performed.

## Delivered media

| Property | Result |
|---|---|
| Complete companion | {package['duration_label']} / {timing['duration']:.3f} seconds |
| Picture | 1920×1080, 30 fps, {media['frames']:,} frames |
| Encoding | H.264 / YUV420p / AAC; fast-start MP4 |
| Master file | {media['master_bytes']:,} bytes |
| Standalone narrated chapters | 18, each with a spoken section name and purpose |
| Slower product overview | {package['chapters'][0]['duration_label']}; chapter one also exported separately |
| Additional references | Eight silent 32-second animated summaries plus complete original figures |
| Narration | AI-generated Cedar, speed configuration 0.82, calm delivery |
| Script | {len(timing['words']):,} words |
| Mean pace over speech intervals | {timing['measured_spoken_wpm']:.2f} words/minute |
| Individual beat pace range | {low:.1f}–{high:.1f} words/minute; the mean is not a per-sentence guarantee |
| Reading holds | ≥3.5 seconds per result; introductions receive an extra four seconds |
| Caption cues | {package['master_caption_cues']} master VTT/SRT cues; separate chapter captions |
| Integrated loudness | {media['audio_lufs']:.2f} LUFS |
| True peak | {media['audio_true_peak_dbtp']:.2f} dBTP |
| Full master decode | PASS; every frame and audio stream decoded |
| Preserved files | {media['preservation']['protected_files']} unchanged |

The mean spoken pace is about fourteen percent slower than the original pilot's 125.7 words/minute. Whole-video pace also includes section and reading holds. The resulting runtime is longer than the earlier proposal's estimate; content is chaptered rather than compressed into a faster fixed-length film.

## Timing, repairs and voice consistency

Seven coherent Cedar takes used identical voice, model, speed and delivery instructions. Two word-timing requests covered those takes. Alignment caught an omitted context passage and missing augmentation passages. One combined targeted take restored those five beats; a further alignment request checked the repair. Raw original responses, the repair and timing metadata remain under ignored `demo/work/article-animation-full/`.

The final 3,760 caption words exactly preserve the authored script order. Thirty-eight individual words use neighboring ASR envelopes after number/acronym normalization; they are not described as exact recognized word boundaries. The poor raw take alignment that triggered repair is retained for provenance and is not presented as the final narration's quality score.

Approximately {sum(b['sentence_pause_seconds_added'] for b in timing['beats']):.2f} seconds of silence were inserted at existing sentence boundaries. Every voiced PCM sample in the selected passages is preserved; pitch and speech speed were not digitally stretched. One-second visual leads, result holds and longer introduction holds are added outside the narration. Loudness normalization applies a common measured gain strategy before AAC encoding.

All seventy-four beat layouts passed font loading and text-bound checks. Cards reveal at staged word positions; request tokens, phrase scoring and receipt transitions provide motion beyond the original diagram images. Four encoded-region comparisons verify visible keyword, request, receipt and reservation changes after encoding; see [motion QA](../../../../demo/article-animation-full/motion-qa.json). This establishes visible change, not comprehension. The renderer samples active motion intervals at 30 fps and holds a rendered frame during deliberate reading pauses; the final output is constant 30 fps. Original raster illustrations are never rewritten.

See [synchronization QA](../../../../demo/article-animation-full/sync-qa.json), [media QA](../../../../demo/article-animation-full/media-qa.json) and the [measured storyboard](storyboard.md). Automated alignment, audio meters and muted playback do not establish listener preference, accent consistency or comprehension. Those remain editorial review judgments.

## Player and encoded-media verification

Player status: **{player['status']}**. The installed Chrome check covers master playback/pause, full screen, caption controls, optional pace, all eighteen chapter files, all eight silent summaries, overview selection, master seeking with current-topic updates, and desktop/phone layout. HTTP byte ranges support seeking; out-of-package paths are denied. No external requests are needed for playback.

The master was fully decoded and matched all {media['frames']:,} expected frames. Every standalone chapter/reference received a header, duration, stream-presence and last-second decode check. Standalone chapters copy the already decoded master source video; the player also checks their opening-frame decode. This is the stated verification scope rather than a claim of independent full decoding of each duplicate export.

## Content, coverage and limitations

The source map covers all twenty academic article sections and twenty-four mechanism-inventory rows across eighteen chapters. The narrative follows Orion's source evidence, RAKE phrases, taxonomy discovery, lexical candidates, augmented request, structured answer, human review and durable receipt. It explains privacy, counterexamples, automatic thresholds, fences, exact request counting, reservations, tokenomics and evaluation separately.

The six candidate scores, four chosen IDs, E1 evidence, historical token counts and small-benchmark results remain grounded in the preserved worked examples and article. Discovery output and classification registry are separate historical fixtures. Libraries sharing a framework are not presented as the same initiative. Current implementation, historical measurements, offline BM25 comparisons, illustrative actions and future experiments are labeled.

Dense retrieval, reranking, contextual retrieval, agentic/adaptive RAG and Jev remain research options rather than claimed implemented features. No new Jev experiment, taxonomy/classification run, repository access check, GitHub login, AWS operation or app regression suite was performed for this media change. Historical results are explained, not rerun. Large exact payloads and formulas remain in the source article and worked examples.

The eight silent reference summaries use four excerpts each; they are navigation aids rather than exhaustive animation of every original diagram label. All eight original illustrations are available alongside them, copied byte-for-byte.

## Provider accounting

This revision used **{media['provider_http_requests_new']} HTTP requests**: seven narration takes, two alignment batches, one targeted repair take and one repair alignment. All succeeded. Including the pilot, animation totals **{media['provider_http_requests_including_pilot']} requests** and **${media['retained_reservations_including_pilot_usd']:.2f} retained conservative reservations** under the shared sixteen-request/$2 animation allowance.

The new revision accounts for ${media['retained_reservations_new_usd']:.2f}. Its recorded admission snapshot plus these reservations is approximately **${current_budget:.6f}** under the existing $5 cumulative ceiling. Binary speech responses do not reconcile invoice usage; these are retained bounds, not a billed-cost assertion. Prior ledgers were not reset. Only the fixed public/synthetic narration and its generated audio went to speech/timing endpoints. No private repository content was sent.

## Preservation and local reproducibility

The pre-production baseline confirms **{media['preservation']['protected_files']} files unchanged**, including prior article editions, original diagrams, pilot/full demo media, readiness reports and protected accounting data. All new work is confined to `demo/article-animation-full/`, `demo/tools/article-animation-full/`, `eval/ai-system-design/animation/full/` and ignored media intermediates. [Preservation audit](preservation-qa.json), [asset manifest](assets-manifest.json) and [export checksums](../../../../demo/article-animation-full/checksums.json).

See the [media guide](../../../../demo/article-animation-full/README.md) for local restart/render commands. Further media generation or public upload is outside this completed local production. The original pilot and its documentation remain historical records, including their earlier statements that a full version was deferred.
'''
(DOC / 'validation.md').write_text(validation)
# The package copy uses links valid from the package rather than the documentation tree.
copy_validation = validation.replace('../../../../demo/article-animation-full/', '').replace('(storyboard.md)', '(../../eval/ai-system-design/animation/full/storyboard.md)').replace('(preservation-qa.json)', '(../../eval/ai-system-design/animation/full/preservation-qa.json)').replace('(assets-manifest.json)', '(../../eval/ai-system-design/animation/full/assets-manifest.json)')
(OUT / 'validation.md').write_text(copy_validation)
media['status'] = 'PASS' if player['status'] == 'PASS' else 'PASS_MEDIA_PENDING_PLAYER'
save(OUT / 'media-qa.json', media)
files = [p for p in OUT.rglob('*') if p.is_file() and p.name != 'checksums.json']
save(OUT / 'checksums.json', {'algorithm': 'sha256', 'files': [{'file': str(p.relative_to(OUT)), 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in sorted(files)]})
print(json.dumps({'status': status, 'chapters': len(package['chapters']), 'references': len(package['references']),
                  'exported_files': len(files), 'coverage_mechanisms': len(coverage['mechanisms']),
                  'conservative_cumulative_usd': round(current_budget, 6)}, indent=2))
