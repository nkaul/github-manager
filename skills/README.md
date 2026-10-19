# Reusable GitHub Manager skills

Three composable skills, packaged October 16, 2026. They preserve the project's explanation style and engineering lessons without requiring another project to adopt its stack.

| Skill | Use it for | Start here |
| --- | --- | --- |
| `system-design` | Architecture reviews, material tradeoffs, ownership and phased plans | [SKILL.md](system-design/SKILL.md) |
| `illustrated-explainers` | Friendly paper-and-marker diagrams and diagram-style animation | [SKILL.md](illustrated-explainers/SKILL.md) |
| `engaging-technical-writing` | Clear technical articles with concrete mechanisms and evidence | [SKILL.md](engaging-technical-writing/SKILL.md) |

The existing writing skill is copied unchanged, including its license and provenance. The illustration skill includes three existing project images as style references. Their historical labels are not the architecture of your next project. System design keeps GitHub Manager-specific decisions in a dated case study.

## Use in this repository

The matching local folders are under `.agents/skills/`. Ask an agent to use the relevant skill by name and provide its path if the agent has not discovered it:

> Use `$system-design` at `skills/system-design/SKILL.md` to review this repository and produce a phased plan. This is planning only; wait for approval before implementation.

> Use `$illustrated-explainers` at `skills/illustrated-explainers/SKILL.md` to illustrate this workflow. Inspect the bundled style references and preserve the technical relationships in the supplied design.

> Use `$engaging-technical-writing` at `skills/engaging-technical-writing/SKILL.md` to revise this article. Preserve its substantive insights and show the actual input, operation, output and consequence.

Explicit path-based use works even if the host does not discover project-local skills automatically. Restart or refresh skill discovery if your host requires it.

## Reuse in another project or agent

Copy the entire desired skill folder, including `references/`, `agents/` and any `assets/`, into that project's `.agents/skills/` directory. For personal Codex installation, copy it into `${CODEX_HOME:-$HOME/.codex}/skills/`; inspect an existing same-name skill before replacing it. This bundle does not modify your global skill installation.

Other agents can read `SKILL.md` directly; the `agents/openai.yaml` file is optional host metadata. Preserve the writing skill's `LICENSE` and provenance when distributing it. New skill instructions synthesize this project's work; bundled images originate in this project and are not accompanied by a separate third-party license grant. Review redistribution rights before publishing the bundle outside the user's authorized context.

Use [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md) as a drop-in task preamble. Ready-to-adapt task prompts are in [prompts/](prompts/): [design](prompts/system-design.md), [illustration](prompts/illustration.md), [writing](prompts/writing.md) and [composed workflow](prompts/composed-workflow.md).

## Compose without loading everything

For an architecture article: establish facts and decisions with `system-design`; explain them with `engaging-technical-writing`; illustrate the approved mechanisms with `illustrated-explainers`. Each skill's entrypoint routes to conditional references. Read only those relevant to the current task. A small wording edit does not require a fresh system design.

For publication preparation, use the writing skill's platform adaptation reference and the illustration skill's visual QA guidance. There is no separate publishing skill in this bundle. Drafting, local preview and media generation do not themselves authorize external publication; existing explicit session permission still applies.

The bundle's [validation report](validation-report.md) records scope, structural checks, provenance and review limitations. `source-preservation.json` records the unchanged writing originals and style-image origins; `manifest.json` records packaged-file hashes. Maintain canonical project-local and portable copies together if editing either later.
