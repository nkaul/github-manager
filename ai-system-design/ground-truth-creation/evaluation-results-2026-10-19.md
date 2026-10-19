# From reviewed repositories to measured retrieval and generation

**October 19, 2026 · Completed evaluation addendum.** Read this after the [illustrated ground-truth story](article.md). That article's October 18 narrative and diagrams remain preserved as the account of building the corpus and review workflow. This addendum records what happened after the user finished thirty repository reviews.

The question became concrete: when we give the app a repository, can it recover the labels the human retained—and where does it lose them?

## The missing label can disappear before the model sees it

We froze thirty real human confirmations containing **83 supported labels**. The application first searches canonical label definitions using sparse TF-IDF and an alias-token boost. It packs a bounded set of candidate Projects, Topics and Tags alongside repository metadata, selected README evidence and RAKE phrases. A LangChain structured-output call then chooses supported relationships.

The retrieval stage supplied **69 of the 83 labels**. The model selected **66 of those 69**. End-to-end recovery was therefore **66/83, or 79.5%**; recovery conditional on the candidate being supplied was **95.7%**.

That distinction changes the next engineering decision. Asking a stronger model to select from the same incomplete shortlist cannot recover labels it is prohibited from selecting. Fourteen of seventeen missed positives were already missing before generation, including twelve Topics. Topic retrieval is the clearest measured weakness.

| Facet | Human-retained | Retrieved | Selected |
|---|---:|---:|---:|
| Projects | 15 | 14 | 13 |
| Topics | 35 | 23 | 23 |
| Tags | 33 | 32 | 30 |

Offline BM25 with the same candidate limits retrieves **71/83**; doubled BM25 lists retrieve **73/83**. Those are useful leads, not a production victory. More candidates consume context and can encourage extra assignments. We did not change the application or regenerate test predictions with the most favorable alternative.

The live baseline was frozen before fifteen test-reserved generations. Those recover **34/41 positives (82.9%)**; fifteen development cases recover **32/42 (76.2%)**. Both preserve repository-family leakage groups. The small selected sample and prior vocabulary curation prevent an untouched-external-holdout or corpus-wide accuracy claim.

## A real citation still needs the right relationship

For the Airbyte Python CDK, the grounding judge supported its Airbyte initiative relationship, API-development capability and Python technology. It did not support GraphQL as a **primary technology** merely because the README described connector support for GraphQL APIs.

This is the same distinction that motivated the taxonomy: mentioning a technology, depending on it and primarily being built around it are different relationships. Mechanical validation can ensure that a canonical ID and an evidence ID exist. It cannot decide that the evidence establishes the relationship.

Ragas Faithfulness scored three development cases **1.0, 1.0 and 0.75**, a macro mean of **0.9167**. Each case used the actual evidence supplied to the producer, with two guarded judge generations. This is a useful diagnostic, not a calibrated quality guarantee or a new human-negative decision.

Promptfoo replayed all thirty saved outputs. Every contract check passed and every per-case score matched the local scorer. Its **30/30 pass rate means replay and contract validity**, not perfect classification. Ragas's deterministic ID metric independently matched candidate-concept coverage; this is not passage-search recall merely because a RAG framework computes it.

## Human confirmation is positive evidence, not an exhaustive answer key

The thirty reviews retain 83 positive assignments, but they do not declare every other concept wrong. The model proposed sixteen additional pairs that remain **unjudged**. Calling those false positives would manufacture negative labels that the human never supplied.

We therefore report recovery of known positives, candidate omissions, unjudged prediction counts and grounding separately. Exhaustive precision and F1 remain unavailable. A private exception sheet covers twenty repositories; the completed thirty reviews need not be repeated. Explicit adjudication of extra predictions is an optional next step if exhaustive precision in a declared scope is needed.

Only six confirmed repositories overlap the earlier independent A/B annotation pilot. Both readers contain all seventeen human-retained positives on that overlap, with fourteen additional A pairs and eighteen additional B pairs still unjudged. Those denominators do not support an accuracy claim for the entire pilot or six hundred repositories.

## A bounded harness includes its own mistakes

We used **50 generation attempts and 100 HTTP attempts**, with no batch above twenty HTTP attempts. Eight early HTTP-200 outputs were rejected by a new evaluation namespace adapter. We repaired the adapter, retained the failed receipts/costs and explicitly repeated those cases. To preserve the cap, the optional model comparison shrank from six to three repositories and grounding from four to three cases.

All thirty primary outputs eventually validated. Two development taxonomy drafts and consolidation also passed structural checks, producing twenty consolidated proposals. Semantic taxonomy quality was not human-rated and the proposals were not applied to the app.

The entire new evaluation recorded **76,617 input tokens, 16,081 output tokens and $0.133941 estimated API charges**, including adapter failures and replacements. Successful primary whole-call latency was p50 **4.188 seconds**, p95 **7.021 seconds** on this local serial run. All calls settled and the run grant is closed. The original cumulative accounting, including retained narration reservations, is **$4.316970 under the $5 ceiling**. Any further generation needs approval.

The frozen corpus and prior articles/diagrams remain preserved. All **2,423 source/dossier hashes**, **548 earlier protected artifacts**, frozen producer/input hashes, Ground Truth/sample workspace states and all thirty human reviews passed preservation checks. A concurrent live GitHub sync changed that separate workspace during reporting; its observation was retained without rollback. Operational extraction and candidate diagnostics passed for **600/600 repositories**; the other 570 still have no human-reference accuracy denominator.

## What the evidence says to do next

Improve Topic retrieval on development evidence, inspect whether supporting source material survives extraction/context packing, and evaluate a versioned alternative on fresh reviewed repositories. Measure the effect of candidate-budget and BM25 changes through generation rather than assuming retrieval gains transfer unchanged. Calibrate judges against explicit human support decisions before using their score to automate acceptance.

This run is complete and reportable without more API calls. Its most useful finding is the location of the bottleneck—and the evidence needed to avoid confusing a contract pass, a plausible extra label or an LLM judge's opinion with human ground truth.

[Detailed results and accounting](../../docs/validation/ground-truth-evaluation-2026-10-19.md) · [Aggregate statistics](evaluation-statistics-2026-10-19.json) · [Reproduction guide](../evaluation/reviewed-30-v1/README.md) · [Preserved October 18 statistics](statistics.json).
