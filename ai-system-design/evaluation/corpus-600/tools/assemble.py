"""Offline, label-separated corpus assembly. Never constructs an API provider.

Use --require-complete only after all three source reviewers finish. Generated
datasets remain ignored/local; aggregate reporting contains no README copies.
"""
import argparse
import base64
from collections import Counter, defaultdict
import csv
import datetime
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys
import unicodedata
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).parent
DATA=ROOT/'docs/validation/private/corpus-600'
sys.path.insert(0,str(ROOT/'backend'))


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def normalized(name):
    return ' '.join(unicodedata.normalize('NFKC',name).casefold().split())


def concept_id(kind,name):
    # C/C++/C# remain distinct; hash suffix also protects other slug collisions.
    slug=re.sub(r'[^a-z0-9]+','-',normalized(name)).strip('-') or 'term'
    return kind.lower()+':'+slug+'-'+digest([kind,normalized(name)])[:8]


def write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n');path.chmod(0o600)


def write_jsonl(path,values):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w') as f:
        for value in values:f.write(json.dumps(value,ensure_ascii=False)+'\n')
    path.chmod(0o600)


def load_records():
    records=[];excluded=[]
    for p in sorted((DATA/'shards').glob('*/*/records/*.local.json')):
        r=json.loads(p.read_text());r['record_path']=str(p.relative_to(ROOT))
        (excluded if r.get('status') in {'REJECTED','OFF_DOMAIN'} else records).append(r)
    return records,excluded


def build_registry(records):
    registry={};by_name={};source_ids=defaultdict(set);domain_ids={};definition_conflicts=[]
    def add(kind,name,description='',aliases=(),domain=None,provenance=None,source_id=None):
        key=(kind,normalized(name));ident=by_name.get(key) or concept_id(kind,name)
        if ident not in registry:
            registry[ident]={'id':ident,'kind':kind,'name':name,'description':description or name,'aliases':[],
                             'domain':domain,'workspace':'corpus600','active':True,'status':'PROPOSED',
                             'human_approved':False,'definition_sources':[]}
            by_name[key]=ident
        item=registry[ident]
        if domain and item['domain'] and domain!=item['domain']:
            definition_conflicts.append({'id':ident,'reason':'PROJECT_PARENT_CONFLICT','domains':[domain,item['domain']]})
        if domain and not item['domain']:item['domain']=domain
        item['aliases']=sorted(set(item['aliases'])|set(aliases or []))
        if provenance and provenance not in item['definition_sources']:item['definition_sources'].append(provenance)
        if source_id:source_ids[(kind,source_id)].add(ident)
        return ident
    catalogs=[]
    for agent in 'abc':
        path=HERE.parent/f'domains-{agent}.json';cat=json.loads(path.read_text());catalogs.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        for d in cat['domains']:
            did=add('DOMAIN',d.get('name',d['id']),d.get('description',''),provenance=str(path.relative_to(ROOT)),source_id=d['id']);domain_ids[d['id']]=did
            for p in d.get('projects',[]):
                add('PROJECT',p['name'],p.get('description') or p.get('membership_criteria') or p.get('scope') or p['name'],p.get('aliases',[]),did,str(path.relative_to(ROOT)),p.get('id'))
            for t in d.get('topics',[]):
                add('TOPIC',t['name'],t.get('description',''),t.get('aliases',[]),provenance=str(path.relative_to(ROOT)),source_id=t.get('id'))
    for path in sorted((DATA/'shards').glob('*/new-topic-proposals.local.json')):
        for t in json.loads(path.read_text()):
            add('TOPIC',t['name'],t.get('description',''),t.get('aliases',[]),provenance=str(path.relative_to(ROOT)),source_id=t.get('id'))
    remaps=[]
    for r in records:
        ann=r.get('annotations') or {}
        for key,kind in [('projects','PROJECT'),('topics','TOPIC'),('tags','TAG')]:
            for label in ann.get(key,[]):
                if not isinstance(label,dict) or not label.get('name'):continue
                ident=by_name.get((kind,normalized(label['name'])))
                if not ident:
                    ident=add(kind,label['name'],label.get('description') or label['name'],provenance=r['record_path'],source_id=label.get('id'))
                    if kind=='PROJECT':definition_conflicts.append({'id':ident,'reason':'ANNOTATION_PROJECT_MISSING_CATALOG_PARENT'})
                remaps.append({'repository_id':r['numeric_id'],'kind':kind,'source_id':label.get('id'),'canonical_id':ident})
    # Enforce current app reservation semantics without merging conceptual scope.
    # Source catalogs stay unchanged; each proposed alias removal is audited.
    def reserved_term(name):return re.sub(r'[^\w+#]+',' ',unicodedata.normalize('NFKC',name).casefold()).strip()
    canon=defaultdict(set);alias_owners=defaultdict(set)
    for ident,item in registry.items():
        canon[(item['kind'],reserved_term(item['name']))].add(ident)
        for alias in item['aliases']:alias_owners[(item['kind'],reserved_term(alias))].add(ident)
    alias_removals=[]
    for ident,item in registry.items():
        retained=[];seen={reserved_term(item['name'])}
        for alias in item['aliases']:
            key=(item['kind'],reserved_term(alias));reason=None
            if key[1] in seen:reason='SELF_DUPLICATE_AFTER_APP_NORMALIZATION'
            elif canon.get(key,set())-{ident}:reason='ALIAS_COLLIDES_WITH_OTHER_CANONICAL'
            elif alias_owners[key]-{ident}:reason='AMBIGUOUS_SHARED_ALIAS'
            if reason:alias_removals.append({'id':ident,'alias':alias,'reason':reason})
            else:retained.append(alias);seen.add(key[1])
        item['aliases']=retained
    # Do not silently merge different canonical concepts with matching terms.
    reservations=defaultdict(set)
    for ident,item in registry.items():
        for value in [item['name'],*item['aliases']]:reservations[(item['kind'],reserved_term(value))].add(ident)
    collisions=[{'kind':k[0],'value':k[1],'ids':sorted(v)} for k,v in reservations.items() if len(v)>1]
    return registry,by_name,domain_ids,remaps,{'catalogs':catalogs,'definition_conflicts':definition_conflicts,'alias_collisions':collisions,'proposed_alias_removals':alias_removals}


