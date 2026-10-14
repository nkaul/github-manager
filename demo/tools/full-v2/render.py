"""1080p scene edits with measured paragraph speech; actions stay at normal speed."""

import hashlib
import json
import re
import subprocess
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / "demo/work/full-v2"
OUT = ROOT / "demo/full-v2"
FF = ROOT / ".tools/video-python/imageio_ffmpeg/binaries/ffmpeg-macos-x86_64-v7.1"
OUT.mkdir(exist_ok=True)
(WORK / "parts").mkdir(exist_ok=True)


def ff(args):
    r = subprocess.run(
        [str(FF), "-hide_banner", "-nostdin", *map(str, args)],
        capture_output=True,
        check=False,
    )
    if r.returncode:
        raise RuntimeError(r.stderr.decode()[-1600:])
    return r


def stamp(t, comma=False):
    ms = round(t * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02}{',' if comma else '.'}{ms % 1000:03}"


timing = json.loads((WORK / "timeline.json").read_text())
capture = json.loads((WORK / "capture.json").read_text())
assert capture["status"] == "PASS" and len(capture["chapters"]) == 32
capture["chapters"].sort(key=lambda c: c["id"])
positions = {}
files = {c["file"] for c in capture["chapters"]} | {
    b["file"] for c in capture["chapters"] for b in c["beats"] if b.get("file")
}
for source_file in sorted(files):
    raw = ff(
        [
            "-loglevel",
            "error",
            "-i",
            source_file,
            "-an",
            "-vf",
            "crop=4:4:1910:1070,scale=1:1,format=rgb24",
            "-f",
            "rawvideo",
            "pipe:1",
        ]
    ).stdout
    pixels = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
    hits = np.where((pixels[:, 0] > 170) & (pixels[:, 1] < 90) & (pixels[:, 2] > 170))[
        0
    ]
    if not len(hits) and Path(source_file).name == "chapter-23.webm":
        raw = ff(
            [
                "-loglevel",
                "error",
                "-i",
                source_file,
                "-an",
                "-vf",
                "crop=4:4:380:834,scale=1:1,format=rgb24",
                "-f",
                "rawvideo",
                "pipe:1",
            ]
        ).stdout
        pixels = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        hits = np.where(
            (pixels[:, 0] > 170) & (pixels[:, 1] < 90) & (pixels[:, 2] > 170)
        )[0]
    if not len(hits):
        raise RuntimeError("Clock marker missing " + source_file)
    positions[source_file] = int(hits[0]) / 25
print(f"All {len(files)} encoded video clocks located", flush=True)

edits = []


def render(b):
    c = next(c for c in capture["chapters"] if c["id"] == b["chapter"])
    rec = b["capture"]
    source_file = rec.get("file", c["file"])
    offset = positions[source_file] + rec["start"]
    length = rec["end"] - rec["start"]
    target = WORK / "parts" / (b["key"] + ".mp4")
    base = (
        "crop=390:844:0:0,drawbox=x=378:y=832:w=12:h=12:color=0xf7f8fd:t=fill,pad=1920:1080:765:118:color=0xf7f8fd"
        if c.get("mobile")
        else "drawbox=x=1908:y=1068:w=12:h=12:color=0xf7f8fd:t=fill"
    )
    base += ",drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text=AI-generated narration - Cedar:x=1650:y=1050:fontsize=14:fontcolor=0x283593:box=1:boxcolor=white@0.9"
    condensed = length > 15
    if condensed:
        # Discrete cut, never global slowing. Keep the beginning and the visible result.
        graph = f"[0:v]split=2[a][z];[a]trim=start={offset}:duration=3,setpts=PTS-STARTPTS[x];[z]trim=start={offset + length - 5}:duration=5,setpts=PTS-STARTPTS[y];[x][y]concat=n=2:v=1:a=0,{base},drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text=Sequence condensed - actions at normal speed:x=1120:y=1030:fontsize=17:fontcolor=0x283593:box=1:boxcolor=white@0.9,tpad=stop_mode=clone:stop_duration={b['span']}[v]"
        edits.append(
            {
                "beat": b["key"],
                "removed_seconds": round(length - 8, 3),
                "method": "discrete cut; actual actions not accelerated",
            }
        )
    else:
        graph = f"[0:v]trim=start={offset}:duration={length},setpts=PTS-STARTPTS,{base},tpad=stop_mode=clone:stop_duration={b['span']}[v]"
    fingerprint = hashlib.sha256(
        (graph + str(Path(source_file).stat().st_mtime_ns)).encode()
    ).hexdigest()
    signature = target.with_suffix(".sha256")
    if target.exists() and signature.exists() and signature.read_text() == fingerprint:
        return str(target)
    ff(
        [
            "-loglevel",
            "error",
            "-y",
            "-i",
            source_file,
            "-filter_complex",
            graph,
            "-map",
            "[v]",
            "-an",
            "-t",
            b["span"],
            "-r",
            "25",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "22",
            "-pix_fmt",
            "yuv420p",
            "-threads",
            "2",
            target,
        ]
    )
    signature.write_text(fingerprint)
    return str(target)


