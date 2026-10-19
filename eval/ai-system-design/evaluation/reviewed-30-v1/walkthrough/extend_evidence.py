"""Add collection history and concrete validation tables from existing artifacts."""

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PRIVATE = ROOT / "docs/validation/private"
RELEASE = PRIVATE / "corpus-600-v2/release"
EVAL = PRIVATE / "corpus-600-v2/evaluation-reviewed-30-v1"


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    inventory = [json.loads(row) for row in (RELEASE / "inventory.jsonl").read_text().splitlines()]
    original_path = PRIVATE / "corpus-600/release/inventory.jsonl"
    old = [json.loads(row) for row in original_path.read_text().splitlines()]
    original_ids = {int(row["repository_id"]) for row in old}
    references = read(EVAL / "reference-snapshot.json")
    summary, ragas = read(EVAL / "evaluation-summary.json"), read(EVAL / "ragas-results.json")
    collector = read(RELEASE / "collection-ledger-summary.local.json")
    pilot = read(ROOT / "eval/ai-system-design/ground-truth-creation/statistics.json")["frozen_pilot"]
    rows = []
    for domain in sorted({r["sampling_domain"] for r in inventory}):
        records = [r for r in inventory if r["sampling_domain"] == domain]
        retained = sum(int(r["repository_id"]) in original_ids for r in records)
        splits = Counter(r["split"] for r in records)
        rows.append(
            {
                "sampling_area": domain,
                "repositories": len(records),
                "retained_original_ids": retained,
                "replacement_ids": len(records) - retained,
                "development": splits["development"],
                "validation": splits["validation"],
                "test_reserved": splits["test_reserved"],
                "human_reviewed_in_evaluation": sum(
                    r["sampling_domain"] == domain for r in references.values()
                ),
            }
        )
    assert len({int(r["repository_id"]) for r in inventory}) == 600
    assert all(r["repositories"] == 60 for r in rows)
    assert sum(r["retained_original_ids"] for r in rows) == 489
    assert sum(r["replacement_ids"] for r in rows) == 111
    assert all(
        (r["development"], r["validation"], r["test_reserved"]) == (18, 12, 30) for r in rows
    )
    tests = []
    for index, kind in enumerate(("PROJECT", "TOPIC", "TAG", "ALL"), 1):
        metric = ragas["candidate_concept_id_recall"][kind]
        local = summary["overall"][kind]
        tests.append(
            {
                "test": f"R{index}",
                "kind": "CANDIDATE_ID_RECALL",
                "facet": kind,
                "input": "Retrieved concept IDs and human-positive concept IDs, filtered to this facet",
                "repositories_with_positive_reference": metric["cases_with_positive_support"],
                "reference_assignments": local["reviewed_positives"],
                "retrieved_positive_assignments": local["retrieved_positives"],
                "measured_score": metric["micro_candidate_recall"],
                "matches_local_scorer": abs(
                    metric["micro_candidate_recall"]
                    - local["candidate_recall_of_reviewed_positives"]
                )
                < 1e-12,
                "quality_threshold": None,
            }
        )
    observed = read(HERE / "evidence/observed-results.json")
    for index, result in enumerate(observed["grounding_judge_results"], 5):
        tests.append(
            {
                "test": f"R{index}",
                "kind": "FAITHFULNESS",
                "repository": result["repository"],
                "input": "Claims derived from saved assignments plus the actual repository evidence supplied to the producer",
                "claims_judged": result["claims_judged"],
                "claims_supported": result["claims_supported"],
                "measured_score": result["score"],
                "generation_calls_in_original_run": 2,
                "quality_threshold": None,
                "status": "MEASURED_NOT_A_QUALITY_PASS",
            }
        )
    stub = (HERE / "evidence/ragas-stub-check.txt").read_text()
    assert "exact two-call fanout PASS; no network" in stub
    tests.append(
        {
            "test": "R8",
            "kind": "CONTROLLED_NO_NETWORK_FANOUT",
            "input": "Fixed repository-provides-testing claim, matching context and predetermined schema replies",
            "expected_mock_generations": 2,
            "observed_mock_generations": 2,
            "score": 1.0,
            "network_calls": 0,
            "status": "PASS",
            "execution_log": "ragas-stub-check.txt",
        }
    )
    sources = [
        ROOT / "eval/ai-system-design/evaluation/corpus-600/README.md",
        ROOT / "docs/validation/corpus-600-v2-review-2026-10-17.md",
        ROOT / "eval/ai-system-design/ground-truth-creation/statistics.json",
        RELEASE / "inventory.jsonl",
        original_path,
        RELEASE / "splits.provisional.json",
        RELEASE / "collection-ledger-summary.local.json",
        EVAL / "ragas-results.json",
        EVAL / "evaluation-summary.json",
        HERE / "evidence/ragas-stub-check.txt",
    ]
    data = {
        "client_date": "2026-10-19",
        "scope": "Revision 2 explanation of existing collection and evaluation evidence; no new GitHub crawl or classification/judge requests.",
        "source_sha256": {str(p.relative_to(ROOT)): sha(p) for p in sources},
        "collection": {
            "repositories": 600,
            "sampling_areas": 10,
            "per_area": rows,
            "retained_original_ids": 489,
            "replacements": 111,
            "original_active_exclusions": {
                "non_english_primary_narrative": 77,
                "inadequate_or_off_domain_evidence": 18,
                "valid_balancing_reserve": 16,
            },
            "retained_bucket_reassignments": 2,
            "original_collection_requests_reported": {"http": 5391, "searches_included": 181},
            "refresh_collection_requests": {
                "http": collector["http_attempts"],
                "searches_included": collector["search_attempts"],
            },
            "readme_snapshots": 600,
            "supporting_files": 1223,
            "active_source_bytes": 18436109,
            "recorded_curation_semantic_read_scope": {
                "complete_readmes": 88,
                "targeted_or_partial_readmes": 512,
            },
            "limits": "Balanced purposive collection, not random GitHub sample or six hundred human-approved references. Counts refer to saved snapshots.",
        },
        "initial_annotation_pilot": {
            k: pilot[k]
            for k in (
                "repositories",
                "independent_passes",
                "annotations",
                "sampling_counts",
                "exact_set_agreement_by_kind",
                "label_set_agreement_repositories",
                "shared_positive_pairs",
                "a_only_pairs",
                "b_only_pairs",
            )
        },
        "internal_performance": {
            k: summary[k] for k in ("overall", "splits", "domains", "paired_comparison")
        },
        "ragas_tests": tests,
        "ragas_distinct_repositories": 30,
        "ragas_deterministic_facet_and_all_metric_evaluations": sum(
            t["repositories_with_positive_reference"] for t in tests[:4]
        ),
        "ragas_semantic_sample_repositories": 3,
        "limits": "Reference unknowns remain unknown. R1-R4 are overlapping metric views; R5-R7 are judge measurements without semantic pass thresholds; R8 is a controlled integration check.",
    }
    target = HERE / "evidence/collection-and-validation-details.json"
    target.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    with (HERE / "evidence/collection-by-area.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(
        json.dumps(
            {
                "areas": len(rows),
                "repositories": 600,
                "retained": 489,
                "replacements": 111,
                "ragas_named_checks": len(tests),
                "new_classification_or_judge_generations": 0,
            }
        )
    )


if __name__ == "__main__":
    main()
