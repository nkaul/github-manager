# Publication v2: writing skill and editorial plan

**Date:** October 15, 2026  
**Status:** Awaiting user approval. Research and planning are complete; skill creation, article rewriting and new illustration work have not begun.

**Latest scope clarification:** preserve the existing content and insights; improve the story and explanations without a shortening target. Add real, inspectable examples of the taxonomy and classification workflows, including retrieval, augmentation and the actual model-input structure. Investigate TypeSafe AI's Jev as future work. These additions are part of the plan awaiting approval.

## 1. What needs to change

The [current article](article.md) has useful technical evidence, but its opening assumes that readers already understand GitHub Manager. Its first sentence introduces Topics, Tags, completed analysis and Projects through an internal classification issue. The reader has not yet learned what the product does, whose problem it solves or why that problem deserves attention.

The article then moves through engineering subjects in sequence. Context, retrieval, authority, memory and budgets are individually explained, but the reader has to assemble the product story. The [LinkedIn post](linkedin-post.txt) inherits the same receipt-first opening. Improving vocabulary alone will leave that structural problem in place.

V2 should establish a recognizable situation: a person has repositories they own, contribute to or save for later, but names and programming languages do not explain how those repositories fit their work. GitHub Manager helps that person discover repositories, understand their purpose and review an organization they control. The technical story should explain how the implementation supports that outcome.

This is an editorial premise, not a measured claim about all GitHub users. We will not invent customer interviews, repository counts, time savings, personal experiences or production results to dramatize it.

| Current difficulty | Proposed correction |
|---|---|
| Internal terminology arrives before the product premise. | Establish the reader, task, friction and useful outcome before introducing taxonomy. |
| Parallel lessons feel like an inventory. | Follow one repository through the workflow, with each engineering choice solving an encountered problem. |
| Named methods compete for attention. | Explain their purpose and mechanism first; introduce names when they help understanding. |
| The solution emerges piecemeal. | Show the user-visible workflow early, then reveal its implementation progressively. |
| Qualifications interrupt the story repeatedly. | Keep material limitations beside the claims they qualify, and put detailed methodology in the companion material. |
| Diagrams show the pipeline but cannot establish the premise alone. | Explain the problem and intended outcome in prose before showing the overview. |

## 2. Public skill investigation

Relevant public `SKILL.md` files do exist. These are editorial resources, not independently validated interventions that guarantee engagement. The following assessment is based on their published instructions, not repository popularity. No remote skill has been installed or executed.

