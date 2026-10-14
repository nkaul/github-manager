"""Compact durable analysis receipts, independent of memberships and optional run history."""

import time

from app.pretest.ai.storage import digest

REAL = {"LIVE_PROVIDER", "REPLAY"}
SUCCESS = {"CLASSIFIED", "NO_MATCH"}
DEFAULT_TYPES = ["CREATE", "CREATE_PROJECT", "EDIT", "ARCHIVE", "MERGE", "RULE", "EVIDENCE"]


def operation(kind):
    return "taxonomy" if kind in {"DISCOVER", "REDISCOVER"} else "classification"


def new_repository(state, key):
    state["organization"].setdefault("analysis", {}).setdefault(
        key,
        {name: {"state": "NEW", "ai_analyzed": False} for name in ("classification", "taxonomy")},
    )


def upgrade(state):
    org = state["organization"]
    records = org.setdefault("analysis", {})
    if org.get("analysis_schema") == 1:
        return state
    for key in state["core"]["repos"]:
        records.setdefault(
            key,
            {
                name: {"state": "UNKNOWN", "ai_analyzed": False}
                for name in ("classification", "taxonomy")
            },
        )
    for run in sorted(org["runs"].values(), key=lambda r: r.get("created_at", "")):
        if run["kind"] not in {"INCREMENTAL", "FULL_CLASSIFICATION"}:
            continue
        for key, outcome in run.get("outcomes", {}).items():
            rec = records.setdefault(key, {}).setdefault("classification", {})
            evidence, model = outcome.get("evidence"), outcome.get("model")
            if outcome.get("status") in SUCCESS and model and evidence in REAL | {"FIXTURE"}:
                rec.update(
                    state="SUCCEEDED",
                    ai_analyzed=evidence in REAL,
                    last_success={
                        "at": run.get("finished_at", run.get("created_at")),
                        "run_id": run["id"],
                        "status": outcome["status"],
                        "evidence": evidence,
                        "model": model,
                        "revision": run.get("revision"),
                        "fingerprint_known": False,
                        "backfilled": True,
                    },
                )
            elif outcome.get("status") in {"FAILED", "INPUT_UNAVAILABLE", "STALE"}:
                rec.update(state="FAILED", error=outcome.get("error"), last_attempt_run=run["id"])
    for draft in sorted(org["drafts"].values(), key=lambda d: d.get("created_at", "")):
        if not draft.get("model") or draft.get("evidence") not in REAL | {"FIXTURE"}:
            continue
        for key in draft.get("repo_keys", []):
            rec = records.setdefault(key, {}).setdefault("taxonomy", {})
            rec.update(
                state="SUCCEEDED",
                ai_analyzed=draft["evidence"] in REAL,
                last_success={
                    "at": draft.get("created_at"),
                    "status": "DRAFTED",
                    "draft_id": draft["id"],
                    "evidence": draft["evidence"],
                    "model": draft["model"],
                    "revision": draft.get("revision"),
                    "fingerprint_known": False,
                    "backfilled": True,
                },
            )
    org["analysis_schema"] = 1
    return state


def receipt(state, key, op="classification"):
    return (
        state["organization"]
        .get("analysis", {})
        .get(key, {})
        .get(op, {"state": "UNKNOWN", "ai_analyzed": False})
    )


def admission(state, key, op="classification", force=False):
    rec = receipt(state, key, op)
    if rec.get("state") == "RUNNING":
        return False, "Analysis is already in flight"
    if force:
        return True, "Explicit re-analysis"
    if rec.get("last_success"):
        return False, "Already analyzed; reconcile offline"
    if rec.get("state") != "NEW":
        return False, "Prior attempt or unknown history; explicit re-analysis required"
    return True, "New repository"


def metadata(repo):
    return digest(
        {k: repo.get(k) for k in ("name", "description", "topics", "language", "readme_sha")}
    )


