# Diagram catalog

All diagrams have editable SVG sources and publication-resolution PNGs at **3600×2160**. Their whiteboard lettering, dark pen outlines and blue/indigo/purple panels follow the earlier [system architecture illustration](../../../docs/diagrams/github_manager_system_architecture.png). Labels are generated deterministically, without an image-generation model or external network requests.

PNG lettering is rendered using locally available fonts. SVGs use Chalkboard SE, Comic Sans MS and Trebuchet MS fallbacks; appearance may vary on another operating system. A renderer audit checks card text and canvas bounds. The figures were also visually inspected. Solid arrows indicate the illustrated workflow; dashed arrows indicate control feedback or proposed experiments, as labeled.

| Article figure | Diagram | Editable source |
|---|---|---|
| 1 | [Actual local architecture](01-actual-system.png) | [SVG](01-actual-system.svg) |
| 2 | [Evidence selection and chunking](03-evidence-and-chunking.png) | [SVG](03-evidence-and-chunking.svg) |
| 3 | [Retrieval, augmentation and generation](02-retrieval-and-generation.png) | [SVG](02-retrieval-and-generation.svg) |
| 4 | [Contextual Retrieval comparison](07-contextual-retrieval-comparison.png) | [SVG](07-contextual-retrieval-comparison.svg) |
| 5 | [Controlled analysis loop](04-controlled-analysis-loop.png) | [SVG](04-controlled-analysis-loop.svg) |
| 6 | [Harness and tokenomics](05-harness-and-tokenomics.png) | [SVG](05-harness-and-tokenomics.svg) |
| 7 | [Evaluation evidence](06-evaluation-evidence.png) | [SVG](06-evaluation-evidence.svg) |
| 8 | [Future experiment roadmap](08-future-experiment-roadmap.png) | [SVG](08-future-experiment-roadmap.svg) |

The original diagrams illustrate the approved AWS target. Figure 1 instead shows the implemented local adapter; it does not depict DynamoDB/SQS as the deployed runtime. Figure 7 summarizes measured regression results without implying independent test-set performance. Figures 4 and 8 explicitly label proposed mechanisms and external research.

See [the layout audit](layout-audit.json) and [rendering instructions](../scripts/README.md).
