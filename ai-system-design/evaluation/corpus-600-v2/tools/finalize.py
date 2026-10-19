"""Freeze the English corpus only after source, eligibility and independent audit gates."""
import hashlib
import json
import re
import sqlite3
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from assemble import DATA, ROOT, load_records, write_json, write_jsonl
from audit_read_scope import audit


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def eligibility(record):
    return record.get('v2_eligibility') or record.get('eligibility_audit') or record.get('eligibility_v2')


def local_targets(text):
    # Audit our navigation, not relative Markdown copied inside untrusted quotes.
    # A truncated source quotation may contain an unmatched Markdown parenthesis.
    for line in text.splitlines():
        if not line.startswith(('[Complete README]', '|')):
            continue
        for target in re.findall(r'\]\(([^)\n]+)\)', line):
            if not target.startswith(('http:', 'https:', '#')):
                yield target


def main():
    release=DATA/'release'
    if (release/'manifest.local.json').exists():
        raise SystemExit('Existing release is immutable. Create a new version instead of overwriting it.')
    records, excluded=load_records()
    validation=json.loads((release/'validation.local.json').read_text())
    assert len(records)==600 and validation['accepted_records']==validation['annotated_records']==600
    assert not validation['source_audit']['issues']
    assert not validation['directory_binding_audit']['issues']
    assert not validation['directory_binding_audit']['missing_directory_entries']
    assert not validation['registry_audit']['definition_conflicts']
    assert not validation['registry_audit']['alias_collisions']
    assert validation['cross_review_audit']['distinct_repositories']>=120
    assert not validation['cross_review_audit']['invalid_or_stale']
    assert validation['human_approved_records']==0
    scope=audit(records);assert not scope['issues'],scope['issues'][:10]
    write_json(release/'read-coverage-audit.local.json',scope)
    for record in records:
        decision=eligibility(record)
        assert decision and decision.get('evidence'),record['full_name']
        assert not decision.get('human_approved',False)
        assert str(decision['decision']).startswith(('RETAIN','ACCEPT','REASSIGN')),decision
        assert record.get('annotations') and not record.get('human_approved')

    # Check every file bound by the original release; do not modify the original.
    prior=ROOT/'docs/validation/private/corpus-600/release'
    old=json.loads((prior/'manifest.local.json').read_text())
    preserved=[]
    for name,binding in old['release_files'].items():
        assert sha(prior/name)==binding['sha256'],name
        preserved.append(str((prior/name).relative_to(ROOT)))
    for section in ('sources_and_dossiers_sha256','pipeline_modules_sha256','methodology_and_tools_sha256'):
        for name,expected in old[section].items():
            assert sha(ROOT/name)==expected,name
            preserved.append(name)
    write_json(release/'v1-preservation-audit.local.json',{'status':'PASS','original_release_id':old['release_id'],
        'original_manifest_sha256':sha(prior/'manifest.local.json'),'bound_files_checked':len(preserved),
        'distinct_files_checked':len(set(preserved)),'altered_files':[]})

    inventory=[json.loads(line) for line in (release/'inventory.jsonl').read_text().splitlines()]
    proposals={row['repository_id']:row for row in map(json.loads,(release/'labels.proposed.jsonl').read_text().splitlines())}
    registry=json.loads((release/'registry.proposed.json').read_text())
    actual=Counter()
    composition=[]
    for domain in sorted({r['sampling_domain'] for r in records}):
        rows=[r for r in records if r['sampling_domain']==domain]
        labels=[label for r in rows for label in proposals[r['numeric_id']]['labels'] if label.get('decision','SUPPORTED')=='SUPPORTED']
        families=Counter(label['id'] for label in labels if label['kind']=='PROJECT')
        actual.update(set(families))
        topics=Counter(label['id'] for label in labels if label['kind']=='TOPIC')
        composition.append({'domain':domain,'repositories':len(rows),'retained_v1':sum(bool(r.get('v1_provenance')) for r in rows),
            'replacement_or_rebalanced':sum(not r.get('v1_provenance') for r in rows),
            'with_supported_project':sum(any(l['kind']=='PROJECT' and l.get('decision','SUPPORTED')=='SUPPORTED' for l in proposals[r['numeric_id']]['labels']) for r in rows),
            'project_family_counts':dict(families),'topic_counts':dict(topics),'owners':len({r['owner'].casefold() for r in rows}),
            'semantic_readme_fully_read':sum(r.get('agent_read_coverage',{}).get('readme',0)>=1 for r in rows),
            'splits':dict(Counter(row['split'] for row in inventory if row['sampling_domain']==domain))})
    coverage={'domains':composition,'project_coverage':[{'id':c['id'],'name':c['name'],'domain':c.get('domain'),
        'supported_repositories':sum(any(label['id']==c['id'] and label.get('decision','SUPPORTED')=='SUPPORTED' for label in p['labels']) for p in proposals.values())}
        for c in registry.values() if c['kind']=='PROJECT'],
        'all_active_english_eligibility_decisions':600,'human_approved':0,
        'language_gate_scope':'Full-file machine screening plus targeted agent purpose/language review; not exhaustive semantic knowledge extraction',
        'taxonomy_status':'PROPOSED; seed vocabulary was curated upfront. Missing labels remain UNKNOWN.'}
    write_json(release/'composition-audit.local.json',coverage)
    write_jsonl(release/'eligibility.decisions.jsonl',[{'repository_id':r['numeric_id'],'repository':r['full_name'],'decision':eligibility(r)} for r in records])

    # Report the fresh ledger separately from v1; copied cache never resets history.
    with sqlite3.connect(DATA/'collection.sqlite3') as db:
        ledger={'http_attempts':db.execute('SELECT count(*) FROM requests').fetchone()[0],
            'search_attempts':db.execute("SELECT count(*) FROM requests WHERE resource='search'").fetchone()[0],
            'response_statuses':dict(db.execute('SELECT coalesce(status,0),count(*) FROM requests GROUP BY status')),
            'retained_new_bytes':db.execute('SELECT coalesce(sum(bytes),0) FROM source_bytes').fetchone()[0],
            'claims':dict(db.execute('SELECT state,count(*) FROM claims GROUP BY state')),
            'limits':{'http':6000,'search':120,'source_bytes':512*1024**2},'paid_model_calls':0,
            'historical_cache_source':'v1 successful public responses copied; pinned snapshots reused, not all re-fetched live'}
    assert ledger['claims'].get('ACCEPTED')==600
    assert ledger['http_attempts']<=6000 and ledger['search_attempts']<=120
    write_json(release/'collection-ledger-summary.local.json',ledger)

    broken=[];links=0
    for path in (release/'human-review').glob('*.md'):
        for target in local_targets(path.read_text()):
            links+=1
            if not (path.parent/target.split('#')[0]).resolve().exists():broken.append({'file':str(path),'target':target})
    assert not broken,broken[:10]
    write_json(release/'local-links-audit.local.json',{'status':'PASS','local_links_checked':links,'broken':broken})

    bound={}
    for record in records:
        for file in [record['readme'],*record.get('supporting_files',[])]:bound[file['local_path']]=sha(ROOT/file['local_path'])
        bound[record['record_path']]=sha(ROOT/record['record_path'])
    release_id='public-corpus-600-english-2026-10-16-v2-PROPOSED'
    (release/'START-HERE.md').write_text(f'''# Public - Ground Truth · English corpus v2

Release: `{release_id}`. Exactly 600 public repositories, 60 per sampling domain. **Proposed references, not human-approved ground truth.**

Open GitHub Manager, sign in, and choose **Public - Ground Truth** in the top Workspace selector. Filter sampling/assigned Domains, Projects, Topics and Tags, then choose **Review evidence**. Read the source, edit purpose/labels, check reviewed dimensions, and save a confirmation, correction or unresolved decision. Export your reviews from the header. Added labels require an exact saved-source quote.

The raw sources remain in this version's `sources/` or unchanged v1 `sources/`, with commit and hash references. Inventory, proposed labels, proposed registry, grouped splits and this manifest live in `release/`. Dossiers and eligibility/exclusion records live in `shards/a/` and `shards/b/`. Human decisions persist in the configured application SQLite database under your GitHub numeric ID's `ground-truth` workspace, separately from personal organization and the immutable proposal files.

Start with `inventory.csv` or `human-review/README.md` if you prefer files. `repositories-with-content.reference-only.jsonl` includes complete retained source text and proposed labels for reference review; **never use it as model input**. `inputs.jsonl` is the annotation-free model input allowlist. Safety fixtures and v1 reports are preserved.

English eligibility screening is not a claim of full semantic reading of every source. Read-scope audits disclose that boundary. Both agents performed language/purpose screening; a risk/random independent audit covers 120 repositories. Human-confirmed corpus labels still start at zero. Missing concepts/labels remain unknown. Splits are provisional until taxonomy/reference approval; related families, owners, lineage and detected duplicates stay together.

The next step is the agreed 30-case agent/LLM/human pilot, with evidence-backed independent proposals, uncertain-case adjudication and random audits of high-agreement cases. No paid model calls were used for this cleanup.
''');(release/'START-HERE.md').chmod(0o600)
    manifest={'release_id':release_id,'created_at_utc':datetime.now(UTC).isoformat(),'status':'PROPOSED_REFERENCES_NOT_GOLD',
        'repositories':600,'readmes':600,'supporting_files':sum(len(r.get('supporting_files',[])) for r in records),
        'independent_cross_reviews':validation['cross_review_audit']['distinct_repositories'],'human_approved_records':0,
        'checks':{'assembly':'PASS','read_scope':'PASS','eligibility':'PASS','v1_preservation':'PASS','local_links':'PASS','paid_api_calls':0},
        'release_files':{str(path.relative_to(release)):{'sha256':sha(path),'bytes':path.stat().st_size} for path in sorted(release.rglob('*')) if path.is_file()},
        'sources_and_dossiers_sha256':bound,
        'methodology_and_tools_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'ai-system-design/evaluation/corpus-600-v2').rglob('*')) if p.is_file() and '__pycache__' not in p.parts},
        'limits':ledger['limits'],'split_status':'PROVISIONAL_NOT_LOCKED_UNTIL_REFERENCE_APPROVAL'}
    write_json(release/'manifest.local.json',manifest)
    print(json.dumps({'release_id':release_id,'repositories':600,'supporting_files':manifest['supporting_files'],'cross_reviews':manifest['independent_cross_reviews'],
        'source_and_dossier_files':len(bound),'v1_bound_files_preserved':len(preserved),'local_links_checked':links,'ledger':ledger},indent=2))


if __name__=='__main__':main()
