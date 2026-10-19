# Corpus 600: human verification and evaluation plan

> **October 19, 2026 update:** The user finished the selected review work. The audit finds 30 confirmed repositories, six overlapping the independent A/B pilot. Continue with the [current evaluation completion plan](ground-truth-evaluation-completion-2026-10-19.md) and [current statistics](../validation/ground-truth-review-completion-2026-10-19.md). The October 16 proposal below remains historical rationale: its v1 corpus counts, proposed sixty-case human pilot and initial zero-human status are not the current V2 execution requirements. The new plan preserves reviewed scopes, partial-label semantics and budget history.

Date: October 16, 2026. Status: **PROPOSED — planning only**.

The next milestone should be a small, credible human reference set and a stage-by-stage offline benchmark. Expand human review and live model evaluation after that calibration, rather than sending all 600 repositories through another model round immediately.

This plan covers the implemented local GitHub Manager: deterministic README evidence selection, RAKE phrases, sparse concept retrieval, bounded context, structured classification, taxonomy drafts and review. It preserves the approved OAuth App approach, local-first delivery and deferred cloud buildout. It proposes no Jev, embedding service, vector database or new production architecture.

## 1. Evidence we already have, and gaps to close

The [completed corpus report](../../eval/ai-system-design/evaluation/corpus-600/validation-2026-10-16.md) records 600 public repositories, 600 complete READMEs, 1,162 supporting files and 120 independent **agent** cross-reviews. There are zero human-approved references. Only 78 READMEs were semantically read in full; the other 522 received recorded targeted reading. All original source bytes remain available.

The baseline retrieved 249/252 proposed Project positives, 436/689 Topic positives and 606/634 Tag positives. These are provisional positive recalls of 98.81%, 63.28% and 95.58%. They identify Topic retrieval as a priority; they do not measure model classification accuracy. Of 1,575 proposed supported labels, lexical evidence-quote containment occurs for 1,293 in the profile and 1,035 in the compact request. That is an omission diagnostic, not semantic entailment.

Repository inspection found four important evaluation gaps:

1. **Reference completeness:** approving existing positives does not establish that all correct labels were found. Unlisted labels currently remain unknown.
2. **Scoring semantics:** [`backend/app/pretest/ai/evaluation.py`](../../backend/app/pretest/ai/evaluation.py) computes false positives as `predicted - gold`. That is appropriate only for an adequately complete reference scope. Applying it directly to this partially labeled corpus would wrongly count unknown labels as errors.
3. **Split coverage:** provisional totals are 180 development, 120 validation and 300 test-reserved, but finance has only three validation records and healthcare four. Commerce has six development/six validation records, while cloud has seven development records. Related groups must remain intact, so equal overall totals do not imply usable per-domain evaluation samples.
4. **Evidence sufficiency:** some reference evidence comes from supporting files the current app does not receive; valid full-source labels can also disappear during extraction or packing. Correct IDs, valid citations and supported meanings are separate checks.

The proposed registry has 335 concepts: 10 Domains, 64 Projects, 162 Topics and 99 Tags. Definitions were curated with access to corpus sources. The corpus and aggregate baseline have already been inspected. A future locked split can measure performance after the freeze, but must not be described as a completely untouched external holdout or unseen-registry test.

## 2. What human ground truth should mean here

Use **human-adjudicated reference labels under a versioned organization policy**, rather than claiming one universal taxonomy is objectively correct. Product relationships and primary technologies have factual evidence; the useful granularity of Topics and preferred Domain grouping also involve user choices.

| Dimension | Proposed annotation rule |
| --- | --- |
| Purpose | One plain-language statement of what this repository principally provides, with source evidence |
| Project | Explicit product/initiative, component, dedicated integration or documented lineage relationship under the approved family definition |
| Domain | Derived from supported Project parents; a sampling bucket never assigns a Domain |
| Topic | Primary purpose/capability/subject; distinguish implemented functionality from subjects taught by a course or listed in a resource index |
| Tag | Primary implementation or task-relevant dependency technology; distinguish API language, source language and incidental development dependencies |
| Artifact/maturity | Product, SDK, connector, course, documentation, curated index, sample, deployment configuration, generated client; implemented versus planned features |
| No match | Dimension-scoped conclusion under this registry and policy; lack of a Project is not a global classification NO_MATCH |

