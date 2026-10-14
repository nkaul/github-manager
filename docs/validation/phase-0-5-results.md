# Phase 0.5 — AI readiness results

Review date: October 12, 2026 (America/New_York).

Status: **CONDITIONAL GO for review-first AI; production/comparison limits remain.** Phase 0.5 implementation is approved. Offline algorithms and safety tests have run; live results are recorded below. No automatic taxonomy publication, GitHub mutations or AWS changes occurred.

Plan: [AI readiness pre-testing](../planning/phase-0-5-ai-readiness.md). Run instructions: [local setup](../development/phase-0-5-ai-readiness.md).

## Actual validation

| Check | Evidence | Status | Result |
|---|---|---|---|
| Ruff backend | LOCAL_TEST | PASS | All checks passed. |
| Backend regression | LOCAL_TEST | PASS | 81 passed in 4.18s; includes atomic concurrent request-count cap. |
| Twenty-call round audit | LOCAL_AUDIT_OF_LIVE_PROVIDER | PASS | 20 distinct paid reservations, 20 live HTTP 200 generations/counts, 20 unique cases; no replays/retries; cumulative attempts 34. |
| Public corpus | LIVE_GITHUB | PASS | 10 allowlisted public repos; public visibility, numeric IDs, README SHAs and license metadata recorded |
| RAKE / YAKE | LOCAL_ALGORITHM | PASS | 30 profiles each; source spans and selected purpose evidence; no runtime tokenizer downloads |
| Reference labels | HUMAN_REVIEW | RECORDED | Public labels/registry approved by user; synthetic fixture truth |

## Latest primary-label validation

Outcome: **PASS_CONTRACT**; planned quality targets met: **True**. Exactly **20** additional model-generation requests, four concurrent isolated clients, **17.078s** wall time. Existing access evidence was reused; no login probes, retries, candidate expansions or extra model calls. Each generation also used its required input-count request before a durable spending reservation.

The same frozen evaluation partition contains 8 public + 12 synthetic cases. Primary-label instructions were fixed before this round; no labels or extractor outputs changed. Models never received reference labels. Three evaluation cases had already informed the user's policy clarification, so this is a regression validation on a reused corpus, not an independent production generalization estimate.

| Kind | TP / FP / FN | Positive repos / labels | Precision | Recall | F1 |
|---|---|---|---|---|---|
| PROJECT | 10 / 0 / 0 | 8 / 10 | 100.0% | 100.0% | 100.0% |
| TOPIC | 18 / 0 / 1 | 18 / 19 | 100.0% | 94.7% | 97.3% |
| TAG | 22 / 0 / 1 | 18 / 23 | 100.0% | 95.7% | 97.8% |
| ALL | 50 / 0 / 2 | 18 / 52 | 100.0% | 96.2% | 98.0% |

| Source | Repos | Micro TP / FP / FN | Precision | Recall | F1 |
|---|---|---|---|---|---|
| PUBLIC_GITHUB | 8 | 16 / 0 / 0 | 100.0% | 100.0% | 100.0% |
| SYNTHETIC | 12 | 34 / 0 / 2 | 100.0% | 94.4% | 97.1% |

| Case | Extra labels | Missing labels |
|---|---|---|
| synthetic/helios-dashboard | — | Telemetry |
| synthetic/helios-audit | — | python |

FastAPI now returns only Web APIs/python, correcting the earlier two secondary assignments. No false-positive project membership was observed, and the two empty/fork no-match cases remained unassigned. Missing Telemetry on Helios Dashboard and python on Helios Audit are retained as measured misses; no further tuning/retest occurred after this round.

Per-request latency including count/client work: n=20, p50=2.974s, p95=4.749s. Concurrent-run latency is not directly comparable with the earlier serial smoke subset. This small sample does not establish production service levels.

Round estimated spending: **$0.003319**. Experiment total: **$0.052212 / $5.00**; outstanding reservations **$0.000000**. Durable attempt count 14 → 34; the 34-attempt ceiling is reached. Prices were rechecked October 12; estimates use the existing conservative method and are not invoice reconciliation.

Executed model `gpt-6-luna`; prompt hash `138ecbb1eb0c9202b26067bad9c7e7808020375b57a97e7830285cade6d49dd3`; schema hash `57492877e2aed355f4cac60ed7332b1190e7ffbf6c7bc67d7917a2e543f7f0f9`. Per-case actual returned models, request IDs, counts, cached/input/output/reasoning usage, errors and outputs are preserved in ignored mode-0600 `validation-round-2.local.json`, individual case JSON and immutable `ai-primary-round2-*.md`/JSON reports.

Recommendation: **CONDITIONAL GO for review-first AI feasibility**. Keep Luna for classification and Sol for taxonomy as preflight defaults in backend/.env. Astra/full paired Sol comparison, numeric human rubric, broader multilingual extraction, README-format noise correction, large stability/compaction and independent production evaluation remain explicit limits. No production auto-apply, Phase 1 implementation or new data authorization follows from this result.

## Real provider checks

