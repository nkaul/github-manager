# Public - Ground Truth — quick UX research and screen specification

Date: 2026-10-17. Status: recommendation for review; production implementation and package installation are not authorized. This work leaves the corpus, reviews, APIs and application code unchanged.

This research records alternatives considered. The coordinating [UX plan](ground-truth-review-ux-plan.md) resolves the proposed screen direction: explicit Save draft / Needs evidence / Confirm & next actions, and independent multi-facets with an additive API contract. Those refinements supersede the decision-dropdown and single-facet transitional options discussed below.

## Decision

Use **Material UI Core** as the single proposed component direction for the review workspace, with a small project-owned theme and wrappers. It gives this form-heavy surface styled inputs, searchable selection, chips, dialogs, tabs and feedback together. Keep the approved Deep Purple / Indigo / Blue / Light Blue / Purple palette as independent design tokens: those colors do not require MUI, and Next.js supplies routing/rendering facilities rather than business UI controls. A dependency-free prototype can demonstrate the visual and interaction direction before installation.

Preserve human authority: immutable proposals and pinned evidence inform a separate human decision; saved human decisions never become indistinguishable from agent output. This is the additive local Phase 0.9 corpus workflow, with the existing release-bound, owner-scoped SQLite records. It does not replace the approved cloud architecture. [Workspace contract](public-ground-truth-workspace.md), [architecture](../system-design.md), [execution/approval rules](../system-design-execution.md).

## Evidence from the existing interface

The audit is code-based; these are confirmed structures and likely layout consequences, not a claimed live-browser accessibility certification.

| Observed implementation | Consequence and refinement |
|---|---|
| `corpus.css` uses `2fr repeat(6,minmax(110px,1fr))` for seven fields. All facets appear simultaneously. | Search and long option labels compete for space. Give search the flexible area; keep status plus a Filters trigger visible. Reveal secondary facets below. |
| Global `globals.css` gives every `main` `width:calc(100% - 246px)`; `.corpus-main` resets margin but does not explicitly reset width. | A likely inherited sidebar allowance reduces the sidebar-free corpus workspace. Verify computed width during prototype QA; explicitly scope/reset the corpus layout later. |
| Dossier appears after up to 25 repository articles; `inspect()` scrolls to it. | Each case separates the queue from evidence. Keep the selected case alongside a compact queue and return to the same queue position. |
| Original labels are details elements; retained labels appear again in a separate form. Restore/add requires choosing an option and pressing Add. | Present each proposed concept with its evidence and retained/removed state together; selection from a searchable known-label picker immediately stages an addition. |
| Purpose, label additions, dimensions, notes and decision are followed by one Save button. | Add a persistent decision/action bar and Save & next; keep the three deliberate dimension acknowledgements. |
| `openSource()` lacks request identity/cancellation; a failed source load still has a loading placeholder. `inspect()` clears current edits; close/switch do not check dirty state. | Guard stale responses, show source-specific error/retry, and protect unsaved work. |
| Native controls inherit several global/workspace/theme selectors; evidence uses 12–13px preformatted text. | Unify sizing, readable type and CSS scope. Increasing contrast/type requires explicit tokens and QA, not only a library install. |

Local evidence: [CorpusWorkspace.tsx](../../frontend/src/components/workspace/CorpusWorkspace.tsx), [corpus.css](../../frontend/src/components/workspace/corpus.css), [globals.css](../../frontend/src/app/globals.css), [workspace CSS](../../frontend/src/components/workspace.css), [theme CSS](../../frontend/src/components/workspace-theme.css), [review validation](../../backend/app/demo/corpus.py). The visual reference is sibling `github-manager-demo/assets/site.css` and `index.html`: borrow its dark ink, clear type hierarchy, restrained pale surfaces, rounded cards and calm cat; its marketing hero scale is unsuitable for repeated review.

## Component research and compatibility

