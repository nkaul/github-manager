"""Frozen, source-bound evaluation of the actual reviewed repositories."""

import argparse
import hashlib
import json
import sqlite3
import sys
import time
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "eval/relocation"))
from relocation_support import historical_bytes, historical_sha256, repo_path
sys.path.insert(0, str(ROOT / "backend"))

from app.demo.corpus import Corpus
from app.demo.evidence import build_profile
from app.pretest.ai.chains import CLASSIFY_SYSTEM, TAXONOMY_SYSTEM, classification_input
from app.pretest.ai.evidence import Retriever
from app.pretest.ai.schemas import Classification, TaxonomyDraft
from app.pretest.ai.storage import digest, private_json
from scoring import score

DATA = ROOT / "docs/validation/private/corpus-600-v2"
OUT = DATA / "evaluation-reviewed-30-v1"


def read(path):
    return json.loads(Path(path).read_text())


def save(name, value):
    private_json(OUT / name, value)


def source_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stable(value):
    return hashlib.sha256(("reviewed-30-v1:" + str(value)).encode()).hexdigest()


def corpus():
    value = Corpus(ROOT, DATA / "release", None)
    value.load()
    return value


def repo_input(c, rid):
    d = c.dossier(rid)
    text = c.source(rid, d["readme"]["path"])["text"]
    repo = {
        "key": str(rid),
        "id": str(rid),
        "name": d["full_name"],
        "description": d.get("description") or "",
        "topics": d.get("native_topics", []),
        "language": d.get("primary_language"),
        "readme_sha": d["readme"]["git_blob_sha"],
        "sha": d["readme"]["git_blob_sha"],
        "source": "PUBLIC_GITHUB",
        "private": False,
        "policy_verified": True,
    }
    return repo, text


