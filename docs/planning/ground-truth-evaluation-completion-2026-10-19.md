# Complete the GitHub Manager evaluations

October 19, 2026 · **Approved for execution.** The user approved the call/generation limits and requested another approval if additional generations are needed. Publishing is proceeding independently in the demo repository. Results are recorded as they become available, separately from the planned measurements below.

> **Completed October 19.** See the [final measured report](../validation/ground-truth-evaluation-2026-10-19.md). Thirty primary classifications, three paired comparisons, two taxonomy drafts/consolidation and three Ragas grounding cases completed; Promptfoo replay and local diagnostics passed their contracts. Eight rejected adapter attempts remain counted, reducing optional comparison/grounding scope within the unchanged 50-generation/100-HTTP limits. Estimated new charges are $0.133941; the run grant is FINISHED. No further generation is authorized without another approval. The original approved schedule and rationale below remain preserved as the plan, not rewritten as execution history.

**Execution budget correction:** the planning audit's $4.872381 figure covered the original classification ledger only. Including the copied-demo ledger increment and four retained narration manifests accounts for $4.183029 cumulatively, leaving $0.816971 under the existing $5 ceiling before this run. The execution guard must use the tighter of that remaining amount and the approved $1 sub-ceiling, rechecking all historical reservations. No historical reservation is released or reset by this correction.

## Intended result

Produce a reproducible answer to four questions: Does the app find the right candidate labels? Does the evidence survive extraction and prompt packing? Does the LLM choose supported primary labels? What does that quality cost? Run the local scorer and established evaluation frameworks on the **same frozen inputs and outputs**, then update the Ground Truth publication with measured results and their limits.

Use the **30 repositories actually confirmed by the human**, rather than requiring another review of all 600 or completion of a different pilot queue. The 600-repository corpus remains useful for offline pipeline diagnostics; its other 570 proposals do not become human ground truth.

Continue the implemented local app: RAKE profiles, alias-boosted sparse TF-IDF retrieval, bounded context and LangChain structured classification; a separate taxonomy-discovery workflow; SQLite/files for persistence. BM25 and YAKE are offline comparisons. No Jev implementation, embedding service, vector database or AWS buildout is introduced.

## Current evidence and dependencies

See the [read-only completion audit](../validation/ground-truth-review-completion-2026-10-19.md) and [aggregate JSON](../../eval/ai-system-design/ground-truth-creation/history/review-completion-audit-2026-10-19.json).

| Observed fact | Evaluation consequence |
|---|---|
| 30 confirmed records, 30 distinct repositories, one review owner | Single-reviewer reference set; not independent human consensus |
| 83 positives: 15 Project, 35 Topic, 33 Tag | Score multiple labels; derive Domains from Project parents |
| 4 changed label sets versus original proposals: 3 additions, 2 removals | Observed corrections, not validated accuracy of the remaining 600 |
| 9 sampling domains; data 10, finance 6, cloud 0 | Report slice denominators; no cloud-quality or population error-rate claim |
| 18 leakage groups; 15 development and 15 test-reserved; no validation records | Preserve groups/splits; score test-reserved cases after configuration freeze |
| 6 overlap the independent A/B pilot; 4 overlap its suggested queue | A/B-versus-human denominator is 6; queue-stratum denominator is 4 |
| Review bindings: 8 at v0, 5 at v1, 17 at v2 | Preserve historical contexts and vocabulary availability |
| 1 unfinished draft | Exclude it; do not overwrite it or require completion to evaluate the saved 30 |
| All 30 records retain `UNKNOWN_NOT_NEGATIVE` | Unselected labels cannot silently become false positives |

The base vocabulary has 337 concepts: 10 Domains, 64 Projects, 166 Topics and 97 Tags. The owner extension adds one Project and one Topic, making 339 effective concepts. Legacy records without a context resolve against base v0. No base definitions were changed.

The existing Phase 0.5 scorer treats `predicted - gold` as false positives. Its original fixture contract must remain intact; a **partial-label-aware adapter** is needed for these references. Ragas and DeepEval are not installed. LangSmith is installed transitively, but remote tracing remains disabled. Current model and ledger settings exist; new run-specific quotas, framework integration and live predictions still need implementation/authorization.

## Step 1 — Freeze the actual reference set

Take a consistent read-only export of the 30 final reviews, their history, evidence and per-record vocabulary context. Include numeric repository IDs, pinned commits, source/proposal/manifest hashes, definitions at v0/v1/v2, split/group membership, capture time and evaluation-input hashes. Recheck current counts before freezing; this dated audit must not override later user edits.

