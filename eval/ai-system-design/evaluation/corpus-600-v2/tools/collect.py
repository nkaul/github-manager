"""Resumable public-source harvest through the credential-isolated local broker.

Harvested evidence is not an agent reading or human annotation. Those are separate,
explicitly recorded review steps.
"""
import argparse,base64,hashlib,json,os,re,sys,time
from pathlib import Path,PurePosixPath
from urllib.parse import quote
import httpx

ROOT=Path(__file__).resolve().parents[5];DATA=ROOT/'docs/validation/private/corpus-600-v2';HERE=Path(__file__).parent

class SourceIntegrityError(ValueError):
    def __init__(self,doc,actual):
        super().__init__('Git blob integrity mismatch')
        self.audit={'path':doc.get('path'),'reason':'GIT_BLOB_INTEGRITY_MISMATCH',
                    'expected_git_blob_sha':doc.get('sha'),'actual_git_blob_sha':actual,
                    'reported_type':doc.get('type'),'reported_size':doc.get('size')}

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp');fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
    with os.fdopen(fd,'w') as f:json.dump(value,f,indent=2,ensure_ascii=False);f.write('\n')
    os.replace(tmp,path);os.chmod(path,0o600)

class Broker:
    def __init__(self):
        x=json.loads((DATA/'broker-access.local.json').read_text());self.base=x['base_url']
        self.client=httpx.Client(timeout=90,trust_env=False,headers={'X-Corpus-Key':x['capability']})
    def api(self,path,params=None):
        while True:
            r=self.client.get(self.base+'/github',params={'path':path,'params':json.dumps(params or {})});r.raise_for_status();x=r.json()
            if x.get('terminal'):raise RuntimeError('Broker stopped: '+x.get('error',''))
            headers=x.get('headers',{})
            if x['status'] in {403,429} and (x.get('retry_seconds') or headers.get('x-ratelimit-remaining')=='0' or headers.get('retry-after')):
                wait=x.get('retry_seconds') or max(1,float(headers.get('x-ratelimit-reset',time.time()+60))-time.time()+2)
                print('Rate checkpoint; waiting',round(wait),'seconds',flush=True)
                time.sleep(min(30,max(1,wait)));continue
            return x
    def post(self,path,value):
        r=self.client.post(self.base+path,json=value);r.raise_for_status();return r.json()
    def stats(self):return self.client.get(self.base+'/stats').json()

def catalog(agent):return json.loads((HERE.parent/f'domains-{agent}.json').read_text())
def shard(agent):return DATA/'shards'/agent

def discover(agent):
    broker=Broker();cat=catalog(agent)
    for d in cat['domains']:
        dest=shard(agent)/d['id']/'candidates.local.json'
        if dest.exists():print('Cached candidate queue',d['id'],flush=True);continue
        batches=[];queries=[]
        for i,q in enumerate(d['queries']):
            params={'q':q.get('query',q.get('q')),'per_page':min(30,q.get('per_page',30))}
            if q.get('sort') in {'stars','forks','help-wanted-issues','updated'}:params.update(sort=q['sort'],order=q.get('order','desc'))
            response=broker.api('/search/repositories',params);body=response.get('data') or {}
            record={'index':i,'query':params,'stratum':q.get('stratum','unknown'),'status':response['status'],'incomplete_results':body.get('incomplete_results'),'total_count':body.get('total_count')}
            queries.append(record)
            batches.append([(item,record) for item in body.get('items',[]) if item.get('private') is False and item.get('fork') is False])
        # Take results evenly across discovery channels, not only the first owner.
        queue=[];seen=set()
        for rank in range(30):
            for batch in batches:
                if rank>=len(batch):continue
                item,q=batch[rank]
                if item['id'] in seen:continue
                seen.add(item['id']);queue.append({'metadata':item,'query':q,'search_rank':rank+1})
                if len(queue)>=180:break
            if len(queue)>=180:break
        save(dest,{'agent':agent,'domain':d['id'],'queries':queries,'candidates':queue,'raw_search_results':sum(map(len,batches))})
        print('Discovered',d['id'],len(queue),'staged unique candidates from',len(queries),'queries',flush=True)

