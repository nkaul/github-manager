"""Summarize real saved outcomes; absent measurements never become passes."""

import json
import random
import sqlite3
from collections import Counter, defaultdict
from datetime import UTC, datetime

from runner import OUT, ROOT, read, save, verify  # isort: skip

from live import Counters, external_accounted_micros, predictions
from scoring import score


def interval(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row["group"]].append(row)
    keys = sorted(groups)
    rng = random.Random(20261019)
    values = []
    for _ in range(1000):
        sample = [r for key in rng.choices(keys, k=len(keys)) for r in groups[key]]
        p = sum(len(r["positive_ids"]) for r in sample)
        if p:
            values.append(
                sum(len(set(r["positive_ids"]) & set(r.get("predicted_ids", []))) for r in sample)
                / p
            )
    values.sort()
    return {
        "resamples": len(values),
        "groups": len(keys),
        "lower": values[int(len(values) * 0.025)],
        "upper": values[min(len(values) - 1, int(len(values) * 0.975))],
        "scope": "Descriptive resampling of selected leakage groups, not corpus-wide confidence.",
    }


def main():
    verify()
    cases, registry, config = (
        read(OUT / name) for name in ("reference-snapshot.json", "registry.json", "config.json")
    )
    saved = predictions()
    rows = [
        {**case, **saved.get("primary:" + rid, {"status": "NOT_RUN", "predicted_ids": []})}
        for rid, case in cases.items()
    ]
    overall = score(rows, registry)
    slices = {
        split: score([r for r in rows if r["split"] == split], registry)
        for split in ("development", "test_reserved")
    }
    per_domain = {
        domain: score([r for r in rows if r["sampling_domain"] == domain], registry)
        for domain in sorted({r["sampling_domain"] for r in rows})
    }
    compare_ids = [rid for rid in config["comparison"] if "comparison:" + rid in saved]
    comparison = {
        role: score([{**cases[rid], **saved[role + ":" + rid]} for rid in compare_ids], registry)
        for role in ("primary", "comparison")
    }
    # Actual monetary ledger retains failed adapter attempts as well as valid calls.
    dbpath = ROOT / "docs/validation/private/ai-pretest/runs.sqlite3"
    with sqlite3.connect(f"{dbpath.as_uri()}?mode=ro", uri=True) as db:
        calls = db.execute(
            "SELECT c.task,c.model,c.charged,c.reserved,c.state,c.detail FROM calls c JOIN app_call_prices p ON c.id=p.call_id WHERE p.plan_id=?",
            (config["run_id"],),
        ).fetchall()
        plan = db.execute(
            "SELECT ceiling,remaining,state,http_used,generation_used FROM app_run_budgets WHERE id=?",
            (config["run_id"],),
        ).fetchone()
        historical = db.execute(
            "SELECT COUNT(*),COALESCE(SUM(COALESCE(c.charged,c.reserved)),0) FROM calls c LEFT JOIN app_call_prices p ON c.id=p.call_id WHERE p.plan_id IS NULL OR p.plan_id!=?",
            (config["run_id"],),
        ).fetchone()
    cost = sum(charged or 0 for _, _, charged, _, _, _ in calls) / 1e6
    external, _ = external_accounted_micros()
    tokens = Counter()
    for _, _, _, _, _, detail in calls:
        usage = json.loads(detail)
        tokens.update(
            {k: usage.get(k, 0) for k in ("input_tokens", "output_tokens", "total_tokens")}
        )
    budgets = {
        "new_ledger_calls": len(calls),
        "new_estimated_charge_usd": cost,
        "tokens_including_adapter_failures": dict(tokens),
        "original_non_eval_call_rows": historical[0],
        "original_non_eval_accounted_usd": historical[1] / 1e6,
        "combined_accounted_usd": cost + historical[1] / 1e6 + external / 1e6,
        "run_grant": {
            "ceiling_usd": plan[0] / 1e6,
            "remaining_conservative_hold_usd": plan[1] / 1e6,
            "state": plan[2],
            "http_used": plan[3],
            "generation_used": plan[4],
        },
        **Counters(OUT / "evaluation-control.sqlite3").summary(),
    }
    exceptions = []
    for row in rows:
        unknown = set(row.get("predicted_ids", [])) - set(row["positive_ids"])
        missed = set(row["positive_ids"]) - set(row.get("predicted_ids", []))
        if unknown or missed:
            exceptions.append(
                {
                    "id": row["id"],
                    "repository": row["name"],
                    "split": row["split"],
                    "status": row["status"],
                    "unjudged_predictions": [
                        {"id": cid, "name": registry[cid]["name"], "kind": registry[cid]["kind"]}
                        for cid in sorted(unknown)
                    ],
                    "missed_reviewed_positives": [
                        {
                            "id": cid,
                            "name": registry[cid]["name"],
                            "kind": registry[cid]["kind"],
                            "candidate_was_supplied": cid in row["candidate_ids"],
                        }
                        for cid in sorted(missed)
                    ],
                    "human_decisions": "PENDING_NOT_AUTOMATIC_NEGATIVES",
                }
            )
    save("exceptions.json", exceptions)
    lines = [
        "# Evaluation exceptions for optional adjudication",
        "",
        "Original thirty reviews stay confirmed. This sheet asks only about additional predictions or relevant omissions; it does not rewrite references. Record SUPPORTED / UNSUPPORTED / UNKNOWN with source and rationale. A suggested LLM answer is not a human decision.",
        "",
    ]
    for case in exceptions:
        lines += [
            "## " + case["repository"],
            "",
            "[Open public repository](https://github.com/"
            + case["repository"]
            + ") · "
            + case["split"],
            "",
            "| Item | Kind | Reason for review | Human decision / source |",
            "|---|---|---|---|",
        ]
        lines += [
            f"| {r['name']} | {r['kind']} | Extra model prediction; reference unjudged | |"
            for r in case["unjudged_predictions"]
        ]
        lines += [
            f"| {r['name']} | {r['kind']} | Retained positive missed; {'candidate supplied' if r['candidate_was_supplied'] else 'retrieval omission'} | Existing confirmed positive; inspect failure |"
            for r in case["missed_reviewed_positives"]
        ]
        lines += [""]
    (OUT / "exceptions.md").write_text("\n".join(lines) + "\n")
    result = {
        "captured_at_utc": datetime.now(UTC).isoformat(),
        "overall": overall,
        "splits": slices,
        "domains": per_domain,
        "paired_comparison": {"repositories": len(compare_ids), "models": comparison},
        "bootstrap_reviewed_positive_recall": interval(rows),
        "budgets": budgets,
        "exceptions_repositories": len(exceptions),
        "adapter_failures_retained": sum(len(r.get("prior_attempts", [])) for r in saved.values()),
        "frameworks": {
            "ragas": read(OUT / "ragas-results.json")
            if (OUT / "ragas-results.json").exists()
            else {"status": "PENDING"},
            "promptfoo": {
                "result_file": "promptfoo-results.json",
                "available": (OUT / "promptfoo-results.json").exists(),
            },
        },
        "limits": "Unknown labels not negative; single-reviewer selected sample; no exhaustive F1 or external holdout claim.",
    }
    save("evaluation-summary.json", result)
    print(
        json.dumps(
            {
                "overall": overall,
                "splits": {s: v["ALL"] for s, v in slices.items()},
                "budgets": budgets,
                "exceptions_repositories": len(exceptions),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