Keep two vocabulary views: historical base-only definitions for A/B analysis and an explicitly frozen effective v2 for new predictions. The new run can search all 339 concepts, but a new label absent from an older human review stays unjudged there. Never rewrite an old confirmation to pretend it reviewed the expanded vocabulary.

Validate source bindings, canonical IDs, derived Domains, review acknowledgements, additional-label quotes and definition availability. Save owner-specific decisions privately; publish aggregate statistics and brief public-source examples.

**Output:** private `reference-snapshot.json`, `registry-history.json`, `manifest.json`, `reference-quality.md`. **Gate:** no structural/source-binding errors; exclusions and unknowns explicit. No LLM calls.

## Step 2 — Finish reference and annotation statistics

Produce per-kind/domain/group coverage, empty-Project/Tag counts, review revisions, additions/removals and vocabulary-gap discoveries. Separate purpose-text edits from label edits and observed changes from inferred reasons.

For the six A/B overlaps, report shared human positives, human-only positives, agent-only unjudged labels and descriptive set agreement. Both agents currently contain all 17 human-retained positives on that overlap, with 14 additional A pairs and 18 additional B pairs; neither exactly matches any of the six sets. Those extra pairs are not yet adjudicated errors. Human and agent primary-purpose/granularity policies may differ.

The four completed cases from the original 20-case queue are all `RANDOM_FILL`; no completed risk-selected or random-Green case occurs in that intersection. Do not calculate the planned risk-versus-random comparison from unrelated reviews. Report actual sample denominators and uncertainty; use group bootstrap where feasible, retaining descriptive results for tiny slices. Do not infer review time from saved timestamps or independent-human agreement from one reviewer.

**Output:** `reference-statistics.json`, `annotation-comparison.md`, correction and vocabulary-gap tables. No new agents or paid calls are required.

## Step 3 — Measure retrieval and context locally

Reuse `app.demo.evidence.build_profile`, the current `Retriever` and compact-input logic. Use disposable evaluation state with **no reference labels preloaded as manual edges or rules**. Otherwise manual answers would inflate classifier quality. Preserve the frozen Phase 0.5 paths and their original extractor/prompt versions.

Keep an inspection trail for every reviewed repository:

1. Saved public metadata and README with hashes; supporting documents remain reference evidence rather than automatic app input.
2. App extraction: selected sections, evidence IDs and RAKE phrases.
3. Ranked canonical candidates and the shipped limits: 8 Projects, 10 Topics, 12 Tags.
4. Exact compact request: metadata, purpose evidence, up to eight phrases, candidate definitions, system prompt and structured schema.
5. Later prediction, validation result and reference comparison.

Measure coverage of reviewed positive IDs at current, smaller and expanded candidate budgets. Compare alias-only, current TF-IDF and BM25 offline with a common registry/profile. Compare metadata/purpose-only, RAKE and isolated YAKE profiles without changing the shipped baseline. YAKE's research environment/licensing decision stays separate from production adoption.

Record whether supporting evidence is in metadata/README, only in supporting files, retained in the profile or present in the actual request. Exact quote containment diagnoses omissions; it does not establish entailment, and normalization can make substring checks inconclusive. Never inject human reference quotes into prompts merely to improve scores.

Run extraction/admission/candidate diagnostics on all 600 where sources meet app ceilings. Flag oversized or unsupported inputs; do not silently truncate them. Only the confirmed 30 receive human-reference metrics. No new GitHub crawl or OAuth login is required for the pinned local sources.

**Output:** stage traces, `local-retrieval.md`, `context-coverage.md`, size/token estimates, offline latency and failure categories. **Gate:** deterministic replay, no reference leakage, input ceilings enforced. No paid calls.

## Step 4 — Generate the missing live predictions

Keep configured roles: `gpt-6-luna` for primary classification; `gpt-6.1-sol` for a six-case development comparison, taxonomy discovery and a small supplementary grounding run on Luna outputs. Astra remains configured but is not needed for this initial budget. Verify current pricing, API compatibility and account access at execution. Use the first scheduled classification as the access check, avoiding extra generic probe calls.

| Task | Planned generations | Normal HTTP attempts* | Purpose |
|---|---:|---:|---|
| Primary classification of all 30 reviewed repositories | 30 | 60 | Fifteen development cases first; fifteen test-reserved after freeze |
| Comparison model on six fixed development cases | 6 | 12 | Same inputs/candidates; a small paired comparison, not an established winner |
| Two development taxonomy cohort drafts plus consolidation | 3 | 6 | Test discovery/consolidation, kinds, parents, supporting IDs and deduplication |
| Ragas grounding of four development outputs, allowing two judge generations each | Up to 8 | Up to 16 | Claim-support diagnostics; not judge calibration |
| **Planned total** | **Up to 47** | **Up to 94** | Compatible receipts reduce calls; framework replay does not regenerate predictions |

