# Live workspace redesign: shared contract and acceptance

Date: October 17, 2026. Status: **live structural implementation and independent UX acceptance complete; final production build/restart checks owned by the coordinating agent**.

The user has explicitly authorized the full structural UX improvement and requested three specialists. This authorizes applying the refined main-app and Ground Truth designs to the running application. It supersedes the earlier broad-layout approval hold in the preview implementation notes. The earlier Indigo/control pass was a bounded palette and selector improvement; it did not deliver the proposed structural redesign. This pass must close that gap rather than present another recolored version of the old screens.

The coordinating agent owns integration, bounded backend changes, verification, build and restart. The main-app developer owns its shell/explorer/settings surfaces; the Ground Truth developer owns the review workspace. The UX researcher owns this shared contract and an independent review of actual rendered application screens. No additional agents, provider/model calls, package installation or cloud work are needed.

## Evidence and design premise

Compare the actual [previous live 1440px screen](../design/workspace-refinement/live-indigo/app-1440.png) with the [refined main-app preview](../design/main-app-refined/desktop-1440.png), and the [previous live Ground Truth review](../design/workspace-refinement/live-indigo/ground-truth-review-1920.png) with [Ground Truth v3](../design/ground-truth-review-v3/desktop-1440.png). The main gap is composition: stacked notices, individual KPI cards, oversized chrome and several filter rows push repository work down the page. Ground Truth still requires navigating a long page between repository list, review, annotation comparison and sources. Changing Indigo or making selectors searchable does not resolve those costs.

Use the preview's hierarchy and working-area allocation, while replacing illustrative behavior with real API/state handling. The new active-state color instruction is stronger than the previews: every actual selected/active state uses **white text/icons on Material Indigo `#3949ab`**. Preserve the Zen Cat and its existing configuration. Do not modify or delete historical preview images, readiness evidence, corpus releases, articles, recordings or benchmarks.

This is a local presentation/workflow refactor over the approved architecture. GitHub authentication remains OAuth App based; tokens stay server-side. Stable taxonomy IDs, many-to-many memberships, manual precedence and evidence ownership remain authoritative. Bounded owner-scoped draft and queue-navigation APIs may support the now-authorized review workflow; they do not introduce another service or provider.

## Research translated into decisions

These sources inform the implementation; they do not imply adding their packages or copying their complete visual identities.

