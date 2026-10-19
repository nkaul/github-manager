# Ground Truth Review UX refinement

Date: October 17, 2026. Status: design and implementation plan for approval. This pass produces research and an isolated prototype; it does not install packages or change the running app, corpus, personal workspace or review records.

Later feedback refines the visual specification in the [shared workspace UX plan](workspace-ux-refinement-plan.md) and Ground Truth v3 preview. Preserve this first version as design history. The separately authorized [agent annotation pilot](agent-annotation-pilot-execution.md) adds real comparison data to the current app; the broader visual redesign still awaits approval.

## Recommended direction

Build a focused review workspace with **Material UI Core**, a project-owned theme and a small set of reusable components. Retain the demo's dark ink, readable typography and calm Indigo/Blue surfaces, using Deep Purple for selected actions and Purple/Light Blue as restrained accents. The palette is independent of the library. Next.js provides rendering/routing; the application needs accessible React controls compatible with it.

Material UI supplies the relevant searchable/multiple-selection controls and documented App Router integration. Its exact package versions and adapter must first pass a compatibility spike against the installed **Next 16.4.0 / React 19.3.0**. No peer-dependency bypass, overlapping UI kits or paid grid package is proposed. Scope the theme and styles to Ground Truth; avoid a global reset that alters the personal workspace. See [research and official sources](ground-truth-ux-research.md).

## Problems the redesign must solve

- Seven simultaneous filter columns squeeze search and long options. Legacy global `main` width reserves sidebar space on this sidebar-free screen; several global style layers compete over control and text sizing.
- The review form sits below a 25-repository list, so selecting a case jumps away from the queue. Evidence, candidate labels and editable labels require repeated navigation.
- The current shared `concept` filter silently replaces a Project/Topic/Tag selection when another kind is chosen.
- Add-label needs a picker plus an Add click; removed labels disappear from the editor. Saving has no next-case action.
- Drafts can be overwritten by selecting another case. Detail/source fetches can finish out of order. Revision errors preserve server safety but lack a useful comparison/reapply flow.
- The app has agent proposals and human records today. Independent LLM annotations and their comparison contract are still future work.

## Proposed screen

On a wide desktop: **compact repository queue → review canvas → evidence pane**. The selected case stays beside its queue; review is not appended to the bottom of the collection. Evidence citations open beside the decision and highlight the relevant passage. At intermediate widths, collapse a secondary pane before squeezing text; on mobile use a single-column review with explicit Queue / Review / Evidence navigation and a reachable action bar.

The header carries the workspace name, compact progress and secondary export/account actions. Dataset version, full hashes and raw audit records belong behind a provenance disclosure; source filename, relevant lines and proposal/human status stay visible.

The main toolbar contains a roomy repository search, review status and **Filters**. Secondary facets open in an accessible panel; active chips, counts and Clear filters keep scope apparent. Project, Topic and Tag filters should support independent searchable selections, with **OR within a kind, AND across kinds**. This requires an explicit API enhancement; the current endpoint supports only one concept. Distinguish sampling Domain from assigned Domain, and original proposals from the user's reviewed labels. Do not silently change that basis after saving.

The central canvas contains a concise editable purpose and grouped Projects, Topics and Tags. Definitions and supporting citations sit next to each candidate. Known-label autocomplete stages a selection immediately, with rounded chips, visible not-retained states and Restore. Missing concepts can remain unresolved. Removing a positive does not make every absent label a negative; retain the existing UNKNOWN semantics.

The persistent action bar offers **Save draft**, **Needs evidence**, and **Confirm & next**. Three deliberate review acknowledgements sit near their label groups. Confirmation remains explicit and requires purpose, all reviewed dimensions and valid evidence for newly positive labels. Browsing, model agreement and merely opening a group never mark it reviewed. After a successful save, show the saved revision and select the next case without a return to the list. If saving fails, preserve the current case and edits.

## Visual and component specification

| Area | Proposed rule |
|---|---|
| Typography | 16px body/evidence prose; 14px labels/helpers; clear 20–24px section headings; 28–32px workspace heading; comfortable line height. |
| Inputs/actions | Consistent 44–48px height, roughly 12px radius, visible labels, clear icons and focus states. Desktop repository search gets about 320–360px minimum before wrapping. |
| Layout | 8px spacing scale, roughly 20px surface radii, restrained shadows and pale neutral/Indigo/Blue backgrounds. Do not use pale text to create hierarchy. |
| Search/labels | MUI TextField/InputAdornment, Autocomplete with canonical IDs, Chips and explicit removal names. Label creation is a separate taxonomy action, not arbitrary free text. |
| Panels | MUI Paper/Stack/Box, Tabs, Drawer/Dialog, Tooltip/Popover and clear Buttons; no paid grid is required for 600 paginated records. |
| Feedback | Inline field errors, saved/dirty indicator, focused error summary and Snackbar/Alert for save and refresh outcomes. |
| Evidence | Readable citation snippets first; safe plain-text source view with line numbers, find and quote highlight. Metadata evidence stays distinct from README evidence. |
| Brand/motion | Reuse the existing zen-cat and pause/reduced-motion preference. Keep animation outside the review task hierarchy. |

Measure actual rendered states against WCAG AA: normal text at least 4.5:1, necessary control/state visuals at least 3:1, visible focus, keyboard navigation and reflow. The 44px control target is a usability choice above the AA minimum, not a claim that every WCAG target must be 44px. Prototype measurements do not certify the final component implementation.

