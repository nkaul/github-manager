"""Verify this publication locally without network calls or application writes."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import re
import struct
import zipfile
from pathlib import Path
from urllib.parse import unquote

from refresh_statistics import collect

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "eval/relocation"))
from relocation_support import historical_bytes, historical_sha256, repo_path
PACKAGE = ROOT / "eval/ai-system-design/ground-truth-creation"


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=PACKAGE / "verification.json")
    parser.add_argument(
        "--check-live",
        action="store_true",
        help="Also compare snapshot review counts with current read-only SQLite aggregates.",
    )
    args = parser.parse_args()
    statistics = read(PACKAGE / "statistics.json")
    fresh = collect()
    article = (PACKAGE / "article.md").read_text()
    appendix = (PACKAGE / "validation-evidence.md").read_text()
    overview = (PACKAGE / "README.md").read_text()
    editorial = (PACKAGE / "editorial-and-claim-review.md").read_text()
    missing = []
    link_count = 0
    for md in PACKAGE.rglob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", md.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            target = unquote(target.split("#")[0])
            path = Path(target) if target.startswith("/") else md.parent / target
            link_count += 1
            if not path.exists():
                missing.append({"file": str(md.relative_to(ROOT)), "target": target})
    words = {
        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
    }

    def number(value):
        return int(value) if value.isdigit() else words[value.lower()]

    live = statistics["live_human_review"]
    prose = re.search(
        r"\*\*(\w+) human-confirmed corpus records and (\w+) incomplete drafts\*\*",
        article,
    )
    pilot_prose = re.search(
        r"\*\*(\d+) of (\d+) pilot cases and (\d+) of the initial (\d+) queue cases are human-confirmed",
        article,
    )
    appendix_human = re.search(
        r"(\w+) real corpus records are human-confirmed", appendix
    )
    appendix_pilot = re.search(
        r"Pilot human confirmations are \*\*(\d+)/(\d+)\*\*, including \*\*(\d+)/(\d+)\*\*",
        appendix,
    )
    overview_human = re.search(
        r"(\w+) real corpus confirmations, including (\w+) within the (\d+)-case pilot and initial (\d+)-case queue",
        overview,
    )
    editorial_human = re.search(
        r"\| (\d+) human confirmations, (\d+) drafts; (\d+) in pilot/initial queue; none pilot-bound \|",
        editorial,
    )
    figures = []
    figure_checks = []
    for row in read(PACKAGE / "figures/prompts.json")["figures"]:
        image = PACKAGE / "figures" / row["file"]
        width, height = struct.unpack(">II", image.read_bytes()[16:24])
        figure_checks.append(
            digest(image) == row["sha256"]
            and width == row["width"]
            and height == row["height"]
        )
        if row["file"] != "03-human-review-and-audit.png":
            figures.append(
                {
                    "path": "figures/" + row["file"],
                    "width": width,
                    "height": height,
                    "sha256": digest(image),
                }
            )
    preservation = read(PACKAGE / "history/revision-01-preservation.json")
    archive = PACKAGE / "history" / preservation["archive"]
    with zipfile.ZipFile(archive) as old:
        archived_intact = all(
            hashlib.sha256(old.read(row["path"])).hexdigest() == row["sha256"]
            for row in preservation["files"]
        )
    example = read(PACKAGE / "worked-example.json")
    packet = read(
        ROOT
        / "docs/validation/private/corpus-600-v2/annotation-pilot/packets/639807859.json"
    )
    excerpt = example["article_excerpt"]
    source_text = next(
        source["text"]
        for source in packet["sources"]
        if source["path"] == excerpt["path"]
    )
    with zipfile.ZipFile(archive) as old:
        old_verification = json.loads(old.read("verification.json"))
    prior_figures = {
        row["path"]: row["sha256"]
        for row in old_verification["actual_article_illustrations"]
    }
    observed = read(
        ROOT / "docs/validation/private/corpus-600-v2/annotation-pilot/review.json"
    )["records"][str(example["repository_id"])]
    expected_sets = {
        "shared_labels": observed["comparison"]["agreed_ids"],
        "a_only_labels": observed["comparison"]["a_only_ids"],
        "b_only_labels": observed["comparison"]["b_only_ids"],
    }
    expected_pilot_counts = [
        live["pilot_human_confirmed"],
        statistics["frozen_pilot"]["repositories"],
        live["initial_queue_human_confirmed"],
        sum(statistics["frozen_pilot"]["human_queue"].values()),
    ]
    packet_sources = {source["path"]: source for source in packet["sources"]}
    checks = {
        "relative_links_exist": not missing,
        "corpus_inventory_registry_and_splits_recount": statistics["corpus"]
        == fresh["corpus"],
        "frozen_annotation_agreement_and_coverage_recount": statistics["frozen_pilot"]
        == fresh["frozen_pilot"],
        "dated_qa_counts_match_evidence_report": statistics[
            "reported_software_validation"
        ]
        == fresh["reported_software_validation"],
        "all_snapshot_evidence_hashes_match": all(
            historical_sha256(repo_path(row["path"])) == row["sha256"]
            for row in statistics["evidence_files"]
        ),
        "article_human_counts_match_snapshot": bool(prose)
        and number(prose[1]) == live["human_confirmed"]
        and number(prose[2]) == live["incomplete_drafts"],
        "article_pilot_queue_counts_match_snapshot": bool(pilot_prose)
        and [int(pilot_prose[i]) for i in range(1, 5)] == expected_pilot_counts,
        "appendix_human_and_pilot_counts_match_snapshot": bool(appendix_human)
        and number(appendix_human[1]) == live["human_confirmed"]
        and bool(appendix_pilot)
        and [int(appendix_pilot[i]) for i in range(1, 5)] == expected_pilot_counts,
        "overview_human_and_pilot_counts_match_snapshot": bool(overview_human)
        and [
            number(overview_human[1]),
            number(overview_human[2]),
            int(overview_human[3]),
            int(overview_human[4]),
        ]
        == [
            live["human_confirmed"],
            live["pilot_human_confirmed"],
            expected_pilot_counts[1],
            expected_pilot_counts[3],
        ],
        "editorial_human_and_pilot_counts_match_snapshot": bool(editorial_human)
        and [int(editorial_human[i]) for i in range(1, 4)]
        == [
            live["human_confirmed"],
            live["incomplete_drafts"],
            live["pilot_human_confirmed"],
        ]
        and live["human_confirmed_with_pilot_binding"] == 0,
        "article_current_coverage_boundary": "570 repositories have original corpus proposals, but no independent A/B annotation"
        in article,
        "article_positive_only_reference_caveat": "does **not** record an explicit negative/unknown judgment"
        in article,
        "all_preserved_figure_hashes_and_dimensions_match": all(figure_checks),
        "active_figures_unchanged_from_prior_revision": all(
            prior_figures[row["path"]] == row["sha256"] for row in figures
        ),
        "prior_package_archive_hash_and_members_intact": digest(archive)
        == preservation["archive_sha256"]
        and archived_intact,
        "worked_example_matches_commit_and_proposals": example["commit"]
        == packet["commit"]
        and all(
            {label["id"] for label in example[key]} == set(ids)
            for key, ids in expected_sets.items()
        ),
        "worked_example_source_bindings_match_packet": all(
            row["path"] in packet_sources
            and all(
                row[field] == packet_sources[row["path"]][field]
                for field in ("sha256", "bytes", "role")
            )
            for row in example["source_bindings"]
        ),
        "worked_example_short_quote_is_exact": excerpt["quote"] in source_text
        and len(excerpt["quote"].split()) <= 25,
    }
    if args.check_live:
        checks["current_read_only_human_aggregate_matches_snapshot"] = (
            live == fresh["live_human_review"]
        )
    result = {
        "client_date": statistics["client_date"],
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checked_relative_links": link_count,
        "missing_links": missing,
        "checks": checks,
        "actual_article_illustrations": figures,
        "word_count": len(article.split()),
        "validation_appendix_word_count": len(
            (PACKAGE / "validation-evidence.md").read_text().split()
        ),
        "live_review_snapshot_checked": args.check_live,
        "statistics_snapshot_captured_at_utc": statistics["captured_at_utc"],
        "verified_document_sha256": {
            name: digest(PACKAGE / name)
            for name in (
                "article.md",
                "validation-evidence.md",
                "README.md",
                "editorial-and-claim-review.md",
                "statistics.json",
                "worked-example.json",
            )
        },
        "reproduction": "python3 eval/ai-system-design/ground-truth-creation/scripts/verify_package.py"
        + (" --check-live" if args.check_live else ""),
        "scope": "Publication static/source/count verification only; existing dated application tests were not rerun. Read-only corpus/pilot/SQLite access, no network/model calls or live state writes. Prior four built-in image-generation calls are preserved history; no images generated for this revision.",
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                key: result[key]
                for key in (
                    "status",
                    "checked_relative_links",
                    "missing_links",
                    "checks",
                    "word_count",
                    "validation_appendix_word_count",
                )
            },
            indent=2,
        )
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
