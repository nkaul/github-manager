"""Bounded Cedar pilot speech/alignment. Only the fixed public script/audio leave localhost."""
import argparse
import hashlib
import json
import re
import sqlite3
import subprocess
import wave
from datetime import datetime, UTC
from difflib import SequenceMatcher
from pathlib import Path

import httpx
import numpy as np
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / "demo/work/article-animation"
OUT = ROOT / "demo/article-animation"
STORY = json.loads(Path(__file__).with_name("story.json").read_text())
FF = ROOT / ".tools/video-python/imageio_ffmpeg/binaries/ffmpeg-macos-x86_64-v7.1"
MANIFEST = OUT / "speech-requests.json"

def save(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2) + "\n")
    tmp.replace(p)

def ff(args):
    p = subprocess.run([str(FF), "-hide_banner", "-nostdin", *map(str,args)], capture_output=True)
    if p.returncode: raise RuntimeError(p.stderr.decode()[-1200:])
    return p

def fingerprint(value):
    return hashlib.sha256(value).hexdigest()

def budget():
    with sqlite3.connect(f"file:{ROOT / 'docs/validation/private/ai-pretest/runs.sqlite3'}?mode=ro", uri=True) as db:
        cap = db.execute("SELECT cap FROM experiment").fetchone()[0] / 1e6
        used = db.execute("SELECT COALESCE(SUM(COALESCE(charged,reserved)),0) FROM calls").fetchone()[0] / 1e6
        holds = db.execute("SELECT COALESCE(SUM(remaining),0) FROM app_run_budgets WHERE state IN ('HELD','QUEUED','RUNNING')").fetchone()[0] / 1e6
        count = db.execute("SELECT COUNT(*) FROM calls").fetchone()[0]
    copy = ROOT / "docs/validation/private/demo/full-v2/ai/runs.sqlite3"
    with sqlite3.connect(f"file:{copy}?mode=ro", uri=True) as db:
        copy_used = db.execute("SELECT COALESCE(SUM(COALESCE(charged,reserved)),0) FROM calls").fetchone()[0]
    prior_media = 0
    for p in [ROOT / "demo/voice-preview-v2/speech-requests.json", ROOT / "demo/full-v2/speech-requests.json"]:
        rows = json.loads(p.read_text())["requests"]
        prior_media += sum(r.get("settled_usd", r.get("reserved_usd",0)) for r in rows)
    return {"cap_usd": min(5,cap), "prior_accounted_usd": used + max(0, copy_used-127619)/1e6 + prior_media,
            "active_holds_usd": holds, "prior_generation_rows": count}

def request(ident, endpoint, model, bound, *, body=None, audio=None, method="POST"):
    data = MANIFEST.exists() and json.loads(MANIFEST.read_text()) or {"cap_usd": STORY["media_cap_usd"], "max_http_requests": STORY["max_http_requests"], "requests": []}
    raw = audio.read_bytes() if audio else json.dumps(body,sort_keys=True).encode()
    digest = fingerprint(raw)
    existing = next((r for r in data["requests"] if r["id"] == ident),None)
    if existing:
        if existing["input_sha256"] != digest or existing["state"] != "SUCCEEDED":
            raise RuntimeError("Prior request input changed or outcome unresolved; no silent retry")
        return None
    snap = budget()
    accounted = sum(r.get("settled_usd",r["reserved_usd"]) for r in data["requests"])
    if len(data["requests"]) >= STORY["max_http_requests"]: raise RuntimeError("Pilot HTTP cap reached")
    if accounted + bound > STORY["media_cap_usd"] + 1e-9: raise RuntimeError("Pilot media cap reached")
    if snap["prior_accounted_usd"] + snap["active_holds_usd"] + accounted + bound > snap["cap_usd"] + 1e-9:
        raise RuntimeError("Existing cumulative ceiling reached")
    row = {"id":ident,"endpoint":endpoint,"method":method,"model":model,"input_sha256":digest,
           "reserved_usd":bound,"state":"RESERVED","at":datetime.now(UTC).isoformat(),"prior_budget":snap}
    data["requests"].append(row); save(MANIFEST,data)
    key = dotenv_values(ROOT / "backend/.env").get("OPENAI_API_KEY")
    if not key:
        row["state"]="LOCAL_CREDENTIAL_MISSING";save(MANIFEST,data);raise RuntimeError("Configured OpenAI key missing")
    try:
        with httpx.Client(timeout=180,trust_env=False,follow_redirects=False) as client:
            headers={"Authorization":"Bearer "+key}
            url="https://api.openai.com/v1/"+endpoint
            if method=="GET":
                r=client.get(url,headers=headers)
            elif audio:
                with audio.open("rb") as stream:
                    r=client.post(url,headers=headers,data={"model":model,"language":"en","response_format":"verbose_json","timestamp_granularities[]":"word","temperature":"0"},files={"file":("github-manager-public-narration.mp3",stream,"audio/mpeg")})
            else:
                r=client.post(url,headers=headers,json=body)
        row.update(http_status=r.status_code,request_id=r.headers.get("x-request-id"))
        if r.status_code != 200:
            row["state"]="FAILED_REVIEW_REQUIRED"
            try: row["error_code"]=r.json().get("error",{}).get("code","unspecified")
            except ValueError: row["error_code"]="non_json"
            save(MANIFEST,data)
            raise RuntimeError(f"Provider HTTP {r.status_code}; sanitized manifest saved")
        row.update(state="SUCCEEDED",response_sha256=fingerprint(r.content),bytes=len(r.content))
        if method=="GET": row["settled_usd"]=0
        save(MANIFEST,data)
        return r
    except Exception:
        if row["state"]=="RESERVED": row["state"]="UNKNOWN_REVIEW_REQUIRED"
        save(MANIFEST,data)
        raise

