# Workspace UX refinement — shared design and review plan

> **Latest authorization and implementation — October 17, 2026:** The user approved the **full live structural rollout**. The main application and Ground Truth workspace are now implemented and have completed independent UX acceptance; final build/restart checks are recorded in the [verification report](../validation/live-workspace-redesign-2026-10-17.md). Follow the [live redesign contract and acceptance record](live-workspace-redesign-2026-10-17.md). Its compact layout and white-on-Indigo selected-state rules supersede earlier sizing/color choices and the approval holds below. The following body preserves the prior preview/control-pass history; it is not a current instruction to stop for another approval.

Date: October 17, 2026. Status: live Indigo/searchable-control refinement authorized; broader structural previews retained for later review. This revision responds to the user's feedback that search, fields and dialogs in the first Ground Truth preview still felt disproportionate. It also extends the design study to the main application. Preserve the first preview for comparison.

The user separately authorized the agent annotation pilot and its app comparison/review integration during this pass. That bounded functional work proceeds under [its execution record](agent-annotation-pilot-execution.md); approval remains pending for the broader aesthetic rollout described here.

## October 17 authorized live control refinement

The latest user instruction authorizes applying Indigo and professional control consistency across the live app, including searchable dropdowns. It supersedes this plan’s earlier Deep Purple primary role and its blanket implementation hold **for this bounded UI update**. The larger three-pane redesign, new incomplete-draft API and MUI dependency integration remain separate proposals. No package is being added for these controls.

The demo repository’s Watch Demo and Deep Dive actions are the visual reference: Indigo `#3949ab` filled primary, `#303f9f` hover/interactive text, soft `#e8eaf6` → `#e3f2fd` secondary, rounded action shapes and restrained shadows. Blue remains a supporting accent and visible focus; error/warning/success colors retain their meaning. Reading text stays neutral.

Live controls use a shared searchable single-choice component: 40px ordinary desktop fields/buttons, 32px compact row actions, 44px touch controls, 14px field text, 13px labels and 16px mobile inputs. Search filters known options without accepting arbitrary text. Keyboard selection, modal focus/Escape, disabled options, required validation and long labels must work. This live density supersedes the earlier preview targets below; preserved previews are evidence of an earlier layout study.

Two developer agents own main-app and Ground Truth integration; a separate UX agent audits professional design and accessibility. This bounded update is now implemented and verified; see the [completion report](../validation/indigo-controls-2026-10-17.md) and [actual app captures](../design/workspace-refinement/live-indigo/README.md). Verification covers actual app workflows, searchable controls, desktop/mobile screenshots, contrast and the preserved Ground Truth review gates. Corpus snapshots, annotations, human reviews, benchmark reports and budget ledgers remain untouched.

## What this pass changes

The first pass improved adjacency and safety, but its 78px header, 780×48px search, large page introduction and generous nested cards still spent too much space on controls and chrome. The main app has a different problem: its search is already capped around 360px, while multiple notices, KPI cards and filter rows push repository browsing far down the screen. Do not prescribe the same width correction to both screens.

Four specialists contribute in staged passes: the existing Ground Truth researcher/developer and a new main-app researcher/developer. They share one proportion and typography contract, produce separate previews, and cross-review the results. The coordinating plan resolves any differences between exploratory recommendations.

The aim is a legible, aligned productivity interface. Review the visual balance of complete screens and open dialogs as well as individual pixel measurements. A smaller control alone is not proof of better design.

## Research basis

Use primary professional design systems as references, not additional runtime dependencies:

