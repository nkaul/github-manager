"""Deterministic repository sampling and zero-provider-request run previews."""

import json
from collections import defaultdict
from copy import deepcopy
from datetime import datetime

from app.demo import analysis, domain, explorer, pricing
from app.demo.allowance import RequestAllowance
from app.demo.evidence import model_allowed
from app.demo.run_budget import RunBudgets
from app.pretest.ai.evidence import compact
from app.pretest.ai.storage import BudgetError, digest


def order_candidates(items, taxonomy):
    if taxonomy:
        buckets = defaultdict(list)
        for repo in sorted(items, key=lambda r: r["key"]):
            buckets[(repo.get("owner", ""), repo.get("language") or "Unknown")].append(repo)
        result = []
        while any(buckets.values()):
            for key in sorted(buckets):
                if buckets[key]:
                    result.append(buckets[key].pop(0))
        return result

    def recency(repo):
        try:
            return datetime.fromisoformat(
                repo.get("last_user_activity")
                or repo.get("updated_at")
                or repo.get("pushed_at")
                or ""
            ).timestamp()
        except ValueError:
            return 0

    return sorted(
        items,
        key=lambda r: (
            bool(r["project_count"]),
            bool(r.get("_classified_current")),
            -recency(r),
            r["key"],
        ),
    )


def preview(store, workspace, value, settings, ledger):
    state = store.read(workspace)
    domain.writable(state)
    actor = int(workspace.split(":")[0])
    candidates = explorer.repositories(state, workspace, actor, value.scope.model_dump())
    by_key = {r["key"]: r for r in candidates}
    if value.selection == "MANUAL":
        if not value.repo_keys or any(k not in by_key for k in value.repo_keys):
            raise ValueError("Select repositories in the current scope before previewing")
        candidates = [by_key[k] for k in dict.fromkeys(value.repo_keys)]
    taxonomy = value.mode in {"DISCOVER", "REDISCOVER"}
    rules = value.ai_mode == "RULES" and not taxonomy and value.mode != "EXTRACT"
    if value.ai_mode == "RULES" and taxonomy:
        raise ValueError("Taxonomy discovery needs cached or live AI")
    op = analysis.operation(value.mode)
    for repo in candidates:
        repo["_classified_current"] = bool(analysis.receipt(state, repo["key"]).get("last_success"))
    eligible = [r for r in candidates if rules or model_allowed(r)]
    excluded = [
        {"key": r["key"], "name": r["name"], "reason": "Private or unverified model input"}
        for r in candidates
        if r not in eligible
    ]
    requested = len(candidates) if value.selection == "MANUAL" else value.count
    ordered = order_candidates(eligible, taxonomy)
    if not taxonomy and not rules and not value.reanalyze:
        ordered.sort(key=lambda r: not analysis.admission(state, r["key"], op)[0])
    skipped = (
        [
            {
                "key": r["key"],
                "name": r["name"],
                "reason": analysis.admission(state, r["key"], op, value.reanalyze)[1],
            }
            for r in eligible
            if not analysis.admission(state, r["key"], op, value.reanalyze)[0]
        ]
        if not rules and value.mode != "EXTRACT"
        else []
    )
    if taxonomy:
        ordered = [
            r for r in ordered if analysis.admission(state, r["key"], op, value.reanalyze)[0]
        ]
    chosen = ordered[:requested]
    live = value.ai_mode == "LIVE" and value.mode != "EXTRACT"
    model = settings.openai_taxonomy_model if taxonomy else settings.openai_classification_model
    max_input = (
        settings.ai_pretest_taxonomy_max_input_tokens
        if taxonomy
        else settings.ai_pretest_classification_max_input_tokens
    )
    max_output = (
        settings.ai_pretest_taxonomy_max_output_tokens
        if taxonomy
        else settings.ai_pretest_classification_max_output_tokens
    )
    unit = pricing.reserve_amount(model, max_input, max_output) if live else 0
    policy = RequestAllowance(ledger).policy() if ledger else None
    available = RunBudgets(ledger).available() if ledger else 0
    budget_bound = min(pricing.microdollars(value.budget_usd), available)
    fresh = (
        [r for r in chosen if analysis.admission(state, r["key"], op, value.reanalyze)[0]]
        if live
        else []
    )
    if live and value.budget_mode == "ADAPTIVE" and not taxonomy:
        admitted = budget_bound // unit
        deferred = fresh[admitted:]
        excluded.extend(
            {"key": r["key"], "name": r["name"], "reason": "Deferred by the run's dollar ceiling"}
            for r in deferred
        )
        chosen = [r for r in chosen if r not in deferred]
        fresh = fresh[:admitted]
    generations = (1 if taxonomy else len(fresh)) if live and chosen else 0
    upper = unit * generations
    blocked = None
    if not chosen:
        blocked = (
            (
                "Taxonomy inputs have prior or unknown analysis. Choose Live AI, enable "
                "Re-analyze with AI and enter a reason to intentionally refresh them."
            )
            if taxonomy and skipped
            else "No eligible repositories fit this scope and budget"
        )
    elif value.mode in {"INCREMENTAL", "FULL_CLASSIFICATION"} and not any(
        c["active"] and c["kind"] != "DOMAIN" for c in state["organization"]["concepts"].values()
    ):
        blocked = "Publish or create taxonomy before classifying"
    elif generations and not ledger:
        blocked = "Existing AI ledger is unavailable"
    elif generations and upper > (budget_bound if value.budget_mode == "ADAPTIVE" else available):
        blocked = (
            "The conservative cost bound exceeds available dollars; reduce the run or its scope"
        )
    elif (
        generations
        and value.budget_mode == "FIXED"
        and (
            2 * generations > policy["http"]["remaining"]
            or generations > policy["generations"]["remaining"]
        )
    ):
        blocked = (
            "Fixed request/generation allowance is insufficient; "
            "choose a smaller cohort or adaptive budget"
        )
    plan = {
        "version": state["organization"]["control"]["version"],
        "fence": domain.fence(state),
        "budget_revision": policy["revision"] if policy else None,
        "input": value.model_dump(),
        "keys": [r["key"] for r in chosen],
        "requested": requested,
        "eligible": len(eligible),
        "chosen": len(chosen),
        "excluded": excluded,
        "skipped": skipped,
        "fresh_ai": len(fresh),
        "offline": len(chosen) - len(fresh) if not taxonomy else 0,
        "previously_analyzed_inputs": sum(
            bool(
                analysis.receipt(state, r["key"]).get("last_success")
                or analysis.receipt(state, r["key"], "taxonomy").get("last_success")
            )
            for r in chosen
        ),
        "repositories": [
            {
                "key": r["key"],
                "name": r["name"],
                "language": r.get("language"),
                "source": r["source"],
                "analysis_status": r["analysis"]["status"],
                "freshness": r["analysis"]["freshness"],
                "prior_taxonomy": bool(
                    analysis.receipt(state, r["key"], "taxonomy").get("last_success")
                ),
            }
            for r in chosen
        ],
        "generations": generations,
        "http_requests": 2 * generations,
        "upper_micros": upper,
        "upper_usd": pricing.dollars(upper),
        "per_run_usd": value.budget_usd,
        "model": model if live else None,
        "max_input_tokens": max_input,
        "max_output_tokens": max_output,
        "pricing_version": pricing.VERSION,
        "can_start": blocked is None,
        "blocked_reason": blocked,
        "strategy": "Balanced owner/language sample"
        if taxonomy
        else "New analysis first, then no project, recent work and stable ID",
        "note": (
            "Completed analysis is reconciled locally unless explicit re-analysis is selected. "
            "Upper bound assumes no live cache hits; validated replay/rules reduce actual use. "
            "Cached mode never falls back to paid inference. "
            "Taxonomy uses bounded purpose evidence."
        ),
    }
    plan["fingerprint"] = digest(
        {
            "fence": plan["fence"],
            "keys": plan["keys"],
            "input": plan["input"],
            "budget_revision": plan["budget_revision"],
        }
    )
    plan_id = store.preview_run(workspace, plan)
    return {**plan, "plan_id": plan_id, "expires_in": 300}