Each concept needs a short **concept card**: definition, inclusion/exclusion criteria, parent if relevant, aliases, one clear positive, one near-neighbor and one ambiguity example. Resolve broad family definitions such as official product versus independent distribution before reviewers disagree on individual repositories. Preserve meaningful distinctions such as Learning Content, Technical Documentation and Technical Resource Discovery.

For each repository/concept decision, store **POSITIVE, NEGATIVE or UNKNOWN**. A negative means a human explicitly judged the label inapplicable under the defined primary-purpose/family policy, with a reason. It need not claim that the software can never perform that function. Missing documentation alone remains UNKNOWN.

Separate review strength from semantic label value:

- `PROPOSED`: source-backed agent proposal.
- `AGENT_CROSS_REVIEWED`: independently checked by another agent.
- `HUMAN_POSITIVES_VERIFIED`: a person checked proposed positives; completeness remains unestablished.
- `HUMAN_SCOPE_REVIEWED`: a person reviewed the defined registry/dimension scope, added missing positives and recorded negatives/unknowns.
- `HUMAN_ADJUDICATED`: independent human annotations were reconciled with an actual adjudicator.

These are proposed benchmark statuses, not changes to app state. A repository may be scope-reviewed for Tags but still incomplete for Topics. A reference can correctly retain UNKNOWN; human review does not force an answer.

## 3. Methods to improve references before human review

| Method | Concrete use | Boundary |
| --- | --- | --- |
| Source-first evidence cards | Show purpose passages with neighboring context, headings, pinned source links and full-file access | A clipped quote is insufficient for negation, maturity or relationship scope |
| Deterministic weak labels | Suggest technologies from manifests; flag explicit relationship/feature-negation/version statements | Signals are proposals, not automatic gold; owner equality and a dependency do not prove Project membership |
| Diverse candidate pooling | Union current sparse candidates, BM25, exact aliases and existing proposed labels; let humans search the whole registry and add missing IDs | Do not let the evaluated retriever define the only labels humans can choose |
| Contradiction and visibility checks | Flag README/manifest disagreement, planned features, unsupported evidence, reference-only sources, omitted compact context and thin READMEs | Detecting coordinates or token overlap does not establish entailment |
| Independent blind annotation | Human writes purpose/labels before seeing model confidence, current predictions or another reviewer's answers | Two agents or two LLMs are not two human reviewers |
| Disagreement-driven routing | Prioritize uncertain families, multilingual cases, artifact-type confusion and candidate misses for deeper review | Keep a separate random audit sample; a risk queue cannot estimate the overall error rate |
| Human adjudication | Reconcile disagreements using sources and the policy; preserve original answers and reasons | Majority voting does not resolve a bad concept definition |

