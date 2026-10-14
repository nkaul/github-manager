# Phase 0.9 — Taxonomy browsing and classification clarity

Date: October 13, 2026. Status: **COMPLETE — approved A → B → C implemented and validated, including explicit re-analysis and configurable automatic change thresholds.**

## Problem and evidence

The user asked why repositories remain “unclassified” after topic/tag classification, how to browse those labels, and how the four taxonomy types relate. The follow-up explicitly requires a durable record of completed AI analysis so later assignments can happen offline without repeatedly sending the same repositories to the model, plus a clear current/proposed drag-and-drop scope.

The current explorer's **Uncategorized** filter means **no active project association**. Accepted topics/tags do not change that count. This follows [system-design.md §2](../system-design.md), but the label and missing independent classification coverage make successful topic/tag work appear unfinished. The sidebar/header only browse Domains → Projects. Topic/Tag management tabs exist, and an accepted repository chip already filters by any concept ID, but there is no complete Topic/Tag browsing list. The approved design already calls for Topics/Tags navigation.

Read-only snapshot of the saved GitHub collection:

| Measure | Count |
|---|---:|
| Accessible inventory | 310 |
| My Repos | 106 |
| Active Domains / Projects / Topics / Tags | 8 / 3 / 14 / 4 |
| Repositories with any accepted/rule label | 17 |
| Repositories with a project | 3 |
| Repositories with topics/tags but no project | 14 |
| Repositories with no accepted/rule label | 293 |
| Repositories with an accepted Topic / Tag | 14 / 6; overlapping sets |
| Pending suggestions | 0 |
| Repositories with surviving classification outcomes | 65 |
| Latest outcomes across those records | 17 CLASSIFIED, 29 NO_MATCH, 19 FAILED |
| Latest completed Full Classification cohort | 30 processed / 30 chosen, zero failures, taxonomy revision 9 |

My Repos specifically has four labeled repositories and zero project-associated repositories; therefore its current Uncategorized count includes all 106. The 19 saved failures report `ProviderBlocked`; the surviving per-repo outcomes do not establish the precise underlying cause. Do not label them as successful classifications or automatically retry them.

These are dated snapshots, not account-wide completeness claims. Detailed run history can be reset independently of memberships, so missing history does not prove a repository was never analyzed. A completed count-based run covers its reviewed cohort, not the full inventory. Successful analysis can return NO_MATCH, and generated suggestions only become memberships after human acceptance (rules/manual assignments have their own provenance).

## Taxonomy relationship to preserve

| Type | Meaning | Relationship |
|---|---|---|
| Domain | Broad business or technical area | Contains projects; repository membership is derived through its projects |
| Project | An actual product, initiative or coherent solution | One primary Domain; many repositories; a repository can belong to multiple projects across domains |
| Topic | A reusable subject or capability | Independent many-to-many repository labels, crossing project/domain boundaries |
| Tag | Specific technology or descriptive label | Independent many-to-many repository labels, crossing project/domain boundaries |

Example: Domain **Developer Tools** → Project **GitHub Manager** → repository **backend**, with Topics **Repository Organization**, **OAuth** and Tags **Python**, **FastAPI**. Topics and Tags form independent facets; they are not additional levels under Project. A standalone library can be usefully classified by topics/tags while having no project. Do not invent projects solely to reduce the No project count. GitHub-native topics remain separate upstream metadata.

## Durable AI classification guard and offline assignment

### Required behavior

A repository that has completed validated AI classification must be skipped for fresh AI by default, even if it still has no Project, has a valid NO_MATCH result, has pending suggestions, or its associations have been edited. Missing assignments in one or more taxonomy types must not clear the flag. A completed run is not enough: success is recorded per repository, including successful items in a partially failed run.

The current planner's `_classified_current` marker only changes ordering. It is derived from completed run history and taxonomy revision, and does not exclude already processed repositories. Provider caching saves exact matching inputs, but its key includes taxonomy revision/candidate context; taxonomy/review edits can change that key. The new guard must act before provider construction/token counting, independently of run-history availability and provider-cache hits.

### Persistent record

Maintain a compact owner/repository-scoped analysis record separately from optional detailed run history:

- `ai_analyzed`: true after a validated successful model response, including NO_MATCH, or a validated replay with real-model provenance. Manual assignments, rules-only evaluation and failed/blocked requests do not manufacture AI completion.
- Last attempt state/time, operation/idempotency key and any unresolved attempt; last successful result/model/prompt/schema reference and input/evidence fingerprint when known. Keep attempt state separate from successful analysis so failure never causes an automatic retry loop.
- AI input/taxonomy snapshot and freshness; retain historical success when evidence/taxonomy changes rather than clearing the flag. Record local reconciliation separately from the last actual AI analysis.
- Independent accepted Project, Topic and Tag coverage/IDs, review disposition and derived Domain coverage through Projects. Do not require all four kinds to have a match before treating analysis as complete.

