"""Approved evaluation calls: original monetary ledger, durable bounded batches."""

import json
import sqlite3

from runner import OUT, ROOT, read, save, verify  # isort: skip

from app.demo.ai import DemoAISettings, DemoProvider
from app.demo.allowance import ApplicationLedger, RequestAllowance
from app.demo.run_budget import RunBudgets
from app.pretest.ai.chains import CLASSIFY_SYSTEM, TAXONOMY_SYSTEM
from app.pretest.ai.schemas import (
    Classification,
    TaxonomyDraft,
    validate_classification,
    validate_taxonomy,
)
from app.pretest.ai.storage import BudgetError, private_json


class Counters:
    def __init__(self, path):
        self.path = path
        with sqlite3.connect(path) as db:
            db.executescript(
                "CREATE TABLE IF NOT EXISTS attempts(id INTEGER PRIMARY KEY, batch TEXT, endpoint TEXT); CREATE TABLE IF NOT EXISTS decision(id TEXT PRIMARY KEY, input_hash TEXT, state TEXT);"
            )

    def take(self, batch, endpoint):
        if batch not in {str(i) for i in range(1, 7)}:
            raise BudgetError("Batch outside approved six-batch schedule")
        if endpoint not in {"/v1/responses", "/v1/responses/input_tokens"}:
            raise BudgetError("Unapproved evaluation endpoint")
        with sqlite3.connect(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            total = db.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]
            used = db.execute("SELECT COUNT(*) FROM attempts WHERE batch=?", (batch,)).fetchone()[0]
            gen = db.execute(
                "SELECT COUNT(*) FROM attempts WHERE endpoint='/v1/responses'"
            ).fetchone()[0]
            slots = 2 if endpoint == "/v1/responses" else 1
            if (
                total + slots > 100
                or used + slots > 20
                or (endpoint == "/v1/responses" and gen >= 50)
            ):
                raise BudgetError(
                    "Approved evaluation call/batch ceiling reached; approval required"
                )
            db.execute("INSERT INTO attempts(batch,endpoint) VALUES (?,?)", (batch, endpoint))

    def summary(self):
        with sqlite3.connect(self.path) as db:
            return {
                "http_attempt_admissions": db.execute("SELECT COUNT(*) FROM attempts").fetchone()[
                    0
                ],
                "generation_attempt_admissions": db.execute(
                    "SELECT COUNT(*) FROM attempts WHERE endpoint='/v1/responses'"
                ).fetchone()[0],
                "batches": dict(db.execute("SELECT batch,COUNT(*) FROM attempts GROUP BY batch")),
            }


def external_accounted_micros():
    """Same conservative cross-ledger accounting used by approved narration work."""
    value = 0
    manifests = {}
    for relative in (
        "demo/voice-preview-v2/speech-requests.json",
        "demo/full-v2/speech-requests.json",
        "demo/article-animation/speech-requests.json",
        "demo/article-animation-full/speech-requests.json",
    ):
        rows = read(ROOT / relative)["requests"]
        cost = sum(
            round(row.get("settled_usd", row.get("reserved_usd", 0)) * 1_000_000) for row in rows
        )
        value += cost
        manifests[relative] = cost
    path = ROOT / "docs/validation/private/demo/full-v2/ai/runs.sqlite3"
    with sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True) as db:
        used = db.execute(
            "SELECT COALESCE(SUM(COALESCE(charged,reserved)),0) FROM calls"
        ).fetchone()[0]
    increment = max(0, used - 127619)
    return value + increment, {
        "media_manifests_micros": manifests,
        "copied_demo_increment_micros": increment,
    }


class EvaluationProvider(DemoProvider):
    def __init__(self, batch):
        verify()
        settings = DemoAISettings(ai_pretest_live_enabled=True)
        settings.require_live(True)
        self.counters = Counters(OUT / "evaluation-control.sqlite3")
        self.batch = str(batch)
        ledger = ApplicationLedger(
            settings.ai_pretest_state_directory, settings.ai_pretest_budget_usd
        )
        plan_id = read(OUT / "config.json")["run_id"]
        plans = RunBudgets(ledger)
        external, details = external_accounted_micros()
        with ledger.connect() as db:
            used = db.execute(
                "SELECT COALESCE(SUM(COALESCE(charged,reserved)),0) FROM calls"
            ).fetchone()[0]
            holds = plans.held(db)
            existing = db.execute(
                "SELECT state FROM app_run_budgets WHERE id=?", (plan_id,)
            ).fetchone()
        if not existing:
            ceiling = min(1_000_000, 5_000_000 - external - used - holds)
            if ceiling <= 0:
                raise BudgetError("Combined historical calls/media leave no cumulative allowance")
            policy = RequestAllowance(ledger).policy()
            plans.reserve(
                plan_id,
                "evaluation:reviewed-30-v1",
                ceiling,
                50,
                "user-approved-2026-10-19",
                policy["revision"],
                store_id="isolated-evaluation",
            )
            plans.activate(plan_id, "evaluation:reviewed-30-v1")
            private_json(
                OUT / "budget-admission.json",
                {
                    "approved_subcap_usd": 1,
                    "effective_hold_usd": ceiling / 1e6,
                    "historical_classification_accounted_usd": used / 1e6,
                    "external_accounted_usd": external / 1e6,
                    **details,
                    "limits": {"http": 100, "generations": 50, "batch_http": 20},
                },
            )
        elif existing[0] != "RUNNING":
            raise BudgetError("Evaluation grant finished; no silent renewal")
        ledger.plan_id = plan_id
        super().__init__(settings, ledger, mode="LIVE", authorized=lambda: True)

    def after(self, response):
        super().after(response)
        if response.status_code == 200:
            import time

            private_json(
                OUT / "raw-responses" / (str(time.time_ns()) + ".json"),
                {"task": self.last.get("task"), "response": response.json()},
            )

    def guard(self, request):
        external, _ = external_accounted_micros()
        with self.ledger.connect() as db:
            used = db.execute(
                "SELECT COALESCE(SUM(COALESCE(charged,reserved)),0) FROM calls"
            ).fetchone()[0]
            holds = RunBudgets.held(db)
        if used + holds + external > 5_000_000:
            raise BudgetError("Combined historical generation/media ceiling reached")
        self.counters.take(self.batch, request.url.path)
        super().guard(request)


