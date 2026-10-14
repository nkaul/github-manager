"""One targeted Cedar retake to avoid weighted/unweighted acoustic ambiguity."""

import importlib.util
import json
from difflib import SequenceMatcher
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "full_speech", Path(__file__).with_name("speech.py")
)
speech = importlib.util.module_from_spec(spec)
spec.loader.exec_module(speech)
text = "Automatic organization is configurable. Weighted changes across distinct entities can trigger it. A configured number of new Projects can also trigger it, within the change window."
body = {
    "model": "gpt-4o-mini-tts",
    "voice": "cedar",
    "speed": 0.93,
    "response_format": "wav",
    "input": text + "\n\nEnd of narration.",
    "instructions": "Use the same warm, calm and deliberate Cedar tutorial delivery as the rest of this screen walkthrough. Read exactly the supplied text in natural clear US English, with consistent volume and short natural clause pauses. Give Weighted changes a clear sentence beginning. Avoid an announcer voice. Read the ending marker normally after a pause.",
}
r = speech.request(
    "tts-repair-weighted", "audio/speech", "gpt-4o-mini-tts", 0.04, body=body
)
wavefile = speech.WORK / "weighted-repair.wav"
if r is not None:
    wavefile.write_bytes(r.content)
speech.normalize_header(wavefile)
mp3 = wavefile.with_suffix(".mp3")
speech.ff(
    [
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(wavefile),
        "-ar",
        "16000",
        "-b:a",
        "64k",
        str(mp3),
    ]
)
r = speech.request(
    "asr-repair-weighted", "audio/transcriptions", "whisper-1", 0.02, audio=mp3
)
target = speech.WORK / "weighted-repair-transcript.json"
if r is not None:
    speech.save(target, r.json())
words = json.loads(target.read_text())["words"]
expected = speech.tokens(text)
observed = []
word_indices = []
for i, w in enumerate(words):
    parts = speech.tokens(w["word"])
    observed.extend(parts)
    word_indices.extend([i] * len(parts))
matcher = SequenceMatcher(None, expected, observed, autojunk=False)
matches = {
    a + i: word_indices[b + i]
    for a, b, n in matcher.get_matching_blocks()
    for i in range(n)
}
ratio = len(matches) / len(expected)
if ratio < 0.97:
    raise RuntimeError(f"Targeted retake transcript needs review: {ratio:.3f}")
first = matches[0]
last = matches[len(expected) - 1]
value = {
    "21-thresholds": {
        "text": text,
        "file": str(wavefile),
        "words": words[first : last + 1],
        "trim_start": max(0, words[first]["start"] - 0.15),
        "trim_end": min(speech.duration(wavefile), words[last]["end"] + 0.15),
        "match": ratio,
        "reason": "Original ASR read “on weighted” as “unweighted”; a new sentence beginning removes that ambiguity. No speech stretching.",
    }
}
speech.save(speech.WORK / "repairs.json", value)
print(
    "Targeted calm Cedar retake validated; word match",
    round(ratio * 100, 2),
    "%; two bounded media calls",
)