Backfill successful receipts from surviving trustworthy per-repo outcomes and validated stored results without model calls. Keep uncertain old provenance/input versions explicit. Missing historical evidence remains “No recorded analysis,” not a fabricated success or a claim that the repository has never been sent. Legacy unknown records need explicit user inclusion for paid analysis; automatic jobs must not guess. New ingestion can record genuinely never-submitted state from the outset.

### Admission, recovery and re-analysis

1. Preview identifies **fresh AI needed**, **already analyzed / skipped**, **offline reconciliation**, **blocked/uncertain** and **excluded** counts, rather than treating all selected repositories as paid work. Default automatic AI cohorts select eligible never-analyzed repositories and do not backfill paid slots with previously analyzed repositories when fewer remain.
2. Apply the same guard in the common worker/provider path, including the legacy reorganization route and automatic scheduler. Manual selection or “Full classification” alone does not bypass it. Full processing reconciles the reviewed cohort; it does not imply fresh inference for each member.
3. Claim a repository's approved analysis attempt atomically before dispatch. Concurrent jobs/duplicate deliveries cannot send it twice. Check the durable record again immediately before the external request. No provider call, token-count HTTP request or cost reservation is made for an already analyzed repository in ordinary processing.
4. Validated successful responses create an analysis receipt even when association application is later rejected as stale. Preserve generation/reset/access fences: that historical receipt must not expose or reapply stale assignments. Unknown remote outcomes stay blocked for operator review and preserve conservative spending reservations; restart does not silently repeat them.
5. Offer a separate, explicitly selected **Re-analyze with AI** option, with a reason and exact reviewed cohort/cost preview. It can refresh analysis after meaningful evidence changes or when the user wants another evaluation. No automatic flag clearing, cache deletion, allowance renewal or retry loop authorizes another paid send. Failed/blocked attempts require an explicit retry choice after their cause is reviewed.
6. Taxonomy revision changes, concept rename/reparent/archive, rule changes, accepting/rejecting suggestions and manual/drag assignments trigger local reconciliation or a “review/update available” state. They do not automatically cause previously analyzed repositories to be sent again. Cosmetic changes are local only. Meaningful evidence changes mark freshness stale and offer opt-in re-analysis.
7. Taxonomy discovery/rediscovery is a separate explicitly reviewed operation. Do not silently resend repository evidence for rediscovery after routine taxonomy edits. Its preview must disclose any previously analyzed inputs and paid work; a classification flag must not be misrepresented as proof that collection-wide taxonomy discovery has run.

Analysis receipts survive reload, restart, logout, detailed history deletion and association-only reset. A full taxonomy reset invalidates old concept references and their eligibility for replay, while retaining historical AI-processing metadata; it does not automatically authorize another paid classification. Evidence-cache deletion removes selected application evidence but does not replenish money or silently clear the no-repeat policy. Any future explicit “forget prior analysis / allow new AI processing” control needs a separate impact preview and user confirmation.

### What remains offline

- Explicit manual assignments, removals, drag-and-drop and Domain derivation are local operations.
- Approved deterministic rules can apply with RULE provenance and no model calls.
- Reuse compatible stored validated AI results with their original provenance/revision and current access/ID checks; do not claim a new AI analysis.
- Use local profiles, canonical aliases and existing TF-IDF retrieval to propose matches for new/changed concepts. Uncertain heuristic matches go to human review as **local suggestions**, rather than becoming accepted AI decisions. Rejections and USER mappings keep precedence.
- If existing evidence cannot resolve a new assignment, leave it unresolved for manual review or explicitly authorized AI re-analysis. Offline matching is not a guarantee that every new Project/Topic/Tag can be inferred accurately.

Automatic organization can reconcile previously analyzed repositories locally and apply approved rules. Its existing quiet period/cooldown and explicit saved budget policy still govern genuinely new AI work. Missing Project membership must never be a reason to pay repeatedly for already analyzed repositories.

## Drag-and-drop: current behavior and proposed scope