def audit_sources(records):
    issues=[];counts=Counter();bytes_total=0
    seen_ids=set()
    for r in records:
        rid=r['numeric_id']
        if rid in seen_ids:issues.append({'id':rid,'reason':'DUPLICATE_REPOSITORY_ID'})
        seen_ids.add(rid)
        if r.get('private') is not False or r.get('source')!='PUBLIC_GITHUB':issues.append({'id':rid,'reason':'NON_PUBLIC_RECORD'})
        files={f['path']:f for f in [r['readme'],*r.get('supporting_files',[])]}
        texts={}
        for path,f in files.items():
            p=ROOT/f['local_path']
            if not p.is_relative_to(DATA/'sources') or not p.exists():issues.append({'id':rid,'path':path,'reason':'MISSING_OR_OUTSIDE_SOURCE'});continue
            raw=p.read_bytes();text=raw.decode('utf-8',errors='replace');texts[path]=text
            if len(raw)!=f['bytes'] or hashlib.sha256(raw).hexdigest()!=f['sha256'] or hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()!=f['git_blob_sha']:
                issues.append({'id':rid,'path':path,'reason':'SOURCE_HASH_OR_LENGTH_MISMATCH'})
            bytes_total+=len(raw);counts[f['role']]+=1
        def check_evidence(e):
            if not isinstance(e,dict):return
            if e.get('app_input_channel') in {'METADATA','GITHUB_METADATA'}:
                field=e.get('field') or e.get('path','').rsplit('.',1)[-1]
                value=r.get(field);quote=e.get('quote')
                serialized=json.dumps(value,ensure_ascii=False)
                text=serialized if e.get('metadata_value_sha256') else (value if isinstance(value,str) else serialized)
                if quote and quote not in text:issues.append({'id':rid,'reason':'METADATA_FIELD_EVIDENCE_MISMATCH','field':field})
                if e.get('metadata_value_sha256') and hashlib.sha256(serialized.encode()).hexdigest()!=e['metadata_value_sha256']:
                    issues.append({'id':rid,'reason':'METADATA_VALUE_HASH_MISMATCH','field':field})
                a,b=e.get('start_character'),e.get('end_character')
                if a is not None and b is not None and (not 0<=a<=b<=len(text) or (quote and quote not in text[a:b])):
                    issues.append({'id':rid,'reason':'METADATA_CHARACTER_RANGE_MISMATCH','field':field})
                path=ROOT/e.get('path','')
                if path.is_relative_to(DATA) and path.is_file() and e.get('sha256') and hashlib.sha256(path.read_bytes()).hexdigest()!=e['sha256']:
                    issues.append({'id':rid,'reason':'METADATA_SNAPSHOT_HASH_MISMATCH'})
                counts['shared_input_metadata_evidence']+=1
                return
            if e.get('path') not in texts:
                issues.append({'id':rid,'path':e.get('path'),'reason':'EVIDENCE_PATH_NOT_IN_PINNED_SOURCES'})
                return
            f=files[e['path']];text=texts[e['path']]
            expected=e.get('sha256') or e.get('source_sha256')
            if expected and expected!=f['sha256']:issues.append({'id':rid,'path':e['path'],'reason':'EVIDENCE_HASH_MISMATCH'})
            if e.get('commit') and e['commit']!=r['commit']:issues.append({'id':rid,'path':e['path'],'reason':'EVIDENCE_COMMIT_MISMATCH'})
            if e.get('git_blob_sha') and e['git_blob_sha']!=f['git_blob_sha']:issues.append({'id':rid,'path':e['path'],'reason':'EVIDENCE_BLOB_SHA_MISMATCH'})
            quote=e.get('quote')
            if quote and quote not in text:issues.append({'id':rid,'path':e['path'],'reason':'EVIDENCE_QUOTE_NOT_IN_SOURCE','quote_prefix':quote[:70]})
            a,b=e.get('start_line'),e.get('end_line')
            if a is not None and b is not None:
                if not 1<=a<=b<=len(text.splitlines()):issues.append({'id':rid,'path':e['path'],'reason':'LINE_RANGE_OUTSIDE_SOURCE'})
                elif quote and quote not in ''.join(text.splitlines(keepends=True)[a-1:b]):issues.append({'id':rid,'path':e['path'],'reason':'QUOTE_OUTSIDE_CITED_LINES'})
            a,b=e.get('start_character'),e.get('end_character')
            if a is not None and b is not None and (not 0<=a<=b<=len(text) or (quote and quote not in text[a:b])):
                issues.append({'id':rid,'path':e['path'],'reason':'QUOTE_OUTSIDE_CITED_CHARACTERS'})
        ann=r.get('annotations') or {}
        for e in ann.get('purpose_evidence',[]):check_evidence(e)
        for key in ['projects','topics','tags']:
            for label in ann.get(key,[]):
                for e in label.get('evidence',[]):check_evidence(e)
    return {'files':dict(counts),'source_bytes_in_current_records':bytes_total,'issues':issues}


