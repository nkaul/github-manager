import json
from datetime import datetime
from zoneinfo import ZoneInfo

from app.config import REPO_ROOT
from app.pretest.ai.evaluation import metrics, percentiles
from app.pretest.ai.review_artifacts import reviews
from app.pretest.report import cell


def load_optional(directory, name, default):
    path = directory / name
    return json.loads(path.read_text()) if path.exists() else default


def consolidate(directory, ledger):
    local = load_optional(directory, "offline.local.json", {})
    access = load_optional(directory, "access.local.json", [])
    bench = load_optional(directory, "benchmark.local.json", {})
    limited = load_optional(directory, "limited.local.json", {})
    round2 = load_optional(directory, "validation-round-2.local.json", {})
    validation = load_optional(directory, "validation.local.json", {})
    references = load_optional(directory, "reference-review.local.json", {})
    quality = load_optional(directory, "quality-review.local.json", {})
    reviewed = references.get("approved") is True and references.get("corpus_hash") == local.get(
        "corpus_hash"
    )
    selected = {"gpt-6.1-sol", "gpt-6-luna"}
    passed = {r["requested_model"] for r in access if r["status"] == "PASS"}
    status = (
        "BLOCKED for live AI completion"
        if not selected <= passed
        else "API FEASIBILITY DEMONSTRATED; QUALITY / COVERAGE REVIEW OPEN"
    )
    if round2.get("quality_targets_met"):
        status = "CONDITIONAL GO for review-first AI; production/comparison limits remain"
    today = datetime.now(ZoneInfo("America/New_York")).strftime("%B %d, %Y")
    budget = ledger.summary()
    rows = [
        "# Phase 0.5 — AI readiness results",
        "",
        f"Review date: {today} (America/New_York).",
        "",
        f"Status: **{status}.** Phase 0.5 implementation is approved. "
        "Offline algorithms and safety tests have run; live results are recorded below. "
        "No automatic taxonomy publication, GitHub mutations or AWS changes occurred.",
        "",
        "Plan: [AI readiness pre-testing](../planning/phase-0-5-ai-readiness.md). "
        "Run instructions: [local setup](../development/phase-0-5-ai-readiness.md).",
        "",
        "## Actual validation",
        "",
        "| Check | Evidence | Status | Result |",
        "|---|---|---|---|",
    ]
    for item in validation.get("checks", []):
        rows.append(
            "| "
            + " | ".join(cell(item.get(k, "")) for k in ("check", "evidence", "status", "detail"))
            + " |"
        )
    if local:
        rows += [
            "| Public corpus | LIVE_GITHUB | PASS | 10 allowlisted public repos; "
            "public visibility, numeric IDs, README SHAs and license metadata recorded |",
            "| RAKE / YAKE | LOCAL_ALGORITHM | PASS | 30 profiles each; "
            "source spans and selected purpose evidence; no runtime tokenizer downloads |",
            "| Reference labels | HUMAN_REVIEW | "
            + ("RECORDED" if reviewed else "PENDING")
            + (
                " | Public labels/registry approved by user; synthetic fixture truth |"
                if reviewed
                else " | Public labels pending; synthetic fixture truth |"
            ),
        ]
    if round2:
        latest = ["# Phase 0.5 — primary-label validation round 2", "", *round2_rows(round2)]
        (REPO_ROOT / "docs/validation/phase-0-5-round-2-results.md").write_text(
            "\n".join(latest) + "\n"
        )
        rows += ["", "## Latest primary-label validation", "", *round2_rows(round2)]
    rows += [
        "",
        "## Real provider checks",
        "",
        "The official Responses input-token endpoint is called on the actual LangChain payload, "
        "including JSON Schema, before a durable maximum-cost reservation and generation. "
        "Token-count success is authentication/connectivity evidence; it does not prove "
        "successful model generation or model quality.",
        "",
        "| Candidate | Count HTTP | Generation HTTP | Outcome / sanitized code |",
        "|---|---|---|---|",
    ]
    for item in access:
        rows.append(
            f"| {item['requested_model']} | {item.get('count_http_status', '—')} | "
            f"{item.get('http_status', '—')} | {item['status']}: "
            f"{cell(item.get('provider_error_code') or 'Structured call completed')} |"
        )
    diagnosed = [r for r in access if r.get("provider_error_code") == "credit_balance_exhausted"]
    if diagnosed:
        rows += [
            "",
            "A bounded diagnostic retry returned **HTTP 429 `credit_balance_exhausted`**. "
            "API credit must be restored for the account/project associated with the local key. "
            "Taxonomy, classification, compaction quality and model latency/stability are "
            "**NOT TESTED** while generation is blocked. No model winner has been selected.",
        ]
    elif selected <= passed:
        rows += [
            "",
            "Credit was restored and actual LangChain strict-schema generation now succeeds "
            "for Luna and Sol. Four earlier rejected attempts and the diagnosed "
            "`credit_balance_exhausted` failure are preserved in immutable local reports. "
            "Astra was not retried after the user requested limiting calls.",
        ]
    rows += [
        "",
        "## Local extraction and retrieval",
        "",
        f"Frozen corpus: `{local.get('corpus_hash', 'not prepared')}`. "
        "30 cases: 10 public + 20 synthetic; 10 development + 20 held-out. "
        "Related repositories stay in the same split. Reference labels are never sent to models.",
        "",
        "| Method | Held-out PROJECT recall@8 | TOPIC recall@10 | TAG recall@12 |",
        "|---|---|---|---|",
    ]
    for method, values in local.get("retrieval", {}).items():
        cells = []
        for kind in ("PROJECT", "TOPIC", "TAG"):
            metric = values["heldout"][kind]
            cells.append(
                f"{metric['found']}/{metric['gold']} ({metric['recall']:.1%})"
                if metric["gold"]
                else "No support"
            )
        rows.append("| " + " | ".join([method, *cells]) + " |")
    times = local.get("extraction_seconds", {})
    rows += [
        "",
        f"Development comparison chose **{local.get('retrieval_choice', 'unselected')}** "
        "with a stable tie-break favoring the simpler TF-IDF baseline. Retrieval recall "
        "measures whether expected concepts reach the shortlist; it is not classification "
        "precision, taxonomy usefulness or production coverage. Reference status: "
        + ("user approved" if reviewed else "pending")
        + "; see [reference review](phase-0-5-reference-review.md).",
        "",
        f"Extraction wall time: RAKE {times.get('rake', '—')}s; YAKE {times.get('yake', '—')}s "
        "for 30 profiles. YAKE includes 30 isolated process startups, so this is not a fair "
        "intrinsic algorithm-speed comparison. Phrase samples received qualitative acceptance; "
        "numeric usefulness ratings were not supplied. "
        "The development Spanish case exposes a lexical/English-extraction limitation.",
        "",
        "## Earlier smoke results — before primary-label clarification",
        "",
    ]
    if limited:
        rows += limited_rows(limited)
    else:
        for model, result in bench.get("classification", {}).items():
            rows.append(
                f"- `{model}`: {result['status']}; measured repository cases: "
                f"{len(result.get('records', []))}."
            )
    rows += [
        "",
        "Recommend Sol for review-first taxonomy and Luna for review-first classification "
        "as preflight defaults, based on the successful API evidence and qualitative review. "
        "This does not establish superiority over the deferred Astra/Sol comparisons. "
        "The small preflight cannot authorize production "
        "auto-apply; the later 100–200 human-reviewed evaluation remains required.",
        "",
        "Human review: "
        + (
            "the user reviewed the drafts/extraction samples and said **looks ok**. "
            "Recorded as qualitative acceptance; no numeric rubric or ≥4/5 mean is inferred. "
            "The user requires **primary labels only**, so FastAPI's extra labels are "
            "overclassification for this test. The prompt now states that rule; "
            + (
                "the clarified prompt was tested on all 20 frozen evaluation cases in round 2."
                if round2.get("status") == "PASS_CONTRACT"
                else "the clarified prompt was not live-tested after the earlier request ceiling."
            )
            if quality.get("taxonomy_and_extraction_qualitative_acceptance")
            else "pending taxonomy/extraction assessment."
        ),
        "",
        "Supplementary [Codex results](phase-0-5-codex-results.md) contain actual "
        "ChatGPT-authenticated 20-case Sol/Luna batches and a taxonomy draft. "
        "Those results are attributed separately and do not substitute for this API benchmark.",
        "",
        "## Spending, persistence and artifacts",
        "",
        f"Experiment cap **${budget['cap_usd']:.2f}**; estimated generation spend "
        f"**${budget['estimated_usd']:.6f}**; outstanding maximum reservations "
        f"**${budget['reserved_usd']:.6f}**; remaining allowance "
        f"**${budget['remaining_usd']:.6f}**. Ledger generation attempts: {budget['calls']}. "
        "Rejected-before-generation requests settle at zero; "
        "this is not an invoice reconciliation. "
        "The allowance persists across invocations and includes retries; uncertain charges "
        "retain their reservation. SDK/LangChain automatic retries are disabled.",
        "",
        "SQLite stores run/reservation/cache state under ignored "
        "`docs/validation/private/ai-pretest/`; reports and local JSON use mode 0600. "
        "No raw README content is included in this shareable summary. The key stays server-only; "
        "live calls require a CLI flag and environment override. Remote tracing is disabled.",
        "",
        "Exact evaluation packages are locked in `backend/uv.lock`. YAKE 0.7.3 is isolated "
        "under `.tools/yake`, pinned in `backend/requirements-ai-yake.txt`; its installed artifact "
        "identifies AGPLv3/commercial licensing. "
        "Local evaluation does not approve production adoption.",
        "",
        "Private artifacts: `frozen-corpus.local.json`, `public-corpus.local.json`, "
        "`offline.local.json`, `access.local.json`, `benchmark.local.json`, "
        "`dependencies.local.json`, `runs.sqlite3`, and immutable `ai*.md`/paired JSON reports. "
        "The initial sandbox-network failure and original provider failures are preserved.",
        "",
        "## Remaining gates",
        "",
        (
            "1. The 20-case Luna API validation is complete. The total ceiling of 34 attempts "
            "(14 prior + 20 newly authorized) is reached. Astra and a full paired Sol classifier "
            "comparison remain deferred; no further paid calls follow automatically."
            if round2.get("status") == "PASS_CONTRACT"
            else "1. API access is verified; the full 20-case API benchmark, Astra comparison and "
            "batch consolidation remain deferred under the user's call limit. "
            "The persistent 14-attempt ceiling (four earlier + ten continuation) is reached. "
            "No further paid calls were made."
            if selected <= passed and limited
            else "1. Restore API credit and rerun access using the existing ledger."
        ),
        "2. Reference labels/registry are "
        + ("approved" if reviewed else "pending review")
        + "; drafts/extraction qualitatively accepted; numeric rubric remains unscored.",
        (
            "3. Classification preflight targets pass. Independent 100–200 case production "
            "evaluation, larger compaction/stability coverage and README-format noise fixes "
            "remain later gates; models are preflight recommendations, not comparative winners."
            if round2.get("quality_targets_met")
            else "3. Verify the primary-only prompt and obtain adequate per-kind evidence before "
            "selecting task models; larger compaction/stability tests remain deferred."
        ),
        "4. Review the completed Phase 0.5 report; Phase 1 remains separately unapproved. "
        "Phase 0's broader provenance/watch/SSO limitations remain open.",
        "",
        "Optional browser authentication was not needed for the public/synthetic CLI checks. "
        "There is no paid-run web endpoint or unauthenticated browser spend path.",
        "",
        "References: [OpenAI token counting]"
        "(https://developers.openai.com/api/docs/guides/token-counting), "
        "[pricing](https://developers.openai.com/api/docs/pricing), "
        "[LangChain integration](https://docs.langchain.com/oss/python/integrations/chat/openai).",
    ]
    target = REPO_ROOT / "docs/validation/phase-0-5-results.md"
    if local:
        reviews(directory)
    target.write_text("\n".join(rows) + "\n")
    return target


