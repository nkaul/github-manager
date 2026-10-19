"""Reconstruct article examples offline from preserved public/synthetic records.

Run with backend/.venv/bin/python from the repository. No .env loading, provider
requests, ledger initialization or live workspace writes. LangChain serialization
uses a mock transport; socket connections are additionally denied.
"""

import hashlib
import importlib.metadata
import json
import math
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
DATA = ROOT / "docs/validation/private/ai-pretest"
sys.path.insert(0, str(ROOT / "backend"))


def deny_network(*args, **kwargs):
    raise RuntimeError("Article example reconstruction denies network access")


socket.socket.connect = deny_network
socket.create_connection = deny_network

import httpx2  # noqa: E402
from langchain_openai import ChatOpenAI  # noqa: E402

from app.demo import analysis, domain  # noqa: E402
from app.demo.store import initial_state  # noqa: E402
from app.pretest.ai.chains import (  # noqa: E402
    CLASSIFY_SYSTEM,
    TAXONOMY_SYSTEM,
    classification_input,
)
from app.pretest.ai.corpus import load_corpus, registry  # noqa: E402
from app.pretest.ai.evidence import Retriever, compact, tokens  # noqa: E402
from app.pretest.ai.schemas import (  # noqa: E402
    Classification,
    TaxonomyDraft,
    validate_classification,
    validate_taxonomy,
)
from app.pretest.ai.storage import digest  # noqa: E402


def read(name):
    return json.loads((DATA / name).read_text())


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture_request(model, system, payload, schema, effort, max_output):
    captured = []

    def handler(request):
        assert str(request.url) == "https://api.openai.com/v1/responses"
        captured.append(json.loads(request.content))
        raise RuntimeError("OFFLINE_CAPTURE_COMPLETE")

    with httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False) as client:
        llm = ChatOpenAI(
            model=model,
            api_key="offline-placeholder-not-a-key",
            base_url="https://api.openai.com/v1",
            use_responses_api=True,
            store=False,
            service_tier="default",
            reasoning_effort=effort,
            max_tokens=max_output,
            max_retries=0,
            timeout=5,
            http_client=client,
        )
        chain = llm.with_structured_output(
            schema, method="json_schema", strict=True, include_raw=True
        )
        try:
            chain.invoke(
                [("system", system), ("human", json.dumps(payload, ensure_ascii=False))],
                config={"callbacks": []},
            )
        except Exception:
            # A mock-only transport stopped after serializing the request.
            if len(captured) != 1:
                raise
    assert len(captured) == 1
    body = captured[0]
    assert body["store"] is False and not body.get("tools")
    assert body["text"]["format"]["strict"] is True
    return body


def logical_cache_key(model, task, system, payload, schema, effort, max_input, max_output):
    return digest(
        {
            "model": model,
            "task": task,
            "prompt_version": "phase05-v1",
            "system": system,
            "evidence": payload,
            "schema": schema.model_json_schema(),
            "effort": effort,
            "max_input": max_input,
            "max_output": max_output,
            "privacy": "public_and_synthetic-v1",
            "store": False,
            "tier": "default",
        }
    )


def scored_candidates(prof, retriever):
    q = set(tokens(" ".join(e["text"] for e in prof["evidence"])))
    rows = []
    shortlist = retriever.candidates(prof)
    for ident, doc in zip(retriever.ids, retriever.docs, strict=True):
        item = retriever.registry[ident]
        overlap = sorted(q & set(doc))
        numerator = sum(retriever.idf[w] ** 2 for w in overlap)
        denominator = math.sqrt(
            sum(retriever.idf.get(w, 1) ** 2 for w in q)
            * sum(retriever.idf[w] ** 2 for w in set(doc))
        )
        cosine = numerator / denominator if denominator else 0
        matches = [
            alias
            for alias in [item["name"], *item["aliases"]]
            if tokens(alias) and set(tokens(alias)) <= q
        ]
        score = cosine + 3 * bool(matches)
        if score > 0:
            rows.append(
                {
                    "id": ident,
                    "kind": item["kind"],
                    "name": item["name"],
                    "document_tokens": sorted(set(doc)),
                    "overlap": overlap,
                    "matched_name_or_alias": matches,
                    "cosine": cosine,
                    "alias_boost": 3 if matches else 0,
                    "score": score,
                    "shortlisted": ident in shortlist,
                }
            )
    rows.sort(key=lambda r: (list(Retriever.LIMITS).index(r["kind"]), -r["score"], r["id"]))
    recomputed = []
    for kind, limit in Retriever.LIMITS.items():
        recomputed.extend(r["id"] for r in rows if r["kind"] == kind and r["shortlisted"])
        assert sum(r["shortlisted"] for r in rows if r["kind"] == kind) <= limit
    assert recomputed == shortlist
    return {"query_tokens": sorted(q), "idf": retriever.idf, "rows": rows, "shortlist": shortlist}


