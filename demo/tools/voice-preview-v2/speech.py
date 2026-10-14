"""Approved four-voice audition: four TTS + four word-timing requests, no retries.

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
WORK = ROOT / "demo/work/voice-preview-v2"
OUTPUT = ROOT / "demo/voice-preview-v2"
STORY = json.loads(Path(__file__).with_name("story.json").read_text())
TEXT = "\n\n".join(s["text"] for s in STORY["segments"])
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
        "accounted_usd": used / 1e6,
        "holds_usd": holds / 1e6,
        "generation_rows": calls,
    }


def request(ident, endpoint, model, bound, *, body=None, audio=None):
    manifest = (
        json.loads(MANIFEST.read_text())
        if MANIFEST.exists()
        else {"cap_usd": 0.5, "maximum_api_calls": 8, "requests": []}
    )
    previous = next((r for r in manifest["requests"] if r["id"] == ident), None)
    if previous:
        if previous["state"] != "SUCCEEDED":
            raise RuntimeError(
                "An earlier attempt is unresolved or failed; no automatic retry"
            )
        return None
    if len(manifest["requests"]) >= 8:
        raise RuntimeError("Eight-call media limit reached")
    accounted = sum(
        r.get("settled_usd", r["reserved_usd"]) for r in manifest["requests"]
    )
    product = product_snapshot()
    if (
        accounted + bound > 0.5 + 1e-9
        or product["accounted_usd"] + product["holds_usd"] + accounted + bound > 5
    ):
        raise RuntimeError("Speech/combined spending ceiling reached")
    row = {
        "id": ident,
        "endpoint": endpoint,
        "model": model,
        "reserved_usd": bound,
        "state": "RESERVED",
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
            timeout=60, trust_env=False, follow_redirects=False
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
                                "public-product-narration.wav",
                                stream,
                                "audio/wav",
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


def generate():
    for v in STORY["variants"]:
        ident = v["id"]
        instructions = (
            "You are a friendly product expert giving a colleague a short screen walkthrough. "
            "Use natural US English, warm understated confidence, conversational inflection and consistent volume. "
            "Read exactly the supplied text, with no intro, labels, filler or extra words. "
            "GitHub is pronounced Git Hub; AI is pronounced A eye. Avoid an announcer voice. "
            f"Aim for about {v['target_wpm']} spoken words per minute. "
            + (
                "Use relaxed deliberate phrasing, clear clause boundaries and small natural pauses. "
                if v["pace"] == "calm"
                else "Keep a fluid conversational pace with gentle energy. "
            )
            + "Use a short natural pause between paragraphs. Finish in under 58 seconds."
        )
        body = {
            "model": STORY["model"],
            "voice": v["voice"],
            "input": TEXT,
            "instructions": instructions,
            "response_format": "wav",
            "speed": v["speed"],
        }
        assert len(TEXT) < 1200 and len((TEXT + instructions).encode()) < 2000
        path = WORK / f"{ident}-original.wav"
        response = request(
            ident + "-tts", "audio/speech", STORY["model"], 0.10, body=body
        )
        if response is not None:
            path.write_bytes(response.content)
            save(WORK / f"{ident}-tts-settings.json", body)
        if not path.exists():
            raise RuntimeError(
                "Successful request output missing; do not repeat the call"
            )
        normalize_header(path)
        seconds = duration(path)
        if not 20 < seconds < 100:
            raise RuntimeError("Narration duration outside the reviewed bound")
        print(ident, v["voice"], v["pace"], round(seconds, 3), "seconds", flush=True)


def tokens(text):
    return [
        re.sub(r"[^a-z0-9]", "", w.lower())
        for w in text.split()
        if re.sub(r"[^a-z0-9]", "", w.lower())
    ]


def complete_cedar():
    text = STORY["segments"][-1]["text"]
    body = {
        "model": STORY["model"],
        "voice": "cedar",
        "input": text,
        "response_format": "wav",
        "speed": 0.93,
        "instructions": "Read this exact single sentence in natural, warm US English, in a calm conversational product-guide voice. No extra words. Gentle falling intonation at the end.",
    }
    response = request(
        "cedar-closing-repair", "audio/speech", STORY["model"], 0.04, body=body
    )
    target = WORK / "cedar-closing.wav"
    if response is not None:
        target.write_bytes(response.content)
        normalize_header(target)
    assert 1 < duration(target) < 10
    print(
        "Cedar closing sentence repaired:",
        round(duration(target), 3),
        "seconds",
        flush=True,
    )


def align():
    # Batch two public clips per timing request. This preserves the approved
    # eight-call cap even including the recorded HTTP 400 from a malformed header.
    transcriptions = {}
    for left, right in [("A", "B"), ("C", "D")]:
        pair = left + right
        pair_path = WORK / f"{pair}-timing-input.wav"
        tracks = []
        for ident in (left, right):
            with wave.open(str(WORK / f"{ident}-original.wav")) as audio:
                params = audio.getparams()
                frames = audio.readframes(audio.getnframes())
                assert (
                    params.nframes
                    == len(frames) // params.nchannels // params.sampwidth
                )
                assert (
                    params.framerate == 24000
                    and params.sampwidth == 2
                    and params.nchannels == 1
                )
                tracks.append(frames)
        offset = len(tracks[0]) / 2 / 24000 + 2
        with wave.open(str(pair_path), "wb") as output:
            output.setparams((1, 2, 24000, 0, "NONE", "not compressed"))
            output.writeframes(tracks[0] + bytes(2 * 24000 * 2) + tracks[1])
        assert 20 < duration(pair_path) < 180
        response = request(
            pair + "-timing", "audio/transcriptions", "whisper-1", 0.02, audio=pair_path
        )
        target = WORK / f"{pair}-transcription.json"
        if response is not None:
            save(target, response.json())
        data = json.loads(target.read_text())
        for ident, start, end in [
            (left, 0, offset - 1),
            (right, offset, duration(pair_path) + 1),
        ]:
            words = [
                {
                    **w,
                    "start": max(0, w["start"] - start),
                    "end": max(0, w["end"] - start),
                }
                for w in data["words"]
                if start - 0.75 <= w["start"] < end
            ]
            transcriptions[ident] = {
                "words": words,
                "text": " ".join(w["word"] for w in words),
                "timing_request": pair,
            }
    for v in STORY["variants"]:
        ident = v["id"]
        path = WORK / f"{ident}-original.wav"
        target = WORK / f"{ident}-transcription.json"
        transcript = transcriptions[ident]
        save(target, transcript)
        words = transcript["words"]
        expected = tokens(TEXT)
        observed = [re.sub(r"[^a-z0-9]", "", w["word"].lower()) for w in words]
        matcher = SequenceMatcher(None, expected, observed, autojunk=False)
        indices = {
            a + i: b + i
            for a, b, size in matcher.get_matching_blocks()
            for i in range(size)
        }
        ratio = len(indices) / len(expected)
        repair = (
            ident in {"B", "D"} and words[-1]["word"].lower().strip(".,") == "rules"
        )
        if repair:
            # The ASR outputs end at the original speech tail; both Cedar takes
            # omitted the final sentence. Reuse one separately generated Cedar
            # closing sentence. Its caption uses the measured sentence envelope,
            # rather than inventing per-word timestamps.
            core_expected = tokens("\n".join(s["text"] for s in STORY["segments"][:-1]))
            ratio = len(indices) / len(core_expected)
        if ratio < 0.96:
            raise RuntimeError(
                f"Transcript mismatch {ident}: {ratio:.3f}; review before rendering"
            )
        with wave.open(str(path)) as wav:
            params = wav.getparams()
            assert params.sampwidth == 2 and params.nchannels == 1
            data = np.frombuffer(wav.readframes(wav.getnframes()), dtype=np.int16)
        if repair:
            with wave.open(str(WORK / "cedar-closing.wav")) as closing:
                assert closing.getframerate() == params.framerate
                tail = np.frombuffer(
                    closing.readframes(closing.getnframes()), dtype=np.int16
                )
            start = len(data) / params.framerate + 0.22
            data = np.concatenate(
                [data, np.zeros(round(0.22 * params.framerate), dtype=np.int16), tail]
            )
            # The single caption entry covers the actual measured closing audio.
            words.append(
                {
                    "word": STORY["segments"][-1]["text"],
                    "start": start,
                    "end": len(data) / params.framerate,
                }
            )
        # Boundaries are based on the provider's word timestamps; preserve the waveform.
        groups, cursor = [], 0
        for s in STORY["segments"]:
            count = len(tokens(s["text"]))
            if repair and s["id"] == "appearance":
                first = last = len(words) - 1
            else:
                first = next(
                    indices[i] for i in range(cursor, cursor + count) if i in indices
                )
                last = next(
                    indices[i]
                    for i in reversed(range(cursor, cursor + count))
                    if i in indices
                )
            groups.append(
                {
                    **s,
                    "first_word": first,
                    "last_word": last,
                    "spoken_start": words[first]["start"],
                    "spoken_end": words[last]["end"],
                }
            )
            cursor += count
        boundaries = [max(0, groups[0]["spoken_start"] - 0.12)]
        for prev, nxt in pairwise(groups):
            # ASR boundaries can overlap slightly; never cut before the previous word ends.
            boundaries.append(
                max(prev["spoken_end"], (prev["spoken_end"] + nxt["spoken_start"]) / 2)
            )
        boundaries.append(
            min(len(data) / params.framerate, groups[-1]["spoken_end"] + 0.15)
        )
        clips = [
            data[round(a * params.framerate) : round(b * params.framerate)]
            for a, b in pairwise(boundaries)
        ]
        raw = [len(c) / params.framerate for c in clips]
        # Reserve practical UI interaction time without stretching audio or action footage.
        minimums = [5.5, 5.0, 4.0, 6.0, 10.0, 8.0, 6.0, 5.0]
        spans = [max(r + 0.35, m) for r, m in zip(raw, minimums)]
        if sum(spans) > 60:
            raise RuntimeError(
                f"Narration/action windows exceed one minute for {ident}: {sum(spans):.2f}"
            )
        weights = [0.8, 1, 0.7, 1.1, 1, 1, 0.7, 0.7]
        spare = 60 - sum(spans)
        spans = [a + spare * b / sum(weights) for a, b in zip(spans, weights)]
        track = np.zeros(60 * params.framerate, dtype=np.int16)
        clock = 0.0
        output_words = []
        for i, (s, clip, span) in enumerate(zip(groups, clips, spans)):
            # A small lead allows the pointer/scene to arrive before the first spoken noun.
            lead = min(0.45, max(0.12, (span - raw[i]) * 0.35))
            offset = clock + lead
            start = round(offset * params.framerate)
            # Four-millisecond edge fades prevent low-level clicks at added rests.
            clip = clip.copy()
            fade = min(round(0.004 * params.framerate), len(clip) // 2)
            if fade:
                clip[:fade] = (clip[:fade] * np.linspace(0, 1, fade)).astype(np.int16)
                clip[-fade:] = (clip[-fade:] * np.linspace(1, 0, fade)).astype(np.int16)
            track[start : start + len(clip)] = clip
            s.update(
                start=round(clock, 4),
                end=round(clock + span, 4),
                audio_start=round(offset, 4),
                raw_start=boundaries[i],
                audio_seconds=raw[i],
            )
            for word in words[s["first_word"] : s["last_word"] + 1]:
                output_words.append(
                    {
                        "word": word["word"],
                        "start": round(offset + word["start"] - boundaries[i], 4),
                        "end": round(offset + word["end"] - boundaries[i], 4),
                        "scene": s["id"],
                    }
                )
            clock += span
        with wave.open(str(WORK / f"{ident}-aligned.wav"), "wb") as wav:
            wav.setparams(params)
            wav.writeframes(track.tobytes())
        result = {
            **v,
            "segments": groups,
            "words": output_words,
            "duration": 60,
            "cedar_closing_repair": repair,
            "original_take_seconds": duration(path),
            "original_audio_seconds": len(data) / params.framerate,
            "measured_original_wpm": round(
                len(expected) / (len(data) / params.framerate) * 60, 1
            ),
            "transcript_match": ratio,
            "timing_source": "whisper-1 word timestamps; Cedar closing repair uses its measured sentence envelope",
            "speech_time_stretch": False,
        }
        save(WORK / f"{ident}-timeline.json", result)
        save(OUTPUT / f"{ident}-timing.json", result)
        print(
            ident,
            "aligned",
            result["measured_original_wpm"],
            "wpm;",
            round(ratio * 100, 1),
            "% transcript match",
            flush=True,
        )
    manifest = json.loads(MANIFEST.read_text())
    manifest["accounted_media_usd"] = round(
        sum(r.get("settled_usd", r["reserved_usd"]) for r in manifest["requests"]), 6
    )
    manifest["product_after"] = product_snapshot()
    manifest["combined_accounted_usd"] = round(
        manifest["accounted_media_usd"] + manifest["product_after"]["accounted_usd"], 6
    )
    manifest["cost_note"] = (
        "Conservative holds retained: $0.10/original TTS, $0.04/short closing repair, $0.02/timing attempt including one failed request. Binary speech responses have no token usage. These are not invoiced charges."
    )
    manifest["price_reference"] = {
        "tts_text_per_million": 0.6,
        "tts_audio_per_million": 12,
        "whisper_per_minute": 0.006,
        "checked": "2026-10-13",
        "sources": [
            "https://developers.openai.com/api/docs/models/gpt-4o-mini-tts",
            "https://developers.openai.com/api/docs/models/whisper-1",
        ],
    }
    save(MANIFEST, manifest)
    save(OUTPUT / "speech-requests.json", manifest)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--align", action="store_true")
    parser.add_argument("--complete-cedar", action="store_true")
    args = parser.parse_args()
    if not args.live or sum([args.generate, args.align, args.complete_cedar]) != 1:
        parser.error(
            "Choose exactly one of --generate/--align/--complete-cedar, with --live"
        )
    try:
        generate() if args.generate else (
            complete_cedar() if args.complete_cedar else align()
        )
    except (
        RuntimeError,
        ValueError,
        OSError,
        httpx.HTTPError,
        AssertionError,
        KeyError,
    ) as error:
        # No exception request/body/header dumping; secrets remain local.
        print(type(error).__name__ + ": " + str(error), file=sys.stderr)
        sys.exit(1)
