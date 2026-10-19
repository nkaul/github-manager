# Ground Truth v3: refined review workspace

Date: 2026-10-17. Status: isolated design preview for approval. No production frontend/backend, installed packages, real review records, frozen corpus or benchmark artifacts were changed by this work. The v2 preview remains preserved.

Review the [interactive preview](../design/ground-truth-review-v3/preview.html), [1440px screenshot](../design/ground-truth-review-v3/desktop-1440.png), [1920px screenshot](../design/ground-truth-review-v3/desktop-1920.png), [1280px screenshot](../design/ground-truth-review-v3/desktop-1280.png) and [mobile screenshot](../design/ground-truth-review-v3/mobile-390.png). Reference: [refinement research](ground-truth-ux-refinement-research.md), [shared plan](workspace-ux-refinement-plan.md), [main-app preview](../design/main-app-refined/preview.html).

## What changed from v2

The working area now starts at **y=183px**, compared with approximately 304px in v2. A **56px header**, actual workspace title at **24/30px**, compact inline counts and a **360×36px** search replace the oversized introduction and stretched search. Status and Filters controls are **32px** high, centered on the same y=153px line as the search. The queue remains **280px** wide. The desktop decision footer is **64px** high. All three group acknowledgements are visible above it at 1440×900.

The default page uses neutral surfaces and restrained boundaries. Deep Purple identifies primary actions; Indigo identifies selection; Blue identifies links/focus. Panel radius is 10px, ordinary controls 6px, dialogs 12px. Typography follows UI 14/20, label 13/18, metadata 12/16, repository title 20/26, page title 24/30. Purpose and evidence prose use 15px with greater line height. Wide screens add reading space without enlarging controls. Input text is 16px on mobile; touch controls are at least 44px.

An unchanged copy of [shared tokens](../design/workspace-refinement/tokens.css) is bundled locally as `ground-truth-review-v3/tokens.css` so the preview also works when served as an isolated folder. The existing Zen Cat SVG poster is copied unchanged. These files are proposed preview assets, not a production theme installation.

## Task-sized controls and overlays

| Task | Implemented preview composition |
|---|---|
| Routine filters | **380px anchored panel**, vertically stacked sampling domain, multiselect assigned domains and searchable proposal concepts. Changes apply reversibly and immediately; active chips remain visible outside the panel. Footer shows match count, Clear and Done. No large submit CTA. |
| Add/restore known labels | **390px anchored picker**, grouped checkbox options, persistent search, retained count and Done. Definitions appear on checked/focused options. Multiple Projects, Topics and Tags remain selected together. No separate Add action. |
| Leave unsaved edits | **480×163px** content-sized dialog, one consequence sentence, Discard / Stay / Save & continue. Title, body and footer use aligned 20px insets. |
| New-positive evidence | **560px** focused dialog, known-label context, a 220px saved-source selector and full-width quote editor. Invalid exact quotes show a field error; an explicit Attach updates only the memory draft. Body scrolls within bounded height; heading and actions remain reachable. |
| Evidence at 1280px | The queue and editor retain usable width. Evidence opens as a **400px side sheet**, with close/Escape, focus return, scrim and keyboard containment. Desktop width of 1440px and above shows all three panes. |
| Mobile | Queue / Review / Evidence sections, picker sheets, 44px controls and a visible decision bar. Space is reserved below editor content for the fixed bar. |

Opened-state captures: [filters](../design/ground-truth-review-v3/filters-desktop.png), [known labels](../design/ground-truth-review-v3/labels-desktop.png), [leave dialog](../design/ground-truth-review-v3/small-leave-dialog.png), [evidence form](../design/ground-truth-review-v3/evidence-form-560.png).

The fine-pointer label/filter panels focus their search on open and return focus to the trigger on Escape/Done. An outside click closes them without undoing their immediate reversible changes. No modal backdrop is used for routine desktop filtering. Modal dialogs have a restrained neutral scrim, content-driven height and distinct heading/body/footer; there is no heavy backdrop blur.

## Multiple memberships and human authority

Every editable label group remains a collection of IDs. The default NumPy-like public example shows multiple Topics and Tags while retaining one coherent Project. A **separately and visibly synthetic** integration example demonstrates two Projects, two Topics, two Tags and two derived Domains. It has no GitHub link and explicitly states that it is not part of the public release. Open it through the preview footer; [capture](../design/ground-truth-review-v3/multi-membership-example.png). No extra real NumPy Project or cross-domain membership was fabricated to demonstrate the data structure.

