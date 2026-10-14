# Phase 0.5 — primary-label validation round 2

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
