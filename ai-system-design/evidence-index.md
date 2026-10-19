# Evidence index

Audit: October 14, 2026. Baseline commit: `3ffac3f1ed6618b80045c3ffafc050f50d102d10`.

Implementation claims come from source inspection. Measurements come from dated experiment records; design and historical proposals are separate evidence classes. No new provider calls were made.

## Implementation trace

| ID | Source / entry point | Claim |
|---|---|---|
| I01 | [backend/app/pretest/ai/evidence.py:58](../backend/app/pretest/ai/evidence.py#L58) · `selected_evidence` | README selection, bounds and provenance |
| I02 | [backend/app/pretest/ai/evidence.py:92](../backend/app/pretest/ai/evidence.py#L92) · `rake_phrases` | RAKE configuration and isolated YAKE comparison |
| I03 | [backend/app/pretest/ai/evidence.py:184](../backend/app/pretest/ai/evidence.py#L184) · `Retriever` | Binary-IDF cosine / BM25 / alias candidate retrieval |
| I04 | [backend/app/pretest/ai/chains.py:33](../backend/app/pretest/ai/chains.py#L33) · `classification_input` | Prompt assembly and primary-label instructions |
| I05 | [backend/app/pretest/ai/schemas.py:45](../backend/app/pretest/ai/schemas.py#L45) · `validate_classification` | Structural and application validation |
| I06 | [backend/app/pretest/ai/provider.py:19](../backend/app/pretest/ai/provider.py#L19) · `BudgetedProvider` | Strict LangChain calls, exact counting and replay cache |
| I07 | [backend/app/pretest/ai/storage.py:39](../backend/app/pretest/ai/storage.py#L39) · `Ledger` | Durable cumulative cost reservations and settlement |
| I08 | [backend/app/pretest/ai/evaluation.py:5](../backend/app/pretest/ai/evaluation.py#L5) · `metrics` | Micro metrics, candidate recall and nearest-rank latency |
| I09 | [backend/app/pretest/ai/runner.py:86](../backend/app/pretest/ai/runner.py#L86) · `offline` | Frozen extraction/retrieval evaluation and method selection |
| I10 | [backend/app/pretest/ai/validation_round.py:21](../backend/app/pretest/ai/validation_round.py#L21) · `run` | Executed 20-case round; isolated concurrent clients |
| I11 | [backend/app/demo/evidence.py:18](../backend/app/demo/evidence.py#L18) · `build_profile` | Application-only v2 cleanup and model-input policy |
| I12 | [backend/app/demo/cohorts.py:50](../backend/app/demo/cohorts.py#L50) · `preview` | Deterministic cohorts and exact run previews |
| I13 | [backend/app/demo/cohorts.py:226](../backend/app/demo/cohorts.py#L226) · `taxonomy_collection` | Byte-bounded collection compaction |
| I14 | [backend/app/demo/analysis.py:91](../backend/app/demo/analysis.py#L91) · `admission` | No-repeat admission, receipts and explicit re-analysis |
| I15 | [backend/app/demo/analysis.py:211](../backend/app/demo/analysis.py#L211) · `automation` | Configurable automatic organization thresholds |
| I16 | [backend/app/demo/service.py:530](../backend/app/demo/service.py#L530) · `organize` | Actual application inference and offline reconciliation |
| I17 | [backend/app/demo/domain.py:19](../backend/app/demo/domain.py#L19) · `fence` | Generation/revision/privacy fencing |
| I18 | [backend/app/demo/domain.py:96](../backend/app/demo/domain.py#L96) · `term_conflicts` | Normalized canonical/alias reservations |
| I19 | [backend/app/demo/domain.py:308](../backend/app/demo/domain.py#L308) · `mapping` | USER precedence, rejection tombstones and rules |
| I20 | [backend/app/demo/run_budget.py:12](../backend/app/demo/run_budget.py#L12) · `RunBudgets` | Adaptive holds, finite grants and crash reconciliation |
| I21 | [backend/app/demo/allowance.py:210](../backend/app/demo/allowance.py#L210) · `ApplicationLedger` | Pinned application rates and atomic monetary admission |
| I22 | [backend/app/demo/store.py:56](../backend/app/demo/store.py#L56) · `Store` | Local transactional aggregate and durable job storage |
| I23 | [backend/app/pretest/ai/corpus.py:27](../backend/app/pretest/ai/corpus.py#L27) · `registry` | 42-concept registry, public allowlist and authored edge cases |
| I24 | [backend/app/pretest/ai/runner.py:208](../backend/app/pretest/ai/runner.py#L208) · `benchmark` | Available broader benchmark/expansion path; not the executed round |
| I25 | [backend/app/pretest/ai/settings.py:14](../backend/app/pretest/ai/settings.py#L14) · `AISettings` | Model, token, data and tracing configuration boundaries |
| I26 | [backend/app/demo/pricing.py:14](../backend/app/demo/pricing.py#L14) · `reserve_amount` | Application rate snapshot and conservative bound arithmetic |
| I27 | [backend/app/demo/taxonomy_review.py:199](../backend/app/demo/taxonomy_review.py#L199) · `publish` | Draft checks, opt-in repair and canonical publication |
| I28 | [backend/tests/pretest/ai/test_safety.py:88](../backend/tests/pretest/ai/test_safety.py#L88) · `test_install_only_change_does_not_invalidate_selected_profile` | Frozen selected-evidence invalidation fixture |
| I29 | [backend/tests/demo/test_analysis_policy.py:42](../backend/tests/demo/test_analysis_policy.py#L42) · `test_no_repeat_before_provider_construction_even_after_revision_and_history_deletion` | Tested no-repeat admission after revision/history changes |

## Reports, approved decisions and historical context

| ID | Source | Evidence class |
|---|---|---|
| E01 | [docs/validation/phase-0-5-results.md](../docs/validation/phase-0-5-results.md) | Measured/report |
| E02 | [docs/validation/phase-0-5-round-2-results.md](../docs/validation/phase-0-5-round-2-results.md) | Measured/report |
| E03 | [docs/validation/phase-0-5-reference-review.md](../docs/validation/phase-0-5-reference-review.md) | Measured/report |
| E04 | [docs/validation/phase-0-5-codex-results.md](../docs/validation/phase-0-5-codex-results.md) | Measured/report |
| E05 | [docs/validation/phase-0-9-taxonomy-and-analysis.md](../docs/validation/phase-0-9-taxonomy-and-analysis.md) | Measured/report |
| E06 | [docs/validation/phase-0-9-adaptive-live-20261013T145429Z.md](../docs/validation/phase-0-9-adaptive-live-20261013T145429Z.md) | Measured/report |
| E07 | [docs/validation/phase-0-9-preservation.md](../docs/validation/phase-0-9-preservation.md) | Measured/report |
| E08 | [docs/validation/demo-full-v2.md](../docs/validation/demo-full-v2.md) | Measured/report |
| E09 | [docs/validation/phase-0-9-live-ai-20261012T053557Z.md](../docs/validation/phase-0-9-live-ai-20261012T053557Z.md) | Measured/report |
| D01 | [docs/system-design.md](../docs/system-design.md) | Approved design/ADR |
| D02 | [docs/adr/0002-phase09-local-workspace.md](../docs/adr/0002-phase09-local-workspace.md) | Approved design/ADR |
| D03 | [docs/adr/0004-cohorts-and-adaptive-budgets.md](../docs/adr/0004-cohorts-and-adaptive-budgets.md) | Approved design/ADR |
| D04 | [docs/adr/0005-durable-analysis-and-local-reconciliation.md](../docs/adr/0005-durable-analysis-and-local-reconciliation.md) | Approved design/ADR |
| H01 | [docs/design-conversation.md](../docs/design-conversation.md) | Historical; not proof of delivery |
| H02 | [docs/design-conversation-full.md](../docs/design-conversation-full.md) | Historical; not proof of delivery |
| G01 | [AGENTS.md](../AGENTS.md) | Repository/execution instructions |
| G02 | [docs/system-design-execution.md](../docs/system-design-execution.md) | Repository/execution instructions |

## Reproduction and disclosure

`measurements.json` contains aggregate numbers and content hashes, never README copies, credentials, account inventory, request IDs or raw model responses. The audit script reads only the two named frozen public/synthetic experiment files. Those ignored source files are required for full local recomputation; their hashes make the limitation explicit. Public reviewers can inspect the committed reports and aggregate arithmetic, but cannot independently rerun historical provider generations from this package alone.

```bash
backend/.venv/bin/python ai-system-design/scripts/audit_evidence.py
```

The command writes only this article's aggregate/index files. It does not initialize ledgers, import provider settings, load .env, call a service or rewrite prior results.
