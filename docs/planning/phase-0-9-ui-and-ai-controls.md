# Phase 0.9 refinement — UI, repository cohorts and adaptive budgeting

Date: October 13, 2026. Status: **IMPLEMENTED — verification passed; user theme review pending.** The user approved all four stages and recommended defaults on October 13, 2026. All stages are complete; see the [implementation and validation report](../validation/phase-0-9-ui-and-ai-controls.md).

## Objective and recommendation

Make the local application easier to browse and demonstrate: Deep Purple branding, a useful domain/project tree, clear navigation, compact readable metrics, rounded controls and tags, automatic selection of a chosen number of repositories, and an optional budget based on dollars rather than a fixed 20-call window.

Keep the current Next.js/React components and apply shared Material color, typography, shape and spacing tokens. Most visual work is contained in the frontend; cohort selection and adaptive admission require backend changes. The existing OAuth App, FastAPI, local SQLite adapter and review-first taxonomy/classification workflow remain the foundation. Earlier Phase 0/0.5 tests, benchmarks, frozen references, reports, caches and usage history must be preserved.

Design basis: [system design](../system-design.md), [execution guidance](../system-design-execution.md), [historical rationale](../design-conversation.md), [full historical conversation](../design-conversation-full.md), [approved local adapter](../adr/0002-phase09-local-workspace.md) and [current allowance controls](../adr/0003-local-ai-allowance-controls.md).

Approval of this plan authorizes the staged changes below. Planning itself does not change allowance policy, spend money, update settings or start jobs.

## Findings from the existing repository

| Current implementation | Gap and proposed correction |
|---|---|
| `WorkspaceApp.tsx` contains shell, navigation, explorer and organizer UI in one component | Extract shared shell/tree/summary/filter/run-setup components while retaining the established APIs and workflow behavior. |
| Sidebar is 238px wide, with five repository links, branding/workspace controls and bottom actions; the tree shares the remaining height | Move branding/account actions into the header, compress/collapse the collection links and make the tree the main independently scrolling sidebar region. |
| AI Organization is in both sidebar and page actions; sync is repeated in page headings | Use one persistent header location for AI Organization, Content settings and GitHub Sync. |
| Header text is 11px desktop/9px mobile; tags use 10px text and 4px corners | Establish a readable type scale, taller header, pill tags and consistent rounded controls. |
| Four KPI cards use collection coverage, irrespective of active filters | Return scoped summaries for the current view and expose selected repository counts with consistent units. |
| Language is a free-text field; symbols are mixed text glyphs | Use a searchable language selector, visible filter labels, clear/reset controls and a consistent outlined SVG icon set. |
| `RunInput` accepts explicit IDs; an empty list selects all approved inputs; service rejects more than 30 | Add a server-resolved count-based cohort with a reviewable preview. Retain the 30-repository local-run bound for this iteration. |
| Taxonomy combines repository evidence into one generation; classification can generate once per repository | Present separate sample/batch counts and operation-specific cost/call estimates. Repository count is not API-call count. |
| Audited allowance windows manage HTTP/generation counts, while the cumulative $5 limit is fixed | Retain fixed-count mode and add explicitly authorized adaptive run budgets with coherent monetary and call admission. |

The approved architecture and historical discussions distinguish discovery/access from personal relevance, taxonomy drafts from published concepts, and proposed assignments from USER decisions. The redesign must keep these distinctions visible.

## Visual direction

Use the user's [Material palette reference](https://materialui.co/colors), with values checked against the [official MUI color palette](https://mui.com/material-ui/customization/color/). Apply colors through semantic roles rather than giving every component an unrelated accent, following [Material color roles](https://m3.material.io/styles/color/the-color-system).

| Role | Proposed token | Use |
|---|---|---|
| Primary | Deep Purple 500 `#673AB7` | Main actions, active navigation, brand emphasis |
| Primary hover/pressed | Deep Purple 700 `#512DA8` | Stronger interactive states |
| Primary container | Deep Purple 50 `#EDE7F6` | Selected backgrounds and subtle panels |
| Secondary | Indigo 500 `#3F51B5` | Project navigation and secondary emphasis |
| Taxonomy accent | Purple 500 `#9C27B0` | Selected taxonomy chips and smaller accents |
| Information/link accent | Blue 700 `#1976D2` | Links, information and focus treatment |
| Surfaces and text | White/light neutral surfaces; dark neutral text | Legible repository tables, forms and tree labels |

