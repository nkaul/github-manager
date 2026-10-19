# GitHub Manager: decision provenance and reusable lessons

Snapshot: **October 16, 2026**. This is a synthesis of user directions, approved plans, implementation evidence and dated reports. It is not an exhaustive chat export. Original paths below identify sources in the originating repository; the portable skill remains usable without those files. Consult actual current sources before claiming a later implementation status.

## 1. Product, authority and phased delivery

GitHub Manager helps a user collect accessible repositories and organize/review them through Domains, Projects, Topics and Tags. “Access candidates” are discoverable candidates requiring confirmed access/content, not a claim to possess all public repositories. User-owned organization state is distinct from upstream GitHub facts.

`AGENTS.md` establishes latest explicit user direction → approved design → approved plan → historical conversation. The original request required repository inspection, gap analysis and approval before implementation. Later approvals authorized particular phases and updates; they did not revive superseded options.

The user added Phase 0 for localhost Next.js, OAuth sign-in, repository inventory, minimal FastAPI and actual AWS access tests. They explicitly selected an **OAuth App**, default AWS profile/us-east-1, optional browser sign-in/access confirmation and saved Markdown reports. Private/org completeness needed known fixtures rather than a generic successful login. A tested named scratch stack was retained by explicit instruction.

Phase 0.5 added AI readiness, real OpenAI access/model comparisons, LangChain-compatible experiments, RAKE/YAKE/BM25 comparisons and configurable environment settings. Public samples plus synthetic fixtures and a $5 maximum were approved. Provider credit exhaustion blocked real calls temporarily; offline/Codex work was recorded distinctly. Human reference approval and primary-purpose label adjudication were separate evidence.

Phase 0.9 was approved as a fully functional **local** app with cloud buildout deferred. Local Next.js/FastAPI/SQLite behavior should not be described as deployed DynamoDB/queue infrastructure. Earlier readiness tests and benchmarks remain preserved.

Sources: `docs/system-design.md`, `docs/system-design-execution.md`, `docs/design-conversation{,-full}.md`, `docs/planning/{implementation-plan,phase-0-pretesting,phase-0-5-ai-readiness,phase-0-9-functional-demo}.md`, `docs/validation/{phase-0-results,phase-0-5-results,phase-0-9-results}.md`.

## 2. Data model and access

The approved target separates GitHub facts, content/evidence and Organization data; its AWS logical areas and asynchronous orchestration are a target, not proof of current cloud execution. External facts use stable provider identity and authoritative URLs. User preferences, accepted labels and rejected suggestions retain their own provenance and authority.

Repositories have many Project memberships. Projects have a primary Domain, through which repository Domain membership is derived. Topics and Tags are independent facets. GitHub's native topic strings are external metadata, not automatically approved internal Topic IDs. A term can collide with an alias or protected reservation even when another active canonical name is not visible; errors must identify that source and allow user-selected remediation.

Inventory/content checks distinguish authentication, visibility and completeness across owner, private, collaborator, team and organization relationships. Pagination and access policy matter; a successful public request is insufficient. Content sent to a model must follow the approved public/private policy.

Sources: `docs/system-design.md`, `docs/planning/architecture-review.md`, `docs/planning/phase-0-9-taxonomy-browsing-and-status.md`, `docs/validation/phase-0-9-theme-feedback.md`, current `backend/app/demo/{domain,store,service}.py`.

## 3. AI mechanism and its limits

Collection-level taxonomy discovery and per-repository classification are distinct tasks. Both produce proposals that are validated and reviewed. The implemented context path uses deterministic README cleaning/section extraction, RAKE-derived phrases and weighted lexical concept retrieval; candidate concepts and bounded evidence are supplied for structured model output. Readiness comparisons of BM25/YAKE do not establish that those algorithms replaced the application ranker.

