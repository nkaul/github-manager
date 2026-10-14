"""Package current-UI recordings with timestamp-aligned, unstretched speech."""

import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / "demo/work/voice-preview-v2"
OUT = ROOT / "demo/voice-preview-v2"
FF = ROOT / ".tools/video-python/imageio_ffmpeg/binaries/ffmpeg-macos-x86_64-v7.1"


def run(args):
    result = subprocess.run(
        [str(FF), "-hide_banner", "-nostdin", *args], capture_output=True, check=False
    )
    if result.returncode:
        raise RuntimeError(result.stderr.decode()[-1800:])
    return result


def timestamp(seconds, comma=False):
    t = round(seconds * 1000)
    return f"{t // 3600000:02}:{t // 60000 % 60:02}:{t // 1000 % 60:02}{',' if comma else '.'}{t % 1000:03}"


def captions(timing, target):
    groups, group = [], []
    for w in timing["words"]:
        if group and (
            group[0]["scene"] != w["scene"]
            or len(" ".join(x["word"] for x in group)) > 53
            or len(group) >= 9
        ):
            groups.append(group)
            group = []
        group.append(w)
        if re.search(r"[.!?]$", w["word"]):
            groups.append(group)
            group = []
    if group:
        groups.append(group)
    rows = [
        (
            g[0]["start"],
            max(g[-1]["end"], g[0]["start"] + 0.12),
            " ".join(w["word"] for w in g),
        )
        for g in groups
    ]
    target.with_suffix(".vtt").write_text(
        "WEBVTT\n\n"
        + "\n\n".join(
            f"{timestamp(a)} --> {timestamp(b)}\n{text}" for a, b, text in rows
        )
        + "\n"
    )
    target.with_suffix(".srt").write_text(
        "\n\n".join(
            f"{i}\n{timestamp(a, True)} --> {timestamp(b, True)}\n{text}"
            for i, (a, b, text) in enumerate(rows, 1)
        )
        + "\n"
    )
    return len(rows)


