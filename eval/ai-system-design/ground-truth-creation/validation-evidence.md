# What has been validated, and what must happen next

> **October 19 checkpoint: local and framework evaluations completed.** The [final report](../../../docs/validation/ground-truth-evaluation-2026-10-19.md), [publication addendum](evaluation-results-2026-10-19.md) and [aggregate evidence](evaluation-statistics-2026-10-19.json) supersede the next-action assumptions below. All thirty primary classifications and Promptfoo replay checks completed; Ragas candidate metrics match local scoring and three grounding scores average 0.9167. The run consumed its approved 50 generations/100 HTTP attempts and recorded $0.133941 estimated charges. Sixteen extra predictions remain unknown. This appendix preserves its October 18 evidence snapshot and original protocol for historical comparison.

**October 18, 2026 · Living evidence appendix · Reference quality remains under review.** Read this with [the article](article.md), [current aggregate snapshot](statistics.json) and [exact public worked example](worked-example.json). This appendix documents observed evidence and a proposed evaluation protocol. It does not turn a software test into a semantic correctness result.

## The current decision boundary

The active English-first release contains **600 repositories** and a **337-concept proposed registry**. The independent pilot contains **30 development repositories, 60 annotations and 20 initial human-review cases**. The other **570 repositories do not have independent A/B proposals**. At the October 18, 2026, 22:09 America/New_York snapshot, five real corpus records are human-confirmed: four outside the pilot and one inside it. Pilot human confirmations are **1/30**, including **1/20** in the initial queue. There are no incomplete drafts. No record has a staged-pilot binding; this does not establish whether the reviewer inspected A/B inputs. The earlier four-record snapshot remains in history.

The next action is available now: select **Public - Ground Truth → Repository review scope → Initial human review · 20**, compare the prominent **Agent A & B inputs** against source evidence, and save explicit decisions for the remaining nineteen cases. No further model call or new sixty-case preliminary study is needed to continue that agreed queue. Later expansion is a decision after the first checkpoint.

## Completed evidence, layer by layer

