# Reusable skills: completeness and quality audit

Date: October 16, 2026. Scope: two new skills, unchanged writing-skill packaging, usage prompts and portable copies. This audit combines source-grounded author review, structural validation and one independent system-design forward test. It is **not a measured usability/engagement study**.

## Results

- The system skill-creator validator passed for the new system-design and illustration entrypoints and the copied writing skill.
- Canonical `.agents/skills/` and portable `skills/` skill folders have matching file inventories and SHA-256 hashes.
- All seven original writing-skill files remain unchanged. Its license and provenance are included.
- Three illustration reference images match their original project files byte-for-byte. No new image or speech generation was needed.
- Active entrypoint/reference/usage links resolve. One inherited historical writing-provenance link assumes its original folder depth; it is documented and mapped in [PROVENANCE.md](PROVENANCE.md), while preserving the requested unchanged skill.
- New skills keep essential instructions in `SKILL.md` and route to conditional references. They do not require another skill, a provider account or original project files to perform their core workflows.
- No paid API calls, global skill installation, app configuration changes, publication or deletion were performed for this packaging task.

Machine-check details and file hashes are in `manifest.json`. An original-source preservation check covers the prior animation baseline and the writing/image sources; its exact results are recorded there rather than inferred from a clean Git status.

## System-design coverage

| Lifecycle area | Where the skill captures it |
| --- | --- |
| Latest instructions, approved design/plan and historical rationale | Requirements/decisions; case study 1 |
| Inspect code, identify gaps/dependencies, plan before approval | Entrypoint; requirements; execution |
| Local-first functional delivery and deferred cloud target | Execution; case study 1–2 |
| OAuth App decision, optional browser auth, access completeness | Architecture/access; case study 1–2 |
| Real named AWS checks, retained scratch resources, Markdown reports | Execution; case study 1 |
| External facts versus user organization versus proposals/receipts | Architecture/ownership; AI state |
| Stable identity, authoritative links, provenance and source versions | Architecture/identity |
| Domain/Project cardinality, independent Topics/Tags | Architecture; case study 2 |
| Canonical aliases, hidden reservations, collision detail/remediation | Architecture; experience |
| Taxonomy discovery versus classification, human review | AI/task boundary |
| README extraction, RAKE, weighted sparse retrieval, BM25/YAKE comparisons | AI/retrieval; case study 3 |
| Chunk coordinates, truncation, augmentation and model input | AI/context; illustration content QA |
| Honest limits on embeddings, reranking, contextual retrieval and Jev | AI/retrieval; case study 3 |
| Completion versus coverage, freshness and review; NO_MATCH | AI/state; case study 4 |
| Durable receipts, no repeated inference, explicit re-analysis | AI/state; execution; case study 4 |
| Automatic change thresholds, eligible types, quiet period/cooldown | Execution; case study 4 |
| Rules/user/rejection precedence and additive drag-and-drop | Architecture/mutations; experience |
| Exact cohorts, concurrency, stale/reset fences, unknown outcomes | Architecture; AI/harness; execution |
| Fixed/selective/adaptive budgets, attempt accounting, pricing/caches | Execution; case study 5 |
| Scoped resets, retained history/cost evidence and earlier benchmarks | Execution; case study 5 |
| Human adjudication, provisional metrics, independent test splits | AI/evaluation; case study 5 |
| Public/synthetic/private policy and repository text as untrusted data | Architecture/access; AI/harness |
| Tree space, top navigation, on-demand fetches, scoped KPIs and facets | Experience; case study 6 |
| Consistent palette/status text, rounded chips, icons and Zen variants | Experience; case study 6 |
| Real-account demos, 1080p fit, natural voice/pacing/section purposes | Experience; case study 6 |
| Academic preservation, illustrated editions and concrete narrative | Experience; illustration/writing composition |
| Demo-only Pages repository, Drive embed-only audio, publication scope | Experience; case study 7 |
| Preserve old artifacts; portable prompts and conditional composition | Entrypoint; execution; bundle instructions |

## Behavioral review scenarios

These are desk-reviewed traces through the instructions, not claimed model executions.

| Realistic request | Expected bounded behavior | Review result |
| --- | --- | --- |
| “Review this app and plan; don't implement” | Inspect code/authority, gaps, material decisions and phases; stop before implementation | Explicitly supported; no automatic build/deploy step |
| “I approved the local demo; build it” | Honor approved scope, use local adapter, keep cloud deferred | Supported; no repeated approval or stack replacement |
| “Why is this analyzed repo unclassified?” | Distinguish receipt, Project coverage, Topics/Tags, freshness/review; do not schedule another call by default | Supported with NO_MATCH and reset exceptions |
| “Add a threshold for automatic reclassification” | Explain change types and policy, distinguish local reconciliation from fresh inference, retain explicit re-analysis | Supported; case defaults are dated examples |
| “Create a diagram for another application” | Inspect style assets; derive facts from new design; do not import GitHub Manager hierarchy | Supported; semantic/status safeguards explicit |
| “Animate this article” | Announce sections/purpose, map prose into visible state, match narration to motion | Supported; no assumed paid voice or fixed universal pace |
| “Make this article readable without losing insight” | Establish premise, preserve insight inventory, use concrete data and evidence | Supported by unchanged writing skill and composed prompt |
| “Publish a podcast page using Drive only” | Preserve embed-only authorization, test page; do not copy raw audio to public repo | Supported; local creation does not imply redistribution |
| “Use this skill for a small label correction” | Load relevant reference and make narrow change | Entrypoints explicitly avoid full redesign/rewrite |

## Refinements and limits

Review corrected a nonexistent provider-source pointer to the actual demo AI/evidence modules, added explicit active-ID/type/source validation, and documented the inherited nonportable provenance citation. The case study distinguishes historical phase values and measured results from reusable guidance; it does not mandate AWS, Next.js, SQLite, a particular model, $5, a voice or a palette in other projects.

After completing its collection/review assignment, one of the existing authorized agents independently used `system-design` on the isolated [Research Shelf fixture](validation/system-design-forward/README.md), with four raw source files and a planning-only request. It was given the skill and task, not an intended answer or root's review conclusions. The [result](validation/system-design-forward/review.md) preserves the local-first choice and this project's own $3/20-attempt constraints, distinguishes implemented facts from historical alternatives, identifies unsafe acceptance/privacy and volatile accounting, and proposes reviewable phases without implementing or calling a provider. It explicitly avoids importing GitHub Manager's Domain/Project hierarchy. It correctly observes that the actual reset code deletes labels but does not itself reset the counter, despite the superseded historical proposal mentioning counter erasure.

The four fixture files and raw agent output are preserved alongside a display copy whose local source links were normalized; factual content is unchanged. No accounts, models, package installs or application mutations were used. The result demonstrates one useful bounded behavior on reduced fixtures, not production readiness or a general success rate. Illustration and writing received the source/structure/desk reviews described above, not separate independent forward tests. Future real use should drive targeted refinements.

Current historical-status facts are dated; the GitHub Manager case study is not a continuously updated architecture audit. Tool and pricing choices require current primary-source verification when used. Portable instructions work without the original repository, but original-source citations and redistribution rights do not become portable automatically.