| Public skill | Useful fit | Adaptation needed | License checked |
|---|---|---|---|
| [sjmoran: blog-prose](https://github.com/sjmoran/claude-blog-prose/blob/master/skills/blog-prose/SKILL.md) | Strongest fit for explaining a system to a first-time reader: layered explanation, concrete examples and checkable claims. | Large single entrypoint with strict stylistic defaults. Select relevant guidance, preserve the user's voice and add a compact staged workflow. | [MIT](https://github.com/sjmoran/claude-blog-prose/blob/master/LICENSE) |
| [Xamfonos: technical-writing-best-practices](https://github.com/Xamfonos/technical-writing-best-practices/blob/main/SKILL.md) | Strong problem-to-solution structure, causal transitions and teaching guidance. | Avoid a mandatory story arc for every genre and blanket removal of uncertainty language. | [MIT](https://github.com/Xamfonos/technical-writing-best-practices/blob/main/LICENSE) |
| [Sentry: blog-writing-guide](https://github.com/getsentry/skills/blob/main/skills/blog-writing-guide/SKILL.md) | Useful developer-facing openings, tradeoffs and editorial checks. | Company voice, byline rules and SEO prescriptions are specific to Sentry and this guide's intended use. | [Apache 2.0](https://github.com/getsentry/skills/blob/main/LICENSE) |
| [Mark-Life: writing-for-readers](https://github.com/Mark-Life/agent-skills/blob/main/skills/communication/writing-for-readers/SKILL.md) | Useful reminders about spoken clarity and retaining specific facts. | Rigid sentence-variance, contraction and shortening quotas are unsuitable as acceptance criteria for this article. | [MIT](https://github.com/Mark-Life/agent-skills/blob/main/LICENSE) |

**Recommendation:** reuse and adapt the MIT-licensed `blog-prose` foundation into a compact, reusable `engaging-technical-writing` skill. Add the requested progressive loading, explicit refinement loop and observable acceptance checks. A new workflow is justified by those requirements; a claim that no public writing skills exist is not.

Before incorporating material, record an immutable upstream commit, the reviewed file hash, attribution, license and local modifications. Preserve the applicable license and copyright notice. Other candidates remain research references; there is no need to bundle four overlapping skills. The adaptation will follow the user's instructions when they differ from an upstream default.

## 3. Reusable skill design

Proposed location after approval:

```text
.agents/skills/engaging-technical-writing/
  SKILL.md
  agents/openai.yaml
  references/
    narrative-and-explanation.md
    review-and-refinement.md
    platform-adaptations.md
    provenance.md
  LICENSE
```

This project-local location makes the workflow versionable with the repository. The skill can be used by its path even if automatic discovery requires a session refresh. A global installation is outside this proposal.

The skill should apply to technical articles, newsletters and professional posts that need a clearer explanation or stronger narrative. It should support diagnosis, drafting, revision and platform adaptation without forcing a full article workflow onto a small edit. GitHub Manager's facts belong in the article brief and evidence records, not in the reusable skill.

**Progressive disclosure for the agent:** metadata identifies the use case; a short `SKILL.md` gives the essential workflow and constraints; supporting references load only for the current activity. Narrative guidance is relevant during structural work, the review rubric during validation, and platform guidance during adaptation. Large catalogs of style prohibitions will not sit in the entrypoint.

**Progressive disclosure for the reader:** familiar situation → concrete problem → visible solution → worked example → engineering explanation → evidence and tradeoffs → useful next step. This is a flexible teaching sequence. It should not manufacture a failed approach or pretend that an illustrative alternative was historically implemented.

Progressive disclosure changes the order and layering of information, not the amount of insight retained. The review workflow will include a coverage map from the source article to the new draft. Missing concepts must be restored or explicitly resolved with the user; a readability score cannot justify silently dropping them.

The skill will preserve technical depth by introducing it at the point where it answers a reader's need. It will distinguish observations, interpretations and proposals; keep necessary caveats; and prohibit invented anecdotes, measurements or expert endorsements. Readability checks will flag passages for judgment rather than impose artificial prose quotas.

## 4. Proposed v2 article strategy

**Primary audience:** technically curious developers, data scientists and product builders who understand repositories but have never used GitHub Manager. No prior knowledge of its taxonomy or AI workflow is assumed.

**Reader promise:** understand how the app turns a repository collection into reviewable organization, and take away practical design choices for building an AI feature that preserves user decisions and controls repeat work.

**Working headline:** *Making Sense of Your GitHub Repositories with Reviewable AI*. Develop two alternatives after the draft is stable and select the one that best matches the delivered explanation.

**Central argument:** organizing repositories requires understanding their purpose, maintaining a vocabulary the user controls, and remembering previous decisions. The AI workflow and its execution controls support those product needs.

There is no word-count reduction target. Preserve the current article's substantive insights and add the requested workflow detail. Length will follow the explanation, with clear navigation, examples and layered depth to support a longer read. The shorter LinkedIn feed adaptation serves a different format and does not replace the complete article.

| Narrative stage | Reader's need | Planned content |
|---|---|---|
| Establish the situation | Understand the practical problem. | Repositories accumulate across different relationships; names and languages provide only part of the context. |
| Show the solution | Picture what using GitHub Manager achieves. | Connect GitHub, discover repositories, review proposed concepts, classify against approved concepts and browse accepted relationships. Explain Projects, Domains, Topics and Tags through their jobs. |
| Follow concrete examples through both AI phases | See how meaning becomes an organizational decision. | Use documented public examples such as FastAPI, plus a clearly labeled synthetic initiative case where needed. Show actual evidence, intermediate representations, retrieval output, assembled model inputs and validated results. Distinguish historical observations from current deterministic reconstructions. |
| Explain useful context and retrieval | Understand why the system uses selected evidence and a shortlist. | Purpose text, negation and compact context; sparse candidate retrieval; the distinction between finding possible labels and deciding which are supported. Explain the actual RAG pattern without listing every RAG family. |
| Explain decisions over time | Understand why reviews and prior work persist. | User authority, completed analysis independent of label coverage, local reconciliation and deliberate re-analysis. Introduce receipts after the repeat-work problem is clear. |
| Explain bounded execution | Understand how work stays reviewable and affordable. | The count/reserve/generate/record contract, finite budgets and uncertain outcomes. Connect controls to the workflow rather than enumerate configuration settings. |
| Show evidence and its limits | Assess what was demonstrated. | A readable account of the 20-case regression round, its errors and its limited scope. Include the single-case context comparison only where it explains a design decision. |
| Examine the next architecture choices | Understand what deserves testing next. | Preserve the current evidence-packing, validation, evaluation and retrieval proposals; add the researched Jev decision-model assessment and its implications. |
| Return to practical use | Leave with a transferable idea and a way to explore. | A builder takeaway and the existing demo/deep-dive links. |

The example will not force FastAPI into a fictional personal Project. Separate public-library classification from any explicitly labeled synthetic initiative example needed to explain Project membership. Shared technology alone must not be presented as evidence of a shared initiative.

The [academic](../github-manager-ai-system-design.md) and [illustrated](../illustrated/github-manager-ai-system-design-illustrated.md) editions remain available for additional research detail. Links to them will supplement the v2 explanation. All substantive topics in the current publication article stay covered in v2: semantics, extraction, retrieval, augmentation, generation, authority, receipts, reconciliation, tokenomics, evaluation, limitations and improvement proposals.

### Worked data: make both workflows inspectable

The article will show readable data at each important boundary. The companion examples will preserve complete relevant JSON and prompts so that abbreviated inline displays do not conceal what the model actually receives.

| Boundary | What the reader will see | Algorithm or policy to explain |
|---|---|---|
| Source repository | Named public repository, source/version provenance, metadata and a short verbatim purpose excerpt from the retained sample. | Public-input verification; distinction between GitHub facts and application organization. |
| Extracted evidence | The selected heading/text, evidence IDs, cleaned-text offsets and retained phrases. | Heading-based block selection, bounded text, RAKE phrase scoring and its role; YAKE as an evaluated alternative. Explain what is lost, retained or merely proposed for improvement. |
| Taxonomy collection | Several actual compact repository records, with the collection's bounds visible. | Per-repository compaction and collection packing. Taxonomy discovery does not use the classification candidate retriever. |
| Taxonomy model input | Actual system instructions, assembled collection payload and structured response schema; relevant model/token settings. | LangChain's schema-bound request, exact input counting and budget admission. Explain that discovery proposes vocabulary rather than assigning approved IDs. |
| Taxonomy result and publication | A saved real draft, its supporting repository IDs, review/edit checks and the transition to approved canonical concepts. | Hierarchy validation, same-kind naming/alias conflicts, opt-in remediation and human publication. Do not imply that an unreviewed draft is canonical state. |
| Classification query and registry | Full selected evidence used as the lexical query; actual canonical names, descriptions and aliases used to build searchable documents. | Tokenization and binary-IDF cosine, the alias boost, per-kind candidate caps and the BM25/alias alternatives. Explain shared technology versus initiative membership. |
| Retrieval output | Actual candidate IDs, names, kinds, ranking/scores where recomputable, and why relevant and distracting candidates surfaced. | Query/document overlap and IDF contribution; filtering rejected, manual, rule-covered and existing relationships. A lexical score is not a probability or a final assignment. |
| Augmented classification input | The exact compact evidence/phrase bundle plus candidate objects, primary-purpose instructions, evidence references and output schema. | Prompt assembly as augmentation. Show that retrieval can use more evidence than the compact model input retains. Aliases influence retrieval but the candidate objects sent to classification contain IDs, kinds, names and descriptions. |
| Before generation | The serialized request components, counted input and conservative cost reservation, where retained or safely reconstructable. | Schema overhead, maximum output allowance, finite caps and handling of uncertainty. There is no implemented neural reranker or hidden summarization call to insert into this trace. |
| Generated result | Actual saved assignments, status, evidence IDs, short reasons and available usage. | Distinguish the provider's returned answer from reference labels. Do not invent hidden chain-of-thought or claim that a valid schema proves semantic support. |
| Application outcome | Validation outcome, reviewable associations, derived Domains, receipt and later local reconciliation or explicit re-analysis. | Canonical-ID/type checks, workspace and freshness fences, user precedence, rejection protection and no-repeat admission. |

For the scoring explanation, use a small actual token-overlap example and the implemented formula, then connect it to a computed shortlist. Do not invent rounded scores or imply that the retriever currently exposes diagnostics that it does not. Offline diagnostic recomputation may be used after approval without changing the application or prior reports.

**Provenance rules for examples:**

- Prefer retained public/synthetic samples and observed provider results from the saved work. Keep source/model/prompt versions and hashes where available.
- Label a historical observed response, a current offline reconstruction and an authored synthetic fixture distinctly. Exact serialized input must not be called an original wire capture if it was reconstructed from code.
- Do not splice a historical taxonomy draft, a separately seeded benchmark registry and a later classification response into a fictitious continuous run. If they have different origins, explain the relationship or present separate faithful traces.
- Use the app's actual discovery path and the frozen benchmark's actual generation path as separate evidence classes where their implementations differ. Show any consolidation/batching path only if it was used for the example being described.
- Reference labels and gold answers never become model inputs. Private repository content, credentials and request authorization headers are excluded.
- If an original intermediate artifact was not retained, disclose that gap and reconstruct only deterministic stages. A missing hosted response is not replaced with an invented answer. Any additional paid live verification would need a separately specified scope and limit; the default authoring plan uses existing results.

### Future investigation: TypeSafe AI's Jev

The user confirmed [Jev from TypeSafe AI](https://typesafe.ai/blog/introducing-system-one-models-and-jev). Its documentation describes typed questions against supplied state, returning decisions and probability information rather than open-ended prose. This makes bounded judgments a plausible area to investigate; it does not establish usefulness for this application. [Official introduction](https://docs.typesafe.ai/introduction).

The v2 next-steps section and a companion research note will assess these hypotheses:

| Potential use | Proposed experiment | Important implication |
|---|---|---|
| Candidate or evidence relevance | Judge retrieved concept/evidence pairs, then compare the resulting shortlist with the current lexical baseline and an LLM alternative. | A new decision/reranking layer can discard correct candidates. Measure recall before generation and total workflow cost, not just decision latency. |
| Closed-vocabulary classification | Evaluate each candidate's support, or use appropriately decomposed typed questions, with abstention and review paths. | The app is multi-label. A single mutually exclusive Choice across all Projects, Topics and Tags would change the task. Test per-candidate decisions and their cross-label consistency. |
| Evidence sufficiency and review routing | Assess whether the supplied text supports a bounded claim and whether the case needs more context or human review. | Thresholds must be validated on this task; a confident answer can still be wrong. Do not use the model to override deterministic privacy, budget or re-analysis authorization. |
| Taxonomy assistance | Assess already proposed duplicates, aliases or candidate relationships for review. | Generating new names, descriptions and an open-ended taxonomy remains a generation task. Bounded decisions may complement that work; they are not a direct replacement for discovery. |

The research will distinguish vendor claims from independent evidence and application-specific hypotheses. It will examine fixed model versions, documented limits, data handling, new credentials/provider dependency, retries, failure modes and the effect of fallback calls on the existing ledger and receipts. No Jev integration or paid test is included in this authoring plan.

Two nuances already warrant explicit treatment: a Choice selects one option, while this product permits multiple assignments; and reported confidence is a statistic derived from model probabilities, not an independently demonstrated accuracy estimate for GitHub Manager. The research will evaluate probability calibration and abstention on held-out data rather than reuse current LLM confidence thresholds unchanged. [Choice documentation](https://docs.typesafe.ai/primitives/choice), [confidence documentation](https://docs.typesafe.ai/confidence).

Use the same approved task semantics and evidence when proposing comparisons. Evaluate per-kind precision/recall/F1, no-match behavior, negation and near-neighbor errors, calibration, selective risk versus coverage, human corrections, end-to-end latency and total cost including fallback. Keep the existing 20-case regression results separate from any proposed independent evaluation. Document relevant known limitations, including the vendor's version-specific caveats. [Jev 1.13 limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13).

## 5. Diagram strategy

Reuse the existing [evidence-to-decisions overview](figures/01-evidence-to-decisions.png) after the product premise. Use the [analysis-memory diagram](figures/02-remember-the-analysis.png) when the narrative reaches repeat work. Include the [budget diagram](figures/03-accountable-model-calls.png) only if it adds understanding beyond the prose.

The images under `docs/diagrams` remain the visual style reference: hand-drawn lines, friendly semantic illustrations, clear labels and restrained accent colors. Their older behavioral descriptions must be checked before reuse; visual style does not make an older architecture statement current.

If the completed outline reveals a genuine visual gap, create up to two additional simple illustrations in the same style: one showing the distinct taxonomy/classification paths and one showing source text → extracted evidence → retrieved concepts → augmented request → reviewed result. Each should use small, readable data examples from the documented trace. A figure should explain a transition, not decorate the article. New assets will live under v2; existing images will remain unchanged. Every included image needs a useful caption, alt text and a legibility check at article width and on a narrow screen.

## 6. Optimization, validation and refinement

The skill will make the following workflow reusable. For this article, use the actual v1 as the baseline and record changes with passage-level evidence.

1. **Brief and evidence inventory.** Define audience, practical problem, reader payoff, central argument and supported examples. Consult the existing [claim checks](claim-checks.md) and [evidence index](../evidence-index.md). Establish preservation hashes before edits. Inventory the current article's insights and trace their coverage in v2.
2. **Structure pass.** Write a causal outline and identify the question each section resolves. Check the opening against the reader's lack of product knowledge. Remove tangents or move them to companion notes.
3. **Explanation pass.** Draft around the worked examples for both AI phases. For each important mechanism, explain the problem it addresses, how it works, its consequence and its relevant tradeoff. Show its input/output data and introduce specialist terms after their purpose is understood.
4. **Editorial pass.** Improve sentence clarity, transitions, rhythm, concrete language and useful headings. Read aloud to catch unnatural phrasing. Produce a reverse outline from the actual paragraphs and reconcile it with the intended argument.
5. **Evidence and visual pass.** Audit numerical and architectural claims, examples, citations, qualifications and figure labels. Check that the article works without the images and the images reinforce the prose.
6. **Cold-read review and bounded revision.** Review the draft from the intended reader's perspective, record where a premise or connection is missing, and repair the highest-impact issues. Allow up to three substantive refinement passes. Report unresolved issues rather than declare a misleading pass.
7. **Platform adaptation and handoff.** Prepare platform-specific introductory copy and a native LinkedIn post after the main argument is stable. Validate links, image paths, counts, preservation and skill packaging.

Sequential self-review is not an independent human reader study. No human comprehension result or engagement lift will be claimed without that evidence.

### Editorial rubric

Record v1 and v2 assessments on the same six dimensions, with a supporting passage or concrete issue for each rating:

| Dimension | Observable check |
|---|---|
| Premise and relevance | Within approximately the first 150–200 words, can a new reader identify the user, problem, product and intended outcome? |
| Narrative continuity | Do the headings and section transitions form a connected explanation rather than interchangeable lessons? |
| Explanation and depth | Can the reader follow both phase traces, inspect retrieval and augmentation, identify what each model receives and explain why the major choices matter? Are the source article's insights preserved? |
| Evidence and calibration | Are empirical claims traceable, scoped correctly and separated from interpretation or future work? |
| Readability and voice | Are terms introduced in context, paragraphs coherent and phrasing natural without manufactured drama? |
| Visuals and practical payoff | Do diagrams clarify the relevant steps, and does the reader leave with a useful lesson or action? |

Use a 1–5 editorial scale: 1 = absent or obstructive; 3 = understandable with material gaps; 5 = clear and demonstrated throughout. Scores of 2 and 4 represent intermediate judgments. Target at least 4 on every dimension, with no factual or preservation failures. These are transparent editorial judgments, not validated engagement metrics; a high average cannot excuse a factual failure.

Word counts, paragraph lengths, long sentences and first-use jargon are diagnostic flags. They do not prove comprehension. Real engagement can be assessed later through reader feedback and publication analytics if publishing is separately authorized.

### Hard acceptance gates for this case study

- All prior article editions, figures and saved testing/benchmark records remain unchanged.
- The product is described as the working local application; the deferred AWS design is not presented as deployed production infrastructure.
- Current sparse retrieval and structured classification remain distinct from unimplemented embeddings, reranking, agentic retrieval and Anthropic-style Contextual Retrieval.
- If the 98.0% result appears, it is identified as micro F1 on 20 reused regression cases, with the mixed public/synthetic scope and limitations adjacent. It is not called general accuracy.
- Any cost figure retains its dated inference-ledger scope; no total operating-cost or independently reconciled billing claim is invented.
- No unsupported causal benefit is attributed to RAKE, BM25, prompt changes or the single-case representation comparison.
- No fabricated first-person experience, reader research, customer results or byline appears.
- Both phase traces include understandable inputs and outputs, model-input examples and artifact provenance. Reconstructed, historical and hypothetical material are clearly distinguished.
- Every substantive insight from the current publication article has a recorded v2 destination. Shorter length is not an acceptance criterion.
- Jev appears as researched future work, with task-fit hypotheses and an evaluation proposal, not as an implemented component or a proven optimization.
- Local links, image references and skill references resolve. The skill passes the supplied skill validator and a real drafting/revision pilot; static validation alone is insufficient.

## 7. Phased delivery after approval

| Phase | Work | Completion evidence |
|---|---|---|
| A — Adapt and save the skill | Pin the chosen source, preserve license/provenance, write the compact core and relevant references, validate packaging. Pilot premise revision and a fact-preserving technical explanation. | Saved reusable skill, validator result and observed pilot findings. |
| B — Build publication v2 | Create the editorial brief and faithful data traces, research Jev, write the new narrative, reuse diagrams and add up to two only if needed. | Complete v2 draft with a clear premise, both worked workflows, preserved insights and progressively introduced depth. |
| C — Refine and package | Apply the rubric, revise, audit claims and visuals, prepare platform copy and verify preservation. | Review log, claim checks, publication notes and validated local artifact package. |

Proposed article artifacts:

```text
ai-system-design/publication/v2/
  article.md
  linkedin-post.txt
  publishing-notes.md
  editorial-brief.md
  editorial-review.md
  claim-checks.md
  workflow-examples.md
  decision-model-research.md
  examples/                public/synthetic trace data and model-input artifacts
  verification.json
  figures/                 only if additional illustrations are needed
```

Publishing notes will include a Medium/Substack headline, subtitle, preview/email introduction, LinkedIn treatment, image placements, captions and alt text. The editorial review will include the v1-to-v2 insight coverage map. Workflow examples will carry readable stage explanations plus complete relevant data artifacts; they support the article's inline examples rather than substitute for its explanation. Existing figures can be referenced without duplicating their files. The v2 verification record will include hashes protecting prior artifacts. Any index change will only add navigation to the new edition.

Dependencies are available: the existing articles, public/synthetic evidence records, approved semantics and reusable illustrations. No new GitHub authentication, AWS resources or paid application-model benchmark is needed. Optional illustration generation would use the established image workflow and be recorded separately from application testing.

## 8. Approval requested

Approve phases A–C: save the adapted project-local skill, use it to produce the separate v2 article, workflow examples, Jev research and platform artifacts, and perform the documented refinement and validation. This approval would cover local authoring, safe offline recomputation of deterministic example stages and up to two additional illustrations found necessary. External publication, application changes and paid live model experiments are separate actions.

Until approval, only this research and planning document is being added. The skill, v2 article and additional illustrations remain uncreated.