def audit_directory_bindings(records):
    """Check API text against pinned directory entries, including resolved symlinks."""
    with sqlite3.connect(DATA/'collection.sqlite3') as c:
        cached={key:json.loads(body) for key,body in c.execute('SELECT key,body FROM cache')}
    def response(path,commit):return cached.get(hashlib.sha256(json.dumps([path,{'ref':commit}],sort_keys=True).encode()).hexdigest())
    checked=0;resolved=0;issues=[];missing=[];anomalies=[]
    for r in records:
        endpoint='/repos/'+r['full_name'];commit=r['commit']
        for f in [r['readme'],*r.get('supporting_files',[])]:
            path=Path(f['path']);parent=str(path.parent)
            listing=response(endpoint+'/contents'+('' if parent=='.' else '/'+quote(parent)),commit)
            entry=next((x for x in listing if x.get('path')==f['path']),None) if isinstance(listing,list) else None
            if not entry:missing.append({'id':r['numeric_id'],'path':f['path']});continue
            if f.get('resolved_git_path'):
                target=f['resolved_git_path'];raw_target=target.encode();link_sha=hashlib.sha1(f'blob {len(raw_target)}\0'.encode()+raw_target).hexdigest()
                doc=response(endpoint+'/contents/'+quote(target),commit);raw=(ROOT/f['local_path']).read_bytes()
                if (entry['sha']!=link_sha or entry['sha']!=f.get('logical_git_blob_sha') or not isinstance(doc,dict) or
                    doc.get('path')!=target or doc.get('sha')!=f['git_blob_sha'] or
                    base64.b64decode(doc.get('content',''))!=raw):
                    issues.append({'id':r['numeric_id'],'path':f['path'],'reason':'UNVERIFIED_README_SYMLINK_RESOLUTION'})
                else:resolved+=1;checked+=1
            elif entry['sha']!=f['git_blob_sha'] or entry.get('size')!=f['bytes']:
                issues.append({'id':r['numeric_id'],'path':f['path'],'reason':'DIRECTORY_BLOB_OR_SIZE_MISMATCH','listing_sha':entry['sha'],'file_sha':f['git_blob_sha']})
            else:checked+=1
        text=(ROOT/r['readme']['local_path']).read_bytes().decode('utf-8',errors='replace')
        if text.startswith('Resource from plugin:'):
            anomalies.append({'id':r['numeric_id'],'repository':r['full_name'],'reason':'WRAPPER_LIKE_LITERAL_SOURCE_PREFIX','interpretation':'Untrusted source text; hash/listing consistency checked; origin of literal prefix not independently established.'})
    return {'checked_files':checked,'verified_readme_symlinks':resolved,'issues':issues,'missing_directory_entries':missing,'literal_source_anomalies':anomalies}