The official Responses input-token endpoint is called on the actual LangChain payload, including JSON Schema, before a durable maximum-cost reservation and generation. Token-count success is authentication/connectivity evidence; it does not prove successful model generation or model quality.

| Candidate | Count HTTP | Generation HTTP | Outcome / sanitized code |
|---|---|---|---|
| gpt-6-luna | 200 | 200 | PASS: Structured call completed |
| gpt-6.1-sol | 200 | 200 | PASS: Structured call completed |

Credit was restored and actual LangChain strict-schema generation now succeeds for Luna and Sol. Four earlier rejected attempts and the diagnosed `credit_balance_exhausted` failure are preserved in immutable local reports. Astra was not retried after the user requested limiting calls.

## Local extraction and retrieval

Frozen corpus: `7c9d88ed1a2e31c1b5638e8ad75e0aaf892fe18b16a3d7e5520a0ddf4998693c`. 30 cases: 10 public + 20 synthetic; 10 development + 20 held-out. Related repositories stay in the same split. Reference labels are never sent to models.

| Method | Held-out PROJECT recall@8 | TOPIC recall@10 | TAG recall@12 |
|---|---|---|---|
| alias | 10/10 (100.0%) | 15/19 (78.9%) | 23/23 (100.0%) |
| tfidf | 10/10 (100.0%) | 19/19 (100.0%) | 23/23 (100.0%) |
| bm25 | 10/10 (100.0%) | 19/19 (100.0%) | 23/23 (100.0%) |

Development comparison chose **tfidf** with a stable tie-break favoring the simpler TF-IDF baseline. Retrieval recall measures whether expected concepts reach the shortlist; it is not classification precision, taxonomy usefulness or production coverage. Reference status: user approved; see [reference review](phase-0-5-reference-review.md).

Extraction wall time: RAKE 0.249s; YAKE 12.669s for 30 profiles. YAKE includes 30 isolated process startups, so this is not a fair intrinsic algorithm-speed comparison. Phrase samples received qualitative acceptance; numeric usefulness ratings were not supplied. The development Spanish case exposes a lexical/English-extraction limitation.

## Earlier smoke results — before primary-label clarification

The user restored API credit and requested fewer calls. This continuation made **10 generation requests**: two access probes, one 30-repository taxonomy draft, three Luna classifications, one paired Sol classification, two Luna representation checks and one fresh Luna repeat. All ten passed strict-schema and semantic validation. No implicit retry occurred. This is a smoke subset, not the full API benchmark.

| API model | Repos | Kind | TP / FP / FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|
| gpt-6-luna | 3 | PROJECT | 2 / 0 / 0 | 100.0% | 100.0% | 100.0% |
| gpt-6-luna | 3 | TOPIC | 3 / 1 / 0 | 75.0% | 100.0% | 85.7% |
| gpt-6-luna | 3 | TAG | 3 / 1 / 0 | 75.0% | 100.0% | 85.7% |
| gpt-6-luna | 3 | ALL | 8 / 2 / 0 | 80.0% | 100.0% | 88.9% |
| gpt-6.1-sol | 1 | PROJECT | 0 / 0 / 0 | — | — | — |
| gpt-6.1-sol | 1 | TOPIC | 1 / 1 / 0 | 50.0% | 100.0% | 66.7% |
| gpt-6.1-sol | 1 | TAG | 1 / 1 / 0 | 50.0% | 100.0% | 66.7% |
| gpt-6.1-sol | 1 | ALL | 2 / 2 / 0 | 50.0% | 100.0% | 66.7% |

The fixed Luna subset is FastAPI, Orion Audit (two initiatives), and Negated API (explicitly unrelated initiatives); Sol was paired only on FastAPI. Luna TOPIC/TAG precision is 75% against the approved minimum references, below the 85% target; project support is only one positive repository. Both models add FastAPI's Data Validation topic and fastapi tag. The user adjudicated these as unwanted secondary labels: use primary labels only. These are valid IDs but wrong assignments under that rule. The executed prompt did not state the rule as clearly as the subsequent refinement. Original labels/scores are preserved; these slices cannot close quality gates.

| Task / model | Returned ID | Input | Cached / written | Output (reasoning) | Seconds |
|---|---|---|---|---|---|
| access / gpt-6-luna | gpt-6-luna | 82 | 0 / 0 | 17 (0) | 2.882 |
| access / gpt-6.1-sol | gpt-6.1-sol | 82 | 0 / 0 | 17 (0) | 2.35 |
| taxonomy-limited / gpt-6.1-sol | gpt-6.1-sol | 4897 | 0 / 4894 | 2106 (95) | 30.644 |
| classification / gpt-6-luna | gpt-6-luna | 988 | 0 / 0 | 312 (108) | 3.272 |
| classification / gpt-6-luna | gpt-6-luna | 755 | 0 / 0 | 299 (82) | 3.375 |
| classification / gpt-6-luna | gpt-6-luna | 785 | 0 / 0 | 184 (60) | 3.637 |
| classification / gpt-6.1-sol | gpt-6.1-sol | 988 | 0 / 0 | 210 (0) | 4.4 |
| ablation-baseline / gpt-6-luna | gpt-6-luna | 932 | 0 / 0 | 279 (85) | 3.073 |
| ablation-yake / gpt-6-luna | gpt-6-luna | 955 | 0 / 0 | 264 (66) | 3.766 |
| classification / gpt-6-luna | gpt-6-luna | 988 | 0 / 0 | 332 (126) | 3.956 |