results = []
for ident in ["A", "B", "C", "D"]:
    timing = json.loads((WORK / f"{ident}-timeline.json").read_text())
    capture = json.loads((WORK / f"{ident}-capture.json").read_text())
    assert capture["status"] == "PASS"
    source = Path(capture["raw"])
    # Detect the first magenta clock marker in the actual encoded video. This
    # removes setup footage at a frame boundary rather than guessing from clocks.
    marker = run(
        [
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-an",
            "-vf",
            "crop=4:4:1910:1070,scale=1:1,format=rgb24",
            "-f",
            "rawvideo",
            "pipe:1",
        ]
    ).stdout
    pixels = np.frombuffer(marker, dtype=np.uint8).reshape(-1, 3)
    hits = np.where((pixels[:, 0] > 170) & (pixels[:, 1] < 90) & (pixels[:, 2] > 170))[
        0
    ]
    if not len(hits):
        raise RuntimeError("Recording clock marker missing")
    offset = int(hits[0]) / 25
    count = captions(timing, OUT / ident)
    metadata = WORK / f"{ident}-chapters.ffmeta"
    metadata.write_text(
        ";FFMETADATA1\ntitle=GitHub Manager — "
        + ident
        + " "
        + timing["voice"].title()
        + " "
        + timing["pace"]
        + "\ncomment=Actual current UI, isolated public/synthetic fixture, AI-generated narration.\n"
        + "".join(
            f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(s['start'] * 1000)}\nEND={round(s['end'] * 1000)}\ntitle={s['id'].title()}\n"
            for s in timing["segments"]
        )
    )
    # Measure then apply one consistent loudness correction across the full track.
    audio = WORK / f"{ident}-aligned.wav"
    analysis = run(
        [
            "-i",
            str(audio),
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
            "-f",
            "null",
            "-",
        ]
    ).stderr.decode()
    measure = json.JSONDecoder().raw_decode(analysis[analysis.rfind("{") :])[0]
    # AAC can overshoot the pre-encode true peak slightly; leave 0.5dB headroom.
    loud = f"loudnorm=I=-16:TP=-2:LRA=11:measured_I={measure['input_i']}:measured_TP={measure['input_tp']}:measured_LRA={measure['input_lra']}:measured_thresh={measure['input_thresh']}:offset={measure['target_offset']}:linear=true"
    target = OUT / f"{ident}-{timing['voice']}-{timing['pace']}-1080p.mp4"
    copy_video = "--audio-only" in sys.argv
    encoding_target = target.with_suffix(".encoding.mp4")
    run(
        [
            "-loglevel",
            "error",
            "-y",
            "-ss",
            str(0 if copy_video else offset),
            "-i",
            str(target if copy_video else source),
            "-i",
            str(audio),
            "-i",
            str(OUT / f"{ident}.srt"),
            "-i",
            str(metadata),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-map",
            "2:0",
            "-map_metadata",
            "3",
            "-map_chapters",
            "3",
            *(
                []
                if copy_video
                else [
                    "-vf",
                    "drawbox=x=1907:y=1067:w=13:h=13:color=0xf5f7fc:t=fill,fps=25,format=yuv420p",
                ]
            ),
            "-af",
            loud + ",aresample=48000",
            "-t",
            "60",
            "-c:v",
            "copy" if copy_video else "libx264",
            *(
                []
                if copy_video
                else ["-preset", "veryfast", "-crf", "20", "-threads", "2"]
            ),
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-c:s",
            "mov_text",
            "-metadata:s:s:0",
            "language=eng",
            "-movflags",
            "+faststart",
            str(encoding_target),
        ]
    )
    encoding_target.replace(target)
    run(
        [
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(target),
            "-map",
            "0:a:0",
            "-c:a",
            "copy",
            str(OUT / f"{ident}-{timing['voice']}-{timing['pace']}.m4a"),
        ]
    )
    run(
        [
            "-loglevel",
            "error",
            "-y",
            "-ss",
            "3",
            "-i",
            str(target),
            "-frames:v",
            "1",
            str(OUT / f"{ident}-poster.png"),
        ]
    )
    run(["-loglevel", "error", "-i", str(target), "-f", "null", "-"])
    info = run(
        [
            "-i",
            str(target),
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
            "-f",
            "null",
            "-",
        ]
    ).stderr.decode()
    final_audio = json.JSONDecoder().raw_decode(info[info.rfind("{") :])[0]
    cues = []
    for action in capture["actions"]:
        scene = next(
            (
                s
                for s in timing["segments"]
                if s["start"] - 0.1 <= action["at"] < s["end"] + 0.1
            ),
            None,
        )
        cues.append({**action, "scene": scene["id"] if scene else None})
    qa = {
        "variant": ident,
        "voice": timing["voice"],
        "pace": timing["pace"],
        "video": target.name,
        "audio": f"{ident}-{timing['voice']}-{timing['pace']}.m4a",
        "measured_original_wpm": timing["measured_original_wpm"],
        "source_audio_seconds": timing["original_audio_seconds"],
        "duration_seconds": 60,
        "resolution": "1920x1080",
        "fps": 25,
        "caption_cues": count,
        "transcript_match": timing["transcript_match"],
        "recording_trim_offset": offset,
        "decode_pass": True,
        "audio_time_stretch": False,
        "video_time_stretch": False,
        "integrated_lufs": float(final_audio["input_i"]),
        "true_peak_dbtp": float(final_audio["input_tp"]),
        "workflow_checks": capture["checks"],
        "actions": cues,
        "subjective_voice_review": "Awaiting user audition",
    }
    assert abs(qa["integrated_lufs"] + 16) < 0.8 and qa["true_peak_dbtp"] <= -1.5
    results.append(qa)
    print(ident, target.name, "PASS", flush=True)
(OUT / "media-qa.json").write_text(
    json.dumps({"status": "PASS", "variants": results}, indent=2) + "\n"
)
