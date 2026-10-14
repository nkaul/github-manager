# Phase 0.5 — AI readiness pre-testing

Updated: October 12, 2026 — limited API results and user adjudication recorded.

Date: October 11, 2026 (America/New_York).

Status: **APPROVED and executed; recommend CONDITIONAL GO for review-first AI.** After the initial smoke run and primary-label clarification, the user authorized up to 20 more API calls. All 20 Luna classification calls passed on the frozen evaluation partition in 17.078 seconds; precision 100%, recall 96.2%, micro-F1 98.0%, with planned per-kind preflight targets met. Total estimated spending is $0.052212 of $5, and the 34-attempt cumulative ceiling is reached. Taxonomy/extraction received qualitative user acceptance; numeric rubric and deferred comparisons are disclosed in [round 2 results](../validation/phase-0-5-round-2-results.md). Phase 1 remains separately unapproved.

## Purpose and rationale

Resolve AI feasibility, access, extraction quality, model choice and cost uncertainty before the production foundation. Demonstrate a bounded local flow: public/synthetic repository evidence → local extraction and grouping → taxonomy draft → review → classification against a frozen canonical registry → proposed organization and Markdown evidence.

This tests [system design §5–8](../system-design.md#5-first-run-taxonomy-intelligence), rather than replacing it. Production still uses three DynamoDB tables and SQS workers. SQLite/files/memory are temporary evaluation storage. The original [execution instructions](../system-design-execution.md) and [AGENTS.md](../../AGENTS.md) require review and approval before implementation. Phase 1 remains unstarted and separately gated; Phase 0's broader provenance/watch/SSO limitations remain open.

Interpret the request's **“B25” as BM25**, consistent with the historical discussion. RAKE and YAKE extract phrases; TF-IDF aggregates corpus evidence; BM25 ranks passages or canonical candidates for a query. These methods complement the LLM and do not establish semantic project membership by themselves. Preserve actual purpose sentences: keywords alone can lose negation, context and relationships. KeyBERT, embeddings/vector databases, fine-tuning, code indexing and GitHub modifications remain outside scope.

## Initial repository assessment and planned gap resolution

| Existing evidence / code | Gap | Phase 0.5 resolution |
|---|---|---|
| Working localhost Next.js/FastAPI OAuth App scaffold; named private access and sampled organization reconciliation | GitHub access does not prove OpenAI account/model access or authorize external private content | Separate provider authentication and actual per-model structured calls; public/synthetic allowlist |
| `backend/app/config.py`, ignored `.env`, example config | No validated AI settings or provider dependency; local key presence does not prove access | Prepare template and verify local fields; implement validated server-only settings after approval |
| `backend/app/github/` and `pretest/github_probe.py` | Access checks do not produce a benchmark corpus or a reusable AI evidence profile | Explicit public fixture allowlist; record trusted IDs, visibility, README SHA, source and license; exclude private inventory |
| `backend/pyproject.toml` and `uv.lock` | No LangChain/OpenAI, extraction, retrieval or evaluation dependencies | Pin a compatible evaluation dependency group; verify Python 3.13/Pydantic compatibility, package and resource licenses |
| `backend/app/pretest/report.py` writes private Markdown reports | No AI run ledger, model comparison, cost accounting or quality report | Reuse reporting conventions; add experiment-wide SQLite ledger and sanitized Markdown summary |
| Approved taxonomy/classification contracts | No parser, corpus index, taxonomy chain, semantic validator or labeled evaluation | Local pretest modules and contract fixtures; promote proven components in Phases 3/5/6 |
| User approval owns canonical taxonomy/manual organization | Model confidence is uncalibrated; no independent expected labels | Freeze development/held-out fixtures and human-reviewed references; review-first proposals only |
| YAKE requested for comparison | Upstream license identifies AGPLv3/commercial options | Isolated local evaluation dependency; record exact installed artifact license; no production adoption without review |

## Scope and data policy

- OpenAI is the provider for this experiment, using the official API through LangChain. No Bedrock provisioning or new AWS resources are needed.
- Send only allowlisted **public metadata and selected public README evidence**, plus synthetic fixtures. Unknown visibility fails closed. Private names, metadata, README text, extracted private phrases, existing private access reports and OAuth credentials are excluded.
- Public visibility is not permission to commit complete README copies. Record source/license/SHA; keep fetched text and detailed runs in ignored local storage. Do not follow arbitrary README links, execute code or fetch unbounded documents.
- Review README text as untrusted input; filter secret-bearing material, bound size and sections, and test injection attempts. Models have no tools, browser access or mutation capabilities.
- Explicit `store=false`; no hosted files, conversations, vector stores, background jobs or remote LangSmith tracing. Provider-side retention remains governed by OpenAI's account/API policies; `store=false` does not establish zero retention.
- Keep business-state simulation in memory or SQLite; require durable local spending reservations for paid calls even if result caching is disabled. Local state/report files use the existing private directory and restrictive permissions.

## Model experiment and provisional configuration

The following are **starting candidates, not benchmark winners**. Official documentation checked October 11, 2026 describes Sol as balancing cost/intelligence and Luna as suited to focused high-volume tasks. All three candidate model pages list structured output support. Actual LangChain strict-schema calls now pass for Luna and Sol. Per-task model choice remains provisional: the small API subset shows overclassification, and full API comparison/quantitative quality evidence remains open.

| Task | Provisional model | Comparison | Selection rationale |
|---|---|---|---|
| Collection taxonomy drafting and consolidation | `gpt-6.1-sol` | `gpt-6-astra` on the same bounded collection/group evidence | Test whether stronger reasoning improves logical projects, hierarchy and alias distinctions enough to justify cost |
| Multi-label repo classification and organization proposals | `gpt-6-luna` | `gpt-6.1-sol` on the same held-out inputs | Choose the least expensive model meeting per-kind quality and safety gates |

Use low reasoning effort initially, fixed prompts/schema and supported parameters only. Do not assume every model accepts temperature, a seed or identical reasoning controls. Record requested and returned model IDs, version/fingerprint when available, adapter version and request IDs; do not invent snapshot IDs or promise deterministic LLM output. Unavailable comparison models are reported explicitly, without silently substituting another model.

Standard short-context pricing checked for the initial estimate is $2 input/$10 output per million tokens for Sol, $0.10/$0.50 for Luna, and $10/$50 for Astra. Cache writes and other applicable charges must be included in admission estimates. Refresh rates before the first live run; final reports distinguish measured token usage, estimated dollars and any independently reconciled billing.

Requested fields are prepared in `backend/.env.example` and confirmed present in ignored `backend/.env`; existing local values were preserved. The validated harness now reads these fields; live API calls remain disabled by default:

```dotenv
OPENAI_API_KEY=
OPENAI_TAXONOMY_MODEL=gpt-6.1-sol
OPENAI_CLASSIFICATION_MODEL=gpt-6-luna
OPENAI_TAXONOMY_COMPARISON_MODEL=gpt-6-astra
OPENAI_CLASSIFICATION_COMPARISON_MODEL=gpt-6.1-sol
OPENAI_TAXONOMY_REASONING_EFFORT=low
OPENAI_CLASSIFICATION_REASONING_EFFORT=low
AI_PRETEST_LIVE_ENABLED=false
AI_PRETEST_ALLOWED_DATA=public_and_synthetic
AI_PRETEST_BUDGET_USD=5.00
AI_PRETEST_PERSISTENCE=sqlite
AI_PRETEST_STATE_DIRECTORY=../docs/validation/private/ai-pretest
AI_PRETEST_CLASSIFICATION_MAX_INPUT_TOKENS=2000
AI_PRETEST_CLASSIFICATION_MAX_OUTPUT_TOKENS=2048
AI_PRETEST_TAXONOMY_MAX_INPUT_TOKENS=12000
AI_PRETEST_TAXONOMY_MAX_OUTPUT_TOKENS=4096
AI_PRETEST_REQUEST_TIMEOUT_SECONDS=60
AI_PRETEST_MAX_RETRIES=1
AI_PRETEST_MAX_GENERATION_CALLS=34
LANGSMITH_TRACING=false
LANGCHAIN_TRACING_V2=false
```

The user supplies the key locally in `backend/.env`, never chat, Git-tracked files or frontend config. Store it as a secret field excluded from repr/status/errors. Validate local mode, official provider endpoint, model allowlist, data mode, positive bounded budgets and supported model parameters; reject inherited remote tracing/proxy settings that would change the approved data destination. The final selected task models are saved only after reviewing measured results.

## Experiment-wide spending controls

The **$5 allowance covers the entire Phase 0.5 experiment**, including authentication probes, comparisons, retries, escalation and repeated runs. It is not a fresh allowance per invocation. The ledger is local to this harness and does not control unrelated account usage.

Before every call, reserve the conservative maximum charge for its bounded input, schema/instruction overhead, maximum billable output including reasoning, and applicable pricing. Reconcile with returned usage; keep reservations for uncertain outcomes such as a timeout after submission. Disable implicit SDK/LangChain retries: each of at most one explicit retry must pass the same reservation check. Run serially initially. If counting, rates or usage cannot support safe accounting, stop rather than guessing. Restarting must preserve reservations; missing/corrupt prior state blocks paid continuation. Do not automatically recreate a fresh allowance.

Proposed allocation: access/contracts $0.15; taxonomy comparison $1.50; classifier comparison $1.50; targeted ablations/repeats $1.00; contingency $0.85. These are planning allocations within one hard admission ceiling, not spending targets or guarantees about the final invoice. Cap reached → save a partial report and remaining cases; no silent increase.

Classification's 2,000-token input target includes schema overhead. Taxonomy operates on bounded collection/group summaries and has a separate 12,000-token ceiling. Output limits include reasoning; they exceed the expected visible classification JSON of roughly 300–500 tokens. Record truncation/incomplete output and evaluate it as a failure, rather than silently accepting a partial object. Any rerun requires remaining budget.

## Benchmark and reference labels

Start with **30 repository cases: 10 development and 20 held-out**, including at least 10 real public repository samples; use synthetic fixtures to establish controlled edge cases. Freeze membership, SHA/evidence, labels, rubric, prompt/schema and candidate limits before comparing models. Keep closely related repos/forks in the same split to reduce leakage. This small preflight does not replace the 100–200 human-reviewed repo evaluation required before broad production automation.

The implementer proposes reference labels and evidence for human review. Unreviewed public labels remain provisional and cannot support a final quality PASS. Synthetic expected outcomes are explicitly authored fixture truth. The same candidate/label set is used for paired model comparisons; model-generated labels or an LLM judge are not independent ground truth. Separate public and synthetic results, with denominators and uncertainty. Report slices with too few positive examples as insufficient evidence.

Include related repositories forming at least two multi-repo initiatives, unrelated repos sharing a language/framework, aliases/acronyms, near-duplicate names, forks, multi-project membership, metadata-only/sparse/missing README, negation, boilerplate-heavy and oversized README, ambiguous/no-match cases, prompt injection and secret-like synthetic markers. Include an out-of-domain/language case to disclose limits rather than assume multilingual extraction works.

Taxonomy quality uses a human rubric for relevance, evidence support, hierarchy/type correctness, alias/distinctness and useful logical grouping. Classification uses a frozen, reviewed canonical registry. The discovery draft is evaluated separately: a model's own draft must not define the ground truth against which it is graded. A local review of the draft demonstrates the draft→approved-fixture-registry→classification flow without publishing product state.

## Approved implementation stages

| Stage | Work and demonstration | Evidence / dependencies |
|---|---|---|
| 0.5A Configuration and dependency readiness | Add validated settings, local CLI, dependency lock, fixture schema, cost ledger and report writer integration | Key presence only; exact package/resource license and Python/Pydantic compatibility; credential-free failure tests |
| 0.5B Local extraction and retrieval | Parse useful Markdown sections; RAKE/YAKE comparison; TF-IDF distinct-repo aggregation; alias+TF-IDF versus alias+BM25 candidate retrieval | Actual local runs on pinned public/synthetic corpus; no provider key needed |
| 0.5C Real OpenAI access and contracts | Tiny synthetic strict-schema call through LangChain for each candidate model | Real endpoint/model response, usage and sanitized errors; billing/model access is not inferred from a models-list response |
| 0.5D Taxonomy intelligence | Group compact evidence; draft domains/projects/topics/tags; consolidate aliases while preserving distinctions; produce review sheet | Sol/Astra paired drafts; evidence/type/hierarchy checks and human rubric |
| 0.5E Classification and organization | Apply manual/rule precedence; shortlist concepts; classify compact evidence; validate IDs/evidence; propose organization | Luna/Sol paired held-out results against the frozen registry; zero product or GitHub mutations |
| 0.5F Reliability and persistence | Exercise bounded enrichment/retry, refusal/truncation, stale context, cache invalidation, restart and budget handling | Mocked fault tests labeled FIXTURE; repeated real calls on a small stability subset labeled LIVE |
| 0.5G Report and recommendation | Generate per-run Markdown plus consolidated comparison, selected task models, extraction/retrieval choice and carry-forward risks | Actual metrics/costs and human-review status; GO / CONDITIONAL GO / NO-GO for AI feasibility |

### Local extraction and retrieval details

Keep title/about/purpose/features/use cases and selected architecture sentences; remove badges, installation/code/log/license boilerplate. Extract roughly 15–25 phrases with source spans, normalizations and versions. Preserve technical acronyms. Verify repeated terms in one README cannot dominate distinct-repo TF-IDF.

RAKE is the baseline. Evaluate YAKE in an isolated local development environment and record the exact artifact's license; isolation does not itself settle licensing obligations. Do not add it to production runtime/packaging or serve it from the app during this experiment. Verify tokenizer/stopword resources and their licenses during setup; no hidden runtime downloads. Rank quality, reproducibility and failure modes matter more than comparing incomparable raw RAKE/YAKE scores.

BM25 indexes canonical names, aliases and descriptions, queried with repository evidence. Passage ranking is a separate optional test using candidate descriptions as queries; keep it only if useful. Measure exact/alias-only, TF-IDF and BM25 retrieval independently of model classification. Proposed shortlist limits match the design: domains 3, projects 8, topics 10, tags 12. A justified expanded lookup/context retry is allowed once; measure initial and expanded recall separately.

Compare bounded metadata+purpose baseline, RAKE+purpose and YAKE+purpose representations on a small fixed development subset; do not multiply every extraction/model/retrieval combination across the full corpus. Select retrieval/extraction on development evidence, then freeze it for held-out model comparison. A token-saving representation is useful only if required meaning and classification quality survive.

### LangChain, validators and organization simulation

Use `langchain-openai`/LangChain Core runnables, not an autonomous agent. Explicitly select provider-native JSON Schema via `with_structured_output(..., method="json_schema", strict=True)` and retain raw usage/status metadata for accounting. Resolve unsupported Pydantic schema features explicitly; never silently downgrade to unconstrained JSON. All provider calls, including live probes, pass through the same budgeted model factory.

Application validation must reject unknown/inactive/cross-workspace/wrong-kind/out-of-shortlist concept IDs, invented evidence, excess assignments, inconsistent no-match outcomes and stale taxonomy/profile/policy versions. Project→domain consistency is derived from the frozen registry. No new suggestion becomes canonical without review. Preserve USER mappings, explicit rejections and distinctions; do not force ambiguous cases to match. Fixture tests cover invalid results even if the real model does not produce them during the small run.

Simulate an organization run with queued/running/completed/partial-failed outcomes, separate proposed/manual/uncategorized counts and provenance. Add one reviewed concept and verify eligible previously classified repos can be reconsidered using cached profiles without a GitHub resync. This is a local orchestration contract demonstration; it does not prove SQS durability, DynamoDB concurrency, production scheduling or reset fencing.

### Persistence and app authentication

SQLite stores experiment reservations, runs, result-cache references and an immutable fixture-registry snapshot; files store local review artifacts. Cache keys include task/model parameters, prompt/schema/extractor versions, evidence/metadata hashes, candidates/taxonomy revision, workspace and privacy policy. Store only successful validated results as reusable cache entries; keep failures as run outcomes. Changing an allowed input invalidates the cache. An install-only README change with identical selected evidence should not trigger classification.

LangChain orchestrates calls; SQLite is the local storage implementation. No LangGraph, conversational memory or vector store is needed. Default cache/report data stays under `docs/validation/private/ai-pretest/`, SQLite uses rollback journals rather than WAL; any temporary sidecars stay local. Do not automatically purge the spending ledger or past Markdown evidence.

Public/synthetic CLI checks do not require browser login. Optionally reuse the existing loopback app to let the user select allowlisted public repos and review results. If an API/UI slice is added, it must require the existing session, owner isolation and CSRF for paid run creation, expose no keys/prompts in status, and prevent unauthenticated/replayed requests from spending. Test expired session and cross-owner access with fixtures; a real browser login can confirm the actual selection path. No new OAuth scopes or auth provider are required. UI work is conditional on its value for review and follows frontend instructions.

## Approved preflight acceptance gates

Thresholds below are approved preflight targets, not production quality guarantees. Report counts as well as percentages; a tiny sample cannot establish production reliability.

| Area | Required evidence / proposed gate |
|---|---|
| Access and schema | Real LangChain strict-schema calls succeed for each selected task model; comparison-model access recorded separately; refusals/incomplete/error paths explicit |
| Privacy and safety | All leakage, secret-marker, unauthorized-spend and invalid-output fixtures pass; no private data sent; accepted results have valid IDs/kinds/evidence; no manual override or automatic canonical publication |
| Extraction | Deterministic local extraction with traceable phrases/purpose, no runtime resource downloads, noise/negation/empty-input cases handled; human phrase usefulness reported on at least 10 cases |
| Retrieval | Held-out gold project candidate recall@8 ≥95%; topic@10 and tag@12 ≥90%; initial/expanded recall and per-kind support shown |
| Classification | On adequately supported PROJECT/TOPIC/TAG slices: precision ≥85%, recall ≥75%, and overall multi-label micro-F1 ≥80%; derive/report domain consistency separately; ambiguous/no-match behavior reviewed |
| Taxonomy | Human mean rubric ≥4/5, valid supporting references/type/hierarchy for accepted proposals, no unsupported forced projects; draft and reviewer decisions saved |
| Cost and compactness | Full token/schema/output/reasoning accounting; local reservations enforce $5 experiment allowance; compare token reduction and paired quality; do not adopt compaction solely for savings |
| Reliability | Fault tests, restart/reservation preservation and cache invalidation pass; report live latency p50/p95 with sample size, and repeated-subset disagreement |
| Reports and decision | Reproducible source/config hashes, actual per-model metrics, license disposition, missing evidence, human-review state and explicit recommendation |

Any privacy, unauthorized spending or accepted-invalid-result failure is a NO-GO for that path. Missing key/account entitlement blocks live completion but not offline setup/extraction. Missing human review or inadequate positive support means quality remains unverified. A comparison-model access failure or unresolved YAKE adoption can lead to CONDITIONAL GO only when its impact and acceptance are explicit; do not mark requested unrun checks as passed. Production auto-apply remains disabled regardless of this small benchmark's outcome.

## Files, commands and reports

Implemented local additions live under `backend/app/pretest/ai/`: settings/model factory, corpus loader, Markdown evidence, keyword/retrieval adapters, schemas/semantic validation, taxonomy/classifier runnables, SQLite ledger/cache, metrics and runner. Add focused tests under `backend/tests/pretest/ai/` and synthetic fixtures with no credentials; keep public content caches ignored. Reuse `pretest/report.py`. Update the backend evaluation dependency group/lock, example config and a Phase 0.5 local setup guide. Promote proven logic into production modules later, avoiding a second competing AI implementation.

Implemented commands (from repository root; see the setup guide for local tooling):

```bash
bash scripts/check-phase05.sh
PYTHONPATH=backend backend/.venv/bin/python -m app.pretest.ai --stage offline
AI_PRETEST_LIVE_ENABLED=true PYTHONPATH=backend backend/.venv/bin/python -m app.pretest.ai --stage access --live
AI_PRETEST_LIVE_ENABLED=true PYTHONPATH=backend backend/.venv/bin/python -m app.pretest.ai --stage benchmark --live
PYTHONPATH=backend backend/.venv/bin/python -m app.pretest.ai --stage report
```

Live commands require approved phase execution, configured key, explicit live flag and enabled setting, frozen allowlist and usable spending ledger. Credential-free checks remain the default. Use repository-local tooling/cache as in Phase 0. Run the existing backend regression after settings/dependency changes; run relevant UI checks only if frontend changes.

Generate immutable `docs/validation/private/ai-pretest/ai-<UTC-run>.md` reports, a local manifest/ledger and a sanitized consolidated [Phase 0.5 results report](../validation/phase-0-5-results.md). Each check distinguishes LIVE provider, LIVE GitHub, LOCAL_ALGORITHM, FIXTURE or HUMAN_REVIEW evidence and PASS/FAIL/BLOCKED/NOT_TESTED. Cache hits are labeled REPLAY, not new live evidence. Always save a report on blocked, failed and budget-stopped runs.

Reports include source/SHA/split hashes, label-review status, model/adapter/prompt/schema versions, settings without secrets, extractor/retrieval comparisons, candidate recall, classification confusion/error cases, taxonomy rubric, latency/stability, cached/input/output/reasoning usage without double counting, price date, spent/reserved budget, sanitized failures, file paths and carry-forward owners. Do not publish full prompts, READMEs or credentials in the shareable summary.

## Current readiness and remaining gates

| Gate | Current status | Next action |
|---|---|---|
| Scope, data and spending | APPROVED: public/synthetic and $5 total | Preserve the existing experiment ledger |
| Architecture and plan | APPROVED / local implementation present | No Phase 1 or production changes authorized |
| Key and account/model access | PASS: Luna/Sol count and strict generation HTTP 200 | Preserve historical credit failure; Astra not retried |
| Dependencies and offline harness | PASS: actual RAKE/YAKE, TF-IDF/BM25; 81 tests and Ruff | Human-rate phrase usefulness; YAKE production license review later |
| Reference corpus | 30 cases frozen; labels/registry approved by user | Changes require a recorded amendment, no silent retuning |
| Real LangChain AI checks | 10/10 limited requests PASS; $0.048893 estimated; request ceiling reached | Full API comparison deferred; TOPIC/TAG precision 75%; primary-only clarification applied after testing, not yet retested |
| Supplementary Codex checks | PASS structural: two 20-case classifications and a 20-proposal taxonomy draft | Qualitatively accepted, numeric rubric unscored; no API access/cost claim from this route |
| Phase 0.5 outcome | CONDITIONAL GO recommended | Primary-only validation passes; review explicit comparison/production limits before Phase 1 |

The latest instruction authorizes a temporary supplementary Codex CLI inference route while API credit is unavailable. This uses the existing ChatGPT login, public/synthetic evidence, explicit JSON Schema and the same semantic validators. It does not use or reset the API spending ledger. Codex batch context, client instructions, tools/protocol and subscription accounting differ from the approved production provider path: results can inform feasibility, but cannot close LangChain compatibility, API billing, per-request latency, compaction or model-selection gates. No production provider architecture changes.

Continue within approved Phase 0.5 scope; do not request the same plan/data/budget approval again. Stop after evidence/selection review. Phase 1 requires separate approval, with Phase 0 limitations still visible.

## Primary references checked

- [OpenAI model selection](https://developers.openai.com/api/docs/guides/model-selection), [GPT-6 family guidance](https://developers.openai.com/api/docs/guides/latest-model), [Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol), [Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) and [pricing](https://developers.openai.com/api/docs/pricing). Candidate recommendation is a hypothesis to evaluate; documented availability is not account access evidence.
- [OpenAI structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs) and [data controls](https://developers.openai.com/api/docs/guides/your-data): schema handling, refusal paths, storage and retention constraints.
- [LangChain ChatOpenAI](https://docs.langchain.com/oss/python/integrations/chat/openai): explicit structured-output method, model invocation and usage metadata. Verify behavior with the pinned integration version.
- [RAKE-NLTK license](https://raw.githubusercontent.com/csurfer/rake-nltk/master/LICENSE) (MIT), [rank_bm25 license](https://raw.githubusercontent.com/dorianbrown/rank_bm25/master/LICENSE) (Apache-2.0), [YAKE license](https://raw.githubusercontent.com/INESCTEC/yake/master/LICENSE) (AGPLv3/commercial). Recheck exact package artifacts/resources at installation; this identifies licenses and does not settle production legal applicability.
- [Historical keyword/ranking rationale](../design-conversation.md#turn-4--research-enhancement-yakerakekeybertbm25-for-extracted-evidence) and [full conversation](../design-conversation-full.md): local extraction versus semantic association, retained purpose evidence, canonical registry memory and progressive enrichment.

## Historical findings from the initial limited run

- Reference labels/registry semantics are approved, but minimum expected sets do not establish exhaustive precision truth. The user confirmed primary labels only; FastAPI's extra Data Validation topic and fastapi tag are overclassification. The prompt now states the rule explicitly; original scores are preserved and no further paid call verified the refinement.
- The Markdown-only parser retains reStructuredText image/target noise from pytest's public README. Some RAKE phrases are generic prose. Add README-format/noise fixtures and version any extractor revision; do not mutate the frozen baseline after model outputs.
- TF-IDF and BM25 tie on the measured candidate-recall slices; retain TF-IDF as the simpler provisional choice. RAKE remains the licensed baseline. YAKE is informative locally but is not approved for production packaging.
- The one-repository representation check used fewer input tokens for metadata+purpose than for RAKE/YAKE, with identical assignment sets. One fresh repeat agreed on assignment IDs. These observations do not establish general compaction benefit or stability.
- Luna/Sol are feasible through LangChain native structured output. The user qualitatively accepted the taxonomy/extraction sheets; keep task models provisional until the clarified prompt is verified with adequate measured support. Numeric ratings were not provided. The user-requested continuation used ten generation calls; no further API calls follow automatically even though $4.951107 remains.

## Latest authorized validation round

The user authorized up to 20 additional model calls. The unchanged primary-only prompt was applied to all 20 frozen evaluation cases with four isolated clients: 20/20 API contracts passed in 17.078 seconds. Aggregate precision 100%, recall 96.2%, micro-F1 98.0%; all planned per-kind preflight targets pass. Eight public cases scored 100% micro-F1; 12 synthetic cases scored 97.1%. Two measured misses (Telemetry, python) remain recorded. No labels/extractor outputs were changed, and no retry or expansion was attempted.

The cumulative ceiling is now 34 attempts: four rejected historical attempts, ten smoke calls and twenty newly authorized calls. Estimated spending totals $0.052212, with zero outstanding reservations. Further calls do not follow automatically. Recommend Luna classification and Sol taxonomy for review-first use; Astra/full paired Sol comparison, numeric human ratings, README-format noise correction, broader stability/compaction and independent production evaluation remain explicit limits. This reused corpus includes three previously reviewed cases and is not an independent production generalization estimate. Phase 1 remains unapproved. [Detailed results](../validation/phase-0-5-round-2-results.md).