class Groups:
    def __init__(self,ids):self.parent={i:i for i in ids}
    def find(self,i):
        while self.parent[i]!=i:self.parent[i]=self.parent[self.parent[i]];i=self.parent[i]
        return i
    def join(self,a,b):
        a,b=self.find(a),self.find(b)
        if a!=b:self.parent[max(a,b)]=min(a,b)


def grouped_splits(records,by_name):
    groups=Groups([r['numeric_id'] for r in records]);families=defaultdict(list);hashes=defaultdict(list);owners=defaultdict(list);relations=[]
    names={r['full_name'].casefold():r['numeric_id'] for r in records}
    shingle_sets={};fingerprints=defaultdict(list)
    for r in records:
        rid=r['numeric_id'];hashes[r['readme']['sha256']].append(rid);owners[r['owner'].casefold()].append(rid)
        text=(ROOT/r['readme']['local_path']).read_bytes().decode('utf-8',errors='replace')
        words=re.findall(r'[\w+#]+',re.sub(r'https?://\S+',' ',text).casefold())
        if len(words)>=200:
            shingles={hashlib.sha256(' '.join(words[i:i+5]).encode()).digest()[:8] for i in range(len(words)-4)}
            shingle_sets[rid]=shingles
            for fingerprint in sorted(shingles)[:32]:fingerprints[fingerprint].append(rid)
        for label in (r.get('annotations') or {}).get('projects',[]):
            if label.get('decision','SUPPORTED')=='SUPPORTED':families[by_name[('PROJECT',normalized(label['name']))]].append(rid)
        for c in (r.get('annotations') or {}).get('conflicts',[]):
            if not isinstance(c,dict):continue
            related=c.get('related_repo');kind=c.get('type','')
            if related and any(w in kind for w in ['LINEAGE','DUPLICATE']):
                other=names.get(related.casefold())
                if other is not None:groups.join(rid,other);relations.append({'a':rid,'b':other,'reason':kind})
    for reason,buckets in [('PROJECT_FAMILY',families),('IDENTICAL_README',hashes),('CONSERVATIVE_SHARED_OWNER',owners)]:
        for key,ids in buckets.items():
            for other in ids[1:]:groups.join(ids[0],other);relations.append({'a':ids[0],'b':other,'reason':reason,'key':key})
    candidates=Counter()
    for ids in fingerprints.values():
        for i,a in enumerate(ids):
            for b in ids[i+1:]:candidates[tuple(sorted([a,b]))]+=1
    for (a,b),overlap in candidates.items():
        if overlap<5:continue
        similarity=len(shingle_sets[a]&shingle_sets[b])/len(shingle_sets[a]|shingle_sets[b])
        if similarity>=.8:
            groups.join(a,b);relations.append({'a':a,'b':b,'reason':'NORMALIZED_README_NEAR_DUPLICATE','five_word_shingle_jaccard':similarity})
    members=defaultdict(list)
    for r in records:members[groups.find(r['numeric_id'])].append(r)
    target={'development':180,'validation':120,'test_reserved':300};counts=Counter();assigned={};group_rows=[]
    ordered=sorted(members.values(),key=lambda rs:(-len(rs),digest(sorted(r['numeric_id'] for r in rs))))
    for rs in ordered:
        # Greedy deficit allocation preserves groups, prioritizing the intended proportions.
        split=max(target,key=lambda k:(target[k]-counts[k])/target[k]);counts[split]+=len(rs)
        gid='group:'+digest(sorted(r['numeric_id'] for r in rs))[:16]
        for r in rs:assigned[r['numeric_id']]={'group':gid,'split':split}
        group_rows.append({'id':gid,'split':split,'repository_ids':sorted(r['numeric_id'] for r in rs)})
    return assigned,{'targets':target,'actual':dict(counts),'groups':group_rows,'grouping_edges':relations,
                     'status':'PROVISIONAL_NOT_LOCKED_UNTIL_REFERENCE_APPROVAL',
                     'limits':'Exact hashes, recorded source lineage/families, conservative shared-owner groups and detected near-duplicates are grouped. Near-duplicate detector uses32 bottom-hash candidates,≥5 shared hashes,≥200 words and five-word-shingle Jaccard≥0.8; it is not exhaustive. Shared-owner grouping prevents leakage, not evidence of Project membership. Registry definitions were curated with corpus source access; this is not an unseen-registry benchmark.'}