with ThreadPoolExecutor(max_workers=4) as pool:
    parts = list(pool.map(render, timing["beats"]))
print("128 UI paragraphs rendered", flush=True)
concat = WORK / "parts.txt"
concat.write_text("".join("file '" + p.replace("'", "'\\''") + "'\n" for p in parts))
video = WORK / "picture.mp4"
ff(
    [
        "-loglevel",
        "error",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        concat,
        "-c",
        "copy",
        video,
    ]
)
rate = 24000
track = np.zeros(round(timing["duration"] * rate), dtype=np.int16)
for b in timing["beats"]:
    with wave.open(b["file"]) as w:
        assert w.getframerate() == rate
        clip = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    start = round(b["audio_start"] * rate)
    track[start : start + len(clip)] = clip
aligned = WORK / "aligned.wav"
with wave.open(str(aligned), "wb") as w:
    w.setparams((1, 2, rate, 0, "NONE", "not compressed"))
    w.writeframes(track.tobytes())
analysis = ff(
    [
        "-i",
        aligned,
        "-af",
        "loudnorm=I=-16:TP=-2:LRA=11:print_format=json",
        "-f",
        "null",
        "-",
    ]
).stderr.decode()
m = json.JSONDecoder().raw_decode(analysis[analysis.rfind("{") :])[0]
loud = f"loudnorm=I=-16:TP=-2:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
rows = []
group = []
for word in timing["words"]:
    if group and (
        word["scene"] != group[0]["scene"]
        or word["beat"] != group[0]["beat"]
        or len(" ".join(w["word"] for w in group)) > 55
        or len(group) >= 9
    ):
        rows.append(group)
        group = []
    group.append(word)
    if re.search(r"[.!?]$", word["word"]):
        rows.append(group)
        group = []
if group:
    rows.append(group)
vtt = OUT / "full-demo.vtt"
srt = OUT / "full-demo.srt"
vtt.write_text(
    "WEBVTT\n\n"
    + "\n\n".join(
        f"{stamp(g[0]['start'])} --> {stamp(max(g[-1]['end'], g[0]['start'] + 0.12))}\n"
        + " ".join(w["word"] for w in g)
        for g in rows
    )
    + "\n"
)
srt.write_text(
    "\n\n".join(
        f"{i}\n{stamp(g[0]['start'], True)} --> {stamp(max(g[-1]['end'], g[0]['start'] + 0.12), True)}\n"
        + " ".join(w["word"] for w in g)
        for i, g in enumerate(rows, 1)
    )
    + "\n"
)
chapters = []
for c in capture["chapters"]:
    beats = [b for b in timing["beats"] if b["chapter"] == c["id"]]
    chapters.append(
        {
            "id": c["id"],
            "title": c["title"],
            "start": beats[0]["start"],
            "end": beats[-1]["end"],
            "source": c["source"],
            "checks": [x for x in capture["checks"] if x["chapter"] == c["id"]],
        }
    )
