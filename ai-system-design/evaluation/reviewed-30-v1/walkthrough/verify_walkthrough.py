"""Check the explanation against saved evidence; read-only, no provider imports."""

import hashlib
import json
import re
import sqlite3
import struct
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PACKAGE = HERE.parent
DATA = ROOT / "docs/validation/private/corpus-600-v2/evaluation-reviewed-30-v1"


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def slug(value):
    value = re.sub(r"[^\w\s-]", "", value.casefold())
    return re.sub(r"\s", "-", value)


def main():
    evidence = read(HERE / "evidence/observed-results.json")
    article_path = PACKAGE / "ground-truth-evaluation-explained.md"
    article = article_path.read_text()
    missing = []
    checked_links = 0
    for md in (
        article_path,
        HERE / "evidence/repository-results.md",
        PACKAGE / "README.md",
        HERE / "editorial-review.md",
    ):
        anchors = {slug(h) for h in re.findall(r"^#{1,6} (.+)$", md.read_text(), re.M)}
        for target in re.findall(r"\]\(([^)]+)\)", md.read_text()):
            if "://" in target:
                continue
            checked_links += 1
            if target.startswith("#"):
                if target[1:] not in anchors:
                    missing.append({"file": md.name, "anchor": target})
            else:
                resolved = (md.parent / unquote(target.split("#")[0])).resolve()
                # This invocation creates its own linked receipt after checking inputs.
                if (
                    resolved != (HERE / "evidence/verification.json").resolve()
                    and not resolved.exists()
                ):
                    missing.append({"file": md.name, "target": target})
    source_changes = [
        name
        for name, expected in evidence["source_evidence_sha256"].items()
        if sha(DATA / name) != expected
    ]
    frozen = read(DATA / "manifest.json")
    frozen_changes = [
        name for name, expected in frozen["files"].items() if sha(DATA / name) != expected
    ] + [
        name for name, expected in frozen["producer_files"].items() if sha(ROOT / name) != expected
    ]
    runs = evidence["primary_replay_results"]
    judged = evidence["grounding_judge_results"]
    figures = read(HERE / "figures/manifest.json")["figures"]
    image_checks = []
    for row in figures:
        for export in row["files"]:
            path = HERE / export["path"]
            correct = sha(path) == export["sha256"]
            if path.suffix == ".png":
                width, height = struct.unpack(">II", path.read_bytes()[16:24])
                correct = correct and width >= 1920 and height >= 900
            image_checks.append(correct)
    dbpath = ROOT / "docs/validation/private/ai-pretest/runs.sqlite3"
    with sqlite3.connect(f"{dbpath.as_uri()}?mode=ro", uri=True) as db:
        grant = db.execute(
            "SELECT state,generation_used,http_used FROM app_run_budgets WHERE id=?",
            (read(DATA / "config.json")["run_id"],),
        ).fetchone()
    with sqlite3.connect(
        f"{(DATA / 'evaluation-control.sqlite3').as_uri()}?mode=ro", uri=True
    ) as db:
        attempts = db.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]
        generations = db.execute(
            "SELECT COUNT(*) FROM attempts WHERE endpoint='/v1/responses'"
        ).fetchone()[0]
    software_log = (HERE / "evidence/software-checks.txt").read_text()
    stub_log = (HERE / "evidence/ragas-stub-check.txt").read_text()
    checks = {
        "all_local_links_and_section_anchors_exist": not missing,
        "prior_evaluation_result_files_unchanged": not source_changes,
        "frozen_input_and_producer_hashes_match": not frozen_changes,
        "thirty_unique_public_repository_results": len(runs) == 30
        and len({r["repository_id"] for r in runs}) == 30,
        "label_counts_match_headline": [
            sum(r[k] for r in runs)
            for k in (
                "reviewed_positive_labels",
                "positive_labels_retrieved",
                "positive_labels_selected",
                "unjudged_predictions",
            )
        ]
        == [83, 69, 66, 16],
        "all_thirty_promptfoo_contract_results_pass": all(r["contract_pass"] for r in runs),
        "each_reported_case_recall_is_reproducible": all(
            abs(
                r["reviewed_positive_recall"]
                - r["positive_labels_selected"] / r["reviewed_positive_labels"]
            )
            < 1e-12
            for r in runs
        ),
        "promptfoo_replay_has_zero_model_tokens_and_cost": all(
            r["replay_model_tokens"] == 0 and r["replay_cost_usd"] == 0 for r in runs
        ),
        "grounding_has_three_cases_nine_claims_eight_supported": len(judged) == 3
        and sum(r["claims_judged"] for r in judged) == 9
        and sum(r["claims_supported"] for r in judged) == 8,
        "grounding_scores_match_recorded_verdicts": all(
            abs(r["score"] - r["claims_supported"] / r["claims_judged"]) < 1e-12 for r in judged
        ),
        "nine_png_and_svg_pairs_match_export_manifest": len(figures) == 9
        and len(image_checks) == 18
        and all(image_checks),
        "four_software_tests_passed_in_saved_execution": "4 passed" in software_log
        and "FAILED" not in software_log,
        "ragas_no_network_two_call_check_passed": "exact two-call fanout PASS; no network"
        in stub_log,
        "original_grant_remains_finished_at_fifty_generations_and_one_hundred_http": grant
        == ("FINISHED", 50, 100)
        and (generations, attempts) == (50, 100),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "client_date": "2026-10-19",
        "verified_at_utc": datetime.now(UTC).isoformat(),
        "checks": checks,
        "checked_local_links": checked_links,
        "missing_links": missing,
        "changed_source_result_files": source_changes,
        "changed_frozen_inputs_or_producer_files": frozen_changes,
        "article_words": len(article.split()),
        "article_sha256": sha(article_path),
        "observed_evidence_sha256": sha(HERE / "evidence/observed-results.json"),
        "new_model_generations_for_walkthrough": 0,
        "visual_review": "Nine exported PNG figures inspected by the authoring agent for clipping, labels, legends and readable counts; not an independent reader study.",
        "scope": "Explanation arithmetic/source/link/image/guard checks. Software tests use temporary data. No new live predictions or semantic quality passes are implied.",
    }
    (HERE / "evidence/verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
