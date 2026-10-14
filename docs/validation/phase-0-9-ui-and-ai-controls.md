# Phase 0.9 UI and AI-controls refinement — implementation results

Date: October 13, 2026. Status: **PASS — technical verification complete; local application available. User theme review pending.**

The user approved all four stages of the [refinement plan](../planning/phase-0-9-ui-and-ai-controls.md). This report covers the refreshed local application, deterministic count-based cohorts, exact preview/start execution and adaptive cost admission. Prior readiness/benchmark evidence and the original narrated video remain preserved. Cloud remains deferred.

## Delivered behavior

| Area | Result |
|---|---|
| Color and shape | Deep Purple `#673AB7` primary; Purple, Indigo and Blue semantic accents; rounded controls, badges and tags. Material palette guidance applied to the existing components without adding a component-library dependency. |
| Header | Visible 76px desktop header with original normal-to-zen cat artwork, workspace selection, AI Organization, Content settings, Sync GitHub/samples and account menu. Sidebar/page duplicates removed. |
| Sidebar | Compact, collapsible Collections; independently scrolling domain/project tree; remembered domain collapse state; preserved drag-to-project behavior. Mobile drawer removes hidden navigation from keyboard focus and supports Escape. |
| Header tree | Optional Domains & Projects menu renders hierarchy metadata. Opening/hovering does not request repository lists; selecting a node changes scope and fetches its repositories. |
| Explorer | Five compact cards: In this view, Project-organized, Uncategorized, Awaiting review and Selected. Server-derived distinct counts cover matching pages; selected subtotals follow actual selection. Readable search, language options, visibility/activity filters and removable filter pills. |
| Selection | Preserved while loading more and opening AI Organization; project scope is retained in run setup. Collection/view/filter changes clear selection. Delayed list responses cannot replace a newer request context; Load more also checks the active cursor. |
| AI cohort setup | Separate taxonomy/classification counts, default ten, bounded to thirty. Automatic or manual selection; current view/filter or entire-collection scope; deterministic global sampling/prioritization. |
| Exact reviewed execution | Operation buttons create a five-minute server preview without model calls. Preview shows requested, eligible, chosen, excluded/deferred repositories, ordering, cost bound and finite call grant. Start reviewed run executes that exact plan once. Stale state, owner, expiry, price or budget revision is checked. |
| Adaptive budget | Optional $0.25 maximum per run, within original cumulative $5. Operator-approved finite grants can continue beyond exhausted fixed counts. Atomic holds/reservations, pinned application pricing, per-run history, terminal/orphan/restart recovery and retained unknown-call reservations. Fixed renewal/selected overrides remain available. |
| Defaults and automation | Save defaults starts no work. Counts/budget policy survive reload and can be reused by explicitly enabled automation; existing 90-second quiet period and 30-minute cooldown remain. |

The cat is original SVG artwork, implementing the approved normal-to-zen alternative. It is decorative and has a static reduced-motion expression. GitHub's [logo guidance](https://brand.github.com/foundations/logo) informed that choice.

Color roles use the user's [palette reference](https://materialui.co/colors), the [official MUI palette](https://mui.com/material-ui/customization/color/) and [Material color guidance](https://m3.material.io/styles/color/the-color-system). New application reservations use the October 13 [official pricing snapshot](https://developers.openai.com/api/docs/pricing); mandatory [provider token counting](https://developers.openai.com/api/docs/guides/token-counting) still checks the actual request. Earlier benchmark pricing/source remains frozen.

## Verification

| Check | Actual result |
|---|---|
| Full backend suite | **133 passed**, 9.90s. Includes all earlier tests and twelve refinement tests. |
| Product Playwright suite | **8 passed**, 43.5s. Existing OAuth fixture, sync, draft publication, classification/review, content/rules, private-evidence protection, manual/bulk/drag membership, reset and allowance workflows retained. |
| Original preflight Playwright suite | **4 passed**, 6.9s. Original UI, session boundary, repository/report behavior and mobile setup retained. |
| Static checks | Ruff, ESLint and TypeScript all pass. |
| Production frontend | Next.js production build passes; restarted with `bash scripts/dev-demo.sh --live-ai`. |
| Production smoke | Frontend and Phase 0.9 local health return 200; anonymous identity returns 401; existing OAuth registration configured; rendered 1920×1080 sign-in screen has Deep Purple primary styling and no page errors. |
| Real adaptive canary | **PASS**, one approved public FastAPI classification through real LangChain/OpenAI, one generation/two HTTP requests, no retries or renewal. See [canary report](phase-0-9-adaptive-live-20261013T145429Z.md). |
| Preservation | **PASS**, 163 protected files, original experiment row, 34 historical call rows, 29 historical cache rows and identical preflight UI copy. Eight original demo artifacts match their stored SHA-256 hashes. |