def taxonomy_collection(profiles, max_input):
    """Bound application evidence without altering frozen extraction or output limits."""
    collection = [
        {"repo_id": key, **deepcopy(compact(profile))} for key, profile in profiles.items()
    ]
    # One UTF-8 byte is a conservative token upper bound for text. Leave schema/
    # system/role overhead and require the provider's exact count before inference.
    cap = max(512, max_input - 5000)
    if len(json.dumps(collection, ensure_ascii=False).encode()) <= cap:
        return collection
    per_repo = max(100, cap // max(1, len(collection)) - 100)
    for row in collection:
        row["phrases"] = row.get("phrases", [])[:3]
        evidence = row["evidence"][:2]
        for item in evidence:
            item["text"] = (
                item["text"].encode()[: per_repo // max(1, len(evidence))].decode(errors="ignore")
            )
        row["evidence"] = evidence
    while len(json.dumps(collection, ensure_ascii=False).encode()) > cap:
        phrases = [row for row in collection if row.get("phrases")]
        if phrases:
            max(phrases, key=lambda r: len(json.dumps(r["phrases"]).encode()))["phrases"].pop()
            continue
        texts = [
            item
            for row in collection
            for item in row["evidence"]
            if len(item["text"].encode()) > 16
        ]
        if not texts:
            raise BudgetError("Taxonomy evidence does not fit; choose fewer repositories")
        item = max(texts, key=lambda e: len(e["text"].encode()))
        item["text"] = (
            item["text"]
            .encode()[: max(16, len(item["text"].encode()) // 2)]
            .decode(errors="ignore")
        )
    return collection
