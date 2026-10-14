"""Offline native narration; no API credentials, uploads or paid speech calls."""

import json
import subprocess
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "demo/work"
WORK.mkdir(parents=True, exist_ok=True)
FFMPEG = ROOT / ".tools/video-python/imageio_ffmpeg/binaries/ffmpeg-macos-x86_64-v7.1"
story = json.loads((ROOT / "demo/tools/story.json").read_text())
for chapter in story:
    stem = WORK / chapter["id"]
    text = stem.with_suffix(".txt")
    aiff = stem.with_suffix(".aiff")
    wav = stem.with_suffix(".wav")
    if not wav.exists() or not text.exists() or text.read_text() != chapter["narration"]:
        text.write_text(chapter["narration"])
        subprocess.run(["/usr/bin/say", "-v", "Samantha", "-r", "158", "-f", str(text), "-o", str(aiff)], check=True)
        subprocess.run([str(FFMPEG), "-hide_banner", "-loglevel", "error", "-y", "-i", str(aiff), "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(wav)], check=True)
    with wave.open(str(wav)) as audio:
        chapter["audio_seconds"] = audio.getnframes() / audio.getframerate()
    print(chapter["id"], chapter["title"], round(chapter["audio_seconds"], 2), flush=True)
(WORK / "story-audio.json").write_text(json.dumps(story, indent=2))