| Layer / recorded date | Observed result | Evidence to inspect | What the result does and does not establish |
| --- | --- | --- | --- |
| English-first release, October 17 | 600 distinct repositories; 60 per sampling domain; 489 retained + 111 replacements | [Release report](../../../docs/validation/corpus-600-v2-review-2026-10-17.md); private manifest/inventory bindings in [snapshot](statistics.json) | Balanced eligible acquisition, not a representative random sample or human-approved label set. |
| Source/read-scope audit, October 17 | 600 complete saved READMEs; 1,223 supporting files; 18,436,109 source bytes; 1,746 evidence items consistent with recorded read intervals | Release report; manifest/source hashes | Text retention and interval/citation consistency, not proof of comprehension. Original curation recorded 88 full semantic README reads and 512 targeted/partial reads. Do not add those 88 to pilot 30 without deduplicating overlapping repositories. |
| Curation peer review, October 17 | 120 distinct cross-cohort reviews with current source/annotation bindings | Release report and retained cross-review history | Selected source/eligibility/proposal claims were inspected; this is not the later double annotation and not human gold. |
| Corpus software activation, October 17 | 164 backend tests,14 corpus-tool tests; 13 existing app UI cases plus the corpus workflow reported passing | Release report's validation section | Historical run-specific behavior. Counts overlap later runs and are not summed into an accumulated accuracy result. |
| Independent pilot, October 17 | 30 development packets; 2 passes; 60 schema/evidence-validated annotations; 126 supplied source channels; 810,821 bytes | [Pilot handoff](../../../docs/validation/agent-annotation-pilot-2026-10-17.md), [methodology](../evaluation/annotation-pilot/README.md) and manifest-bound sidecar | Both agents produced traceable proposals without the other answers, original labels or production shortlist. Semantic correctness remains open. |
| Pilot coordinator/app QA, October 17 | 190 backend tests, including 20 coordinator cases and 6 app contract cases; 2 isolated browser workflows | Pilot handoff's verification section | Import validation, owner/CSRF boundaries, explicit staging/save and evidence channels behaved as tested. These disposable QA confirmations are not human review records. |
| Live review redesign, October 17 | 121 backend demo tests; 17 main and 5 Ground Truth browser workflows across full/focused reruns; lint/type/build passed | [Redesign report](../../../docs/validation/live-workspace-redesign-2026-10-17.md) | Draft restoration, save-before-next, source-sheet focus, conflicts and responsive review were checked. This is a different run scope, not a regression from 190. |
| Session/Sync and isolation, October 18 | 179 backend demo/auth/session/GitHub cases,12 focused recovery checks and 6 fixture-port checks; 22 main-suite and 10 corpus-suite checks reported | [Recovery report](../../../docs/validation/session-sync-recovery-2026-10-18.md) | Expiry/recovery/navigation and test separation were checked; suite counts include utility tests and repeated focused cases. They are not additive unique experiments. |
| Latest A/B visibility and scope, October 18 | 57 backend checks, including 6 focused scope cases; all 12 isolated Ground Truth suite checks; lint/type/Ruff/build passed | [A/B scope report](../../../docs/validation/ground-truth-agent-inputs-2026-10-18.md) and its [capture guide](../../../docs/design/workspace-refinement/agent-inputs-2026-10-18/README.md) | A/B inputs are discoverable; 600/30/20 scoping is applied before pagination and retained by continuation. The suite includes a palette utility assertion as well as browser journeys. Not 12 independent label-quality experiments. |
| Latest preservation, October 18 | 548 protected artifacts unchanged; existing reviews preserved; new user review retained | A/B scope report; local `.tools/ab-visibility-preservation-result.json` | Source/pilot/readiness/budget content was not replaced. Exact read-only reconstruction of the previous state attributes the change to the user's new review and control-version increment; no rollback occurred. |
| This publication revision | Link/image/source/numerical checks rerun; active illustration hashes unchanged | [verification.json](verification.json), [reproducible verifier](scripts/verify_package.py), [revision history](history/revision-01-preservation.json) | Publication consistency, not application retesting, annotation accuracy, full accessibility certification or a reader study. |

The release reports are the dated records of their respective runs. This documentation task reads them; it does not silently rerun backend/browser suites or claim their outputs as new execution results. Current aggregate counts are independently recounted from saved artifacts and read-only SQLite.

## Source and annotation integrity: exact guarantees

The frozen release binds the repository numeric ID, commit, source path and SHA-256. Git blob checks were part of acquisition; app/coordinator reads verify the retained manifest-bound content. Public metadata is a separate acquisition-time snapshot. It must never be presented as a README passage or described as made permanently immutable by a source commit.

The annotation importer validates:

- Exact sample coverage and packet/release binding; no extra, duplicate or missing repository rows.
- Known canonical concept IDs and strict schema; no direct Domain labels. Domains derive from retained Project parents.
- Source hashes and exact quotation substrings at inclusive 1-based line coordinates.
- Citation placement within the reader's declared read intervals and honest complete/partial declarations.
- Preserved positive IDs, evidence, scope, caveats and missing concepts. Omission remains unknown.
- Atomic import, safe paths and sidecar manifests. Mutated source bytes or stale/wrong release/context invalidate the proposals instead of quietly accepting them.

Representative executable evidence is in [coordinator tests](../../../backend/tests/demo/test_annotation_pilot.py), [source/review tests](../../../backend/tests/demo/test_corpus.py), [annotation/app contracts](../../../backend/tests/demo/test_corpus_annotations.py), [draft contracts](../../../backend/tests/demo/test_corpus_drafts.py) and [scope tests](../../../backend/tests/demo/test_corpus_annotation_scope.py). A parametrized test function can produce several cases; count reported cases, not function names, when comparing runs.

A real quote proves that text exists. It cannot prove entailment, primary-purpose relevance or a correct family relationship. Saved code declaring Node.js may support a runtime statement while leaving the primary-Tag decision unresolved. The Backstage example deliberately preserves that boundary.

