"""One authorized twenty-case primary-label validation round, with four isolated clients."""

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime

from app.pretest.ai.chains import CLASSIFY_SYSTEM, classify
from app.pretest.ai.corpus import load_corpus, registry
from app.pretest.ai.evaluation import metrics, percentiles
from app.pretest.ai.evidence import Retriever
from app.pretest.ai.provider import BudgetedProvider
from app.pretest.ai.runner import freeze
from app.pretest.ai.schemas import Classification
from app.pretest.ai.settings import AISettings
from app.pretest.ai.storage import Ledger, digest, private_json
from app.pretest.report import write_report


def run(settings, *, workers=4):
    directory = settings.ai_pretest_state_directory
    path = directory / "validation-round-2.local.json"
    if path.exists():
        raise ValueError("Round already attempted; preserve its outcome instead of repeating calls")
    ledger = Ledger(directory, settings.ai_pretest_budget_usd)
    before = ledger.summary()
    if before["calls"] != 14 or settings.ai_pretest_max_generation_calls != 34:
        raise ValueError("This authorization covers only attempts 15 through 34")
    cases, concepts = load_corpus(directory), registry()
    local = json.loads((directory / "offline.local.json").read_text())
    corpus_hash = freeze(directory, cases, concepts)
    review = json.loads((directory / "reference-review.local.json").read_text())
    if not review.get("approved") or review["corpus_hash"] != corpus_hash:
        raise ValueError("Approved reference corpus required")
    cases = [repo for repo in cases if repo["split"] == "heldout"]
    if len(cases) != 20:
        raise ValueError("Exactly twenty frozen held-out cases required")
    output = {
        "status": "RUNNING",
        "evidence": "LIVE_PROVIDER",
        "model": settings.openai_classification_model,
        "started_utc": datetime.now(UTC).isoformat(),
        "corpus_hash": corpus_hash,
        "authorization": "User authorized another set of <=20 API calls; original $5 cap retained",
        "call_limit": 20,
        "total_generation_ceiling": 34,
        "workers": workers,
        "selection": [r["id"] for r in cases],
        "budget_before": before,
        "prompt": CLASSIFY_SYSTEM,
        "prompt_hash": digest(CLASSIFY_SYSTEM),
        "schema_hash": digest(Classification.model_json_schema()),
        "policy": "primary labels only; no label/extractor changes; no retries or expansions",
        "records": [],
    }
    private_json(path, output, exclusive=True)
    started = time.monotonic()
    profiles = local["profiles"]["rake"]
    retriever = Retriever(concepts, local["retrieval_choice"])
    candidates = {r["id"]: retriever.candidates(profiles[r["id"]]) for r in cases}

    def check(repo):
        # Provider.last and HTTP hooks are per-client mutable state: never share between threads.
        provider = BudgetedProvider(settings, ledger)
        try:
            call = classify(
                provider,
                settings.openai_classification_model,
                repo,
                profiles[repo["id"]],
                candidates[repo["id"]],
                concepts,
                task="classification-primary-round2",
                fresh=True,
            )
        finally:
            provider.close()
        return {
            "id": repo["id"],
            "source": repo["source"],
            "gold": repo["labels"],
            "predicted": [a["concept_id"] for a in call.get("result", {}).get("assignments", [])],
            "call": call,
        }

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(check, repo): repo for repo in cases}
        for future in as_completed(futures):
            repo = futures[future]
            try:
                record = future.result()
            except Exception as error:
                record = {
                    "id": repo["id"],
                    "source": repo["source"],
                    "gold": repo["labels"],
                    "predicted": [],
                    "call": {"status": "FAIL", "error_type": type(error).__name__},
                }
            output["records"].append(record)
            private_json(
                directory / f"round2-case-{digest(repo['id'])[:16]}.local.json",
                record,
                exclusive=True,
            )
            private_json(path, output)
            print(
                json.dumps(
                    {
                        "stage": "primary-round2",
                        "done": len(output["records"]),
                        "case": repo["id"],
                        "status": record["call"]["status"],
                    }
                ),
                flush=True,
            )
    output["records"].sort(key=lambda r: output["selection"].index(r["id"]))
    output["budget_after"] = ledger.summary()
    output["generation_attempts"] = output["budget_after"]["calls"] - before["calls"]
    output["round_estimated_usd"] = round(
        output["budget_after"]["estimated_usd"] - before["estimated_usd"], 6
    )
    output["seconds"] = round(time.monotonic() - started, 3)
    output["metrics"] = metrics(output["records"], concepts)
    output["slices"] = {
        source: metrics([r for r in output["records"] if r["source"] == source], concepts)
        for source in ("PUBLIC_GITHUB", "SYNTHETIC")
    }
    output["latency"] = percentiles(
        [r["call"]["seconds"] for r in output["records"] if "seconds" in r["call"]]
    )
    output["status"] = (
        "PASS_CONTRACT"
        if all(r["call"]["status"] == "PASS" for r in output["records"])
        else "PARTIAL_FAILED"
    )
    output["quality_targets_met"] = (
        output["status"] == "PASS_CONTRACT"
        and all(
            (output["metrics"][kind]["precision"] or 0) >= 0.85
            and (output["metrics"][kind]["recall"] or 0) >= 0.75
            for kind in ("PROJECT", "TOPIC", "TAG")
        )
        and (output["metrics"]["ALL"]["f1"] or 0) >= 0.80
    )
    private_json(path, output)
    rows = [
        {
            "check": r["id"],
            "evidence": "LIVE_PROVIDER",
            "status": r["call"]["status"],
            "detail": ", ".join(r["predicted"]) or "No assignments",
        }
        for r in output["records"]
    ]
    report = write_report(
        directory,
        "ai-primary-round2",
        "Phase 0.5 primary-label validation",
        rows,
        [
            f"Prompt hash: {output['prompt_hash']}",
            f"Corpus hash: {corpus_hash}",
            f"Generation attempts: {output['generation_attempts']}; no retries/expansion",
            f"Quality targets met: {output['quality_targets_met']}",
        ],
    )
    private_json(report.with_suffix(".local.json"), output)
    print(
        json.dumps(
            {
                "status": output["status"],
                "quality_targets_met": output["quality_targets_met"],
                "seconds": output["seconds"],
                "budget": output["budget_after"],
                "report": str(report),
            }
        ),
        flush=True,
    )
    return 0 if output["status"] == "PASS_CONTRACT" else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", required=True)
    args = parser.parse_args()
    settings = AISettings()
    settings.require_live(args.live)
    return run(settings)


if __name__ == "__main__":
    try:
        result = main()
    except Exception as error:
        print(json.dumps({"status": "BLOCKED", "error_type": type(error).__name__}))
        result = 2
    raise SystemExit(result)
