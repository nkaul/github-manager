# GitHub Manager — AI system design article

## Choose an edition

| Edition | Best suited to | Diagrams |
|---|---|---|
| [Academic edition](github-manager-ai-system-design.md) | Research review, precise architecture and implementation detail | Original eight block diagrams, editable SVGs and 3600×2160 PNGs; preserved unchanged |
| [Illustrated edition](illustrated/github-manager-ai-system-design-illustrated.md) | Accessible explanations, presentations and broader audiences | Separate hand-drawn, icon-led illustrations matching `docs/diagrams`; same audited technical case study |
| [Publication edition](publication/article.md) | Medium, Substack or LinkedIn articles | Shorter narrative with three simple editorial diagrams; includes a separate [LinkedIn feed post](publication/linkedin-post.txt) |

The illustrated edition has its own [figure catalog](illustrated/figures/README.md), [generation prompts](illustrated/figures/illustration-prompts.json) and [academic preservation record](illustrated/academic-preservation.json). Its images do not replace the academic article or original diagrams.

Read [Engineering a Repository Organizer Around Bounded Evidence](github-manager-ai-system-design.md), the detailed standalone case study of the implemented system, measured results, limits and research next steps.

The article covers context engineering in both development and runtime prompts; sparse candidate retrieval; RAKE/YAKE/BM25 and the exact binary-IDF cosine implementation; evidence/chunking and augmentation; structured generation; memory, controlled loops and harnesses; tokenomics; evaluation; and proposed embedding, contextual-retrieval and reranking experiments. It distinguishes deployed behavior, offline comparisons, historical design and future work.

## Package

| Artifact | Purpose |
|---|---|
| [Article](github-manager-ai-system-design.md) | More than 12,000 words, with source-linked claims and primary research references |
| [Evidence index](evidence-index.md) | Implementation entry points, dated reports, approved decisions and historical context |
| [Measurements](measurements.json) | Sanitized aggregates recomputed from the frozen public/synthetic experiment |
| [Source manifest](source-manifest.json) | SHA-256 of inspected implementation/evidence files and baseline commit |
| [Figure catalog](figures/README.md) | Eight PNG diagrams and editable SVG sources |
| [Package verification](verification.json) | Link, data, source preservation, image and document checks |
| [Scripts](scripts/README.md) | Recompute aggregate evidence, regenerate figures and verify this package without model calls |

## Main findings

The implemented system is retrieval-augmented structured classification with sparse canonical candidate search and durable application memory. It does not deploy dense embeddings, a neural reranker, an autonomous retrieval agent or Anthropic Contextual Retrieval. The latest real API round achieved 98.0% micro F1 on twenty **reused** public/synthetic cases; this is regression feasibility evidence, not independent generalization.

The strongest engineering mechanisms are source-linked bounded context, review-first canonical organization, durable no-repeat analysis receipts, explicit re-analysis, stale-write fencing and conservative monetary admission. The article also identifies validation/evidence-selection gaps and specifies experiments needed to assess improvements without overstating novelty.

Created October 14, 2026 under the repository root as requested. Prior readiness reports, benchmark files, app code, live data and spending controls are preserved. No paid API calls or publication were performed for this documentation task.

## Expanded publication v2

[Read the new publication v2](publication/v2/article.md) for a premise-first narrative with real taxonomy/classification traces and a Jev decision-model investigation. The [v2 package](publication/v2/README.md) includes platform copy, workflow data, editorial review and verification. Earlier editions and all prior diagrams remain preserved.