## Reading coverage and independent comparison

Both readers received all 126 channels. A declared 109 complete channel reads and left 17 incidental license/trademark-license files unread; B declared 126 complete reads. A therefore has 14 complete and 16 partial supplied-scope repository declarations. Full retained scope is not full repository scope. A ledger can be internally consistent without demonstrating comprehension.

The resulting bands are 2 Green / 12 Amber / 16 Red. In this run, Red is driven by incomplete supplied reading; it must not be translated into sixteen incorrect annotations or sixteen missing-purpose READMEs. A future relevance policy could separately identify required semantic evidence by decision type, retaining whole-packet coverage alongside it. That would be a versioned policy change, not permission to improve this run's numbers retroactively.

| Facet | Exact set agreement /30 | Both empty | Same nonempty set | Shared / union positive pairs |
| --- | ---: | ---: | ---: | ---: |
| Projects | 28/30 | 12 | 16 | 16/18 |
| Topics | 10/30 | 0 | 10 | 74/103 |
| Tags | 19/30 | 1 | 18 | 58/71 |

Across all facets, 148 positive repository/concept pairs are shared, out of 192 union pairs. This is positive-set overlap, not accuracy. The exact full label set matches for 5/30 repositories. A proposes 153 positives; B proposes 187; 5 are A-only and 39 B-only. None of those differences is automatically a false positive or negative until adjudicated.

Independence means separately authored source-first passes under the recorded restrictions. The base models may be the same or related, and the readers share definitions and retained evidence. Correlated policy/model mistakes can survive agreement. Lexical/systematic blind spots can also survive both readers, which is why random review is not optional evidence merely because risk review finds more changes.

## What the human decision currently records

The app stores a purpose, positive `label_ids`, Projects/Topics/Tags acknowledgements, status, additional evidence/notes, context bindings, revision and history. It derives Domains. It supports several relevant labels per facet, saved drafts and explicit unresolved decisions. Its owner-scoped export does not combine reviewers into consensus.

It does **not** currently store a per-concept `NEGATIVE`/`UNKNOWN` judgment table or a formal exhaustiveness/completeness declaration. A group acknowledgement means the human checked that group in the workflow; it does not establish that every unselected concept was reviewed and rejected. `HUMAN_CONFIRMED` is workflow provenance, not evidence of a blinded expert panel.

Review the initial queue as follows:

1. Read the README introduction and relevant supporting passages before deciding. Check the repository's actual artifact role: application/library/demo/catalog/deployment tool, current capability versus plan, and what belongs to another linked repository.
2. Inspect both prominent agent summaries and their evidence. Use A or B as a staged starting point only if helpful; edit as needed. Staging has no final write and clears reviewed checks.
3. Check Project relationships, primary Topics and primary Tags. New positives need a real exact saved-source quote. Record missing registry concepts or insufficient evidence rather than forcing an assignment.
4. Confirm only after the three groups are deliberately reviewed. Otherwise save a draft or choose Needs evidence. Keep a note for a consequential correction or ambiguity.
5. Stay in **Initial human review · 20** through Confirm & next. Switching to the 30-case pilot is explicit. All 600 remains a broader corpus view, not a promise of two-agent annotations.

The scope guard resolves a concrete evaluation risk: if review navigation quietly broadened to 600, a pilot-review count could be inflated with cases that have no independent proposals. Latest backend/browser tests cover this continuation boundary and unavailable-pilot errors.

## Human validation checkpoint: proposed analysis after the initial twenty

Keep three sampling strata distinct:10 risk-selected, 2 random Green agreement and 8 deterministic random-fill cases. Record the actual completed denominator and unresolved cases in each. A targeted correction rate describes that targeted queue; it is not a corpus error estimate. Random fill is not automatically Green or representative of every family/domain. Small groups produce wide uncertainty, and related families reduce effective independence.

For each reviewed case, retain or derive an analysis row containing:

| Field to analyze | Why it helps | Availability now |
| --- | --- | --- |
| Queue stratum, repository, release/source/pilot versions | Preserve sample provenance and compare like with like. | Present in frozen queue/bindings; join adapter needed for reports. |
| Purpose correction and final positive set | Inspect what changed, separately against A and B. | Saved review plus annotations available. |
| Error reason: family-membership overreach; incidental capability/technology; missing concept; negation/planned feature; source insufficiency | Turn corrections into policy/extractor/retrieval improvements. | Notes exist; standardized reason coding is proposed, not an existing app field. |
| Accepted/removed/added candidate judgments with evidence | Distinguish unsupported suggestions from unknown omissions. | Positives/evidence available; explicit per-candidate negative/unknown adapter/review extension required. |
| Evidence sufficiency and completeness scope | State what a label-quality denominator actually covers. | Agent scope exists; formal human reference scope is not yet stored. |
| Review status and revision | Do not count drafts/unresolved cases as completed gold. | Available in persisted records. |
| Active review time, interactions and assistance/staging choice | Test the human-effort claim and detect anchoring. | Not measured as validated outcome; future instrumentation/protocol needed. |

Report reviewed counts, changed-case counts, unresolved counts and reason/facet breakdowns before derived rates. Keep each reader's results separate. Do not call a final answer identical to staged A “A accuracy” without considering that the reviewer saw A. A stronger later audit can hide source-reader identities or have a subset reviewed independently before showing proposals, then adjudicate disagreement. This is a proposed bias-control extension, not a completed blinded study.

No new automatic acceptance threshold is justified yet. Choose further random audits from observed outcomes and the desired error tolerance; state confidence intervals or other uncertainty estimates appropriate to the design. Do not claim that zero errors in the two Green cases establishes a high future accuracy. For later multi-family estimates, consider group-aware/cluster bootstrap uncertainty rather than pretending related repositories are independent. No interval or population accuracy has been estimated for this run.

## From reviewed cases to a fair retrieval/classification evaluation

### Gate 1: Freeze the meaning of a reference answer

Resolve recurring definition and missing-concept disputes on development cases. Version the registry, evidence-relevance policy and annotation instructions. Human-review records must remain tied to the versions they actually reviewed; a new definition must not silently re-interpret an old approval.

Define reviewed-positive, reviewed-unsupported and unknown decisions and the scope in which completeness is claimed. The current positive-only app records are useful reference evidence, but insufficient for every exhaustive metric. A downstream evaluation adapter can join them with an explicit candidate-judgment sheet or a bounded additional review interface. Mark that extension as planned until implemented and reviewed.

### Gate 2: Protect evaluation independence

The provisional v2 splits are 180 development / 120 validation / 300 held-out, exactly 18/12/30 per domain. Related Project families, shared-owner groups, recorded lineage and detected near-duplicates are grouped. Keep groups intact when freezing or updating splits. Do not use held-out labels as prompt examples, taxonomy tuning feedback or model-selection criteria.

The registry was curated with access to corpus sources; a development-only definition boundary has not been demonstrated. Earlier exploratory outputs across the original v1 collection of 600 repositories were already inspected, and v2 retains 489 of those repositories. The reserved partitions are therefore not a pristine external or unseen-registry holdout. Freezing now can protect subsequent model-selection comparisons, but cannot undo earlier source/result exposure. Report that provenance and, if a pristine test is required later, collect a genuinely new versioned external set after freezing the policy and system.

The independent pilot receives the full registry and does not use the production candidate shortlist. Evaluate on annotation-free source inputs; the combined reference-only content file contains answers and must not enter model prompts. Keep discovery queries, eligibility outcomes and old proposed labels out of the model-input allowlist. Public-source use also does not establish that a base model has never seen the repository in pretraining; no such contamination audit was performed.

### Gate 3: Measure retrieval before blaming generation

For each adjudicated supported concept, ask whether it appears in the candidate set at a fixed declared budget `k`, by facet. Candidate recall at that budget is:

`reviewed supported IDs retrieved / reviewed supported IDs in the declared reference scope`.

Always report the denominator and coverage scope. If that scope is incomplete, describe recall against the reviewed positives; do not call it exhaustive true-label recall. Report macro summaries by domain/family alongside pair-weighted totals. A family that dominates the corpus must not conceal a weak family. Include candidate count/latency/context size where measured; none is newly measured by this document.

Use the same frozen sources, registry, split and candidate budgets when comparing the app's current retrieval strategy with any future sparse/dense/hybrid/reranking alternative. Predeclare the experiment and budget rather than changing both retrieval and generation while attributing every improvement to one. No dense index, reranker winner or v2 retrieval benchmark result is claimed here.

### Gate 4: Measure selection and evidence separately

With the candidate set fixed, evaluate whether classification selects supported labels, abstains when appropriate and avoids unsupported relationships. Have humans adjudicate predicted labels not already judged; unknown labels cannot simply be counted as false positives. Conventional precision requires supported versus unsupported predicted decisions. Recall requires a defensible positive-reference scope. F1 is meaningful only when the paired precision/recall denominators are compatible.

Report Projects, Topics and Tags separately; Domains are derived and should not masquerade as an independent classification task. Preserve multi-label cases. Track exact-set match, per-facet errors, missing-known-label errors, unresolved/missing-concept rates and grounded evidence support, with the actual reference semantics stated. Schema validity and valid citation containment are separate from semantic evidence support.

If a future LLM judge assists entailment review, calibrate it against a human-audited subset, disclose judge/model overlap with the classifier and keep uncertain cases reviewable. No judge call or judge score exists for the current corpus. A Q&A answer-faithfulness score alone would not establish repository family/capability correctness.

### Gate 5: Check the operational loop

Record real provider attempts, retries, token usage, cost, latency and cache reuse when a paid evaluation is authorized. Use explicit total-call/cost and per-request limits, immutable request/reference versions and reproducible run receipts. The historic Phase 0.5 readiness experiment is separate; its allowance or small-fixture scores are not v2 corpus evidence or new spending authorization.

The English-first acquisition used 902 HTTP attempts, 9 searches and 3,457,838 new retained bytes, under ceilings of 6,000 attempts / 120 searches / 512 MiB. Cached historical snapshots were reused with provenance. The independent annotation pilot added 0 provider requests and $0 incremental provider spend; Codex allowance/token use remains unmeasured. Source bytes are not token counts, and neither establishes a cost per correct label or human minute saved.

Before any automated promotion, verify that saved human decisions cannot be overwritten by sync/annotation, reruns cannot silently change the reference version, drafts remain excluded, and invalid/stale context fails visibly. Existing isolated API/UI tests cover several of these safety boundaries. Continue using 3015/8015 for Ground Truth tests and 3016/8016 for main-app tests; never bind fixture entrypoints to the live 3000/8000 app.

## Evidence incident and preservation

Earlier validation briefly put a fixture service at the normal localhost ports, causing the user to see a test account. This was corrected by restoring the real app, isolating test ports/builds and blocking fixture entrypoints at normal ports. [The recovery report](../../../docs/validation/session-sync-recovery-2026-10-18.md) records the incident, successful checks and preserved user review. It is not evidence that the live account or database became a synthetic account.

The later A/B visibility validation separately preserves 548 protected artifacts and an additional real user review, using exact read-only reconstruction. Its four-confirmation count was the live progress at that check. Another user review arrived during this publication update, bringing the publication snapshot to five confirmations, including one pilot case. The older four/three/zero-review statements remain historical snapshots; they must not be rewritten as if they happened later.

This publication update preserves the previous complete package in [revision 1](history/ground-truth-creation-2026-10-18-revision-01.zip), with its [hash manifest](history/revision-01-preservation.json). Existing illustrated figures remain unchanged because their 30/20 counts and authority boundaries remain correct. No application code, source corpus, annotation output, database or provider ledger is mutated by the publication updater/verifier.