def inputs_and_labels(records,registry,by_name,domain_ids):
    inputs=[];labels=[]
    for r in records:
        # Explicit allowlist keeps annotation/search/review data out of app inputs.
        inputs.append({'key':'github:'+str(r['numeric_id']),'id':r['numeric_id'],'name':r['full_name'],
                       'description':r.get('description') or '','topics':r.get('native_topics',[]),'language':r.get('primary_language'),
                       'readme_sha':r['readme']['git_blob_sha'],'private':False,'source':'PUBLIC_GITHUB','policy_verified':True,
                       'readme_path':r['readme']['local_path']})
        ann=r.get('annotations') or {};proposed=[];project_domains=set()
        for key,kind in [('projects','PROJECT'),('topics','TOPIC'),('tags','TAG')]:
            for label in ann.get(key,[]):
                ident=by_name[(kind,normalized(label['name']))]
                proposed.append({**label,'id':ident,'kind':kind,'source_annotation_id':label.get('id')})
                if kind=='PROJECT' and label.get('decision','SUPPORTED')=='SUPPORTED' and registry[ident]['domain']:project_domains.add(registry[ident]['domain'])
        labels.append({'repository_id':r['numeric_id'],'status':r.get('annotation_status','PROPOSED'),'human_approved':r.get('human_approved',False),
                       'purpose':ann.get('purpose'),'purpose_evidence':ann.get('purpose_evidence',[]),'labels':proposed,'derived_domains':sorted(project_domains),
                       'sampling_domain_is_not_assignment':True,'read_coverage':r.get('agent_read_coverage'),
                       'dimension_status':ann.get('dimension_status') or {'unlisted_memberships':'UNKNOWN_NOT_NEGATIVE'},
                       'exclusions':ann.get('exclusions',[]),'conflicts':ann.get('conflicts',[]),'annotation_confidence':ann.get('annotation_confidence'),
                       'dossier_path':r['record_path']})
    return inputs,labels


def attach_cross_reviews(records,labels):
    by_id={r['numeric_id']:r for r in records};label_map={r['repository_id']:r for r in labels};valid=[];invalid=[]
    for path in sorted((DATA/'cross-review').glob('*/results.local.json')):
        content=json.loads(path.read_text());rows=content if isinstance(content,list) else content.get('reviews',[])
        for review in rows:
            rid=review.get('repository_id');r=by_id.get(rid);reason=None
            if not r:reason='REPOSITORY_NOT_CURRENTLY_ACCEPTED'
            elif review.get('reviewer')==r['collector_agent'] or str((r.get('annotations') or {}).get('reviewer','')).casefold().replace('agent','').strip(' -_:')==review.get('reviewer'):reason='NOT_INDEPENDENT_REVIEWER'
            elif review.get('annotation_sha256')!=digest(r.get('annotations')):reason='STALE_ANNOTATION_BINDING'
            elif review.get('readme_sha256')!=r['readme']['sha256']:reason='STALE_SOURCE_BINDING'
            elif review.get('verdict') not in {'SUPPORTED','NEEDS_CORRECTION','UNKNOWN'}:reason='INVALID_VERDICT'
            elif not review.get('inspected_sources'):reason='NO_SOURCE_INSPECTION_RECORDED'
            if reason:invalid.append({'repository_id':rid,'reason':reason,'path':str(path.relative_to(ROOT))});continue
            valid.append(review);target=label_map[rid];target.setdefault('cross_reviews',[]).append(review)
            if review['verdict']=='NEEDS_CORRECTION':target['status']='DISPUTED'
            elif review['verdict']=='SUPPORTED' and target['status']!='DISPUTED':target['status']='CROSS_REVIEWED'
    return {'valid_reviews':len(valid),'distinct_repositories':len({r['repository_id'] for r in valid}),
            'verdicts':dict(Counter(r['verdict'] for r in valid)),'invalid_or_stale':invalid,'human_approval_implied':False}


