"""Render chapter-aligned H.264/AAC video, captions, chapter markers and audio-only copy."""

import json
import hashlib
import math
import re
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "demo"
WORK = DEMO / "work"
FFMPEG = ROOT / ".tools/video-python/imageio_ffmpeg/binaries/ffmpeg-macos-x86_64-v7.1"
partial = "--partial" in sys.argv
override = next((arg.split("=", 1)[1] for arg in sys.argv if arg.startswith("--capture=")), None)
capture = Path(override) if override else (sorted((DEMO / "raw").glob("*/capture.json"))[-1].parent if partial else Path((WORK / "latest-capture.txt").read_text().strip()))
record = json.loads((capture / "capture.json").read_text())
assert not record["dry"] and (partial or record["status"] == "PASS")
segments = WORK / "segments"
segments.mkdir(exist_ok=True)


def command(args):
    result = subprocess.run([str(FFMPEG), "-hide_banner", "-loglevel", "error", "-y", *args], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-4000:])


def timestamp(seconds, comma=False):
    millis = round(seconds * 1000)
    return f"{millis // 3600000:02}:{millis // 60000 % 60:02}:{millis // 1000 % 60:02}{',' if comma else '.'}{millis % 1000:03}"


chapters = []
subtitles = []
offset = 0.0
for chapter in record["chapters"]:
    if "file" not in chapter or "end" not in chapter:
        continue
    start, end = chapter["start"], chapter["end"]
    boundaries = [start]
    for a, b in chapter["cuts"]:
        boundaries.extend([a, b])
    boundaries.append(end)
    pieces = list(zip(boundaries[::2], boundaries[1::2]))
    kept = sum(b - a for a, b in pieces)
    duration = math.ceil(max(kept, chapter["audio_seconds"] + 2) * 25) / 25
    filters = []
    if len(pieces) == 1:
        filters.append(f"[0:v]setpts=PTS-STARTPTS,fps=25,tpad=stop_mode=clone:stop_duration={duration:.3f},format=yuv420p[v]")
    else:
        filters.append("[0:v]split=" + str(len(pieces)) + "".join(f"[s{i}]" for i in range(len(pieces))))
        for i, (a, b) in enumerate(pieces):
            filters.append(f"[s{i}]trim=start={a-start:.3f}:end={b-start:.3f},setpts=PTS-STARTPTS[p{i}]")
        filters.append("".join(f"[p{i}]" for i in range(len(pieces))) + f"concat=n={len(pieces)}:v=1:a=0,fps=25,tpad=stop_mode=clone:stop_duration={duration:.3f},format=yuv420p[v]")
    output = segments / (chapter["id"] + ".mp4")
    signature = hashlib.sha256(json.dumps(chapter, sort_keys=True).encode()).hexdigest()
    signature_file = output.with_suffix(".signature")
    if not output.exists() or not signature_file.exists() or signature_file.read_text() != signature:
      command(["-ss", f"{start:.3f}", "-t", f"{end-start:.3f}", "-i", chapter["file"], "-i", str(WORK / (chapter["id"] + ".wav")),
             "-filter_complex", ";".join(filters), "-map", "[v]", "-map", "1:a:0",
             "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,adelay=1000:all=1,apad",
             "-t", f"{duration:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-threads", "2", "-r", "25", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "1", "-video_track_timescale", "12800", str(output)])
      signature_file.write_text(signature)
    public = {key: chapter[key] for key in ["id", "title", "source", "narration"]}
    public.update(start=round(offset, 3), end=round(offset + duration, 3), duration=duration,
                  wait_removed_seconds=round((end-start)-kept, 3))
    chapters.append(public)
    sentences = re.split(r"(?<=[.!?])\s+", chapter["narration"])
    weight = sum(len(s.split()) for s in sentences)
    cursor = offset + 1
    for sentence in sentences:
        length = chapter["audio_seconds"] * len(sentence.split()) / weight
        subtitles.append((cursor, cursor + length, "\n".join(textwrap.wrap(sentence, 84))))
        cursor += length
    offset += duration
    print(f"Rendered {chapter['id']}: {chapter['title']} ({duration:.2f}s)", flush=True)

