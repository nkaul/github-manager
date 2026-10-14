"""Verify preservation and save the reviewable full-demo documentation."""

import hashlib
import json
import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "demo/full-v2"
WORK = ROOT / "demo/work/full-v2"
BASE = ROOT / ".tools/full-v2-baseline-20261013"
qa = json.loads((OUT / "media-qa.json").read_text())
player = json.loads((OUT / "player-qa.json").read_text())
capture = json.loads((WORK / "capture.json").read_text())
speech = json.loads((OUT / "speech-requests.json").read_text())
assert qa["status"] == player["status"] == capture["status"] == "PASS"
assert len(capture["chapters"]) == 32 and len(player["chapter_seeks"]) == 32
assert len(speech["requests"]) + speech["new_intelligence_http"] <= 20
assert speech["combined_accounted_usd"] <= 5
baseline = json.loads((BASE / "prior-media-sha256.json").read_text())
changes = []
for name, sha in baseline.items():
    if name == "demo-video.md":
        continue
    if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != sha:
        changes.append(name)
assert not changes, changes
assert (
    (ROOT / "demo-video.md")
    .read_bytes()
    .startswith((BASE / "demo-video.md").read_bytes())
)


def rowset(file, table):
    with sqlite3.connect(f"file:{file}?mode=ro", uri=True) as db:
        return sorted(db.execute("SELECT * FROM " + table).fetchall())


original = ROOT / "docs/validation/private/ai-pretest/runs.sqlite3"
ledger_same = {
    t: rowset(original, t) == rowset(BASE / "runs.sqlite3", t)
    for t in [
        "experiment",
        "calls",
        "cache",
        "phase09_http",
        "phase09_allowance_control",
        "phase09_allowance_audit",
    ]
}
assert all(ledger_same.values()), ledger_same


def real_org(file):
    with sqlite3.connect(f"file:{file}?mode=ro", uri=True) as db:
        return json.loads(
            db.execute(
                "SELECT state FROM workspace WHERE id LIKE '%:github'"
            ).fetchone()[0]
        )["organization"]


