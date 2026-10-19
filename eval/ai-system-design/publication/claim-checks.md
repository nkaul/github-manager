# Editorial claim checks

Checked against the existing source audit and frozen public/synthetic reports. No fresh repository classification, taxonomy call or quality benchmark was run to write these drafts.

| Editorial claim | Evidence | Qualification |
|---|---|---|
| Label coverage, processing, freshness and review are separate | [ADR 0005](../../../docs/adr/0005-durable-analysis-and-local-reconciliation.md), [analysis validation](../../../docs/validation/phase-0-9-taxonomy-and-analysis.md) | No Project does not mean no useful Topic/Tag or no completed analysis |
| Primary-only prompt clarification corrected FastAPI's extra assignments | [Phase 0.5 results](../../../docs/validation/phase-0-5-results.md), [reference approval](../../../docs/validation/phase-0-5-reference-review.md) | Reused cases; not an independent causal effect-size estimate |
| Context uses selected blocks and bounded phrases | [Academic methods](../github-manager-ai-system-design.md#5-ingestion-chunking-and-evidence-provenance), [evidence index](../evidence-index.md) | Heuristic selection and truncation can omit relevant information |
| Lexical cosine/BM25 recovered four Topics missed by alias-only matching | [Aggregates](../measurements.json), [Phase 0.5 results](../../../docs/validation/phase-0-5-results.md) | Small registry, generous caps; no observed BM25 advantage or dense comparison |
| The app's TF-IDF label denotes binary-IDF cosine | [Exact implementation analysis](../github-manager-ai-system-design.md#7-retrieval-strategy-sparse-candidates-first) | Do not present it as default count-based TF-IDF |
| A receipt prevents ordinary repeat inference, including successful NO_MATCH | [ADR 0005](../../../docs/adr/0005-durable-analysis-and-local-reconciliation.md) | Explicit refresh remains available; failures/uncertainty/unknown history do not get silent retries |
| Runtime checks preserve user decisions and fence stale results | [Analysis validation](../../../docs/validation/phase-0-9-taxonomy-and-analysis.md) | Tested local behavior; not a semantic correctness proof or distributed cloud guarantee |
| Count/reserve/settle and finite adaptive budgets retain cumulative cap | [ADR 0004](../../../docs/adr/0004-cohorts-and-adaptive-budgets.md), [adaptive canary](../../../docs/validation/phase-0-9-adaptive-live-20261013T145429Z.md) | Counting is a distinct HTTP operation; unknown cost remains reserved |
| Latest round: 50 TP / 0 FP / 2 FN, P 100%, R 96.2%, micro F1 98.0% | [Round 2](../../../docs/validation/phase-0-5-round-2-results.md), [recomputed aggregates](../measurements.json) | Twenty reused cases: eight public/twelve synthetic; no independent generalization |
| 16,041 input / 3,414 output, $0.003319 ledger estimate | [Recomputed aggregates](../measurements.json) | Dated rates, per-call rounding; excludes infrastructure/review and invoice reconciliation |
| One purpose-only representation used 932 tokens versus 988 with RAKE, same assignments | [Earlier smoke/ablation](../../../docs/validation/phase-0-5-results.md) | One FastAPI case under earlier prompt; no broad winner |
| Current product is local Next.js/FastAPI/SQLite | [ADR 0002](../../../docs/adr/0002-phase09-local-workspace.md) | Approved AWS runtime remains deferred |

Both earlier articles and all their diagrams are protected by [the preservation manifest](prior-editions-preservation.json). The publication edition adds a shorter narrative and simplified illustrations without revising the original evidence or claims.
