# Explanation review — October 19, 2026

This is an authoring-agent self-review, not an independent human readability test. The document applies the project's [engaging-technical-writing skill](../../../../skills/engaging-technical-writing/SKILL.md).

The intended reader understands repositories but need not know evaluation or retrieval terminology. The useful outcome is to explain what entered the system, what the model was allowed to do, what the measurements mean and where their evidence can be inspected.

| Review pass | Problem addressed | Change made | Inspectable result |
|---|---|---|---|
| Structure | The old report led with metrics before establishing the task, inputs and meaning of a label. | Start with organizing a repository, define the four category kinds, separate evidence from the answer sheet, then explain the split. | Sections 1–3 establish the problem before algorithms or scores. |
| Explanation | Taxonomy discovery, candidate retrieval and classification can sound interchangeable. Recall, software pass and grounding can sound like conflicting accuracy claims. | Separate discovery from the fixed vocabulary. Follow one saved Airbyte Python CDK example through all three different measurements. Define LLM, API, canonical ID, alias, profile, JSON, augmentation and contract. | Sections 4–7 and 10 show the actual 2/3 recall, software pass and 3/4 grounding result with their different denominators. |
| Evidence and presentation | Percentages without units, an unexplained 30/30 pass and a tiny semantic sample can overstate reliability. | Add nine count-labelled figures, a complete thirty-case table, explicit zero Promptfoo score threshold, three-case grounding denominator, retained adapter failures and direct result/log links. Replace jargon in the split-chart title. | Figure exports, selected JSON, CSV, saved no-network logs and verification receipt accompany the document. |

The explanation retains the substantive original results: historical source/split context; RAKE/TF-IDF/alias/BM25/YAKE roles; evidence packing; reference unknowns; multiple-label scoring; taxonomy structure versus semantic review; paired model limits; Ragas/Promptfoo behavior; costs, failure accounting and future evaluation needs. Exact private input files remain linked rather than republished in full. One public-repository example and per-case aggregate counts make the evidence concrete without exporting human owner identity.

Limits remain explicit: only thirty selected human-confirmed repositories, one review owner, no exhaustive negative labels, no reviewed cloud example, no independent external holdout, no calibrated judge threshold and no human taxonomy-quality score. The article does not promise comprehension or engagement from an editorial checklist.

See [verification.json](evidence/verification.json) for calculations, preserved input/result hashes, links, image export checks and executed software-check evidence. No model generation was needed for this rewrite.
