"""Prepare bounded independent source-review packets; never creates verdicts."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[4]
DATA=ROOT/'docs/validation/private/corpus-600'


def stable(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def create(reviewer,producer):
    assert reviewer!=producer
    dest=DATA/'cross-review'/reviewer/'queue.local.json'
    if dest.exists():raise SystemExit('Existing queue preserved; inspect it rather than replacing reviewed work')
    domains={}
    for p in (DATA/'shards'/producer).glob('*/records/*.local.json'):
        r=json.loads(p.read_text())
        if r.get('status') in {'REJECTED','OFF_DOMAIN'} or not r.get('annotations'):continue
        domains.setdefault(r['sampling_domain'],[]).append((p,r))
    if not domains:raise SystemExit('No source-reviewed producer records')
    selected=[];domain_counts={}
    def risk(r):
        ann=r['annotations'];labels=[x for k in ['projects','topics','tags'] for x in ann.get(k,[])]
        return (bool(ann.get('conflicts'))*3+sum(any(e.get('app_input_channel')=='REFERENCE_ONLY' for e in x.get('evidence',[])) for x in labels)*2+
                (len(ann.get('projects',[]))>1)*3+(r.get('agent_read_coverage',{}).get('readme',0)<.2))
    for i,domain in enumerate(sorted(domains)):
        target=40//len(domains)+(i<40%len(domains));rows=domains[domain]
        if len(rows)<target:raise SystemExit(f'Need {target} reviewed {domain} records, only {len(rows)} ready')
        rows.sort(key=lambda pair:(-risk(pair[1]),stable(pair[1]['numeric_id'])))
        risky=rows[:target//2];chosen={r['numeric_id'] for _,r in risky}
        remaining=sorted([pair for pair in rows if pair[1]['numeric_id'] not in chosen],key=lambda pair:stable(['cross-review',pair[1]['numeric_id']]))
        picked=risky+remaining[:target-len(risky)];domain_counts[domain]=len(picked)
        for path,r in picked:selected.append({'repository_id':r['numeric_id'],'full_name':r['full_name'],'domain':domain,'dossier_path':str(path.relative_to(ROOT)),
                                              'annotation_sha256':stable(r['annotations']),'source_sha256':r['readme']['sha256'],'producer':producer,'reviewer':reviewer})
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps({'reviewer':reviewer,'producer':producer,'records':selected,'domain_counts':domain_counts},indent=2)+'\n');dest.chmod(0o600)
    print(json.dumps({'queue':str(dest.relative_to(ROOT)),'records':len(selected),'domains':domain_counts},indent=2))


def packet(reviewer,start,count):
    queue=json.loads((DATA/'cross-review'/reviewer/'queue.local.json').read_text())
    emitted=[]
    for item in queue['records'][start:start+count]:
        r=json.loads((ROOT/item['dossier_path']).read_text());ann=r['annotations']
        # Bind the actual source/annotation displayed, retaining the initial queue snapshot.
        item={**item,'queue_annotation_sha256':item['annotation_sha256'],'annotation_sha256':stable(ann),
              'queue_source_sha256':item['source_sha256'],'source_sha256':r['readme']['sha256']}
        print('\nREPOSITORY',r['numeric_id'],r['full_name'],'DOMAIN',r['sampling_domain'],'PRODUCER',item['producer'])
        print('PURPOSE_PROPOSAL',ann.get('purpose'));print('METADATA',json.dumps({k:r.get(k) for k in ['description','primary_language','native_topics','license']},ensure_ascii=False))
        labels=[];by_path={}
        for kind in ['projects','topics','tags']:
            for label in ann.get(kind,[]):
                labels.append({'kind':kind,'id':label.get('id'),'name':label.get('name'),'decision':label.get('decision'),'rationale':label.get('rationale')})
                for e in label.get('evidence',[]):
                    if e.get('app_input_channel') in {'METADATA','GITHUB_METADATA'}:continue
                    if e.get('path') and e.get('start_line') is not None:by_path.setdefault(e['path'],set()).update(range(max(1,e['start_line']-1),e['end_line']+2))
        print('LABEL_PROPOSALS',json.dumps(labels,ensure_ascii=False));print('EXCLUSIONS',json.dumps(ann.get('exclusions',[]),ensure_ascii=False)[:1600]);print('CONFLICTS',json.dumps(ann.get('conflicts',[]),ensure_ascii=False)[:1600])
        # Reviewer sees actual source text, not just the producer's quoted evidence.
        files=[r['readme'],*r.get('supporting_files',[])];printed=0;inspected=[]
        for f in files:
            text=(ROOT/f['local_path']).read_bytes().decode('utf-8',errors='replace');lines=text.splitlines()
            wanted=set(by_path.get(f['path'],[]))
            if f['role']=='README':wanted.update(range(1,min(30,len(lines))+1))
            if not wanted:continue
            print('SOURCE',f['path'],'SHA256',f['sha256'],'CHANNEL',f['app_input_channel'],'TOTAL_LINES',len(lines))
            intervals=[]
            for i in sorted(wanted):
                if not 1<=i<=len(lines):continue
                line=lines[i-1]
                # Explicitly omit giant generated lines; no claim of reading them.
                if len(line)>1200:print(f'{i}: [LONG LINE OMITTED; inspect full file if needed]');continue
                if printed+len(line)>6500:print('[PACKET SOURCE BUDGET REACHED; inspect full source if needed]');break
                print(f'{i}: {line}');printed+=len(line);intervals.append(i)
            print('DISPLAYED_LINE_NUMBERS',json.dumps(intervals))
            inspected.append({'path':f['path'],'sha256':f['sha256'],'displayed_line_numbers':intervals,'coverage':'TARGETED_PACKET_NOT_COMPLETE_READING'})
        print('REVIEW_BINDING',json.dumps(item,ensure_ascii=False))
        emitted.append({**item,'inspected_sources':inspected,'status':'EMITTED_FOR_REVIEW_NOT_A_VERDICT'})
    dest=DATA/'cross-review'/reviewer/'packets'/f'{start}-{count}.local.json';dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(emitted,indent=2)+'\n');dest.chmod(0o600)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['create','packet']);p.add_argument('--reviewer',choices=['a','b','c','root'],required=True);p.add_argument('--producer',choices=list('abc'));p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=3);a=p.parse_args()
    if a.mode=='create':create(a.reviewer,a.producer)
    else:packet(a.reviewer,a.start,a.count)
