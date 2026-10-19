# Publication handoff

## Main article

Recommended headline: **What Building a GitHub Organizer Taught Us About Reliable AI**

Subtitle: **Lessons in context engineering, retrieval, useful memory and making every model call accountable.**

Alternative headlines:

- **Context, Memory and Control: The Engineering Behind GitHub Manager**
- **A Receipt for Every AI Decision: Lessons From Building GitHub Manager**
- **Building an AI Repository Organizer That Preserves User Decisions**

Preview/excerpt:

> A repository can have useful labels and a completed AI analysis while belonging to no Project. Building GitHub Manager showed us why reliable AI needs meaningful context, durable processing history and clear controls around every model call.

Use [article.md](article.md) as the complete Medium/Substack or LinkedIn article draft. Its reading-time and word-count measurements are in [verification.json](verification.json); the estimates use 225 words per minute and are editorial estimates rather than platform-calculated values.

## Platform adaptations

| Destination | Prepared treatment |
|---|---|
| Medium | Use the headline, subtitle, complete article and inline diagrams. Upload each local PNG where its Markdown image appears, then preserve the caption and alt text. |
| Substack | Use the same article. The preview above can serve as the email description; the first diagram works as the opening image. Keep the benchmark qualification adjacent to the results. |
| LinkedIn article | Use the complete article with its images and result table. If the editor does not retain the table, turn its seven rows into a short list with the same numbers and qualifications. |
| LinkedIn feed | Use [linkedin-post.txt](linkedin-post.txt). Attach the first diagram if desired. The copy is plain text, including the demo URL; it does not rely on Markdown rendering. Its character count is recorded in verification. |

The post invites discussion about repeat inference. The long-form article preserves the fuller narrative and operating tradeoffs. No claim about platform ranking algorithms, reach or posting-time optimization is implied.

## Image placement and accessibility

| Asset | Placement | Alt text |
|---|---|---|
| [Evidence to decisions](figures/01-evidence-to-decisions.png) | After the opening; also the suggested feed attachment | Four steps connect repository discovery, purpose evidence, canonical concepts and human review. |
| [Remember the analysis](figures/02-remember-the-analysis.png) | Analysis receipts and local reconciliation section | A receipt check separates bounded first analysis from local reconciliation, with deliberate re-analysis available. |
| [Accountable model calls](figures/03-accountable-model-calls.png) | Harness and spending section | Count the complete request, reserve its maximum, generate within limits and record usage; uncertain costs stay reserved. |

The diagrams are deliberately simpler than the full technical illustrations. The article carries the detailed qualifications. Do not crop away the notes on user authority, NO_MATCH, explicit re-analysis or uncertain cost.

## Evidence and scope

The [claim-check sheet](claim-checks.md) is an editor's companion, not part of the publishable article body. It links to the local audit and saved reports. The public application-source repository and full benchmark artifacts have not been assumed to exist online; no invented source-code or results URL appears in the draft.

The public [demo](https://nkaul.github.io/github-manager-demo/) and [architecture deep dive](https://nkaul.github.io/github-manager-demo/deep-dive/) returned HTTP 200 when checked on October 14, 2026. That URL check does not claim a fresh video-playback or full application test.

Keep these distinctions during editing:

- 98.0% is **micro F1 on twenty reused cases**, not general accuracy or an independent production estimate.
- The $0.003319 value is a **round inference ledger estimate**, not the whole project's cost or a verified invoice.
- Both current retrieval and local reconciliation should remain distinguishable from proposed dense retrieval, reranking and agentic search.
- Existing USER decisions, protected rejections and an explicit path to re-analysis are all part of the design.
- The product runs locally; cloud production infrastructure remains deferred.

Select the preferred author/byline in the publishing editor. The draft intentionally avoids inventing credentials or an affiliation. The article's short method note discloses its source basis and AI-assisted illustration process.