def offline_check(inputs,labels,registry):
    from app.demo.evidence import build_profile
    from app.pretest.ai.evidence import Retriever,compact,tokens,clean
    from markdown_it import MarkdownIt
    retriever=Retriever(registry,method='tfidf');profiles=[];ranking=[];metrics=defaultdict(Counter);failures=[];previews=[];availability=Counter()
    label_map={r['repository_id']:r for r in labels}
    def quote_tokens(quote):
        parts=[]
        for token in MarkdownIt('commonmark').parse(quote):
            if token.type=='inline':parts.extend(c.content for c in (token.children or []) if c.type in {'text','softbreak'})
        return ' '.join(tokens(clean(' '.join(parts))))
    for repo in inputs:
        try:
            prof=build_profile(repo,(ROOT/repo['readme_path']).read_bytes().decode('utf-8',errors='replace'))
            compacted=compact(prof);candidates=retriever.candidates(prof);profiles.append({'repository_id':repo['id'],'profile':prof,'compact':compacted})
            reference=label_map[repo['id']];proposed=reference['labels']
            expected=[x for x in proposed if x.get('decision','SUPPORTED')=='SUPPORTED'] if reference['status']!='DISPUTED' else []
            support=[]
            for label in expected:
                diagnostic={'id':label['id'],'has_app_input_channel_evidence':False,'quote_token_sequence_in_profile':False,'quote_token_sequence_in_compact':False}
                for e in label.get('evidence',[]):
                    channel=e.get('app_input_channel')
                    if channel not in {'README','METADATA','GITHUB_METADATA'}:continue
                    diagnostic['has_app_input_channel_evidence']=True
                    needle=quote_tokens(e.get('quote') or '')
                    if not needle:continue
                    for field,items in [('quote_token_sequence_in_profile',prof['evidence']),('quote_token_sequence_in_compact',compacted['evidence'])]:
                        text=' '.join(tokens(' '.join(x['text'] for x in items if (x['id']=='E0')==(channel!='README'))))
                        diagnostic[field]|=(' '+needle+' ') in (' '+text+' ')
                support.append(diagnostic);availability['supported_positive_labels']+=1
                for key in ['has_app_input_channel_evidence','quote_token_sequence_in_profile','quote_token_sequence_in_compact']:availability[key]+=diagnostic[key]
            previews.append({'repository_id':repo['id'],'status':'OFFLINE_RECONSTRUCTION_NOT_SENT',
                             'scenario':'Fresh isolated corpus workspace; no existing edges/rejections/rules; registry revision0.',
                             'classification_evidence':{'source':'PUBLIC_GITHUB','private':False,'repo_id':repo['key'],'workspace':'corpus600','revision':0,
                                                        'evidence_hash':prof['hash'],'policy':prof['policy'],**compacted,
                                                        'candidates':[{k:registry[cid][k] for k in ['id','kind','name','description']} for cid in candidates]}})
            row={'repository_id':repo['id'],'candidate_ids':candidates,'candidate_count':len(candidates),'full_reference_positive_ids':[x['id'] for x in expected],
                 'missing_positive_ids':[x['id'] for x in expected if x['id'] not in candidates],
                 'reference_only_positive_ids':[x['id'] for x in expected if x.get('evidence') and all(e.get('app_input_channel')=='REFERENCE_ONLY' for e in x['evidence'])],
                 'metadata_only_positive_ids':[x['id'] for x in expected if x.get('evidence') and all(e.get('app_input_channel') in {'GITHUB_METADATA','METADATA'} for e in x['evidence'])],
                 'reference_status':reference['status'],'support_availability_diagnostics':support,'evidence_items':len(prof['evidence']),'phrases':len(prof['phrases']),'compact_characters':len(json.dumps(compacted,ensure_ascii=False))}
            ranking.append(row)
            for x in expected:metrics[x['kind']]['positive_labels']+=1;metrics[x['kind']]['retrieved_positive_labels']+=x['id'] in candidates
        except Exception as e:failures.append({'repository_id':repo['id'],'type':type(e).__name__,'message':str(e)[:200]})
    result={kind:{**dict(v),'positive_recall':v['retrieved_positive_labels']/v['positive_labels'] if v['positive_labels'] else None} for kind,v in metrics.items()}
    return profiles,ranking,previews,{'status':'PROVISIONAL_SOURCE_REVIEW_DIAGNOSTIC','profile_successes':len(profiles),'failures':failures,'positive_recall_by_kind':result,'source_to_compact_quote_diagnostics':dict(availability),
                            'support_diagnostic_limits':'Token-sequence containment after Markdown cleaning is a lexical omission diagnostic, not semantic entailment or proof of what an LLM can infer. Compact payloads are offline reconstructions; no requests were transmitted.',
                            'limits':'No API, generation or judge calls. Recall uses agent-proposed positives, not human-approved gold. Unknown/unlisted labels are not negatives, so precision/F1 are not computed. Full-source reference recall includes support the app may omit; metadata inputs can overlap technology references. Defaults were not tuned on this corpus.'}


