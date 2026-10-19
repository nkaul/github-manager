"""Local assembly, captions, silent reference summaries and media verification.

No provider calls. Source illustrations, earlier media and application state are read-only.
"""
import argparse
import hashlib
import json
import sys
import re
import shutil
import subprocess
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "eval/relocation"))
from relocation_support import historical_bytes, historical_sha256, repo_path
OUT = ROOT / 'demo/article-animation-full'
WORK = ROOT / 'demo/work/article-animation-full'
DOC = ROOT / 'eval/ai-system-design/animation/full'
FF = ROOT / '.tools/video-python/imageio_ffmpeg/binaries/ffmpeg-macos-x86_64-v7.1'
TIMING = json.loads((OUT / 'timing.json').read_text())
STORY = json.loads((Path(__file__).parent / 'story.json').read_text())

REFERENCES = [
    ('01-actual-system', 'The local system and its boundaries', ['03-context-01', '03-context-04', '01-purpose-03', '03-context-03']),
    ('02-retrieval-and-generation', 'Retrieval, request and decision', ['07-retrieval-01', '07-retrieval-03', '08-augmentation-04', '09-generation-02']),
    ('03-evidence-and-chunking', 'Evidence, phrases and provenance', ['04-evidence-01', '04-evidence-02', '05-keywords-02', '04-evidence-03']),
    ('04-controlled-analysis-loop', 'Controlled loops and durable receipts', ['12-loops-01', '11-memory-02', '12-loops-02', '12-loops-03']),
    ('05-harness-and-tokenomics', 'Admission, reservations and tokenomics', ['13-harness-01', '13-harness-02', '13-harness-03', '14-tokenomics-02']),
    ('06-evaluation-evidence', 'Evaluate the layers separately', ['15-evaluation-01', '15-evaluation-02', '15-evaluation-03', '15-evaluation-04']),
    ('07-contextual-retrieval-comparison', 'Contextual retrieval and future choices', ['16-future-retrieval-01', '16-future-retrieval-03', '16-future-retrieval-04', '16-future-retrieval-05']),
    ('08-future-experiment-roadmap', 'A measured research roadmap', ['17-jev-01', '16-future-retrieval-02', '17-jev-04', '18-complete-trace-04']),
]


def save(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2) + '\n')


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for data in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def ff(args):
    p = subprocess.run([str(FF), '-hide_banner', '-nostdin', *map(str, args)], capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode(errors='replace')[-3000:])
    return p


def stamp(t, comma=False):
    n = max(0, round(t * 1000))
    return f"{n // 3600000:02}:{n // 60000 % 60:02}:{n // 1000 % 60:02}{',' if comma else '.'}{n % 1000:03}"


def duration_label(seconds):
    seconds = round(seconds)
    return f'{seconds // 60}:{seconds % 60:02}'


def concat_list(name, beats):
    p = WORK / (name + '.ffconcat')
    rows = ['ffconcat version 1.0']
    for b in beats:
        source = str(WORK / 'clips' / (b['id'] + '.mp4')).replace("'", "'\\''")
        rows.append(f"file '{source}'")
    p.write_text('\n'.join(rows) + '\n')
    return p


def captions(name, words, offset=0):
    groups, current = [], []
    for word in words:
        if current and (current[0]['beat'] != word['beat'] or
                        len(' '.join(w['word'] for w in current) + ' ' + word['word']) > 66 or
                        len(current) >= 9 or word['start'] - current[0]['start'] > 4.5 or
                        word['start'] - current[-1]['end'] > .6):
            groups.append(current)
            current = []
        current.append(word)
        if re.search(r'[.!?]$', word['word']):
            groups.append(current)
            current = []
    if current:
        groups.append(current)
    rows = []
    for i, group in enumerate(groups):
        start = max(0, group[0]['start'] - offset)
        end = max(start + .12, group[-1]['end'] - offset)
        if i + 1 < len(groups):
            end = min(end, max(start + .03, groups[i + 1][0]['start'] - offset))
        rows.append((start, end, ' '.join(w['word'] for w in group)))
    base = OUT / name
    base.parent.mkdir(parents=True, exist_ok=True)
    base.with_suffix('.vtt').write_text('WEBVTT\n\n' + '\n\n'.join(f'{stamp(a)} --> {stamp(b)}\n{s}' for a, b, s in rows) + '\n')
    base.with_suffix('.srt').write_text('\n\n'.join(f'{i}\n{stamp(a, True)} --> {stamp(b, True)}\n{s}' for i, (a, b, s) in enumerate(rows, 1)) + '\n')
    assert ' '.join(s for _, _, s in rows).split() == [w['word'] for w in words]
    assert all(a < b for a, b, _ in rows)
    return len(rows)