def sanitized_call(call):
    keep = (
        "task", "requested_model", "returned_model", "status", "evidence", "result",
        "max_input", "max_output", "counted_input_tokens", "usage", "seconds",
        "count_http_status", "http_status", "cache_key", "price_date",
    )
    return {k: call[k] for k in keep if k in call}


def main():
    local, round2, limited = read("offline.local.json"), read("validation-round-2.local.json"), read("limited.local.json")
    config = read("experiment-config.local.json")["settings_without_key"]
    cases = load_corpus(DATA, fetch=False)
    assert all(r["private"] is False and r["source"] in {"PUBLIC_GITHUB", "SYNTHETIC"} for r in cases)
    concepts = registry()
    frozen = read("frozen-corpus.local.json")
    assert digest(concepts) == frozen["registry_hash"]
    assert digest(frozen) == local["corpus_hash"] == round2["corpus_hash"] == limited["corpus_hash"]
    assert digest(CLASSIFY_SYSTEM) == round2["prompt_hash"]
    assert digest(Classification.model_json_schema()) == round2["schema_hash"]
    lookup = {r["id"]: r for r in cases}
    profiles = local["profiles"]["rake"]
    records = {r["id"]: r for r in round2["records"]}
    retriever = Retriever(concepts, method=local["retrieval_choice"])
    chosen = ["synthetic/orion-api", "fastapi/fastapi", "synthetic/negated-api", "synthetic/orion-audit", "synthetic/unknown-empty"]
    traces = {}
    for key in chosen:
        repo, prof, call = lookup[key], profiles[key], records[key]["call"]
        payload, context = classification_input(repo, prof, retriever.candidates(prof), concepts)
        validate_classification(Classification.model_validate(call["result"]), context, concepts)
        effort = config["openai_classification_reasoning_effort"]
        reconstructed_key = logical_cache_key(
            call["requested_model"], call["task"], CLASSIFY_SYSTEM, payload,
            Classification, effort, call["max_input"], call["max_output"],
        )
        assert reconstructed_key == call["cache_key"], f"Logical request mismatch: {key}"
        source = {k: repo.get(k) for k in ("id", "name", "description", "topics", "language", "source", "private", "sha", "license")}
        trace = {
            "provenance": {"input": "Deterministic reconstruction, logical cache key matched to historical call", "output": "Historical observed Phase 0.5 round-2 provider result", "raw_historical_wire_capture": False},
            "source": source,
            "profile": prof,
            "retrieval": scored_candidates(prof, retriever),
            "payload": payload,
            "validation_context": context,
            "call": sanitized_call(call),
            "reasoning_effort": effort,
            "request": capture_request(call["requested_model"], CLASSIFY_SYSTEM, payload, Classification, effort, call["max_output"]),
            "expected_labels_for_evaluation_only": records[key]["gold"],
            "yake_phrases_from_saved_offline_comparison": local["profiles"]["yake"][key]["phrases"],
            "alternate_candidate_ids": {method: Retriever(concepts, method).candidates(prof) for method in ("alias", "bm25")},
        }
        traces[key] = trace
        write(key.split("/")[-1] + ".json", trace)

    call = limited["taxonomy"][0]
    taxonomy_payload = {
        "source": "PUBLIC_AND_SYNTHETIC", "private": False,
        "collection": [{"repo_id": p["id"], **compact(p)} for p in profiles.values()],
    }
    validate_taxonomy(TaxonomyDraft.model_validate(call["result"]), set(profiles))
    effort = config["openai_taxonomy_reasoning_effort"]
    assert logical_cache_key(call["requested_model"], call["task"], TAXONOMY_SYSTEM, taxonomy_payload, TaxonomyDraft, effort, call["max_input"], call["max_output"]) == call["cache_key"]
    write("taxonomy.json", {
        "provenance": {"input": "Deterministic reconstruction; logical cache key matched", "output": "Historical observed 30-repository taxonomy-limited result", "raw_historical_wire_capture": False, "not_the_seeded_classification_registry": True},
        "payload": taxonomy_payload, "system": TAXONOMY_SYSTEM,
        "schema": TaxonomyDraft.model_json_schema(), "call": sanitized_call(call),
        "reasoning_effort": effort,
        "request": capture_request(call["requested_model"], TAXONOMY_SYSTEM, taxonomy_payload, TaxonomyDraft, effort, call["max_output"]),
    })
    write("registry.json", {"provenance": "Authored approved benchmark registry, not the generated taxonomy draft", "concepts": concepts})
    write("prompts-and-schemas.json", {"classification_system": CLASSIFY_SYSTEM, "taxonomy_system": TAXONOMY_SYSTEM, "classification_schema": Classification.model_json_schema(), "taxonomy_schema": TaxonomyDraft.model_json_schema()})

    # Pure application functions replay a saved result in a new in-memory state.
    state = initial_state()
    key = "synthetic/orion-api"
    state["core"]["repos"][key] = {**lookup[key], "key": key, "unavailable": False, "decision_version": 0}
    state["organization"]["concepts"] = concepts
    state["intelligence"]["profiles"][key] = profiles[key]
    analysis.new_repository(state, key)
    lifecycle = {"provenance": "New offline in-memory application replay of a saved provider result; no live workspace writes", "before": {"admission": analysis.admission(state, key), "edges": {}}}
    fence = domain.fence(state)
    analysis.claim(state, [key], "classification", "article-offline-replay", False, "Documented in-memory example", fence)
    analysis.record(state, key, "classification", "article-offline-replay", records[key]["call"], profiles[key], fence, CLASSIFY_SYSTEM)
    lifecycle["after_analysis"] = {"status": analysis.receipt(state,key)["last_success"]["status"], "ai_analyzed": analysis.receipt(state,key)["ai_analyzed"], "edges": {k:list(edges) for k,edges in state["organization"]["edges"].items()}, "admission": analysis.admission(state,key)}
    ids = records[key]["predicted"]
    domain.mapping(state, [key], ids, "ADD", source="USER")
    lifecycle["after_simulated_user_acceptance"] = {"edges": {cid:edge["source"] for cid,edge in state["organization"]["edges"][key].items()}, "derived_domains": sorted({concepts[cid]["domain"] for cid in ids if concepts[cid]["kind"]=="PROJECT"}), "admission": analysis.admission(state,key)}
    domain.mapping(state, [key], ["p-orion"], "REMOVE")
    lifecycle["after_simulated_project_removal"] = {"remaining_ids": list(state["organization"]["edges"][key]), "protected_rejection": state["organization"]["rejections"][key]["p-orion"]["protected"], "admission": analysis.admission(state,key), "explicit_force_admission": analysis.admission(state,key,force=True)}
    assert not lifecycle["after_analysis"]["edges"]
    assert lifecycle["after_simulated_project_removal"]["admission"][0] is False
    assert lifecycle["after_simulated_project_removal"]["explicit_force_admission"][0] is True
    write("lifecycle-replay.json", lifecycle)

    names = ["offline.local.json", "validation-round-2.local.json", "limited.local.json", "experiment-config.local.json", "frozen-corpus.local.json", "public-corpus.local.json"]
    write("provenance.json", {
        "created_date": "2026-10-15", "scope": "Offline reconstruction and sanitized historical outputs; no provider requests",
        "source_files": {name:file_sha(DATA/name) for name in names},
        "baseline_corpus_hash": local["corpus_hash"],
        "logical_cache_matches": len(chosen)+1,
        "mock_serializations": len(chosen)+1,
        "real_network_calls": 0,
        "versions": {name:importlib.metadata.version(name) for name in local["versions"]},
        "historical_versions": local["versions"],
        "classification_cases": chosen,
        "taxonomy_repository_count": len(taxonomy_payload["collection"]),
        "public_source_attribution": [{"repository":r["id"],"readme_blob_sha":r["sha"],"license":r["license"]} for r in cases if r["source"]=="PUBLIC_GITHUB"],
        "excluded_from_call_exports": ["authorization headers", "API keys", "request_id", "response_id", "reservation IDs"],
        "limits": ["The original serialized HTTP bodies were not retained; current-library bodies are reconstructions", "Taxonomy discovery and seeded classification are separate experiments", "In-memory acceptance/removal is a new illustrative replay, not historical user activity"],
    })
    print(json.dumps({"status":"PASS","logical_request_matches":len(chosen)+1,"taxonomy_repositories":len(profiles),"real_network_calls":0,"mock_serializations":len(chosen)+1,"output":str(OUT.relative_to(ROOT))}))


if __name__ == "__main__":
    main()
