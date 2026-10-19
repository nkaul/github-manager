# Live workspace redesign verification

October 17, 2026. Status: complete; final browser/static checks and local production health passed.

## Scope and authority

The user explicitly requested three coordinated agents and authorized implementing the refined layouts in both live workspaces. The earlier Indigo/control pass standardized controls but left the structural previews unimplemented. This pass implements the compact main repository list and the adjacent Ground Truth queue/review/evidence workflow, rather than publishing another standalone mockup.

The [shared design contract](../planning/live-workspace-redesign-2026-10-17.md) supersedes earlier layout approval holds. Existing prototypes, corpus releases, annotation knowledge, benchmark/readiness reports, articles, diagrams and recordings remain preserved. No dependency installation, cloud deployment, GitHub write or external model call is required.

## Coordinated ownership

- UX design researcher: professional design guidance, shared proportions and interaction contract, independent source/screenshot audit.
- Main-app UX developer: shared compact theme, shell/navigation, summary strip, repository list and selection states, dialogs, main browser regressions.
- Ground Truth UX developer: actual three-pane layout, search/filter flow, grouped label review, evidence/provenance, saved drafts, explicit confirmation and continuation, review browser regressions.
- Coordinating agent: bounded local API extensions, concurrency/persistence tests, preservation checks, integrated browser validation, production build/restart.

## Design acceptance

Desktop targets: 56px header, 32px ordinary actions, 36px fields, a roughly 52px KPI strip with meaningful counts instead of repeated explanatory copy. Neutral reading surfaces, consistent small radii and all actual active/selected states in Material Indigo `#3949ab` with white text/icons. Mobile/coarse-pointer controls retain usable touch targets. The first repository row should be visible near 330–360px at 1440×900 in ordinary browsing, while actionable access/budget errors remain visible.

Ground Truth targets: queue, editable grouped review and source evidence adjacent on wide screens; responsive evidence disclosure/mobile tabs; reachable decision actions. One uncomplicated confirmation should require the three deliberate dimension acknowledgements and a final Confirm & next action. Added canonical labels stage on selection; missing supporting evidence remains explicit. Save draft persists incomplete work separately from final human decisions.

## Local API support

See the [workflow API contract](../planning/corpus-review-workflow-api.md). Incomplete drafts are owner/release/repository scoped, revision-fenced, independent of review counts/export and bound to source/annotation context. Final review validation remains strict and consumes only the draft revision the client observed. Combined taxonomy facets and an immutable-key neighbor endpoint support review continuation without dropping a row after status changes.

**All 121 backend demo tests passed**, including twelve new focused draft/facet/continuation tests. They cover incomplete authority boundaries, persistence/isolation/CSRF, concurrent edits, source/quote integrity, canonical/release binding, facets/basis and page-boundary continuation. Ruff checks passed for the changed backend files.

## Final verification

- **17 main-app browser workflows passed** in the full run: OAuth fixture/session, sync, taxonomy editing/repair/publication, classification and no-repeat/re-analysis controls, manual/bulk/drag assignments, rules, allowance management, protected private details, persistence, logo preferences, selected colors and responsive layouts.
- **Five Ground Truth browser workflows passed** across the full functional run and focused corrective rerun: independent annotation staging with no implicit save; save-first confirmation plus navigation-only retry; incomplete draft restoration and exact-quote correction; stale-write preservation/explicit reapply; and desktop/mobile geometry, source-sheet focus and provenance access. No assertion was removed to hide a layout failure.
- Final measured desktop header **56px**, ordinary action **32px**, fields **36px**, KPI strip **52px**. The first main repository row is within **360px** at the checked desktop sizes. The Ground Truth working region starts at **183px**, with a **280px** queue; decision actions remain within the viewport at 1920, 1440, 1280 and 390px layouts.
- Main text contrast across twelve sampled UI roles is at least **5.76:1**. White-on-Indigo selection is approximately **7.73:1**. These checks and independent visual inspection do not represent a full screen-reader/accessibility certification.
- ESLint, standalone TypeScript and the final production build pass. Desktop/mobile images are actual running-app captures against isolated test backends, not the earlier HTML mockups.

Actual captures: [main 1440px](../design/workspace-refinement/live-redesign/app-1440.png), [main mobile](../design/workspace-refinement/live-redesign/app-mobile.png), [Ground Truth 1440px](../design/workspace-refinement/live-redesign/ground-truth-1440.png), [Ground Truth mobile](../design/workspace-refinement/live-redesign/ground-truth-390.png), [1280px evidence sheet](../design/workspace-refinement/live-redesign/evidence-sheet-1280.png). Measurements: [main](../design/workspace-refinement/live-redesign/app-layout-audit.json), [Ground Truth](../design/workspace-refinement/live-redesign/ground-truth-layout-audit.json).

Browser QA caught and corrected nested Escape dismissal, a redundant current-row detail fetch that could reset an open evidence editor, focused controls obscured at a smaller viewport, evidence-sheet return-focus timing while the background was inert, and a legacy 740px table minimum that clipped mobile descriptions despite no document-level overflow. Test-only fixes also removed a nonexistent corpus fixture name, scoped an alert assertion away from Next's announcer, and cleaned up proxy routes after tests. All final functional and layout cases pass.

The visual design intentionally adapts the AI Organization preview to its existing functional task page instead of shipping the illustrative 640px Run/Automation/History overlay. Its controls, layout density and typography are refined; all real budget, receipt, automation and history behavior stays available. That specific mock overlay is not claimed as delivered.

## Preservation

Fresh read-only hashes of 548 protected corpus/pilot/readiness/demo artifacts and logical table contents of the application and budget SQLite databases are recorded in ignored `.tools/live-redesign-preservation-before.json`. **All 548 protected artifact hashes match, and both SQLite databases have identical logical table contents after testing and the production restart.** All automated review writes use disposable test databases. Earlier previews, benchmark reports, corpus/annotation artifacts, saved human decisions and the provider allowance ledger remain intact.


## Using the review workflow

1. Open the app, sign in and choose **Public - Ground Truth** from the workspace selector. The first queue record opens beside its evidence; selecting another row does not require scrolling to a separate dossier.
2. Review the purpose, retained Projects/Topics/Tags and relevant evidence. Selecting a known label adds it immediately; a new positive still needs its exact saved-source quote. The Original proposed labels disclosure preserves the independent original purpose and labels.
3. Use **Save draft** for incomplete work, **Needs evidence** for an explicit unresolved decision, or acknowledge the three groups and choose **Confirm & next**. Only a successful final save advances. Ctrl/Command+Enter is an optional confirmation shortcut after the same requirements are met.
4. A saved draft restores separately from final decisions. Conflict comparison keeps local edits; reapplying requires reviewing all groups again. A failed successor fetch offers **Next repository** without another PUT.

## Local production health

The final production build passed, and the application was restarted using the existing `scripts/dev-demo.sh --live-ai` launch mode. Read-only checks returned HTTP 200 for the frontend at `http://127.0.0.1:3000`, backend health at `http://127.0.0.1:8000/health`, and the actual-screen design gallery at `http://127.0.0.1:8132/workspace-refinement/`. No external model requests were made during this verification. An in-memory OAuth session can require signing in again after restart; saved work remains intact.
