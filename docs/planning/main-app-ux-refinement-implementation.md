# Main application UX refinement — implementation proposal

Date: 2026-10-17. Status: isolated design preview; production implementation requires approval.

The [functional preview](../design/main-app-refined/preview.html) refines the existing workspace rather than changing its architecture. It uses the unchanged [Zen Cat rays poster](../../frontend/public/branding/v2/zen-loop-rays-poster.svg), public repository names and explicitly illustrative metadata, favorites, memberships and proposals. Search, filters, selections and dialogs run in memory. No account, GitHub, API, storage, database, scheduler or model calls occur.

Read with [main-app research](main-app-ux-refinement-research.md), [shared refinement plan](workspace-ux-refinement-plan.md), [shared tokens](../design/workspace-refinement/tokens.css), [system design](../system-design.md) and [execution rules](../system-design-execution.md). The reviewed code includes `WorkspaceApp.tsx`, `workspace/Shell.tsx`, `ExplorerTools.tsx`, `AutomationSettings.tsx`, `Icons.tsx`, branding config, both layered workspace stylesheets, historical design conversation and the sibling `github-manager-demo` static showcase. The bundled Next 16.4 CSS, client-boundary and `use client` guides inform the future application integration. This preview adds no runtime dependencies.

## Concrete design changes

| Area | Proposed behavior and proportion | Production impact after approval |
|---|---|---|
| Header | 56px, one row; Zen Cat and collection context left, task navigation right. Mobile retains brand and navigation trigger. | Recompose `Shell.tsx`; keep existing collection and identity boundaries. Move secondary actions into task-specific surfaces. |
| Taxonomy rail | 280px desktop, roomy 34–36px rows, visible domain/project hierarchy, Topics and Tags separate. Mobile drawer makes hidden content inert and traps focus. | Preserve `TaxonomyBrowser` semantics and stable concept IDs. Reconcile existing rail/header browse duplication; do not infer new taxonomy hierarchy. Optional resizing is a later usability enhancement, absent from this preview. |
| Summary | One neutral strip; a consistent subtle 16px icon per label; modest numbers; review count is actionable; selection has a separate contextual action bar. | Rework `ExplorerSummary`, preserving actual scope and selected-summary counts. Never mix totals across views. |
| Toolbar | 360×36px preferred search (400px cap), 32px desktop buttons and language selector, anchored 360px additional-filter panel. | Rework `ExplorerFilters`; preserve query/filter request behavior and visible labels. Existing search already has a base width cap: the improvement is consistent height, alignment and surrounding chrome. |
| Repository explorer | 14px names; 12px metadata; readable 92px rows; quiet project/tag chips; local details use a chevron. Table and card layouts are preview alternatives. | Preserve trusted GitHub links separately from local details, server pagination, selection across pages and many-to-many memberships. A card toggle is a proposed addition and requires approval; do not change API data to support invented activity. |
| AI setup | 640px, single-column form; 108px numeric fields; 270px inference selector; compact scope summary; run setup/automation/history tabs. | Extract a focused dialog over existing `RunSetup`/`AutomationSettings`. Keep run start explicit and await the authoritative response. Reuse actual budget receipts and job status; no optimistic completion or fabricated history. |
| Taxonomy review | 800px complex review dialog; 238px proposal navigation and one selected editor/conflict detail. Header and action footer remain visible; body scrolls. | Extract `DraftReview`; retain server check/remediation, selected proposals, revision guard, undo and canonical reservations. Longer editing sessions may merit a full task page after validation. |
| Palette and density | Neutral surfaces dominate; Deep Purple primary actions, Indigo navigation/selection, Blue focus/links. 14/20 body, 13/18 labels, 12/16 metadata, 24/30 page title. 6px controls, 10px panels, 12px dialogs. 44px touch tier; 16px mobile input text. | Adopt one shared theme with Ground Truth. Audit contrast and the existing CSS specificity collisions before replacing styles. |

The normal desktop preview puts the first repository row at **359px** at 1920×1080, 1440×900 and 1280×800. It preserves one concise illustrative notice. This improves on the previously reviewed layout where stacked chrome pushed the first row to roughly 640px; that earlier measurement is visual review evidence, not a performance benchmark.