White text on the five proposed solid accent colors has calculated contrast of at least 4.6:1; every actual text/background/state pairing will still be checked. Success, warning and error retain distinct semantic colors and text/icons. The [MUI palette guidance](https://mui.com/material-ui/customization/palette/) calls for checking text contrast rather than relying on automatic palette generation alone.

Recommended typography: body/control text 14–16px, supporting labels 12–14px, page titles 24–28px, KPI values 24–26px. Remove the current 9–11px treatment for important controls/status. Use 12px control corners, 16px cards, 20px dialogs and fully rounded tag/filter pills. Rounding is defined by shared component tokens.

Use bundled, consistent outlined SVG icons for repositories, favorites, recent work, domain/project folders, search, filters, sync, AI, settings and disclosure controls. Keep labels on important actions, accessible names on icon buttons, clear focus states and comfortable touch targets. Avoid a remotely loaded icon font.

## Navigation and layout

Conceptual desktop layout:

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│ Cat · GitHub Manager   Workspace   Domains & Projects ▾   AI   Content   Sync  Me│
├──────────────────────┬─────────────────────────────────────────────────────────┤
│ Collections ▾        │ View title / breadcrumbs                                │
│ Compact repo views   │ In view · Organized · Uncategorized · Review · Selected │
│                      │ Search                 Language ▾   Visibility ▾   Clear│
│ Domains & Projects   │ Active filter chips                                     │
│ ▾ Domain             │                                                         │
│   Project            │ Repository list / content / AI Organization              │
│   Project            │                                                         │
│ ▾ Domain             │                                                         │
│   Project            │                                                         │
│ [independent scroll] │                                                         │
└──────────────────────┴─────────────────────────────────────────────────────────┘
```

- Header: approximately 72px desktop/64px mobile, visible branding/breadcrumbs and a single set of actions. Use **AI Organization**, **Content settings**, and **Sync GitHub** labels; syncing GitHub and asking AI to organize are separate actions.
- Sidebar: approximately 280px desktop, with a compact collapsible Collections group and a flexing tree region. Support long labels, remembered expansion state and collapse/expand controls. Preserve project drag/drop and active-node feedback. Target at least 55% of sidebar content height for the tree at 1280×800 and 65% at 1920×1080.
- Mobile: a usable drawer/tree and responsive header overflow rather than shrinking labels. Support keyboard navigation and restore focus when menus/drawers close.
- Include the optional **Domains & Projects** header menu. It renders existing hierarchy metadata; selecting a domain/project loads its repositories through the existing concept filter. Opening or hovering the menu does not fetch repositories for every node. Use request cancellation/identity checks so a slow response cannot replace a newer selection. Standard loading of the active repository page remains supported.
- Keep all collection views reachable, including Access candidates and its existing relevance/inclusion explanation.

### Main icon

Recommend an **original cat mascot with a brief normal → zen transition** for the application brand. Use SVG/CSS motion, a static reduced-motion version, and a decorative transition on hover/focus; actual job state remains explicit text and progress.

GitHub's [brand guidance](https://brand.github.com/foundations/logo) says its logo should not be modified or used as another project's icon. The recommendation preserves the requested cat/zen idea with original artwork and keeps an unchanged permitted GitHub mark for the integration/sign-in treatment. This asset choice is an explicit approval point.

## Explorer, KPIs and selection

- Use five compact cards, approximately 76–88px high: **In this view**, **Project-organized**, **Uncategorized**, **Awaiting review**, **Selected**. On small screens they wrap without reducing label size.
- Main metrics reflect the active collection, repository view, concept, search, language, visibility and activity window, across all matching pages. Counts use distinct repositories; multiple project memberships do not inflate totals. Awaiting review counts repositories with pending suggestions, with the suggestion total available as supporting detail.
- Selected updates immediately on checkbox/bulk selection. Where useful, other cards show a selected subtotal, such as “12 organized · 3 selected.” Clearly distinguish manually selected repositories from an automatically planned AI cohort.
- Preserve manual selection across pagination and while opening AI Organization. Clear it on collection/view/filter changes with visible feedback, preventing hidden repositories from entering an unexpected run. Provide Select visible and Clear selection with explicit labels.
- Search: readable field with a real search icon, clear button, existing debouncing and a result count. Language: searchable options from the scoped inventory, including Unknown. Visibility: a labeled selector. Show removable active-filter pills and Clear filters.
- Scope summaries and language options must come from the server, rather than being calculated from the first loaded page. Extend the repository response or add a scoped summary endpoint; bind both to the same filter/access rules and signed pagination semantics.
- Render local tags, aliases, memberships and active filters as rounded pills. Keep GitHub-native topics distinguishable from local taxonomy labels.

## Repository counts for AI workflows

Add a **Run setup** panel inside AI Organization with two selection modes: **Manual selection** and **Choose a number automatically**. Default automatic scope is the current view/filter context; broader collection or Access candidates scope must be an explicit choice.

Provide separate remembered fields:

| Operation | Default / local bound | Selection and model behavior |
|---|---|---|
| Discover/rediscover taxonomy | Up to 10 repositories / 1–30 | Deterministic sample balanced across available owners/languages and useful evidence; bounded combined input; normally one generation plus its token count |
| Classify/reorganize | Up to 10 repositories / 1–30 | Deterministic priority for uncategorized/stale candidates, then stable recency/ID ordering; up to one generation plus token count per admitted repository |

Clamp defaults to available eligible repositories. “Full classification” means full reconciliation of the chosen cohort, with its count shown; it must not imply that the entire account was processed. Existing incremental semantics remain disclosed. Larger batches/chunked orchestration are a separate extension rather than silently raising the current local bound.

Before starting, show **requested, eligible, chosen and excluded counts**, the chosen repositories, exclusion reasons, ordering strategy, cache/rules opportunities and an estimated cost range/conservative upper bound. Resolve the cohort on the server across all matching pages; it must not depend on the current table page or database insertion order.

The preview creates a short-lived plan bound to owner, collection, filters, selected IDs, operation, taxonomy/evidence fences and budget policy revision. Start executes that exact reviewed plan once. Access changes, reset, stale taxonomy or policy changes invalidate/revalidate the plan instead of silently substituting another cohort.

Private/unverified content remains excluded from external model input. Local manual assignments and rules retain their current scope. Taxonomy publication and suggestion acceptance still require human review. Saving counts or budget preferences does not launch work. Existing automatic organization can reuse a saved, explicitly enabled cohort/budget policy; its 90-second quiet period and 30-minute cooldown remain enforced.

## Adaptive budget option

Offer **Fixed count limits** and **Adaptive cost budget** independently of inference mode (Live AI, validated cache or Rules only).

Fixed mode retains the existing audited HTTP/generation window controls. Adaptive mode uses an operator-approved **per-run dollar ceiling**, recommended initial default **$0.25**, bounded by the remaining cumulative **$5** ceiling. A requested repository count becomes a maximum; the preview shows how many fit. Manual selections are never quietly reduced: any smaller admitted cohort is shown before Start.

Adaptive execution:

1. Build the exact eligible cohort/evidence plan and identify only provably valid cache/rules results as zero-generation work. Preview itself makes no OpenAI requests.
2. Compute conservative admission from configured models, complete prompt/schema overhead, token/output ceilings, remaining dollars and outstanding reservations. Keep models and quality ceilings explicit; avoid silently switching models or trimming outputs to meet a price target. Recheck pricing before implementation live validation; bind new reservations to a versioned application pricing snapshot and retain the original rates/history for earlier reservations. Display estimates rather than implying that the app reads the provider's billing balance.
3. On explicit operator Start, reserve the run's conservative monetary bound and derive a finite HTTP/generation allowance from that plan. A fresh taxonomy usually needs two HTTP slots; classification needs up to twice its fresh-generation count. Cached/rules work can reduce those needs. The old fixed 20/44 ceilings must not remain hidden additional blockers in adaptive mode.
4. Admit each request atomically, transfer the relevant run hold into its normal per-call reservation without counting money twice, perform the existing mandatory provider token count, and reconcile actual usage. Release only demonstrably unused holds; uncertain calls retain conservative reservations and consumed attempts. Retries remain disabled.
5. Stop or save an honest partial result if access/context/budget/provider conditions prevent continuation. No unbounded retries, automatic dollar increases or renewal loops.

Enabling adaptive policy or authorizing a derived call grant is restricted to configured budget operators, audited and protected by session/Origin/CSRF and stale-revision checks. Original fixed-window audit, lifetime usage, experiment identity, anchors, model cache and historical benchmark records remain intact. Automatic jobs use only an explicitly enabled saved policy; they cannot independently expand it.

Dependency: current app state and the spending ledger are separate SQLite databases. Run-budget holds and request/generation admission belong together in the spending ledger. Link enqueue/start by an idempotent plan ID with explicit recovery for enqueue failure, restart and orphaned holds; do not assume a transaction spans both files. Record the policy change in a new local ADR after approval, without changing frozen pre-testing source.

## Implementation sequence and verification

| Step | Deliverable and likely files | Completion evidence | Complexity |
|---|---|---|---|
| 1. Theme and app shell | Shared tokens, outlined icons, original mascot, header/sidebar/tree; split `frontend/src/components/WorkspaceApp.tsx` into focused components, refine `workspace.css` | Visual review at 1920×1080, 1440×900, 1280×800 and mobile; keyboard/focus/reduced-motion and real color-pair contrast checks; tree space targets | M |
| 2. Explorer refinements | Compact scoped KPI cards, selected count, filters, pills, header tree menu; `frontend/src/lib/workspace.ts`, `backend/app/local.py` and scoped projections | Correct counts across pagination/multiple memberships; filter/selection behavior; header menu network assertions proving no eager repository fetching; drag/drop and existing workflows preserved | M |
| 3. Cohort preview and execution | New application cohort/planning module, `RunInput`/preview models, `Service.queue`, worker plan handling and organizer setup UI | Deterministic sampling, count/context bounds, private/access exclusions, exact one-use plan execution, stale/reset/owner isolation, reload and saved-count behavior | M |
| 4. Adaptive budget and acceptance | New app budget-policy/plan-hold module, `allowance.py`, application provider adapter, operator UI/CLI and ADR; additive ledger migration | Concurrent fixed/adaptive admission, no overspend/double counting, stale grants, orphan/unknown-call/restart recovery, unchanged historical rows, fixed-mode regression, complete functional walkthrough | L |

Implement in dependency order. Step 3 supplies the frozen cohort/cost plan required by Step 4. Review the refreshed layout before expanding the functional controls. New APIs will likely be `POST /api/v1/organizer/preview` and an execution route accepting `plan_id`, with operator budget-policy changes extending the existing allowance route. Confirm exact contracts against existing route/schema conventions during implementation.

Run targeted new backend/browser checks, then existing backend regression, product and original preflight browser suites, lint/typecheck and the production build. Use disposable app/ledger fixtures for destructive and admission tests. If a live canary is necessary, limit it to one approved public/synthetic generation plus token count (at most two HTTP requests) within already authorized funds/allowance; do not renew an allowance just to validate.

Save implementation results and screenshots under the existing validation conventions, including a new Markdown report. Run the preservation verifier before/after and retain the existing video/audio and benchmark artifacts. Update the operator runbook for navigation, count selection and budget modes. A revised video is a separate deliverable if requested.

No cloud deployment or resource changes are involved in this refinement. Rollback keeps old fixed mode available and uses additive plan/ledger records; a UI rollback must not delete usage or uncertainty reservations.

## Approval points

Approve the four-step scope with these recommended defaults:

1. Material palette/rounded treatment on the existing Next.js UI, with a tree-first sidebar and the optional on-demand header tree menu included.
2. Separate automatic taxonomy/classification counts, default up to ten and bounded to thirty per local run, with a visible server-side cohort preview.
3. Adaptive mode as a dollar-based, audited alternative to fixed-count mode: $0.25 default per run, existing cumulative $5 ceiling, finite plan-derived calls and explicit operator authorization.
4. Original normal-to-zen cat artwork for the main icon, with the permitted GitHub integration mark unchanged.

Historical planning boundary: only this document was added before approval. The subsequently approved implementation and additive migrations are now complete; prior pre-testing sources/history and video artifacts passed preservation checks. The real adaptive canary used one generation/two HTTP requests within existing funds and did not renew fixed allowances.


## User feedback revision — October 13, 2026

The user requested implementation of these revisions after reviewing the first theme:

1. Balance Deep Purple with visible Indigo navigation, Blue sync/links, Light Blue informational/progress surfaces and Purple AI accents. Replace the mascot with a clear meditation pose and update run labels/progress styling.
2. Explain exact canonical/alias conflicts, including archived reservations and duplicate draft terms. Add local server checks and user-chosen draft repairs (remove conflicting aliases, suggest a distinct name, reuse an existing active concept, or exclude a row). Repairs never auto-publish, merge live concepts or remove archived reservations.
3. Verify conflict atomicity, ownership/revision/fence checks, human-controlled remediation and the revised theme/status presentation; retain previous readiness/history/video and save a new report/screenshots. No new paid AI checks are needed for these changes.

This is an authorized refinement of the approved local workflow, not a new cloud architecture. Conflict checking/remediation operates on submitted draft values and uses the same validation as publication; it does not call a model or change live taxonomy until explicit publication. Visual sign-off remains pending user feedback on the revised previews.

The feedback revision is implemented and covered by the [new verification report](../validation/phase-0-9-theme-feedback.md). Technical checks passed; revised visual sign-off remains pending user feedback.