def assemble():
    render = json.loads((WORK / 'render.json').read_text())
    expected_frames = sum(b['frames'] for b in TIMING['beats'])
    assert render['status'] == 'PASS' and len(render['results']) == len(TIMING['beats'])
    assert render['total_frames'] == expected_frames
    (OUT / 'chapters').mkdir(exist_ok=True)
    (OUT / 'references').mkdir(exist_ok=True)
    (OUT / 'figures').mkdir(exist_ok=True)
    fingerprint = hashlib.sha256(((OUT / 'timing.json').read_text() + (WORK / 'render.json').read_text()).encode()).hexdigest()
    old_path = WORK / 'assembly-state.json'
    old = json.loads(old_path.read_text()) if old_path.exists() else {}
    completed = set(old.get('completed', [])) if old.get('fingerprint') == fingerprint else set()

    def done(name):
        completed.add(name)
        save(old_path, {'fingerprint': fingerprint, 'completed': sorted(completed)})

    norm_file = WORK / 'normalization.json'
    if 'normalization' not in completed:
        analysis = ff(['-i', WORK / 'aligned.wav', '-af', 'loudnorm=I=-16:TP=-2:LRA=11:print_format=json', '-f', 'null', '-']).stderr.decode()
        levels = json.JSONDecoder().raw_decode(analysis[analysis.rfind('{'):])[0]
        save(norm_file, levels)
        done('normalization')
    levels = json.loads(norm_file.read_text())
    norm = (f"loudnorm=I=-16:TP=-2:LRA=11:measured_I={levels['input_i']}:measured_TP={levels['input_tp']}:"
            f"measured_LRA={levels['input_lra']}:measured_thresh={levels['input_thresh']}:offset={levels['target_offset']}:linear=true")

    def narrated(name, beats, start, duration):
        file = OUT / (name + '.mp4')
        if name not in completed or not file.exists():
            source = concat_list(name.replace('/', '-'), beats)
            ff(['-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', source,
                '-ss', f'{start:.9f}', '-i', WORK / 'aligned.wav', '-map', '0:v:0', '-map', '1:a:0',
                '-c:v', 'copy', '-af', norm, '-ar', '48000', '-c:a', 'aac', '-b:a', '160k',
                '-t', f'{duration:.9f}', '-movflags', '+faststart', file])
            done(name)
        print('Assembled', name, duration_label(duration), flush=True)

    narrated('complete-1080p', TIMING['beats'], 0, TIMING['duration'])
    ff(['-loglevel', 'error', '-y', '-i', OUT / 'complete-1080p.mp4', '-vn', '-c:a', 'copy', OUT / 'narration.m4a'])
    master_cues = captions('complete', TIMING['words'])
    package = {'title': 'GitHub Manager · illustrated AI system design', 'date': '2026-10-15',
               'duration': TIMING['duration'], 'duration_label': duration_label(TIMING['duration']),
               'voice': 'AI-generated Cedar', 'spoken_wpm': TIMING['measured_spoken_wpm'],
               'master': 'complete-1080p.mp4', 'master_captions': 'complete.vtt', 'chapters': [], 'references': []}
    for number, chapter in enumerate(TIMING['chapters'], 1):
        beats = [b for b in TIMING['beats'] if b['chapter_id'] == chapter['id']]
        duration = chapter['end'] - chapter['start']
        name = 'chapters/' + chapter['id']
        narrated(name, beats, chapter['start'], duration)
        words = [w for w in TIMING['words'] if w['beat'] in {b['id'] for b in beats}]
        cues = captions(name, words, chapter['start'])
        package['chapters'].append({'id': chapter['id'], 'number': number, 'title': chapter['title'],
                                   'purpose': chapter['purpose'], 'start': chapter['start'], 'end': chapter['end'],
                                   'duration': duration, 'duration_label': duration_label(duration),
                                   'file': name + '.mp4', 'captions': name + '.vtt', 'caption_cues': cues,
                                   'text': '\n\n'.join(b['text'] for b in beats)})
    shutil.copyfile(OUT / package['chapters'][0]['file'], OUT / 'overview-slower-1080p.mp4')
    shutil.copyfile(OUT / package['chapters'][0]['captions'], OUT / 'overview-slower.vtt')
    (OUT / 'empty.vtt').write_text('WEBVTT\n\n')
    lookup = {b['id']: b for b in TIMING['beats']}
    for slug, title, ids in REFERENCES:
        name = 'references/' + slug
        file = OUT / (name + '.mp4')
        if name not in completed or not file.exists():
            inputs, filters = [], []
            for i, bid in enumerate(ids):
                b = lookup[bid]
                start = 0 if b['layout'] == 'intro' else min(b['end'] - b['start'] - 8, max(0, b['reveal_times'][2] - 1.5))
                inputs += ['-ss', f'{start:.9f}', '-t', '8', '-i', WORK / 'clips' / (bid + '.mp4')]
                filters.append(f'[{i}:v]setpts=PTS-STARTPTS[v{i}]')
            filters.append(''.join(f'[v{i}]' for i in range(4)) + 'concat=n=4:v=1:a=0[out]')
            ff(['-loglevel', 'error', '-y', *inputs, '-filter_complex', ';'.join(filters), '-map', '[out]',
                '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p',
                '-threads', '2', '-r', '30', '-frames:v', '960', '-movflags', '+faststart', file])
            done(name)
        figure = ROOT / 'eval/ai-system-design/illustrated/figures' / (slug + '.png')
        shutil.copyfile(figure, OUT / 'figures' / figure.name)
        package['references'].append({'id': slug, 'title': title, 'file': name + '.mp4',
                                      'figure': 'figures/' + figure.name, 'duration': 32, 'duration_label': '0:32',
                                      'source_beats': ids, 'silent': True})
        print('Assembled silent reference', slug, flush=True)
    ff(['-loglevel', 'error', '-y', '-ss', '6', '-i', OUT / 'complete-1080p.mp4', '-frames:v', '1', OUT / 'poster.png'])
    package['master_caption_cues'] = master_cues
    save(OUT / 'package.json', package)
    save(WORK / 'assembly.json', {'status': 'PASS', 'fingerprint': fingerprint, 'normalization': levels,
                                 'chapters': len(package['chapters']), 'references': len(package['references']),
                                 'master_frames': expected_frames, 'master_caption_cues': master_cues})
    print('Assembly complete', flush=True)


