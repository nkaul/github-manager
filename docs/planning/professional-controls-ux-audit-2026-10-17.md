# Professional controls audit: Indigo theme and searchable selection

Date: October 17, 2026. This audit supports the user's instruction to apply the demo site's Indigo treatment across the live application, make dropdowns searchable and make fields/buttons consistent. It is an implementation acceptance guide, not a claim that the changes already pass. The broader review-workflow redesign remains a separate scope.

## Finding and scope

The live application has a usable set of workflows, but controls come from several independently styled surfaces. A palette-only edit would leave the principal usability problem unresolved: a person can search one list, must scroll another, and sees different field/button proportions while completing the same task.

At the initial source audit, 31 native `<select>` sites remained across six files. One site renders the three Project/Topic/Tag selectors dynamically, so the rendered count can be higher. The language filter separately uses a native `<datalist>`. There is no shared search-select component at this starting point.

| Surface | Selection controls to cover | Existing source |
|---|---|---|
| Shell | Workspace collection | `workspace/Shell.tsx` and the separate Corpus header |
| Repository explorer | Language, visibility, activity window, organization-status view, bulk membership | `workspace/ExplorerTools.tsx`, `WorkspaceApp.tsx` |
| Taxonomy/content | Concept type, parent Domain, merge target, manual membership, rule field/condition/concept | `WorkspaceApp.tsx` |
| AI organization | Inference mode, selection mode, scope, budget mode, allowance action, post-reset action | `workspace/RunSetup.tsx`, `WorkspaceApp.tsx` |
| Classification review | Taxonomy type, concept, grouping | `workspace/ReviewQueue.tsx` |
| Ground Truth | Sampling/assigned Domain, Project/Topic/Tag, status, known label, evidence file, source document, decision | `workspace/CorpusWorkspace.tsx` |

Searchability applies to every option selector in this authorized pass, including short option lists. It does not turn action menus, checkboxes, taxonomy tree expansion or tabs into comboboxes. Ordinary text fields remain free text. Numeric budget/sample-size controls retain their numeric types, min/max constraints and validation.

## Concrete visual direction

Use the existing local demo's `assets/site.css` as the reference, particularly `.button.primary` and `.deep-dive-cta`. The former uses Indigo `#3949ab`, white text and a restrained shadow. The latter uses dark Indigo `#303f9f`, a pale Indigo/Blue surface and a rounded outline. Adapt these roles to a productivity interface; marketing-scale padding and continuous glow do not belong on routine forms.

| Role | Suggested token | Purpose |
|---|---|---|
| Primary action | `#3949ab` | Save, confirm, run/review entry points |
| Primary hover | `#303f9f` | Darker action state |
| Primary pressed | `#283593` | Deliberate active state |
| Secondary action | `#e8eaf6` to `#e3f2fd`, text `#303f9f` | Cancel, preview, inspect, secondary navigation |
| Main text | `#24263c` | Neutral readable content |
| Secondary text | `#535a73` | Labels, helper text and metadata |
| Control boundary | `#8993a5` | Necessary field/button outlines on white |
| Decorative separation | `#dfe4ef` or `#c5cae9` | Panels and quiet selected surfaces |
| Focus | `#0277bd` | Keyboard focus, separate from selected state |

Retain red for destructive/error actions, amber for warnings and green for successful states. Keep status text/icons so color is not the only signal. Indigo must replace active Deep Purple action/selection roles in AI headers, progress, badges, stale-analysis labels, taxonomy counts and logo selector controls as well as the first button encountered. Existing Zen Cat assets and the user's logo configuration remain intact.

Calculated sRGB contrast at the initial audit: white on Indigo `#3949ab` **7.73:1**; white on `#303f9f` **8.98:1**; dark Indigo on `#e8eaf6` **7.50:1**; neutral `#24263c` on white **14.81:1**; secondary `#535a73` on white **6.82:1**; control boundary `#8993a5` on white **3.10:1**; pale `#c5cae9` on white **1.62:1**. Therefore the pale demo border is suitable for decorative separation, but should not be the sole necessary field boundary on white. Verify actual computed colors and backgrounds after integration, including gradients, hover, focus and selected states.

Normal text should reach 4.5:1, with the usual large-text exception. Necessary control/state visuals should reach 3:1 against adjacent colors. These are acceptance targets, not an accessibility certification of the app. [W3C text contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html), [W3C non-text contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html).

## Proportion contract

The values below are project recommendations rather than dimensions mandated by a source. A coherent standard with an explicit compact variant is more professional than making every component large or allowing every page to invent its own scale.