## Implementation sequence after approval

1. **Theme and component compatibility spike (S).** Validate any MUI Core adoption against exact installed Next 16.4.0 / React 19.3.0 and an approved library version, App Router integration, CSS ordering and existing layered styles. MUI is a candidate, not an installed or proven dependency. Record bundle/focus/SSR effects. Either use it deliberately or retain small native components; do not mix two competing size systems.
2. **Workspace shell and explorer (M).** Introduce shared tokens; adjust header, rail, title, notice and summary; then toolbar and repository rows. Keep the current API/contracts, semantic views, GitHub-owned fields and pagination unchanged. Verify the same repository identities/counts before and after, with no hidden warnings.
3. **Scoped overlays (M).** Replace generic modal sizing with 400–480px confirmation, 560–640px form/detail/setup and 800px complex taxonomy review. Scope body overflow and pinned footer, restore focus, support Escape, identify server errors by field, preserve dirty edits and prevent stale responses from replacing a newly selected record.
4. **AI organization and taxonomy review (M).** Adapt existing components without weakening budget, privacy, revision, manual-precedence or conflict checks. Use actual run history or truthful unavailable/empty states. Keep reset/rediscovery safety and typed destructive confirmation independent of the visual restyle.
5. **Regression and review gate (M).** Run lint/typecheck and approved disposable UI fixtures. Test desktop/mobile/200% zoom; keyboard and coarse-pointer interaction; long names; loading, empty and error states; selected scope across filters/pages; conflict repair/undo; cancelled/failed AI start; footer reachability; and no changes to connected user records during QA. Present screenshots and behavior evidence before merging.

Style changes risk leaking through the current `workspace.css`/`workspace-theme.css` cascade. Prefer one explicit component layer or CSS Modules, rather than appending more high-specificity overrides. The prototype intentionally does not model backend concurrency, durable drafts, real sync coverage, live inference, reset, or correct classification. Its manual assignment updates one example row's displayed project; production must preserve the full many-to-many relationship model.

## Preview verification

Reproduce from the repository root:

```bash
.tools/node/bin/node docs/design/main-app-refined/check-preview.cjs
```

The checker uses the existing local Playwright installation and browser. Browser launch may need the environment's sandbox approval; no package installation or account access is needed. The artifact also opens directly as local HTML. It imports the shared sibling token stylesheet, so keep `docs/design/workspace-refinement/tokens.css` alongside it.

18 browser smoke checks passed: initial rendering; viewport overflow and proportions; keyboard search; combined language/topic filtering; filter dismissal/focus return; selection and scoped actions; local assignment display; list/card toggles; bounded AI setup; tabs and explicit simulation; no invented history; dialog focus restoration; alias conflict publication gate and explicit repair; truthful Latest Work unconnected state; empty search recovery; mobile drawer/inert behavior; mobile footer reachability; narrow reflow; zero page/console errors and zero HTTP/API/model requests. The last narrow-reflow check is not a full browser-zoom audit; production must still test actual 200% zoom and assistive technology.

Evidence: [check results](../design/main-app-refined/prototype-checks.json), [1920 desktop](../design/main-app-refined/desktop-1920.png), [1440 desktop](../design/main-app-refined/desktop-1440.png), [1280 desktop](../design/main-app-refined/desktop-1280.png), [390 mobile](../design/main-app-refined/mobile-390.png), [AI setup desktop](../design/main-app-refined/ai-setup-desktop.png), [AI setup mobile](../design/main-app-refined/ai-setup-mobile.png), [taxonomy conflict review](../design/main-app-refined/taxonomy-review-desktop.png), [search](../design/main-app-refined/search-desktop.png), [filters](../design/main-app-refined/filters-desktop.png), [selection](../design/main-app-refined/selection-desktop.png) and [cards](../design/main-app-refined/cards-desktop.png).

No application, dependency, API, database or sibling-demo files were edited by this task. Existing previews are preserved. Approve the shared visual system and the shell/explorer slice before production implementation.
