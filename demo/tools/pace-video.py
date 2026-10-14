"""Spread visible UI actions across narration; retain original chapter times/audio."""

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEMO, WORK = ROOT / "demo", ROOT / "demo/work"
FF = ROOT / ".tools/video-python/imageio_ffmpeg/binaries/ffmpeg-macos-x86_64-v7.1"
chapters = json.loads((DEMO / "chapters.json").read_text())
paced = WORK / "paced"
paced.mkdir(exist_ok=True)
observations = []
for c in chapters:
    source = WORK / "segments" / (c["id"] + ".mp4")
    # These editor scenes have minor recurring updates after the dialog closes.
    # Use layout changes to identify their action span, rather than extending it
    # through the trailing idle interval. Keep status/scheduler scenes sensitive.
    threshold = 0.01 if c["id"] in {"09", "10", "12", "13", "14", "15", "16", "17"} else 0.002
    scan = subprocess.run([str(FF), "-hide_banner", "-i", str(source), "-an", "-vf", f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-"], capture_output=True, text=True)
    assert scan.returncode == 0, scan.stderr[-1000:]
    changes = [float(t) for t in re.findall(r"pts_time:([0-9.]+)", scan.stderr)]
    action_end = min(c["duration"], max(changes, default=0) + 1.2)
    stretch = c["duration"] - 2.5
    adjust = c["id"] not in {"01", "26"} and 1.5 < action_end < stretch * 0.85
    video_filter = f"trim=duration={action_end:.3f},setpts={(stretch/action_end):.6f}*(PTS-STARTPTS),fps=25,tpad=stop_mode=clone:stop_duration=4,format=yuv420p" if adjust else "fps=25,format=yuv420p"
    output = paced / source.name
    result = subprocess.run([str(FF), "-hide_banner", "-loglevel", "error", "-y", "-i", str(source), "-vf", video_filter,
                             "-t", str(c["duration"]), "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-threads", "2", "-pix_fmt", "yuv420p", "-r", "25",
                             "-c:a", "copy", "-video_track_timescale", "12800", str(output)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr[-1000:]
    observations.append({"chapter": c["id"], "action_end_seconds": round(action_end, 2), "paced": adjust, "speed_factor": round(action_end/stretch, 3) if adjust else 1})
    print(f"Paced chapter {c['id']}: active UI {action_end:.2f}s, adjusted={adjust}", flush=True)
listing = paced / "concat.txt"
listing.write_text("".join(f"file '{(paced / (c['id']+'.mp4')).as_posix()}'\n" for c in chapters))
output = WORK / "walkthrough-paced.mp4"
result = subprocess.run([str(FF), "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
                         "-i", str(WORK / "walkthrough.srt"), "-i", str(WORK / "chapters.ffmeta"),
                         "-map", "0:v:0", "-map", "0:a:0", "-map", "1:0", "-map_metadata", "2", "-map_chapters", "2",
                         "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text", "-metadata:s:s:0", "language=eng", "-disposition:s:0", "default", "-movflags", "+faststart", str(output)], capture_output=True, text=True)
assert result.returncode == 0, result.stderr[-1000:]
output.replace(DEMO / "github-manager-walkthrough-1080p.mp4")
qa = json.loads((DEMO / "media-qa.json").read_text())
for key in ("browser_playback_pass", "chapter_seek_checks", "caption_cues", "audio_duration_seconds", "decode_pass", "visual_inspection_pass"):
    qa.pop(key, None)
qa.update(pacing="Visible UI actions slowed to fit narration; long scheduler wait removed. Test execution used normal scheduler intervals.", size_bytes=(DEMO / "github-manager-walkthrough-1080p.mp4").stat().st_size)
(DEMO / "media-qa.json").write_text(json.dumps(qa, indent=2)+"\n")
(WORK / "pacing.json").write_text(json.dumps(observations, indent=2)+"\n")
