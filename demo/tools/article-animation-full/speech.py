"""Seven slower Cedar takes, bounded timing calls, and source-aligned chapter audio."""
import argparse,hashlib,importlib.util,json,math,re,wave
from difflib import SequenceMatcher
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
WORK=ROOT/'demo/work/article-animation-full';OUT=ROOT/'demo/article-animation-full'
STORY=json.loads((HERE/'story.json').read_text());TAKES=json.loads((HERE/'takes.json').read_text())
spec=importlib.util.spec_from_file_location('pilot_speech_helpers',ROOT/'demo/tools/article-animation/speech.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
prior_budget=base.budget
def budget():
 snap=prior_budget();pilot=json.loads((ROOT/'demo/article-animation/speech-requests.json').read_text())
 snap['prior_accounted_usd']+=sum(r.get('settled_usd',r['reserved_usd']) for r in pilot['requests']);return snap
pilot=json.loads((ROOT/'demo/article-animation/speech-requests.json').read_text());pilot_used=sum(r.get('settled_usd',r['reserved_usd']) for r in pilot['requests'])
base.budget=budget;base.MANIFEST=OUT/'speech-requests.json';base.STORY={**STORY,'media_cap_usd':2-pilot_used,'max_http_requests':16-len(pilot['requests'])}
save=base.save;ff=base.ff

def normalize(path):
 with wave.open(str(path)) as w:params=w.getparams();pcm=w.readframes(w.getnframes())
 assert params.nchannels==1 and params.sampwidth==2
 with wave.open(str(path),'wb') as w:w.setparams((1,2,params.framerate,0,'NONE','not compressed'));w.writeframes(pcm)

DIRECTION=("Read the supplied explanation exactly, as the same calm Cedar narrator throughout an illustrated educational series. "
 "The listener found the pilot too fast. Use clearly slower, unhurried US English, near 108 words per minute, consistent volume, "
 "warm understated delivery and natural pauses between sentences. Announce section names clearly. Give the purpose room to land. "
 "Do not whisper or use theatrical announcer energy. Do not omit, summarize, paraphrase or add words. "
 "Pronounce GitHub as Git Hub, README as read me, API as A P I, FastAPI as fast A P I, RAKE as rake, YAKE as yake, "
 "BM25 as B M twenty five, IDF as I D F, Jev as jevv, and Noul as no-ool. "
 "Read the final timing-marker sentence after a short pause; it will be removed locally. Complete every preceding sentence.")

def generate():
 assert json.loads((WORK/'visual-rehearsal.json').read_text())['status']=='PASS'
 frozen=WORK/'frozen-story.json'
 if frozen.exists() and json.loads(frozen.read_text())!=STORY:raise RuntimeError('Frozen public narration changed')
 save(frozen,STORY);save(WORK/'frozen-takes.json',TAKES)
 for take in TAKES:
  text=take['text']+'\n\n'+take['marker'];assert len(text)<=4096
  r=base.request('tts-'+take['id'],'audio/speech',STORY['model'],.15,body={'model':STORY['model'],'voice':'cedar','input':text,'instructions':DIRECTION,'response_format':'wav','speed':STORY['speed']})
  path=WORK/(take['id']+'.wav')
  if r is not None:(WORK/(take['id']+'-provider.wav')).write_bytes(r.content);path.write_bytes(r.content);normalize(path)
  if not path.exists():raise RuntimeError('Successful speech response missing its local audio; no silent repeat')
  with wave.open(str(path)) as w:duration=w.getnframes()/w.getframerate()
  print(take['id'],round(duration,2),'seconds',round(len(take['text'].split())/duration*60,1),'words/min',flush=True)

def align_calls():
 for index,group in enumerate([TAKES[:4],TAKES[4:]],1):
  tracks=[];offsets=[];clock=0;rate=None
  for take in group:
   with wave.open(str(WORK/(take['id']+'.wav'))) as w:
    rate=w.getframerate();data=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16)
   offsets.append({'take':take['id'],'start':clock,'end':clock+len(data)/rate});tracks.extend([data,np.zeros(rate*2,dtype=np.int16)]);clock+=len(data)/rate+2
  path=WORK/f'align-{index}.wav'
  with wave.open(str(path),'wb') as w:w.setparams((1,2,rate,0,'NONE','not compressed'));w.writeframes(np.concatenate(tracks).tobytes())
  mp3=path.with_suffix('.mp3');ff(['-loglevel','error','-y','-i',path,'-ar','16000','-b:a','64k',mp3]);assert mp3.stat().st_size<25_000_000
  r=base.request(f'align-{index}','audio/transcriptions','whisper-1',.18,audio=mp3)
  if r is not None:save(WORK/f'align-{index}.json',r.json())
  save(WORK/f'align-{index}-offsets.json',offsets)
  print('Aligned batch',index,'minutes',round(clock/60,2),flush=True)

