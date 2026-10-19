"""Check the explanation against saved evidence; read-only, no provider imports."""

import argparse
import hashlib
import json
import sys
import re
import sqlite3
import struct
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "eval/relocation"))
from relocation_support import historical_bytes, historical_sha256, repo_path
PACKAGE = HERE.parent
DATA = ROOT / "docs/validation/private/corpus-600-v2/evaluation-reviewed-30-v1"


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def slug(value):
    value = re.sub(r"[^\w\s-]", "", value.casefold())
    return re.sub(r"\s", "-", value)


def tables(text):
    found, rows = [], []
    for line in [*text.splitlines(), ""]:
        if line.startswith("|"):
            if re.fullmatch(r"[| :\-]+", line):
                continue
            rows.append([cell.strip().replace("**", "") for cell in line.strip("|").split("|")])
        elif rows:
            found.append(rows)
            rows = []
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "evidence/verification.json")
    args = parser.parse_args()
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
        PACKAGE / "public-illustrations/README.md",
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
        name for name, expected in frozen["producer_files"].items() if sha(repo_path(name)) != expected
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
    details = read(HERE / "evidence/collection-and-validation-details.json")
    collection_sources_match = all(
        historical_sha256(repo_path(name)) == expected for name, expected in details["source_sha256"].items()
    )
    collection_rows = details["collection"]["per_area"]
    source_summary = read(DATA / "evaluation-summary.json")
    article_tables = tables(article)
    areas = {r["sampling_area"]: r for r in collection_rows}
    aliases = {
        "AI": "ai",
        "Cloud": "cloud",
        "Commerce": "commerce",
        "Data": "data",
        "Developer tools": "developer",
        "Education": "education",
        "Finance": "finance",
        "Healthcare": "healthcare",
        "Science": "science",
        "Security": "security",
    }
    acquisition_table = next(t for t in article_tables if t[0][:2] == ["Area", "Retained from v1"])
    acquisition_matches = len(acquisition_table) == 12 and all(
        list(map(int, row[1:]))
        == [
            areas[aliases[row[0]]][field]
            for field in (
                "retained_original_ids",
                "replacement_ids",
                "development",
                "validation",
                "test_reserved",
            )
        ]
        for row in acquisition_table[1:-1]
    )
    facet_table = next(t for t in article_tables if t[0][:2] == ["Kind", "Confirmed targets"])
    kind_ids = {"Project": "PROJECT", "Topic": "TOPIC", "Tag": "TAG", "All": "ALL"}
    facet_matches = True
    for row in facet_table[1:]:
        metric = source_summary["overall"][kind_ids[row[0]]]
        expected = [
            str(metric[k])
            for k in ("reviewed_positives", "retrieved_positives", "selected_positives")
        ]
        expected += [
            f"{metric['candidate_recall_of_reviewed_positives']:.1%}",
            f"{metric['prediction_recall_of_reviewed_positives']:.1%}",
            str(metric["unjudged_predictions"]),
        ]
        facet_matches = facet_matches and row[1:] == expected
    split_table = next(t for t in article_tables if t[0][:2] == ["Split", "Kind"])
    split_matches = len(split_table) == 7
    for row in split_table[1:]:
        metric = source_summary["splits"][
            "development" if row[0] == "Development" else "test_reserved"
        ][kind_ids[row[1]]]
        expected = [
            str(metric[k])
            for k in ("reviewed_positives", "retrieved_positives", "selected_positives")
        ]
        expected += [
            f"{metric['prediction_recall_of_reviewed_positives']:.1%}",
            str(metric["unjudged_predictions"]),
        ]
        split_matches = split_matches and row[2:] == expected
    test_inventory = next(t for t in article_tables if t[0][:2] == ["Test", "What we supplied"])
    public_manifest = read(PACKAGE / "public-illustrations/manifest.json")
    public_images_match = len(public_manifest["selected_figures"]) == 3 and all(
        sha(PACKAGE / "public-illustrations" / r["file"]) == r["sha256"]
        and struct.unpack(">II", (PACKAGE / "public-illustrations" / r["file"]).read_bytes()[16:24])
        == (r["width"], r["height"])
        for r in public_manifest["selected_figures"]
    )
    history = read(PACKAGE / "history/plain-language-evaluation-v1-preservation.json")
    archived = PACKAGE / "history" / history["archive"]
    with zipfile.ZipFile(archived) as old:
        history_matches = sha(archived) == history["sha256"] and all(
            hashlib.sha256(old.read(r["path"])).hexdigest() == r["sha256"] for r in history["files"]
        )
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
        "collection_source_fingerprints_match": collection_sources_match,
        "ten_areas_each_sixty_and_489_retained_111_replacements": len(collection_rows) == 10
        and all(r["repositories"] == 60 for r in collection_rows)
        and sum(r["retained_original_ids"] for r in collection_rows) == 489
        and sum(r["replacement_ids"] for r in collection_rows) == 111,
        "printed_acquisition_and_split_table_matches_inventory": acquisition_matches,
        "printed_internal_facet_performance_table_matches_results": facet_matches,
        "printed_internal_split_facet_table_matches_results": split_matches,
        "eight_named_ragas_checks_match_saved_test_inventory": len(test_inventory) == 9
        and [r[0].split(" · ")[0] for r in test_inventory[1:]]
        == [r["test"] for r in details["ragas_tests"]],
        "three_selected_public_illustrations_match_manifest": public_images_match,
        "previous_guide_and_chart_archive_intact": history_matches,
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
        "new_application_classification_or_judge_api_generations": 0,
        "builtin_illustration_generation_calls_this_revision": public_manifest[
            "builtin_image_generation_calls"
        ],
        "visual_review": "Nine quantitative PNG figures and three selected illustrated explainers inspected by the authoring agent. One generated draft was corrected to clarify scoring-only use of human labels and additive extras. Not an independent reader study.",
        "scope": "Explanation arithmetic/source/link/image/guard checks. Software tests use temporary data. No new live predictions or semantic quality passes are implied.",
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
