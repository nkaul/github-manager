# Ground Truth review completion: statistics and evaluation readiness

October 19, 2026, America/New_York. The user reports review work complete. This is a **read-only audit of saved references**, not a new classifier or RAG-evaluation result. The [detailed completion plan](../planning/ground-truth-evaluation-completion-2026-10-19.md) specifies the remaining work and proposed call budget.

## Saved human work

| Measure | Observed |
|---|---:|
| Confirmed records / distinct repositories / review owners | 30 / 30 / 1 |
| Positive Project / Topic / Tag assignments | 15 / 35 / 33 |
| Total retained positive assignments | 83 |
| Repositories without Projects / without Tags | 15 / 3 |
| Distinct derived assigned Domains | 4 |
| Leakage groups represented | 18 |
| Development / validation / test-reserved records | 15 / 0 / 15 |
| Changed label sets versus original proposals | 4/30 |
| Added / removed original-proposal label pairs | 3 / 2 |
| Purpose text changed versus original proposals | 0/30 |
| Reviews revised after first save / retained history entries | 3 / 3 |
| Unfinished drafts, excluded from confirmed set | 1 |
| Confirmations at base v0 / v1 / v2 | 8 / 5 / 17 |
| Current extension additions | 1 Project, 1 Topic |

The base vocabulary has 337 concepts; current owner v2 has 339. The eight base-version records have no explicit context field and resolve against v0 under the legacy rule. Nothing was rewritten or rebound by this audit.

| Sampling domain | Confirmed repositories |
|---|---:|
| AI | 3 |
| Cloud | 0 |
| Commerce | 3 |
| Data | 10 |
| Developer | 1 |
| Education | 2 |
| Finance | 6 |
| Healthcare | 1 |
| Science | 2 |
| Security | 2 |
| **Total** | **30** |

These are sampling buckets, not automatically assigned Domains. The full corpus retains 60 repositories in each of ten buckets, 600 READMEs and 1,223 supporting files. Its provisional partitions remain 180 development, 120 validation and 300 test-reserved. Review coverage is uneven; these 30 confirmations support neither a population estimate nor a cloud-quality claim.

## Corrections and A/B overlap

Relative to the original frozen proposals, the human added one Project, one Topic and one Tag and removed two Tags, changing four repository label sets. These are observed edit counts, not proof that the original or revised sets are exhaustive. All 30 confirmations explicitly keep unlisted labels unknown rather than negative.

Six confirmed repositories overlap the independent 30-repository A/B pilot. Each agent shares all 17 human-retained positive pairs on that overlap; A additionally proposes 14 pairs and B 18. Complete-set matches are 0/6 for both. Additional pairs remain unjudged relative to the human reference, not automatic false positives. This is a small, selected descriptive comparison.

Four completed records overlap the earlier 20-case suggested queue, all `RANDOM_FILL`. Its risk-selected and random-Green intersections have no completed records. The old pilot/queue need not be completed to use the actual reviewed 30; they remain separate experiments with separate denominators.

No current confirmation has an explicit A/B-sidecar binding. Joining immutable repository/release identities allows retrospective comparison, but does not prove the user inspected both agents while confirming.

## Integrity checks and limits

Read-only SQLite and existing corpus/registry adapters checked all 30 confirmations for release/proposal/commit bindings, historical canonical IDs, review acknowledgements, explicit context hashes where present and derived Project-parent Domains. All three added-label quotes match saved source text; reviewed dossier integrity checks passed. No structural issue was found.

This establishes recorded integrity, not quote entailment, full-source reading, independent-human agreement or exhaustive negatives. The draft was not promoted, discarded or included as confirmed. No app state, source, corpus manifest, proposal, A/B annotation or API allowance was changed.

Final preservation checks verified all **2,423 manifest-bound source/dossier hashes**, the unchanged corpus manifest, unchanged saved-workspace aggregate hashes and unchanged API-ledger bytes. The prior package archive and illustration hashes are intact. Relative documentation links and whitespace checks passed. The local audit result is `.tools/ground-truth-evaluation-plan-verification-2026-10-19.json`. These checks are not a rerun of the app's backend/browser suites.

The [new collector snapshot](../../ai-system-design/ground-truth-creation/history/statistics-2026-10-19-review-completion-audit.json) retains the old collector's generic publication status and historical software-validation fields. The separate [completion audit JSON](../../ai-system-design/ground-truth-creation/history/review-completion-audit-2026-10-19.json) supplies current counts, coverage, versions and structural diagnostics. Neither claims that new classifier/framework runs occurred. The prior active publication package was [archived](../../ai-system-design/ground-truth-creation/history/ground-truth-creation-2026-10-19-pre-evaluation-plan.zip), with a [hash manifest](../../ai-system-design/ground-truth-creation/history/pre-evaluation-plan-preservation-2026-10-19.json), before current-checkpoint links were added. Earlier articles, statistics and illustrations remain preserved.

## Calls and budget

The existing local ledger contains 91 generation-reservation entries: 87 settled, 4 rejected before generation. Estimated historical charges total **$0.127619**, with no outstanding call reservations or active run holds, leaving **$4.872381** under the original $5 cap at audit time. These are historical app/pretest records, not new evaluation calls, an account balance or a provider invoice.

This audit made **zero paid model calls** and changed no allowance. The plan proposes a $1 sub-ceiling within the original cap, up to 47 planned generations/94 normal HTTP attempts, hard totals of 50 generation attempts/100 HTTP attempts including contingency, and at most 20 HTTP attempts per batch. New implementation, paid execution and framework installation await approval.

After approval: freeze references, measure the local stages, generate bounded live outputs, replay them through the frameworks and update the publication with results. An exceptions-only human pass may be needed for exhaustive precision/F1; repeating all thirty reviews is unnecessary.
