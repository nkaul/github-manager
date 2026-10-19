"""Isolated offline feasibility experiment; no provider, installs or app writes.

Select 3 development repositories per sampling domain without label access.
Persist complete source bytes, source-coordinate chunks and extractive packets.
Compare candidate recall against unapproved agent references, never gold accuracy.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import socket
import sqlite3
import sys
import time
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / 'backend'))
from markdown_it import MarkdownIt
from app.demo.evidence import build_profile
from app.pretest.ai.evidence import Retriever

DATA = ROOT / 'docs/validation/private/corpus-600'
OUT = DATA / 'non-llm-pilot-v1'
SEED = 'non-llm-feasibility-v1'
PURPOSE = re.compile(r'overview|about|purpose|introduction|what is|getting started|features', re.I)
CONSTRAINT = re.compile(r'\b(?:not|without|never|planned|roadmap|deprecated|superseded|experimental|no longer)\b', re.I)
RELATION = re.compile(r'\b(?:plugin for|connector for|integration with|part of|built on|built with|based on|provides|designed to|framework|library|platform)\b', re.I)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')
    path.chmod(0o600)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def blocks(source, raw):
    """Verbatim Markdown spans, not generated paraphrases or claims."""
    text = raw.decode('utf-8', errors='replace')
    lines = text.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    result, seen = [], set()
    heading = 'TITLE'
    for token in MarkdownIt('commonmark').parse(text):
        if token.type == 'inline' and token.map:
            start, end = token.map
            if start < len(lines) and lines[start].lstrip().startswith('#'):
                heading = token.content
            if (start, end) in seen:
                continue
            seen.add((start, end))
            passage = ''.join(lines[start:end])
            if len(passage.strip()) < 35:
                continue
            result.append({'path': source['path'], 'source_sha256': source['sha256'],
                           'role': source['role'], 'heading': heading, 'text': passage,
                           'start_line': start + 1, 'end_line': end,
                           'start_character': offsets[start], 'end_character': offsets[end]})
    return result


def packet(source_blocks, metadata):
    candidates = []
    for i, block in enumerate(source_blocks):
        text = block['text']
        # Fixed source-independent heuristics; no label or registry input.
        score = (4 if block['role'] == 'README' else 0)
        score += 4 if PURPOSE.search(block['heading']) else 0
        score += 3 if RELATION.search(text) else 0
        score += 2 if CONSTRAINT.search(text) else 0
        score += 2 if block['start_line'] <= 40 else 0
        if re.search(r'license|contribut|sponsor|install', block['heading'], re.I):
            score -= 6
        candidates.append((score, i, block))
    candidates.sort(key=lambda item: (-item[0], item[1]))
    picked, used, total = [], set(), 0

    def add(item, slot):
        nonlocal total
        _, i, block = item
        # Oversized spans stay searchable in the ledger; never silently truncate.
        if i in used or len(block['text']) > 2200 or total + len(block['text']) > 6000:
            return
        picked.append({**block, 'slot': slot})
        total += len(block['text'])
        used.add(i)

    for slot, predicate, limit in [
        ('PURPOSE_OR_CAPABILITY', lambda b: b['role'] == 'README', 3),
        ('CONSTRAINT_OR_MATURITY_CUE', lambda b: bool(CONSTRAINT.search(b['text'])), 2),
        ('RELATIONSHIP_CUE', lambda b: bool(RELATION.search(b['text'])), 2),
    ]:
        before = len(picked)
        for item in candidates:
            if predicate(item[2]):
                add(item, slot)
            if len(picked) - before >= limit:
                break
    return {'status': 'EXTRACTIVE_UNVERIFIED_NOT_COMPLETE_SEMANTIC_KNOWLEDGE',
            'metadata': metadata, 'passages': picked, 'characters': total,
            'eligible_markdown_blocks': len(source_blocks),
            'limits': 'English-heavy fixed heuristics; cue flags are not relation, negation or entailment verdicts. Complete source retained separately.'}


def signal(text, term, kind='TOPIC'):
    """Deliberately narrow English weak-label baseline, allowing abstention."""
    match = re.search(r'(?<!\w)' + re.escape(term) + r'(?!\w)', text, re.I)
    if not match:
        return 'ABSTAIN'
    lower = text.casefold()
    if re.search(r'\bplanned\b|\broadmap\b|\bfuture release\b', lower):
        return 'PLANNED_ONLY'
    if re.search(r'\bnot\b.{0,20}\b(?:much|primarily|necessarily|only)\b', lower):
        return 'ABSTAIN'
    prefix = lower[max(0, match.start() - 60):match.start()]
    if re.search(r'\balternative to\s*$', prefix):
        return 'ALTERNATIVE_NOT_MEMBERSHIP'
    if re.search(r'\b(?:not|no|without|never)\b', prefix):
        return 'NEGATIVE_HINT'
    if kind == 'PROJECT':
        return 'RELATIONSHIP_HINT' if re.search(r'\b(?:plugin for|connector for|part of)\s*$', prefix) else 'ABSTAIN'
    if re.search(r'\b(?:supports?|provides?|implements?|includes?|using|built with)\b', prefix):
        return 'POSITIVE_HINT'
    return 'ABSTAIN'


def controls():
    # Authored controls, not human-reviewed corpus labels or a universal NLP test.
    cases = [
        ('Supports payments.', 'payments', 'TOPIC', 'POSITIVE_HINT'),
        ('Does not support payments.', 'payments', 'TOPIC', 'NEGATIVE_HINT'),
        ('Payments are planned for a future release.', 'payments', 'TOPIC', 'PLANNED_ONLY'),
        ('A plugin for OpenMM.', 'OpenMM', 'PROJECT', 'RELATIONSHIP_HINT'),
        ('An alternative to Keycloak.', 'Keycloak', 'PROJECT', 'ALTERNATIVE_NOT_MEMBERSHIP'),
        ('A simulator using PyTorch.', 'PyTorch', 'PROJECT', 'ABSTAIN'),
        ('Does not do much analysis.', 'analysis', 'TOPIC', 'ABSTAIN'),
        ('Supports not only payments but also billing.', 'payments', 'TOPIC', 'ABSTAIN'),
        ('Does not lack payments.', 'payments', 'TOPIC', 'POSITIVE_HINT'),
        ('No Docker is required; this service provides payments.', 'payments', 'TOPIC', 'POSITIVE_HINT'),
        ('Payments are not implemented.', 'payments', 'TOPIC', 'NEGATIVE_HINT'),
        ('Este projeto suporta pagamentos.', 'payments', 'TOPIC', 'POSITIVE_HINT'),
    ]
    return [{'text': t, 'term': term, 'kind': kind, 'expected': expected,
             'actual': signal(t, term, kind), 'matched_expected': signal(t, term, kind) == expected}
            for t, term, kind, expected in cases]


def main():
    global OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', default='non-llm-pilot-v1')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}', args.run_id):
        parser.error('run-id must be a simple local folder name')
    OUT = DATA / args.run_id
    # Runtime provider/network calls are forbidden even if accidentally introduced.
    network_calls = []

    def forbidden(*args, **kwargs):
        network_calls.append('blocked')
        raise RuntimeError('Offline experiment forbids network access')

    socket.socket.connect = forbidden
    socket.socket.connect_ex = forbidden
    started = time.monotonic()
    OUT.mkdir(parents=True, exist_ok=True)
    OUT.chmod(0o700)
    inventory = read_jsonl(DATA / 'release/inventory.jsonl')
    chosen = []
    for domain in sorted({r['sampling_domain'] for r in inventory}):
        pool = [r for r in inventory if r['sampling_domain'] == domain and r['split'] == 'development']
        pool.sort(key=lambda r: sha((SEED + str(r['repository_id'])).encode()))
        chosen.extend(pool[:3])
    assert len(chosen) == 30
    inputs = {r['id']: r for r in read_jsonl(DATA / 'release/inputs.jsonl')}
    registry = json.loads((DATA / 'release/registry.proposed.json').read_text())
    methods = {
        'current_app_tfidf': Retriever(registry, method='tfidf'),
        'full_sources_tfidf': Retriever(registry, method='tfidf'),
        'extractive_packet_tfidf': Retriever(registry, method='tfidf'),
        'extractive_packet_bm25': Retriever(registry, method='bm25'),
    }
    dbpath = OUT / 'evidence.sqlite3'
    if dbpath.exists():
        raise RuntimeError('Preserve prior experiment; choose a new output version instead of overwriting')
    db = sqlite3.connect(dbpath)
    dbpath.chmod(0o600)
    db.executescript('CREATE TABLE sources(id INTEGER PRIMARY KEY, repository_id INTEGER, path TEXT, commit_sha TEXT, sha256 TEXT, raw BLOB); CREATE VIRTUAL TABLE chunks USING fts5(repository_id UNINDEXED, path UNINDEXED, start_line UNINDEXED, end_line UNINDEXED, body);')
    predictions, packets, snapshots = {}, [], []
    file_count = byte_count = chunk_count = roundtrip = 0
    # Labels are loaded only after every feature packet and prediction is built.
    for item in chosen:
        rid = item['repository_id']
        record = json.loads((ROOT / item['dossier_path']).read_text())
        sources = [record['readme'], *record.get('supporting_files', [])]
        raw_readme = (ROOT / record['readme']['local_path']).read_bytes()
        baseline = build_profile(inputs[rid], raw_readme.decode('utf-8', errors='replace'))
        all_blocks, full_text = [], []
        for source in sources:
            raw = (ROOT / source['local_path']).read_bytes()
            assert sha(raw) == source['sha256']
            assert hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() == source['git_blob_sha']
            cur = db.execute('INSERT INTO sources(repository_id,path,commit_sha,sha256,raw) VALUES(?,?,?,?,?)', (rid, source['path'], record['commit'], source['sha256'], raw))
            restored = db.execute('SELECT raw FROM sources WHERE id=?', (cur.lastrowid,)).fetchone()[0]
            assert restored == raw
            file_count += 1
            roundtrip += 1
            byte_count += len(raw)
            text = raw.decode('utf-8', errors='replace')
            full_text.append(text)
            lines = text.splitlines(keepends=True)
            covered = set()
            for a in range(0, len(lines), 20):
                b = min(a + 30, len(lines))
                db.execute('INSERT INTO chunks VALUES(?,?,?,?,?)', (str(rid), source['path'], a + 1, b, ''.join(lines[a:b])))
                covered.update(range(a, b))
                chunk_count += 1
            assert len(covered) == len(lines)
            if Path(source['path']).suffix.casefold() in {'.md', '.markdown', '.rst', '.txt'} or source['role'] == 'README':
                all_blocks.extend(blocks(source, raw))
        summary = packet(all_blocks, baseline['evidence'][0]['text'])
        source_map = {f['path']: f for f in sources}
        for block in summary['passages']:
            original = (ROOT / source_map[block['path']]['local_path']).read_bytes().decode('utf-8', errors='replace')
            assert original[block['start_character']:block['end_character']] == block['text']
        feature_packet = {'evidence': [baseline['evidence'][0], *[{'id': 'S' + str(i), 'text': b['text']} for i, b in enumerate(summary['passages'])]]}
        full_profile = {'evidence': [baseline['evidence'][0], {'id': 'ALL_SOURCE_REFERENCE_ONLY', 'text': '\n'.join(full_text)}]}
        features = {'current_app_tfidf': baseline, 'full_sources_tfidf': full_profile,
                    'extractive_packet_tfidf': feature_packet, 'extractive_packet_bm25': feature_packet}
        predictions[rid] = {method: retriever.candidates(features[method]) for method, retriever in methods.items()}
        packets.append({'repository_id': rid, 'repository': item['full_name'], 'split': 'development',
                        'packet': summary, 'baseline_profile_characters': sum(len(e['text']) for e in baseline['evidence']),
                        'all_source_characters': sum(map(len, full_text)), 'predictions': predictions[rid]})
        snapshots.append({'repository_id': rid, 'name': item['full_name'], 'sampling_domain': item['sampling_domain'],
                          'commit': record['commit'], 'sources': [{k: f[k] for k in ['path', 'role', 'sha256', 'git_blob_sha', 'bytes']} for f in sources]})
    db.commit()
    # Parameterized FTS retrieval smoke test using a term actually present.
    probe = db.execute('SELECT body FROM chunks WHERE chunks MATCH ? LIMIT 1', ('"python"',)).fetchone()
    db.close()
    labels = {r['repository_id']: r for r in read_jsonl(DATA / 'release/labels.proposed.jsonl')}
    counts = {method: defaultdict(Counter) for method in methods}
    rows = []
    for item in chosen:
        rid = item['repository_id']
        expected = [l for l in labels[rid]['labels'] if l.get('decision', 'SUPPORTED') == 'SUPPORTED']
        for method in methods:
            for label in expected:
                counts[method][label['kind']]['positives'] += 1
                counts[method][label['kind']]['found'] += label['id'] in predictions[rid][method]
            rows.append({'repository_id': rid, 'method': method,
                         'candidate_ids': predictions[rid][method],
                         'missing_proposed_positive_ids': [l['id'] for l in expected if l['id'] not in predictions[rid][method]]})
    metrics = {method: {kind: {**values, 'positive_recall': values['found'] / values['positives'] if values['positives'] else None}
                        for kind, values in by_kind.items()} for method, by_kind in counts.items()}
    tests = controls()
    result = {'status': 'OFFLINE_FEASIBILITY_NOT_HUMAN_ACCURACY', 'sample': 30,
              'selection': '3 per sampling domain, development only, fixed SHA256 order; selection does not read labels',
              'seed': SEED, 'files': file_count, 'retained_bytes': byte_count, 'source_roundtrips': roundtrip,
              'indexed_chunks': chunk_count, 'all_source_lines_indexed': True, 'fts_probe_found': bool(probe),
              'source_bound_extractive_passages': sum(len(p['packet']['passages']) for p in packets),
              'candidate_limits_per_kind': Retriever.LIMITS, 'proxy_positive_recall': metrics,
              'language_controls': {'cases': len(tests), 'matched_expected': sum(t['matched_expected'] for t in tests), 'results': tests},
              'network_attempts': len(network_calls), 'provider_calls': 0, 'model_downloads': 0,
              'new_packages': 0, 'human_approved_references': 0, 'seconds': round(time.monotonic() - started, 3),
              'producer_script_sha256': sha(Path(__file__).read_bytes()),
              'corpus_manifest_sha256': sha((DATA / 'release/manifest.local.json').read_bytes()),
              'limits': 'References/registry were agent-proposed with corpus access. No precision/F1, semantic-comprehension or near-human quality claim. Larger multi-document inputs and 6000-character packets differ from production payloads and incur unmeasured downstream token cost. English cue rules fail on scope, double negation and translation. Code and interpretation are Codex-authored; the runtime experiment invokes no LLM.'}
    save(OUT / 'result.local.json', result)
    save(OUT / 'packets.local.json', packets)
    save(OUT / 'source-manifest.local.json', snapshots)
    save(OUT / 'retrieval.local.json', rows)
    print(json.dumps({k: v for k, v in result.items() if k != 'language_controls'}, indent=2))
    print('language controls', sum(t['matched_expected'] for t in tests), '/', len(tests))


if __name__ == '__main__':
    main()