SMALL=['zero','one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen']
TENS=['','','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety']
def number(n):
 if n<20:return [SMALL[n]]
 if n<100:return [TENS[n//10]]+([] if n%10==0 else number(n%10))
 if n<1000:return number(n//100)+['hundred']+([] if n%100==0 else number(n%100))
 if n<1000000:return number(n//1000)+['thousand']+([] if n%1000==0 else number(n%1000))
 return [str(n)]
def expand(word):
 raw=word.lower().replace('’',"'").replace(',','');parts=re.findall(r"\d+(?:\.\d+)?|[a-z]+(?:'[a-z]+)?|%",raw);out=[]
 mapping={'github':['git','hub'],'readme':['read','me'],'api':['a','p','i'],'apis':['a','p','i'],'ai':['a','i'],'idf':['i','d','f'],'tf':['t','f'],'tfidf':['t','f','i','d','f'],'fastapi':['fast','a','p','i'],'nextjs':['next','js'],'sqlite':['s','q','l','lite'],'f1':['f','one'],'jeff':['jev'],'soul':['sol'],'yak':['yake'],'null':['noul'],'newell':['noul'],"doesn't":['does','not'],"don't":['do','not'],"isn't":['is','not'],"can't":['can','not'],'%':['percent']}
 for p in parts:
  if p.replace('.','',1).isdigit():
   a,*b=p.split('.');out+=number(int(a))
   if b:out+=['point']+[SMALL[int(d)] for d in b[0]]
  else:out+=mapping.get(p,[p.replace("'",'')])
 return out

def match_words(script_words,observed):
 expected=[];owners=[];obs=[];observed_owners=[]
 for i,word in enumerate(script_words):
  for t in expand(word):expected.append(t);owners.append(i)
 for i,word in enumerate(observed):
  for t in expand(word['word']):obs.append(t);observed_owners.append(i)
 sm=SequenceMatcher(None,expected,obs,autojunk=False)
 matched={a+i:observed_owners[b+i] for a,b,n in sm.get_matching_blocks() for i in range(n)}
 positions={}
 for i,o in enumerate(owners):
  if i in matched:positions.setdefault(o,[]).append(observed[matched[i]])
 rows=[]
 for i,word in enumerate(script_words):
  hits=positions.get(i)
  if hits:rows.append({'word':word,'start':min(x['start'] for x in hits),'end':max(x['end'] for x in hits),'timing':'ASR_MATCHED'})
  else:
   prev=max((j for j in positions if j<i),default=None);nxt=min((j for j in positions if j>i),default=None)
   a=max(x['end'] for x in positions[prev]) if prev is not None else 0;b=min(x['start'] for x in positions[nxt]) if nxt is not None else a+.2
   rows.append({'word':word,'start':a,'end':max(a+.03,b),'timing':'NEIGHBOR_ENVELOPE'})
 mismatches=[{'tag':tag,'expected':expected[a:b],'observed':obs[c:d]} for tag,a,b,c,d in sm.get_opcodes() if tag!='equal']
 return rows,len(matched)/max(1,len(expected)),mismatches

def repair():
 review=json.loads((WORK/'alignment-review.json').read_text());ids={r['beat'] for r in review['bad_beats']}
 beats=[b for c in STORY['chapters'] for b in c['beats'] if b['id'] in ids];text='\n\n'.join(b['text'] for b in beats)+'\n\nThat completes this part of the explanation.'
 assert len(text)<4096
 r=base.request('tts-targeted-repair','audio/speech',STORY['model'],.12,body={'model':STORY['model'],'voice':'cedar','input':text,'instructions':DIRECTION,'response_format':'wav','speed':STORY['speed']})
 path=WORK/'targeted-repair.wav'
 if r is not None:(WORK/'targeted-repair-provider.wav').write_bytes(r.content);path.write_bytes(r.content);normalize(path)
 mp3=path.with_suffix('.mp3');ff(['-loglevel','error','-y','-i',path,'-ar','16000','-b:a','64k',mp3])
 r=base.request('align-targeted-repair','audio/transcriptions','whisper-1',.15,audio=mp3)
 if r is not None:save(WORK/'targeted-repair-asr.json',r.json())
 observed=json.loads((WORK/'targeted-repair-asr.json').read_text())['words'];meta=[{'word':w,'beat':b['id']} for b in beats for w in b['text'].split()]
 words,ratio,errors=match_words([m['word'] for m in meta],observed);overrides={}
 for b in beats:
  rows=[{**w,'beat':m['beat']} for m,w in zip(meta,words) if m['beat']==b['id']]
  assert sum(w['timing']=='ASR_MATCHED' for w in rows)/len(rows)>=.95,(b['id'],rows)
  assert rows[-1]['timing']=='ASR_MATCHED',(b['id'],'missing ending')
  overrides[b['id']]={'file':str(path),'words':rows}
 save(WORK/'repaired-beats.json',{'agreement':ratio,'mismatches':errors,'overrides':overrides,'reason':'Restore omitted context passage and augmentation section; one combined targeted take, original audio retained'})
 print('Repaired',len(beats),'passages; agreement',round(ratio,4),flush=True)

def sentence_pauses(clip,words,rate):
 """Add silence at existing sentence boundaries; preserve every voiced sample."""
 duration=len(clip)/rate;desired=len(words)/110*60;extra=max(0,desired-duration)
 candidates=[]
 for i,w in enumerate(words[:-1]):
  if re.search(r'[.!?]$',w['word']):
   lo=max(0,int(w['end']*rate));hi=min(len(clip),int(words[i+1]['start']*rate))
   midpoint=(lo+hi)//2
   if hi-lo>rate*.025:
    window=max(1,int(rate*.012));steps=range(lo,max(lo+1,hi-window),max(1,window//2))
    midpoint=min(steps,key=lambda x:float(np.mean(clip[x:x+window].astype(np.float64)**2)))+window//2
   candidates.append(max(0,min(len(clip),midpoint)))
 if not candidates or extra<=.02:return clip,words,0
 pause=min(.85,extra/len(candidates));added=round(pause*rate);pieces=[];cursor=0
 for point in candidates:pieces.extend([clip[cursor:point],np.zeros(added,dtype=np.int16)]);cursor=point
 pieces.append(clip[cursor:]);changed=[]
 for w in words:
  changed.append({**w,'start':w['start']+sum(p<=round(w['start']*rate) for p in candidates)*added/rate,'end':w['end']+sum(p<round(w['end']*rate) for p in candidates)*added/rate})
 return np.concatenate(pieces),changed,len(candidates)*added/rate

def timing():
 observed_by_take={}
 for batch in [1,2]:
  words=json.loads((WORK/f'align-{batch}.json').read_text())['words'];offsets=json.loads((WORK/f'align-{batch}-offsets.json').read_text())
  for row in offsets:observed_by_take[row['take']]=[{**w,'start':max(0,w['start']-row['start']),'end':w['end']-row['start']} for w in words if row['start']-.2 <= (w['start']+w['end'])/2 < row['end']]
 source_pcm=[];source_words=[];clock=0;reviews=[];rate=24000
 for take in TAKES:
  meta=[]
  for part in take['parts']:meta.extend({'word':w,'beat':part['beat']} for w in part['text'].split())
  matched,ratio,errors=match_words([m['word'] for m in meta],observed_by_take[take['id']]);reviews.append({'take':take['id'],'agreement':ratio,'mismatches':errors})
  first=next((r for r in matched if r['timing']=='ASR_MATCHED'),None);last=next((r for r in reversed(matched) if r['timing']=='ASR_MATCHED'),None);assert first and last
  a=max(0,first['start']-.16);z=last['end']+.2
  with wave.open(str(WORK/(take['id']+'.wav'))) as w:rate=w.getframerate();data=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16)
  clip=data[round(a*rate):round(z*rate)];source_pcm.extend([clip,np.zeros(round(rate*.35),dtype=np.int16)])
  source_words.extend([{**r,'beat':m['beat'],'start':clock+r['start']-a,'end':clock+r['end']-a} for m,r in zip(meta,matched)])
  clock+=len(clip)/rate+.35
 all_pcm=np.concatenate(source_pcm);beats=[b for c in STORY['chapters'] for b in c['beats']];lookup={b['id']:b for b in beats}
 overrides=json.loads((WORK/'repaired-beats.json').read_text())['overrides'] if (WORK/'repaired-beats.json').exists() else {}
 groups=[];bad=[]
 for b in beats:
  words=[w for w in source_words if w['beat']==b['id']];matched_count=sum(w['timing']=='ASR_MATCHED' for w in words)
  if b['id'] not in overrides and (matched_count/len(words)<.92 or words[-1]['timing']!='ASR_MATCHED'):bad.append({'beat':b['id'],'agreement':matched_count/len(words),'missing':[w['word'] for w in words if w['timing']!='ASR_MATCHED']})
  groups.append((b,words))
 save(WORK/'alignment-review.json',{'takes':reviews,'bad_beats':bad,'source_words':source_words})
 if bad:raise RuntimeError('Alignment requires review before rendering: '+json.dumps(bad))
 boundaries=[max(0,groups[0][1][0]['start']-.12)]
 for (_,before),(_,after) in zip(groups,groups[1:]):boundaries.append((before[-1]['end']+after[0]['start'])/2)
 boundaries.append(min(len(all_pcm)/rate,groups[-1][1][-1]['end']+.22))
 blocks=[];track_parts=[];timeline_words=[];cursor=0;chapters=[]
 for i,(b,words) in enumerate(groups):
  a,z=boundaries[i:i+2];clip=all_pcm[round(a*rate):round(z*rate)]
  if b['id'] in overrides:
   override=overrides[b['id']];words=override['words'];a=max(0,words[0]['start']-.16);z=words[-1]['end']+.2
   with wave.open(override['file']) as w:assert w.getframerate()==rate;repair_pcm=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16)
   clip=repair_pcm[round(a*rate):round(z*rate)]
  relative=[{**w,'start':max(0,w['start']-a),'end':max(0,w['end']-a)} for w in words]
  clip,relative,pause_added=sentence_pauses(clip,relative,rate)
  lead=1;hold=3.5+(4 if b['layout']=='intro' else 0);frames=math.ceil((lead+len(clip)/rate+hold)*30);span=frames/30
  local=[{**w,'start':cursor+lead+w['start'],'end':cursor+lead+w['end']} for w in relative];c=next(c for c in STORY['chapters'] if any(x['id']==b['id'] for x in c['beats']))
  reveals=[.55,local[min(len(local)-1,round(len(local)*.30))]['start']-cursor,local[min(len(local)-1,round(len(local)*.63))]['start']-cursor]
  record={**b,'chapter_id':c['id'],'chapter_title':c['title'],'purpose':c['purpose'],'figure':c['figure'],'start':cursor,'end':cursor+span,'audio_start':cursor+lead,'audio_end':cursor+lead+len(clip)/rate,'frames':frames,'reveal_times':reveals,'sentence_pause_seconds_added':pause_added,'targeted_repair':b['id'] in overrides}
  blocks.append(record);timeline_words.extend(local)
  pcm=np.zeros(round(span*rate),dtype=np.int16);pcm[round(lead*rate):round(lead*rate)+len(clip)]=clip;track_parts.append(pcm);cursor+=span
 for c in STORY['chapters']:
  rows=[b for b in blocks if b['chapter_id']==c['id']];chapters.append({**c,'start':rows[0]['start'],'end':rows[-1]['end']})
 with wave.open(str(WORK/'aligned.wav'),'wb') as w:w.setparams((1,2,rate,0,'NONE','not compressed'));w.writeframes(np.concatenate(track_parts).tobytes())
 out={'duration':cursor,'voice':'cedar','speed':STORY['speed'],'delivery':'Slower Cedar; explicit section name and purpose','beats':blocks,'chapters':chapters,'words':timeline_words,'speech_time_stretch':False,'minimum_result_hold_seconds':3.5,'introduction_extra_hold_seconds':4,'measured_spoken_wpm':len(source_words)/(sum(b['audio_end']-b['audio_start'] for b in blocks)/60),'neighbor_envelope_words':sum(w['timing']!='ASR_MATCHED' for w in timeline_words),'take_alignment_agreement':[r['agreement'] for r in reviews]}
 save(OUT/'timing.json',out);save(WORK/'timing.json',out)
 print(json.dumps({k:out[k] for k in ['duration','measured_spoken_wpm','neighbor_envelope_words','take_alignment_agreement']},indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['generate','align','timing','repair']);a=p.parse_args()
 {'generate':generate,'align':align_calls,'timing':timing,'repair':repair}[a.mode]()
