# Main application UX refinement research

Date: 2026-10-17. Status: design recommendation for review. No production application changes, dependency installation, API writes, or model calls are authorized by this document.

## Recommendation

Refine GitHub Manager as a compact repository workspace: give repository data and review evidence the strongest hierarchy, keep navigation quieter, bound search width, and size dialogs to their task. The goal is not to make every element smaller. Keep readable text, sufficient targets, explicit scope, and protected human decisions while reducing oversized framing and repeated chrome.

Use one shared design contract for the main app and Ground Truth. Preserve the earlier user-directed Deep Purple brand/primary, Indigo navigation, Blue links/selection, and original Zen Cat. Neutral surfaces should dominate; semantic color should identify a state or action rather than decorate every card. Ground Truth may use a three-pane review layout; the main explorer should remain a comparison-friendly table. They should share controls, typography, spacing, focus, status treatment, and dialog conventions.

This proposal updates the *visual sizing recommendations* in the earlier [UI plan](phase-0-9-ui-and-ai-controls.md) and [Ground Truth research](ground-truth-ux-research.md), subject to approval. It does not replace their functional contracts or the [system design](../system-design.md).

## Evidence and limits

Inspected repository instructions, the architecture and execution documents, relevant historical design rationale, the Phase 0.9 UI/AI plan and feedback, Ground Truth research/plan/implementation notes, and these actual implementation files:

- `frontend/src/components/WorkspaceApp.tsx`: explorer, taxonomy forms/draft review, details, allowance, merge/archive/reset dialogs, organizer.
- `frontend/src/components/workspace/Shell.tsx`, `TaxonomyBrowser.tsx`, `ExplorerTools.tsx`, `ReviewQueue.tsx`, `RunSetup.tsx`, `Icons.tsx`.
- `workspace.css`, `workspace-theme.css`, `src/app/globals.css`, `frontend/package.json`.
- Sibling `github-manager-demo/assets/site.css` and README as the established public brand reference.

Visually inspected [main app 1440px screenshot](../../frontend/test-results/refinement-1440.png) and [Ground Truth v2 1440px screenshot](../design/ground-truth-review-v2/desktop-1440.png). These are existing local artifacts, not a new live-runtime certification. Computer-use inventory had no available browser, and opening the in-app browser returned “Browser is not available: iab.” Official systems were inspected through their current published documentation; external layouts were not interactively measured. Proposed preview screenshots and automated geometry checks must supply the next visual evidence.

The installed manifest is Next.js **16.4.0**, React/React DOM **19.3.0**, with project CSS and SVG icons. No MUI, Tailwind, or UIkit is installed. MUI Core is an earlier recommendation, not an approved dependency decision. Before technical recommendations, read the bundled Next guides for CSS, CSS-in-JS, and font optimization under `frontend/node_modules/next/dist/docs/01-app/`.