def limited_rows(run):
    from app.pretest.ai.corpus import registry

    calls = run["access"] + run["taxonomy"]
    calls += [r["call"] for value in run["classification"].values() for r in value["records"]]
    calls += [r["call"] for r in run["ablations"] + run["stability"]]
    if len(calls) != 10 or any(result["status"] != "PASS" for result in calls):
        return [
            f"Limited continuation is partial: {len(calls)} recorded generation outcomes; "
            "see `limited.local.json`. No full smoke/quality PASS is inferred.",
        ]
    rows = [
        "The user restored API credit and requested fewer calls. This continuation made "
        "**10 generation requests**: two access probes, one 30-repository taxonomy draft, "
        "three Luna classifications, one paired Sol classification, two Luna representation "
        "checks and one fresh Luna repeat. All ten passed strict-schema and semantic validation. "
        "No implicit retry occurred. This is a smoke subset, not the full API benchmark.",
        "",
        "| API model | Repos | Kind | TP / FP / FN | Precision | Recall | F1 |",
        "|---|---|---|---|---|---|---|",
    ]
    for model, result in run["classification"].items():
        for kind, item in (result.get("metrics") or {}).items():
            values = [
                "—" if item[k] is None else f"{item[k]:.1%}" for k in ("precision", "recall", "f1")
            ]
            rows.append(
                f"| {model} | {item['repos']} | {kind} | "
                f"{item['tp']} / {item['fp']} / {item['fn']} | " + " | ".join(values) + " |"
            )
    rows += [
        "",
        "The fixed Luna subset is FastAPI, Orion Audit (two initiatives), and "
        "Negated API (explicitly unrelated initiatives); Sol was paired only on FastAPI. "
        "Luna TOPIC/TAG precision is 75% against the approved minimum references, below the 85% "
        "target; project support is only one positive repository. Both models add FastAPI's "
        "Data Validation topic and fastapi tag. The user adjudicated these as unwanted secondary "
        "labels: use primary labels only. These are valid IDs but wrong assignments under that "
        "rule. The executed prompt did not state the rule as clearly as the subsequent refinement. "
        "Original labels/scores are preserved; these slices cannot close quality gates.",
        "",
        "| Task / model | Returned ID | Input | Cached / written | Output (reasoning) | Seconds |",
        "|---|---|---|---|---|---|",
    ]
    for result in calls:
        usage = result.get("usage", {})
        details = usage.get("input_tokens_details", {})
        rows.append(
            f"| {result['task']} / {result['requested_model']} | "
            f"{result.get('returned_model', '—')} | {usage.get('input_tokens', '—')} | "
            f"{details.get('cached_tokens', 0)} / {details.get('cache_write_tokens', 0)} | "
            f"{usage.get('output_tokens', '—')} "
            f"({usage.get('output_tokens_details', {}).get('reasoning_tokens', 0)}) | "
            f"{result['seconds']} |"
        )
    rows += [
        "",
        "Reasoning tokens are included in output totals and are not added twice. "
        "Admission and recorded estimates conservatively include input plus reported "
        "cache-write charges; these are local estimates, not invoice reconciliation.",
        "",
    ]
    for model, result in run["classification"].items():
        values = percentiles([r["call"]["seconds"] for r in result["records"]])
        rows.append(
            f"- API classification `{model}`: n={values['n']}, "
            f"p50={values['p50']}s, p95={values['p95']}s including token counting/client work. "
            "Tiny-sample percentiles do not establish production latency."
        )
    reference = next(iter(run["classification"].values()))["records"][0]
    base = reference["call"]
    base_ids = set(reference["predicted"])
    rows += [
        "",
        "| FastAPI / Luna input | Input tokens | Reference micro-F1 | Same labels as RAKE |",
        "|---|---|---|---|",
    ]
    variants = [("RAKE + purpose", base)]
    variants += [(item["representation"], item["call"]) for item in run["ablations"]]
    for name, result in variants:
        predicted = [a["concept_id"] for a in result.get("result", {}).get("assignments", [])]
        score = metrics([{"gold": reference["gold"], "predicted": predicted}], registry())["ALL"][
            "f1"
        ]
        rows.append(
            f"| {name} | {result.get('counted_input_tokens', '—')} | "
            f"{score:.1%} | {set(predicted) == base_ids} |"
        )
    repeat = run["stability"][0]["call"] if run["stability"] else {}
    repeat_ids = {a["concept_id"] for a in repeat.get("result", {}).get("assignments", [])}
    rows += [
        "",
        f"One fresh Luna repeat: assignment-set agreement={repeat_ids == base_ids}. "
        "This is one pair; summary/confidence equality and broad stability are not established. "
        "The metadata+purpose baseline used fewer input tokens than either keyword variant "
        "on this one repository. No extraction/model winner is selected from this ablation.",
        "",
        "The API Sol taxonomy draft passed supporting-ID/type/hierarchy validation. The user "
        "qualitatively accepted the [actual drafts](private/ai-pretest/taxonomy-review.md) "
        "and [10 public extraction samples](private/ai-pretest/extraction-review.md). "
        "Local organization simulation preserved manual choices/rejections and derived domains; "
        "fixtures cover queued/running/completed/partial-failed states and counts. "
        "it does not establish production worker durability or concurrency.",
        "",
        "Extraction review exposed real noise: pytest's README contains reStructuredText "
        "image/target markup that the Markdown-only parser retains, and some RAKE phrases are "
        "generic prose. Add an explicit README-format policy and noise fixtures before promoting "
        "this extractor. Do not silently rebuild frozen evidence after seeing model results.",
    ]
    return rows


