"""Offline safety checks: no GitHub credentials, sockets or paid model calls."""
import base64
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor

import httpx
import broker
import collect


def blob(path, raw):
    return {'path':path,'type':'file','encoding':'base64','size':len(raw),
            'content':base64.b64encode(raw).decode(),
            'sha':hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()}


class CollectionSafety(unittest.TestCase):
    def test_public_paths_and_pinned_content_only(self):
        self.assertTrue(broker.valid_path('/search/repositories',{'q':'is:public topic:science'}))
        self.assertFalse(broker.valid_path('/search/repositories',{'q':'topic:science'}))
        self.assertFalse(broker.valid_path('/repos/o/r/contents/README.md',{'ref':'main'}))
        self.assertFalse(broker.valid_path('/repos/o/r/contents/%2e%2e/x',{'ref':'a'*40}))
        self.assertFalse(broker.valid_path('/repos/o/r/issues',{}))
        self.assertTrue(broker.valid_path('/repos/o/r/readme',{'ref':'a'*40}))

    def test_integrity_failure_writes_no_source(self):
        with tempfile.TemporaryDirectory() as d, patch.object(collect,'ROOT',Path(d)), patch.object(collect,'DATA',Path(d)/'data'):
            class Sink:
                def post(self,*args):raise AssertionError('Integrity failure must not reserve bytes')
            doc=blob('README.md',b'Complete README\n');doc['sha']='0'*40
            with self.assertRaises(collect.SourceIntegrityError) as ctx:
                collect.store_file(Sink(),{'id':1,'full_name':'o/r'},'a'*40,doc,'README',100)
            self.assertEqual(ctx.exception.audit['expected_git_blob_sha'],'0'*40)
            self.assertFalse((Path(d)/'data/sources').exists())

    def test_valid_source_is_complete_and_hashed(self):
        with tempfile.TemporaryDirectory() as d, patch.object(collect,'ROOT',Path(d)), patch.object(collect,'DATA',Path(d)/'data'):
            calls=[]
            class Sink:
                def post(self,path,value):calls.append((path,value));return {'saved':True}
            raw='Purpose\nUnicode: λ\n'.encode();doc=blob('README.md',raw)
            result=collect.store_file(Sink(),{'id':1,'full_name':'o/r'},'a'*40,doc,'README',100)
            self.assertEqual((Path(d)/result['local_path']).read_bytes(),raw)
            self.assertEqual(result['sha256'],hashlib.sha256(raw).hexdigest())
            self.assertEqual(calls[0][1]['bytes'],len(raw))
            self.assertIsNone(collect.store_file(Sink(),{'id':1,'full_name':'o/r'},'a'*40,doc,'README',2))

    def test_optional_mismatch_is_audited_not_accepted(self):
        with tempfile.TemporaryDirectory() as d, patch.object(collect,'ROOT',Path(d)), patch.object(collect,'DATA',Path(d)/'data'):
            readme=blob('README.md',b'# Product\nPurpose evidence\n');bad=blob('go.mod',b'module example.org/r\n');bad['sha']='0'*40
            repo={'id':1,'full_name':'o/r','private':False,'default_branch':'main','html_url':'https://github.com/o/r','description':'product','topics':[],
                  'language':'Go','stargazers_count':1,'fork':False,'archived':False,'owner':{'login':'o'},'license':None,'pushed_at':'2026-01-01T00:00:00Z'}
            class Fake:
                def __init__(self):self.finish=[]
                def api(self,path,params=None):
                    if path=='/repos/o/r':data=repo
                    elif '/commits/' in path:data={'sha':'a'*40}
                    elif path.endswith('/readme'):data=readme
                    elif path.endswith('/contents'):data=[{'name':'go.mod','path':'go.mod','type':'file','size':bad['size']}]
                    elif path.endswith('/contents/go.mod'):data=bad
                    elif path.endswith('/languages'):data={'Go':1}
                    else:raise AssertionError(path)
                    return {'status':200,'data':data}
                def post(self,path,value):
                    if path=='/claim':return {'claimed':True}
                    if path=='/finish':self.finish.append(value)
                    return {'saved':True}
            fake=Fake();result,error=collect.collect_one(fake,'a','healthcare',{'metadata':repo,'query':{}})
            self.assertIsNone(error);self.assertEqual(result['supporting_files'],[])
            self.assertEqual(result['supporting_exclusions'][0]['reason'],'GIT_BLOB_INTEGRITY_MISMATCH')
            self.assertFalse((Path(d)/'data/sources/1'/('a'*40)/'go.mod').exists())
            self.assertEqual(fake.finish[-1]['state'],'ACCEPTED')

    def test_shared_limit_is_atomic_and_cache_does_not_spend(self):
        with tempfile.TemporaryDirectory() as d, patch.object(broker,'DATA',Path(d)), patch.object(broker,'DB',Path(d)/'collection.sqlite3'), patch.object(broker,'LIMIT',4):
            (Path(d)/'authentication.local.json').write_text(json.dumps({'status':'PASS','checks':[{'endpoint':'/rate_limit','status':200,'headers':{}}]*3}))
            broker.initialize();upstream=[]
            def transport(request):
                upstream.append(str(request.url));return httpx.Response(200,json={'id':1,'private':False,'visibility':'public'},headers={'x-ratelimit-remaining':'4999'})
            reader=broker.Reader.__new__(broker.Reader);reader.client=httpx.Client(transport=httpx.MockTransport(transport));reader.last=0;reader.search_last=0
            try:
                with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda p:reader.get(p,{}),['/repos/o/a','/repos/o/b']))
                self.assertEqual(sorted(r['status'] for r in results),[200,429]);self.assertEqual(len(upstream),1)
                successful=upstream[0].split('https://api.github.com')[1]
                replay=reader.get(successful,{})
                self.assertTrue(replay['cached']);self.assertEqual(len(upstream),1)
                self.assertEqual(broker.stats()['http_attempts'],4)
            finally:reader.client.close()

    def test_nested_primary_readme_is_not_fetched_again_as_support(self):
        with tempfile.TemporaryDirectory() as d, patch.object(collect,'ROOT',Path(d)), patch.object(collect,'DATA',Path(d)/'data'):
            repo={'id':1,'full_name':'o/r','private':False,'default_branch':'main','html_url':'https://github.com/o/r',
                  'stargazers_count':1,'fork':False,'archived':False,'owner':{'login':'o'}}
            readme=blob('docs/README.md',b'# Browser editor\nPurpose evidence\n')
            class Fake:
                def api(self,path,params=None):
                    if path=='/repos/o/r':data=repo
                    elif '/commits/' in path:data={'sha':'a'*40}
                    elif path.endswith('/readme'):data=readme
                    elif path.endswith('/contents'):data=[{'name':'docs','path':'docs','type':'dir'}]
                    elif path.endswith('/contents/docs'):data=[{'name':'README.md','path':'docs/README.md','type':'file','size':readme['size']}]
                    elif path.endswith('/languages'):data={}
                    else:raise AssertionError('Unexpected repeated README content request: '+path)
                    return {'status':200,'data':data}
                def post(self,path,value):return {'claimed':True,'saved':True}
            result,error=collect.collect_one(Fake(),'c','developer',{'metadata':repo,'query':{}})
            self.assertIsNone(error)
            self.assertEqual(result['supporting_files'],[])
            self.assertEqual(result['readme']['role'],'README')


if __name__=='__main__':unittest.main()