- [GitHub Primer TextInput](https://primer.style/product/components/text-input/) and [Dialog](https://primer.style/product/components/dialog/) inform context-specific sizing and accessible form/dialog behavior.
- [Vercel Geist Input](https://vercel.com/geist/input) distinguishes single-line text, multiline text and searchable known-list selection. [Geist Typography](https://vercel.com/geist/typography) distinguishes common 14px product copy from more spacious 16px modal copy.
- [Vercel interface guidelines](https://vercel.com/design/guidelines) inform deliberate alignment, intrinsic layout, consistent nested radii, visible focus and responsive controls. Preserve browser zoom and use 16px mobile inputs. Adapt generic advice to our workflow: human confirmation and AI run initiation remain explicit and depend on server success.
- The specialists' research adds Carbon, Atlassian and Linear where their official guidance supports a concrete recommendation. Record actual pages/screens inspected and distinguish source guidance from our chosen dimensions.

Retain the Material palette and existing Zen Cat. Neutral surfaces dominate; the latest approved Indigo role supports primary actions, interactive text and selection/navigation, Blue supports accents/focus, and semantic colors communicate status with text. Avoid adding a different visual system to every panel.

## Proposed shared proportions

These numbers are project choices to validate in the previews, not universal rules attributed to the reference systems.

| Element | Desktop target | Responsive/content rule |
|---|---|---|
| Application header | 56px | May wrap deliberately on narrow screens; never squeeze all navigation into one row. |
| Main taxonomy rail / review queue | Approximately 280px | Collapse or expose a drawer before it crowds the working pane. Resizing is a possible later enhancement, not an existing feature claim. |
| Toolbar controls | 32px | Same-row controls align by outer edge and baseline. |
| Search and ordinary single-line forms | 36px | Mobile/coarse-pointer controls have at least 44px targets; mobile input text is 16px. |
| Repository search | Preferred 360px, maximum about 400px | Shrinks or wraps safely; modal searches can fill their local form column. |
| Selects / numeric fields | Roughly 160–220px / 96–120px | Width follows meaningful expected content; long options remain readable in their picker. |
| Typography | UI 14/20, labels 13/18, secondary metadata 12/16 | Purpose/evidence prose may use 15–16px with greater line height; no essential instruction hidden in tiny text. |
| Page heading | 24/30 | Clear task name and one concise supporting sentence. |
| Radii | Controls 6px; panels 10px; dialogs 12px | Nested curves follow a coherent hierarchy; tags remain rounded. |
| Spacing | 4px base; 8/12/16/24px roles | Space groups deliberately; consistent label-to-input and helper gaps. |
| Dialog widths | Confirmation 400–480px; forms/filters 560–640px | Approximately 800px only for genuinely complex comparison/setup content; small screens use available width with margins. |
| Dialog structure | Distinct heading, body and action footer | Bound height to viewport; scroll the body; keep focus and actions reachable, including zoom and mobile keyboard. |

## Ground Truth preview revision

Preserve queue → review → evidence adjacency, immutable proposals and the explicit human decision. Replace the marketing-style introduction with a compact task heading and progress. Use quieter surfaces and fewer competing containers. Size search/status/filter controls as a matched toolbar; keep field labels outside the value area when space permits.

Refine the filter and known-label dialogs as real form compositions: short heading, consistent columns and labels, bounded results area, selected count and clear footer actions. Confirmation and dirty-leave dialogs use a smaller width. Keep evidence quotes legible, source information secondary and the final decision visible.

The interaction proposal remains Save draft / Needs evidence / Confirm & next, with three deliberate group acknowledgements. Retain the prior plan's separate incomplete-draft API, validated multi-facet semantics, stable queue continuation, structured conflict recovery and stale-response protection. This aesthetic pass does not make those capabilities implemented.

## Main-app preview

1. Compact header with clear workspace context, AI Organization and content/sync access. Reuse branding and existing functional terminology.
2. Give the taxonomy tree sustained space below compact collection navigation. Projects, Topics and Tags remain discoverable; accepted/pending states stay explicit.
3. Replace the large KPI card row with a restrained summary strip, including selection count. Use icons consistently with readable labels and numbers.
4. Consolidate routine feedback into one appropriate notice and local state. Preserve material access/rate-limit warnings; do not hide actionable conditions merely to reduce height.
5. Align search, language, visibility and view controls. Keep the normal repository list near the top of the working area; aim for the first row within roughly 330–360px at 1440×900, then assess the actual screenshot.
6. Design the AI setup dialog with grouped steps/fields, appropriately narrow numeric inputs and a clear primary action. Preserve existing budget modes, sample sizing, reanalysis controls and private-content choices.
7. Design taxonomy conflict review with the exact conflicting canonical/alias owner and an explicit repair choice. A bounded detail area and reachable footer replace an endlessly growing stack. Do not introduce silent remediation or automatic publication.

Use illustrative public examples and clearly label simulated preview behavior. Do not represent an animation, fake progress or a mock save as a live service result.

## Verification before presentation

- Inspect actual screenshots at 1920×1080, 1440×900, 1280×800 and 390×844, with open filter/setup/conflict dialogs as well as default screens.
- Measure toolbar alignment, widths, input heights, dialog padding, text hierarchy and visible working area. Check long names and selected values, wrapping, overflow, keyboard focus and mobile input text.
- Measure actual text/background contrast and necessary control/state contrast. Normal text targets WCAG AA 4.5:1; necessary non-text visuals 3:1. A prototype check is not certification of a later MUI implementation.
- Exercise meaningful in-memory preview interactions: search/filter, selection, tree browsing, dialog open/close, invalid input, draft guards and explicit review gates. Document simulated behaviors and limitations.
- Cross-review the two screens for common tokens and consistent controls. Resolve visible inconsistencies before calling the design ready.
- Verify application/config hashes remain unchanged. Preserve corpus files, human reviews, benchmark reports, credentials and the running local app.

## Implementation sequence after design approval

1. Validate/pin the single MUI Core integration against the locked Next/React versions, with one shared project-owned theme and context-specific density wrappers. Reference systems inform appearance; their packages are not installed together.
2. Deliver the Ground Truth vertical slice and its bounded API/persistence additions from the existing UX plan; verify workflow and review authority.
3. Apply the approved shared foundation to the main app shell, browsing/filter controls and KPI summary without changing eligibility/classification semantics.
4. Refine AI settings and taxonomy review using their existing contracts, then complete focused regressions, accessibility checks and visual review.

The independent LLM annotation pilot can run from a command-line harness against the frozen corpus and registry. Its version-bound outputs can later feed the review UI; this design work is not a prerequisite and starts no model calls.

Approval remains required for the broader structural proposals beyond the authorized live control refinement: [AGENTS.md](../../AGENTS.md), “Ask for approval before implementing.”

## Completed review artifacts

- [Local review hub](http://127.0.0.1:8132/workspace-refinement/) while the preview server is running; [saved hub](../design/workspace-refinement/index.html).
- [Ground Truth v3 preview](../design/ground-truth-review-v3/preview.html), [desktop](../design/ground-truth-review-v3/desktop-1440.png), [filters](../design/ground-truth-review-v3/filters-desktop.png), [mobile](../design/ground-truth-review-v3/mobile-390.png), [developer notes](ground-truth-ux-v3-implementation.md).
- [Main-app preview](../design/main-app-refined/preview.html), [desktop](../design/main-app-refined/desktop-1440.png), [AI setup](../design/main-app-refined/ai-setup-desktop.png), [taxonomy conflict review](../design/main-app-refined/taxonomy-review-desktop.png), [developer notes](main-app-ux-refinement-implementation.md).
- [Ground Truth primary-source research](ground-truth-ux-refinement-research.md), [main-app primary-source research](main-app-ux-refinement-research.md), and [shared token reference](../design/workspace-refinement/tokens.css).

The main preview passes 18 documented browser checks; Ground Truth v3 passes 23, including the cross-review fix for active filter chips pushing the footer beyond the viewport. Desktop measurements: header 56px; search 360×36px; main first repository row at 359px; Ground Truth working region at 183px. Ground Truth's anchored pickers are 380/390px, its small leave dialog 480px and evidence form 560px; the main AI setup is 640px and complex taxonomy review 800px. These are prototype results with illustrative data, not production accessibility or API certification. Earlier v2 artifacts remain available.