| Interaction | Current support | Planned behavior |
|---|---|---|
| Repository row → Project in left sidebar | **Supported on desktop**, through `ProjectTree`'s assignment callback; tested in the product browser suite | Retain; add clear drop-target highlighting and success/error feedback |
| Repository row → Topic or Tag | No dedicated browsing/drop target exists yet | Support in the new sidebar Topics/Tags modes; save an explicit USER association without AI |
| Repository row → Project/Topic/Tag in header taxonomy menu | Header hierarchy currently supports browsing only; its tree has no assignment callback | Add equivalent drop targets when the menu is open, with clearly indicated assignable nodes; opening it still fetches no repository lists |
| Repository row → Domain | Unsupported; Domains derive from Project membership | Domain hover can expand its children; dropping offers a project picker for that Domain. No direct repo–Domain edge or automatic project creation |
| Multiple selected repositories → concept | Current drag payload contains only the dragged row, regardless of checkbox selection | Dragging a selected row includes the explicit selected set; dragging an unselected row includes that row only. Show the count and confirm the exact multi-repo target/set before saving |
| Project → Domain | No drag reparenting; change its Domain in Content settings | Continue using the existing editor; drag reparenting is outside this iteration |
| Keyboard/touch assignment | Existing row details **Add membership** and bulk **Add membership** are available for Project/Topic/Tag | Preserve as full alternatives; do not depend on native HTML drag behavior on phones |

All drops **add** membership. They do not remove other Projects/Topics/Tags or exclusively move a repository. Project assignment updates derived Domain membership locally. Removal remains an explicit separate action and preserves rejection semantics. Already-present membership is an idempotent no-op. A drop neither resets `ai_analyzed` nor schedules paid inference. The backend revalidates access, workspace ownership, current active concept and reset state; rejected drops make no partial change.

Tests must cover single-row and selected-set behavior, cross-page selections, duplicate drops, invalid/stale/archive targets, preserving multiple memberships and USER provenance, Domain project selection, header/sidebar parity and keyboard/touch alternatives. Browser drag tests use disposable fixtures and make no model calls.

## Recommended user experience

### Clear coverage and status

- Rename visible **Uncategorized** to **No project** (supporting text: “No active project membership”). Keep the existing legacy API view name compatible if useful.
- Keep five compact cards: **In this view**, **Labeled**, **No project**, **Needs review**, **Selected**. Labeled counts distinct accessible repositories with any accepted/rule Project, Topic or Tag membership. Proposed suggestions alone do not count. Detailed coverage exposes Project/Topic/Tag and No labels counts without adding another large row of KPI cards.
- Separate three independent dimensions: **analysis outcome**, **label coverage**, and **review state**. Add taxonomy/evidence freshness to analysis rather than turning stale repositories into unlabeled repositories.
- Analysis outcomes: No recorded analysis; Queued/Running; Match found; No match; Failed/Blocked; Excluded by input/access policy; Stale. Record method/provenance so “Rules checked” is not presented as successful LLM analysis. If a repository already has accepted labels, a new NO_MATCH can mean no additional match, rather than no organization at all.
- Show the exact cohort in completion messages, for example “30 repositories analyzed: …; remaining inventory not included in this run.” Failed/blocked requests and privacy exclusions remain explicit. Do not infer all-account success from a completed job.

### Browse all four types without shrinking the tree

Use a segmented browser above the existing tree: **Projects | Topics | Tags**. Projects remains the default and keeps **Domains → Projects**. Topics and Tags display searchable flat lists with aliases, distinct accepted-repository counts and separate pending-review badges. Only one browser occupies the scrolling sidebar region at a time.

Extend the header menu to **Browse taxonomy** with the same three modes. Opening/changing modes uses hierarchy/facet metadata only; repository lists are fetched after selecting a concept. Preserve the existing on-demand rule and response identity checks. Reuse the existing `/repos?concept=<id>` path for all concept types. Sidebar/header counts must use server-projected accessible collection/view scope across pages, rather than the loaded table page, and show zero-member active concepts as well.

Selecting a Topic or Tag opens its repository list with an explicit context heading and existing manual/bulk actions. Add **View repositories** and counts to Content settings concept cards, while preserving their editing role. Local Topics and GitHub-native topics have distinct labels if both are displayed.

### Review assignments easily

Add Project/Topic/Tag, concept and repository filters to the AI review queue. Offer grouping by repository or concept, showing existing accepted memberships beside proposed additions and their reasons/evidence. Distinguish accepted-member counts from pending-suggestion counts.

Support explicitly selected bulk acceptance/rejection with a reviewable summary and per-item stale/access validation. Retain individual controls and manual precedence/rejection protection. Never automatically accept or merge model proposals. Add clear repository views for **No labels**, **No project**, **Needs review**, **No match**, **Failed/Blocked** and stale analysis; the last three depend on reliable durable outcome state.

## Implementation phases