- [Primer TextInput](https://primer.style/product/components/text-input/) explicitly supports size choices appropriate to context, labels, captions and validation. Apply one deliberate compact desktop tier and one comfortable touch tier instead of independent per-page sizing.
- [Primer PageLayout](https://primer.style/product/components/page-layout/) provides a useful header/content/pane/footer composition model. Our three-pane evidence task should allocate stable areas to queue, decision and source rather than stack every region into one long document.
- [Carbon data-table guidelines](https://www.carbondesignsystem.com/building-blocks/core/components/data-table/guidelines) distinguish density tiers and the table's toolbar, headings, rows and pagination. Our repository rows contain several lines, so they should be compact and consistently aligned, not forced into a single-line 24px table.
- [Vercel's interface guidelines](https://vercel.com/design/guidelines) emphasize keyboard operation, focus management, unobscured controls, useful hit areas and readable mobile input text. Preserve zoom; do not adopt any suggestion that disables it. Human confirmation and AI execution remain explicit and await authoritative success.
- [W3C tabs](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/), [combobox](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/) and [modal-dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) guidance informs keyboard/focus behavior. Appropriate semantics depend on whether the control switches a panel, chooses a value or opens an action. Keep ordinary text editing and return focus when an overlay closes.
- [W3C reflow guidance](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) informs narrow-screen/zoom acceptance. A wide data region may scroll deliberately; the entire application should not require horizontal scrolling to reach basic controls and decisions.

The exact dimensions below are project choices validated against the previews and real screens, not universal requirements attributed to those sources.

## Shared visual and interaction contract

| Element | Desktop target | Responsive rule |
|---|---|---|
| Application header | **56px**, one compact row | Deliberately simplify/reflow navigation; avoid the old 176px mobile header. |
| Primary/secondary routine action | **32px** | At least 44px on narrow/coarse-pointer surfaces. |
| Search, text, numeric and searchable select | **36px** | At least 44px touch tier; 16px mobile input text. |
| Repository search | Preferred **360px**, cap about 400px | Fill its local column on mobile, never force viewport overflow. |
| Typography | Body/control **14/20**, label **13/18**, metadata **12/16** | Purpose/evidence prose may be 15–16px with more line height. |
| Page heading | **24/30** | One task title and concise context, no marketing introduction. |
| Numeric input | About **96–120px** | Width reflects the value; do not stretch a small number across a pane. |
| Summary | One approximately **52px** neutral strip | Wrap meaningfully; avoid five tall cards and repeated helper sentences. |
| Main rail / GT queue | About **280px** | Collapse before it crowds the working task. |
| Spacing | 4px base; 8/12/16/24px roles | Align label/value/action baselines and local insets. |
| Radii | Fields about 6px, panels 10px, dialogs 12px; rounded action buttons/tags | Consistent roles matter more than decorating every container. |
| Dialogs | 400–480px confirmation, 560–640px ordinary form/setup, about 800px complex review | Bounded body scroll; heading/footer reachable. |

Neutral surfaces dominate. Main text remains dark neutral; Indigo identifies decisions and active state. Semantic red, amber and green retain their meanings with accompanying text/icons. Necessary field outlines use a contrast-capable border, not only a pale decorative stroke. Focus remains visibly distinct from a selected state.

### Selected/active state is a complete treatment

Use `#3949ab` background and white text/icons/secondary text for the current navigation item, active taxonomy node/mode, active task/mobile tab, selected repository/queue row, chosen or keyboard-active popup option and active filter/picker choice. Explicitly reset child link/helper/icon colors so older rules do not leave dark text on Indigo. White on this Indigo is approximately **7.73:1**.

Hover-only neutral states may be pale. Ordinary membership chips and derived Domain labels are data rather than an active navigation choice and can remain neutral. Closed search-select fields remain normal readable fields; their selected popup option receives the active treatment. Disabled and destructive states must not become misleadingly active.

Retain the shared searchable selector's commit/query separation. Arbitrary typed text must not become a concept ID, workspace, inference mode or human decision. Enter commits an enabled option; Escape dismisses a popup before its enclosing modal; Tab discards uncommitted query text. Required selection, no-result states, disabled choices, long labels, viewport-constrained popup placement and focus return remain covered. Dropdowns must stay searchable after the structural move.

## Main application: implement the preview's composition

1. **Header and rail.** Place brand/collection context in the compact header and expose task navigation once. Keep sync and AI access discoverable in the relevant header/task surface without duplicating large buttons. Give the taxonomy rail sustained room for Domains/Projects and easy Topics/Tags access. Preserve lazy fetching for header taxonomy browsing and actual collection boundaries.
2. **Heading and routine feedback.** Show a short task heading. Consolidate repeated routine information; keep material access, sync, privacy, allowance and failure conditions actionable. Hitting a height target is not a reason to hide an important warning.
3. **Summary and selection.** Replace KPI cards with one quiet summary strip: scoped total, with-project/labeled coverage as honestly defined, no project, needs review and selected count. Keep actual selected subtotals available without boilerplate repeated under each number. A contextual selection bar exposes manual membership and selected-repository organization actions.
4. **Toolbar and list.** Align search, language and a compact Filters entry; disclose secondary filters in a bounded anchored panel with active filter chips outside. Preserve all existing view/visibility/activity/concept filters. Show a crisp table/list with 14px repository names, short 12px metadata, quiet many-to-many labels, explicit review/analysis status, trusted external GitHub link and distinct local detail action. Target first repository row **at or above y=360px at 1440×900** for a normal populated case with routine notice content.
5. **AI setup.** Use a focused 640px dialog/task surface with compact scope, counts, budget and reanalysis controls; group automation/history rather than stack every setting by default. Keep actual approved allowance caps, run previews/receipts, cache reuse, private-content policy and explicit execution.
6. **Taxonomy review.** Use bounded complex-review space: proposal navigation, one editor/conflict detail, visible heading and reachable actions. Preserve exact conflict owner/alias, explicit remediation, undo, saved draft and server revision/publication gate. No silent repair or inferred publishing approval.

Do not invent repository activity, merge GitHub-native topics with local labels, remove pagination or reinterpret a repo lacking a Project as never classified. Table/card alternatives are secondary to the working list; finish the real workflows before polishing extra layouts.

## Ground Truth: make evidence review the default workspace

At desktop widths of about 1440px and above, show **queue → review → evidence** together. Use a roughly 280px queue, a useful central review width and a readable source pane. Aim for the working region to begin **by y=200px** in the ordinary case. Fit the workspace to remaining viewport height, including active-filter chips; independent pane scrolling and a pinned decision footer must not require calculating a brittle fixed page height.

At approximately 1280px, keep queue/review usable and expose evidence as a bounded side sheet. At narrow widths, offer explicit Queue / Review / Evidence sections and keep the current decision reachable. The evidence overlay returns focus and has working Escape/close behavior. Reserve enough scroll space that a fixed action footer never hides the final label group or focused input.

### Reduce review steps while retaining authority

- Selecting a queue item opens its real review in place; maintain current position and visible status. Avoid a separate list-to-dossier page jump.
- Place repository purpose immediately below the repository header. Preserve the immutable proposal separately from the editable human purpose.
- Group retained labels under Projects, Topics and Tags, with one deliberate acknowledgement for each dimension. Domains derive from all retained Project parents and are read-only. Multiple relevant labels remain supported in every group.
- Put Evidence/quote access beside each label. Selecting it should open the relevant pinned source/quote in the evidence pane without navigating away from the editable review. Show path, source hash and line context/provenance truthfully; distinguish saved metadata from repository documents. Untrusted content remains plain text.
- Use a searchable grouped Add/restore picker with immediate reversible draft selection; eliminate a separate redundant Add button. A new positive still needs valid supporting saved-source evidence. Removing/restoring a label resets the relevant group acknowledgement.
- Keep optional notes, detailed provenance and independent annotation comparison available through progressive disclosure or a dedicated task tab. Their depth must remain accessible without dominating every normal review.
- Keep Save draft, Needs evidence and Confirm & next in a persistent action area, with a truthful saved/dirty state and group progress. Do not auto-check dimensions, auto-confirm agreement or treat a model confidence band as human approval.

### Persistence and navigation contracts

**Save draft** persists incomplete work separately from authoritative final reviews, scoped to owner, release and repository and bound to base review/source versions. It does not require all final evidence/checks, change immutable proposals, count as human confirmation or create a gold label. Draft restore clearly identifies stale/conflicting base state.

**Needs evidence** must not bypass exact-quote validation for new positives. Persist a valid unresolved review when supported by final validation, or preserve incomplete work as a draft and explain the remaining evidence. Never report a successful human confirmation.

**Confirm & next** requires the existing purpose/dimension/evidence/revision gates. Await the authoritative final write, then advance to the next repository in stable current filtered queue order, including server-page boundaries. Confirmation failure leaves the current form and selection intact. A successful write followed by summary refresh failure remains a successful save with a separate refresh warning.

Preserve dirty-leave protection for repository, workspace, filters and task navigation. A structured revision conflict retains user edits and offers explicit recovery; a slow old detail/source response cannot replace the newly selected repository/source. Do not silently drop a draft when filter changes or a confirmed row leaves the current queue.

## Delivery sequence and proof

1. Implement the shared compact shell, state tokens and density rules in real components. Inspect the CSS cascade rather than accumulating contradictory page-specific overrides.
2. Deliver the main explorer and focused settings/review surfaces while the Ground Truth developer composes queue/review/evidence. The coordinator supplies bounded draft/next API support as needed.
3. Integrate both screens with the same active-state/density rules; verify feature parity and explicit human authority.
4. Run appropriate backend and disposable browser workflows, lint/typecheck/build, then restart and health-check the local app. No real provider call is required to validate this UX work.
5. Independently inspect **actual app screenshots**, compare them with both preview references and the geometry goals, and record any remaining gap. A passing prototype or palette-only screenshot cannot satisfy this gate.

### Acceptance matrix

| Area | Required evidence |
|---|---|
| Main composition | Actual populated screens at 1920×1080, 1440×900, 1280×800 and 390×844; compact header/summary, first-row location and rail space measured. |
| Ground Truth composition | Actual three-pane desktop, 1280px evidence sheet and mobile review with final label group and action footer visible/reachable. |
| Controls and active state | Computed 36px fields/32px desktop actions/44px touch; white-on-Indigo selected text/icons; dropdown search and all original options preserved. |
| Layout robustness | Long repository/concept/path names, empty/loading/error, active chips, zoom/narrow reflow, focus not hidden behind sticky regions, no unintended whole-page horizontal overflow. |
| Main behavior | Workspace/filter/selection/pagination, many-to-many manual assignment, AI preview/start safety, taxonomy conflict repair/undo/draft/publication, relevant settings/reset behavior. |
| Ground Truth behavior | Queue→source→label correction, multiple labels and derived Domains, added-positive exact quote, separate incomplete draft save/restore, valid unresolved review, explicit confirm then next, dirty-leave/cancel, revision conflict, stale fetch protection, persistence/export/isolation. |
| Accessibility | Keyboard-operable task/queue/filter/label/evidence/action flows, visible focus, correct dialog/tab/combobox semantics, readable sampled contrast; record scope honestly rather than claim blanket certification. |
| Preservation | Frozen corpus/release bindings, real human reviews, model budgets, credentials, prior tests/benchmarks/reports and existing articles/diagrams untouched except intentionally versioned owner-scoped review/draft writes during normal use. QA uses disposable identities/databases. |

## Review status

Research, baseline/preview comparison, shared contract, source review and independent actual-screen acceptance are complete. Recommendations were sent to both developers and the coordinating agent before implementation. The main and Ground Truth structures are implemented in actual application components. Refreshed desktop/mobile, final-label and open-evidence-sheet captures were independently inspected after integration. No unresolved visual or interaction blocker remains within this audit's reviewed scope. The coordinating agent reports **22 distinct browser workflows passing**: seventeen main workflows, four Ground Truth functional workflows and the expanded responsive layout/keyboard workflow. Final lint/type/build, preservation and localhost restart outcomes belong in the [verification report](../validation/live-workspace-redesign-2026-10-17.md), rather than being inferred from screenshot acceptance.

### Integration corrections and verification

The initial backend source review found the separate draft authority model intact: incomplete buffers do not affect final-review counts or exports, owner/CSRF boundaries remain enforced, draft and base-review revisions are fenced, source/proposal/commit/annotation bindings remain checked, and final confirmation still validates exact quotes and dimension acknowledgements. The coordinating agent reports twelve new draft/facet/neighbor tests passing. The neighbor endpoint seeks from an immutable repository identity even when confirmation removes that item from the filtered queue; the frontend must use it and distinguish successful save from a later navigation failure.

The source audit has also raised concrete integration corrections before browser acceptance: active tab counters must not leave white text on an old pale badge; selected-row icon hover and active taxonomy drop surfaces must retain contrast; obsolete base `!important` rules must not reintroduce indented descriptions, 12px check labels or 11px taxonomy editor inputs. The shared searchable selector retains committed-ID validation and portals within the nearest modal's boundary. Ground Truth's custom evidence-sheet focus trap must include provenance summaries and isolate its background, ordinary quote validation must not be misreported as a concurrent saved-record conflict, and metadata-only citations must not silently leave an unrelated README presented as the newly opened supporting source.

Those source-level corrections are now present. Ground Truth also uses the tested neighbor endpoint after the final write, with a no-write navigation retry, and scopes its own 56px flex header to avoid inheriting the main app's two-row mobile header. Actual main-app screenshots at the four target viewports visibly match the intended composition: a compact heading, one summary strip and a single toolbar put the first row at approximately 351px. Independent visual review identified a remaining faint Source coverage section and legacy nowrap/minimum-width rules clipping mobile cards. These were corrected and the final rendered capture now shows wrapped descriptions inside the 390px viewport. Main mobile deliberately retains two 56px header rows to keep collection selection and touch actions available, reducing the previous 176px header to 112px.

The live AI Organization surface remains a task page over the real settings/run workflow rather than the preview's illustrative 640px tabbed setup dialog. Describe this as an intentional task-page adaptation, not delivery of that exact prototype overlay. The bounded taxonomy proposal editor and modal body are implemented separately.

### Independent actual-screen findings

The latest actual Ground Truth captures at 1920×1080, 1440×900, 1280×800 and 390×844 were reviewed independently after the developer's integration changes. The measured desktop header is **56px**, the review workspace begins at **y=183px**, and its queue is **280px** wide. At 1440px the three panes have usable queue/review/source widths of 280/728/360px; the decision footer occupies y=823–887px. At 1280px the source becomes a sheet and the review receives 940px; its footer occupies y=723–787px. In the focused-label captures, the last Tags acknowledgement is visible above the footer at both 1280px and mobile. These are rendered app measurements, not prototype dimensions.

| Actual application evidence | Captures |
|---|---|
| Main repository workspace | [1920px](../design/workspace-refinement/live-redesign/app-1920.png), [1440px](../design/workspace-refinement/live-redesign/app-1440.png), [1280px](../design/workspace-refinement/live-redesign/app-1280.png), [mobile](../design/workspace-refinement/live-redesign/app-mobile.png) |
| Ground Truth queue/review/evidence | [1920px](../design/workspace-refinement/live-redesign/ground-truth-1920.png), [1440px](../design/workspace-refinement/live-redesign/ground-truth-1440.png), [1280px](../design/workspace-refinement/live-redesign/ground-truth-1280.png), [1280px evidence sheet](../design/workspace-refinement/live-redesign/evidence-sheet-1280.png), [mobile final group](../design/workspace-refinement/live-redesign/ground-truth-390.png) |
| Measured rendered geometry | [Main controls and sampled contrast](../design/workspace-refinement/live-redesign/app-layout-audit.json), [Ground Truth pane/footer bounds](../design/workspace-refinement/live-redesign/ground-truth-layout-audit.json) |

The redundant immutable-purpose paragraph was removed from the normal editor header and retained under Original proposed labels. The editable purpose, derived Domains, three grouped label reviews and optional detail disclosures now form one continuous review surface. The selected queue row and mobile Review tab use white text on Indigo. Focus is Blue. The earlier legacy green field focus was removed from the shared theme. No visual blocker was found in the reviewed queue/review/footer captures.

Source inspection confirms that keyboard focus visibility is adjusted only inside the review scroller, using the real scroller/footer bounds after animation-frame layout. It does not move the whole page or depend on one fixed footer height. Mobile tabs now use one active tab stop and Left/Right/Home/End navigation. Escape handlers respect already-handled popup events. The evidence sheet's background is inert and its focus trap includes source/provenance disclosures. The actual 1280px sheet capture was independently reviewed with the provenance disclosure open and visibly focused; the source text and provenance remain inside the bounded sheet. Expanded browser checks exposed a close-focus race while the opener's background was still inert. The shared close handler now returns focus after the commit using an animation frame, with connected/not-reopened guards. The coordinating agent reports the expanded layout workflow passing, including chooser-only Escape dismissal, provenance keyboard access and sheet Escape returning focus to its opener. Screenshot review and source inspection were independent; browser execution/results are attributed to the coordinating agent.

The main actual 1440px capture confirms the corrected 12–13px Source coverage text and compact 52px summary strip. Desktop fields measure 36px. Sampled active navigation text has approximately 7.73:1 contrast; sampled muted table text on its light header has approximately 5.76:1. These sampled checks do not constitute a full accessibility certification. The final 390px capture confirms repository descriptions wrap within the card and the detail action remains reachable. The coordinating agent also added computed whitespace and right-bound assertions that caught the remaining legacy 740px minimum-width inheritance before the final pass. The focused responsive check now passes. Historical screenshots, preview designs and benchmark/readiness documentation remain preserved; final preservation hashes and production readiness are documented by the coordinating agent in the [verification report](../validation/live-workspace-redesign-2026-10-17.md).