def check():
    r=request("availability", "models/"+STORY["model"],STORY["model"],0,body={"model":STORY["model"]},method="GET")
    if r is not None: save(WORK / "availability.json",{"model":r.json().get("id"),"status":"AVAILABLE"})
    print("Narration model available; no generation performed by this check")

def generate(take):
    review=WORK / "visual-rehearsal.json"
    if not review.exists() or json.loads(review.read_text()).get("status")!="PASS":
        raise RuntimeError("Complete offline visual rehearsal before paid narration")
    frozen=WORK / "frozen-story.json"
    if frozen.exists() and json.loads(frozen.read_text()) != STORY: raise RuntimeError("Frozen story changed")
    save(frozen,STORY)
    script="\n\n".join(s["text"] for s in STORY["segments"])
    instructions=("Read exactly the supplied script as a warm, thoughtful product guide, in the calm Cedar delivery chosen in Option D. "
       "Use natural clear US English, consistent volume, gentle emphasis and unhurried clause pauses. Aim near 135 words per minute. "
       "Leave a short natural pause between paragraphs. Avoid theatrical announcer energy and excessive breathiness. "
       "Pronounce GitHub as Git Hub, README as read me, API as A P I, FastAPI as fast A P I, Orion as oh RYE un. "
       "Do not add any introduction, commentary, closing line, or timing markers. Read the final sentence completely.")
    r=request("tts-"+take,"audio/speech",STORY["model"],.12,body={"model":STORY["model"],"voice":"cedar","input":script,"instructions":instructions,"response_format":"wav","speed":STORY["speed"]})
    p=WORK / (take+".wav")
    if r is not None:
        (WORK / (take+"-provider.wav")).write_bytes(r.content)
        p.write_bytes(r.content)
        with wave.open(str(p)) as w:
            params=w.getparams();pcm=w.readframes(w.getnframes())
        with wave.open(str(p),"wb") as w:
            w.setparams((params.nchannels,params.sampwidth,params.framerate,0,params.comptype,params.compname));w.writeframes(pcm)
    if not p.exists(): raise RuntimeError("Saved successful audio missing; do not repeat provider request")
    with wave.open(str(p)) as w: print("Narration seconds:",round(w.getnframes()/w.getframerate(),3))

def expand(word):
    w=re.sub(r"[^a-z0-9]","",word.lower())
    return {"github":["git","hub"],"readme":["read","me"],"fastapi":["fast","api"],"apis":["api"]}.get(w,[w])

