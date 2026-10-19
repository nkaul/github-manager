# AI systems, retrieval and evaluation

## Identify the actual model task

Separate collection-level taxonomy discovery from per-item classification. Discovery proposes a vocabulary from a reviewed sample; classification assigns existing approved concept IDs to a specific repository using evidence. Neither should silently publish new concepts or replace protected user decisions. Valid NO_MATCH is a completed result, not proof that another call is required.

Show the real boundary with a small source-backed example: repository metadata/README → local extraction → candidate retrieval → bounded evidence/context → structured model output → validation → human review. Validate allowed active concept IDs, type/cardinality rules and source references before accepting a suggestion; a syntactically valid JSON response alone is insufficient. State whether a displayed payload is a wire capture, a deterministic reconstruction or an authored illustration. Do not claim access to hidden model reasoning.

## Retrieval and augmentation decisions

Start with the retrieval problem: finding relevant concepts, repository evidence, source passages, or answer documents are different tasks. In GitHub Manager the implemented path used deterministic README processing, RAKE phrases and a weighted lexical concept ranker. BM25 and YAKE were readiness comparisons; this does not mean dense embeddings, a vector database, a learned reranker or Anthropic-style contextual retrieval were deployed.

For a lexical baseline, document fields, weights, tokenization, aliases, matching/ranking, cutoff and tie behavior. Inspect sparse failure cases such as synonyms with no lexical overlap before proposing dense retrieval. For embeddings, identify the query/document unit, versioning, dimensions, storage, permissions, refresh cost and exact evaluation baseline. Hybrid retrieval and reranking are experiments with measurable latency/cost/quality consequences, not automatic improvements.

Chunk by evidence use. A section-aware README excerpt can preserve heading context and source coordinates without becoming a generic fixed-length chunk index. Record which transformations precede coordinates: an offset in cleaned text is not necessarily a line in the original README. Distinguish truncation from summarization. Packing retrieved candidates and source excerpts into a bounded request is augmentation; ranking them is not necessarily a neural reranker. An LLM-generated contextual prefix requires its own cost, provenance and ablation evidence before claiming contextual retrieval.

## Context, loop and harness responsibilities

- **Context:** task instructions, approved registry semantics, selected evidence, source IDs, exclusions and structured schema.
- **Loop:** bounded review/refinement or retries with explicit stopping conditions, change triggers and preserved user rejection semantics.
- **Harness:** admission checks, exact cohort, access/privacy policy, request limits, reservations, cache/replay rules, output validation, receipts and failure recovery.

State which component does what. A deterministic worker pipeline is not automatically an autonomous agent. SQLite state is not automatically conversational memory. Persistent approved taxonomy is organizational memory in a limited sense; explain that meaning rather than borrowing a broader RAG label.

## Separate durable states

Keep at least these concepts distinct when the product needs them: analyzed successfully; accepted label coverage; freshness of input/taxonomy; pending human review. A repository can be analyzed, have no Project, have accepted Topics and await review simultaneously.

Successful validated results create per-item receipts, including NO_MATCH and successes within partially failed runs. Guard already-analyzed items before provider construction and before paid token-count calls. Cache reuse and durable “already processed” receipts serve different purposes. History deletion, changed labels, stale evidence or a reset must not silently authorize paid repetition. Explicit re-analysis can be supported with reason, exact reviewed cohort and bounded cost. Automatic triggers may reconcile locally without clearing prior analysis.

## Evaluate the stage that makes the claim

| Stage | Relevant evidence |
| --- | --- |
| Source/extraction | Source coverage, phrase usefulness, coordinates, headings retained, no invented spans |
| Candidate retrieval | Recall@k, precision@k, ranking metrics, synonym/no-match errors, candidate exclusion audit |
| Classification | Per-type precision/recall/F1, exact ID validity, abstention/NO_MATCH quality, primary-purpose policy |
| Evidence support | Citation validity separately from entailment/groundedness, conflicting evidence |
| Taxonomy | Relevance, hierarchy/type, alias distinctness, useful grouping, human acceptance |
| Harness | No duplicate calls, budget admission, stale-result handling, restart and reset behavior |
| Product | Can users find, review and correct assignments with trustworthy status? |

Reference-free judge metrics can diagnose a result but do not replace independent labels. Calibrate judges against human decisions, log rubric/model/version, avoid self-grading as sole evidence, and account for judge calls separately. Browse current primary framework documentation when selecting an evaluation integration; do not bake a dated tool ranking into this skill.

Keep proposed, cross-reviewed and human-approved labels distinct. Separate development, validation and locked test groups; keep families, forks and near-duplicate lineages together to avoid leakage. Native GitHub topics may be input features, so using the same strings as independent truth can inflate scores. Preserve hard negatives, NO_MATCH, unsupported and ambiguous cases rather than forcing every example into the registry.

Report sample size, selection policy, reused cases, metric denominator, exclusions and uncertainty. GitHub Manager's reused 20-case result (50 TP, 0 FP, 2 FN; micro-F1 about 0.9804) was regression evidence, not independent production accuracy. Qualitative “looks ok” is not a numerical human rubric. Do not claim calibrated confidence, entailment evaluation or a deployed decision model without evidence.