def freeze():
    if (OUT / "manifest.json").exists():
        verify()
        print("Existing immutable reference verified; no resnapshot.")
        return
    c = corpus()
    dbpath = ROOT / "docs/validation/private/demo/app.sqlite3"
    with sqlite3.connect(f"{dbpath.as_uri()}?mode=ro", uri=True) as db:
        states = [json.loads(row[0]) for row in db.execute("SELECT state FROM workspace")]
    matches = [s for s in states if s.get("reference_reviews", {}).get(c.manifest["release_id"])]
    if len(matches) != 1:
        raise ValueError("Select one explicit review owner; do not combine owners automatically")
    state = matches[0]
    view = c.registry_adapter().export(state)
    effective = c.registry_adapter().view(state)
    registry = {item["id"]: item for item in effective["registry"]}
    records = state["reference_reviews"][c.manifest["release_id"]]
    confirmed = {rid: r for rid, r in records.items() if r["status"] == "HUMAN_CONFIRMED"}
    if len(confirmed) != 30:
        raise ValueError(
            "Reviewed set changed from approved thirty-case scope; inspect before freezing"
        )
    ranker = Retriever(registry, "tfidf")
    cases, profiles, inputs = {}, {}, {}
    for rid in sorted(confirmed, key=stable):
        review = confirmed[rid]
        inv = c.inventory[int(rid)]
        if (
            review["manifest_sha256"] != c._manifest_hash
            or review["proposal_sha256"] != digest(c.proposals[int(rid)])
            or review["commit"] != inv["commit"]
        ):
            raise ValueError("Stale reference source binding")
        historical = c.registry_adapter().view(
            state, (review.get("registry_context") or {}).get("revision", 0)
        )
        ids = {i["id"] for i in historical["registry"]}
        if not set(review["label_ids"]) <= ids or not all(review["dimensions"].values()):
            raise ValueError("Invalid human reference IDs or acknowledgements")
        repo, text = repo_input(c, int(rid))
        prof = build_profile(repo, text)
        candidates = ranker.candidates(prof)
        payload, context = classification_input(
            repo,
            prof,
            candidates,
            registry,
            revision=effective["registry_context"]["revision"],
        )
        cases[rid] = {
            "id": rid,
            "name": inv["full_name"],
            "split": inv["split"],
            "group": inv["group"],
            "sampling_domain": inv["sampling_domain"],
            "commit": inv["commit"],
            "positive_ids": review["label_ids"],
            "explicit_negative_ids": [],
            "candidate_ids": candidates,
            "source_path": c.dossier(int(rid))["readme"]["local_path"],
            "repo": repo,
            "review": review,
            "historical_registry_context": historical["registry_context"],
        }
        profiles[rid] = prof
        inputs[rid] = {"payload": payload, "context": context}
    dev = [rid for rid in cases if cases[rid]["split"] == "development"]
    test = [rid for rid in cases if cases[rid]["split"] == "test_reserved"]
    if (
        len(dev) != 15
        or len(test) != 15
        or {cases[i]["group"] for i in dev} & {cases[i]["group"] for i in test}
    ):
        raise ValueError("Approved group/split scope changed")
    # Diversify comparison by sampling bucket, then deterministic hash; never labels.
    buckets = defaultdict(list)
    for rid in dev:
        buckets[cases[rid]["sampling_domain"]].append(rid)
    comparison = []
    while len(comparison) < 6:
        for domain in sorted(buckets):
            if buckets[domain] and len(comparison) < 6:
                comparison.append(buckets[domain].pop(0))
    config = {
        "client_date": "2026-10-19",
        "approved": True,
        "run_id": "reviewed-30-v1-2026-10-19",
        "release_id": c.manifest["release_id"],
        "release_manifest_sha256": c._manifest_hash,
        "registry_context": effective["registry_context"],
        "primary_model": "gpt-6-luna",
        "comparison_model": "gpt-6.1-sol",
        "taxonomy_model": "gpt-6.1-sol",
        "judge_model": "gpt-6.1-sol",
        "development": dev,
        "test_reserved": test,
        "comparison": comparison,
        "judge_cases": dev[:4],
        "limits": {
            "usd": 1.0,
            "cumulative_usd": 5.0,
            "http": 100,
            "generations": 50,
            "batch_http": 20,
            "classification_input": 2000,
            "classification_output": 2048,
            "taxonomy_input": 12000,
            "taxonomy_output": 4096,
            "judge_input": 3000,
            "judge_output": 1024,
        },
        "classify_system": CLASSIFY_SYSTEM,
        "taxonomy_system": TAXONOMY_SYSTEM,
        "classification_schema": Classification.model_json_schema(),
        "taxonomy_schema": TaxonomyDraft.model_json_schema(),
        "created_at": datetime.now(UTC).isoformat(),
        "unlisted_labels": "UNKNOWN_NOT_NEGATIVE",
    }
    OUT.mkdir(parents=True, exist_ok=True, mode=0o700)
    for name, data in {
        "reference-snapshot.json": cases,
        "registry.json": registry,
        "registry-history.json": view,
        "profiles.json": profiles,
        "classification-inputs.json": inputs,
        "config.json": config,
    }.items():
        private_json(OUT / name, data, exclusive=True)
    producer = [
        ROOT / "backend/app/demo/evidence.py",
        ROOT / "backend/app/pretest/ai/evidence.py",
        ROOT / "backend/app/pretest/ai/chains.py",
        ROOT / "backend/app/pretest/ai/schemas.py",
        HERE / "scoring.py",
    ]
    manifest = {
        "files": {
            name: source_hash(OUT / name)
            for name in (
                "reference-snapshot.json",
                "registry.json",
                "registry-history.json",
                "profiles.json",
                "classification-inputs.json",
                "config.json",
            )
        },
        "producer_files": {str(p.relative_to(ROOT)): source_hash(p) for p in producer},
        "scope": "Single-reviewer positives, historical per-review vocabulary, current v2 producer registry; no exhaustive negatives.",
    }
    private_json(OUT / "manifest.json", manifest, exclusive=True)
    print(
        json.dumps(
            {
                "frozen": len(cases),
                "positives": sum(len(r["positive_ids"]) for r in cases.values()),
                "development": len(dev),
                "test_reserved": len(test),
                "registry": len(registry),
            }
        )
    )


