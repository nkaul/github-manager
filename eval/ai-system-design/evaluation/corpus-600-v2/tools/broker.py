"""Credential-isolated, public-only GitHub reader with one shared audited allowance."""
import base64
from contextlib import contextmanager
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit, parse_qs

import httpx
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[5]
DATA = ROOT / 'docs/validation/private/corpus-600-v2'
DB = DATA / 'collection.sqlite3'
LIMIT, SEARCH_LIMIT, BYTE_LIMIT = 6000, 120, 512*1024**2
LOCK = threading.RLock()
DOMAINS = {'healthcare','finance','commerce','education','science','data','ai','cloud','security','developer'}


@contextmanager
def connection():
    c = sqlite3.connect(DB, timeout=30)
    c.row_factory = sqlite3.Row
    try:
        with c:yield c
    finally:c.close()


def private_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    fd = os.open(tmp, os.O_WRONLY|os.O_CREAT|os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as f: json.dump(value,f,indent=2);f.write('\n')
    os.replace(tmp,path);os.chmod(path,0o600)


def initialize():
    DATA.mkdir(parents=True,exist_ok=True);os.chmod(DATA,0o700)
    with connection() as c:
        c.executescript('''PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS requests(id INTEGER PRIMARY KEY, at REAL, path TEXT, params TEXT, resource TEXT, status INTEGER, headers TEXT, failure TEXT);
        CREATE TABLE IF NOT EXISTS cache(key TEXT PRIMARY KEY, path TEXT, status INTEGER, body TEXT, headers TEXT);
        CREATE TABLE IF NOT EXISTS public_repos(name TEXT PRIMARY KEY, id INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS claims(id INTEGER PRIMARY KEY, name TEXT, domain TEXT, agent TEXT, state TEXT, reason TEXT);
        CREATE TABLE IF NOT EXISTS source_bytes(key TEXT PRIMARY KEY, bytes INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS control(key TEXT PRIMARY KEY, value TEXT NOT NULL);''')
    os.chmod(DB,0o600)


def valid_path(path, params):
    if not isinstance(path,str) or '..' in unquote(path) or '?' in path or '#' in path: return False
    if path == '/rate_limit': return not params
    if path == '/search/repositories':
        return (isinstance(params.get('q'),str) and 'is:public' in params['q'].split() and
                set(params)<={'q','sort','order','per_page','page'} and 1<=int(params.get('per_page',30))<=100)
    m=re.fullmatch(r'/repos/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)(.*)',path)
    if not m: return False
    suffix=m[2]
    if suffix=='': return not params
    if suffix=='/languages': return not params
    if suffix in {'/readme','/contents'} or suffix.startswith('/contents/'):
        return set(params)<={'ref'} and bool(re.fullmatch('[a-f0-9]{40}',str(params.get('ref',''))))
    if suffix.startswith('/commits/'):
        return not params and bool(re.fullmatch(r'[A-Za-z0-9_.%/-]+',suffix[len('/commits/'):]))
    return False


def stats():
    with connection() as c:
        counts={r['domain']:r['n'] for r in c.execute("SELECT domain,count(*) n FROM claims WHERE state='ACCEPTED' GROUP BY domain")}
        return {'http_attempts':c.execute('SELECT count(*) FROM requests').fetchone()[0],
                'search_attempts':c.execute("SELECT count(*) FROM requests WHERE resource='search'").fetchone()[0],
                'cache_entries':c.execute('SELECT count(*) FROM cache').fetchone()[0],
                'retained_source_bytes':c.execute('SELECT coalesce(sum(bytes),0) FROM source_bytes').fetchone()[0],
                'accepted':counts,'accepted_total':sum(counts.values()),
                'claimed_total':c.execute('SELECT count(*) FROM claims').fetchone()[0],
                'limits':{'http':LIMIT,'search':SEARCH_LIMIT,'source_bytes':BYTE_LIMIT}}


class Reader:
    def __init__(self):
        cfg=dotenv_values(ROOT/'backend/.env')
        if not cfg.get('GITHUB_CLIENT_ID') or not cfg.get('GITHUB_CLIENT_SECRET'): raise RuntimeError('Missing OAuth App configuration')
        self.client=httpx.Client(auth=httpx.BasicAuth(cfg['GITHUB_CLIENT_ID'],cfg['GITHUB_CLIENT_SECRET']),
            timeout=25,follow_redirects=False,trust_env=False,headers={'Accept':'application/vnd.github+json',
            'X-GitHub-Api-Version':'2026-03-10','User-Agent':'github-manager-corpus600-public-readonly'})
        self.last=0;self.search_last=0

    def get(self,path,params):
        if not valid_path(path,params):return {'status':400,'error':'Endpoint or public query rejected'}
        key=hashlib.sha256(json.dumps([path,params],sort_keys=True).encode()).hexdigest()
        resource='search' if path=='/search/repositories' else 'core'
        with LOCK:
            with connection() as c:
                old=c.execute('SELECT * FROM cache WHERE key=?',(key,)).fetchone()
                if old:return {'status':old['status'],'data':json.loads(old['body']),'headers':json.loads(old['headers']),'cached':True}
                match=re.match(r'/repos/([^/]+/[^/]+)(/.*)',path)
                if match and not c.execute('SELECT 1 FROM public_repos WHERE name=?',(match[1],)).fetchone():
                    return {'status':403,'error':'Public metadata must be verified first'}
                s=stats()
                if s['http_attempts']>=LIMIT or (resource=='search' and s['search_attempts']>=SEARCH_LIMIT):
                    return {'status':429,'error':'Approved request ceiling reached','terminal':True}
                halted=c.execute("SELECT value FROM control WHERE key='halt'").fetchone()
                if halted:return {'status':503,'error':halted[0],'terminal':True}
                waits=c.execute("SELECT value FROM control WHERE key IN (?,?)",('wait-global','wait-'+resource)).fetchall()
                wait_until=max([float(r[0]) for r in waits]+[0])
                if wait_until>time.time():return {'status':429,'error':'Rate-limited checkpoint','retry_seconds':round(wait_until-time.time()+1,2)}
            # Serial upstream GETs, conservatively <=25 repository searches/minute.
            time.sleep(max(0,.08-(time.monotonic()-self.last),2.5-(time.monotonic()-self.search_last) if resource=='search' else 0))
            with connection() as c:
                cur=c.execute('INSERT INTO requests(at,path,params,resource,status) VALUES(?,?,?,?,NULL)',(time.time(),path,json.dumps(params),resource));rid=cur.lastrowid
            headers={};status=None;failure=None;body=None
            try:
                with self.client.stream('GET','https://api.github.com'+path,params=params) as r:
                    status=r.status_code
                    headers={k:r.headers[k] for k in ['x-ratelimit-limit','x-ratelimit-remaining','x-ratelimit-reset','x-ratelimit-resource','retry-after','etag','last-modified'] if k in r.headers}
                    raw=bytearray()
                    for chunk in r.iter_bytes():
                        raw.extend(chunk)
                        if len(raw)>2_500_000:raise ValueError('Bounded GitHub response exceeded')
                    body=json.loads(raw) if status==200 else None
            except (httpx.RequestError,ValueError) as e:failure=type(e).__name__
            self.last=time.monotonic()
            if resource=='search':self.search_last=self.last
            with connection() as c:
                c.execute('UPDATE requests SET status=?,headers=?,failure=? WHERE id=?',(status,json.dumps(headers),failure,rid))
                if status in {401,403} and 'retry-after' not in headers and headers.get('x-ratelimit-remaining')!='0':
                    # A forbidden individual resource is reported, not retried. Authentication failure stops globally.
                    if status==401:c.execute("INSERT OR REPLACE INTO control VALUES('halt','GitHub authentication rejected')")
                if status in {403,429} and ('retry-after' in headers or headers.get('x-ratelimit-remaining')=='0'):
                    until=time.time()+float(headers.get('retry-after',60))
                    if headers.get('x-ratelimit-remaining')=='0':until=max(until,float(headers.get('x-ratelimit-reset',until))+2)
                    c.execute('INSERT OR REPLACE INTO control VALUES(?,?)',('wait-global' if 'retry-after' in headers else 'wait-'+resource,str(until)))
                if failure:return {'status':502,'error':'Transport or bounded-response failure','failure_type':failure,'request_id':rid}
                if status==200:
                    ismeta=bool(re.fullmatch(r'/repos/[^/]+/[^/]+',path))
                    if ismeta:
                        if body.get('private') is not False or body.get('visibility','public')!='public':return {'status':403,'error':'Non-public data rejected'}
                        name=path[len('/repos/'):];c.execute('INSERT OR REPLACE INTO public_repos VALUES(?,?)',(name,body['id']))
                    if resource=='search' and any(x.get('private') is not False for x in body.get('items',[])):
                        return {'status':403,'error':'Non-public search result rejected'}
                    c.execute('INSERT OR REPLACE INTO cache VALUES(?,?,?,?,?)',(key,path,status,json.dumps(body),json.dumps(headers)))
            return {'status':status or 502,'data':body,'headers':headers,'cached':False,'request_id':rid}


class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def reply(self,x,status=200):
        b=json.dumps(x).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
    def authorized(self):return hmac.compare_digest(self.headers.get('X-Corpus-Key',''),self.server.key)
    def do_GET(self):
        if not self.authorized():return self.reply({'error':'Local capability required'},403)
        parts=urlsplit(self.path)
        if parts.path=='/stats':return self.reply(stats())
        if parts.path!='/github':return self.reply({'error':'Not found'},404)
        try:
            q=parse_qs(parts.query);params=json.loads(q.get('params',['{}'])[0]);path=q['path'][0]
            if not isinstance(params,dict):raise ValueError()
            self.reply(self.server.reader.get(path,params))
        except (ValueError,KeyError):self.reply({'error':'Invalid local request'},400)
    def do_POST(self):
        if not self.authorized():return self.reply({'error':'Local capability required'},403)
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<20000:raise ValueError()
            x=json.loads(self.rfile.read(size))
            with LOCK,connection() as c:
                if self.path=='/claim':
                    if x['domain'] not in DOMAINS or x['agent'] not in {'a','b'} or not isinstance(x['id'],int):raise ValueError()
                    row=c.execute('SELECT * FROM claims WHERE id=?',(x['id'],)).fetchone()
                    if row:return self.reply({'claimed':row['agent']==x['agent'] and row['domain']==x['domain'],'existing':dict(row)})
                    owner=x['name'].split('/')[0].lower()
                    owner_count=c.execute("SELECT count(*) FROM claims WHERE lower(substr(name,1,instr(name,'/')-1))=? AND state IN ('ACCEPTED','COLLECTING')",(owner,)).fetchone()[0]
                    if owner_count>=30:return self.reply({'claimed':False,'reason':'OWNER_CAP_30'})
                    domain_count=c.execute("SELECT count(*) FROM claims WHERE domain=? AND state IN ('ACCEPTED','COLLECTING')",(x['domain'],)).fetchone()[0]
                    if domain_count>=60:return self.reply({'claimed':False,'reason':'DOMAIN_TARGET_REACHED'})
                    c.execute('INSERT INTO claims VALUES(?,?,?,?,?,?)',(x['id'],x['name'],x['domain'],x['agent'],'COLLECTING',''))
                    return self.reply({'claimed':True})
                if self.path=='/finish':
                    if x['state'] not in {'ACCEPTED','REJECTED'}:raise ValueError()
                    c.execute('UPDATE claims SET state=?,reason=? WHERE id=? AND agent=?',(x['state'],x.get('reason',''),x['id'],x['agent']))
                    return self.reply({'saved':True})
                if self.path=='/source-bytes':
                    if not isinstance(x['bytes'],int) or x['bytes']<0:raise ValueError()
                    old=c.execute('SELECT bytes FROM source_bytes WHERE key=?',(x['key'],)).fetchone()
                    total=c.execute('SELECT coalesce(sum(bytes),0) FROM source_bytes').fetchone()[0]
                    if total+(0 if old else x['bytes'])>BYTE_LIMIT:return self.reply({'error':'Source content ceiling reached'},409)
                    c.execute('INSERT OR IGNORE INTO source_bytes VALUES(?,?)',(x['key'],x['bytes']))
                    return self.reply({'saved':True})
            self.reply({'error':'Not found'},404)
        except (KeyError,ValueError,json.JSONDecodeError):self.reply({'error':'Invalid local mutation'},400)


if __name__=='__main__':
    initialize();reader=Reader();server=ThreadingHTTPServer(('127.0.0.1',8767),Handler)
    server.reader=reader;server.key=secrets.token_urlsafe(32)
    private_json(DATA/'broker-access.local.json',{'base_url':'http://127.0.0.1:8767','capability':server.key,'pid':os.getpid()})
    print('Public GitHub collector listening on 127.0.0.1:8767; authenticated credentials isolated',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:reader.client.close();server.server_close()
