"""Build documentation examples with local extraction and mock-only serialization.

Reads the existing authored Orion samples and published example registry. Does
not construct BudgetedProvider, read .env, call GitHub/OpenAI, or mutate app state.
"""

import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "backend"))

import httpx2
from langchain_openai import ChatOpenAI
from langsmith import tracing_context

from app.demo.cohorts import taxonomy_collection
from app.demo.evidence import sample_records
from app.pretest.ai.chains import CLASSIFY_SYSTEM, TAXONOMY_SYSTEM
from app.pretest.ai.evidence import Retriever, compact, tokens
from app.pretest.ai.schemas import Classification, TaxonomyDraft
from app.pretest.ai.settings import AISettings


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def capture_request(model, system, payload, schema, effort, maximum):
    captured = []

    def handler(request):
        assert str(request.url) == "https://api.openai.com/v1/responses"
        captured.append(json.loads(request.content))
        raise RuntimeError("OFFLINE_SERIALIZATION_COMPLETE")

    with httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False) as client:
        llm = ChatOpenAI(
            model=model,
            api_key="offline-placeholder-not-a-key",
            base_url="https://api.openai.com/v1",
            use_responses_api=True,
            store=False,
            service_tier="default",
            reasoning_effort=effort,
            max_tokens=maximum,
            max_retries=0,
            timeout=5,
            http_client=client,
        )
        chain = llm.with_structured_output(
            schema, method="json_schema", strict=True, include_raw=True
        )
        try:
            with tracing_context(enabled=False):
                chain.invoke(
                    [("system", system), ("human", json.dumps(payload, ensure_ascii=False))],
                    config={"callbacks": []},
                )
        except Exception:
            if len(captured) != 1:
                raise
    assert len(captured) == 1
    result = captured[0]
    assert result["store"] is False and not result.get("tools")
    assert result["text"]["format"]["strict"] is True
    return result


def main():
    defaults = {name: field.default for name, field in AISettings.model_fields.items()}
    repos, profiles = sample_records()
    keys = ["synthetic/orion-api", "synthetic/orion-ui"]
    profiles = {key: profiles[key] for key in keys}
    registry_path = ROOT / "eval/ai-system-design/publication/v2/examples/registry.json"
    registry = json.loads(registry_path.read_text())["concepts"]
    # A clearly authored documentation workspace, not a real account identifier.
    workspace = "0:samples"
    registry = {key: {**value, "workspace": workspace} for key, value in registry.items()}
    searchable = {
        key: value for key, value in registry.items()
        if value["active"] and value["kind"] != "DOMAIN"
        and tokens(" ".join([value["name"], value["description"], *value["aliases"]]))
    }
    retriever = Retriever(searchable, method="tfidf")
    profile = profiles[keys[0]]
    candidates = retriever.candidates(profile)
    payload = {
        "source": repos[keys[0]]["source"],
        "private": False,
        "repo_id": keys[0],
        "workspace": workspace,
        "revision": 1,
        "evidence_hash": profile["hash"],
        "policy": profile["policy"],
        **compact(profile),
        "candidates": [
            {name: registry[key][name] for name in ("id", "kind", "name", "description")}
            for key in candidates
        ],
    }
    taxonomy = {
        "source": "PUBLIC_AND_SYNTHETIC", "private": False,
        "collection": taxonomy_collection(
            profiles, defaults["ai_pretest_taxonomy_max_input_tokens"]
        ),
    }
    context = {
        "revision": 1, "active_revision": 1,
        "profile_hash": profile["hash"], "active_profile_hash": profile["hash"],
        "workspace": workspace, "candidates": candidates,
        "evidence_ids": [e["id"] for e in profile["evidence"]], "rejections": [],
    }
    q = set(tokens(" ".join(e["text"] for e in profile["evidence"])))
    ranking = []
    for key, doc in zip(retriever.ids, retriever.docs, strict=True):
        overlap = q & set(doc)
        denominator = math.sqrt(
            sum(retriever.idf.get(w, 1) ** 2 for w in q)
            * sum(retriever.idf[w] ** 2 for w in set(doc))
        )
        cosine = sum(retriever.idf[w] ** 2 for w in overlap) / denominator if denominator else 0
        item = searchable[key]
        boost = 3 if any(
            set(tokens(alias)) <= q for alias in [item["name"], *item["aliases"]]
            if tokens(alias)
        ) else 0
        ranking.append({
            "id": key, "name": item["name"], "kind": item["kind"],
            "cosine": cosine, "alias_boost": boost, "score": cosine + boost,
            "shortlisted": key in candidates, "matching_tokens": sorted(overlap),
        })
    save("source-repositories.json", {key: repos[key] for key in keys})
    save("profiles.json", profiles)
    save("registry.json", registry)
    save("retrieval.json", {"query_tokens": sorted(q), "canonical_documents": len(retriever.docs), "rows": ranking, "shortlist": candidates})
    save("taxonomy-payload.json", taxonomy)
    save("classification-payload.json", payload)
    save("classification-server-context.json", context)
    for task, schema, system, value in [
        ("taxonomy", TaxonomyDraft, TAXONOMY_SYSTEM, taxonomy),
        ("classification", Classification, CLASSIFY_SYSTEM, payload),
    ]:
        (HERE / f"{task}-system-prompt.txt").write_text(system + "\n")
        save(f"{task}-schema.json", schema.model_json_schema())
        save(f"{task}-messages.json", [{"role": "system", "content": system}, {"role": "human", "content": json.dumps(value, ensure_ascii=False)}])
        save(f"{task}-request.json", capture_request(
            defaults[f"openai_{task}_model"], system, value, schema,
            defaults[f"openai_{task}_reasoning_effort"],
            defaults[f"ai_pretest_{task}_max_output_tokens"],
        ))
    source_paths = [
        "backend/app/demo/service.py", "backend/app/demo/evidence.py",
        "backend/app/demo/cohorts.py", "backend/app/demo/taxonomy_review.py",
        "backend/app/pretest/ai/evidence.py", "backend/app/pretest/ai/chains.py",
        "backend/app/pretest/ai/schemas.py", "backend/app/pretest/ai/provider.py",
        "backend/app/pretest/ai/settings.py",
    ]
    save("provenance.json", {
        "date": "2026-10-20", "source": "Current local application code",
        "example": "Existing authored Orion synthetic samples and published authored benchmark registry; documentation workspace 0:samples and revision 1 are illustrative.",
        "model_settings": "Code defaults, not a reading of backend/.env or a claim about a live run's overrides.",
        "real_network_requests": 0, "live_generations": 0,
        "mock_serializations": 2, "app_state_writes": 0,
        "registry_source": str(registry_path.relative_to(ROOT)),
        "source_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in source_paths},
    })
    print(json.dumps({"status": "PASS", "profiles": len(profiles), "candidate_ids": candidates, "mock_requests": 2, "real_network_requests": 0}))


if __name__ == "__main__":
    main()