*The existing provider normally makes one serialized-input token-count request before one generation. Count-only failures, retries and framework subcalls consume the HTTP counter too. Generation and HTTP limits are different.

**Proposed authorization:** $1 total for this evaluation, also bounded by the remaining original $5 cumulative cap; at most 100 HTTP attempts and 50 generation attempts including contingency; at most 20 HTTP attempts in each checkpointed batch. This is a proposed new-run allowance, not a claim that earlier 20-request approval already authorized 100 requests.

A six-batch normal schedule is: 8 development classifications; 7 development classifications plus 1 comparison; 5 comparisons plus 3 taxonomy calls; up to 8 judge generations; then 8 and 7 locked test classifications. Normal HTTP totals are 16, 16, 16, 16, 16 and 14. Six spare HTTP attempts are contingency, not an instruction to retry every failure. Reduce work if any token, dollar, batch or framework-fanout bound would be exceeded.

Use the existing durable monetary ledger and explicit run-scoped grants. Do not reset ledgers, create a fresh ledger to evade spend, renew app-wide allowances silently or edit `.env` limits to bypass them. Persist experiment-wide and per-batch counters across restarts, reserving both count/generation slots before dispatch. Unknown usage retains its reservation. Refusals, timeouts and incomplete outputs are recorded instead of silently retried or counted as valid predictions.

The audit finds $0.127619 estimated historical charges, zero outstanding reservations/active holds and $4.872381 remaining under the original $5 cap. This is a local ledger estimate, not an account balance or invoice. Recheck it, all active holds and the pricing version before execution. Every new-call reservation, including judges/retries, must fit the $1 sub-ceiling.

Record prompt/schema/profile/candidate/registry/model/config hashes, requested/returned model, request ID, attempts, tokens/cache usage, cost estimate and latency. Distinguish fresh generation, matching replay and unavailable output. No silent token-ceiling increase or model substitution. Send only approved public saved-source snippets; no private README, OAuth secret or personal review note. Disable remote traces/telemetry.

Before test calls, freeze prompt, baseline retrieval, registry, schema, ceilings and scoring semantics. Version any development alternative separately. Do not select a configuration after inspecting test results and call it locked. Corpus-wide registry curation and prior aggregate inspection also prevent an “untouched external holdout” claim.

Taxonomy calls use only development evidence, not human label lists or test cases. Score structure, duplicate/parent rules, supporting-ID validity and traceability. Open-ended discovery is not exact canonical-ID classification; unmatched proposal meanings need review. Report two drafts and consolidation separately, and do not fabricate human rubric ratings or auto-publish a taxonomy.

## Step 5 — Score locally and using frameworks

### Metric contract

Keep every repository/concept outcome supported, unsupported or unknown. A removal is an observed correction; it is not automatically an evidence-backed negative with an invented rationale. New-vocabulary discoveries are separate from old-registry misses. An empty Project group does not imply that Topics and Tags have no match.

| Metric | Defensible interpretation |
|---|---|
| Candidate recall of reviewed positives | Human-retained IDs retrieved / reviewed positive IDs, by kind and vocabulary availability |
| Prediction recall of reviewed positives | Human-retained IDs selected / reviewed positive IDs; not exhaustive recall of all correct labels |
| End-to-end and candidate-conditional selection | Separate candidate omissions from generation errors; include skips/failures in coverage denominators |
| Positive-set agreement | Descriptive set overlap/exact matches; not exhaustive accuracy |
| Judged precision | Supported predicted pairs / explicitly supported-or-unsupported predicted pairs; show judgement coverage and unjudged count |
| Conventional precision/recall/F1 | Only for a declared sufficiently reviewed scope with compatible denominators; otherwise not estimable |
| Grounding | Supplied evidence supports, partially supports, contradicts or cannot resolve the claim; separate from label correctness |
| Operational metrics | Schema/ID/citation/parent validity; abstentions/refusals/timeouts; completed coverage; tokens/cost/latency/cache |

Create a compact **exceptions sheet** for predictions outside retained positives, consequential removals and ambiguous evidence. Agents/judges may suggest evidence-backed decisions but cannot promote them to human negatives. The user need not repeat all 30 reviews: only adjudicate exceptions if exhaustive precision/F1 is desired. Without further review, complete the release with honest reviewed-positive, grounding and coverage metrics and leave exhaustive F1 unavailable.