def predictions():
    path = OUT / "predictions.json"
    return read(path) if path.exists() else {}


def validate_evaluation_classification(value, context, registry):
    # Corpus definitions enter an isolated evaluation namespace; IDs stay intact.
    return validate_classification(
        value,
        {**context, "workspace": "evaluation"},
        {cid: {**concept, "workspace": "evaluation"} for cid, concept in registry.items()},
    )


def classify_one(provider, rid, model, role, *, retry=False):
    key = role + ":" + rid
    records = predictions()
    if key in records and (records[key]["status"] == "PASS" or not retry):
        return records[key]
    inputs, registry = (
        read(OUT / "classification-inputs.json"),
        read(OUT / "registry.json"),
    )
    data = inputs[rid]
    result = provider.invoke(
        model,
        "eval-classification-" + role,
        Classification,
        CLASSIFY_SYSTEM,
        data["payload"],
        lambda value: validate_evaluation_classification(value, data["context"], registry),
    )
    record = {
        "id": rid,
        "role": role,
        "call": result,
        "predicted_ids": [a["concept_id"] for a in result.get("result", {}).get("assignments", [])],
        "status": result["status"],
    }
    if key in records:
        record["prior_attempts"] = [
            *records[key].get("prior_attempts", []),
            {k: v for k, v in records[key].items() if k != "prior_attempts"},
        ]
    records[key] = record
    save("predictions.json", records)
    save("usage-progress.json", provider.counters.summary())
    print(
        json.dumps(
            {
                "task": key,
                "status": result["status"],
                "http": result.get("http_status"),
                "count_http": result.get("count_http_status"),
                "input_tokens": result.get("counted_input_tokens"),
                "error_type": result.get("error_type"),
            }
        ),
        flush=True,
    )
    return record


def taxonomy_checks(provider):
    from app.demo.cohorts import taxonomy_collection

    config, profiles = read(OUT / "config.json"), read(OUT / "profiles.json")
    selected = config["development"]
    output = read(OUT / "taxonomy.json") if (OUT / "taxonomy.json").exists() else {}
    for index, cohort in enumerate((selected[:8], selected[8:])):
        key = "draft-" + str(index + 1)
        if key in output:
            continue
        evidence = {
            "source": "PUBLIC_GITHUB",
            "private": False,
            "collection": taxonomy_collection({i: profiles[i] for i in cohort}, 12000),
        }
        result = provider.invoke(
            config["taxonomy_model"],
            "taxonomy-eval-" + key,
            TaxonomyDraft,
            TAXONOMY_SYSTEM,
            evidence,
            lambda value, cohort=cohort: validate_taxonomy(value, set(cohort)),
        )
        output[key] = {"cohort_ids": cohort, "payload": evidence, "call": result}
        save("taxonomy.json", output)
        print(json.dumps({"task": key, "status": result["status"]}), flush=True)
    if "consolidation" not in output and all(
        output[key]["call"]["status"] == "PASS" for key in ("draft-1", "draft-2")
    ):
        evidence = {
            "source": "PUBLIC_GITHUB",
            "private": False,
            "allowed_repo_ids": selected,
            "drafts_to_consolidate": [
                output[key]["call"]["result"] for key in ("draft-1", "draft-2")
            ],
        }
        result = provider.invoke(
            config["taxonomy_model"],
            "taxonomy-eval-consolidation",
            TaxonomyDraft,
            TAXONOMY_SYSTEM,
            evidence,
            lambda value: validate_taxonomy(value, set(selected)),
        )
        output["consolidation"] = {"payload": evidence, "call": result}
        save("taxonomy.json", output)
        print(
            json.dumps({"task": "consolidation", "status": result["status"]}),
            flush=True,
        )


def wave(number):
    config = read(OUT / "config.json")
    provider = EvaluationProvider(number)
    try:
        dev, test, compare = (
            config["development"],
            config["test_reserved"],
            config["comparison"],
        )
        primary = (
            dev[:8]
            if number == 1
            else dev[8:]
            if number == 2
            else test[:8]
            if number == 5
            else test[8:]
            if number == 6
            else []
        )
        if number in {5, 6} and not (OUT / "test-freeze.json").exists():
            raise BudgetError("Create explicit producer/scoring freeze before test generation")
        for rid in primary:
            classify_one(provider, rid, config["primary_model"], "primary")
        for rid in compare[:1] if number == 2 else compare[1:3] if number == 3 else []:
            classify_one(provider, rid, config["comparison_model"], "comparison")
        if number == 3:
            taxonomy_checks(provider)
        save("usage-progress.json", provider.counters.summary())
    finally:
        provider.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wave", type=int, choices=[1, 2, 3, 5, 6])
    wave(parser.parse_args().wave)