def review_artifacts(records,labels,registry,out):
    label_map={r['repository_id']:r for r in labels};combined=[];forms=[];by_domain=defaultdict(list)
    for r in records:
        label=label_map[r['numeric_id']];files=[]
        for f in [r['readme'],*r.get('supporting_files',[])]:
            files.append({**f,'text_utf8':(ROOT/f['local_path']).read_bytes().decode('utf-8',errors='replace')})
        combined.append({'repository_id':r['numeric_id'],'repository':r['full_name'],'metadata':{k:r.get(k) for k in ['url','description','native_topics','primary_language','license','commit','retrieved_at_utc']},
                         'files':files,'proposed_reference':label,'purpose':'HUMAN_REFERENCE_ONLY_NOT_MODEL_INPUT'})
        forms.append({'repository_id':r['numeric_id'],'repository':r['full_name'],'decision':'PENDING','approved_positive_ids':[],
                      'rejected_positive_ids':[],'additional_labels':[],'notes':'','reviewer':'','reviewed_at':None})
        by_domain[r['sampling_domain']].append(r)
    write_jsonl(out/'repositories-with-content.reference-only.jsonl',combined)
    write_json(out/'human-review-decisions.template.json',{'status':'UNREVIEWED_TEMPLATE','instructions':'Record actual reviewer decisions. Empty lists and PENDING are not negative labels. Do not mark human approval automatically.','decisions':forms})
    folder=out/'human-review';folder.mkdir(exist_ok=True)
    index=['# Proposed reference review','',
           '600 is the collection target; consult validation.local.json for the current complete/reviewed count. These are agent-proposed references, not approved ground truth. Cross-review does not substitute for your approval.','',
           'Review the primary purpose, Project relationship, Topics and primary technology Tags. Unlisted memberships remain UNKNOWN. Approve supported positives, reject a specific unsupported positive, or request more evidence. Do not infer global NO_MATCH from an empty Project list.','',
           'The complete README and supporting sources are available through each dossier. Supporting documents are reference-only unless the current app receives equivalent evidence. Language metadata is shared input and is not independent technology truth. Targeted reading is disclosed; source retention does not mean every byte was semantically read.','',
           'Record decisions in a copy of ../human-review-decisions.template.json, retaining the repository IDs and actual reviewer/date. This work does not automatically import labels into the app or replace controlled fixtures.','',
           '| Sampling domain | Records | Review sheet |','| --- | --- | --- |']
    for domain,rows in sorted(by_domain.items()):
        path=folder/f'{domain}.md';text=[f'# {domain}: proposed reference review','',
                                      'Review status is recorded per repository. Source-backed proposals still require human approval; missing labels are UNKNOWN.','']
        for r in sorted(rows,key=lambda x:x['full_name'].casefold()):
            ref=label_map[r['numeric_id']];ann=r.get('annotations') or {}
            text.extend([f"## {r['full_name']} · {r['numeric_id']}",'',ref.get('purpose') or 'Purpose review pending.','',
                         f"Status: **{ref['status']}**. README semantic read coverage: {r.get('agent_read_coverage',{}).get('readme',0):.1%}. Human decision: **PENDING**.",''])
            for kind in ['PROJECT','TOPIC','TAG']:
                names=[x['name'] for x in ref['labels'] if x['kind']==kind and x.get('decision','SUPPORTED')=='SUPPORTED']
                text.append(f"- {kind.title()}: {', '.join(names) if names else 'UNKNOWN / no supported positive proposed'}")
            domains=[registry[i]['name'] for i in ref['derived_domains']];text.append('- Derived Domain: '+(', '.join(domains) if domains else 'UNKNOWN; sampling bucket does not assign Domain'))
            text.extend(['',f"[Complete README](../../{Path(r['readme']['local_path']).relative_to(DATA.relative_to(ROOT)).as_posix()}) · [Full dossier](../../{Path(r['record_path']).relative_to(DATA.relative_to(ROOT)).as_posix()}) · [Pinned GitHub source]({r['readme']['source_url']})",''])
            # A few inspectable passages; all evidence is retained in the dossier/JSONL.
            seen=set()
            for label in ref['labels']:
                e=next((e for e in label.get('evidence',[]) if e.get('quote')),None)
                if not e or e['quote'] in seen:continue
                seen.add(e['quote']);snippet=' '.join(e['quote'].split())[:240]
                text.append(f"> {snippet.replace('>','')}"+('…' if len(' '.join(e['quote'].split()))>240 else ''))
                text.extend(['',f"Evidence for {label['name']}: `{e.get('path')}`; channel **{e.get('app_input_channel','UNSPECIFIED')}**.",''])
                if len(seen)>=3:break
            if ann.get('conflicts'):text.extend(['Review notes: '+json.dumps(ann['conflicts'],ensure_ascii=False),''])
            text.extend(['Decision: PENDING. Corrections/additional evidence: ______.',''])
        path.write_text('\n'.join(text));path.chmod(0o600)
        index.append(f'| {domain} | {len(rows)} | [{domain}]({domain}.md) |')
    (folder/'README.md').write_text('\n'.join(index)+'\n');(folder/'README.md').chmod(0o600)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--require-complete',action='store_true');parser.add_argument('--offline-check',action='store_true');args=parser.parse_args()
    records,excluded=load_records();counts=Counter(r['sampling_domain'] for r in records);reviewed=sum(bool(r.get('annotations')) for r in records)
    if args.require_complete and (len(records)!=600 or len(counts)!=10 or any(n!=60 for n in counts.values()) or reviewed!=600):
        raise SystemExit(f'Incomplete: {len(records)} records, {reviewed} reviewed; domains={dict(counts)}')
    registry,by_name,domain_ids,remaps,registry_audit=build_registry(records);sources=audit_sources(records);directory=audit_directory_bindings(records)
    assigned,splits=grouped_splits(records,by_name);inputs,labels=inputs_and_labels(records,registry,by_name,domain_ids)
    cross_reviews=attach_cross_reviews(records,labels)
    if args.require_complete and (cross_reviews['distinct_repositories']<120 or cross_reviews['invalid_or_stale']):
        raise SystemExit('Cross-review gate incomplete or stale: '+json.dumps(cross_reviews))
    label_status={r['repository_id']:r['status'] for r in labels}
    out=DATA/'release';write_json(out/'registry.proposed.json',registry);write_json(out/'registry-audit.local.json',registry_audit);write_jsonl(out/'concept-id-remap.jsonl',remaps)
    write_jsonl(out/'inputs.jsonl',inputs);write_jsonl(out/'labels.proposed.jsonl',labels);write_json(out/'splits.provisional.json',splits)
    inventory=[]
    for r in records:
        inventory.append({'repository_id':r['numeric_id'],'full_name':r['full_name'],'url':r['url'],'sampling_domain':r['sampling_domain'],
                          'description':r.get('description'),'language':r.get('primary_language'),'stars':r['stars'],'owner':r['owner'],
                          'commit':r['commit'],'readme_path':r['readme']['local_path'],'readme_bytes':r['readme']['bytes'],'readme_sha256':r['readme']['sha256'],
                          'supporting_files':len(r.get('supporting_files',[])),'license_spdx':(r.get('license') or {}).get('spdx_id','UNKNOWN'),
                          'reviewed':bool(r.get('annotations')),'annotation_status':label_status[r['numeric_id']],'human_approved':r.get('human_approved',False),
                          'readme_read_coverage':r.get('agent_read_coverage',{}).get('readme',0),'dossier_path':r['record_path'],**assigned[r['numeric_id']]})
    write_jsonl(out/'inventory.jsonl',inventory)
    if inventory:
        with (out/'inventory.csv').open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(inventory[0]));writer.writeheader();writer.writerows(inventory)
        (out/'inventory.csv').chmod(0o600)
    diagnostics=None
    if args.offline_check:
        profiles,ranks,previews,diagnostics=offline_check(inputs,labels,registry)
        write_jsonl(out/'profiles.app-v2.jsonl',profiles);write_jsonl(out/'retrieval.app-tfidf.jsonl',ranks);write_jsonl(out/'model-request-previews.offline.jsonl',previews);write_json(out/'offline-diagnostics.local.json',diagnostics)
    review_artifacts(records,labels,registry,out)
    report={'date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'accepted_records':len(records),'annotated_records':reviewed,'excluded_records_in_current_paths':len(excluded),
            'sampling_domains':dict(counts),'languages':dict(Counter(r.get('primary_language') or 'UNKNOWN' for r in records)),
            'top_owners':Counter(r['owner'].casefold() for r in records).most_common(15),'license_unknown':sum((r.get('license') or {}).get('spdx_id','UNKNOWN') in {'UNKNOWN','NOASSERTION'} for r in records),
            'readme_fully_read':sum(r.get('agent_read_coverage',{}).get('readme',0)>=1 for r in records),
            'readme_targeted_or_partial':sum(0<r.get('agent_read_coverage',{}).get('readme',0)<1 for r in records),
            'registry_counts':dict(Counter(v['kind'] for v in registry.values())),'registry_audit':registry_audit,'source_audit':sources,'directory_binding_audit':directory,
            'split_counts':splits['actual'],'cross_review_audit':cross_reviews,'offline_diagnostics':diagnostics,'human_approved_records':sum(bool(r.get('human_approved')) for r in records),
            'release_status':'PROPOSED_REFERENCES_NOT_GOLD','input_label_separation':'Explicit input allowlist; annotations/search provenance are separate files.'}
    write_json(out/'validation.local.json',report)
    print(json.dumps({k:v for k,v in report.items() if k not in {'registry_audit','source_audit'}},indent=2));print('source_integrity_issues',len(sources['issues']))
    if args.require_complete and (sources['issues'] or directory['issues'] or directory['missing_directory_entries'] or registry_audit['definition_conflicts'] or registry_audit['alias_collisions']):raise SystemExit('Release blocked: inspect source/registry audit')


if __name__=='__main__':main()