### Selected tools

| Tool | Role |
|---|---|
| Existing Python/Pytest harness | Authoritative partial-label scorer, traces, grouped summaries and quota/security checks |
| **Promptfoo** | Local regression runner; custom Python provider replays saved predictions and Python assertions use the same scorer. A missing receipt fails, with no live fallback |
| **Ragas** | ID-based recall cross-check for retrieved ontology-context IDs, explicitly named candidate-concept coverage; faithfulness of assignment claims against actual supplied evidence |
| DeepEval | Alternative if an adapter proves incompatible, not an additional automatic judge run |
| LangSmith / TruLens / Phoenix / Langfuse | Defer observability-platform setup; saved local traces/reports suffice for this milestone |

Promptfoo documents [custom Python providers](https://www.promptfoo.dev/docs/providers/python/) and [Python assertions](https://www.promptfoo.dev/docs/configuration/expected-outputs/python/). Ragas documents [ID-based recall](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_recall/) and [faithfulness](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/). A concept-ID coverage score is not passage-retrieval accuracy merely because the same formula is used.

For faithfulness, deterministically express assignments as claims about primary purpose/technology, linked to their definitions. Candidate definitions explain meanings; their presence does not prove repository properties. Judges receive the actual request evidence, not withheld full sources that the producer never saw. Separate label correctness, grounding and human preference.

Pin supported framework versions in an isolated evaluation environment. Use current APIs: Ragas distinguishes collections-based APIs from legacy metric APIs. Verify actual inner-call fanout with stubbed transports before live use. All framework generation routes delegate to the same budget guard; no raw SDK bypass. Enable no default embeddings, answer-relevancy metric with hidden embedding calls or synthetic test generation. Four semantic cases establish integration/diagnostics, not calibrated judge reliability, a universal 0.85 gate or safe unattended auto-apply.

OpenAI's [evaluation guidance](https://developers.openai.com/api/docs/guides/evaluation-best-practices) supports task-specific metrics and checking judges against human judgements. Avoid a new dependency on its hosted Evals platform: [current deprecation guidance](https://developers.openai.com/api/docs/deprecations) lists read-only operation from October 31 and shutdown on November 30, 2026. The selected local route avoids that migration dependency.

**Output:** local JSON/Markdown scores, local Promptfoo results, Ragas ID/grounding results, deterministic-score agreement checks, exceptions and limitations. Reruns score saved outputs rather than repeating generations.

## Step 6 — Finish reporting and the publication

| Proposed location | Contents |
|---|---|
| `eval/ai-system-design/evaluation/reviewed-30-v1/` | README, contract, reproducible runner/adapters, pinned config/environment and tests; created after approval |
| `docs/validation/private/corpus-600-v2/evaluation-reviewed-30-v1/` | Frozen owner reference, registry history, stage traces, call receipts, predictions and exception decisions |
| `docs/validation/ground-truth-evaluation-<run-date>.md` | Results, per-stage/slice tables, usage, exclusions, failures and limitations |
| `eval/ai-system-design/ground-truth-creation/` | Preserve prior revision; refresh article/statistics/evidence with measured results and current links |

The reference remains viewable in **Public - Ground Truth**. Evaluation is file-driven and needs no app login. This milestone adds no evaluation dashboard or automatic write of predictions into reference assignments. The exceptions sheet can link repository/source/label identities; an in-app negative/completeness editor would be a separate UX change.

Keep local diagnostics, live outputs and framework checks as separate evidence. Preserve original sources/proposals, A/B records, human history, prior Phase 0.5 benchmarks and budget receipts, academic/illustrated articles, diagrams and safety fixtures. External publishing is not included.

## Approval and completion

Approval covers adapters/tests, isolated pinned framework installation, read-only reference freeze, the bounded call schedule and local reports/publication-draft updates. It does not authorize new cloud resources, GitHub crawling/writes, hosted uploads, a higher cumulative dollar cap or automatic judge-to-human promotion.

Completion means: immutable input/reference manifests; accurate statistics; replayable local stage measurements; scheduled predictions or explicit failures/exclusions; Promptfoo and Ragas artifacts; actual usage; an exceptions-only review sheet if needed; and an updated publication without unsupported F1/holdout/judge-calibration claims. Hard call/dollar limits take precedence over optional comparisons.

Preparation/statistics are complete and execution is approved. Stop at the approved limits and ask before any additional generation allowance. [AGENTS.md](../../AGENTS.md) requires approval for a later implementation-scope expansion.