Reasoning tokens are included in output totals and are not added twice. Admission and recorded estimates conservatively include input plus reported cache-write charges; these are local estimates, not invoice reconciliation.

- API classification `gpt-6-luna`: n=3, p50=3.375s, p95=3.637s including token counting/client work. Tiny-sample percentiles do not establish production latency.
- API classification `gpt-6.1-sol`: n=1, p50=4.4s, p95=4.4s including token counting/client work. Tiny-sample percentiles do not establish production latency.

| FastAPI / Luna input | Input tokens | Reference micro-F1 | Same labels as RAKE |
|---|---|---|---|
| RAKE + purpose | 988 | 66.7% | True |
| baseline | 932 | 66.7% | True |
| yake | 955 | 66.7% | True |

One fresh Luna repeat: assignment-set agreement=True. This is one pair; summary/confidence equality and broad stability are not established. The metadata+purpose baseline used fewer input tokens than either keyword variant on this one repository. No extraction/model winner is selected from this ablation.

The API Sol taxonomy draft passed supporting-ID/type/hierarchy validation. The user qualitatively accepted the [actual drafts](private/ai-pretest/taxonomy-review.md) and [10 public extraction samples](private/ai-pretest/extraction-review.md). Local organization simulation preserved manual choices/rejections and derived domains; fixtures cover queued/running/completed/partial-failed states and counts. it does not establish production worker durability or concurrency.

Extraction review exposed real noise: pytest's README contains reStructuredText image/target markup that the Markdown-only parser retains, and some RAKE phrases are generic prose. Add an explicit README-format policy and noise fixtures before promoting this extractor. Do not silently rebuild frozen evidence after seeing model results.

Recommend Sol for review-first taxonomy and Luna for review-first classification as preflight defaults, based on the successful API evidence and qualitative review. This does not establish superiority over the deferred Astra/Sol comparisons. The small preflight cannot authorize production auto-apply; the later 100–200 human-reviewed evaluation remains required.

Human review: the user reviewed the drafts/extraction samples and said **looks ok**. Recorded as qualitative acceptance; no numeric rubric or ≥4/5 mean is inferred. The user requires **primary labels only**, so FastAPI's extra labels are overclassification for this test. The prompt now states that rule; the clarified prompt was tested on all 20 frozen evaluation cases in round 2.

Supplementary [Codex results](phase-0-5-codex-results.md) contain actual ChatGPT-authenticated 20-case Sol/Luna batches and a taxonomy draft. Those results are attributed separately and do not substitute for this API benchmark.

## Spending, persistence and artifacts

Experiment cap **$5.00**; estimated generation spend **$0.052212**; outstanding maximum reservations **$0.000000**; remaining allowance **$4.947788**. Ledger generation attempts: 34. Rejected-before-generation requests settle at zero; this is not an invoice reconciliation. The allowance persists across invocations and includes retries; uncertain charges retain their reservation. SDK/LangChain automatic retries are disabled.

SQLite stores run/reservation/cache state under ignored `docs/validation/private/ai-pretest/`; reports and local JSON use mode 0600. No raw README content is included in this shareable summary. The key stays server-only; live calls require a CLI flag and environment override. Remote tracing is disabled.

Exact evaluation packages are locked in `backend/uv.lock`. YAKE 0.7.3 is isolated under `.tools/yake`, pinned in `backend/requirements-ai-yake.txt`; its installed artifact identifies AGPLv3/commercial licensing. Local evaluation does not approve production adoption.

Private artifacts: `frozen-corpus.local.json`, `public-corpus.local.json`, `offline.local.json`, `access.local.json`, `benchmark.local.json`, `dependencies.local.json`, `runs.sqlite3`, and immutable `ai*.md`/paired JSON reports. The initial sandbox-network failure and original provider failures are preserved.

## Remaining gates

1. The 20-case Luna API validation is complete. The total ceiling of 34 attempts (14 prior + 20 newly authorized) is reached. Astra and a full paired Sol classifier comparison remain deferred; no further paid calls follow automatically.
2. Reference labels/registry are approved; drafts/extraction qualitatively accepted; numeric rubric remains unscored.
3. Classification preflight targets pass. Independent 100–200 case production evaluation, larger compaction/stability coverage and README-format noise fixes remain later gates; models are preflight recommendations, not comparative winners.
4. Review the completed Phase 0.5 report; Phase 1 remains separately unapproved. Phase 0's broader provenance/watch/SSO limitations remain open.

Optional browser authentication was not needed for the public/synthetic CLI checks. There is no paid-run web endpoint or unauthenticated browser spend path.

References: [OpenAI token counting](https://developers.openai.com/api/docs/guides/token-counting), [pricing](https://developers.openai.com/api/docs/pricing), [LangChain integration](https://docs.langchain.com/oss/python/integrations/chat/openai).