if partial:
    print("Completed available chapters; final packaging waits for capture PASS.", flush=True)
    raise SystemExit(0)

srt = WORK / "walkthrough.srt"
srt.write_text("\n\n".join(f"{i}\n{timestamp(a, True)} --> {timestamp(b, True)}\n{text}" for i, (a, b, text) in enumerate(subtitles, 1)) + "\n")
(DEMO / "github-manager-walkthrough.vtt").write_text("WEBVTT\n\n" + "\n\n".join(f"{timestamp(a)} --> {timestamp(b)}\n{text}" for a, b, text in subtitles) + "\n")
(DEMO / "chapters.json").write_text(json.dumps(chapters, indent=2) + "\n")
metadata = WORK / "chapters.ffmeta"
metadata.write_text(";FFMETADATA1\ntitle=GitHub Manager — complete local walkthrough\ncomment=Actual 1920x1080 browser capture; native synthetic narration; provider provenance identified per chapter.\n" + "".join(
    f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(c['start']*1000)}\nEND={round(c['end']*1000)}\ntitle={c['id']} {c['title']}\n" for c in chapters))
concat = WORK / "concat.txt"
concat.write_text("".join("file '" + str(segments / (c['id'] + '.mp4')).replace("'", "'\\''") + "'\n" for c in chapters))
video = DEMO / "github-manager-walkthrough-1080p.mp4"
command(["-f", "concat", "-safe", "0", "-i", str(concat), "-i", str(srt), "-i", str(metadata),
         "-map", "0:v:0", "-map", "0:a:0", "-map", "1:0", "-map_metadata", "2", "-map_chapters", "2",
         "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text", "-metadata:s:s:0", "language=eng", "-disposition:s:0", "default",
         "-movflags", "+faststart", str(video)])
command(["-i", str(video), "-map", "0:a:0", "-c:a", "copy", "-map_chapters", "0", str(DEMO / "github-manager-narration.m4a")])
command(["-ss", "4", "-i", str(video), "-frames:v", "1", str(DEMO / "poster.png")])
public_checks = {"date": record["date"], "status": record["status"], "viewport": record["viewport"],
                 "checks": record["checks"], "notes": record["notes"], "budget": record["budget"],
                 "live_github": {"repositories": record["liveGithub"]["repositories"],
                                  "expected_name_matches": record["liveGithub"]["expected_name_matches"],
                                  "expected_name_matches_scope": record["liveGithub"].get("expected_name_matches_scope", "First 100 inventory rows only"),
                                  "named_fixture_verification": record["liveGithub"].get("named_fixture_verification", {}),
                                  "private_count_on_first_100": record["liveGithub"]["private_count_on_first_100"],
                                  "source_statuses": [{"source": s["source"], "status": s["status"]} for s in record["liveGithub"]["source_coverage"]],
                                  "activity_statuses": [{"source": s["source"], "status": s["status"]} for s in record["liveGithub"]["activity_coverage"]]}}
(DEMO / "validation.json").write_text(json.dumps(public_checks, indent=2) + "\n")
info = subprocess.run([str(FFMPEG), "-hide_banner", "-i", str(video)], capture_output=True, text=True).stderr
assert "1920x1080" in info and "25 fps" in info and "Audio: aac" in info and "Subtitle: mov_text" in info
assert len(chapters) == 26
qa = {"resolution": "1920x1080", "fps": 25, "video_codec": "H.264", "audio_codec": "AAC", "caption_track": "English mov_text + WebVTT", "chapters": len(chapters), "duration_seconds": round(offset, 2), "size_bytes": video.stat().st_size}
(DEMO / "media-qa.json").write_text(json.dumps(qa, indent=2) + "\n")
print(json.dumps(qa), flush=True)