New backend cases cover scoped counts/facets and pagination, private exclusions, deterministic global cohorts, exact/idempotent execution, owner/state/expiry isolation, adaptive fit and stale budget policy, actual provider/LangChain admission with a mock transport beyond old fixed ceilings, atomic monetary accounting, unknown-call reservations, bounded taxonomy packing without source mutation, operator restrictions, concurrent Start, restart/orphan/app-database isolation, pinned price settlement and concurrent fixed/adaptive money admission. Backend cases may exercise multiple related assertions; the count above is pytest test cases.

Browser fixtures use isolated app/ledger databases and clearly labeled fake external providers; they make no paid calls. The real canary uses a synthetic authenticated app session and a public corpus snapshot, not a new live GitHub OAuth observation. Existing real account/access evidence remains in prior reports/video. No production workspace was reset or repopulated for validation.

## Layout, keyboard and contrast evidence

| Screen | Tree share of sidebar with Collections expanded | KPI height | KPI label | Minimum tested text contrast |
|---|---:|---:|---:|---:|
| 1920×1080 | 67.6% | 84px | 13px | 5.97:1 |
| 1440×900 | 60.6% | 84px | 13px | 5.97:1 |
| 1280×800 | 55.1% | 88.6px | 13px | 5.97:1 |
| 390×844 | Navigation drawer | Cards wrap | Readable labels retained | Desktop shared tokens; mobile geometry checked |

All four viewports have no document-level horizontal overflow. The repository table and mobile header actions have their own horizontal scrolling where needed. Assertions cover one global copy of each action, drawer visibility, tree keyboard navigation, header-menu Escape/focus restoration and reduced motion. Thirteen actual computed text/background pairs were checked on each desktop size, including navigation, KPI labels, filters, repository descriptions, visibility, activity and source. This is targeted verification, not a comprehensive accessibility certification.

Screenshots and measured JSON are saved locally under `docs/validation/private/demo/ui-refinement-20261013/`: [1080p explorer](private/demo/ui-refinement-20261013/refinement-1920.png), [1440px](private/demo/ui-refinement-20261013/refinement-1440.png), [1280px](private/demo/ui-refinement-20261013/refinement-1280.png), [mobile](private/demo/ui-refinement-20261013/refinement-390.png), [run setup and preview](private/demo/ui-refinement-20261013/refinement-run-preview.png), and [layout/contrast audit](private/demo/ui-refinement-20261013/refinement-layout-audit.json). That directory also contains browser/build logs, production smoke and preservation evidence. Screenshots use synthetic UI fixtures; zero-spend values in them belong to the isolated fixture ledger.

## Spending and historical continuity

Before the canary: 64 cumulative generation reservations, 60 lifetime application HTTP attempts and $0.103089 estimated cumulative usage. The fixed HTTP window was already exhausted at 20 used.

After the canary: **65 cumulative generation reservations; 62 lifetime application HTTP attempts; $0.103264/$5 estimated cumulative usage; $0 unresolved call reservations; $0 active run holds.** The fixed HTTP-window usage stays 20. Additional canary usage is $0.000175. These are dated snapshots; subsequent user activity can change them.

Adaptive grants are stored alongside the original spending ledger. Fixed-window counters exclude adaptive-scoped attempts, while lifetime history includes both. Money admission includes settled usage, unresolved calls and active run holds across all modes. Run hold → call reservation transfer is counted once. No original window was renewed for this refinement. No prior readiness call/cache row was edited or deleted.

The initial canary preflight guard rejected an ambiguous text-only search before any provider request: both public FastAPI and a synthetic description mentioned FastAPI. The final canary added the Python filter, reviewed the exact public repository and completed with the approved two-HTTP maximum. No provider retry occurred.

## Operational handoff and limits

Open **http://127.0.0.1:3000**, reload, and sign in again after the backend restart. Use the header actions. For fresh AI, open AI Organization → choose count/scope and Live AI → Adaptive cost budget → operation preview → Start reviewed run. Taxonomy publication and suggestion acceptance remain human decisions. The updated [runbook](../development/phase-0-9-demo-runbook.md), [ordered checklist](../development/phase-0-9-acceptance-checklist.md) and [allowance guide](../development/ai-allowance.md) explain the workflow. [ADR 0004](../adr/0004-cohorts-and-adaptive-budgets.md) records the architecture extension.

This remains a single-process local demo with a thirty-repository run bound. Live previews intentionally assume cache misses and can overestimate use. Cached mode requires matching evidence/IDs and never silently spends. GitHub access/activity coverage and unknown branch counts retain their existing disclosed limits. Private/unverified model inputs stay blocked. Estimated application costs do not represent the provider's invoice or credit balance.

The existing video/audio, captions, chapters, player and benchmark/readiness artifacts were preserved. The earlier video shows the previous layout; a revised recording is a separate request. No AWS resource, deployment or GitHub repository was modified.
