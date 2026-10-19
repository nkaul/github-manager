# Explanation review — October 19, 2026 · revisions 1 and 2

This is an authoring-agent self-review, not an independent human readability test. The document applies the project's [engaging-technical-writing skill](../../../../../skills/engaging-technical-writing/SKILL.md).

The intended reader understands repositories but need not know evaluation or retrieval terminology. The useful outcome is to explain what entered the system, what the model was allowed to do, what the measurements mean and where their evidence can be inspected.

| Review pass | Problem addressed | Change made | Inspectable result |
|---|---|---|---|
| Structure | The old report led with metrics before establishing the task, inputs and meaning of a label. | Start with organizing a repository, define the four category kinds, separate evidence from the answer sheet, then explain the split. | Sections 1–3 establish the problem before algorithms or scores. |
| Explanation | Taxonomy discovery, candidate retrieval and classification can sound interchangeable. Recall, software pass and grounding can sound like conflicting accuracy claims. | Separate discovery from the fixed vocabulary. Follow one saved Airbyte Python CDK example through all three different measurements. Define LLM, API, canonical ID, alias, profile, JSON, augmentation and contract. | Sections 4–7 and 10 show the actual 2/3 recall, software pass and 3/4 grounding result with their different denominators. |
| Evidence and presentation | Percentages without units, an unexplained 30/30 pass and a tiny semantic sample can overstate reliability. | Add nine count-labelled figures, a complete thirty-case table, explicit zero Promptfoo score threshold, three-case grounding denominator, retained adapter failures and direct result/log links. Replace jargon in the split-chart title. | Figure exports, selected JSON, CSV, saved no-network logs and verification receipt accompany the document. |

The explanation retains the substantive original results: historical source/split context; RAKE/TF-IDF/alias/BM25/YAKE roles; evidence packing; reference unknowns; multiple-label scoring; taxonomy structure versus semantic review; paired model limits; Ragas/Promptfoo behavior; costs, failure accounting and future evaluation needs. Exact private input files remain linked rather than republished in full. One public-repository example and per-case aggregate counts make the evidence concrete without exporting human owner identity.

Limits remain explicit: only thirty selected human-confirmed repositories, one review owner, no exhaustive negative labels, no reviewed cloud example, no independent external holdout, no calibrated judge threshold and no human taxonomy-quality score. The article does not promise comprehension or engagement from an editorial checklist.

See [verification.json](evidence/verification.json) for calculations, preserved input/result hashes, links, image export checks and executed software-check evidence. No classification or judge API generation was added for the explanation.

## Revision 2: collection context, concrete results and public illustrations

The user requested fuller context for acquiring the 600 repositories, more concrete internal results and a visible inventory of Ragas checks. The original complete guide, evidence and nine PNG/SVG chart pairs are preserved in the [version 1 archive](../history/plain-language-evaluation-v1-2026-10-19.zip).

| Issue | Change and verification |
|---|---|
| Six hundred repositories appeared without an acquisition story. | Added the three-agent original collection, two-agent English-first refresh, query/source rules, 489 retained/111 replacements, exclusion reasons and ten-area distribution. Retention counts were independently recalculated by comparing original/current numeric repository IDs. |
| “Performance” mixed measured semantic recovery with software completion. | Added an internal scorecard, facet/split/domain tables, missed-label locations and the small paired model comparison. Printed facet and split tables are checked directly against saved metrics. |
| Ragas completion could be mistaken for an unexplained quality pass. | Named R1–R8 with input, operation, actual result and pass meaning. Four ID views reuse the same thirty cases; three semantic judgements have no automatic threshold; the mock fanout check is separate. All nine actual claim verdicts are visible. |
| Publication needed semantic illustrations, not only numeric charts. | Applied illustrated-explainers with a real style reference and three built-in image generations. One targeted correction adds an explicit after-the-run/scoring-only label and changes an arrow to a plus sign for extra predictions. Final illustrations were inspected for exact counts, qualifiers and readable text. |

The selected public assets are in [the illustration kit](../public-illustrations/README.md), with exact original/correction prompts, native export dimensions, hashes, captions and alt text. Four built-in illustration calls are recorded separately from the unchanged application API ledger. No additional classification/judge call, new GitHub crawl, human-reference edit or production configuration change occurred.
