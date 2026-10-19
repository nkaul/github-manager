"""Assemble and verify the 120-second animation; all operations are local."""
import hashlib
import json
import sys
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "eval/relocation"))
from relocation_support import historical_bytes, historical_sha256, repo_path
OUT=ROOT/"demo/article-animation"
WORK=ROOT/"demo/work/article-animation"
DOC=ROOT/"eval/ai-system-design/animation"
FF=ROOT/".tools/video-python/imageio_ffmpeg/binaries/ffmpeg-macos-x86_64-v7.1"

def save(p,x):p.write_text(json.dumps(x,indent=2)+"\n")
def ff(args):
    p=subprocess.run([str(FF),"-hide_banner","-nostdin",*map(str,args)],capture_output=True)
    if p.returncode: raise RuntimeError(p.stderr.decode()[-1600:])
    return p
def stamp(t,comma=False):
    n=round(t*1000)
    return f"{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02}{',' if comma else '.'}{n%1000:03}"
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()

timing=json.loads((OUT/"timing.json").read_text())
render=json.loads((WORK/"render.json").read_text())
assert render["status"]=="PASS" and render["frames"]==3600
analysis=ff(["-i",WORK/"aligned.wav","-af","loudnorm=I=-16:TP=-2:LRA=11:print_format=json","-f","null","-"]).stderr.decode()
levels=json.JSONDecoder().raw_decode(analysis[analysis.rfind('{'):])[0]
norm=f"loudnorm=I=-16:TP=-2:LRA=11:measured_I={levels['input_i']}:measured_TP={levels['input_tp']}:measured_LRA={levels['input_lra']}:measured_thresh={levels['input_thresh']}:offset={levels['target_offset']}:linear=true"
video=OUT/"overview-1080p.mp4"
ff(["-loglevel","error","-y","-i",WORK/"picture.mp4","-i",WORK/"aligned.wav","-map","0:v:0","-map","1:a:0","-c:v","copy","-af",norm,"-ar","48000","-c:a","aac","-b:a","160k","-t","120","-movflags","+faststart",video])
ff(["-loglevel","error","-y","-i",video,"-vn","-c:a","copy",OUT/"narration.m4a"])

groups=[];current=[]
for word in timing["words"]:
    if current and (current[0]["scene"]!=word["scene"] or len(' '.join(w['word'] for w in current))>54 or len(current)>=9):
        groups.append(current);current=[]
    current.append(word)
    if re.search(r'[.!?]$',word['word']):groups.append(current);current=[]
if current:groups.append(current)
rows=[(g[0]['start'],max(g[-1]['end'],g[0]['start']+.2),' '.join(w['word'] for w in g)) for g in groups]
(OUT/"captions.vtt").write_text("WEBVTT\n\n"+'\n\n'.join(f"{stamp(a)} --> {stamp(b)}\n{s}" for a,b,s in rows)+'\n')
(OUT/"captions.srt").write_text('\n\n'.join(f"{i}\n{stamp(a,True)} --> {stamp(b,True)}\n{s}" for i,(a,b,s) in enumerate(rows,1))+'\n')
chapters=[{"id":s['id'],"title":s['heading'],"start":s['start'],"end":s['end']} for s in timing['segments']]
save(OUT/"chapters.json",chapters)

# Full decode, not just a header inspection.
decode=ff(["-v","error","-i",video,"-progress","pipe:1","-f","null","-"])
progress=dict(re.findall(r'^(\w+)=(.*)$',decode.stdout.decode(),re.M))
metadata=ff(["-i",video,"-t","0","-f","null","-"]).stderr.decode()
assert '1920x1080' in metadata and '30 fps' in metadata and 'h264' in metadata and 'aac' in metadata
assert int(progress.get('frame',0))==3600
audio=ff(["-i",video,"-vn","-af","loudnorm=I=-16:TP=-2:LRA=11:print_format=json","-f","null","-"]).stderr.decode()
actual=json.JSONDecoder().raw_decode(audio[audio.rfind('{'):])[0]
assert -17<=float(actual['input_i'])<=-15
assert float(actual['input_tp']) < -1
silence=ff(["-i",video,"-vn","-af","silencedetect=noise=-45dB:d=1","-f","null","-"]).stderr.decode()
silences=[float(x) for x in re.findall(r'silence_duration: ([\d.]+)',silence)]

assets=[]
for f in ["eval/ai-system-design/publication/figures/01-evidence-to-decisions.png","eval/ai-system-design/publication/v2/figures/01-two-ai-phases.png","eval/ai-system-design/publication/v2/figures/02-data-through-classification.png","docs/design/logo-variants-20261013/animated-v2/zen-loop-orbit-poster.png"]:
    assets.append({"file":f,"sha256":sha(ROOT/f),"use":"Read-only source; browser viewport composition, no raster modification"})
save(DOC/"assets-manifest.json",{"assets":assets,"new_raster_generation_requests":0,"additional_layers":"Code-native SVG cards, highlights, arrows, icons and state changes","font":"Locally installed Chalkboard; font binary not distributed"})

baseline=json.loads((DOC/"preservation-baseline.json").read_text())
changes = [r['file'] for r in baseline['files'] if not repo_path(r['file']).exists() or historical_sha256(repo_path(r['file'])) != r['sha256']]
preservation={"status":"PASS" if not changes else "CHANGED_REVIEW_REQUIRED","protected_files":len(baseline['files']),"changed":changes}
save(DOC/"preservation-qa.json",preservation)
manifest=json.loads((OUT/"speech-requests.json").read_text())
requests=manifest['requests'];accounted=sum(r.get('settled_usd',r['reserved_usd']) for r in requests)
report={"status":"PASS_TECHNICAL_PENDING_PLAYER_REVIEW","width":1920,"height":1080,"fps":30,"frames":3600,"duration_seconds":120,"codec":"H.264 / AAC","voice":"cedar","delivery":"Option D · calmer delivery","speech_time_stretch":False,"caption_cues":len(rows),"measured_spoken_wpm":timing['measured_spoken_wpm'],"script_token_agreement":timing['speech_script_token_agreement'],"neighbor_envelope_words":timing['neighbor_envelope_words'],"audio_lufs":float(actual['input_i']),"audio_true_peak_dbtp":float(actual['input_tp']),"longest_silence_seconds":max(silences,default=0),"full_decode":"PASS","provider_http_requests":len(requests),"media_accounted_usd":accounted,"accounting_note":"Conservative retained reservations, not reconciled billing","new_repository_model_calls":0,"preservation":preservation,"video_sha256":sha(video),"video_bytes":video.stat().st_size,"perceptual_review":"Technical checks do not establish listener preference; this pilot is for user feedback"}
save(OUT/"media-qa.json",report)
print(json.dumps(report,indent=2))