Derived Domains are computed from all retained Project parent IDs and displayed as a read-only collection. They are not a single-value manual field. The planned Assigned domain facet is multiselect, with OR within selected Domains. Label filters use OR within a kind and AND across selected kinds. Sampling, status and text combine with those filters. Queue facets remain explicitly based on immutable **Original proposals**; changing a human draft does not silently change that basis.

Save draft, Needs evidence and Confirm & next retain their distinct meanings. Group checks start unchecked, are never completed by opening a source, and a changed group's acknowledgement resets. A newly added positive needs an exact saved-source quote before final save; a separate incomplete draft can remain unfinished. Confirmation is an explicit user action, applies only to the current record, and advances only after simulated save success. Unlisted labels remain unknown. No agent, independent annotation result or model agreement is presented as human confirmation.

The preview shows **current proposals only**. Its Annotation pilot entry explains the separate work; it does not load pilot artifacts, invoke a model or claim that genuine independent runs have not happened. The actual pilot/comparison feature is a separately authorized application slice managed by the coordinating agent.

## Production impact after approval

This visual pass supersedes v2's blanket 44–48px desktop controls and large rounded dialogs. It preserves the functional contracts in [implementation notes](ground-truth-ux-implementation-notes.md): owner/release/repository-scoped separate draft storage, strict final citations, revision fencing/history, structured 409 recovery with retained edits, source/detail request generation guards, write-success versus refresh-failure distinction and stable queue continuation across server pages.

1. Adopt the approved shared tokens and density wrappers across the main app and Ground Truth. Verify exact Next 16.4 / React 19.3 integration before selecting/pinning MUI or another single component implementation. No framework or package change is implied by this static HTML.
2. Refactor `CorpusWorkspace.tsx` into toolbar, queue, review canvas, label picker/group, evidence pane and decision footer. Scope/reset generic inherited layout rules, including the current sidebar allowance on `main`.
3. Add the bounded multi-facet/draft/structured-conflict/next-navigation API changes from the existing plan. `assigned_domain_ids` must accept validated multiple Domain IDs with OR semantics; derive all Domains from supported Project parents. Use collection-shaped positive IDs end to end; no single Project/Topic/Tag assumption in DTOs, display or exports.
4. Integrate the separately approved real annotation comparison without changing human authority or source provenance. Broad aesthetic implementation still requires design approval.
5. Run the existing isolated 3015/8015 disposable-identity/database checks, focused API regressions, visual/keyboard/screen-reader QA, true zoom/virtual-keyboard checks and production integration validation. Keep actual review state and frozen artifacts untouched during QA.

## Verification evidence and limits

[Prototype checks](../design/ground-truth-review-v3/prototype-checks.json) record actual rendered geometry and **23 passed checks**: six viewport/reflow cases, compact control measurements and centerlines, all reviewed groups visible at 1440px, search, combined facets/chips, picker focus return, incomplete draft, invalid/valid exact-quote attachment, dirty-leave preservation, explicit confirmation then next with fresh checks, 1280px evidence sheet, mobile disclosure, multiple collections/derived Domains in the synthetic fixture, assigned-domain multiselect, and read-only guidance. There were **zero page/console errors and zero HTTP/API requests**.

Captures cover 1920×1080, 1440×900, 1280×800 and 390×844. Additional geometry checks cover 1024×768 and 720×450 reflow. The latter is a reflow check, not a full browser-zoom or assistive-technology audit. This prototype does not validate backend persistence/concurrency, actual source integrity, the real corpus taxonomy or actual pilot outputs. Preview saves remain in this tab and disappear on reload; separate draft/multi-facet/seek APIs remain planned capabilities. Exact quote containment is illustrated, and semantic relevance remains a human judgment.

Computed contrast against white for the rendered palette: primary text #202434 **15.40:1**, secondary #626e80 **5.17:1**, Deep Purple #673ab7 **7.33:1**, Indigo #3949ab **7.73:1**, Blue links #1565c0 **5.75:1**, necessary control boundary #8993a5 **3.10:1**, focus #0277bd **4.80:1**. These pair checks do not replace auditing every interactive state, background, native checkbox or assistive-technology flow.

Cross-review correction: desktop main is now a bounded flex column and the queue/review grid takes its actual remaining height (`flex: 1; min-height: 0`), so an applied-chip row reduces pane height instead of moving the decision footer beyond the viewport. With two filter chips and two retained Tags at 1440×900, the full footer ends at **y=866px** and Confirm & next ends at **y=860px**. The refreshed filter capture includes the complete bar. On 390×844, keyboard focus scrolls the full last Tag group above the fixed footer; the group ends at **y=382px** and the footer starts at **y=700px**. [Mobile last-group capture](../design/ground-truth-review-v3/mobile-last-group.png) and measured checks record this. Only the current v3 preview and these notes were changed by this correction.
