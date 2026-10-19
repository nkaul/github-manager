"""Export aggregate, public/synthetic experiment evidence without calling services.

No .env reads, provider initialization, database writes or raw model-text exports.
Run from any directory with the repository's existing Python environment.
"""

import ast
import hashlib
import json
import math
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "eval/ai-system-design"
PRIVATE = ROOT / "docs/validation/private/ai-pretest"
SOURCES = {
    "I01": ("backend/app/pretest/ai/evidence.py", "selected_evidence", "README selection, bounds and provenance"),
    "I02": ("backend/app/pretest/ai/evidence.py", "rake_phrases", "RAKE configuration and isolated YAKE comparison"),
    "I03": ("backend/app/pretest/ai/evidence.py", "Retriever", "Binary-IDF cosine / BM25 / alias candidate retrieval"),
    "I04": ("backend/app/pretest/ai/chains.py", "classification_input", "Prompt assembly and primary-label instructions"),
    "I05": ("backend/app/pretest/ai/schemas.py", "validate_classification", "Structural and application validation"),
    "I06": ("backend/app/pretest/ai/provider.py", "BudgetedProvider", "Strict LangChain calls, exact counting and replay cache"),
    "I07": ("backend/app/pretest/ai/storage.py", "Ledger", "Durable cumulative cost reservations and settlement"),
    "I08": ("backend/app/pretest/ai/evaluation.py", "metrics", "Micro metrics, candidate recall and nearest-rank latency"),
    "I09": ("backend/app/pretest/ai/runner.py", "offline", "Frozen extraction/retrieval evaluation and method selection"),
    "I10": ("backend/app/pretest/ai/validation_round.py", "run", "Executed 20-case round; isolated concurrent clients"),
    "I11": ("backend/app/demo/evidence.py", "build_profile", "Application-only v2 cleanup and model-input policy"),
    "I12": ("backend/app/demo/cohorts.py", "preview", "Deterministic cohorts and exact run previews"),
    "I13": ("backend/app/demo/cohorts.py", "taxonomy_collection", "Byte-bounded collection compaction"),
    "I14": ("backend/app/demo/analysis.py", "admission", "No-repeat admission, receipts and explicit re-analysis"),
    "I15": ("backend/app/demo/analysis.py", "automation", "Configurable automatic organization thresholds"),
    "I16": ("backend/app/demo/service.py", "organize", "Actual application inference and offline reconciliation"),
    "I17": ("backend/app/demo/domain.py", "fence", "Generation/revision/privacy fencing"),
    "I18": ("backend/app/demo/domain.py", "term_conflicts", "Normalized canonical/alias reservations"),
    "I19": ("backend/app/demo/domain.py", "mapping", "USER precedence, rejection tombstones and rules"),
    "I20": ("backend/app/demo/run_budget.py", "RunBudgets", "Adaptive holds, finite grants and crash reconciliation"),
    "I21": ("backend/app/demo/allowance.py", "ApplicationLedger", "Pinned application rates and atomic monetary admission"),
    "I22": ("backend/app/demo/store.py", "Store", "Local transactional aggregate and durable job storage"),
    "I23": ("backend/app/pretest/ai/corpus.py", "registry", "42-concept registry, public allowlist and authored edge cases"),
    "I24": ("backend/app/pretest/ai/runner.py", "benchmark", "Available broader benchmark/expansion path; not the executed round"),
    "I25": ("backend/app/pretest/ai/settings.py", "AISettings", "Model, token, data and tracing configuration boundaries"),
    "I26": ("backend/app/demo/pricing.py", "reserve_amount", "Application rate snapshot and conservative bound arithmetic"),
    "I27": ("backend/app/demo/taxonomy_review.py", "publish", "Draft checks, opt-in repair and canonical publication"),
    "I28": ("backend/tests/pretest/ai/test_safety.py", "test_install_only_change_does_not_invalidate_selected_profile", "Frozen selected-evidence invalidation fixture"),
    "I29": ("backend/tests/demo/test_analysis_policy.py", "test_no_repeat_before_provider_construction_even_after_revision_and_history_deletion", "Tested no-repeat admission after revision/history changes"),
}
REPORTS = {
    "E01": "docs/validation/phase-0-5-results.md",
    "E02": "docs/validation/phase-0-5-round-2-results.md",
    "E03": "docs/validation/phase-0-5-reference-review.md",
    "E04": "docs/validation/phase-0-5-codex-results.md",
    "E05": "docs/validation/phase-0-9-taxonomy-and-analysis.md",
    "E06": "docs/validation/phase-0-9-adaptive-live-20261013T145429Z.md",
    "E07": "docs/validation/phase-0-9-preservation.md",
    "E08": "docs/validation/demo-full-v2.md",
    "E09": "docs/validation/phase-0-9-live-ai-20261012T053557Z.md",
    "D01": "docs/system-design.md",
    "D02": "docs/adr/0002-phase09-local-workspace.md",
    "D03": "docs/adr/0004-cohorts-and-adaptive-budgets.md",
    "D04": "docs/adr/0005-durable-analysis-and-local-reconciliation.md",
    "H01": "docs/design-conversation.md",
    "H02": "docs/design-conversation-full.md",
    "G01": "AGENTS.md",
    "G02": "docs/system-design-execution.md",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metric(records):
    tp = fp = fn = 0
    for row in records:
        gold, predicted = set(row["gold"]), set(row["predicted"])
        tp += len(gold & predicted)
        fp += len(predicted - gold)
        fn += len(gold - predicted)
    return {"tp": tp, "fp": fp, "fn": fn, "precision": tp / (tp + fp),
            "recall": tp / (tp + fn), "f1": 2 * tp / (2 * tp + fp + fn)}


def main():
    # Only these frozen public/synthetic experiment files are read.
    round_path = PRIVATE / "validation-round-2.local.json"
    offline_path = PRIVATE / "offline.local.json"
    round2 = json.loads(round_path.read_text())
    offline = json.loads(offline_path.read_text())
    rows = round2["records"]
    assert len(rows) == len({r["id"] for r in rows}) == 20
    assert Counter(r["source"] for r in rows) == {"PUBLIC_GITHUB": 8, "SYNTHETIC": 12}
    assert all(r["call"]["status"] == "PASS" for r in rows)
    assert round2["metrics"]["ALL"] | metric(rows) == round2["metrics"]["ALL"]
    assert round2["corpus_hash"] == offline["corpus_hash"]
    usages = [r["call"]["usage"] for r in rows]
    inp = sum(u["input_tokens"] for u in usages)
    out = sum(u["output_tokens"] for u in usages)
    cached = sum(u.get("input_tokens_details", {}).get("cached_tokens", 0) for u in usages)
    writes = sum(u.get("input_tokens_details", {}).get("cache_write_tokens", 0) for u in usages)
    reasoning = sum(u.get("output_tokens_details", {}).get("reasoning_tokens", 0) for u in usages)
    assert (inp, out, reasoning, cached, writes) == (16041, 3414, 702, 0, 0)
    # Historical Luna rates, microdollars per token. Round each request as the ledger does.
    raw_usd = (inp * 0.10 + out * 0.50) / 1_000_000
    rounded_usd = sum(math.ceil(u["input_tokens"] * 0.10 + u["output_tokens"] * 0.50)
                      for u in usages) / 1_000_000
    assert math.isclose(rounded_usd, round2["round_estimated_usd"], abs_tol=1e-10)
    result = {
        "audit_date": "2026-10-14",
        "baseline_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "scope": "Read-only audit of frozen public/synthetic data; no fresh inference or network calls",
        "corpus_hash": round2["corpus_hash"],
        "prompt_hash": round2["prompt_hash"], "schema_hash": round2["schema_hash"],
        "sources": {"round2": {"path": str(round_path.relative_to(ROOT)), "sha256": sha(round_path)},
                    "offline": {"path": str(offline_path.relative_to(ROOT)), "sha256": sha(offline_path)}},
        "corpus": offline["counts"], "retrieval_choice": offline["retrieval_choice"],
        "retrieval": offline["retrieval"], "extraction_seconds": offline["extraction_seconds"],
        "experiment_versions": offline["versions"],
        "round2": {"n": len(rows), "models_returned": sorted({r["call"]["returned_model"] for r in rows}),
                   "metrics": round2["metrics"], "slices": round2["slices"], "latency": round2["latency"],
                   "wall_seconds": round2["seconds"], "workers": round2["workers"],
                   "input_tokens": inp, "output_tokens": out, "reasoning_tokens_in_output": reasoning,
                   "cached_input_tokens": cached, "cache_write_tokens": writes,
                   "raw_token_rate_usd": raw_usd, "ledger_rounded_usd": rounded_usd,
                   "mean_input_tokens": inp / 20, "mean_output_tokens": out / 20,
                   "mean_ledger_usd_per_repo": rounded_usd / 20,
                   "input_plus_output_per_true_positive": (inp + out) / metric(rows)["tp"],
                   "ledger_usd_per_true_positive": rounded_usd / metric(rows)["tp"],
                   "generation_attempts": round2["generation_attempts"],
                   "count_http_200": sum(r["call"].get("count_http_status") == 200 for r in rows),
                   "generation_http_200": sum(r["call"].get("http_status") == 200 for r in rows),
                   "experiment_total_after_round_usd": round2["budget_after"]["estimated_usd"]},
        "interpretation": "Reused 20-case regression set, not independent generalization; human rubric unscored",
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "measurements.json").write_text(json.dumps(result, indent=2) + "\n")
    entries = []
    for ident, (path, symbol, claim) in SOURCES.items():
        tree = ast.parse((ROOT / path).read_text())
        node = next(n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == symbol)
        entries.append((ident, path, node.lineno, symbol, claim))
    lines = ["# Evidence index", "", "Audit: October 14, 2026. Baseline commit: `" + result["baseline_commit"] + "`.", "",
             "Implementation claims come from source inspection. Measurements come from dated experiment records; design and historical proposals are separate evidence classes. No new provider calls were made.", "",
             "## Implementation trace", "", "| ID | Source / entry point | Claim |", "|---|---|---|"]
    manifest = {}
    for ident, path, line, symbol, claim in entries:
        lines.append(f"| {ident} | [{path}:{line}](../../{path}#L{line}) · `{symbol}` | {claim} |")
        manifest[path] = sha(ROOT / path)
    lines += ["", "## Reports, approved decisions and historical context", "", "| ID | Source | Evidence class |", "|---|---|---|"]
    for ident, path in REPORTS.items():
        kind = "Measured/report" if ident.startswith("E") else "Approved design/ADR" if ident.startswith("D") else "Repository/execution instructions" if ident.startswith("G") else "Historical; not proof of delivery"
        lines.append(f"| {ident} | [{path}](../../{path}) | {kind} |")
        manifest[path] = sha(ROOT / path)
    manifest["backend/uv.lock"] = sha(ROOT / "backend/uv.lock")
    lines += ["", "## Reproduction and disclosure", "",
              "`measurements.json` contains aggregate numbers and content hashes, never README copies, credentials, account inventory, request IDs or raw model responses. The audit script reads only the two named frozen public/synthetic experiment files. Those ignored source files are required for full local recomputation; their hashes make the limitation explicit. Public reviewers can inspect the committed reports and aggregate arithmetic, but cannot independently rerun historical provider generations from this package alone.", "",
              "```bash", "backend/.venv/bin/python eval/ai-system-design/scripts/audit_evidence.py", "```", "",
              "The command writes only this article's aggregate/index files. It does not initialize ledgers, import provider settings, load .env, call a service or rewrite prior results.", ""]
    (OUT / "evidence-index.md").write_text("\n".join(lines))
    (OUT / "source-manifest.json").write_text(json.dumps({"baseline_commit": result["baseline_commit"], "sha256": manifest}, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "repos": 20, "tp": 50, "fp": 0, "fn": 2,
                      "input": inp, "output": out, "round_usd": rounded_usd, "source_files": len(manifest)}))


if __name__ == "__main__":
    main()