Concrete implementation details explain the tradeoff: section-selected evidence has an 8,000-character README budget, 700-character individual excerpts and 600-character metadata evidence. RAKE proposes up to 20 phrases of one to four words using a project-authored English stopword list. The path named `tfidf` uses binary token sets, smoothed IDF-weighted cosine overlap and an exact-name/alias boost, rather than conventional count-based TF-IDF. Per-type candidate limits are 8 Projects, 10 Topics and 12 Tags. The compact classification payload keeps metadata, up to two README evidence items selected by a purpose-first heuristic and eight phrase strings, plus candidate definitions. These are dated implementation values, not design defaults for another project. They create inspectable extraction, candidate-cutoff and packing failure points; a larger full README or a correct full-source reference does not mean the relevant passage reached generation.

Structured prompts distinguish primary-purpose Topics from incidental capabilities, a dependency technology from a library's own name, and dedicated initiative relationships from a shared language. Domain assignments are derived, not generated. Language/metadata fields are retrieval-time facts; immutable commits pin source files, not those changing API attributes. LangChain integration and deterministic local persistence support the selected provider path without proving an autonomous agent or vector retrieval implementation.

There is no basis here to claim deployed dense embeddings, vector search, learned reranking, Anthropic contextual retrieval or Jev. The user explicitly asked to focus evaluation on the implemented system. These may be investigated later with separate proposals and evidence. A saved receipt is durable processing metadata; it is not conversational RAG memory. Valid citation coordinates are not proof of semantic entailment.

The article work preserved academic and illustrated editions, then created a clearer narrative with source-backed workflow examples. Reconstructed payloads are labeled as reconstructions, not provider wire captures. Corrected figures distinguish excerpts from summaries and cleaned-text coordinates from original-source lines.

Sources: `eval/ai-system-design/{github-manager-ai-system-design,evidence-index}.md`, `eval/ai-system-design/publication/v2/{article,workflow-examples}.md`, `eval/ai-system-design/illustrated/figures/{content-requirements,review}.json`, `backend/app/pretest/ai/`, `backend/app/demo/{ai,evidence}.py`.

## 4. Organization, analysis and concurrency

Analysis completion, label coverage, freshness and human review are independent. “No Project” replaces an ambiguous “Unclassified” when Topics/Tags already exist. A validated NO_MATCH is successful analysis. Per-item receipts survive reload/restart/logout, history deletion and association-only resets; successes in partial runs are retained. Unsupported legacy evidence does not manufacture completion.

Already-analyzed repositories are skipped before fresh provider/count requests by default. Changed taxonomy or missing memberships can lead to local reconciliation; they do not clear receipts. Explicit re-analysis remains possible for taxonomy and classification with reason, exact cohort and bounded cost. Cached AI does not silently fall back to paid inference.

Automatic organization has configurable eligible change types, weighted changes, distinct entities, new-Project threshold, lookback, quiet period and cooldown. Historical defaults: six weighted changes across three entities **OR** two new Projects, 15-minute window, 90-second quiet period, 30-minute cooldown. These settings do not enable automatic paid re-analysis of previously analyzed items.

Drag-and-drop **adds** Project/Topic/Tag membership idempotently; it does not exclusively move repositories. Domain updates follow Project relationships locally. Backend checks access, workspace, active concept and reset state. User decisions and rejection semantics remain protected during rule/model reconciliation. Concurrent starts and stale responses use claims/version/reset fences; unsafe assignments are not applied even when valid historical receipts and costs are retained.

Sources: `docs/planning/phase-0-9-taxonomy-browsing-and-status.md` (completed October 13), `docs/validation/phase-0-9-taxonomy-and-analysis.md`, `backend/app/demo/{analysis,cohorts,service,store}.py`.

## 5. Budgets, resets and evaluation

The user requested selective allowance changes because the original 20/20 display blocked testing. Final controls distinguish request and generation limits: the documented default window is 20 HTTP attempts/10 generations, with finite adaptive grants and the cumulative $5 experiment ceiling preserved. Renewing a window or changing selected limits retains spending, reservations, request rows, generations, caches and reports. Unknown remote outcomes keep conservative holds; hidden SDK retries must not bypass attempt accounting.

Reset has selected scopes, exact impact previews and revision-bound confirmation. Organization reset is separate from allowance renewal. Removing labels/history does not erase durable processing evidence or authorize new spending. Pricing and cache accounting are dated/model-specific rather than universal constants.

