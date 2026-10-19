"""Offline consistency check of source citations and recorded semantic reading.

Producers record whole-line, line-character or global-character intervals.
This verifies their records, not comprehension or human reference approval.
"""
import json
from pathlib import Path

from assemble import DATA, ROOT, load_records, write_json


def coverage_mask(text, coverage):
    mask = bytearray(len(text))
    lines = text.splitlines(keepends=True)
    offsets = []
    offset = 0
    for line in lines:
        offsets.append(offset)
        offset += len(line)

    def mark(start, end):
        if not 0 <= start <= end <= len(text):
            raise ValueError('Reading character interval outside source')
        mask[start:end] = b'\1' * (end - start)

    for start, end in coverage.get('intervals', coverage.get('read_line_intervals', [])):
        if not 1 <= start <= end <= len(lines):
            raise ValueError('Reading line interval outside source')
        mark(offsets[start - 1], offsets[end - 1] + len(lines[end - 1]))
    for start, end in coverage.get('character_intervals', []):
        mark(start, end)
    for interval in coverage.get('line_character_intervals', []):
        line = interval['line']
        if not 1 <= line <= len(lines):
            raise ValueError('Reading line outside source')
        start, end = interval['start_char'], interval['end_char']
        if not 0 <= start <= end <= len(lines[line - 1]):
            raise ValueError('Reading line-character interval outside source line')
        mark(offsets[line - 1] + start, offsets[line - 1] + end)
    return mask


def quote_is_read(text, quote, mask):
    # Whitespace between displayed passages is not a comprehension claim.
    # A repeated passage can be supported by any actually read occurrence.
    if not quote.strip():
        return False
    start = text.find(quote)
    while start >= 0:
        if all(char.isspace() or mask[start + i] for i, char in enumerate(quote)):
            return True
        start = text.find(quote, start + 1)
    return False


def source_evidence(value, files):
    if isinstance(value, dict):
        if value.get('quote') and value.get('path') in files:
            yield value
        for child in value.values():
            yield from source_evidence(child, files)
    elif isinstance(value, list):
        for child in value:
            yield from source_evidence(child, files)


def audit(records):
    issues = []
    quotes = checked = 0
    for record in records:
        files = {f['path']: f for f in [record['readme'], *record.get('supporting_files', [])]}
        scope = record.get('agent_read_coverage', {})
        coverage = {f['path']: f for f in scope.get('files', [])}
        coverage.update({path: value for path, value in scope.get('source_intervals', {}).items() if value})
        texts, masks = {}, {}
        for path, item in coverage.items():
            checked += 1
            source = files.get(path)
            if not source:
                issues.append({'id': record['numeric_id'], 'path': path, 'reason': 'READING_PATH_NOT_SOURCE'})
                continue
            text = (ROOT / source['local_path']).read_bytes().decode('utf-8', errors='replace')
            texts[path] = text
            try:
                masks[path] = coverage_mask(text, item)
            except ValueError as error:
                issues.append({'id': record['numeric_id'], 'path': path, 'reason': str(error)})
            expected = item.get('sha256') or item.get('source_sha256')
            if expected and expected != source['sha256']:
                issues.append({'id': record['numeric_id'], 'path': path, 'reason': 'READING_HASH_MISMATCH'})
        for evidence in source_evidence(record['annotations'], files):
            quotes += 1
            path = evidence['path']
            text = texts.get(path)
            if text is None:
                text = (ROOT / files[path]['local_path']).read_bytes().decode('utf-8', errors='replace')
            if not quote_is_read(text, evidence['quote'], masks.get(path, bytearray(len(text)))):
                issues.append({'id': record['numeric_id'], 'path': path, 'reason': 'QUOTE_OUTSIDE_RECORDED_SEMANTIC_READING', 'quote': evidence['quote'][:80]})
    return {'status': 'PASS' if not issues else 'ISSUES', 'records': len(records),
            'quoted_source_evidence_items': quotes, 'reading_file_records': checked, 'issues': issues,
            'limits': 'Checks quoted source characters against whole-line, line-character and global-character reading intervals. Whitespace separators are ignored. This verifies recorded scope, not independent comprehension; citation coordinates and byte integrity are separately audited by assemble.py.'}


if __name__ == '__main__':
    records, _ = load_records()
    result = audit(records)
    write_json(DATA / 'release/read-coverage-audit.local.json', result)
    print(json.dumps({key: value for key, value in result.items() if key != 'issues'}, indent=2))
    print('issues', len(result['issues']))
    if result['issues']:
        raise SystemExit(1)
