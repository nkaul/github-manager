import argparse
import importlib.metadata
import json
import time

from app.config import REPO_ROOT
from app.pretest.ai.chains import classify, taxonomy
from app.pretest.ai.corpus import load_corpus, registry
from app.pretest.ai.evaluation import candidate_recall, corpus_groups, metrics, percentiles
from app.pretest.ai.evidence import Retriever, document_frequency, profile
from app.pretest.ai.limited import limited_checks
from app.pretest.ai.provider import BudgetedProvider
from app.pretest.ai.reporting import consolidate
from app.pretest.ai.schemas import AccessProbe
from app.pretest.ai.settings import AISettings
from app.pretest.ai.storage import Ledger, digest, private_json
from app.pretest.report import cell, write_report


def freeze(directory, cases, concepts):
    manifest = {
        "version": "phase05-v1",
        "registry_hash": digest(concepts),
        "cases": [
            {k: case[k] for k in ("id", "source", "sha", "split", "labels", "label_review")}
            | {
                "metadata_hash": digest(
                    {k: case[k] for k in ("name", "description", "topics", "language")}
                )
            }
            for case in cases
        ],
    }
    path = directory / "frozen-corpus.local.json"
    if path.exists():
        if json.loads(path.read_text()) != manifest:
            raise ValueError("Frozen corpus changed; do not tune held-out references silently")
    else:
        private_json(path, manifest, exclusive=True)
    return digest(manifest)


def reference_sheet(cases, concepts, corpus_hash):
    path = REPO_ROOT / "docs/validation/phase-0-5-reference-review.md"
    if path.exists():
        return
    lines = [
        "# Phase 0.5 reference review",
        "",
        "Status: **PROVISIONAL — human review pending.**",
        "",
        f"Frozen corpus hash: `{corpus_hash}`.",
        "",
        "Public labels are implementer-proposed minimum expected labels, not model-generated "
        "truth. Review evidence and correct the expected sets before a quality PASS. Synthetic "
        "cases have authored expected outcomes. Models never see labels. Related repos are "
        "kept in the same split. No project is expected for public libraries solely because "
        "they share an owner/framework.",
        "",
        "| Case | Split/source | Proposed expected concepts |",
        "|---|---|---|",
    ]
    for repo in cases:
        name = repo.get("canonical_name", repo["id"])
        link = f"[{name}](https://github.com/{name})" if repo["source"] == "PUBLIC_GITHUB" else name
        labels = ", ".join(concepts[i]["name"] for i in repo["labels"]) or "NO_MATCH"
        lines.append(f"| {link} | {repo['split']} / {repo['source']} | {cell(labels)} |")
    lines += [
        "",
        "## Registry semantics",
        "",
        "Projects represent initiatives; topics describe capabilities; tags describe "
        "technologies. Domains derive through project membership. One repository can have "
        "multiple projects. Orion/Helios/Atlas/Meridian are authored synthetic initiatives. "
        "The other project entries are distractors for lexical retrieval. Negated-api names "
        "Helios/Orion but explicitly excludes membership.",
        "",
        "Review actions: confirm/correct public expected sets and registry semantics; "
        "then review the eventual taxonomy drafts using relevance, support, hierarchy, "
        "alias/distinctness and logical grouping (1–5 each). An algorithm/model cannot "
        "approve its own reference labels or assign a human rubric score.",
    ]
    path.write_text("\n".join(lines) + "\n")


