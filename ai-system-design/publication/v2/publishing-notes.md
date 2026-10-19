# Publication v2 handoff

The [complete article](article.md) is prepared for Medium, Substack or a LinkedIn article. The [feed post](linkedin-post.txt) is a separate native adaptation. This package is saved locally; it has not been published externally.

## Headline and introductory copy

Selected headline: **Making Sense of Your GitHub Repositories**

Subtitle: **How GitHub Manager turns repository evidence into an organization you can review, and what the build teaches about context, retrieval, memory and bounded AI.**

Alternatives:

- **Building an AI Repository Organizer Around Evidence and User Decisions**
- **Inside GitHub Manager: From README Evidence to an Organized Workspace**

The selected headline leads with the reader's task. The subtitle makes the engineering payoff explicit. It avoids implying a new algorithm, measured productivity gain or production deployment.

Preview:

> A library and an application can share Python and FastAPI while serving different purposes. GitHub Manager uses repository evidence, an approved vocabulary and human review to organize those relationships. This case study follows the actual data through taxonomy, retrieval, generation and repeat work.

Substack/email introduction:

> A useful GitHub collection needs more than a list of languages and repository names. This edition walks through the AI workflow behind GitHub Manager with real saved examples: what gets extracted, which concepts retrieval returns, what the model receives and how user decisions survive later changes. It also shows where the current approach falls short and what a Jev decision-model experiment would need to prove.

## Platform treatment

| Destination | Treatment |
|---|---|
| Medium | Preserve the complete narrative and section order. Upload the five figures at their marked locations, including captions and alt text. Retain the result qualification beside the metric. |
| Substack | Use the complete article and the email introduction above. Keep the concrete examples, including the evidence-selection weakness; the longer length is intentional. |
| LinkedIn article | Use the full article. If tables/code are not retained by the editor, format the same data as lists or screenshots with accompanying text. Do not replace the mechanisms with an abbreviated feed post. |
| LinkedIn feed | Use the standalone plain-text post. It establishes the product premise and one real saved classification example. The synthetic fixture and proposed Jev status remain explicit. |

No current platform character-limit, ranking or reach claim is made. Word/character counts are recorded in [verification.json](verification.json) as editorial measurements, not platform acceptance tests. Reading time is only a rough estimate; the worked examples invite slower inspection.

## Figure placement and accessibility

| Figure | Placement | Alt text |
|---|---|---|
| [Existing overview](../figures/01-evidence-to-decisions.png) | After the opening premise | Repository discovery leads to purpose evidence, approved concepts and user review. Domains derive through Projects. |
| [Two AI phases](figures/01-two-ai-phases.png) | After the taxonomy types and phase distinction | Collection evidence generates proposed concepts for human review; classification retrieves approved candidates for one repository and returns supported IDs for review. |
| [Classification data](figures/02-data-through-classification.png) | After the Orion request/result walkthrough | Purpose evidence leads to six candidate concepts; evidence, definitions, instructions and schema form the request. Four supported labels are reviewed and two distractors remain unselected. |
| [Existing receipts](../figures/02-remember-the-analysis.png) | Analysis lifecycle section | Receipts separate first inference from local reconciliation and keep explicit re-analysis available. A no-match can be completed work. |
| [Existing budget](../figures/03-accountable-model-calls.png) | Execution/cost section | Count the complete request, reserve a conservative maximum, generate within limits and settle reported usage; unknown usage stays reserved. |

The new drawings match the project's white-paper, hand-drawn illustration style. The two-phase image is a conceptual workflow, not proof that the saved draft supplied the benchmark's IDs. The data-path image abbreviates the README wording; the verbatim text and full JSON are available in the article and [workflow companion](workflow-examples.md).

Preserve whole images and captions. At narrow phone widths, use full-size image viewing or zoom to inspect small labels; the article and alt text carry their meaning without requiring the image text to be legible at thumbnail size. The unselected Forge and Package Management candidates are meaningful, so do not crop them away.

## Evidence handoff

The [claim-check sheet](claim-checks.md), [workflow artifacts](workflow-examples.md) and [editorial review](editorial-review.md) are editor-facing companions. Keep critical scope statements in the article itself:

- Orion is synthetic; the provider responses are saved real API results.
- Logical input reconstructions match historical cache keys. The serialized bodies are current offline captures, not original wire logs.
- The generated taxonomy and seeded classification registry have separate provenance.
- 98.0% is micro F1 on twenty reused public/synthetic cases, not general accuracy or independent production evidence.
- The round's spending is a historical inference ledger estimate, not total project cost or a reconciled invoice.
- The application is local, and Jev/dense retrieval/reranking/contextual enrichment remain proposals.

The linked GitHub Pages site hosts recordings and overview material; it is not the deployed interactive application or a public source-code/results repository. Do not invent a public URL for the local article or raw benchmark package. Replace local artifact links with their eventual real destinations if this package is published later.

Select the author's actual byline in the publishing editor. No biography or credentials are supplied here. Preserve the method note and illustration disclosure. External publication remains a separate action.