The reused 20-case validation round contained 8 public/12 synthetic cases; 50 TP/0 FP/2 FN yields micro-F1 ≈ 0.9804. It supports regression checks, not independent production accuracy. Human “looks ok” was qualitative, not the requested five-dimension numerical rubric. References were approved separately; FastAPI extras were adjudicated in favor of primary labels. Confidence calibration and full entailment metrics were not established by these results.

The new 600-repository public corpus has completed collection, source review and 120 independent cross-reviews at this snapshot. Its references remain proposed, not human-approved gold. Source-backed proposed annotations, cross-review and human approval must remain distinct. Families/lineages need grouped splits; upstream topics used as inputs cannot simultaneously be treated as independent truth without qualification. Controlled synthetic fixtures stay available for edge-case tests.

Sources: `docs/development/ai-allowance.md`, `docs/validation/{phase-0-9-allowance-controls,phase-0-9-reset-replay,phase-0-5-reference-review,phase-0-5-round-2-results}.md`, `docs/planning/public-repository-corpus-600.md`, `eval/ai-system-design/evaluation/corpus-600/{README,validation-2026-10-16}.md`, `backend/app/demo/run_budget.py`.

## 6. Interface, identity and explanation

User feedback drove a balanced Material-inspired purple/indigo/blue/light-blue palette rather than uniform Deep Purple. The concept tree regained sidebar space; sync/AI actions moved to the header; Topics/Tags gained browsing; optional top-nav fetching occurs on click. Compact scoped KPI cards, icons, rounded tags, readable text and clearer search/language/visibility filters support the workflow. Progress and errors follow the same style. Reserved-name errors expose the conflict and offer explicit remediation. A cleaner tail-free Zen-cat icon has configurable variants and reduced-motion behavior.

The user requested a complete walkthrough because the workflow was difficult to follow. They authorized real-account, unmasked demo content. Authentication screens remained outside recording. 1080p viewport fit, chapter assertions and final player checks were necessary; output resolution alone was insufficient. Cedar calmer delivery was selected after voice options. Later diagram-style videos required section announcements and purpose before each concept; a faster pilot led to a slower chapter-based production. Average pace and ASR checks remain technical evidence, not proof every viewer finds narration natural.

The non-block diagram style uses white paper, dark ink, readable handwritten headings, semantic objects and blue/purple accents. User requests preserved academic/block diagrams while adding illustrated and publication editions. Better storytelling retained technical depth and showed concrete retrieval, augmentation and model input instead of only abstract terminology.

Sources: `docs/planning/phase-0-9-ui-and-ai-controls.md`, `docs/validation/{phase-0-9-ui-and-ai-controls,phase-0-9-theme-feedback,phase-0-9-logo-and-kpi-icons,demo-full-v2}.md`, `eval/ai-system-design/animation/full/{production-brief,validation}.md`, `eval/ai-system-design/publication/v2/`.

## 7. Publication boundary

The user chose a **demo-site-and-recordings-only** repository, `nkaul/github-manager-demo`, cloned separately. GitHub Pages publishes the static demo; it does not host the full local application's services. A matching deep-dive page embeds a Drive video and podcast. The user explicitly chose **Drive audio embed only**, declining a raw public repository copy. Header navigation exposes the deep dive with restrained/reduced-motion-aware animation.

Local creation, authenticated demo access and source reuse are separate from public redistribution. Preserve the current authorization for each artifact and avoid re-asking for a publication already explicitly approved.

Sources: `docs/planning/github-pages-demo-site.md`, `docs/validation/{github-pages-demo-publication,github-pages-deep-dive,github-pages-header-cta}.md`.

## Apply the lessons elsewhere

Carry forward authority tracking, ownership boundaries, truthful status, durable receipts, finite external work, phased capability proofs, evidence-proportional evaluation and clear correction workflows. Re-evaluate the stack, palette, providers, thresholds, phase names, voice and hosting for the new product. Those were deliberate GitHub Manager choices, not requirements imposed by this skill.
