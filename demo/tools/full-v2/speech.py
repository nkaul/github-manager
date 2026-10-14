"""Full Cedar narration: public product script only; no repository content in speech input.

Only the public product script and its generated audio leave localhost.
Binary speech responses have no billing usage; keep their conservative holds.
"""

import argparse
import hashlib
import json
import re
import sqlite3
import sys
import wave
from datetime import UTC, datetime
from difflib import SequenceMatcher
from itertools import pairwise
from pathlib import Path

import httpx
import numpy as np
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / "demo/work/full-v2"
OUTPUT = ROOT / "demo/full-v2"
STORY = json.loads(Path(__file__).with_name("story.json").read_text())
TEXT = "\n\n".join(b["text"] for c in STORY["chapters"] for b in c["beats"])
MANIFEST = WORK / "speech-requests.json"
WORK.mkdir(parents=True, exist_ok=True)
OUTPUT.mkdir(parents=True, exist_ok=True)


def save(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def product_snapshot():
    ledger = ROOT / "docs/validation/private/ai-pretest/runs.sqlite3"
    with sqlite3.connect(f"file:{ledger}?mode=ro", uri=True) as db:
        cap = db.execute("SELECT cap FROM experiment").fetchone()[0]
        used = db.execute(
            "SELECT COALESCE(SUM(COALESCE(charged,reserved)),0) FROM calls"
        ).fetchone()[0]
        holds = db.execute(
            "SELECT COALESCE(SUM(remaining),0) FROM app_run_budgets WHERE state IN ('HELD','QUEUED','RUNNING')"
        ).fetchone()[0]
        calls = db.execute("SELECT COUNT(*) FROM calls").fetchone()[0]
    app = ROOT / "docs/validation/private/demo/app.sqlite3"
    with sqlite3.connect(f"file:{app}?mode=ro", uri=True) as db:
        active = db.execute(
            "SELECT COUNT(*) FROM jobs WHERE status IN ('QUEUED','RUNNING')"
        ).fetchone()[0]
    if active or holds:
        raise RuntimeError(
            "Paid product jobs/holds are active; resume media calls after they finish"
        )
    return {
        "cap_usd": cap / 1e6,
        "accounted_usd": used / 1e6 + copy_delta() + 0.5,
        "prior_voice_preview_usd": 0.5,
        "real_demo_model_delta_usd": copy_delta(),
        "holds_usd": holds / 1e6,
        "generation_rows": calls,
    }


def request(ident, endpoint, model, bound, *, body=None, audio=None):
    manifest = (
        json.loads(MANIFEST.read_text())
        if MANIFEST.exists()
        else {"cap_usd": 2.5, "maximum_api_calls": 16, "requests": []}
    )
    previous = next((r for r in manifest["requests"] if r["id"] == ident), None)
    if previous:
        current_hash = hashlib.sha256(
            json.dumps(body, sort_keys=True).encode() if body else audio.read_bytes()
        ).hexdigest()
        if previous.get("public_input_sha256") != current_hash:
            raise RuntimeError(
                "Saved media request input changed; do not reuse its timing or repeat the call"
            )
        if previous["state"] != "SUCCEEDED":
            raise RuntimeError(
                "An earlier attempt is unresolved or failed; no automatic retry"
            )
        return None
    if (
        len(manifest["requests"]) >= 16
        or len(manifest["requests"]) + live_http_count() >= 20
    ):
        raise RuntimeError("Sixteen-call media limit reached")
    accounted = sum(
        r.get("settled_usd", r["reserved_usd"]) for r in manifest["requests"]
    )
    product = product_snapshot()
    if (
        accounted + bound > 2.5 + 1e-9
        or product["accounted_usd"] + product["holds_usd"] + accounted + bound > 5
    ):
        raise RuntimeError("Speech/combined spending ceiling reached")
    row = {
        "id": ident,
        "endpoint": endpoint,
        "model": model,
        "reserved_usd": bound,
        "state": "RESERVED",
        "public_input_sha256": hashlib.sha256(
            json.dumps(body, sort_keys=True).encode() if body else audio.read_bytes()
        ).hexdigest(),
        "at": datetime.now(UTC).isoformat(),
        "product_before": product,
    }
    manifest["requests"].append(row)
    save(MANIFEST, manifest)
    key = dotenv_values(ROOT / "backend/.env").get("OPENAI_API_KEY", "")
    if not key:
        raise RuntimeError("Missing configured speech credential")
    try:
        with httpx.Client(
            timeout=120, trust_env=False, follow_redirects=False
        ) as client:
            headers = {"Authorization": "Bearer " + key}
            if audio:
                with audio.open("rb") as stream:
                    response = client.post(
                        "https://api.openai.com/v1/" + endpoint,
                        headers=headers,
                        data={
                            "model": model,
                            "language": "en",
                            "response_format": "verbose_json",
                            "timestamp_granularities[]": "word",
                            "temperature": "0",
                        },
                        files={
                            "file": (
                                "public-product-narration.mp3",
                                stream,
                                "audio/mpeg",
                            )
                        },
                    )
            else:
                response = client.post(
                    "https://api.openai.com/v1/" + endpoint, headers=headers, json=body
                )
        row["http_status"] = response.status_code
        row["request_id"] = response.headers.get("x-request-id")
        if response.status_code != 200:
            row["state"] = "FAILED_REVIEW_REQUIRED"
            try:
                row["error_code"] = (
                    response.json().get("error", {}).get("code", "unclassified")
                )
            except ValueError:
                row["error_code"] = "non_json"
            raise RuntimeError(
                f"Speech provider HTTP {response.status_code}; see sanitized request manifest"
            )
        row["state"] = "SUCCEEDED"
        row["response_sha256"] = hashlib.sha256(response.content).hexdigest()
        row["bytes"] = len(response.content)
        save(MANIFEST, manifest)
        return response
    except Exception:
        if row["state"] == "RESERVED":
            row["state"] = "UNKNOWN_REVIEW_REQUIRED"
        save(MANIFEST, manifest)
        raise


def duration(path):
    with wave.open(str(path)) as audio:
        frames = audio.readframes(audio.getnframes())
        return (
            len(frames)
            / audio.getsampwidth()
            / audio.getnchannels()
            / audio.getframerate()
        )


def normalize_header(path):
    # Streaming WAV uses an unknown-length RIFF sentinel. Save a seekable header
    # without changing one PCM sample or repeating the provider request.
    with wave.open(str(path)) as audio:
        params = audio.getparams()
        pcm = audio.readframes(audio.getnframes())
    if params.nframes != len(pcm) // params.sampwidth // params.nchannels:
        path.with_name(path.stem + "-provider.wav").write_bytes(path.read_bytes())
        temporary = path.with_suffix(".normalized.wav")
        with wave.open(str(temporary), "wb") as audio:
            audio.setparams(
                (
                    params.nchannels,
                    params.sampwidth,
                    params.framerate,
                    0,
                    params.comptype,
                    params.compname,
                )
            )
            audio.writeframes(pcm)
        temporary.replace(path)


FF = ROOT / ".tools/video-python/imageio_ffmpeg/binaries/ffmpeg-macos-x86_64-v7.1"


def copy_delta():
    with sqlite3.connect(
        f"file:{ROOT / 'docs/validation/private/demo/full-v2/ai/runs.sqlite3'}?mode=ro",
        uri=True,
    ) as db:
        used = db.execute(
            "SELECT COALESCE(SUM(COALESCE(charged,reserved)),0) FROM calls"
        ).fetchone()[0]
    return max(0, used - 127619) / 1e6


def live_http_count():
    audit = ROOT / "docs/validation/private/demo/full-v2/live-http.json"
    return len(json.loads(audit.read_text())) if audit.exists() else 0


def ff(args):
    import subprocess

    r = subprocess.run(
        [str(FF), "-hide_banner", "-nostdin", *args], capture_output=True, check=False
    )
    if r.returncode:
        raise RuntimeError(r.stderr.decode()[-900:])
    return r


def batches():
    flat = [
        {"id": c["id"] + "-" + b["id"], "chapter": c["id"], **b}
        for c in STORY["chapters"]
        for b in c["beats"]
    ]
    # Twelve paragraphs = three chapters. Fixed public narration only.
    return [flat[i : i + 12] for i in range(0, len(flat), 12)]


def generate():
    frozen = WORK / "frozen-story.json"
    if frozen.exists() and json.loads(frozen.read_text()) != STORY:
        raise RuntimeError(
            "Narration script changed after freezing; review before any new call"
        )
    save(frozen, STORY)
    capture = json.loads((WORK / "capture.json").read_text())
    if capture.get("status") != "PASS":
        raise RuntimeError(
            "Finish and verify the current UI recording before paid narration"
        )
    for i, group in enumerate(batches()):
        ident = f"tts-{i + 1:02}"
        narration = "\n\n".join(b["text"] for b in group) + "\n\nEnd of narration."
        instructions = (
            "You are the same friendly product expert throughout a complete screen tutorial. "
            "Read exactly the supplied text, with warm understated confidence, a natural clear US English voice, "
            "consistent volume and relaxed deliberate phrasing. Use the calm Cedar tutorial delivery selected in option D. "
            "Give each paragraph a short natural pause and a clear sentence ending. Do not rush the ending. "
            "Pronounce GitHub as Git Hub, AI as A eye, OAuth as Oh auth, and SQLite as S Q L lite. "
            "Avoid an announcer voice. Do not add introductory words or omit any sentence. "
            "End of narration is a timing marker; read it normally after a short pause."
        )
        if len(narration) > 4000:
            raise RuntimeError("Speech input too long")
        r = request(
            ident,
            "audio/speech",
            STORY["model"],
            0.12,
            body={
                "model": STORY["model"],
                "voice": "cedar",
                "input": narration,
                "instructions": instructions,
                "response_format": "wav",
                "speed": 0.93,
            },
        )
        target = WORK / (ident + ".wav")
        if r is not None:
            target.write_bytes(r.content)
        if not target.exists():
            raise RuntimeError(
                "Successful request missing its saved audio; manual recovery required"
            )
        normalize_header(target)
        save(
            WORK / (ident + "-script.json"),
            {"beats": group, "text": narration, "duration": duration(target)},
        )
        print(ident, round(duration(target), 2), "seconds", flush=True)


def norm(s):
    token = re.sub(r"[^a-z0-9]", "", s.lower())
    numbers = {
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
        "ten": "10",
        "fourteen": "14",
        "twenty": "20",
        "thirty": "30",
        "ninety": "90",
    }
    if token in numbers:
        return numbers[token]
    for word, digit in numbers.items():
        if token in {word + "day", word + "days", word + "second", word + "seconds"}:
            return digit + token[len(word) :]
    return token


def tokens(s):
    result = []
    for text in re.findall(r"[A-Za-z0-9]+(?:[’\'][A-Za-z0-9]+)?", s):
        token = norm(text)
        result.extend(
            {
                "backend": ["back", "end"],
                "frontend": ["front", "end"],
                "github": ["git", "hub"],
                "readme": ["read", "me"],
                "pretesting": ["pre", "testing"],
                "reanalysis": ["re", "analysis"],
                "reanalyze": ["re", "analyze"],
            }.get(token, [token])
        )
    return result


def align():
    files = [WORK / f"tts-{i + 1:02}.wav" for i in range(len(batches()))]
    divided = [files[:6], files[6:]]
    all_transcripts = {}
    for batch, fileset in enumerate(divided, 1):
        samples = []
        offsets = []
        clock = 0
        params = None
        for f in fileset:
            with wave.open(str(f)) as w:
                params = w.getparams()
                data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
            offsets.append((f, clock, len(data) / params.framerate))
            samples.extend([data, np.zeros(params.framerate * 2, dtype=np.int16)])
            clock += len(data) / params.framerate + 2
        joined = WORK / f"align-{batch}.wav"
        with wave.open(str(joined), "wb") as w:
            w.setparams((1, 2, params.framerate, 0, "NONE", "not compressed"))
            w.writeframes(np.concatenate(samples).tobytes())
        mp3 = joined.with_suffix(".mp3")
        ff(
            [
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(joined),
                "-ar",
                "16000",
                "-b:a",
                "64k",
                str(mp3),
            ]
        )
        target = WORK / f"align-{batch}.json"
        r = request(
            f"asr-{batch}", "audio/transcriptions", "whisper-1", 0.10, audio=mp3
        )
        if r is not None:
            save(target, r.json())
        transcript = json.loads(target.read_text())
        for f, offset, length in offsets:
            words = [
                {
                    **w,
                    "start": max(0, w["start"] - offset),
                    "end": min(length, w["end"] - offset),
                }
                for w in transcript["words"]
                if offset - 0.75 <= w["start"] < offset + length
            ]
            all_transcripts[f.stem] = words
    result = {
        "voice": "cedar",
        "speed": 0.93,
        "option": "D · calmer delivery",
        "timing_source": "whisper-1 actual spoken word timestamps",
        "beats": [],
        "words": [],
        "duration": 0,
        "raw_spoken_seconds": 0,
    }
    cursor = 0.0
    repairs = (
        json.loads((WORK / "repairs.json").read_text())
        if (WORK / "repairs.json").exists()
        else {}
    )
    result["narration_repairs"] = {
        key: {k: v for k, v in value.items() if k not in {"file", "words"}}
        for key, value in repairs.items()
    }
    capture = json.loads((WORK / "capture.json").read_text())
    for f in files:
        script = json.loads(f.with_name(f.stem + "-script.json").read_text())
        words = all_transcripts[f.stem]
        expected = tokens("\n\n".join(b["text"] for b in script["beats"]))
        observed, observed_indices = [], []
        for index, word in enumerate(words):
            pieces = tokens(word["word"])
            observed.extend(pieces)
            observed_indices.extend([index] * len(pieces))
        matches = SequenceMatcher(None, expected, observed, autojunk=False)
        indices = {
            a + i: observed_indices[b + i]
            for a, b, n in matches.get_matching_blocks()
            for i in range(n)
        }
        ratio = len(indices) / len(expected)
        save(
            WORK / (f.stem + "-word-review.json"),
            {
                "expected": expected,
                "observed_tokens": observed,
                "observed_word_indices": observed_indices,
                "words": words,
                "match": ratio,
                "opcodes": matches.get_opcodes(),
            },
        )
        if ratio < 0.965:
            raise RuntimeError(
                f"{f.stem} word agreement {ratio:.3f}; review before rendering"
            )
        with wave.open(str(f)) as w:
            params = w.getparams()
            data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
        source_index = 0
        groups = []
        for b in script["beats"]:
            count = len(tokens(b["text"]))
            mapped = [
                indices[x]
                for x in range(source_index, source_index + count)
                if x in indices
            ]
            if len(mapped) < count * 0.85:
                raise RuntimeError(
                    "Incomplete spoken paragraph " + b["chapter"] + " " + b["id"]
                )
            groups.append((b, mapped[0], mapped[-1]))
            source_index += count
        boundaries = [max(0, words[groups[0][1]]["start"] - 0.15)]
        for (_, _, last), (_, first, _) in pairwise(groups):
            boundaries.append(
                max(
                    words[last]["end"], (words[last]["end"] + words[first]["start"]) / 2
                )
            )
        boundaries.append(
            min(len(data) / params.framerate, words[groups[-1][2]]["end"] + 0.15)
        )
        for i, (b, first, last) in enumerate(groups):
            a, z = boundaries[i : i + 2]
            clip = data[
                round(a * params.framerate) : round(z * params.framerate)
            ].copy()
            selected_words = words[first : last + 1]
            repair = repairs.get(b["chapter"] + "-" + b["id"])
            if repair:
                with wave.open(repair["file"]) as repaired:
                    assert repaired.getframerate() == params.framerate
                    pcm = np.frombuffer(
                        repaired.readframes(repaired.getnframes()), dtype=np.int16
                    )
                a, z = repair["trim_start"], repair["trim_end"]
                clip = pcm[
                    round(a * params.framerate) : round(z * params.framerate)
                ].copy()
                selected_words = repair["words"]
                b = {**b, "text": repair["text"]}
            fade = min(round(0.004 * params.framerate), len(clip) // 2)
            clip[:fade] = (clip[:fade] * np.linspace(0, 1, fade)).astype(np.int16)
            clip[-fade:] = (clip[-fade:] * np.linspace(1, 0, fade)).astype(np.int16)
            raw_seconds = len(clip) / params.framerate
            chapter = next(c for c in capture["chapters"] if c["id"] == b["chapter"])
            recorded = next(x for x in chapter["beats"] if x["id"] == b["id"])
            # Keep actions at natural speed. Long waits become explicit edits; result holds provide reading time.
            action_span = recorded["end"] - recorded["start"]
            visible = min(action_span, 8) if action_span > 15 else action_span
            span = max(raw_seconds + 0.95, visible + 0.6, 8.0)
            span = np.ceil(span * 25) / 25
            output = WORK / f"beat-{b['chapter']}-{b['id']}.wav"
            with wave.open(str(output), "wb") as w:
                w.setparams((1, 2, params.framerate, 0, "NONE", "not compressed"))
                w.writeframes(clip.tobytes())
            row = {
                **b,
                "key": b["chapter"] + "-" + b["id"],
                "start": round(cursor, 4),
                "end": round(cursor + span, 4),
                "span": span,
                "audio_start": round(cursor + 0.4, 4),
                "raw_start": a,
                "audio_seconds": raw_seconds,
                "file": str(output),
                "transcript_match": ratio,
                "capture": recorded,
            }
            result["beats"].append(row)
            for w in selected_words:
                result["words"].append(
                    {
                        "word": w["word"],
                        "start": round(cursor + 0.4 + w["start"] - a, 4),
                        "end": round(cursor + 0.4 + w["end"] - a, 4),
                        "scene": b["chapter"],
                        "beat": b["id"],
                    }
                )
            cursor += span
            result["raw_spoken_seconds"] += raw_seconds
        print(f.stem, "timed", round(100 * ratio, 2), "%", flush=True)
    result["duration"] = round(cursor, 4)
    result["measured_wpm"] = round(
        sum(len(b["text"].split()) for b in result["beats"])
        / result["raw_spoken_seconds"]
        * 60,
        1,
    )
    save(WORK / "timeline.json", result)
    manifest = json.loads(MANIFEST.read_text())
    manifest.update(
        accounted_media_usd=sum(
            r.get("settled_usd", r["reserved_usd"]) for r in manifest["requests"]
        ),
        product_after=product_snapshot(),
        new_intelligence_http=live_http_count(),
        voice="cedar",
        option="D · calmer delivery",
        cost_note="Conservative media reservations; binary TTS responses do not include invoiced token usage.",
    )
    manifest["combined_accounted_usd"] = (
        manifest["accounted_media_usd"] + manifest["product_after"]["accounted_usd"]
    )
    save(MANIFEST, manifest)
    save(OUTPUT / "speech-requests.json", manifest)
    print(
        "Aligned",
        round(cursor / 60, 2),
        "minutes;",
        result["measured_wpm"],
        "wpm",
        flush=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("operation", choices=["generate", "align"])
    args = parser.parse_args()
    if not args.live:
        parser.error("--live required")
    try:
        generate() if args.operation == "generate" else align()
    except (
        RuntimeError,
        ValueError,
        OSError,
        httpx.HTTPError,
        AssertionError,
        KeyError,
        IndexError,
    ) as e:
        print(type(e).__name__ + ": " + str(e).split("Request(")[0], file=sys.stderr)
        sys.exit(1)
