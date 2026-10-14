#!/usr/bin/env python3
"""Verify frozen readiness evidence and the historical portion of the shared ledger."""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('baseline',type=Path)
args=parser.parse_args()
baseline=args.baseline.resolve()
manifest=json.loads((baseline/'manifest.json').read_text())
protected={name:sha for name,sha in manifest.items() if (
    name.startswith(('backend/app/','backend/tests/pretest/','frontend/tests/pretest/',
                     'infrastructure/','docs/validation/'))
    or name in {'frontend/src/app/globals.css','frontend/src/lib/api.ts','backend/uv.lock',
                'frontend/package-lock.json','backend/pyproject.toml'})
    and name!='docs/validation/private/ai-pretest/runs.sqlite3'}
changed=[name for name,sha in protected.items() if not (ROOT/name).exists() or
         hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=sha]
legacy='docs/validation/private/ai-pretest/runs.sqlite3'
old=sqlite3.connect(baseline/legacy);new=sqlite3.connect(ROOT/legacy)
counts={}
for table,key in [('experiment','id'),('calls','id'),('cache','key')]:
    rows=old.execute('SELECT * FROM '+table).fetchall()
    counts[table]=len(rows)
    for row in rows:
        current=new.execute('SELECT * FROM '+table+' WHERE '+key+'=?',(row[0],)).fetchone()
        if current!=row:
            changed.append('historical-ledger:'+table+':'+str(row[0]))
old.close();new.close()
preflight=hashlib.sha256((ROOT/'frontend/src/components/Preflight.tsx').read_bytes()).hexdigest()
if preflight!=manifest['frontend/src/app/page.tsx']:
    changed.append('Preserved original Preflight.tsx')
result={'status':'PASS' if not changed else 'FAIL','protected_files':len(protected),
        'historical_rows':counts,'preflight_copy_identical':preflight==manifest['frontend/src/app/page.tsx'],
        'changes':changed,'baseline_files':len(manifest)}
print(json.dumps(result,indent=2))
raise SystemExit(bool(changed))