| Observed implementation / artifact | Interpretation and proposed response |
|---|---|
| Desktop shell header is 76px; sidebar is 280px, increasing to 300px above 1700px. Header becomes 122px at intermediate width and 176px on mobile. | Persistent navigation consumes substantial vertical space. Use a 56px desktop header and move secondary actions into a menu before wrapping; preserve workspace context and mobile reachability. |
| Main app search is **already capped at 360px** through base CSS. Theme applies 44px search/select height and 40px buttons. | Do not diagnose all search as unbounded. Retain the cap and reduce surrounding height/padding. In contrast, Ground Truth v2 visibly stretches search to about 780px at 1440px, with a 48px field. |
| Main screenshot places the first data row around y=640 after heading, demo note, transient notice, five KPIs, toolbar, scope strip, and table heading. | Vertical hierarchy costs more than repository text. Compress framing, consolidate scope information, and evaluate normal and notice-present states separately. |
| Five KPI cards each use colored top borders, tinted gradients, colored numbers, and icons. “Selected” is always a separate emphasized card. | Several accents compete without encoding distinct urgency. Use neutral metrics; emphasize Needs review only when actionable and selection when nonzero. Counts and their units remain unchanged. |
| Theme gives panel radii 16px, modal radii 20px, control radii 12px, and many full-pill labels. | Large rounding repeats at every level. Use a small, nested radius hierarchy; retain pills for compact status/filter chips only. |
| Taxonomy search has both an outer search boundary and a visible inner input boundary in the screenshot. | Confirmed cascade issue: `.wm-app input:not([type=checkbox])` outranks `.wm-taxonomy-search input`. Use one owning search control with one border and one focus ring. |
| Main repository links/names are already 14px; source/status text is mostly 12px after theme overrides. | Preserve these improvements. Increasing density should not return to the original 8–11px primary labels. |
| All modal tasks share `max-width:780px`, `max-height:90vh`, padding, and scrolling for the whole dialog. | Archive confirmation, concept creation, and large taxonomy draft review have different content needs. Introduce task-based widths and separate scrollable body from persistent header/actions. |
| Generic Modal supports Escape, initial focus, a basic Tab loop, and restoration, but every backdrop click closes immediately. | Preserve the existing useful focus behavior; protect dirty forms, verify background inertness/scroll lock and visible-only focus handling. This is a code risk requiring runtime QA, not a claim that the current trap always fails. |
| Local repository Details uses an external-arrow SVG, while GitHub links also show an external arrow. Star/watch/empty-state treatments still include text glyphs. | Local inspection and external navigation should look distinct. Reuse the SVG family for detail, star/watch, empty state and close actions. |
| Content and organizer headings are “Make it your own.” and “Organization, with oversight.” | Prefer task names “Content settings” and “AI Organization”; keep explanatory language subordinate. |
| Review queue renders reason, existing membership, evidence IDs, provenance and actions in large suggestion articles. | Preserve the evidence; organize repeatable fields into an aligned comparison structure, with secondary detail disclosed locally. |
| Sibling demo uses dark ink `#24263c`, Indigo `#3949ab`, pale neutrals and calm cat branding; it also has an 88px header, 16px marketing body and 20px surfaces. | Borrow color discipline and legibility. Marketing hero/header scale is not the right repeated-workspace scale. |

## Professional references and how they apply

These are current **primary sources**, checked on 2026-10-17. The exact project values below are design judgments informed by these sources, not universal constants or copied framework defaults.