def store_file(broker,repo,commit,doc,role,maximum):
    if not isinstance(doc,dict) or doc.get('encoding')!='base64' or doc.get('size',maximum+1)>maximum:return None
    raw=base64.b64decode(doc.get('content',''),validate=False)
    if len(raw)>maximum or not raw or b'\0' in raw:return None
    path=PurePosixPath(doc['path'])
    if path.is_absolute() or '..' in path.parts:return None
    blob=hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
    if blob!=doc.get('sha'):raise SourceIntegrityError(doc,blob)
    dest=DATA/'sources'/str(repo['id'])/commit/str(path)
    broker.post('/source-bytes',{'key':str(dest.relative_to(DATA)),'bytes':len(raw)})
    dest.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(dest,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
    with os.fdopen(fd,'wb') as f:f.write(raw)
    text=raw.decode('utf-8',errors='replace')
    return {'path':str(path),'local_path':str(dest.relative_to(ROOT)),'role':role,'bytes':len(raw),'git_blob_sha':blob,
            'sha256':hashlib.sha256(raw).hexdigest(),'lines':len(text.splitlines()),'characters':len(text),
            'utf8_replacements':text.count('\ufffd'),'source_url':f"https://github.com/{repo['full_name']}/blob/{commit}/{quote(str(path))}",
            'app_input_channel':'README' if role=='README' else 'REFERENCE_ONLY'}

def collect_one(broker,agent,domain,candidate):
    name=candidate['metadata']['full_name'];endpoint='/repos/'+name
    metadata=broker.api(endpoint)
    if metadata['status']!=200:return None,'METADATA_'+str(metadata['status'])
    repo=metadata['data']
    if repo.get('private') is not False:return None,'NON_PUBLIC'
    claim=broker.post('/claim',{'id':repo['id'],'name':repo['full_name'],'domain':domain,'agent':agent})
    if not claim.get('claimed'):return None,'DUPLICATE_OR_OWNER_CAP'
    def fail(reason):broker.post('/finish',{'id':repo['id'],'agent':agent,'state':'REJECTED','reason':reason});return None,reason
    head=broker.api(endpoint+'/commits/'+quote(repo.get('default_branch') or 'HEAD',safe=''))
    if head['status']!=200:return fail('COMMIT_'+str(head['status']))
    commit=head['data']['sha'];response=broker.api(endpoint+'/readme',{'ref':commit})
    if response['status']!=200:return fail('README_'+str(response['status']))
    try:readme=store_file(broker,repo,commit,response['data'],'README',262144)
    except SourceIntegrityError as e:
        save(shard(agent)/domain/'integrity-exclusions'/f"{repo['id']}.local.json",{'repo':name,'commit':commit,**e.audit})
        return fail('README_GIT_BLOB_INTEGRITY_MISMATCH')
    if not readme:return fail('README_EMPTY_OVERSIZED_OR_NOT_TEXT')
    root=broker.api(endpoint+'/contents',{'ref':commit});items=root.get('data') if root['status']==200 else []
    items=items if isinstance(items,list) else []
    files={v['name'].lower():v for v in items if v.get('type')=='file'};chosen=[]
    # At most four supporting files, selected from an actual pinned directory listing.
    for prefix in ['architecture','overview','design','readme.','package.json','pyproject.toml','pom.xml','cargo.toml','go.mod','composer.json','gemfile','requirements.txt','license','copying']:
        for key,v in files.items():
            if key.startswith(prefix) and v['path']!=readme['path'] and v['path'] not in [z['path'] for z in chosen]:chosen.append(v)
        if len(chosen)>=3:break
    # A purpose/architecture document is more useful than indiscriminate code fetching.
    docs=next((v for v in items if v.get('type')=='dir' and v['name'].lower() in {'docs','doc','documentation'}),None)
    if docs and len(chosen)<4:
        listing=broker.api(endpoint+'/contents/'+quote(docs['path']),{'ref':commit})
        if listing['status']==200 and isinstance(listing.get('data'),list):
            candidates=[v for v in listing['data'] if v.get('type')=='file' and v['path']!=readme['path'] and v['path'] not in [z['path'] for z in chosen] and re.search(r'(architecture|overview|introduction|index|readme).*\.(md|rst|txt)$',v['name'],re.I)]
            if candidates:chosen.append(candidates[0])
    supporting=[];missing=[]
    for item in chosen[:4]:
        if item.get('size',0)>131072:missing.append({'path':item['path'],'reason':'OVERSIZED'});continue
        res=broker.api(endpoint+'/contents/'+quote(item['path']),{'ref':commit})
        try:f=store_file(broker,repo,commit,res.get('data'),'SUPPORTING',131072) if res['status']==200 else None
        except SourceIntegrityError as e:
            missing.append(e.audit)
            continue
        if f:supporting.append(f)
        else:missing.append({'path':item['path'],'reason':'UNAVAILABLE_OR_BOUNDED_OUT','status':res['status']})
    language=broker.api(endpoint+'/languages');langs=language.get('data') if language['status']==200 else None
    record={'numeric_id':repo['id'],'full_name':repo['full_name'],'url':repo['html_url'],'private':False,'source':'PUBLIC_GITHUB',
            'sampling_domain':domain,'collector_agent':agent,'status':'COLLECTED_PENDING_AGENT_REVIEW','description':repo.get('description'),
            'native_topics':repo.get('topics',[]),'primary_language':repo.get('language'),'languages_bytes':langs,
            'stars':repo['stargazers_count'],'fork':repo['fork'],'archived':repo['archived'],'owner':repo['owner']['login'],
            'license':repo.get('license'),'default_branch':repo['default_branch'],'commit':commit,'pushed_at':repo.get('pushed_at'),
            'readme':readme,'supporting_files':supporting,'supporting_exclusions':missing,'discovery':candidate['query'],
            'annotation_status':'PROPOSED','human_approved':False,'agent_read_coverage':{'readme':0,'supporting':0},
            'annotations':None,'retrieved_at_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    dest=shard(agent)/domain/'records'/f"{repo['id']}.local.json";save(dest,record)
    broker.post('/finish',{'id':repo['id'],'agent':agent,'state':'ACCEPTED','reason':'Complete pinned README and public identity verified; annotation pending'})
    return record,None

def harvest(agent,batch=None):
    broker=Broker();done=0
    for d in catalog(agent)['domains']:
        queue=shard(agent)/d['id']/'candidates.local.json'
        if not queue.exists():raise RuntimeError('Run discover first')
        folder=shard(agent)/d['id']/'records';records=[json.loads(p.read_text()) for p in folder.glob('*.local.json')] if folder.exists() else []
        existing={r['numeric_id'] for r in records if r.get('status') not in {'REJECTED','OFF_DOMAIN'}}
        rejected_path=shard(agent)/d['id']/'exclusions.local.json';rejected=json.loads(rejected_path.read_text()) if rejected_path.exists() else []
        attempted={r['id'] for r in rejected}|{r['numeric_id'] for r in records if r.get('status') in {'REJECTED','OFF_DOMAIN'}}
        for item in json.loads(queue.read_text())['candidates']:
            if len(existing)>=d.get('target',60):break
            ident=item['metadata']['id']
            if ident in existing or ident in attempted:continue
            try:r,error=collect_one(broker,agent,d['id'],item)
            except Exception as e:print('Collection stopped',d['id'],type(e).__name__,str(e)[:160],flush=True);raise
            if r:
                existing.add(r['numeric_id']);done+=1
                print('Collected',agent,d['id'],len(existing),'/',d.get('target',60),r['full_name'],r['readme']['bytes'],'README bytes',flush=True)
            else:
                rejected.append({'id':ident,'name':item['metadata']['full_name'],'reason':error});save(rejected_path,rejected)
            if batch and done>=batch:return
        print('Domain harvest',d['id'],len(existing),'/',d.get('target',60),flush=True)

def packet(agent,domain,start=0,count=5):
    records=sorted((shard(agent)/domain/'records').glob('*.local.json'))[start:start+count]
    for p in records:
        r=json.loads(p.read_text());print('\nREPOSITORY',r['full_name'],'ID',r['numeric_id'],'RECORD',p.relative_to(ROOT))
        print('METADATA',json.dumps({k:r[k] for k in ['description','native_topics','primary_language','stars','license']},ensure_ascii=False))
        for f in [r['readme']]+r['supporting_files']:
            print('\nFILE',f['path'],'SHA256',f['sha256'],'CHANNEL',f['app_input_channel'])
            text=(ROOT/f['local_path']).read_bytes().decode('utf-8',errors='replace')
            for i,line in enumerate(text.splitlines(),1):print(f'{i:05} {line}')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['discover','harvest','packet','stats']);p.add_argument('--agent',choices=list('abc'));p.add_argument('--domain');p.add_argument('--batch',type=int);p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=5);a=p.parse_args()
    if a.mode=='discover':discover(a.agent)
    elif a.mode=='harvest':harvest(a.agent,a.batch)
    elif a.mode=='packet':packet(a.agent,a.domain,a.start,a.count)
    else:print(json.dumps(Broker().stats(),indent=2))
