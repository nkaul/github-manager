"""Ten-request continuation requested after account credit restoration."""

import json

from app.pretest.ai.chains import classify, taxonomy
from app.pretest.ai.evaluation import metrics, organization_simulation
from app.pretest.ai.evidence import Retriever
from app.pretest.ai.schemas import AccessProbe
from app.pretest.ai.storage import private_json


def limited_checks(provider, settings, cases, concepts, local):
    directory = settings.ai_pretest_state_directory
    path = directory / "limited.local.json"
    if path.exists():
        raise ValueError("Limited run already recorded; do not silently repeat paid checks")
    selection = ["fastapi/fastapi", "synthetic/orion-audit", "synthetic/negated-api"]
    output = {
        "scope": "limited smoke; not full held-out benchmark",
        "corpus_hash": local["corpus_hash"],
        "selection": selection,
        "label_review": "APPROVED_USER",
        "access": [],
        "taxonomy": [],
        "classification": {},
        "ablations": [],
        "stability": [],
        "generation_limit_total": settings.ai_pretest_max_generation_calls,
        "budget_before": provider.ledger.summary(),
        "remaining_gates": [
            "full 20-case API benchmark",
            "Astra comparison",
            "human taxonomy/extraction ratings",
            "stable per-model latency",
        ],
    }
    private_json(path, output, exclusive=True)

    def checkpoint():
        output["budget_after"] = provider.ledger.summary()
        private_json(path, output)

    models = list(
        dict.fromkeys([settings.openai_classification_model, settings.openai_taxonomy_model])
    )
    for model in models:
        result = provider.invoke(
            model,
            "access",
            AccessProbe,
            "Synthetic preflight. Return authenticated true and category TEST.",
            {"source": "SYNTHETIC", "private": False},
            lambda value: value if value.authenticated else fail_access(),
            max_output=512,
            fresh=True,
        )
        output["access"].append(result)
        checkpoint()
        print(
            json.dumps({"stage": "limited-access", "model": model, "status": result["status"]}),
            flush=True,
        )
        if result["status"] != "PASS":
            return output
    private_json(directory / "access.local.json", output["access"])
    profiles = local["profiles"]["rake"]
    output["taxonomy"].append(
        taxonomy(
            provider,
            settings.openai_taxonomy_model,
            list(profiles.values()),
            task="taxonomy-limited",
        )
    )
    checkpoint()
    lookup = {repo["id"]: repo for repo in cases}
    retriever = Retriever(concepts, local["retrieval_choice"])
    for model in models:
        records = []
        output["classification"][model] = {"records": records, "metrics": None}
        for ident in selection if model == settings.openai_classification_model else selection[:1]:
            repo, prof = lookup[ident], profiles[ident]
            result = classify(provider, model, repo, prof, retriever.candidates(prof), concepts)
            predicted = [a["concept_id"] for a in result.get("result", {}).get("assignments", [])]
            records.append(
                {
                    "id": ident,
                    "source": repo["source"],
                    "gold": repo["labels"],
                    "predicted": predicted,
                    "call": result,
                }
            )
            output["classification"][model]["metrics"] = metrics(records, concepts)
            checkpoint()
            print(
                json.dumps(
                    {
                        "stage": "limited-classification",
                        "model": model,
                        "case": ident,
                        "status": result["status"],
                    }
                ),
                flush=True,
            )
            if result["status"] != "PASS":
                return output
        output["classification"][model]["status"] = "MEASURED_SMALL_SUBSET"
    repo = lookup[selection[0]]
    for representation in ("baseline", "yake"):
        prof = local["profiles"]["yake" if representation == "yake" else "rake"][repo["id"]]
        result = classify(
            provider,
            settings.openai_classification_model,
            repo,
            prof,
            retriever.candidates(prof),
            concepts,
            representation=representation,
            task=f"ablation-{representation}",
        )
        output["ablations"].append(
            {"id": repo["id"], "representation": representation, "call": result}
        )
        checkpoint()
        if result["status"] != "PASS":
            return output
    prof = profiles[repo["id"]]
    result = classify(
        provider,
        settings.openai_classification_model,
        repo,
        prof,
        retriever.candidates(prof),
        concepts,
        fresh=True,
    )
    output["stability"].append({"id": repo["id"], "call": result})
    output["organization_example"] = organization_simulation(
        [i for r in output["classification"][models[0]]["records"] for i in r["predicted"]],
        concepts,
    )
    checkpoint()
    return output


def fail_access():
    raise ValueError("Unexpected access result")