| Direction | Fit and tradeoff |
|---|---|
| **MUI Core — recommended** | Ready-styled coverage fits the fastest coherent refinement. Autocomplete supports grouping, multiple selection and keyboard interaction; use canonical IDs and disable free-text creation for labels. Theme tokens centralize typography, shape and palette. Adds MUI, Emotion and Next cache integration, so account for CSS precedence and client JavaScript. [Autocomplete](https://mui.com/material-ui/react-autocomplete/), [theming](https://mui.com/material-ui/customization/theming/), [installation](https://mui.com/material-ui/getting-started/installation/). |
| shadcn/ui | Good control over owned component source and styling, but updates/fixes become project maintenance. Its current Next installation requires Tailwind for an existing custom app; this frontend has neither Tailwind nor a UI kit installed. Current combobox docs use Base UI and support multiselect; do not assume every current shadcn component is Radix-backed. [Next installation](https://ui.shadcn.com/docs/installation/next), [Base combobox](https://ui.shadcn.com/docs/components/base/combobox). |
| Radix Primitives | Accessible behavior and documented SSR support, while the application owns appearance and composition. Attractive for retaining plain CSS, but more assembly work for this review surface. [Accessibility](https://www.radix-ui.com/primitives/docs/overview/accessibility), [SSR](https://www.radix-ui.com/primitives/docs/guides/server-side-rendering). |
| Base UI directly | Unstyled controls work with existing CSS; its own Combobox supports multiple values and chips. Less styling infrastructure than shadcn, more visual-system work than MUI. Official docs state React 17+ and maintained bundler support. [About](https://base-ui.com/react/overview/about), [Combobox](https://base-ui.com/react/components/combobox). |

MUI Core is MIT licensed; the proposed controls need no paid grid package. The cost is dependency integration, theming and regression work, not an asserted license fee. Do not introduce MUI X Pro/Premium or multiple overlapping kits for this slice. [MUI license](https://github.com/mui/material-ui/blob/master/LICENSE).

**Exact-version gate:** the installed stack is Next **16.4.0**, React/React DOM **19.3.0**, with no component library. MUI's current installation docs identify v9.5.0 and list React `^19.0.0` peers, which includes 19.3 semantically. That is not proof of this exact locked combination. Its Next guide uses `@mui/material-nextjs/v15-appRouter` and describes a version-specific `v1X` path; verify the available adapter export and peer ranges for Next 16 before choosing/pinning packages. Do not guess `v16-appRouter` or bypass peer errors. [MUI Next integration](https://mui.com/material-ui/integrations/nextjs/).

Read the **bundled Next 16.4 documentation** first: `05-server-and-client-components.md`, `11-css.md`, App Router `css-in-js.md`, and architecture `accessibility.md` under `frontend/node_modules/next/dist/docs/`. It requires client boundaries for stateful controls and cautions that CSS-in-JS needs explicit Server Component/streaming support. MUI is listed for client use; a generic Emotion setup is not a substitute for MUI's supported cache integration. Keep the server layout and place interactive review state/theme providers in appropriate client boundaries. Avoid a global CSS reset that changes the personal workspace. Next's route announcer does not announce selection changes inside this single screen: provide local focus/status handling.

Later approved compatibility spike: pin the candidate versions; confirm adapter exports and no forced peers; verify SSR/hydration and first paint; check portaled autocomplete/dialog focus, theme/CSS order, existing selectors, route navigation and bundle impact; run typecheck/lint and disposable corpus QA. No such package install or integration test was run for this planning document.

## Visual rules for the prototype and later theme

Use Inter/system sans as in the demo; 16px body and evidence prose, 14px field labels/helper text, 20–24px section headings, 28–32px page heading, line-height 1.5–1.65. Use 8px spacing steps, 12px control radius and 20px surface radius. Inputs/actions share a 44–48px height; source/purpose areas expand vertically. Long repository and concept names wrap; do not make ellipsis the only way to understand a label.

| Token role | Candidate value | Measured contrast on white |
|---|---|---|
| Ink | `#24263c` | 14.81:1 |
| Secondary text | `#535a73` | 6.82:1 |
| Primary action / Indigo | `#3949ab` | 7.73:1 with white text |
| Selected accent / Deep Purple | `#673ab7` | 7.33:1 with white text |
| Links / Blue | `#1565c0` | Verify every actual surface pairing |
| Focus / Light Blue | `#0277bd` | 4.80:1 |
| Control boundary | `#7986cb` | 3.45:1 |
| Background / surface / tint | `#f7f9fd` / `#ffffff` / `#e8eaf6` | Use dark ink; verify all state pairs |
| Purple accent | `#7b1fa2` | Definition/provenance accents; verify actual pairs |

Ratios were calculated from sRGB relative luminance, rounded to two decimals. These candidate pairs do not certify the finished UI. WCAG AA requires 4.5:1 for normal text, 3:1 for qualifying large text, and 3:1 for necessary control/state visuals against adjacent colors. Pale card borders can remain decorative; input boundaries and focus indicators must remain discernible. [Text contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html), [non-text contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html).

Keep the zen-cat in the header, outside the evidence and decision hierarchy; decorative image uses empty alt. Preserve the existing animation preference and static reduced-motion image. Disable decorative animation and smooth scrolling with reduced motion. Provide a discoverable pause control for persistent animation, following the demo's behavior. Use only brief opacity/color transitions for task controls; no pulsing confidence or celebratory confirmation motion.

## Screen and action specification

### 1. Review queue

Header: cat/brand, full workspace name, secondary Export my reviews action, account actions. Main heading: Public - Ground Truth, short statement that these are proposed references. Compact counts distinguish all repositories, records saved by you and human-confirmed records; never label all saved drafts complete.

Toolbar: **Search repositories** flexes from roughly 20rem on desktop; **Review status** roughly 12–14rem; **Filters** shows active count. Allow wrapping before shrinking controls. On small screens search occupies its own full row. Desktop filter popover/expanded region, mobile full-width panel: sampling domain, assigned domain and **one** searchable proposal-label facet grouped by Project/Topic/Tag. Explain that proposal facets remain immutable after human correction; retain this limitation from the current API. Selected filter chips and Clear filters are visible. Do not quietly offer multi-facet AND logic the endpoint cannot perform.

Queue rows show repository, brief proposed purpose, status, sampling domain and a restrained label preview. A separate repository link opens GitHub; a clearly named Review action selects locally. Keep filters, scroll and selected ID stable. Support no results with Clear filters; loading and failure are separate states. Do not display an empty queue while an old request is being replaced.

### 2. Evidence and decision workspace

On wide screens use a compact queue rail plus two primary areas: **Evidence** and **Your decision**. At intermediate widths collapse the rail into a queue button while keeping evidence and decision side by side. On narrow screens stack evidence then decision with jump links; avoid forcing a wide three-column layout or hiding all evidence behind a modal.

Evidence starts with the proposed purpose and grouped Project/Topic/Tag concepts. Each concept shows its definition, original support/dispute state, rationale and exact citation. One click on a citation opens the saved file and highlights the quoted passage/known lines; preserve raw text and visible path, commit and hash. Metadata evidence is identified as metadata and never receives invented README lines. Plain text remains the safe default for untrusted source content. Present eligibility/read coverage in a concise audit summary, with raw records under disclosure.

Your decision shows editable purpose, retained/removed/added concept states, explicit Projects/Topics/Tags reviewed checkboxes, notes and three decision options: Needs review, Unresolved / missing concept, Human confirmed. Removing a concept leaves a visible removed state with Restore. A searchable multiselect stages known-label changes immediately; domains derive from projects and are not directly selectable. Each newly positive concept requires a saved source plus an exact quote. A useful follow-up shortcut is **Use selected quote**, with explicit target concept and user confirmation; do not synthesize evidence.

The sticky action bar shows Unsaved changes / Saving / Saved revision, **Save review**, and primary **Save & next**. Both actions save the explicitly selected decision. Opening evidence or checking a dimension never changes the decision automatically. Saving confirmation requires purpose plus all three acknowledgements; inline validation names the missing requirement and moves focus to the first invalid field. Keep server validation authoritative. The normal confirmed path needs one save action after deliberate inspection, rather than returning to the long list.

### 3. Drafts, errors and sequence integrity

- Track an unsaved session draft against reviewer, release/manifest, repository, source commit and base revision. Clearly distinguish it from a persisted Needs review record. Do not silently autosave human confirmation or add new backend status values.
- On selecting another repository, closing review, changing workspace or signing out while dirty, offer **Stay / Discard / Save & continue**. Save & continue advances only on successful persistence. Native browser-leave protection is a fallback; persistent browser draft storage is a separate follow-up decision.
- Capture the next repository ID from the current filtered queue before saving: status filters may remove the saved case. After success, refresh counts and open that next ID. At page boundaries query the same filter sequence without skipping the shifted row; when exhausted show Queue complete and Back to queue. A failed save stays on the current draft.
- If persistence succeeds but counts/queue refresh fails, report **Review saved; queue refresh failed** and offer retry. Never imply the save failed or require a blind repeated PUT solely because a later GET failed.
- Revision conflict preserves the user's draft and offers comparison with the latest saved review, then explicit reload/reapply. Never retry over a newer revision silently. Release/hash/source-integrity failures block confirmation and require reloading valid evidence.
- Guard detail/source requests by repository+path+request identity or abort signal; late responses must not replace the current case. Source failure has a local Retry control, separate from the editable review. Keep errors near their fields plus a focusable summary; announce save outcomes politely and errors assertively.

### 4. Agent proposals now; independent LLM comparison later

The current endpoint returns original proposals, cross-review/audit information and the user's review. Present these as **Agent proposal / Independent audit / Your decision** using actual provenance only. Legacy `HIGH` text is uncalibrated and must not be styled as a probability or approval signal.

Future comparison can add a concept-by-concept matrix with Agent, independent LLM and Human columns, provenance/evidence per cell, model/run/time/source/taxonomy version and an explicit Not run / Failed / Unavailable state. This needs a new proposal/run contract and independently produced results; it is not implemented today. Agreement is an agreement count, not calibrated confidence. No row, majority vote or comparison action may overwrite a saved human decision. Keep human-reviewed completion and model agreement separate, and preserve unknown versus explicit negative semantics. [Current corpus policy](public-ground-truth-workspace.md).

## Accessibility and acceptance for an approved implementation

Use labels, fieldset/legend groups, genuine buttons and accessible multiselect removal names; retain library keyboard/focus props when customizing. Check Tab/Shift+Tab, arrows, Enter, Escape, focus restoration, screen-reader announcements, 200% zoom and narrow reflow. A practical 44px target exceeds the WCAG AA 24px minimum in most controls; exceptions and spacing still require verification. Sticky header/action bars must not cover focused content. [Target size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html), [focus not obscured](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html). MUI's accessibility report does not certify this application; conduct task-specific checks. [MUI accessibility](https://mui.com/material-ui/getting-started/accessibility/).

Acceptance: no horizontal page overflow or clipped long selections at 1440/1024/768/390px; save/reopen shows the same revision and evidence; Save & next never skips a filter-shifted item; dirty transitions, failures, stale requests and conflicts preserve work; reduced motion uses a still cat; keyboard-only review completes; contrast is measured on all actual states. Run browser persistence checks only against the documented disposable corpus QA identity/database. Before approval, deliver the local prototype and this plan; after approval, execute a compatibility spike, then one corpus-only vertical slice and its regression checks.