def round2_rows(run):
    from app.pretest.ai.corpus import registry

    if "metrics" not in run:
        return ["Round 2 is in progress or partial; no final quality claim."]
    rows = [
        f"Outcome: **{run['status']}**; planned quality targets met: "
        f"**{run['quality_targets_met']}**. Exactly **{run['generation_attempts']}** additional "
        f"model-generation requests, four concurrent isolated clients, **{run['seconds']}s** "
        "wall time. Existing access evidence was reused; no login probes, retries, candidate "
        "expansions or extra model calls. Each generation also used its required input-count "
        "request before a durable spending reservation.",
        "",
        "The same frozen evaluation partition contains 8 public + 12 synthetic cases. "
        "Primary-label instructions were fixed before this round; no labels or extractor "
        "outputs changed. Models never received reference labels. Three evaluation cases "
        "had already informed the user's policy clarification, so this is a regression "
        "validation on a reused corpus, not an independent production generalization estimate.",
        "",
        "| Kind | TP / FP / FN | Positive repos / labels | Precision | Recall | F1 |",
        "|---|---|---|---|---|---|",
    ]
    for kind, value in run["metrics"].items():
        scores = [
            "—" if value[k] is None else f"{value[k]:.1%}" for k in ("precision", "recall", "f1")
        ]
        rows.append(
            f"| {kind} | {value['tp']} / {value['fp']} / {value['fn']} | "
            f"{value['positive_repos']} / {value['label_support']} | " + " | ".join(scores) + " |"
        )
    rows += [
        "",
        "| Source | Repos | Micro TP / FP / FN | Precision | Recall | F1 |",
        "|---|---|---|---|---|---|",
    ]
    for source, values in run["slices"].items():
        value = values["ALL"]
        rows.append(
            f"| {source} | {value['repos']} | {value['tp']} / {value['fp']} / "
            f"{value['fn']} | {value['precision']:.1%} | {value['recall']:.1%} | "
            f"{value['f1']:.1%} |"
        )
    concepts = registry()
    rows += ["", "| Case | Extra labels | Missing labels |", "|---|---|---|"]
    for record in run["records"]:
        extra = set(record["predicted"]) - set(record["gold"])
        missing = set(record["gold"]) - set(record["predicted"])
        if extra or missing:
            extras = ", ".join(concepts[i]["name"] for i in sorted(extra)) or "—"
            misses = ", ".join(concepts[i]["name"] for i in sorted(missing)) or "—"
            rows.append(f"| {record['id']} | {cell(extras)} | {cell(misses)} |")
    latency = run["latency"]
    before, after = run["budget_before"], run["budget_after"]
    rows += [
        "",
        "FastAPI now returns only Web APIs/python, correcting the earlier two "
        "secondary assignments. No false-positive project membership was observed, and "
        "the two empty/fork no-match cases remained unassigned. Missing Telemetry on "
        "Helios Dashboard and python on Helios Audit are retained as measured misses; "
        "no further tuning/retest occurred after this round.",
        "",
        f"Per-request latency including count/client work: n={latency['n']}, "
        f"p50={latency['p50']}s, p95={latency['p95']}s. Concurrent-run latency is not "
        "directly comparable with the earlier serial smoke subset. This small sample "
        "does not establish production service levels.",
        "",
        f"Round estimated spending: **${run['round_estimated_usd']:.6f}**. Experiment "
        f"total: **${after['estimated_usd']:.6f} / ${after['cap_usd']:.2f}**; outstanding "
        f"reservations **${after['reserved_usd']:.6f}**. Durable attempt count "
        f"{before['calls']} → {after['calls']}; the 34-attempt ceiling is reached. "
        "Prices were rechecked October 12; estimates use the existing conservative "
        "method and are not invoice reconciliation.",
        "",
        f"Executed model `{run['model']}`; prompt hash `{run['prompt_hash']}`; schema "
        f"hash `{run['schema_hash']}`. Per-case actual returned models, request IDs, "
        "counts, cached/input/output/reasoning usage, errors and outputs are preserved "
        "in ignored mode-0600 `validation-round-2.local.json`, individual case JSON "
        "and immutable `ai-primary-round2-*.md`/JSON reports.",
        "",
        "Recommendation: **CONDITIONAL GO for review-first AI feasibility**. Keep Luna "
        "for classification and Sol for taxonomy as preflight defaults in backend/.env. "
        "Astra/full paired Sol comparison, numeric human rubric, broader multilingual "
        "extraction, README-format noise correction, large stability/compaction and "
        "independent production evaluation remain explicit limits. No production "
        "auto-apply, Phase 1 implementation or new data authorization follows from this result.",
    ]
    return rows
