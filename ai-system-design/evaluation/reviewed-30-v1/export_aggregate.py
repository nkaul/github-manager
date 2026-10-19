"""Export aggregate publication evidence, excluding individual owner references."""

import json
import shutil

from runner import HERE, OUT, ROOT, read, source_hash, verify  # isort: skip


def main():
    verify()
    summary = read(OUT / "evaluation-summary.json")
    checks = read(OUT / "final-checks.json")
    assert checks["status"] == "PASS"
    assert read(OUT / "preservation-check.json")["status"] == "PASS"
    assert summary["budgets"]["run_grant"]["state"] == "FINISHED"
    ragas = summary["frameworks"]["ragas"]
    export = {
        "client_date": "2026-10-19",
        "status": "COMPLETED_WITH_REFERENCE_LIMITATIONS",
        "captured_at_utc": summary["captured_at_utc"],
        "reference": {
            "repositories": 30, "review_owners": 1, "positives": 83,
            "registry_concepts": 339, "leakage_groups": 18,
            "unselected_labels": "UNKNOWN_NOT_NEGATIVE",
        },
        "overall": summary["overall"], "splits": summary["splits"],
        "domains": summary["domains"], "paired_comparison": summary["paired_comparison"],
        "bootstrap": summary["bootstrap_reviewed_positive_recall"],
        "budgets": summary["budgets"],
        "local_retrieval": read(OUT / "local-results.json"),
        "exploratory_retrieval": read(OUT / "retrieval-representation-diagnostics.json"),
        "quote_visibility_aggregate": read(OUT / "quote-visibility.json")["counts"],
        "corpus_operations": {
            key: read(OUT / "corpus-diagnostics.json")[key]
            for key in ("seconds", "counts", "human_accuracy_claim")
        },
        "frameworks": {
            "promptfoo_version": "0.124.1", "saved_output_replays": checks["promptfoo_replays"],
            "promptfoo_contract_successes": checks["promptfoo_contract_successes"],
            "promptfoo_scores_match_local": checks["promptfoo_per_case_scores_match_local"],
            "ragas_version": ragas["ragas_version"],
            "ragas_candidate_id_metrics_match_local": checks["ragas_candidate_id_metrics_match_local"],
            "faithfulness_case_scores": [r["value"] for r in ragas["faithfulness"]],
            "faithfulness_macro_mean": sum(r["value"] for r in ragas["faithfulness"]) / len(ragas["faithfulness"]),
            "limits": "Contract pass is not semantic accuracy. Candidate-ID recall is not passage recall. Three grounding cases do not calibrate a judge.",
        },
        "taxonomy": checks["taxonomy"], "latencies": checks["latencies"],
        "task_usage": checks["task_usage"], "cache_usage": checks["cache_and_reasoning_usage"],
        "adapter_rejected_attempts": summary["adapter_failures_retained"],
        "exceptions_repositories": summary["exceptions_repositories"],
        "preservation": read(OUT / "preservation-check.json"),
        "private_evidence_sha256": {
            name: source_hash(OUT / name) for name in (
                "manifest.json", "test-freeze.json", "evaluation-summary.json", "final-checks.json",
                "predictions.json", "promptfoo-results.json", "ragas-results.json", "preservation-check.json",
            )
        },
        "limits": "Selected single-reviewer partial-positive references. Unknown predictions are not false positives; exhaustive precision/F1 remain unavailable. No owner identity, individual review, raw prediction, full source or credential is exported here.",
    }
    path = ROOT / "ai-system-design/ground-truth-creation/evaluation-statistics-2026-10-19.json"
    path.write_text(json.dumps(export, indent=2, allow_nan=False) + "\n")
    framework_dir = HERE / "frameworks"
    framework_dir.mkdir(exist_ok=True)
    for name in ("package.json", "package-lock.json"):
        shutil.copyfile(ROOT / ".tools/evaluation-promptfoo" / name, framework_dir / name)
    print("Exported aggregate statistics and exact Promptfoo dependency lock; individual references remain private.")


if __name__ == "__main__":
    main()