| Source evidence | Application to GitHub Manager |
|---|---|
| [Primer Button](https://primer.style/product/components/button/) distinguishes compact/default/large uses and advises sparse primary-action emphasis. | Use compact desktop toolbar actions; one primary action in a local task group. Avoid making AI, Content and Sync look like three competing calls to action. |
| [Primer Dialog guidelines](https://primer.style/product/components/dialog/guidelines/) describe separate header, scrollable body and footer, a safe content area, and simple focused dialog tasks. Forms receive special dismissal treatment. | Give confirmation and form dialogs different widths, keep actions reachable, and guard unsaved edits. Large multi-context taxonomy work may deserve an in-page editor in a later approved phase. |
| [Geist Input](https://vercel.com/geist/input) offers size variants, scoped search, labels, error/helper text and known-list selection guidance. | “Search repositories” and “Search taxonomy” remain distinct scopes. A searchable known-language/concept picker should preserve canonical values and visible labels; an icon or placeholder cannot be the only label. |
| [Geist Table](https://vercel.com/geist/table) supports semantic comparative tables, clear unknown values and aligned numeric data. | Keep the explorer a table, use tabular figures, make unknown data explicit, and distinguish local details from external links. |
| [Carbon Data table](https://www.carbondesignsystem.com/building-blocks/core/components/data-table/guidelines) provides 24/32/40/48/64px row tiers for different density/content needs and ties toolbar/action proportions to table density. | Density must match content. A two-line repository record should not be forced into a 32px single-line row. Keep toolbar, bulk actions and pagination visually related; use expansion/detail for secondary material. |
| [Carbon Modal specifications](https://www.carbondesignsystem.com/building-blocks/core/components/modal/specifications) provide multiple responsive size classes. | Dialog width depends on content and viewport; a common 780px maximum for every task is insufficient design control. Do not copy Carbon’s full-width button treatment into this app automatically. |
| [Atlassian Typography](https://atlassian.design/foundations/typography) defines 14/20px default app text, 16/24px larger text and 12/16px secondary text. [Spacing](https://atlassian.design/foundations/spacing) distinguishes compact gaps from section/layout spacing. [Tokens](https://atlassian.design/foundations/tokens/design-tokens/) names repeatable semantic decisions. | Centralize text, spacing, colors and sizing so the two workspaces cannot drift. Use 14px for repeated UI and more generous evidence reading styles without making every label large. |
| Linear’s [March 2026 design refresh](https://linear.app/now/behind-the-latest-design-refresh) reduces competing sidebar prominence, excessive icons, broad tab treatments and unnecessary separators. | Let the current repository/task dominate. This supports quieter framing, not inaccessible low-contrast text or removing useful structure. Linear’s dark screenshots are a hierarchy reference, not a palette to copy. |

## Shared token contract proposed for approval

Coordinate this contract with the isolated Ground Truth and main app previews. The approved palette’s roles remain; reduce how much tinted area each role occupies.

| Role | Proposed value / rule |
|---|---|
| Font | Existing Inter/system sans stack; explicitly verify the rendered fallback. No new font download is required. |
| Repeated UI/body | 14px / 20px, weight 400; emphasized labels 500–600. |
| Labels/helpers | 13px / 18px; metadata 12px / 16px. Essential decisions and errors never become tiny metadata. |
| Page / section / dialog titles | 24/30px; 16/24px; 18/24px. Repository list name 14/20px, detail name 16/24px. |
| Evidence prose | 14/22px default; optional 16/24px reading presentation. Raw source 12–13/20px monospace, adjustable/wrappable where appropriate. |
| Numeric metrics | 22/28px semibold, tabular figures; neutral ink by default. |
| Desktop controls | 32px buttons/select triggers; 36px search/standard form controls. Textareas expand with content. No additional arbitrary 38px tier. |
| Coarse pointer / narrow touch UI | At least 44px interactive targets; mobile text inputs 16px. Preserve pinch zoom and browser scaling. |
| Icon / target | 16px toolbar, row and metadata icons; 18px navigation icons; 32px desktop icon-button target. Close/delete/remove targets must stay distinct and reachable. |
| Spacing | 4, 8, 12, 16, 24, 32px. Icon-to-text 6–8px; related field gap 12px; panel padding 16px; larger section gap 24px. |
| Radius | 6px controls; 8px panels; 10px dialogs; 999px compact status/filter chips only. Inner corners smaller than outer surface corners. |
| Shell | 56px desktop header; 280px taxonomy rail. Optional later resizing 240–320px, without making it a dependency of the visual refinement. |
| Main content | 24px desktop and 16px narrow gutters. Table uses available width; prose/settings forms use an appropriate reading/form maximum. Do not artificially stretch text fields to fill a wide page. |
| Search width | Explorer/Ground Truth 360px default, max 400px when query content warrants; min 240px before wrapping. Narrow layout 100%. Taxonomy search fills its rail. |
| Form widths | Short numbers about 112–160px, ordinary selects about 160–240px, names up to 400px. Long concept pickers may expand; text wrapping must remain available. |
| Explorer rows | 64px target minimum for two-line records, 12–16px horizontal cell padding. Allow growth for content; optionally disclose excess chips after two lines with an explicit count. One-line histories may use 40px rows. |
| KPI summary | 56–64px neutral summary cells, 12px gaps. Preserve all current counts and selected subtotals; do not confuse label coverage with project organization. |
| Dialog widths | Confirmation 400–480px; focused form 560–640px; genuinely complex review 800px. Width never exceeds viewport minus 32px. |
| Dialog height | Desktop maximum `calc(100dvh - 48px)`; body scrolls with header/actions available. Full-screen form dialog on narrow screens if needed. |
| Surface / ink | Page `#f7f9fd`, white panels; primary text `#24263c`, secondary `#535a73`. |
| Brand / primary | Deep Purple `#673ab7`, hover `#512da8`; use for the principal action and brand emphasis. |
| Navigation / selection / link | Indigo `#3949ab` / `#303f9f`; pale selected surface `#e8eaf6`; Blue link `#1565c0`. Avoid blanket coloring of ordinary text. |
| Information / focus | Pale Light Blue information only when useful; focus `#0277bd`, 2px visible ring with 2px offset. Focus is distinct from selection. |
| Boundaries | Decorative separator around `#e0e6ef`; required input boundary around `#8791a5` against white. Do not rely on a pale separator as the only input affordance. |
| Elevation / motion | Quiet 1px panels, shadow mainly for overlays. Brief 120–180ms feedback; reduced motion honored, existing mascot animation preference retained. |

Calculated sRGB pairs: ink/white **14.81:1**, secondary/white **6.82:1**, white/primary **7.33:1**, white/Indigo **7.73:1**, Blue/white **5.75:1**, selected text/surface **7.50:1**, proposed input boundary/white **3.17:1**, focus/white **4.80:1**. Decorative separator/white is **1.25:1**, so it is not sufficient as a required control boundary. These calculations do not certify hover, disabled, selected, chip, error or tinted-surface combinations. Validate the rendered pairs against [WCAG text contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) and [non-text contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html).

32px desktop controls exceed the usual [WCAG 2.2 target-size minimum](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html), but small inline controls, spacing exceptions and actual hit areas still require checks. 44px is this project’s touch target, not a claim that WCAG AA requires 44px everywhere. Sticky headers/actions must not cover focus; see [focus not obscured](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html).

## Main app changes in priority order

### 1. Shell, explorer and shared controls

Retain the cat/brand and workspace picker in the header. Keep Sync GitHub separate from AI Organization. Use compact labeled actions at wide widths and a reachable menu for secondary actions before wrapping into a tall header. Content settings is navigation rather than a permanent primary call to action. Preserve the optional taxonomy menu as an additional access path without duplicating every sidebar control on the page.

Keep Collections compact and the taxonomy rail independently scrollable. Fix the double input border. Use one selection treatment for the active collection and one related treatment for a selected concept, with 16–18px consistent icons and aligned counts. Long taxonomy names need wrapping or an accessible reveal; do not let badges push all text out. Preserve remembered expansion, search-by-alias, pending/accepted counts, drop feedback and keyboard/manual-assignment alternatives.

Compress page heading, neutralize KPI decoration, and keep the search/filters on one deliberate toolbar. Group the organization-view choice with filtering; make accepted-label breakdown secondary text/disclosure instead of a second competing toolbar. Preserve all current organization-status views. Keep visible applied-filter chips and result counts; do not silently drop the activity window or collection/concept context.

Keep repository names at 14px and the table as the default view. Give Repository the widest column; show description as a second line and current organization in a stable aligned column. Use one local Details icon/label and reserve external arrows for GitHub links. Keep public/private/synthetic and USER/RULE/AI provenance explicit. Additional labels may collapse into a named “+N labels” action only if the full set remains one action away. Unknown and no observed activity remain honest states.

### 2. AI Organization, sync and review

Use task titles and a short status line that distinguishes execution, coverage and freshness. Sync imports GitHub data; AI organization classifies against the approved taxonomy; rediscovery creates a proposal. Keep these meanings and labels separate. Progress remains non-blocking so imported repositories remain usable.

Organize run setup by operation, scope/selection and budget, with advanced re-analysis behind disclosure. Values and eligibility must stay visible before Start. Preview and Start remain two separate deliberate stages; preserve the exact server-issued plan, expiry, exclusions, cost/call ceilings, cache/rules distinctions and no-fallback policy. Do not use optimistic completion or auto-start while simplifying the form.

Use restrained comparison rows for suggestions: repository/current membership, proposed concept, reason/evidence, provenance/state, Accept/Reject. Keep existing bulk review summary and stale/skipped outcomes. An accepted proposal becomes a protected human decision only after server success. Model confidence remains uncalibrated; never style it as correctness. A dense view must not conceal evidence or replace deliberate review with majority/automatic acceptance.

### 3. Taxonomy management and dialogs

Keep concept cards for short discovery-oriented collections; use aligned rows/table for large inventories where name, type, parent, alias and membership counts need comparison. Put optional logo settings below the primary content-management task or behind a section disclosure. Keep type and canonical IDs separate from display names; retain archive/merge consequences and duplicate/alias warnings.

Apply confirmation/form/review dialog variants instead of one generic size. Archive and simple membership confirmations should be compact; create/edit concept uses a focused single column. Large taxonomy draft review may use 800px with grouped rows and a persistent publish footer; a future in-page editor is preferable if draft complexity becomes a full workspace. Reset retains its two independent groups, impact preview and exact DELETE confirmation regardless of visual compression.

Dirty form/backdrop/Escape behavior must preserve edits. Verify focus restoration, body scroll locking, background inertness, focusable validation summary and first-invalid-field focus. Keep save errors local, distinguish a successful save from a failed refresh, and prevent double submission without removing progress feedback or losing keyboard focus.

## Implementation risks and boundaries

1. **Cascade drift:** project styles layer broad preflight selectors, compressed workspace CSS and successive theme overrides. After approval, use project-owned semantic tokens and scoped component styles rather than adding another broad override sheet. Bundled Next CSS documentation warns that global styles persist through navigation and production chunk ordering can differ; verify a production build as well as development.
2. **Library choice is separate:** these refinements are achievable with existing CSS. MUI remains a possible later implementation tool. Its theme still needs these task-specific sizes, colors and wrappers; adding it alone cannot repair hierarchy. Before adoption, explicitly verify the actual Next 16.4/React 19.3 combination and App Router styling integration. Do not install MUI, Tailwind or another system during research.
3. **Density versus access:** shrink excess padding, not all text or hit targets. Account for 200% zoom, 320px reflow, long canonical names, touch and keyboard navigation. Never disable zoom to preserve a layout.
4. **Truthful fixtures:** previews must label illustrative repos, counts, AI plans and statuses. They cannot imply a real API call, saved review, eligible cohort or production integration. Production confidence requires disposable runtime validation after implementation approval.
5. **Architecture preserved:** GitHub-owned metadata, private evidence policy, manual precedence, independent concept types, revisions, reset fencing, budgets and audit history remain untouched. UI changes cannot silently change backend semantics to fit a mockup.

## Acceptance and phased approval

**Design phase, authorized now:** produce isolated main/Ground Truth previews using the agreed contract, with screenshots at 1920×1080, 1440×900, 1280×800, 1024×768 and 390×844. Include normal, filter-active, selected, loading, empty, error and dialog states. Compare the screens side by side at the same viewport and zoom. Review actual alignment, text hierarchy and proportion; the presence of 32px controls is not evidence of a successful design by itself.

**Proposed production phase 1, requires approval:** shared theme/control/shell and explorer hierarchy; preserve behaviors. Validate search, filters, selection across pages, local/external navigation, long names, tree expansion/search/drop/manual assignment, focus and reflow. Suggested geometry target: first repository row at or above **420px** in a 1440×900 normal fixture without transient notices, with at least six two-line repository rows visible. A notice-present fixture must show how each added message affects this budget. Treat this as a review target, not a reason to hide required warnings.

**Proposed production phase 2, requires approval:** dialog variants, content management and organizer/review hierarchy. Validate dirty-state protection, all focus paths, error/partial outcomes, exact reviewed-run execution, canonical conflict repair and reset confirmation. Never create production reset/AI work solely for visual QA.

Acceptance checklist:

- One shared typography/control/spacing/radius contract; retained approved palette/mascot behavior; no new unapproved dependency.
- Search respects scope and desktop width, all control borders are single, and icons communicate local versus external navigation consistently.
- No horizontal **page** overflow at supported widths; a genuinely comparative table may scroll inside its named container. Long forms/labels reflow without clipped text or hidden actions.
- Body, label, metadata and metric hierarchy is consistent; evidence remains comfortably readable. All essential text/state/control pairs are measured, including focus and hover.
- Header stays compact without making essential actions unreachable; taxonomy receives most remaining rail height and has independent scrolling.
- Dialogs use their content class, preserve viewport safe areas, keep header/actions reachable and return focus correctly. Keyboard-only completion and 200% zoom remain usable.
- Loading retains context; no-results, empty collection, source/API error, partial success and stale/conflicting result are distinguishable. Server-success gating remains for saves, acceptance, publication, Start and reset.
- Main app behavior and Ground Truth behavior keep their separate domain contracts while sharing visual primitives.
- Run relevant existing demo/corpus browser suites, typecheck, lint and production build after approved application changes. Add meaningful regression checks for changed interaction risks; screenshots and geometry do not substitute for persistence or safety checks.

Final production implementation approval remains pending. The isolated previews and this research are the concrete review artifacts; neither authorizes application edits, deployment, package installation, model spending or data mutation.
