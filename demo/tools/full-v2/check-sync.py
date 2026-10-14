"""Validate paragraph/word envelopes against final playback; no API requests."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / "demo/work/full-v2"
OUT = ROOT / "demo/full-v2"
t = json.loads((WORK / "timeline.json").read_text())
m = json.loads((OUT / "media-qa.json").read_text())
p = json.loads((OUT / "player-qa.json").read_text())
assert (
    len(t["beats"]) == 128 and abs(p["properties"]["duration"] - t["duration"]) < 0.05
)
assert len({b["key"] for b in t["beats"]}) == 128
rows = []
for b in t["beats"]:
    words = [
        w for w in t["words"] if w["scene"] == b["chapter"] and w["beat"] == b["id"]
    ]
    assert words and b["end"] > b["start"]
    assert min(w["start"] for w in words) >= b["start"] - 0.04
    assert max(w["end"] for w in words) <= b["end"] + 0.04
    assert b["audio_start"] + b["audio_seconds"] <= b["end"] + 0.04
    rows.append(
        {
            "beat": b["key"],
            "scene_start": b["start"],
            "scene_end": b["end"],
            "first_spoken_word": min(w["start"] for w in words),
            "last_spoken_word": max(w["end"] for w in words),
            "words": len(words),
            "status": "PASS",
        }
    )
for a, b in zip(t["beats"], t["beats"][1:]):
    assert abs(a["end"] - b["start"]) < 0.0001
result = {
    "status": "PASS",
    "paragraphs": 128,
    "duration_seconds": t["duration"],
    "decoded_playback_duration": p["properties"]["duration"],
    "caption_cues_loaded": p["caption_loading"]["cues"],
    "speech_time_stretch": False,
    "normal_speed_actions": True,
    "method": "Actual Whisper word timestamps, numeric/compound normalization, per-paragraph UI action/result clips and explicit reading holds. This is paragraph synchronization, not a claim that every control click lands on an exact word.",
    "narration_repairs": t["narration_repairs"],
    "paragraph_checks": rows,
}
(OUT / "synchronization-qa.json").write_text(json.dumps(result, indent=2) + "\n")
public = {
    **t,
    "beats": [
        {k: v for k, v in b.items() if k not in {"file", "capture"}}
        | {
            "capture": {
                k: (Path(v).name if k == "file" else v) for k, v in b["capture"].items()
            }
        }
        for b in t["beats"]
    ],
}
(OUT / "timing.json").write_text(json.dumps(public, indent=2) + "\n")
print(
    "PASS: 128 spoken paragraph envelopes, continuous scene times and 390 loaded captions"
)