def projection(state, key):
    rec = receipt(state, key)
    success = rec.get("last_success")
    stale = False
    if success:
        profile = state["intelligence"]["profiles"].get(key)
        control = state["organization"]["control"]
        stale = (
            success.get("revision") != control["revision"]
            or success.get("taxonomy_epoch", control["taxonomy_epoch"]) != control["taxonomy_epoch"]
            or bool(
                success.get("profile_hash")
                and (not profile or success["profile_hash"] != profile["hash"])
            )
            or bool(
                success.get("metadata_hash")
                and success["metadata_hash"] != metadata(state["core"]["repos"][key])
            )
        )
    status = rec.get("state", "UNKNOWN")
    if status == "SUCCEEDED":
        status = success["status"] if success else "UNKNOWN"
    freshness = (
        "STALE"
        if stale
        else "CURRENT"
        if success and success.get("fingerprint_known")
        else "UNKNOWN"
    )
    return {
        "state": rec.get("state", "UNKNOWN"),
        **rec,
        "status": status,
        "stale": stale,
        "ai_analyzed": bool(rec.get("ai_analyzed")),
        "freshness": freshness,
    }


def claim(state, keys, op, run_id, force, reason, expected):
    from app.demo import domain

    domain.check_fence(state, expected)
    approved = []
    for key in keys:
        repo = state["core"]["repos"].get(key)
        if not repo or repo.get("unavailable"):
            continue
        if not admission(state, key, op, force)[0]:
            continue
        rec = (
            state["organization"].setdefault("analysis", {}).setdefault(key, {}).setdefault(op, {})
        )
        rec.update(
            state="RUNNING", last_attempt_run=run_id, last_attempt_at=time.time(), reason=reason
        )
        approved.append(key)
    return approved


def record(state, key, op, run_id, result, profile, expected, system):
    from app.demo import domain

    rec = state["organization"].setdefault("analysis", {}).setdefault(key, {}).setdefault(op, {})
    if rec.get("last_attempt_run") != run_id:
        return
    passed = result.get("status") == "PASS"
    rec.update(state="SUCCEEDED" if passed else "FAILED", error=result.get("error_type"))
    if passed:
        current = (
            domain.fence(state) == expected and not state["organization"]["control"]["resetting"]
        )
        real = result.get("evidence") in REAL and bool(result.get("returned_model"))
        rec["ai_analyzed"] = bool(rec.get("ai_analyzed")) or real
        rec["last_success"] = {
            "at": time.time(),
            "run_id": run_id,
            "status": result["result"].get("status", "DRAFTED"),
            "evidence": result["evidence"],
            "model": result.get("returned_model"),
            "profile_hash": profile.get("hash"),
            "metadata_hash": metadata(state["core"]["repos"].get(key, {})),
            "revision": expected["revision"],
            "taxonomy_epoch": expected["taxonomy_epoch"],
            "fence": expected,
            "prompt_hash": digest(system),
            "schema_version": "demo-v1",
            "cache_key": result.get("cache_key"),
            "fingerprint_known": True,
            "result": result["result"] if op == "classification" and current else None,
            "references_invalidated": not current,
        }


def interrupt(state, run_id):
    for operations in state["organization"].get("analysis", {}).values():
        for rec in operations.values():
            if rec.get("state") == "RUNNING" and rec.get("last_attempt_run") == run_id:
                rec.update(state="UNCERTAIN", error="Interrupted attempt; remote outcome unknown")


def automation(state, timestamp=None):
    now = timestamp or time.time()
    org, c = state["organization"], state["organization"]["control"]
    types = c.get("auto_change_types", DEFAULT_TYPES)
    events = [
        x
        for i, x in enumerate(org["changes"], 1)
        if x.get("sequence", i) > c.get("auto_processed_sequence", 0)
        and x["at"] >= now - c.get("auto_window_seconds", 900)
        and x["type"] in types
    ]
    weight = sum(x["weight"] for x in events)
    entities = len({x["entity"] for x in events})
    projects = len({x["entity"] for x in events if x["type"] == "CREATE_PROJECT"})
    threshold = (
        weight >= c.get("auto_weight_threshold", 6)
        and entities >= c.get("auto_entity_threshold", 3)
    ) or (c.get("auto_project_threshold", 2) > 0 and projects >= c.get("auto_project_threshold", 2))
    quiet = max(0, c.get("quiet_seconds", 90) - (now - max((x["at"] for x in events), default=0)))
    cooldown = max(0, c.get("cooldown_seconds", 1800) - (now - c.get("last_auto", 0)))
    return {
        "weight": weight,
        "entities": entities,
        "new_projects": projects,
        "threshold_met": threshold,
        "quiet_remaining": round(quiet),
        "cooldown_remaining": round(cooldown),
        "ready": bool(events and threshold and not quiet and not cooldown),
        "sequence": max((x.get("sequence", i) for i, x in enumerate(org["changes"], 1)), default=0),
    }