## Phased execution after approval

1. **Component and styling foundation.** Pin a compatible MUI Core/Emotion/Next adapter set; verify streaming SSR, hydration, portal focus, CSS precedence and bundle impact. Add corpus-scoped theme/wrappers. Replace inherited layout sizing with an explicit responsive workspace grid. Validate one real search and label selector before expanding.
2. **Current-data review vertical slice.** Refactor the existing CorpusWorkspace into queue, toolbar, editor, evidence viewer and action-bar components. Use existing source/proposal/review endpoints initially. Add safe request cancellation/identity guards, inline validation, dirty-state protection, source-specific retry and visible restored/removed states. Keep the actual agent-only provenance.
3. **Complete the seamless workflow.** Add independent multi-facet filtering and explicit label-basis support; filter-aware next/previous navigation; persistent incomplete drafts; structured revision-conflict recovery. Save before advancing, preserve the filtered queue and handle page boundaries without skipping rows. If persistence succeeds but a later refresh fails, show “Review saved; refresh failed” rather than retrying the save blindly.
4. **Verify and hand over.** Run focused API/concurrency tests, existing corpus and personal-workspace browser regressions, lint/typecheck/build, and screenshot/keyboard/reflow/contrast checks. Confirm frozen corpus hashes and existing reviews remain intact. Present the working slice for feedback before extending the style system to the rest of the app.

The future independent LLM comparison is a separate follow-on to the annotation pilot: add real run/provenance data, then show Agent / LLM / Human differences. A design preview may show a clearly labeled planned state, but the production UI must say Not run until results exist. Agreement is not calibrated confidence and cannot override human decisions.

## API and persistence dependencies

The present review contract already provides owner scoping, CSRF, release/source bindings, expected revision and exact-quote validation. Preserve all of them.

- **Incomplete drafts:** current validation requires evidence for a newly added label even in NEEDS_REVIEW, so a generic Save draft button cannot safely promise persistence of unfinished edits. Add a separate owner/release/repository-scoped draft contract, with draft revision and base-review revision, distinct from final reference_reviews. Permit unfinished purpose/quote in that draft only; do not weaken confirmation validation. Unsaved buffers can remain in memory with navigation protection until explicitly saved. No tokens or raw sources go into browser storage.
- **Facets and counts:** validate repeated canonical IDs, define OR/AND semantics and pagination, and make counts/search basis reflect original proposals versus that user's decisions. Preserve backward compatibility with the single-concept endpoint during migration.
- **Next case:** use a stable filtered sequence/seek anchor or neighbor endpoint so saving a record out of a status filter does not skip the following record at a page boundary.
- **Conflicts:** return the latest review/revision in a structured conflict response. Keep the user's local changes for explicit compare/reapply; do not overwrite a newer revision automatically.
- **Future comparisons/negatives:** independent model proposals and explicit negative decisions need their own validated annotation contract. An unselected label remains unknown under the current contract; do not relabel it as a benchmark negative merely for a cleaner UI.

These are bounded extensions of the approved local adapter, not new cloud infrastructure. Frozen reference files, personal GitHub data, prior benchmarks, articles and recordings remain intact.

## Acceptance criteria

- Search, selected values and long repository/concept names remain readable at 1920×1080, 1440×900, 1280×800 and narrow/mobile layouts; no horizontal page overflow at 200% zoom/reflow.
- A straightforward confirmation needs queue selection, three deliberate group acknowledgements and one Confirm & next action—no decision dropdown or return to the list. This is a design target to measure, not a claimed live usability result.
- Adding a known label is one search/selection action rather than selection plus a separate Add button. New evidence can be attached from an explicitly selected source quote without inventing text.
- A failed save, stale response, concurrent revision or workspace change never discards an unsaved draft or marks the wrong repository confirmed.
- Confirmation advances only after server success; saved records, history, release binding and user isolation survive reload/restart.
- Keyboard-only review, focus restoration, screen-reader announcements, contrast, reduced motion and virtual-keyboard/sticky-bar behavior are checked in the real implementation.
- No automatic human confirmation, fabricated LLM comparison, inferred negative labels or alteration of the immutable corpus.

## Review artifacts

- [Open the local interactive preview](http://127.0.0.1:8131/preview.html) while its localhost preview server is running.
- [Desktop preview at 1920×1080](../design/ground-truth-review-v2/desktop-1920.png) and [1440×900](../design/ground-truth-review-v2/desktop-1440.png).
- [Filters preview](../design/ground-truth-review-v2/filters-desktop.png) and [mobile preview](../design/ground-truth-review-v2/mobile-390.png).
- [Research](ground-truth-ux-research.md)
- [Developer impact and validation notes](ground-truth-ux-implementation-notes.md)
- [Interactive design preview](../design/ground-truth-review-v2/preview.html)

The prototype is a local design artifact using representative public examples. It does not make live API calls or save real annotations. Approval of the screen direction and component choice is the next gate required by AGENTS.md before production implementation.

Prototype smoke checks passed at 1920×1080, 1440×900, 1024×768 and 390×844 without horizontal page overflow. Search, combined Topic/Tag facets, dirty-navigation protection, separate in-memory incomplete drafts, explicit confirmation/next and plain-text source behavior passed with no console errors or HTTP/API requests. See [check results](../design/ground-truth-review-v2/prototype-checks.json). These results apply only to the illustrative prototype; durable storage, concurrency, production accessibility and real app behavior remain implementation acceptance checks.
