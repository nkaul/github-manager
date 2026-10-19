# README section illustrations

Two compact orientation banners created on October 19, 2026 with the built-in
image-generation tool and the repository's
[Illustrated Explainers skill](../../../skills/illustrated-explainers/SKILL.md).
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