def offline(settings, cases, concepts, corpus_hash):
    directory = settings.ai_pretest_state_directory
    profiles, times = {}, {}
    for extractor in ("rake", "yake"):
        started = time.monotonic()
        profiles[extractor] = {repo["id"]: profile(repo, extractor) for repo in cases}
        times[extractor] = round(time.monotonic() - started, 3)
    retrieval = {}
    for method in ("alias", "tfidf", "bm25"):
        retriever = Retriever(concepts, method)
        candidate_sets = {r["id"]: retriever.candidates(profiles["rake"][r["id"]]) for r in cases}
        expanded_sets = {
            r["id"]: retriever.candidates(profiles["rake"][r["id"]], expanded=True) for r in cases
        }
        retrieval[method] = {
            split: candidate_recall(
                [r for r in cases if r["split"] == split], candidate_sets, concepts
            )
            for split in ("dev", "heldout")
        } | {
            "expanded_heldout": candidate_recall(
                [r for r in cases if r["split"] == "heldout"], expanded_sets, concepts
            )
        }
    # Select only from development labels. Stable tie-break prefers the simpler TF-IDF baseline.
    choice = max(
        ("tfidf", "bm25"),
        key=lambda m: sum((v["recall"] or 0) for v in retrieval[m]["dev"].values()),
    )
    result = {
        "corpus_hash": corpus_hash,
        "profiles": profiles,
        "extraction_seconds": times,
        "retrieval": retrieval,
        "retrieval_choice": choice,
        "document_frequency": document_frequency(list(profiles["rake"].values())),
        "groups": corpus_groups(cases),
        "label_review": "PENDING",
        "counts": {"public": 10, "synthetic": 20, "dev": 10, "heldout": 20},
        "versions": {
            name: importlib.metadata.version(name)
            for name in (
                "langchain-openai",
                "langchain-core",
                "openai",
                "rake-nltk",
                "rank-bm25",
                "markdown-it-py",
                "nltk",
                "numpy",
            )
        },
    }
    private_json(directory / "offline.local.json", result)
    rows = [
        {
            "check": f"{name.upper()} extraction",
            "evidence": "LOCAL_ALGORITHM",
            "status": "PASS",
            "detail": f"30 profiles; {elapsed}s; no tokenizer downloads",
        }
        for name, elapsed in times.items()
    ]
    for method, values in retrieval.items():
        for kind, item in values["heldout"].items():
            rows.append(
                {
                    "check": f"{method} held-out {kind} candidate recall",
                    "evidence": "LOCAL_ALGORITHM",
                    "status": "MEASURED",
                    "detail": f"{item['found']}/{item['gold']}; human reference review pending",
                }
            )
    path = write_report(
        directory,
        "ai-offline",
        "Phase 0.5 offline algorithm results",
        rows,
        [
            f"Corpus hash: {corpus_hash}",
            f"Development retrieval choice: {choice}",
            "Labels provisional; measured retrieval is not a final quality PASS.",
        ],
    )
    private_json(path.with_suffix(".local.json"), result)
    reference_sheet(cases, concepts, corpus_hash)
    return result, path


def access(provider, settings):
    results = []
    for model in settings.models:
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
        results.append(result)
        print(
            json.dumps(
                {
                    "stage": "access",
                    "model": model,
                    "status": result["status"],
                    "code": result.get("provider_error_code"),
                }
            ),
            flush=True,
        )
    private_json(settings.ai_pretest_state_directory / "access.local.json", results)
    return results


def fail_access():
    raise ValueError("Unexpected access probe result")


