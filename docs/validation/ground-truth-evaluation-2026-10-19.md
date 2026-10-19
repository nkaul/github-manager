# Ground Truth evaluation — October 19, 2026

**Completed within the approved limits.** Thirty human-confirmed repositories now have real model predictions, local scores, Promptfoo replay and Ragas checks. The model selected **66 of 83 reviewed positive labels (79.5%)**. Retrieval supplied **69/83 (83.1%)**; the model selected **66/69 supplied positives (95.7%)**. Most measured misses originated before generation. These percentages measure recovery of saved positive labels, not exhaustive accuracy.

The new evaluation cost is **$0.133941 in estimated recorded API charges**. All **50 generation attempts and 100 HTTP attempts** were consumed; the run grant is **FINISHED**, with no outstanding call reservations or unused active hold. Further generations require another approval. Combined historical accounting, including retained narration reservations, is **$4.316970 under the original $5 cap**. This is local accounting, not an invoice or account-balance claim.

[Approved plan](../planning/ground-truth-evaluation-completion-2026-10-19.md) · [reference audit](ground-truth-review-completion-2026-10-19.md) · [reproduction guide](../../ai-system-design/evaluation/reviewed-30-v1/README.md) · [publication update](../../ai-system-design/ground-truth-creation/evaluation-results-2026-10-19.md).

## What the reference permits us to claim

The frozen reference contains **30 distinct repositories, one human review owner and 83 positive assignments**: 15 Project, 35 Topic and 33 Tag. Fifteen repositories are development and fifteen test-reserved, preserving 18 leakage groups. The effective producer vocabulary contains 339 concepts; historical review bindings remain at v0/v1/v2. Domains derive from Project parents; sampling domains are collection buckets, not direct assignment targets.

All 30 records retain `UNKNOWN_NOT_NEGATIVE`. Sixteen additional predicted repository/label pairs therefore remain **unjudged**, not false positives. There are no explicitly adjudicated negatives. Conventional exhaustive precision and F1 are **not estimable**. The scorer's conditional `judged_precision=1.0` describes only its already-supported subset and is not overall precision; 66/82 predicted pairs have human-positive coverage.

This selected, single-reviewer sample has uneven coverage and no cloud case. Prior corpus/vocabulary curation and aggregate inspection also prevent calling it an untouched external holdout. Prompt, registry, candidates, scorer and adapter configuration were frozen before the fifteen test generations. No alternative was selected from test results.

## Classification results

| Facet | Reviewed positives | Retrieved | Model selected | Recovery of reviewed positives | Extra unjudged predictions |
|---|---:|---:|---:|---:|---:|
| Project | 15 | 14 | 13 | 86.7% | 0 |
| Topic | 35 | 23 | 23 | 65.7% | 6 |
| Tag | 33 | 32 | 30 | 90.9% | 10 |
| **All** | **83** | **69** | **66** | **79.5%** | **16** |

All thirty final primary outputs passed structured-schema, canonical-ID, candidate-membership and citation-ID validation. They contain 82 assignments. Ten repositories exactly match the retained positive set; this is descriptive set agreement, not exhaustive correctness. Empty Project groups remain valid.

| Split | Repositories | Positives | Retrieved | Selected | Selected / positives | Selected / supplied positives |
|---|---:|---:|---:|---:|---:|---:|
| Development | 15 | 42 | 33 | 32 | 76.2% | 97.0% |
| Test-reserved | 15 | 41 | 36 | 34 | 82.9% | 94.4% |

Fourteen of seventeen missed positives were absent from the supplied candidate list: one Project, twelve Topics and one Tag. The three supplied-but-not-selected positives were Python for `airbytehq/airbyte`, Docker for `anchore/grype`, and the Apache Fineract Project for `apache/fineract-chat-archive`. Those remain reference misses; evidence packing and policy/granularity need inspection before assigning a cause.

A deterministic 1,000-resample bootstrap over 18 leakage groups yields a descriptive interval of **69.1–88.9%** for reviewed-positive recovery. It describes resampling this selected set, not population uncertainty across GitHub.

### Sampling-domain slices

| Collection bucket | Repositories | Positives | Retrieved | Selected |
|---|---:|---:|---:|---:|
| AI | 3 | 8 | 6 | 6 |
| Commerce | 3 | 8 | 6 | 6 |
| Data | 10 | 29 | 23 | 22 |
| Developer tools | 1 | 2 | 2 | 2 |
| Education | 2 | 3 | 3 | 3 |
| Finance | 6 | 19 | 15 | 14 |
| Healthcare | 1 | 4 | 4 | 4 |
| Science | 2 | 5 | 5 | 5 |
| Security | 2 | 5 | 5 | 4 |
| Cloud | 0 | 0 | — | — |

Tiny slices cannot establish domain-wide reliability even when every retained positive is recovered.

## Retrieval and context measurements

