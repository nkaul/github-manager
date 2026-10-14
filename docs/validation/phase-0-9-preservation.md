# Phase 0.9 — Prior readiness evidence preservation

Date: October 12, 2026. Result: **PASS**.

The user explicitly required preservation of all prior testing, benchmarking and readiness work. A protected local baseline was taken before Phase 0.9 edits at `.tools/phase09-baseline-20261012T045829Z`. Its manifest covers 186 original files; directories/files use private permissions and no .env was copied. This is an additional local safeguard, not a replacement for version control or the live reports.

Final verification compared SHA-256 values and historical SQLite rows:

| Protected material | Result |
|---|---|
| 163 original source/test/infrastructure/validation/lock files selected by the verifier | Unchanged |
| Original preflight page retained as `frontend/src/components/Preflight.tsx` | Byte-identical |
| Earlier Phase 0/0.5 public and private Markdown reports and frozen corpus/reference artifacts | Unchanged |
| Original ledger experiment identity/cap | Identical, 1 record |
| Historical API attempts, reservations, settlements and usage | Identical, all 34 records |
| Historical model replay entries | Identical, all 29 records |
| Original cumulative budget sentinel | Unchanged |
| AWS scratch template, tests and retained-resource records | Unchanged; no AWS operations performed |

The shared ledger legitimately changed by adding the Phase 0.9 request allowance and four new generation records/results. Historical records were compared individually, rather than claiming the expanded database is byte-identical. The original Phase 0.5 configured 34-attempt ceiling remains unchanged; only the separate approved local adapter permits the extension to 44 cumulative attempts and 20 renewed HTTP slots.

App data is in a separate ignored SQLite file. Application reset never deletes readiness reports, the experiment sentinel, historical API accounting or old replay records. The application extraction wrapper is versioned separately; frozen RAKE/BM25/YAKE evaluation work was not regenerated or relabeled. Planning documents and README were updated to reflect approval/delivery; their earlier versions also remain in the baseline.

Reproduce the audit:

```bash
python3 scripts/verify-pretest-preservation.py .tools/phase09-baseline-20261012T045829Z
```

Output: PASS; 163 protected files; experiment=1, calls=34, cache=29; identical original preflight copy; no unexpected changes. Raw output is saved under ignored `docs/validation/private/demo/preservation.local.json`.
