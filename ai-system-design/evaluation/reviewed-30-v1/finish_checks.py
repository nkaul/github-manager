"""Offline final reconciliation; does not create a provider or dispatch requests."""

import json
import math
import sqlite3
from collections import Counter, defaultdict
from statistics import median

from runner import OUT, ROOT, read, save, verify  # isort: skip

from app.pretest.ai.evidence import Retriever
from live import Counters
from scoring import score


def distribution(values):
    values = sorted(values)
    return {
        "count": len(values),
        "p50": median(values),
        "p95_nearest_rank": values[math.ceil(len(values) * 0.95) - 1],
        "minimum": min(values),
        "maximum": max(values),
    }


def main():
    verify()
    cases, registry, profiles, inputs, predictions, config = (
        read(OUT / name)
        for name in (
            "reference-snapshot.json",
            "registry.json",
            "profiles.json",
            "classification-inputs.json",
            "predictions.json",
            "config.json",
        )
    )
    counters_before = Counters(OUT / "evaluation-control.sqlite3").summary()
    assert counters_before["generation_attempt_admissions"] == 50
    assert counters_before["http_attempt_admissions"] == 100
    assert all(predictions["primary:" + rid]["status"] == "PASS" for rid in cases)

    # Post-run exploratory diagnostics only. They cannot change frozen production inputs.
    representations = {}
    for representation in ("metadata_only", "packed_purpose_evidence", "rake_phrases_only"):
        rows = []
        retriever = Retriever(registry, "tfidf")
        for rid, case in cases.items():
            evidence = inputs[rid]["payload"]["evidence"]
            if representation == "metadata_only":
                evidence = evidence[:1]
            elif representation == "rake_phrases_only":
                evidence = [{"text": " ".join(p["text"] for p in profiles[rid]["phrases"][:8])}]
            rows.append({**case, "candidate_ids": retriever.candidates({"evidence": evidence})})
        representations[representation] = score(rows, registry)
    reduced = Retriever(registry, "tfidf")
    reduced.LIMITS = {"PROJECT": 4, "TOPIC": 5, "TAG": 6}
    representations["full_evidence_half_candidate_limits"] = score(
        [
            {**case, "candidate_ids": reduced.candidates(profiles[rid])}
            for rid, case in cases.items()
        ],
        registry,
    )
    save(
        "retrieval-representation-diagnostics.json",
        {
            "measurements": representations,
            "scope": "Post-run local exploration; not used to choose or retune the frozen live baseline. No generation or accuracy claim for unknown labels.",
        },
    )

    promptfoo = read(OUT / "promptfoo-results.json")["results"]
    replay_rows = promptfoo["results"]
    seen = set()
    for row in replay_rows:
        rid = str(row["vars"]["repository_id"])
        assert rid not in seen
        seen.add(rid)
        expected = score([{**cases[rid], **predictions["primary:" + rid]}], registry)["ALL"]
        assert row["success"] and row["response"]["cost"] == 0
        assert row["response"]["tokenUsage"]["total"] == 0
        assert row["gradingResult"]["namedScores"]["contract_valid"] == 1
        assert abs(row["score"] - expected["prediction_recall_of_reviewed_positives"]) < 1e-12
        assert row["namedScores"]["unjudged_predictions"] == expected["unjudged_predictions"]
    assert seen == set(cases)
    local = read(OUT / "local-results.json")["rankers"]["tfidf"]
    ragas = read(OUT / "ragas-results.json")
    for kind, value in ragas["candidate_concept_id_recall"].items():
        assert (
            abs(
                value["micro_candidate_recall"]
                - local[kind]["candidate_recall_of_reviewed_positives"]
            )
            < 1e-12
        )
    counters_after = Counters(OUT / "evaluation-control.sqlite3").summary()
    assert counters_before == counters_after

    with sqlite3.connect(ROOT / "docs/validation/private/ai-pretest/runs.sqlite3") as db:
        rows = db.execute(
            "SELECT c.task,c.model,c.charged,c.reserved,c.state,c.detail,p.version FROM calls c JOIN app_call_prices p ON c.id=p.call_id WHERE p.plan_id=?",
            (config["run_id"],),
        ).fetchall()
    by_task = defaultdict(lambda: Counter())
    cache = Counter()
    for task, _model, charged, reserved, _state, detail, _version in rows:
        usage = json.loads(detail)
        by_task[task]["attempts"] += 1
        by_task[task]["charge_micros"] += charged or 0
        by_task[task]["outstanding_reservation_micros"] += reserved if charged is None else 0
        for key in ("input_tokens", "output_tokens", "total_tokens"):
            by_task[task][key] += usage.get(key, 0)
        for key, value in usage.get("input_tokens_details", {}).items():
            cache[key] += value
        cache["reasoning_output_tokens"] += usage.get("output_tokens_details", {}).get(
            "reasoning_tokens", 0
        )
    taxonomy = read(OUT / "taxonomy.json")
    taxonomy_summary = {}
    for key, record in taxonomy.items():
        proposals = record["call"]["result"]["proposals"]
        taxonomy_summary[key] = {
            "status": record["call"]["status"],
            "proposals": len(proposals),
            "kinds": dict(Counter(p["kind"] for p in proposals)),
            "unique_supported_repositories": len(
                {rid for p in proposals for rid in p["supporting_repo_ids"]}
            ),
            "semantic_human_rubric": "NOT_MEASURED",
        }
    successful_primary = [predictions["primary:" + rid]["call"] for rid in cases]
    latencies = {
        "successful_primary_seconds_including_input_count": distribution(
            [r["seconds"] for r in successful_primary]
        ),
        "successful_primary_counted_input_tokens": distribution(
            [r["counted_input_tokens"] for r in successful_primary]
        ),
    }
    save(
        "final-checks.json",
        {
            "status": "PASS",
            "promptfoo_replays": len(replay_rows),
            "promptfoo_contract_successes": promptfoo["stats"]["successes"],
            "promptfoo_per_case_scores_match_local": True,
            "ragas_candidate_id_metrics_match_local": True,
            "framework_replay_added_generations": 0,
            "counter_snapshot_after_all_calls_and_replay": counters_after,
            "ledger_states": dict(Counter(row[4] for row in rows)),
            "ledger_models": dict(Counter(row[1] for row in rows)),
            "pricing_versions": sorted({row[6] for row in rows}),
            "task_usage": {key: dict(value) for key, value in by_task.items()},
            "cache_and_reasoning_usage": dict(cache),
            "latencies": latencies,
            "taxonomy": taxonomy_summary,
            "limits": "Replay success asserts canonical/citation contract and score agreement, not a 100% semantic quality result. Timings are one local serial run, not production SLAs.",
        },
    )
    print(
        json.dumps(
            {
                "framework_replays": len(replay_rows),
                "counters": counters_after,
                "latencies": latencies,
                "taxonomy": taxonomy_summary,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