metadata = WORK / "chapters.ffmeta"
metadata.write_text(
    ";FFMETADATA1\ntitle=GitHub Manager — complete real-account demo · Cedar calm\ncomment=AI-generated Cedar narration. Real GitHub account, explicitly labeled workspace copy for edits and resets.\n"
    + "".join(
        f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(c['start'] * 1000)}\nEND={round(c['end'] * 1000)}\ntitle={c['id']} {c['title']}\n"
        for c in chapters
    )
)
target = OUT / "github-manager-full-cedar-calm-1080p.mp4"
ff(
    [
        "-loglevel",
        "error",
        "-y",
        "-i",
        video,
        "-i",
        aligned,
        "-i",
        srt,
        "-i",
        metadata,
        "-map",
        "0:v",
        "-map",
        "1:a",
        "-map",
        "2:0",
        "-map_metadata",
        "3",
        "-map_chapters",
        "3",
        "-c:v",
        "copy",
        "-af",
        loud,
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-ar",
        "48000",
        "-ac",
        "1",
        "-c:s",
        "mov_text",
        "-metadata:s:s:0",
        "language=eng",
        "-t",
        timing["duration"],
        "-movflags",
        "+faststart",
        target,
    ]
)
ff(
    [
        "-loglevel",
        "error",
        "-y",
        "-i",
        target,
        "-vn",
        "-c:a",
        "copy",
        OUT / "github-manager-full-cedar-calm.m4a",
    ]
)
ff(
    [
        "-loglevel",
        "error",
        "-y",
        "-ss",
        "2",
        "-i",
        target,
        "-frames:v",
        "1",
        OUT / "poster.jpg",
    ]
)
final = ff(
    [
        "-i",
        target,
        "-af",
        "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
        "-f",
        "null",
        "-",
    ]
).stderr.decode()
measure = json.JSONDecoder().raw_decode(final[final.rfind("{") :])[0]
ff(["-loglevel", "error", "-i", target, "-f", "null", "-"])
qa = {
    "status": "PASS",
    "width": 1920,
    "height": 1080,
    "fps": 25,
    "duration_seconds": timing["duration"],
    "chapters": len(chapters),
    "paragraphs": len(timing["beats"]),
    "caption_cues": len(rows),
    "voice": "cedar",
    "delivery": "Option D · calmer delivery",
    "measured_spoken_wpm": timing["measured_wpm"],
    "audio_lufs": float(measure["input_i"]),
    "audio_true_peak_dbtp": float(measure["input_tp"]),
    "decode": "PASS",
    "normal_speed_actions": True,
    "speech_time_stretch": False,
    "edited_sequences": edits,
    "clock_offsets": {Path(p).name: t for p, t in positions.items()},
    "source": "Real account, no masking, no fixture AI",
    "checks": len(capture["checks"]),
    "page_errors": capture["errors"],
    "sync_method": "Each verified narration paragraph is placed at the corresponding UI action scene; captions use actual word timestamps. Result holds and discrete cuts are explicit.",
}
assert abs(qa["audio_lufs"] + 16) < 1 and qa["audio_true_peak_dbtp"] <= -1.5
for name, value in [
    ("chapters.json", chapters),
    ("media-qa.json", qa),
    ("timing.json", timing),
    ("feature-checks.json", capture["checks"]),
]:
    (OUT / name).write_text(json.dumps(value, indent=2) + "\n")
transcript = "# GitHub Manager · complete real-account demo\n\nAI-generated Cedar narration · Option D, calmer delivery.\n\n"
for c in chapters:
    transcript += (
        f"## {c['id']} · {c['title']} ({stamp(c['start'])[:8]})\n\n"
        + "\n\n".join(b["text"] for b in timing["beats"] if b["chapter"] == c["id"])
        + "\n\n"
    )
(OUT / "transcript.md").write_text(transcript)
print(json.dumps(qa, indent=2), flush=True)