def benchmark(provider, settings, cases, concepts, local, accesses):
    allowed = {r["requested_model"] for r in accesses if r["status"] == "PASS"}
    profiles = local["profiles"]["rake"]
    heldout = [r for r in cases if r["split"] == "heldout"]
    retriever = Retriever(concepts, local["retrieval_choice"])
    output = {
        "taxonomy": [],
        "classification": {},
        "ablations": [],
        "stability": [],
        "blocked_models": [m for m in settings.models if m not in allowed],
        "corpus_hash": local["corpus_hash"],
        "label_review": "PENDING",
    }
    for model in dict.fromkeys(
        [settings.openai_taxonomy_model, settings.openai_taxonomy_comparison_model]
    ):
        if model not in allowed:
            output["taxonomy"].append(
                {
                    "requested_model": model,
                    "status": "BLOCKED",
                    "reason": "Access gate failed; no taxonomy call attempted",
                }
            )
            continue
        groups = list(corpus_groups(cases).values())
        grouped = {ident for group in groups for ident in group}
        groups.extend([[repo["id"]] for repo in cases if repo["id"] not in grouped])
        batches = [[], []]
        for group in sorted(groups, key=lambda values: -len(values)):
            target = min(batches, key=len)
            target.extend(profiles[ident] for ident in group)
        drafts = []
        for index, batch in enumerate(batches):
            result = taxonomy(provider, model, batch, task=f"taxonomy-batch-{index}")
            output["taxonomy"].append(result)
            if result["status"] == "PASS":
                drafts.append(result["result"])
        if len(drafts) == len(batches):
            output["taxonomy"].append(
                taxonomy(
                    provider,
                    model,
                    list(profiles.values()),
                    task="taxonomy-consolidation",
                    proposals=drafts,
                )
            )
    for model in dict.fromkeys(
        [settings.openai_classification_model, settings.openai_classification_comparison_model]
    ):
        if model not in allowed:
            output["classification"][model] = {"status": "BLOCKED", "records": [], "metrics": None}
            continue
        records, calls = [], []
        for repo in heldout:
            prof = profiles[repo["id"]]
            candidates = retriever.candidates(prof)
            result = classify(provider, model, repo, prof, candidates, concepts)
            calls.append(result)
            if result["status"] == "PASS" and result["result"]["status"] == "NEEDS_MORE_CONTEXT":
                candidates = retriever.candidates(prof, expanded=True)
                result = classify(
                    provider,
                    model,
                    repo,
                    prof,
                    candidates,
                    concepts,
                    task="classification-expanded",
                )
                calls.append(result)
            predicted = [a["concept_id"] for a in result.get("result", {}).get("assignments", [])]
            records.append(
                {
                    "id": repo["id"],
                    "source": repo["source"],
                    "gold": repo["labels"],
                    "predicted": predicted,
                    "call": result,
                }
            )
            print(
                json.dumps(
                    {
                        "stage": "classification",
                        "model": model,
                        "case": repo["id"],
                        "status": result["status"],
                    }
                ),
                flush=True,
            )
            if result["status"] == "BLOCKED":
                break
        output["classification"][model] = {
            "status": "MEASURED_PROVISIONAL",
            "records": records,
            "metrics": metrics(records, concepts),
            "by_source": {
                source: metrics([r for r in records if r["source"] == source], concepts)
                for source in ("PUBLIC_GITHUB", "SYNTHETIC")
            },
            "latency": percentiles(
                [c["seconds"] for c in calls if c["evidence"] == "LIVE_PROVIDER"]
            ),
        }
    # Small development ablation and repeat subset; no full Cartesian product.
    model = settings.openai_classification_model
    if model in allowed:
        for repo in [r for r in cases if r["split"] == "dev"][:3]:
            for representation in ("baseline", "rake", "yake"):
                prof = local["profiles"]["yake" if representation == "yake" else "rake"][repo["id"]]
                result = classify(
                    provider,
                    model,
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
        for repo in heldout[:2]:
            prof = profiles[repo["id"]]
            result = classify(
                provider, model, repo, prof, retriever.candidates(prof), concepts, fresh=True
            )
            output["stability"].append({"id": repo["id"], "call": result})
    private_json(settings.ai_pretest_state_directory / "benchmark.local.json", output)
    return output


def report(directory, ledger, results, *, stage):
    rows = []
    accesses = results.get("access", [])
    for result in accesses:
        rows.append(
            {
                "check": result["requested_model"] + " strict-schema access",
                "evidence": result["evidence"],
                "status": result["status"],
                "detail": result.get("provider_error_code") or "Structured generation completed",
            }
        )
    benchmark_result = results.get("benchmark", {})
    limited = results.get("limited", {})
    review_path = directory / "quality-review.local.json"
    quality_reviewed = review_path.exists() and json.loads(review_path.read_text()).get(
        "taxonomy_and_extraction_qualitative_acceptance"
    )
    for task in ("taxonomy", "classification"):
        blocked = benchmark_result.get("blocked_models", [])
        rows.append(
            {
                "check": task + " quality",
                "evidence": "LIVE_PROVIDER / HUMAN_REVIEW",
                "status": (
                    ("HUMAN_QUALITATIVE_ACCEPTED" if quality_reviewed else "HUMAN_REVIEW_PENDING")
                    if task == "taxonomy"
                    else "PARTIAL_SUBSET"
                )
                if limited
                else ("BLOCKED" if blocked else "NOT_TESTED"),
                "detail": (
                    "Limited API outcomes recorded; quality/full coverage remain open"
                    if limited
                    else ("Model access blocked" if blocked else "Requires measured/human review")
                ),
            }
        )
    rows.append(
        {
            "check": "Experiment-wide spending",
            "evidence": "LOCAL_LEDGER",
            "status": "PASS",
            "detail": str(ledger.summary()),
        }
    )
    path = write_report(
        directory,
        "ai",
        f"Phase 0.5 {stage} report",
        rows,
        [
            "Public/synthetic data only. No automatic publication or GitHub writes.",
            "Reference approval recorded separately; taxonomy/extraction rubric remains pending.",
        ],
    )
    private_json(path.with_suffix(".local.json"), results)
    consolidate(directory, ledger)
    return path


def main():
    parser = argparse.ArgumentParser(description="Local Phase 0.5 AI readiness checks")
    parser.add_argument(
        "--stage", choices=["offline", "access", "benchmark", "limited", "report"], required=True
    )
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--fetch-public", action="store_true")
    parser.add_argument(
        "--init", action="store_true", help="One-time explicit budget initialization"
    )
    args = parser.parse_args()
    settings = AISettings()
    directory = settings.ai_pretest_state_directory
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        ledger = Ledger(directory, settings.ai_pretest_budget_usd, initialize=args.init)
    except Exception as error:
        path = write_report(
            directory,
            "ai",
            "Phase 0.5 budget gate blocked",
            [
                {
                    "check": "durable spending state",
                    "evidence": "LOCAL_LEDGER",
                    "status": "BLOCKED",
                    "detail": type(error).__name__,
                }
            ],
            ["No provider call attempted. Missing/corrupt state must not reset the allowance."],
        )
        print(json.dumps({"status": "BLOCKED", "report": str(path)}))
        return 2
    results, provider = {}, None
    try:
        if args.stage == "offline":
            cases = load_corpus(directory, fetch=args.fetch_public)
            concepts = registry()
            corpus_hash = freeze(directory, cases, concepts)
            results["offline"], path = offline(settings, cases, concepts, corpus_hash)
            consolidate(directory, ledger)
        else:
            access_path = directory / "access.local.json"
            results["access"] = json.loads(access_path.read_text()) if access_path.exists() else []
            if args.stage in {"access", "benchmark", "limited"}:
                settings.require_live(args.live)
                provider = BudgetedProvider(settings, ledger)
                if args.stage == "limited":
                    cases, concepts = load_corpus(directory), registry()
                    freeze(directory, cases, concepts)
                    local = json.loads((directory / "offline.local.json").read_text())
                    results["limited"] = limited_checks(provider, settings, cases, concepts, local)
                    results["access"] = results["limited"]["access"]
                elif args.stage == "access" or not results["access"]:
                    results["access"] = access(provider, settings)
                if args.stage == "benchmark":
                    cases, concepts = load_corpus(directory), registry()
                    freeze(directory, cases, concepts)
                    local = json.loads((directory / "offline.local.json").read_text())
                    results["benchmark"] = benchmark(
                        provider, settings, cases, concepts, local, results["access"]
                    )
            elif (directory / "limited.local.json").exists():
                results["limited"] = json.loads((directory / "limited.local.json").read_text())
            elif (directory / "benchmark.local.json").exists():
                results["benchmark"] = json.loads((directory / "benchmark.local.json").read_text())
            path = report(directory, ledger, results, stage=args.stage)
        print(json.dumps({"report": str(path), "budget": ledger.summary()}), flush=True)
    except Exception as error:
        path = write_report(
            directory,
            "ai",
            "Phase 0.5 blocked/failed run",
            [
                {
                    "check": args.stage,
                    "evidence": "LOCAL_RUNNER",
                    "status": "BLOCKED",
                    "detail": type(error).__name__,
                }
            ],
            ["Error details suppressed to avoid credential/content disclosure."],
        )
        print(
            json.dumps(
                {
                    "status": "BLOCKED",
                    "error_type": type(error).__name__,
                    "report": str(path),
                    "budget": ledger.summary(),
                }
            )
        )
        return 1
    finally:
        if provider:
            provider.close()
    if args.stage in {"access", "benchmark", "limited"} and any(
        result["status"] != "PASS" for result in results.get("access", [])
    ):
        return 2
    if args.stage == "limited":
        limited = results["limited"]
        calls = limited["access"] + limited["taxonomy"]
        calls += [
            r["call"] for value in limited["classification"].values() for r in value["records"]
        ]
        calls += [r["call"] for r in limited["ablations"] + limited["stability"]]
        if len(calls) != 10 or any(result["status"] != "PASS" for result in calls):
            return 2
    return 0
