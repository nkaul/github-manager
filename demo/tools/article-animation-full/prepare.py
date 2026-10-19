"""Preserve prior work and prepare the authorized full series without provider calls."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
OUT=ROOT/'demo/article-animation-full';WORK=ROOT/'demo/work/article-animation-full';DOC=ROOT/'ai-system-design/animation/full'
for p in (OUT,WORK,DOC):p.mkdir(parents=True,exist_ok=True)
story=json.loads((HERE/'story.json').read_text())
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
baseline=DOC/'preservation-baseline.json'
if not baseline.exists():
 prior=json.loads((ROOT/'ai-system-design/animation/preservation-baseline.json').read_text())['files']
 paths={ROOT/r['file'] for r in prior}
 for folder in ['ai-system-design/animation','demo/article-animation','demo/tools/article-animation']:
  paths.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and DOC not in p.parents and '__pycache__' not in p.parts)
 save(baseline,{'date':'2026-10-15','files':[{'file':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(paths)]})
 print('Protected files:',len(paths))
brief='''# Full animated companion — production brief

Approved October 15, 2026 by the instruction to incorporate slower pacing, announce each section with its introduction and purpose, and generate the remaining videos.

The original pilot remains unchanged. The new series has eighteen standalone chapters, a complete master, a revised introductory overview and eight animated reference summaries linked to the earlier detailed illustrations. Retrieval, augmentation, generation, context engineering, memory, loops, harnesses and evaluation have explicit spoken section introductions.

Pacing target: approximately 105–112 spoken words per minute, with a one-second visual lead and at least 3.5 seconds to inspect each result. Introductions also retain a four-second title/purpose hold. The complete runtime follows actual speech and reading pauses, rather than the previous 25–30-minute estimate. No speech time-stretching is planned.

Keep the hand-drawn paper/ink/marker style. Explain each topic with a purpose, visible input, operation, result, caveat and connection to the next stage. Orion remains the concrete authored synthetic example. Current, historical, compared-offline, external-research and proposed components remain labeled.

Seven coherent speech takes and two word-alignment requests are planned. Up to two targeted repair requests fit the shared sixteen-request animation limit when the pilot's five requests are included. The animation reservation ceiling remains $2 including the pilot's $0.29; the existing $5 cumulative ceiling also remains. No new repository inference, benchmark, cloud operation or publication is authorized by this media task.
'''
(DOC/'production-brief.md').write_text(brief)
transcript=['# GitHub Manager — illustrated AI system design','','AI-generated Cedar narration. Slower delivery and explicit section introductions, incorporating pilot feedback.','']
beats=[];cursor=0
for c in story['chapters']:
 transcript.extend(['## '+c['title'],'','Purpose: '+c['purpose'],''])
 for b in c['beats']:
  transcript.extend(['### '+b['title'],'',b['text'],''])
  length=len(b['text'].split())/108*60
  span=length+story['beat_lead_seconds']+story['beat_hold_seconds']+(story['chapter_title_hold_seconds'] if b['layout']=='intro' else 0)
  beats.append({**b,'chapter_id':c['id'],'chapter_title':c['title'],'purpose':c['purpose'],'figure':c['figure'],'start':cursor,'end':cursor+span,'audio_start':cursor+1,'audio_end':cursor+1+length,'reveal_times':[0,span*.30,span*.60]});cursor+=span
(DOC/'transcript.md').write_text('\n'.join(transcript))
(OUT/'transcript.md').write_text('\n'.join(transcript))
save(WORK/'rehearsal-timing.json',{'duration':cursor,'beats':beats,'chapters':story['chapters'],'words':[],'status':'OFFLINE_REHEARSAL_ONLY'})
academic=(ROOT/'ai-system-design/github-manager-ai-system-design.md').read_text()
rows=[]
for line in academic.split('### 20.2 Algorithm and mechanism inventory')[1].split('### 20.3')[0].splitlines():
 if not line.startswith('|') or '---' in line or 'Algorithm / mechanism' in line:continue
 fields=[v.strip() for v in line.strip('|').split('|')];name=fields[0]
 match=[(r'CommonMark|Regex|SHA',4),(r'RAKE|YAKE|Distinct',5),(r'Binary|BM25|Alias token|Per-kind',7),(r'Owner|Byte-bounded|Unicode',6),(r'New-analysis|Durable|Weighted|Generation/epoch',12),(r'Native',9),(r'Approved|Stored-analysis',11),(r'Integer',13),(r'Micro set',15),(r'Dense|Contextual',16)]
 n=next((i for pattern,i in match if re.search(pattern,name)),None);assert n,(name,'unmapped')
 ch=story['chapters'][n-1];rows.append({'mechanism':name,'role':fields[1],'source_status':fields[2],'chapter':ch['id'],'animated_beats':[b['id'] for b in ch['beats']]})
save(DOC/'coverage.json',{'academic_source':'ai-system-design/github-manager-ai-system-design.md','mechanisms':rows,'source_sections':{str(n):[c['id'] for c in story['chapters'] if n in c['source_sections']] for n in range(1,21)},'chapters':[{k:c[k] for k in ['id','title','purpose','source_sections','figure']} for c in story['chapters']],'limitations':'Exact formulas and large payloads also remain in the linked source articles; narrated and animated mechanisms do not imply new tests.'})
assert all(any(n in c['source_sections'] for c in story['chapters']) for n in range(1,21))
print('Rehearsal runtime minutes:',round(cursor/60,2));print('Mechanisms mapped:',len(rows))
