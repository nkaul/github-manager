"""Read-only aggregate snapshot. Never changes corpus, pilot or application state."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[4]
PACKAGE = ROOT / "eval/ai-system-design/ground-truth-creation"
DATA = ROOT / "docs/validation/private/corpus-600-v2"


def read(path: Path):
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect() -> dict:
    pilot = DATA / "annotation-pilot"
    release = DATA / "release"
    comparison = read(pilot / "comparison-report.json")
    review = read(pilot / "review.json")
    selection = read(pilot / "selection.json")
    registry = read(release / "registry.proposed.json")
    inventory = [
        json.loads(line)
        for line in (release / "inventory.jsonl").read_text().splitlines()
        if line
    ]
    release_manifest = read(release / "manifest.local.json")
    queue_ids = {
        str(r["repository_id"])
        for r in read(pilot / "human-review-queue.json")["records"]
    }
    pilot_ids = set(review["records"])
    counts = {
        "saved_records": 0,
        "statuses": Counter(),
        "human_confirmed": 0,
        "pilot_human_confirmed": 0,
        "initial_queue_human_confirmed": 0,
        "human_confirmed_with_pilot_binding": 0,
        "incomplete_drafts": 0,
    }
    # Aggregate only. No actor, workspace identity, review text or repository-level
    # human decisions are exported into this publication package.
    database = ROOT / "docs/validation/private/demo/app.sqlite3"
    con = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        for (serialized,) in con.execute("SELECT state FROM workspace"):
            state = json.loads(serialized)
            for rows in state.get("reference_reviews", {}).values():
                for rid, record in rows.items():
                    if record.get("release_id") != comparison["release_id"]:
                        continue
                    counts["saved_records"] += 1
                    status = record.get("status", "UNKNOWN")
                    counts["statuses"][status] += 1
                    if status == "HUMAN_CONFIRMED":
                        counts["human_confirmed"] += 1
                        counts["pilot_human_confirmed"] += int(str(rid) in pilot_ids)
                        counts["initial_queue_human_confirmed"] += int(
                            str(rid) in queue_ids
                        )
                        counts["human_confirmed_with_pilot_binding"] += int(
                            bool(record.get("annotation_pilot_sha256"))
                        )
            counts["incomplete_drafts"] += len(
                state.get("reference_drafts", {}).get(comparison["release_id"], {})
            )
    finally:
        con.close()
    counts["statuses"] = dict(counts["statuses"])
    label_counts = {a: Counter() for a in ("a", "b")}
    scope_counts = {a: Counter() for a in ("a", "b")}
    agreement = Counter()
    agreement_details = {kind: Counter() for kind in ("PROJECT", "TOPIC", "TAG")}
    reading = {a: Counter() for a in ("a", "b")}
    shared = only_a = only_b = 0
    for record in review["records"].values():
        for a in ("a", "b"):
            ann = record["annotations"][a]
            label_counts[a].update(registry[cid]["kind"] for cid in ann["positive_ids"])
            scope_counts[a].update([ann["group_scope"]["projects"]["status"]])
            reading[a]["supplied"] += len(ann["source_reading"])
            reading[a]["complete"] += sum(
                bool(s["complete"]) for s in ann["source_reading"]
            )
        for kind in ("PROJECT", "TOPIC", "TAG"):
            a_ids = {
                i
                for i in record["annotations"]["a"]["positive_ids"]
                if registry[i]["kind"] == kind
            }
            b_ids = {
                i
                for i in record["annotations"]["b"]["positive_ids"]
                if registry[i]["kind"] == kind
            }
            agreement[kind] += int(a_ids == b_ids)
            agreement_details[kind]["both_empty"] += int(not a_ids and not b_ids)
            agreement_details[kind]["exact_nonempty"] += int(
                bool(a_ids) and a_ids == b_ids
            )
            agreement_details[kind]["shared_positive_pairs"] += len(a_ids & b_ids)
            agreement_details[kind]["union_positive_pairs"] += len(a_ids | b_ids)
        shared += len(record["comparison"]["agreed_ids"])
        only_a += len(record["comparison"]["a_only_ids"])
        only_b += len(record["comparison"]["b_only_ids"])
    source_counts = Counter(
        s["role"] for row in selection["repositories"] for s in row["sources"]
    )
    public_sources = [
        ROOT / "docs/validation/corpus-600-v2-review-2026-10-17.md",
        ROOT / "docs/validation/agent-annotation-pilot-2026-10-17.md",
        ROOT / "eval/ai-system-design/evaluation/annotation-pilot/README.md",
        ROOT / "docs/planning/corpus-review-workflow-api.md",
        ROOT / "docs/validation/ground-truth-agent-inputs-2026-10-18.md",
        ROOT / "docs/validation/session-sync-recovery-2026-10-18.md",
        ROOT / "docs/validation/live-workspace-redesign-2026-10-17.md",
    ]
    frozen_sources = [
        release / "manifest.local.json",
        release / "registry.proposed.json",
        release / "inventory.jsonl",
        release / "splits.provisional.json",
        pilot / "selection.json",
        pilot / "review.json",
        pilot / "comparison-report.json",
        pilot / "human-review-queue.json",
        pilot / "manifest.json",
    ]
    latest_report = ROOT / "docs/validation/ground-truth-agent-inputs-2026-10-18.md"
    latest_text = latest_report.read_text()
    backend = re.search(r"\*\*(\d+) backend checks passed\*\*", latest_text)
    browser = re.search(
        r"\*\*All (\d+) Ground Truth browser workflows passed\*\*", latest_text
    )
    protected = re.search(r"All \*\*(\d+) protected", latest_text)
    if not all((backend, browser, protected)):
        raise ValueError(
            "Latest reported software validation counts require review; expected evidence wording changed."
        )
    return {
        "schema_version": "1.1",
        "client_date": datetime.now(ZoneInfo("America/New_York")).date().isoformat(),
        "captured_at_utc": datetime.now(UTC).isoformat(),
        "status": "LIVING_PUBLICATION_DRAFT_HUMAN_REVIEW_IN_PROGRESS",
        "release_id": comparison["release_id"],
        "release_manifest_sha256": comparison["manifest_sha256"],
        "selection_sha256": comparison["selection_sha256"],
        "corpus": {
            "repositories": len(inventory),
            "sampling_counts": dict(
                Counter(row["sampling_domain"] for row in inventory)
            ),
            "readme_snapshots": release_manifest["readmes"],
            "supporting_files": sum(row["supporting_files"] for row in inventory),
            "registry_by_kind": dict(Counter(c["kind"] for c in registry.values())),
            "split_actual": read(release / "splits.provisional.json")["actual"],
            "manifest_checks": release_manifest["checks"],
            "historical_release_report": {
                "sampling_domains": 10,
                "per_domain": 60,
                "readme_snapshots": 600,
                "supporting_files": 1223,
                "source_bytes": 18436109,
                "retained_original": 489,
                "replacements": 111,
                "complete_readme_semantic_reads": 88,
                "targeted_partial_readme_reads": 512,
                "curation_peer_audits": 120,
                "supported_project_repositories": 308,
            },
        },
        "frozen_pilot": {
            **comparison["summary"],
            "provenance": comparison["provenance"],
            "positive_decisions_by_kind": {a: dict(c) for a, c in label_counts.items()},
            "shared_positive_pairs": shared,
            "a_only_pairs": only_a,
            "b_only_pairs": only_b,
            "exact_set_agreement_by_kind": dict(agreement),
            "agreement_details_by_kind": {
                kind: dict(value) for kind, value in agreement_details.items()
            },
            "reading_channels": {a: dict(c) for a, c in reading.items()},
            "supplied_scope_by_repository": {
                a: dict(c) for a, c in scope_counts.items()
            },
            "source_channels_by_role": dict(source_counts),
            "source_channel_bytes": sum(
                s["bytes"] for row in selection["repositories"] for s in row["sources"]
            ),
            "sampling_counts": selection["counts"],
            "limits": "Agreement is not accuracy; frozen human_confirmed is historical, not live progress.",
        },
        "live_human_review": {
            **counts,
            "scope": "Aggregate current owner-scoped records for this release; record count is not a deduplicated multi-reviewer consensus gold count.",
            "privacy": "Counts only; no actors, identities or review text exported.",
        },
        "reported_software_validation": {
            "source": str(latest_report.relative_to(ROOT)),
            "client_date": "2026-10-18",
            "backend_checks_passed": int(backend.group(1)),
            "isolated_ground_truth_suite_checks_passed": int(browser.group(1)),
            "protected_artifacts_unchanged": int(protected.group(1)),
            "ground_truth_test_ports": [3015, 8015],
            "scope": "Dated reported run, not rerun by this statistics updater; suite includes a deterministic palette test as well as browser journeys. These checks are not human-label accuracy.",
            "counts_not_cumulative": True,
        },
        "evidence_files": [
            {
                "path": str(p.relative_to(ROOT)),
                "sha256": sha(p),
                "publicly_versioned": p in public_sources,
            }
            for p in public_sources + frozen_sources
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Write a NEW dated snapshot; existing files are never overwritten.",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(PACKAGE.resolve()):
        raise SystemExit("Output must remain inside this publication package.")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as stream:
        json.dump(collect(), stream, indent=2)
        stream.write("\n")
    print(f"Saved aggregate snapshot: {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