| Element | Recommended default | Constraint |
|---|---|---|
| Single-line input/search/search-select | 40px height | Equal outer height within a row; label outside value area |
| Primary/secondary/destructive button | 40px minimum height | Same font, padding system and aligned baseline |
| Dense row action | Explicit 32px compact variant | Use only in dense rows; never silently shrink primary form actions |
| Narrow-screen/coarse-pointer control | 44px minimum target | Input text 16px; do not prevent zoom |
| Input/button typography | 14px, roughly 20px line height | Sentence case; important labels should not become 10px text |
| Labels/helper/metadata | 13px / 12px | Clear hierarchy; readable contrast |
| Field radius | One 10–12px token | Match search/select/text/numeric fields |
| Action radius | Rounded pill | Retain compact dimensions and consistent icon alignment |
| Textarea | Same field border/radius/font | Full local width, meaningful min-height and vertical resize |
| Search width | Preferred 360px, about 400px maximum in a broad toolbar | Fill only its local column; shrink safely on mobile |
| Short numeric field | Roughly 96–120px | Avoid a tiny number floating inside an unnecessarily wide box |

WCAG 2.2's minimum target criterion is 24×24 CSS pixels, with exceptions including sufficient spacing. The recommended 44px touch target here is a more comfortable project choice; it should not be described as the WCAG AA minimum. [W3C target-size guidance](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum).

## Search-select behavior contract

Use one shared editable combobox with a listbox. Preserve each existing option's stable value, visible label, disabled state and change handler. The control has an accessible name, expanded state, associated popup and active-option reference. Keyboard focus remains on the input; Arrow keys navigate enabled choices, Enter accepts and Escape dismisses. Popup indicators/options are not extra Tab stops. Keep ordinary browser text editing intact. [W3C combobox pattern](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/).

The following are additional product decisions for this app:

1. Typing filters labels, with group/category text available where it helps disambiguate. No network or model request is needed to search an already loaded option list.
2. The typed query and committed selection are separate. A random string can never become a taxonomy ID, workspace, budget mode or human-review decision.
3. Enter commits only an enabled, visible result. Searching with no matches announces a clear empty state; it cannot submit the enclosing form accidentally.
4. Escape restores the committed label and closes the popup before a second Escape can dismiss an enclosing modal. Tab or outside click discards an uncommitted filter query; it must not silently select the first match.
5. Show all choices when explicitly opening the list, while indicating the committed choice. Search should be case-insensitive. For long taxonomy lists, preserve useful Project/Topic/Tag grouping and search the displayed kind/name.
6. Required and disabled selectors retain their previous meaning. Disabled choices can be explained visually but cannot be reached as a selectable keyboard result or committed through pointer activation.
7. Long concept names and saved file paths remain readable in the popup. Constrain popup width/height to available viewport space, scroll results and keep the active result visible.
8. An optional hidden native select used only as a compatibility bridge must not become a duplicate screen-reader control, visible field, validation trap or Tab stop. Test the actual user-facing combobox rather than relying only on `selectOption()` against an invisible implementation detail.

## Integration hazards found

- `WorkspaceApp.tsx` contains a custom modal whose Escape handler currently closes unconditionally. A new search popup must consume its own Escape event when open.
- That modal also gathers `button,input,select,textarea,a[href]` for its focus loop. Hidden native controls or popup affordances can corrupt the loop unless only genuinely focusable visible controls participate. Recheck focus return to the invoking button and dirty-review behavior. The dialog must keep Tab navigation inside and restore focus when dismissed. [W3C modal-dialog pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/).
- The search shell already removes its inner input border with a sufficiently specific rule; taxonomy search does not consistently have the same protection. Avoid doubled borders, nested focus rings or two backgrounds inside one field.
- Current field heights range among 32/36/40/42/44px, with an independently compact header select. Multiple layered CSS rules style the same controls. Centralize the dimensions and states rather than adding another page-specific override for each screenshot.
- Ground Truth's seven-column filter row and wide semantic option labels need intrinsic min-width handling. At intermediate widths, deliberately wrap into fewer columns instead of squeezing every field into a narrow box.
- Ground Truth annotation-panel buttons have their own CSS Module, including a hardcoded `#673ab7` stage action. Shared global styling alone will miss them.
- Some taxonomy kind classes are reused on cards, chips and sidebar tree rows. Keep the scope of shared control selectors narrow so a chip does not become a 40px form field.
- Sticky headers/source panes, long source hashes and review notices must not cover the focused control or final action. [W3C focus-not-obscured guidance](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html).

## Acceptance and independent review

Check complete screens and open forms at 1920×1080, 1440×900, 1280×800 and 390×844. Inspect 200% zoom as a separate reflow check. Confirm no whole-page horizontal overflow, while deliberately scrollable evidence/table regions remain usable. Compare field/button outer heights and text baselines in the same row, not only their declared CSS tokens.

