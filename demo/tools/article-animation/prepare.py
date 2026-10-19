"""Freeze prior artifacts and prepare the approved two-minute pilot, offline."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "demo/article-animation"
WORK = ROOT / "demo/work/article-animation"
DOC = ROOT / "ai-system-design/animation"

def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n")

for d in (OUT, WORK, DOC):
    d.mkdir(parents=True, exist_ok=True)

baseline = DOC / "preservation-baseline.json"
if not baseline.exists():
    files = set()
    files.update(p for p in (ROOT / "ai-system-design").rglob("*") if p.is_file() and DOC not in p.parents and "__pycache__" not in p.parts)
    files.update(p for p in (ROOT / "docs/validation").rglob("*") if p.suffix in {".md", ".json"} and p.is_file())
    for folder in ["docs/diagrams", "docs/assets/images", "demo/full-v2", "demo/voice-preview-v2"]:
        files.update(p for p in (ROOT / folder).rglob("*") if p.is_file())
    for f in ["docs/validation/private/ai-pretest/runs.sqlite3", "docs/validation/private/demo/full-v2/ai/runs.sqlite3"]:
        p = ROOT / f
        if p.exists(): files.add(p)
    rows = []
    for p in sorted(files):
        h = hashlib.sha256()
        with p.open("rb") as f:
            for block in iter(lambda: f.read(4 * 1024 * 1024), b""): h.update(block)
        rows.append({"file": str(p.relative_to(ROOT)), "bytes": p.stat().st_size, "sha256": h.hexdigest()})
    save(baseline, {"date": "2026-10-15", "files": rows})
    print("Protected prior files:", len(rows))

story = json.loads(Path(__file__).with_name("story.json").read_text())
text = "\n\n".join(s["text"] for s in story["segments"])
assert len(text) < 4096
print("Narration:", len(text.split()), "words;", len(text), "characters")
timeline = []
cursor = 0
for s in story["segments"]:
    span = 120 * len(s["text"].split()) / len(text.split())
    timeline.append({**s, "start": cursor, "end": cursor + span, "audio_start": cursor + .3,
                     "cues": {c: cursor + span * (i + 1) / (len(s["cues"]) + 1) for i, c in enumerate(s["cues"])}})
    cursor += span
save(WORK / "rehearsal-timing.json", {"duration": 120, "segments": timeline, "words": [], "status": "OFFLINE_REHEARSAL_ONLY"})
save(DOC / "pilot-approval.json", {"date": "2026-10-15", "user_instruction": "Lets create the 2 min version first to see if we need to align and adjust", "authorized_scope": "Two-minute pilot only", "long_form": "Awaiting user feedback", "voice": "Cedar, calmer delivery", "max_http_requests": story["max_http_requests"], "media_reservation_cap_usd": .4, "cumulative_ceiling_usd": 5, "new_repository_inference": False, "publication": False})
save(DOC / "coverage-pilot.json", {"scope": "Overview, not all long-form concepts", "scenes": story["segments"], "deferred_to_full_companion": ["RAKE/YAKE/BM25 algorithm details", "Evaluation and statistical qualifications", "Full failure/concurrency paths", "Contextual retrieval, dense/hybrid retrieval and reranking", "Jev future research", "Detailed tokenomics and source contracts"]})
transcript = "# GitHub Manager — two-minute animated overview\n\nAI-generated Cedar narration; calmer delivery. This is an illustrated explanation, not a new application test.\n\n" + "\n\n".join("## " + s["heading"] + "\n\n" + s["text"] for s in story["segments"]) + "\n"
(DOC / "transcript.md").write_text(transcript)
(OUT / "transcript.md").write_text(transcript)