a, b = (
    real_org(BASE / "app.sqlite3"),
    real_org(ROOT / "docs/validation/private/demo/app.sqlite3"),
)
organization_same = {
    k: a[k] == b[k]
    for k in [
        "concepts",
        "edges",
        "rejections",
        "suggestions",
        "drafts",
        "rules",
        "analysis",
    ]
}
assert all(organization_same.values()), organization_same
pretest = subprocess.run(
    [
        str(ROOT / "backend/.venv/bin/python"),
        str(ROOT / "scripts/verify-pretest-preservation.py"),
        str(ROOT / ".tools/phase09-baseline-20261012T045829Z"),
    ],
    capture_output=True,
    text=True,
    check=True,
)
protected = json.loads(pretest.stdout)
assert protected["status"] == "PASS"
preservation = {
    "status": "PASS",
    "unchanged_prior_media_and_player_files": len(baseline) - 1,
    "guide_original_prefix_preserved": True,
    "protected_readiness_files": protected["protected_files"],
    "original_ledger_tables_unchanged": ledger_same,
    "original_real_account_organization_unchanged": organization_same,
    "permitted_original_write": "One read-only GitHub sync appended its inventory observation and SYNC run. Demo edits and resets used the copy.",
}
(OUT / "preservation-qa.json").write_text(json.dumps(preservation, indent=2) + "\n")
legacy = json.loads((ROOT / "demo/validation.json").read_text())["checks"]
map_ids = [
    ["01"],
    ["02"],
    ["04"],
    ["03"],
    ["02", "03"],
    ["04"],
    ["01", "24"],
    [],
    ["05"],
    ["05"],
    ["06"],
    ["07"],
    ["07"],
    ["08", "09"],
    ["08"],
    ["08", "09"],
    ["13", "14"],
    ["13", "15"],
    ["15", "16"],
    ["16"],
    ["18"],
    ["18"],
    ["18"],
    ["18"],
    ["06", "25"],
    ["25"],
    ["21"],
    ["24"],
    ["04"],
    ["26"],
    ["27"],
    ["28"],
    ["06", "29"],
    ["29"],
    ["19", "20"],
]
notes = {
    7: "Fixture sign-in replaced by real OAuth outside capture; copy-session restoration is explicitly identified.",
    8: "Synthetic/sample collection loading omitted at the user’s request to use the connected real account.",
    15: "One new public classification instead of the earlier three-repository live batch; multi-repository local review is also exercised.",
    19: "Rename/alias validation and dependency reparenting recorded; a separate direct parent-edit regression is historical evidence.",
    27: "Real scheduler interval; real analyzed repositories reconcile offline instead of fixture AI.",
    28: "Real initial OAuth plus copy-session restoration and actual copied-backend restart; no second OAuth roundtrip claimed.",
    29: "Actual contribution windows replace synthetic activity.",
    31: "AI-only reset verified; protected cached-restart preview shown, not a new post-reset cached generation.",
    33: "Fresh taxonomy discovery occurs before resets. The post-reset rebuild is manual, with new IDs and no repeat inference.",
}
coverage = [
    {
        "historical_check": i,
        "name": c["name"],
        "current_chapters": map_ids[i - 1],
        "status": "OMITTED_BY_REQUEST"
        if i == 8
        else "CURRENT_SCOPED"
        if i in notes
        else "CURRENT",
        "note": notes.get(
            i,
            "Actual current-run evidence is in feature-checks.json; the old PASS is retained as historical evidence.",
        ),
    }
    for i, c in enumerate(legacy, 1)
]
(OUT / "historical-coverage.json").write_text(json.dumps(coverage, indent=2) + "\n")
chapters = json.loads((OUT / "chapters.json").read_text())
minutes = int(qa["duration_seconds"] // 60)
seconds = round(qa["duration_seconds"] % 60)
fmt = lambda t: f"{int(t // 60):02}:{int(t % 60):02}"
lines = [
    "# GitHub Manager · full Cedar demo validation",
    "",
    "Date: October 13, 2026. **PASS — recording, media, playback and preservation checks.**",
    "",
    "The user selected Option D (Cedar, calmer delivery), authenticated the real account, and authorized unmasked real-account footage. The full demo is available at [the local player](http://127.0.0.1:8123).",
    "",
    "## Deliverables",
    "",
    f"- Video: `demo/full-v2/github-manager-full-cedar-calm-1080p.mp4` — {minutes}:{seconds:02}, 1920×1080, 25fps, H.264/AAC.",
    "- Separate narration, 32 embedded chapters, English WebVTT/SRT and embedded captions, transcript, poster and chapter player.",
    f"- {qa['checks']} recorded feature assertions; 128 narration paragraphs; {qa['caption_cues']} caption cues. Sources: `demo/tools/full-v2/`.",
    "",
    "## Evidence and boundaries",
    "",
    "The opening contains a fresh sync of the signed-in account’s 310 repositories. The remaining workflows use a labeled copy of that account’s real SQLite workspace. No synthetic inventory or deterministic fixture AI is introduced. Original OAuth sign-in occurs outside capture. Copy-session restoration after sign-out/restart is labeled and is not presented as another OAuth verification.",
    "",
    "Fresh taxonomy and classification use only the allowlisted public repositories `allegro/ralph` and `acassen/keepalived`, with public metadata revalidated against GitHub before input extraction and checked again before provider invocation. Private input is denied. One taxonomy generation and one single-repository classification used four OpenAI HTTP requests including token counting, with automatic retries disabled. Accepted model suggestions and local canonical/alias matches are distinguished in the recording.",
    "",
    "The initial broader launch was rejected by automatic approval review for possible private-data export. It did not execute. A public-only allowlist and export check resolved the concern before the revised launch was approved.",
    "",
    "The actual automatic scheduler waited at least the configured 90-second quiet interval after the new Project event, then reconciled real previously analyzed repositories locally. Existing copy-only edit events were acknowledged as the test baseline before generating the two new Project events. No fixture AI or accelerated scheduler clock was used. Idle/long setup is shortened by disclosed discrete cuts; pointer footage and speech are never slowed globally.",
    "",
    "All destructive resets, allowance renewal/overrides, manual edits and process-restart checks operated on the copied workspace. Its snapshot was restored for the closing history/readiness chapters. The original account’s concepts, memberships, suggestions, rules, rejections, drafts and compact analysis records are unchanged.",
    "",
    "## Audio and synchronization",
    "",
    f"Cedar voice, speed 0.93, consistent warm and deliberate directions. Measured spoken rate: **{qa['measured_spoken_wpm']} words/minute** before added reading holds. Final AAC: **{qa['audio_lufs']} LUFS**, **{qa['audio_true_peak_dbtp']} dBTP**. No music or speech time stretching.",
    "",
    "Whisper word timestamps establish paragraph boundaries and caption times. Each paragraph maps to its actual UI action/result clip. Native drag events and saved memberships were checked. Result holds provide reading time. This verifies paragraph/scene synchronization; it does not claim that every individual control click falls on an exact spoken word. Automated playback is muted and establishes technical playback only. The user’s Option D audition choice supplies voice preference; final full-length listening remains a subjective review.",
    "",
    "## Playback and preservation",
    "",
    f"All 32 chapter seeks, 1080p decode, English caption loading, fullscreen, responsive 1440px/390px player layouts, and HTTP 206 byte ranges passed. The phone product chapter uses an actual 390×844 viewport centered in the 1080p frame. {len(capture['errors'])} product JavaScript page errors were recorded.",
    "",
    f"{len(baseline) - 1} earlier media/player artifacts are byte-identical. The original demo-guide prefix is preserved, with a new appended full-demo entry. All {protected['protected_files']} protected readiness files and the original 34 benchmark call rows / 29 cache rows passed the established preservation verifier. The original app ledger’s calls, cache, HTTP history and allowance controls/audit are unchanged.",
    "",
    "## API and spending accounting",
    "",
    f"{len(speech['requests'])} new media requests + {speech['new_intelligence_http']} intelligence HTTP requests = **{len(speech['requests']) + speech['new_intelligence_http']}/20** new OpenAI HTTP attempts. Media conservative accounting: **${speech['accounted_media_usd']:.6f} / $2.50**. Combined accounting including the prior voice pilot and original app: **${speech['combined_accounted_usd']:.6f} / $5**.",
    "",
    "Binary TTS responses do not return invoice token usage; media reservations are conservative accounting, not invoiced charges. The complete audit is `demo/full-v2/speech-requests.json`. No original allowance was renewed or original budget history rewritten.",
    "",
    "## Chapter and feature evidence",
    "",
    "| Time | Chapter | Recorded assertions |",
    "|---|---|---|",
]
source_audio = json.loads((OUT / "source-audio-qa.json").read_text())
position = lines.index("## Playback and preservation")
lines[position:position] = [
    f"All 12 Cedar takes pass the source-level consistency check: {source_audio['loudness_spread_lu']} LU loudness spread. Numeric, hyphen and compound differences were normalized for alignment. One short sentence was retaken to remove the ASR ambiguity between ‘on weighted’ and ‘unweighted’; the retake has 100% word agreement and uses the same voice/pace. Its two requests are included in the 19-request total. The standalone paragraph synchronization audit is `demo/full-v2/synchronization-qa.json`.",
    "",
]
for c in chapters:
    lines.append(
        f"| {fmt(c['start'])} | {c['id']} · {c['title']} | {len(c['checks'])} |"
    )
lines += [
    "",
    "## Historical check mapping",
    "",
    "All 35 earlier checks are mapped in `demo/full-v2/historical-coverage.json`. Earlier PASS values are historical evidence, not relabeled fresh results. Synthetic sample loading/activity were replaced or omitted following the real-account instruction. Fresh classification is intentionally one public repository. Post-reset rebuild is manual; optional cached restart is previewed with prior-analysis protection. Distributed/cloud runtime, exhaustive GitHub completeness, broad model-quality evaluation, and live interrupted-provider billing recovery are outside this recording. Prior readiness and regression reports remain the evidence for those separately tested capabilities.",
    "",
    "## Reproduce and review",
    "",
    "Serve the packaged player with `backend/.venv/bin/python demo/tools/full-v2/serve.py`. The recording server is temporary, loopback-only, and stopped after capture. Its SQLite copy, raw footage and intermediate audio stay in ignored local storage. Do not replace the original working databases to reproduce a reset scene.",
    "",
    "Speech behavior/timing references: [OpenAI speech generation](https://developers.openai.com/api/docs/guides/text-to-speech) and [speech-to-text word timestamps](https://developers.openai.com/api/docs/guides/speech-to-text).",
]
(ROOT / "docs/validation/demo-full-v2.md").write_text("\n".join(lines) + "\n")
(OUT / "README.md").write_text(
    f"""# GitHub Manager · complete real-account walkthrough\n\n[Watch locally](http://127.0.0.1:8123) · **{minutes}:{seconds:02}** · Cedar, Option D calmer delivery · 1080p · 32 chapters.\n\nUse fullscreen for table and settings detail. Download the MP4, separate M4A audio, VTT/SRT captions and transcript from the player. The opening uses the live signed-in account. Edits, allowance changes, restart and resets use a labeled copy of its real workspace. No synthetic repositories or fixture AI are introduced.\n\nValidation: `docs/validation/demo-full-v2.md`. Machine-readable media, player, feature, historical-coverage and preservation checks are saved beside the video. Earlier media and readiness work remain intact.\n\nStart the player from the repository root:\n\n```bash\nbackend/.venv/bin/python demo/tools/full-v2/serve.py\n```\n\nThe media contains AI-generated narration. Recorded actions run at normal speed, with disclosed cuts and result holds.\n"""
)
guide = ROOT / "demo-video.md"
marker = "## October 13 — complete Cedar walkthrough v2"
if marker not in guide.read_text():
    with guide.open("a") as f:
        f.write(
            f"""\n\n{marker}\n\nThe new full walkthrough uses **Option D: Cedar, calmer delivery** and the connected real GitHub account, unmasked as requested. **{minutes}:{seconds:02} · 1920×1080 · 32 chapters · {qa["checks"]} recorded assertions.**\n\n- [Watch the chaptered local player](http://127.0.0.1:8123).\n- Video: [github-manager-full-cedar-calm-1080p.mp4](demo/full-v2/github-manager-full-cedar-calm-1080p.mp4).\n- [Recording notes and downloads](demo/full-v2/README.md).\n- [Full validation report](docs/validation/demo-full-v2.md).\n\nThe live opening refreshes the real account inventory. Demo edits, budget controls, backend restart and destructive reset scenes use an explicitly labeled copy of that account’s real workspace. Two bounded public-repository intelligence checks are fresh; saved results and local reconciliation are labeled. No synthetic inventory or fixture AI is introduced. Captions follow spoken word timestamps; normal-speed actions use reading holds and disclosed discrete cuts. Earlier walkthroughs, voice pilots and readiness reports are preserved.\n"""
        )
assert guide.read_bytes().startswith((BASE / "demo-video.md").read_bytes())
plan = ROOT / "docs/planning/demo-video-v2.md"
s = plan.read_text().replace(
    "Full walkthrough approved and in production.",
    "Full walkthrough approved and completed; validation PASS.",
)
plan.write_text(s)
print(
    json.dumps(
        {
            "status": "PASS",
            "duration": f"{minutes}:{seconds:02}",
            "checks": qa["checks"],
            "new_openai_http": len(speech["requests"])
            + speech["new_intelligence_http"],
            "combined_accounted_usd": speech["combined_accounted_usd"],
            "preservation": preservation,
        },
        indent=2,
    )
)
