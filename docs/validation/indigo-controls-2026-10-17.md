# Indigo styling and searchable-control refinement

Date: October 17, 2026. Status: complete; live local app rebuilt, restarted and health-checked.

## Request and scope

The user authorized replacing Deep Purple with Indigo, using the demo site's Deep Dive and Watch Demo buttons as the reference, then asked UX and development agents to fix searchability, inconsistent controls and professional appearance across the app. This bounded update applies to the live application. It does not install MUI or claim the earlier structural prototypes are implemented.

## Visual contract

| Role | Value / behavior |
|---|---|
| Primary action | Indigo `#3949ab`, white text; hover `#303f9f`, pressed `#283593` |
| Secondary action | Indigo text `#303f9f`, soft `#e8eaf6` → `#e3f2fd`, border `#c5cae9` |
| Reading text | Neutral ink `#24263c`, secondary `#535a73` |
| Fields | 40px desktop, 44px small-screen controls; border `#8993a5`, radius 10px |
| Action shape | Rounded/pill; restrained primary shadow, no continuous marketing animation |
| Type | 14px values, 13px labels, 12px metadata; 16px mobile field text |
| Focus | Visible Blue `#0277bd` outline |
| Semantic states | Preserve descriptive warning/error/success states; color accompanies text |

The reference is the existing local `github-manager-demo/assets/site.css`. The interface keeps its existing Zen Cat options and KPI icons. Active previews also use Indigo; prior v2 and academic/report artifacts are preserved.

## Interaction and workflow constraints

Searchable selectors filter known options and commit only a selected option. Typing alone must not change the application value. Disabled choices, required fields, long labels, controlled async values, keyboard selection, dismissal and modal focus remain usable. Ground Truth retains its dirty guard, source provenance, staged-label behavior and explicit human confirmation gates. Multi-label assignment remains supported through the existing add/retain workflow.

## Verification

- **17 application browser workflows passed** across the full run and focused corrective reruns. The four new tests cover search/commit separation, Escape and Tab cancellation, required committed-value validation, modal Escape behavior, disabled choices and long-option touch selection. Existing workflows cover allowance management, taxonomy publication/repair, classification, multiple manual/drag assignments, freshness controls, persistence, private-content boundaries and workspace selection.
- **Two Ground Truth workflows passed** across the full run and one corrected assertion rerun: frozen-corpus browsing/source review/save/export/workspace isolation, and independent-agent comparison/staging without an implicit save or human confirmation.
- **Final live layout test passed** at 1920×1080, 1440×900, 1280×800 and 390×844. Measured desktop search, Language, Visibility and workspace fields are all 40px; combobox padding reserves 34px for indicators. Sidebar search has one surrounding `#8993a5` border and a borderless inner input. Document overflow, taxonomy rail, readable KPI labels and reduced-motion branding checks pass.
- Sampled text contrast across 13 existing UI roles was at least **5.97:1** in the desktop audit. Primary white/Indigo is approximately **7.73:1**; the shared necessary field boundary against white is **3.10:1**. These focused checks are not full accessibility certification or a screen-reader audit.
- **ESLint, standalone TypeScript and production build passed**; the final production build was repeated after the last sidebar-border adjustment.
- Existing structural previews passed **18 main-app + 23 Ground Truth checks** and were refreshed to Indigo. They remain illustrative previews, separate from actual app screenshots and browser API evidence.

The first run exposed an ambiguous popup accessible name and test-login IDs absent from the disposable server. Those were corrected. Old assertions expecting stored option IDs now inspect the displayed labels; a selection-only scenario now explicitly creates its prerequisite taxonomy rather than relying on earlier tests. Screenshot review caught residual native-control wrapper padding and nested search borders; stronger narrowly scoped field styles fixed them. No production API contract was changed.

Actual captures and measurements: [live app, 1440px](../design/workspace-refinement/live-indigo/app-1440.png), [mobile](../design/workspace-refinement/live-indigo/app-mobile.png), [Ground Truth review](../design/workspace-refinement/live-indigo/ground-truth-review-1920.png), [layout audit](../design/workspace-refinement/live-indigo/layout-audit.json). The UX specialist independently inspected desktop/mobile images and the measured controls; its [audit](../planning/professional-controls-ux-audit-2026-10-17.md) records research, findings and resolutions.

## Preservation

A read-only baseline records hashes for 548 corpus/pilot/readiness/demo artifacts and logical contents of the application and budget SQLite databases in the ignored `.tools/indigo-controls-preservation-before.json`. No provider API calls, corpus edits, annotation generation or benchmark spending are part of this task. **Final comparison: all 548 artifact hashes match and both SQLite databases have identical logical table contents.** Test writes were restricted to disposable test databases. No provider API calls or additional benchmark spending occurred.


## Production readiness

Final production build passed. The app was restarted using its existing `scripts/dev-demo.sh --live-ai` mode, and HTTP 200 was confirmed for `http://127.0.0.1:3000`, backend `/health` on port 8000 and the design review hub on port 8132. Preservation hashes and logical database contents were checked again after restart and still match. The in-memory OAuth session may require a new sign-in; saved work remains intact.