def repair_ending():
    """A targeted same-voice take restores a TTS-omitted final sentence."""
    text=STORY['segments'][-1]['text']+'\n\nThis is the end of the recording.'
    direction=("Read exactly the supplied script as a warm, thoughtful product guide, in the calm Cedar delivery chosen in Option D. "
       "Use natural clear US English, consistent volume, gentle emphasis and unhurried clause pauses. Aim near 135 words per minute. "
       "Leave a short natural pause between paragraphs. Avoid theatrical announcer energy and excessive breathiness. "
       "Read every supplied sentence completely, including the final timing marker after a pause. Do not add words.")
    r=request('tts-ending-repair','audio/speech',STORY['model'],.08,body={'model':STORY['model'],'voice':'cedar','input':text,'instructions':direction,'response_format':'wav','speed':STORY['speed']})
    repair=WORK/'cedar-ending.wav'
    if r is not None:
        (WORK/'cedar-ending-provider.wav').write_bytes(r.content);repair.write_bytes(r.content)
        with wave.open(str(repair)) as w:params=w.getparams();pcm=w.readframes(w.getnframes())
        with wave.open(str(repair),'wb') as w:w.setparams((params.nchannels,params.sampwidth,params.framerate,0,params.comptype,params.compname));w.writeframes(pcm)
    mp3=repair.with_suffix('.mp3');ff(['-loglevel','error','-y','-i',repair,'-ar','16000','-b:a','64k',mp3])
    r=request('align-ending-repair','audio/transcriptions','whisper-1',.03,audio=mp3)
    target=WORK/'cedar-ending-asr.json'
    if r is not None:save(target,r.json())
    repaired=json.loads(target.read_text())['words']
    original=json.loads((WORK/'cedar-v1-asr.json').read_text())['words']
    first=next(i for i,w in enumerate(repaired) if w['word'].lower().strip('.,')=='every')
    last=next(i for i,w in enumerate(repaired) if w['word'].lower().strip('.,')=='yours')
    source_first=next(i for i,w in enumerate(original) if w['word'].lower().strip('.,')=='every')
    a=max(0,repaired[first]['start']-.18);b=repaired[last]['end']+.22
    cut=max(0,original[source_first]['start']-.18)
    with wave.open(str(WORK/'cedar-v1.wav')) as w:rate=w.getframerate();old=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16)
    with wave.open(str(repair)) as w:
        assert w.getframerate()==rate and w.getnchannels()==1
        new=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16)
    joined=np.concatenate([old[:round(cut*rate)],new[round(a*rate):round(b*rate)]])
    with wave.open(str(WORK/'cedar-complete.wav'),'wb') as w:w.setparams((1,2,rate,0,'NONE','not compressed'));w.writeframes(joined.tobytes())
    merged=original[:source_first]+[{**w,'start':cut+w['start']-a,'end':cut+w['end']-a} for w in repaired[first:last+1]]
    save(WORK/'cedar-complete-asr.json',{'words':merged,'provenance':'Original recognized speech plus targeted same-voice ending; final timing marker excluded'})
    save(WORK/'ending-repair.json',{'reason':'Original TTS omitted the final five-word sentence; raw audio ended after belongs', 'same_voice':'cedar','same_speed':STORY['speed'],'source_cut_seconds':cut,'repair_interval_seconds':[a,b],'timing_marker_removed':True,'speech_time_stretch':False})
    print('Targeted ending repaired; final sentence and timing-marker boundary recognized.')