def verify():
    manifest = read(OUT / "manifest.json")
    for name, expected in manifest["files"].items():
        if source_hash(OUT / name) != expected:
            raise ValueError("Frozen evaluation input modified: " + name)
    for name, expected in manifest["producer_files"].items():
        if source_hash(repo_path(name)) != expected:
            raise ValueError("Producer changed after freeze: " + name)
    c = corpus()
    if c._manifest_hash != read(OUT / "config.json")["release_manifest_sha256"]:
        raise ValueError("Corpus release modified after freeze")


def offline(all_corpus=False):
    verify()
    cases, registry = read(OUT / "reference-snapshot.json"), read(OUT / "registry.json")
    profiles = read(OUT / "profiles.json")
    comparisons = {}
    for method in ("alias", "tfidf", "bm25"):
        retriever = Retriever(registry, method)
        rows = []
        for rid, case in cases.items():
            rows.append({**case, "candidate_ids": retriever.candidates(profiles[rid])})
        comparisons[method] = score(rows, registry)
        comparisons[method + "_expanded"] = score(
            [
                {
                    **case,
                    "candidate_ids": retriever.candidates(profiles[rid], expanded=True),
                }
                for rid, case in cases.items()
            ],
            registry,
        )
    visibility = Counter()
    for rid in cases:
        prof = profiles[rid]
        payload = read(OUT / "classification-inputs.json")[rid]["payload"]
        visibility["profile_evidence_characters"] += sum(len(e["text"]) for e in prof["evidence"])
        visibility["request_evidence_characters"] += sum(
            len(e["text"]) for e in payload["evidence"]
        )
        visibility["logical_request_utf8_bytes"] += len(
            json.dumps(payload, ensure_ascii=False).encode()
        )
    result = {
        "scope": "Recall of reviewed positive IDs; no generation or exhaustive precision/F1",
        "repositories": len(cases),
        "rankers": comparisons,
        "sizes": dict(visibility),
        "paid_api_calls": 0,
    }
    save("local-results.json", result)
    # Optional broad operational diagnostics never use unreviewed labels as gold.
    if all_corpus:
        c = corpus()
        diagnostic = []
        started = time.monotonic()
        ranker = Retriever(registry, "tfidf")
        for rid in c.inventory:
            try:
                repo, text = repo_input(c, rid)
                p = build_profile(repo, text)
                diagnostic.append(
                    {
                        "id": rid,
                        "status": "PASS",
                        "candidate_count": len(ranker.candidates(p)),
                        "evidence_count": len(p["evidence"]),
                        "profile_hash": p["hash"],
                    }
                )
            except (ValueError, OSError) as e:
                diagnostic.append({"id": rid, "status": "EXCLUDED", "reason": str(e)[:200]})
        save(
            "corpus-diagnostics.json",
            {
                "seconds": time.monotonic() - started,
                "counts": dict(Counter(r["status"] for r in diagnostic)),
                "records": diagnostic,
                "human_accuracy_claim": False,
            },
        )
    print(
        json.dumps(
            {
                method: {
                    kind: {
                        "found": value["retrieved_positives"],
                        "positive": value["reviewed_positives"],
                        "recall": value["candidate_recall_of_reviewed_positives"],
                    }
                    for kind, value in kinds.items()
                }
                for method, kinds in comparisons.items()
            },
            indent=2,
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["freeze", "offline"])
    parser.add_argument("--all-corpus", action="store_true")
    args = parser.parse_args()
    freeze() if args.stage == "freeze" else offline(args.all_corpus)


if __name__ == "__main__":
    main()