The application uses sparse TF-IDF with an alias-token boost over canonical definitions. RAKE profiles, compact repository evidence and candidate definitions feed the existing LangChain structured-output classifier. There are no dense embeddings, vector database, Jev implementation or reranker in this path. These are ontology-candidate retrieval evaluations, not passage-search or conversational-answer benchmarks.

| Retrieval method | Projects /15 | Topics /35 | Tags /33 | All /83 |
|---|---:|---:|---:|---:|
| Alias-token baseline | 13 (86.7%) | 15 (42.9%) | 32 (97.0%) | 60 (72.3%) |
| **Shipped TF-IDF + alias boost** | **14 (93.3%)** | **23 (65.7%)** | **32 (97.0%)** | **69 (83.1%)** |
| BM25 + alias boost, same limits | 15 (100%) | 24 (68.6%) | 32 (97.0%) | 71 (85.5%) |
| TF-IDF with doubled candidate limits | 15 (100%) | 24 (68.6%) | 32 (97.0%) | 71 (85.5%) |
| BM25 with doubled candidate limits | 15 (100%) | 26 (74.3%) | 32 (97.0%) | 73 (88.0%) |

Shipped limits are 8 Projects, 10 Topics and 12 Tags. A later local exploration with half those limits retrieves 64/83. Metadata-only and packed-purpose-evidence queries each retrieve 68/83; top-eight-RAKE-phrases-only retrieves 47/83. Equal totals can hide different label sets. These exploratory diagnostics did not change live requests or select a production replacement. Larger lists require measuring token, latency and generation effects before adoption.

RAKE and isolated YAKE extraction ran on the same thirty profiles. The shipped ranker queries evidence text rather than phrase scores: replacing those phrases alone cannot change candidate recall. No paid extractor-versus-generation ablation ran, and neither extractor is declared the quality winner.

Recorded supporting quotes exist for all 83 positive pairs. Exact containment finds 29 in the extracted profile and 23 in the compact request; whitespace/case-normalized checks find 33 and 27 respectively. Candidate definitions are excluded. This lexical diagnostic does not establish semantic evidence recall: section selection, supporting files, formatting and alternative supporting passages all matter. Human reference quotes were not injected into requests.

Extraction/admission/candidate diagnostics completed for **600/600 repositories**, with no excluded input, in approximately 19 seconds on this machine. This is one operational run; the other 570 repositories supply no human classification-accuracy denominator.

## Model comparison and taxonomy discovery

Primary classification used `gpt-6-luna`. Three paired development cases used identical evidence/candidates with `gpt-6.1-sol`: Luna recovered **6/9 positives**, Sol **7/9**, from seven retrieved positives. Each produced two extra unjudged labels. This small comparison cannot establish a winner or a reliable quality/cost tradeoff. It stayed at three rather than six cases to preserve the hard attempt cap after adapter repairs.

Taxonomy discovery used only development evidence, without human label lists or test cases. Two Sol cohort drafts produced 13 proposals each; consolidation produced 20: **5 Domains, 1 Project, 12 Topics and 2 Tags**. All three calls passed existing schema, kind, duplicate-name, parent and supporting-repository-ID checks. Consolidated proposals cite fourteen of fifteen development repositories; complete repository coverage was not a validator requirement.

This demonstrates structure and traceability, not semantic deduplication, appropriate granularity or human-rated taxonomy quality. No proposal was published into the app, and no human taxonomy rubric score was invented.

## Framework results

| Check | Observed result | Interpretation |
|---|---|---|
| Local partial-label scorer | 66/83 selected; 69/83 retrieved; 16 unjudged predictions | Authoritative metric contract |
| Promptfoo 0.124.1 saved-output replay | 30/30 contract checks pass; all per-case scores match local scoring | Valid IDs/citations and adapter agreement; **not 100% semantic accuracy** |
| Ragas 0.4.3 ID-based context recall | Per-case checks and all weighted facet aggregates match local scores | Candidate-concept-ID coverage, not passage relevance |
| Ragas collections Faithfulness | Three cases: **1.0, 1.0, 0.75**; macro mean **0.9167** | Small grounding diagnostic, not calibrated judge reliability |
| Evaluation harness | 4/4 tests pass; Ruff checks pass | Partial-label semantics, namespace isolation, durable caps and count-request headroom |

The grounding judge receives actual supplied evidence and deterministic claims expressing predicted relationships. Definitions explain meanings and are separated from repository facts. For `airbytehq/airbyte-python-cdk`, it supported the Airbyte relationship, API-development capability and Python technology. It rejected GraphQL as a **primary technology** because connector support alone did not establish that role. This is a judge decision, not a new human-negative reference.

Each faithfulness case used two generations, verified first with a no-network stub. The Ragas worker blocks direct sockets and routes all judge calls through the original guarded provider/ledger. No embedding calls, synthetic-test generation or automatic retry occurred. Promptfoo replay consumed zero model tokens and added no generations; its provider invocation count represents local replay, not HTTP calls.

