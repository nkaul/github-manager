# README section illustrations

Two compact orientation banners created on October 19, 2026 with the built-in
image-generation tool and the repository's
`illustrated-explainers` skill (kept locally).
The observed style reference was the skill's `assets/style-overview.png`:
white paper, hand-drawn navy outlines, indigo/blue accents, light marker washes,
and recognizable objects rather than dense service boxes.

| Asset | Purpose | Actual size |
|---|---|---|
| [Demo overview](demo-overview.png) | Preview the app walkthrough, architecture deep dive, and illustrated system design as three independent destinations | 2172 × 724 |
| [Evaluation overview](evaluation-overview.png) | Preview the 600-repository corpus, thirty human-reviewed repositories, and measured comparison with reviewed references | 2172 × 724 |

The images are linked from the corresponding sections of the
[root README](../../../README.md). The first opens the published demo; the second
opens the [plain-language evaluation](../../../eval/ai-system-design/evaluation/reviewed-30-v1/ground-truth-evaluation-explained.md).

## Content and review

The demo banner's vignettes are navigation choices, with no arrows suggesting a
processing sequence. The evaluation banner shows selecting a reviewed subset and
comparing results. It does not claim all 600 repositories received human review,
that human labels were sent to the classifier, or that every prediction was
correct. Its sample label marks illustrate comparison and are not a quantitative
chart.

Both exports were visually inspected in a browser preview at 860 pixels wide
(approximately 287 pixels tall each). All headings were readable, with no clipped
objects or dense fine print. Local images loaded successfully, and README link
targets were checked. Earlier diagrams and evaluation data were not changed.

The [exact prompt set](prompts.json) records the two generation requests. There
were two built-in image-generation calls, no correction calls, and no application
classification or evaluation API calls. [Verification](verification.json) records
asset hashes, dimensions, and local checks. Native PNGs were copied into the
repository without image editing; generated originals remain in their original
tool output location.

## AI Pipeline Overview addition · October 20, 2026

The third [AI pipeline banner](ai-pipeline-overview.png) links to
[Inside the GitHub Manager AI Pipeline](../../github-manager-ai-pipeline.md)
from the root README. It uses three independent vignettes: the Evidence Parser,
Canonical Retriever, and taxonomy/classification. There are no arrows implying
that taxonomy discovery uses the canonical retrieval branch. E0 and E1 are
schematic evidence markers; the full walkthrough explains their construction.
The image is 2172 × 724 pixels and appears second in the README navigation,
between Demo and Evaluation. Its three headings were inspected at 860px width.

The original two banners and their generation/verification receipts remain
unchanged. The new banner was generated with the built-in image tool, using the
same skill and observed visual language. Its exact prompt is in the
[October 20 prompt set](../ai-input-flows/illustration-alias-readme-rag-2026-10-20-prompts.json).
The user subsequently approved both wide RAG illustrations. The main pipeline
document now includes the RAG-only overview and the full registry-to-RAG picture.
The root README links that document with a short reader-facing introduction
beneath this banner. The banner itself remains the compact navigation graphic
created above.