def align(take,offline=False):
    wav=WORK/(take+".wav");mp3=wav.with_suffix(".mp3")
    ff(["-loglevel","error","-y","-i",wav,"-ar","16000","-b:a","64k",mp3])
    target=WORK/(take+"-asr.json")
    if not offline:
        r=request("align-"+take,"audio/transcriptions","whisper-1",.06,audio=mp3)
        if r is not None: save(target,r.json())
    elif not target.exists(): raise RuntimeError('Offline alignment requires saved word-timing provenance')
    observed=json.loads(target.read_text())["words"]
    expected=[];expected_words=[];owners=[]
    for scene in STORY["segments"]:
        for word in scene["text"].split():
            expected_words.append({"word":word,"scene":scene["id"]})
            for token in expand(word): expected.append(token);owners.append(len(expected_words)-1)
    obs=[];obs_owners=[]
    for i,w in enumerate(observed):
        for t in expand(w["word"]): obs.append(t);obs_owners.append(i)
    sm=SequenceMatcher(None,expected,obs,autojunk=False)
    matched={a+i:obs_owners[b+i] for a,b,n in sm.get_matching_blocks() for i in range(n)}
    ratio=len(matched)/len(expected)
    save(WORK/(take+"-alignment-review.json"),{"agreement":ratio,"expected_tokens":expected,"observed_tokens":obs,"opcodes":sm.get_opcodes()})
    if ratio < .99: raise RuntimeError(f"Speech/script agreement {ratio:.3f}; inspect before rendering")
    if len(expected)-1 not in matched: raise RuntimeError('Final spoken word missing; do not invent a closing timestamp')
    mapped={}
    for i,o in enumerate(owners):
        if i in matched: mapped.setdefault(o,[]).append(observed[matched[i]])
    for i,w in enumerate(expected_words):
        rows=mapped.get(i)
        if rows:
            w.update(start=min(x["start"] for x in rows),end=max(x["end"] for x in rows),timing="ASR_MATCHED")
        else:
            prev=max((j for j in mapped if j<i),default=None);nxt=min((j for j in mapped if j>i),default=None)
            a=max(x["end"] for x in mapped[prev]) if prev is not None else 0
            b=min(x["start"] for x in mapped[nxt]) if nxt is not None else a+.3
            w.update(start=a,end=max(a+.04,b),timing="NEIGHBOR_ENVELOPE")
    with wave.open(str(wav)) as w:
        rate=w.getframerate();pcm=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16);params=w.getparams()
    groups=[]
    for scene in STORY["segments"]:
        words=[w for w in expected_words if w["scene"]==scene["id"]]
        groups.append((scene,words))
    boundaries=[max(0,groups[0][1][0]["start"]-.2)]
    for (_,before),(_,after) in zip(groups,groups[1:]):
        boundaries.append((before[-1]["end"]+after[0]["start"])/2)
    boundaries.append(min(len(pcm)/rate,groups[-1][1][-1]["end"]+.25))
    lengths=[boundaries[i+1]-boundaries[i] for i in range(len(groups))]
    room=120-sum(lengths)-.6
    if room < 3: raise RuntimeError("Narration leaves insufficient reading space for 120-second pilot; review a retake")
    weights=[1.2,1,1,1.2,1.1,1.2,1.3,1.5]
    track=np.zeros(round(120*rate),dtype=np.int16);segments=[];words=[];cursor=0
    for i,(scene,items) in enumerate(groups):
        a,b=boundaries[i:i+2];clip=pcm[round(a*rate):round(b*rate)]
        hold=room*weights[i]/sum(weights);lead=.25 if i else .6
        if i: hold-=.25
        span=len(clip)/rate+lead+max(0,hold)
        audio_start=cursor+lead
        start=round(audio_start*rate);track[start:start+len(clip)]=clip
        local=[{**w,"start":audio_start+w["start"]-a,"end":audio_start+w["end"]-a} for w in items]
        cues={}
        for cue in scene["cues"]:
            needle=[t for w in cue.split() for t in expand(w)]
            hay=[];idx=[]
            for k,w in enumerate(local):
                for t in expand(w["word"]):hay.append(t);idx.append(k)
            positions=[k for k in range(len(hay)) if hay[k:k+len(needle)]==needle]
            if not positions: raise RuntimeError("Missing animation phrase: "+cue)
            cues[cue]=local[idx[positions[0]]]["start"]
        segments.append({**scene,"start":cursor,"end":cursor+span,"audio_start":audio_start,"audio_end":audio_start+len(clip)/rate,"cues":cues})
        words.extend(local);cursor+=span
    segments[-1]["end"]=120
    assert cursor <= 120.02,(cursor,room)
    with wave.open(str(WORK/"aligned.wav"),"wb") as w:
        w.setparams((1,2,rate,0,"NONE","not compressed"));w.writeframes(track.tobytes())
    timing={"duration":120,"voice":"cedar","delivery":"Option D · calmer delivery","speed":STORY["speed"],"segments":segments,"words":words,"speech_time_stretch":False,"source_take":take,"source_audio_seconds":len(pcm)/rate,"speech_script_token_agreement":ratio,"neighbor_envelope_words":sum(w["timing"]!="ASR_MATCHED" for w in words),"measured_spoken_wpm":len(expected_words)/(sum(lengths)/60),"source_audio_sha256":fingerprint(wav.read_bytes())}
    save(OUT/"timing.json",timing);save(WORK/"timing.json",timing)
    print(json.dumps({k:timing[k] for k in ["duration","source_audio_seconds","speech_script_token_agreement","neighbor_envelope_words","measured_spoken_wpm"]},indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=["check","generate","align","repair-ending"]);p.add_argument("--take",default="cedar-v1");p.add_argument('--offline',action='store_true');a=p.parse_args()
    if a.mode=="check": check()
    elif a.mode=="generate": generate(a.take)
    elif a.mode=='repair-ending': repair_ending()
    else: align(a.take,a.offline)