Exercise representative controls from every family: workspace switching; language/visibility filtering; long concept selection; create/merge/rule forms; AI scope and budget selection without starting a live run; Ground Truth filters; source selection; added-label evidence and review decision. Cover keyboard search/Arrow/Enter, no results, disabled options, Escape inside a dialog, Tab/outside dismissal and focus return. Verify that a filtered query does not change the underlying selection until accepted.

Run existing app and isolated Corpus browser workflows against disposable test backends. Adapt the interaction helper to exercise the visible combobox, preserving coverage of state changes, validation, persistence and workspace isolation. Existing benchmark/corpus files, human reviews, readiness reports, provider budgets and credentials must remain untouched. No provider or GitHub API call is needed for this UX verification.

Record actual screenshots, viewport/control measurements, contrast checks and test results after integration. Keep findings separate from passing evidence: this source audit by itself is not final verification.

## Status

Initial read-only audit and primary-source research complete. Recommendations were sent to the coordinating agent and both application developers before implementation.

During the first integration source review, two CSS issues were identified and corrected by the implementation agents: the legacy Language class was styling the new wrapper as an extra field, and the generic text-input selector overrode the shared combobox's chevron padding. The current source scopes the former to native language inputs and gives the shared input a stronger, narrowly scoped selector. The modal now excludes hidden/nonfocusable controls from its focus loop, and the shared selector consumes Escape while its popup is open. These are source-review observations; computed-style and workflow verification still follow.

The refreshed main-app AI setup preview was visually inspected for hierarchy, proportions and Indigo actions. It remains an illustrative prototype, separate from live-app implementation evidence.

Independent live-screen review also inspected the regenerated 1440×900 main screen and 390×844 mobile screen, plus Ground Truth's 1920×1080 saved-review and 390×844 mobile screenshots. Ground Truth now has clean retained-label rows, an aligned known-label selector/action, a compact decision field, legible notes/evidence and coherent Indigo actions/checkboxes. Its mobile header/context and summary wrap without visible clipping. The main screen has consistent action/metric colors and a readable organization-status selector; the initial regeneration exposed two additional legacy CSS collisions in Language and taxonomy search, which the coordinating agent is correcting before final visual recheck.

A subsequent source scan found no remaining native `<select>`/`<datalist>` sites or the audited active Deep Purple hexes in application component sources. This is a source-completeness observation, not proof that every runtime branch was exercised.

### Final independent review

The final saved application images were independently inspected at 1920×1080, 1440×900, 1280×800 and 390×844. The corrected main screen has one taxonomy-search outline, aligned search/Language/Visibility fields, sufficient chevron space and a fully readable desktop workspace selection. At 1280px the coverage explanation wraps deliberately; the control row stays aligned. Mobile uses its existing drawer and horizontally scrollable header actions. No new whole-page overflow or clipped form value was visible in the reviewed captures. The final optional result-count centering adjustment was made after these captures; its source changes only the count's alignment/minimum height.

The saved [layout audit](../design/workspace-refinement/live-indigo/layout-audit.json) records 40px heights for search, Language, Visibility and workspace fields at all three desktop widths, 34px right padding for the comboboxes, 13px KPI labels and 84–91px KPI cards. The lowest sampled text contrast is **5.97:1** across thirteen inspected text roles. These are sampled measurements; they do not certify every screen, gradient, assistive technology or physical mobile keyboard.

The coordinating agent reports **17 distinct application browser workflows passing across the full run and focused corrective reruns**, plus **two isolated Corpus workflows passing across their run and a named-popup assertion rerun**. The checks include visible searchable controls, discarded uncommitted text, required selection, disabled options, modal Escape, mobile long-option selection, taxonomy behavior and review persistence/isolation. This independent audit inspected the source, measurements and screenshots; it did not separately rerun those same suites.

The final source consistency correction is complete: taxonomy search now uses the shared `--control-border` (`#8993a5`) instead of the pale decorative border. The coordinating agent also added an actual boundary-color assertion to the existing layout check and is regenerating the final captures. The independent review found no unresolved design blocker within the authorized control/theme scope. Build, restart and final service-health checks belong to the coordinating implementation report.

Saved actual application screenshots: [main 1920px](../design/workspace-refinement/live-indigo/app-1920.png), [main 1440px](../design/workspace-refinement/live-indigo/app-1440.png), [main 1280px](../design/workspace-refinement/live-indigo/app-1280.png), [main mobile](../design/workspace-refinement/live-indigo/app-mobile.png), [Ground Truth review](../design/workspace-refinement/live-indigo/ground-truth-review-1920.png), [Ground Truth mobile](../design/workspace-refinement/live-indigo/ground-truth-mobile.png).