| Phase | Deliverable and dependencies | Likely touchpoints | Acceptance evidence |
|---|---|---|---|
| A — Correct meaning and coverage | Rename No project; add any-label coverage and durable per-repo AI receipts/attempt state, independent from detailed history and memberships. Enforce default no-repeat admission in preview, worker, legacy routes and scheduler; reconcile existing results locally. Backfill only supported evidence; absence remains “No recorded analysis.” | `backend/app/demo/{store,service,explorer,domain}.py`; `backend/app/local.py`; `frontend/src/lib/workspace.ts`; `ExplorerTools.tsx`, `WorkspaceApp.tsx` | Topic/tag-only repositories count as Labeled and No project. Repeating classification on analyzed repositories makes zero model/count HTTP calls, including NO_MATCH and successes from partial runs. Revision/manual/drag/history/reset changes cannot silently bypass the guard; concurrent/uncertain attempts are not repeated. Offline work preserves USER/rejection precedence. No model calls for backfill. |
| B — Taxonomy browsing | Three-mode sidebar/header browser, scoped counts, searchable Topics/Tags, concept-card navigation and explicit single/multi-repository drop targets. Uses A's shared projections and the existing concept filter. | `workspace/Shell.tsx`, shared taxonomy-browser component, `WorkspaceApp.tsx`, theme CSS; scoped concept-facet response | Each type opens correct distinct repositories; counts agree across pages; no eager per-concept fetches. Drop targets add Project/Topic/Tag memberships with zero AI requests, preserve existing memberships and derive Domains locally. Zero-member concepts, archived/access isolation, keyboard/mobile alternatives and tree space targets pass. |
| C — Review and targeted follow-up | Type/concept/repository review filters and grouped, explicitly selected actions; analysis-state views, local matching suggestions and separate opt-in retry/re-analysis with a reviewed cost preview. | Organizer review UI; suggestion routes/service; `cohorts.py`, status projections | Selected suggestions are accepted/rejected safely; stale/conflicting items are reported; USER decisions/tombstones remain protected. Only explicitly authorized retry/re-analysis bypasses the no-repeat guard. Model requests and their cause are auditable; local matching is distinguished from AI. Valid NO_MATCH, lack of a Project and taxonomy changes do not trigger automatic paid repetition. |

A and B provide the first useful user-visible slice. C builds on reliable status and concept counts. Each phase stays within the approved local Next.js/FastAPI/SQLite adapter; cloud infrastructure remains deferred. Durable status belongs to Organization data, consistent with the approved design. Implement additive fields/migrations and retain compatible API behavior rather than resetting stored user data.

## Constraints and validation

- Preserve original canonical IDs, aliases, archived reservations, memberships, rules, user decisions, benchmark/readiness sources/reports, spending ledger and video/audio artifacts.
- No new model comparison, automatic taxonomy publication, private-model input permission, allowance renewal or paid reclassification is implied by this plan. Existing thirty-repository local cohorts and fixed/adaptive budgets remain.
- Use existing cached inventory/evidence. No GitHub resync is necessary for navigation or coverage changes. Analyze NO_MATCH evidence and taxonomy suitability before spending on retries; investigate ProviderBlocked details rather than guessing their cause.
- Verify meaningful backend cases and full product/preflight browser regression, lint/types/build, responsive/focus/contrast checks and preservation checks. Save a new Markdown validation report and review previews. Default fixtures make no paid calls; a new live check is only needed if an unresolved inference-path concern justifies it.
- Rollback can restore presentation while leaving additive status/history records intact. History/association reset preserves compact AI receipts. Taxonomy/evidence resets invalidate affected references/freshness and disclose their impact while preserving historical processing metadata and the no-repeat guard. Missing old evidence must not be manufactured.

## Approval and execution clarification

Approved by the user on October 13, 2026. Execute A → B → C without another approval gate. Explicit re-analysis remains available for both taxonomy discovery/rediscovery and repository classification, with a reason, reviewed cohort and bounded cost. Re-analysis uses fresh inference only in Live AI mode; Cached AI does not fall back to paid calls.

Automatic organization will expose configurable weighted-change, distinct-concept and new-project thresholds, eligible change types, lookback window, quiet period and cooldown. The trigger explanation will show whether the threshold is met. Defaults preserve the existing six weighted changes across three entities OR two new projects, 15-minute window, 90-second quiet period and 30-minute cooldown. Cosmetic edits are excluded. Evidence changes can mark analysis stale. A trigger never clears a receipt: analyzed repositories reconcile offline; new eligible repositories can use the saved budget policy. Failed, unknown and legacy-unrecorded cases require explicit inclusion/re-analysis. Automatic paid re-analysis is not enabled by these settings.

## Implementation completion

A, B and C are complete. Durable admission/receipts, offline reconciliation, explicit fresh taxonomy/classification re-analysis, configurable automatic trigger settings, independent coverage/status, three-mode browsing/assignment and grouped bulk review are implemented. Validation: 157 backend tests, 12 product browser checks, four original preflight checks, Ruff, frontend lint/types and production build/smoke pass. No paid calls were needed. See [the validation/preservation report](../validation/phase-0-9-taxonomy-and-analysis.md), [ADR 0005](../adr/0005-durable-analysis-and-local-reconciliation.md) and [current runbook](../development/phase-0-9-demo-runbook.md).