def metadata(file):
    result = ff(['-i', file, '-t', '0', '-f', 'null', '-']).stderr.decode()
    assert '1920x1080' in result and '30 fps' in result and 'h264' in result, file
    d = re.search(r'Duration: (\d+):(\d+):([\d.]+)', result)
    duration = int(d[1]) * 3600 + int(d[2]) * 60 + float(d[3])
    return {'duration': duration, 'width': 1920, 'height': 1080, 'fps': 30, 'audio': 'Audio:' in result}


def verify():
    package = json.loads((OUT / 'package.json').read_text())
    master = OUT / package['master']
    expected_frames = sum(b['frames'] for b in TIMING['beats'])
    meta = metadata(master)
    assert abs(meta['duration'] - TIMING['duration']) < .1 and meta['audio']
    decode = ff(['-v', 'error', '-i', master, '-progress', 'pipe:1', '-f', 'null', '-'])
    progress = dict(re.findall(r'^(\w+)=(.*)$', decode.stdout.decode(), re.M))
    assert int(progress.get('frame', 0)) == expected_frames, progress
    assert not decode.stderr.strip(), decode.stderr.decode()[:1000]
    print('Master full decode PASS', expected_frames, 'frames', flush=True)
    audio = ff(['-i', master, '-vn', '-af', 'loudnorm=I=-16:TP=-2:LRA=11:print_format=json', '-f', 'null', '-']).stderr.decode()
    actual = json.JSONDecoder().raw_decode(audio[audio.rfind('{'):])[0]
    assert -17 <= float(actual['input_i']) <= -15
    assert float(actual['input_tp']) < -1
    records = []
    for item in package['chapters'] + package['references']:
        file = OUT / item['file']
        m = metadata(file)
        assert abs(m['duration'] - item['duration']) < .12, (file, m)
        assert m['audio'] == ('silent' not in item), (file, m)
        # Decode the end of each standalone asset to catch broken muxing or truncated files.
        ff(['-v', 'error', '-sseof', '-1', '-i', file, '-f', 'null', '-'])
        records.append({'file': item['file'], **m, 'tail_decode': 'PASS', 'bytes': file.stat().st_size})
    words = [b['text'].split() for c in STORY['chapters'] for b in c['beats']]
    assert [w for group in words for w in group] == [w['word'] for w in TIMING['words']]
    assert not TIMING['speech_time_stretch']
    assert all(b['audio_end'] < b['end'] - 3.49 for b in TIMING['beats'])
    assert all(c['beats'][0]['text'].startswith('Section ') for c in STORY['chapters'])
    repaired = [b['id'] for b in TIMING['beats'] if b.get('targeted_repair')]
    samples = []
    for bid, event in [('05-keywords-02', 2), ('08-augmentation-03', 2), ('11-memory-02', 1), ('13-harness-02', 2)]:
        beat = next(b for b in TIMING['beats'] if b['id'] == bid)
        points = [beat['reveal_times'][event] + .25, beat['reveal_times'][event] + .8]
        pictures = []
        for point in points:
            data = ff(['-v', 'error', '-ss', f'{point:.9f}', '-i', WORK / 'clips' / (bid + '.mp4'),
                       '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']).stdout
            pictures.append(np.frombuffer(data, dtype=np.uint8).reshape(1080, 1920, 3)[805:930])
        changed = int(np.count_nonzero(np.max(np.abs(pictures[0].astype(np.int16) - pictures[1].astype(np.int16)), axis=2) > 20))
        assert changed > 100, (bid, 'Expected information-carrying motion absent', changed)
        samples.append({'beat': bid, 'sample_seconds_relative': points, 'region': 'Bottom information layer y=805..930', 'changed_pixels': changed})
    save(OUT / 'motion-qa.json', {'status': 'PASS', 'encoded_samples': samples,
                                'scope': 'Representative keyword, request, receipt and reservation changes survive encoding; not a comprehension study'})
    (WORK / 'encoded-review').mkdir(exist_ok=True)
    for bid in ['03-context-01', '07-retrieval-03', '08-augmentation-02', '09-generation-02', '11-memory-02', '15-evaluation-03', '17-jev-03']:
        b = next(b for b in TIMING['beats'] if b['id'] == bid)
        point = 7 if b['layout'] == 'intro' else b['end'] - b['start'] - 2
        ff(['-v', 'error', '-y', '-ss', f'{point:.9f}', '-i', WORK / 'clips' / (bid + '.mp4'),
            '-frames:v', '1', WORK / 'encoded-review' / (bid + '.png')])
    save(OUT / 'sync-qa.json', {'status': 'PASS', 'script_words': len(TIMING['words']),
                              'caption_order': 'Exact authored word order preserved',
                              'word_timing': 'Provider transcription alignment with number/acronym normalization',
                              'neighbor_envelope_words': TIMING['neighbor_envelope_words'],
                              'targeted_repairs': repaired, 'speech_time_stretch': False,
                              'sentence_silence_added_seconds': sum(b['sentence_pause_seconds_added'] for b in TIMING['beats']),
                              'result_hold_seconds': 3.5, 'introduction_extra_hold_seconds': 4,
                              'limitation': '38 word envelopes use neighboring alignment; automated alignment is not a perceptual listening study.'})
    baseline = json.loads((DOC / 'preservation-baseline.json').read_text())
    changes = [r['file'] for r in baseline['files'] if not repo_path(r['file']).exists() or historical_sha256(repo_path(r['file'])) != r['sha256']]
    preservation = {'status': 'PASS' if not changes else 'CHANGED_REVIEW_REQUIRED', 'protected_files': len(baseline['files']), 'changed': changes}
    save(DOC / 'preservation-qa.json', preservation)
    assert not changes, changes
    manifest = json.loads((OUT / 'speech-requests.json').read_text())
    pilot = json.loads((ROOT / 'demo/article-animation/speech-requests.json').read_text())
    accounted = lambda m: sum(r.get('settled_usd', r['reserved_usd']) for r in m['requests'])
    media_total = accounted(manifest) + accounted(pilot)
    report = {'status': 'PASS_MEDIA_PENDING_PLAYER', 'date': '2026-10-15', **meta,
              'duration_seconds': TIMING['duration'], 'frames': expected_frames, 'codec': 'H.264 / AAC',
              'chapter_count': len(package['chapters']), 'reference_summaries': len(package['references']),
              'voice': 'AI-generated Cedar', 'spoken_wpm': TIMING['measured_spoken_wpm'],
              'audio_lufs': float(actual['input_i']), 'audio_true_peak_dbtp': float(actual['input_tp']),
              'full_master_decode': 'PASS; all frames and audio decoded',
              'standalone_check_scope': 'Headers, duration, stream presence and last-second decode; master covers the source chapter video',
              'standalone_assets': records, 'master_caption_cues': package['master_caption_cues'],
              'provider_http_requests_new': len(manifest['requests']),
              'provider_http_requests_including_pilot': len(manifest['requests']) + len(pilot['requests']),
              'retained_reservations_new_usd': round(accounted(manifest), 6),
              'retained_reservations_including_pilot_usd': round(media_total, 6),
              'accounting_note': 'Conservative retained reservations, not reconciled invoice charges',
              'new_repository_inference_calls': 0, 'preservation': preservation,
              'master_bytes': master.stat().st_size, 'master_sha256': sha(master),
              'perceptual_review': 'Pacing and voice preference remain for the user; muted player automation is not a listening test.'}
    assert media_total <= 2 and report['provider_http_requests_including_pilot'] <= 16
    save(OUT / 'media-qa.json', report)
    print(json.dumps({k: report[k] for k in ['status', 'frames', 'duration_seconds', 'audio_lufs', 'audio_true_peak_dbtp', 'master_bytes', 'retained_reservations_including_pilot_usd']}, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['assemble', 'verify'])
    args = parser.parse_args()
    {'assemble': assemble, 'verify': verify}[args.mode]()