Faithfulness uses the current collections API. Installed Ragas 0.4.3 exposes `IDBasedContextRecall` only through its legacy export, despite a deprecation message pointing to a missing collections export; the adapter records that compatibility limit. Unused incompatible LangGraph/classic packages left by initial resolution were removed from the isolated evaluation environment. The final pinned environment passes `pip check` and the exact-two-call stub. The application environment remains unchanged. Remote tracing/telemetry and hosted sharing are disabled.

## Attempts, failures, tokens and cost

Approved ceilings were $1 for this evaluation, the remaining original $5 cumulative allowance, 50 generation attempts, 100 HTTP attempts and 20 HTTP attempts per batch. Cross-ledger reconciliation found **$4.183029** of prior classification/demo/narration accounting, leaving **$0.816971** at admission. The earlier $4.872381 figure covered the classification ledger alone and was corrected before execution.

The first eight generations returned HTTP 200, but the new adapter rejected their corpus workspace namespace. This was an adapter mistake, not eight demonstrated model-quality failures. The correction validates in an isolated namespace without changing canonical IDs, prompts or evidence; a regression test covers base/extension concepts. All failed receipts and costs remain counted. Initial raw response bodies were not retained; later successful raw bodies are stored privately. Eight explicit replacements ran, with no hidden retry.

To stay within unchanged ceilings, comparison cases were reduced from six to three and grounding cases from four to three. Final allocation: **38 primary attempts including eight rejected attempts, 3 comparison generations, 3 taxonomy generations and 6 judge generations**. Six batches used **20, 20, 18, 12, 16 and 14 HTTP attempts**. All fifty calls settled. The run grant is finished and its unused hold released; historical media reservations remain accounted for.

| Task | Generations | Input tokens | Output tokens | Estimated recorded USD |
|---|---:|---:|---:|---:|
| Primary classification, including eight rejected attempts | 38 | 60,789 | 10,999 | $0.016324 |
| Paired classification comparison | 3 | 4,956 | 593 | $0.028211 |
| Two taxonomy drafts and consolidation | 3 | 5,676 | 3,811 | $0.063630 |
| Ragas claim extraction and support judgement | 6 | 5,196 | 678 | $0.025776 |
| **Total** | **50** | **76,617** | **16,081** | **$0.133941** |

Total usage is 92,698 tokens. The 4,777 reasoning output tokens are already included in output usage. The provider reports 13,287 cached input and 61,443 cache-write tokens; these are input subcategories, not additional tokens to add. Ledger rates bind to `openai-standard-short-2026-10-13`; older provider receipts preserve historical `price_date` metadata. No invoice-level savings percentage is inferred.

Thirty successful primary whole-call latencies, including input counting/local validation, were **p50 4.188 seconds, nearest-rank p95 7.021 seconds**, range 2.474–8.257. Serialized input counts were 1,063–1,846 tokens, within the 2,000-token ceiling; p50 was 1,614.5. These exclude rejected attempts from that latency distribution and are not production SLAs.

## Artifacts, preservation and next decisions

Private artifacts persist under `docs/validation/private/corpus-600-v2/evaluation-reviewed-30-v1/`: frozen sources/reference bindings, exact producer payloads, profiles, predictions, taxonomy drafts, judge requests/results, framework outputs and counters. Start with `manifest.json`, `test-freeze.json`, `evaluation-summary.json`, `final-checks.json`, `exceptions.md`, `promptfoo-results.json`, `ragas-results.json` and `preservation-check.json`. Owner-specific reference records and full source snapshots were not copied into the public publication package.

Preservation passed for **2,423 manifest-bound source/dossier files**, **548 prior readiness/benchmark/pilot artifacts**, the source manifest, frozen producer/input hashes and the archived publication. An earlier audit matched all three real raw workspace states. A final recheck observed a live GitHub sync at `2026-10-19T05:30:40Z`: the GitHub workspace changed, while Ground Truth/sample states, all thirty frozen review records and registry history remained identical. The evaluation opens app SQLite read-only and retained that concurrent observation without rollback. The 91 non-evaluation ledger rows and $0.127619 historical accounting remain present; the monetary database changed intentionally for approved calls. Earlier articles, diagrams, corpus proposals and benchmark paths remain preserved. No login, app restart, production configuration change or model-output write into human references was needed.

The exceptions sheet covers **20 repositories**, including sixteen extra unjudged predictions and seventeen missed positives. The original thirty confirmations remain complete. Further human review is optional for this completed milestone; adjudicate extras if exhaustive precision within a declared reviewed scope is required.

The strongest next experiment is versioned, development-only improvement of Topic retrieval, followed by a fresh evaluation set. Inspect misses and source/context availability before expanding prompts or changing models. Measure generation/token effects of BM25 and larger candidate budgets, then calibrate judges against explicit human support decisions. No extra generation is needed to report this run, and none is authorized beyond the exhausted limits.