Programmatic labeling functions are an established weak-supervision approach, but their outputs can have unknown accuracy and correlation. Use that principle to prepare review suggestions; do not adopt a probabilistic label model as a substitute for human test references. [Snorkel research paper](https://arxiv.org/abs/1711.10160).

A second model could later act as a source-checking assistant, but its agreement with the producer is only another signal. It must quote evidence, allow abstention and remain distinct from human decisions. No new model calls are needed for the first preparation milestone.

## 4. Step-by-step execution

The numbered steps describe dependencies, not a requirement to finish all human review before learning anything. The initial path is Steps 1–3. Once the pilot is adjudicated, begin Step 6 on those reviewed development scopes while Steps 4–5 expand/freeze references. Human validation/test review can continue alongside development diagnostics and the bounded live pilot. Step 10 requires the reviewed, frozen test scope. Keep provisional pilot reports distinct from the later locked benchmark.

### Step 1 — Preserve the baseline and agree on the evaluation contract

Verify the existing release manifest without regenerating or editing it. Create a new evaluation workspace/version referencing the same immutable snapshots. Record the tasks, policy, metrics, unknown handling, input scope and intended claims before selecting improvements.

Draft a group-preserving split-coverage repair while the splits remain provisional. Prefer roughly the existing 180/120/300 proportions, with a proposed minimum of eight validation repositories per domain where feasible. Group integrity takes precedence over exact counts; document infeasible coverage rather than splitting a family. Keep every pilot repository's entire group in development. Save the original and proposed assignments plus the reason for each move.

**Output:** evaluation contract, source manifest check, split-coverage proposal and change log. **Gate:** user accepts the annotation policy and split tradeoffs; no data is silently relabeled or moved.

### Step 2 — Prepare a review pack that reduces anchoring

Create the concept cards and enrich the existing local review sheets. Use two views:

1. **Source view:** identity, source/version, raw purpose context and full README/supporting access. Hide existing predicted labels and confidence initially.
2. **Assistance view:** reveal proposed labels, evidence locations, alternative candidates, conflicts and omissions after the reviewer records an initial purpose/label assessment.

Each review asks: What does it do? Which Project relationships are evidenced? Which Topics describe the primary purpose? Which technologies are primary? What valid labels are missing? What cannot be decided? Record the evidence actually inspected, not a default “full file read” checkbox.

Start with Markdown/JSON already supported by the corpus. A small local two-pane review interface is an optional follow-on if the pilot shows substantial navigation friction; it is not a prerequisite, hosted service or application-taxonomy import.

**Output:** annotation handbook, concept cards, source-first review packets and proposed decision schema. **Gate:** references and source navigation are usable; proposed answers remain visibly separate from human decisions.

### Step 3 — Run a 60-repository human calibration pilot

Select six development repositories per sampling domain, preserving groups. Include supported families, independent neighbors, multilingual evidence, thin/long READMEs and artifact/maturity challenges where available. Record actual coverage; the existing small commerce/cloud/developer development slices limit diversity.

Use two independent people if available. For the first twenty records, both annotate from sources without prelabels. For the remaining forty, the primary reviewer can use the assistance view after writing purpose; the second reviewer still records an independent answer before seeing the first. Then adjudicate disagreements. Measure actual review time, missing-positive discoveries, corrections, abstentions and the influence of assistance; the twenty/forty comparison is descriptive, not a randomized causal study.

If only one human is available, complete human review and a delayed blind re-review of a sample, but label it single-reviewer evidence. Agents can organize evidence and identify contradictions; they cannot supply the missing independent human reviewer.

Report label-set agreement/Jaccard, exact-set agreement and positive/negative/unknown decision disagreements **before adjudication**, separately by kind. Avoid an all-negative-dominated agreement percentage across every possible concept. Multi-label agreement needs task-appropriate treatment; an ordinary single-label kappa over flattened label sets is not enough. [Multi-label annotation quality study](https://aclanthology.org/2022.coling-1.322/).

**Output:** 60 human reference records, original independent decisions, adjudication log and pilot report. **Gate:** every disagreement is resolved or explicitly unknown; systematic definition conflicts are fixed and affected pilot items re-reviewed. Do not set claimed agreement to 100% merely because adjudication produced one final answer.

### Step 4 — Complete development references and freeze policy

Finish human review of the development allocation, using the calibrated handbook. Validate Project scope, primary-purpose rules, artifact types and evidence visibility. Add missing valid concepts only through a recorded registry revision; keep old IDs/mappings auditable.

Finalize the groupwise split proposal and freeze the registry, rubric and scoring policy **before** validation/test model results are used to choose changes. If later human review discovers a material definition defect, issue a new version and reassess affected records rather than silently altering the test answer key.

**Output:** development reference release, frozen policy/registry and group split manifest. **Gate:** enough complete reviewed scope exists for the planned metrics; incomplete dimensions remain masked.

### Step 5 — Scale human verification to the remaining corpus

Give every remaining repository a human pass that checks purpose, adds missing labels and records scope/completeness. Review in batches of twenty and keep uncertain cases in a deeper-review queue. Continue semantic review of the relevant source context beyond the previously targeted agent passages when the decision requires it.

In addition to the sixty double-reviewed pilot items, choose a **120-repository independent human audit** from the other 540: twelve per domain selected before model outcomes, with a recorded random seed. Audit high-risk/disputed items additionally; do not substitute them for the random audit. Use the random sample for a qualified estimate of reference errors and the risk queue for correction. Account for group correlation and sampling weights when making aggregate estimates.

For stronger research/publication claims, independently double-review **all 300 test-reserved repositories**, not just the audit subset. This is a higher-effort option. The minimum route supports human-reviewed references with sampled independent verification; it does not establish two-person agreement on every record. Measure pilot time before extrapolating reviewer hours.

**Output:** up to 600 human-reviewed records with per-dimension completeness, reference-quality audit and unresolved/unsupported cases. **Gate:** only the actually completed scope is promoted; no batch approval inferred from earlier fixture approvals or agent agreement.

### Step 6 — Build and run stage-specific offline evaluation

Implement a corpus-aware scorer alongside the frozen Phase 0.5 scorer. Keep the old fixtures and historical results unchanged. On partial scopes, distinguish known positives, explicit negatives and unjudged predictions. Report unjudged-output rate and review coverage; do not publish ordinary whole-task precision/F1 as if unknowns were negatives.

For a reviewed set, `TP = predicted ∩ positives`, `FN = positives − predicted`, and judged `FP = predicted ∩ explicit_negatives`. Any precision based only on judged predictions must be named **judged precision**, with its coverage. Standard set precision/F1 and exact match are headline metrics only on sufficiently complete, explicitly defined scopes. Do not reward a system for emitting many unjudged labels.

| Stage | Evaluation | Main diagnostic question |
| --- | --- | --- |
| Source and extraction | Source/span validity, human purpose/evidence recall, phrase usefulness, artifact/negation retention | Did the local profile retain the facts needed? |
| Concept retrieval | Recall at current 8 Project/10 Topic/12 Tag limits; recall curves, judged precision, per-domain/family/language results | Were the correct IDs available to the model? |
| Augmentation | Human-judged evidence sufficiency before/after packing, irrelevant-context rate, token size | Did compacting discard the decisive relationship or qualifier? |
| Classification validation | Canonical-ID/type/candidate/evidence validity, derived Domain correctness, invalid output handling | Can a structurally invalid assignment be applied? |
| End-to-end classification | Per-kind micro/macro precision/recall/F1 where justified, exact match, false membership, abstention and review coverage | Does the product make useful, supported decisions? |
| Operational harness | No repeated paid calls, receipts/NO_MATCH, restart, reset fencing, allowance and privacy tests | Is quality evaluation changing correct operating behavior? |

The current retriever returns ordered IDs within each kind; a proposed evaluator adapter can expose scores for ranking analysis without changing production behavior. Compute ranking metrics only where relevance judgments support them. Suppress or qualify macro scores for rare/unrepresented concepts, and report denominators. Use groupwise bootstrap intervals for model comparisons rather than treating related repositories or multiple labels as independent observations.

Use development data for error analysis and tuning. Preserve the historical all-600 exploratory baseline, but do not continue examining test-specific misses to choose improvements after the freeze.

**Output:** offline baseline report, per-stage failures, metric scope/denominators and reproducible artifact hashes. **Gate:** deterministic reference/scoring tests pass; unknowns cannot become false positives implicitly; no paid APIs required.

### Step 7 — Run a bounded live readiness pilot

After explicit approval and human reference readiness, use the configured, approved LangChain model path in an isolated evaluation workspace. Do not classify into the user's live organization state or clear durable receipts to manufacture a new run.

Propose at most **20 actual provider HTTP attempts**, including token counting, generations, retries and optional judging. A nominal schedule is six repository classifications, one small development taxonomy draft and one optional judge request: eight generations plus their count requests normally use sixteen attempts, leaving four for accounted failures. Reduce the schedule if admission estimates or actual transport behavior require it; do not assume twenty attempts means twenty generations.

Propose a separate **$1 pilot ceiling**, also bounded by the remaining approved cumulative budget and configured allowance. Never reset the existing $5 ledger or increase a cap implicitly. If remaining approved allowance is insufficient, report the dependency rather than spending. Current pricing, model compatibility and token/schema overhead must be verified at execution; this plan selects no new model.

The six classifications are a contract/trace smoke test, not a statistical quality benchmark. Record the exact registry/profile/prompt/model versions, candidate IDs, actual supplied evidence, status, token/cost/latency and validated result. Cache replays remain distinct from fresh generations. Default tracing remains local/disabled for external services.

**Output:** live pilot Markdown report and local traces. **Gate:** bounded counting/reservation works, output contracts hold, human references can be scored and calls cannot bypass receipts or budget controls. Stop and inspect failures before a larger batch.

### Step 8 — Evaluate taxonomy discovery separately

Use development mini-collections with evidenced families, independent neighbors and artifact-type diversity. Review drafts using relevance, source support, hierarchy/type correctness, alias distinctness and useful grouping, with a defined 1–5 rubric and supporting repo IDs. Also measure proposed-concept count, unsupported-family rate, duplicate rate, missing useful distinctions, acceptance/edit/reject rates and reviewer time.

Match synonyms and acceptable scope alternatives before scoring; exact draft-name overlap with the 335-concept registry is not the objective. A concise useful draft should not be penalized for failing to reproduce every possible concept, nor rewarded for one Project per repository. Compare baseline/candidate drafts in randomized A/B order with model identity hidden.

Keep **fixed-registry classification** and **discovery followed by classification under its approved draft** as separate experiments. Do not attribute an end-to-end discovery gain to the classifier alone or create a registry using held-out test repositories and call it unseen discovery.

**Output:** taxonomy rubric and human quality report. **Gate:** conceptual support/grouping and review usability are demonstrated independently of label-string matching. Larger live batches require their own approved call/dollar plan.

### Step 9 — Improve one stage at a time, then choose on validation

Start with Topic candidate loss and evidence packing. Compare the existing sparse ranker with already available BM25/alias baselines, bounded candidate expansion, development-derived alias/definition improvements and purpose/negation-aware packing. Hold sources, reviewed labels and other pipeline components fixed for each comparison. RAKE/YAKE comparisons remain subject to the existing licensing boundary; this is not approval to introduce YAKE into production.

Use development-only diagnostic oracle runs when needed: (a) add a missing human-correct candidate while keeping context fixed, or (b) supply a minimal human-selected decisive passage while keeping candidates fixed. These isolate candidate and context failures; they are not deployable performance results. Respect normal payload/cost bounds and label every oracle run. Never inject answer labels into normal evaluation inputs.

Select the smallest change that improves human-reviewed quality and reviewer effort without unacceptable token, latency or false-assignment cost. Validation selects among predeclared alternatives; repeated experimentation eventually turns validation into tuning data and should trigger a new future holdout.

**Output:** ablation report, selected configuration and rejected tradeoffs. **Gate:** improvement is supported by human references with uncertainty, not only higher provisional recall. No neural reranker, dense retrieval or decision model is added by this plan.

### Step 10 — Run the locked benchmark and set operating policy

Freeze the chosen code/configuration and run the reviewed locked test allocation once as the confirmatory comparison. Paid classification across hundreds of records is a **separate approved batch**, not included in the twenty-attempt pilot. Estimate generations, count calls, retries, judge calls and maximum dollars before execution; cache only identical valid requests and report replays separately.

Publish results by kind, domain, artifact type, language, popularity, family/nonfamily and evidence sufficiency, with support counts and groupwise uncertainty. Report both all-reference end-to-end performance and the subset for which app-visible evidence was sufficient; do not silently remove difficult cases to improve the headline.

Include user-review time and correction burden, tokens/dollars per correctly supported accepted association, NO_MATCH/NEEDS_MORE_CONTEXT quality, overassignment, invalid IDs and repeat-call avoidance. Keep confidence-based auto-apply disabled until human-reviewed validation supports a per-kind selective policy with adequate sample size. Model-reported confidence alone does not establish that threshold.

Preserve the test report even when it fails. Fixing issues based on that report makes a subsequent run a regression check; a new confirmatory claim needs another frozen version/holdout. A later fresh public-repository sample can test generalization, with separate crawl approval and preserved lineage exclusions.

**Output:** versioned benchmark, model/data/config manifests, limitations and review/auto-apply recommendation. **Gate:** human reference quality, stage quality and harness safety are reported separately; controlled synthetic fixtures remain for privacy, races, resets and failure recovery.

## 5. Example of the two reference axes

The existing `airbytehq/pyairbyte` dossier identifies Python utilities exposing Airbyte connectors and records the README's explicit lack of production orchestration/scheduling. Under the proposed policy, Airbyte membership can be a positive while Data Orchestration is an explicit primary-capability negative. Human reviewers must confirm both rather than inheriting every Airbyte-platform capability. This case is currently in validation; use the already documented example only for policy clarification, not repeated validation-driven prompt tuning.

The development `dbt-labs/dbt` snapshot describes Rust dbt v2 and points Python v1 elsewhere. Human reference labels should follow that pinned version, not remembered historical language. Technology judgments still need source/channel provenance rather than simply copying GitHub's language field.

For every positive label, independently record:

| Axis | Example decision |
| --- | --- |
| Full-source truth | The documented product relationship is supported |
| Metadata/README sufficiency | It is explicit here, only in a supporting manifest, or unresolved |
| Extracted-profile sufficiency | Decisive passage retained, omitted or distorted |
| Compact-request sufficiency | Required passage and qualifier reached the actual model input |
| Generated decision | Correct label / incorrect label / appropriate abstention |
| Generated grounding | Cited supplied evidence entails the claim / partial / unsupported / contradicted |

A correct label inferred from model memory while its citation is unsupported gets separate correctness and grounding outcomes. A supporting-file-only fact does not justify demanding a confident answer from a README-only model. Citation existence is a deterministic check; entailment is a semantic review.

## 6. Evaluation tools and human assistance

**Start with the existing Python harness and local Markdown/JSON review artifacts.** Add corpus-specific adapters and tests rather than replacing the validated Phase 0.5 paths. This keeps evaluation reproducible without new SaaS accounts, source uploads or platform migration.

**Ragas is a selective later adapter.** Its ID-based context recall can support deterministic retrieval comparisons, while faithfulness assesses whether response claims are supported by supplied context. For this structured classification task, convert assignments into explicit claims with concept definitions and retain the exact supplied evidence; calibrate semantic judges against human judgments. Generic answer-relevancy scores are not replacements for Project/Topic/Tag correctness or primary-purpose policy. [Ragas context recall](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_recall/), [Ragas faithfulness](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/).

**LangSmith is optional if local review becomes cumbersome.** Its rubric-based annotation queues and pairwise comparisons fit human review of runs and taxonomy alternatives. Using them would require an explicit decision about hosted traces/content and account/cost setup; existing LangChain integration does not enable uploads automatically. [LangSmith annotation queues](https://docs.langchain.com/langsmith/annotation-queues).

**Cleanlab-style consensus is a later research option.** Its documented multiannotator workflow combines annotations with out-of-sample predicted class probabilities. Our partial multi-label registry decisions and small human pilot do not directly satisfy a standard multiclass setup. Do not feed correlated LLM confidences into that workflow and treat its consensus as independent gold. Revisit only with a suitable formulation and enough independent annotations. [Cleanlab multiannotator tutorial](https://docs.cleanlab.ai/stable/tutorials/multiannotator).

Any judge should return support/contradiction/insufficient-evidence outcomes with passages, be blinded to model identity when possible, and be tested on human-reviewed cases. Log rubric/model/version, judge false-positive/false-negative tendencies and abstention. A tiny smoke judge run does not calibrate a judge. No single composite “RAG score” replaces the stage reports.

## 7. Implementation scope and deliverables after approval

Initial approval should cover **Steps 1–3**: offline preparation, concept/annotation policy, review-pack improvements and the sixty-repository human pilot. Human participation is required to execute the pilot; reference labels cannot be generated and called human-approved by the agent. Preparation can proceed without browser authentication, GitHub fetching, new packages or paid API calls.

Proposed files, keeping original releases unchanged:

- `eval/ai-system-design/evaluation/corpus-600/annotation-handbook.md` and concept-card index.
- `eval/ai-system-design/evaluation/corpus-600/tools/prepare_review.py` for source-first packets and independent decisions.
- Private `docs/validation/private/corpus-600/evaluation-v1/` for review packets, real reviewer decisions, split proposals and adjudication; do not overwrite `release/`.
- Later corpus-specific `evaluate.py`/tests for partial-label masks, visibility and grouped reporting, importing existing app logic.
- Dated Markdown reports for human calibration, reference-quality audit, offline stages, live pilot, taxonomy review, ablations and final test.

Every implementation slice must demonstrate its artifact and checks before the next scope is approved. Preserve existing application data, previous benchmarks, corpus sources, academic/illustrated articles, diagrams, media, skills and historical metrics. This planning document authorizes none of the proposed changes, paid runs, public redistribution or fixture replacement by itself.

## 8. Proposed acceptance policy

Hard gates: source/version bindings valid; unknown labels explicitly handled; no test-family leakage; only actual humans recorded as human reviewers; no invalid canonical/evidence IDs applied; no unauthorized content, duplicate paid processing, budget bypass or stale reset writes.

Quality targets should be approved after calibration and **before** validation/test selection. A useful initial proposal is Topic candidate recall of at least 90% on sufficiently reviewed validation scopes, while preserving Project quality and bounded context. This is an engineering goal, not a measured result or universal threshold. Define a per-kind precision/risk requirement for any future auto-apply policy and require adequate uncertainty bounds; rare or ambiguous slices stay review-first.

The first useful outcome is the sixty-record human reference release and trustworthy offline error decomposition. Full-corpus human review and hundreds of paid generations can follow in measured batches rather than blocking that first result.
