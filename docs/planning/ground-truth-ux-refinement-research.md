# Ground Truth — productivity interface refinement

2026-10-17. Planning and isolated-preview specification only. This supersedes the first UX plan's blanket 44–48px desktop controls and large rounded surfaces; it does not authorize production changes or dependency installation. The v2 preview, corpus, SQLite reviews and benchmarks remain preserved.

## Finding and shared direction

The v2 preview improves the review workflow but gives supporting chrome too much space and emphasis. Its search is nearly a hero element; the large page heading, rounded cards, substantial headers and spacious dialog all compete with the case being reviewed. Merely shrinking those elements independently would still leave an inconsistent system. Use one restrained productivity system for the main app and Ground Truth: compact aligned controls, a clear typographic ladder, task-sized overlays and neutral surfaces. Preserve the approved Deep Purple brand/primary role and Indigo/Blue navigation/selection roles with restrained saturation. MUI remains a possible implementation vehicle from the earlier research; these visual decisions do not depend on MUI defaults.

The following contract is agreed with the main-app research/development agents and coordinating agent. These are **project design choices informed by sources**, not measurements copied from Linear or universal usability rules.

| Shared role | Desktop/fine pointer | Touch/coarse pointer |
|---|---|---|
| Global header | 56px height; 24px horizontal padding; 32px cat | Compact wrapping shell; 44px interactive targets; no oversized brand area |
| Navigation/queue rail | 280px preferred; resizable 240–320px | Collapsed into navigation/queue sheet |
| Toolbar buttons, selects, icon actions | 32px height; 10–12px horizontal padding; 16px icon | 44px minimum target; 16px input text |
| Search and ordinary form controls | 36px height; 10–12px horizontal padding | 44px height; do not scale every other element |
| Search width | 360px preferred; 400px maximum; may shrink to 280px before wrapping | Full available row |
| Text hierarchy | UI 14/20px; labels 13/18px; metadata 12/16px; page title 24/30px; section heading 16/24px | Same hierarchy; editable input text 16px to avoid mobile zoom |
| Detail repository title | 20/26px, weight 600; queue names 14/20px | Wrap long names; retain readable body text |
| Corners | Controls 6px; panels 10px; dialogs 12px; badges 4px | Same tokens |
| Spacing | 4/8/12/16/24/32px scale; toolbar gap 8px; panel inset 16px | 16px outer gutter; 12px between touch controls where practical |
| Surfaces | White canvas; neutral off-white rail/background; one soft divider per meaningful boundary | Same |

An expanded evidence reading view may offer 16/24px text without enlarging its navigation chrome. Use `min-height`, not clipped fixed heights, where text can wrap or zoom. Density follows input mode and task, not only a viewport breakpoint.

## What was inspected

- Read root/frontend `AGENTS.md`, relevant architecture/execution constraints, the corpus workspace contract, existing UX plan/developer notes and the first research document. Human authority, version-bound evidence, owner isolation and planning-only scope still apply.
- Inspected `docs/design/ground-truth-review-v2/preview.css`, HTML and the existing **1440×900 desktop** and **filters** PNGs. CSS confirms a 78px shell header, 48px search capped at 780px, 44px buttons, 26px repository title, 16px panels, 20px dialog radius and a 660px filter dialog. The screenshot shows the review canvas beginning near y=304px and the sticky footer covering the lower groups until the editor scrolls. These are observations of the prototype, not the running product.
- Re-read sibling `github-manager-demo/assets/site.css` and `index.html`. Its dark ink, coherent spacing and restrained accents remain useful brand references; its hero/call-to-action proportions are marketing conventions, not review-workspace proportions.
- Read current official Primer, Geist, Carbon and Linear documents linked below through web retrieval. No signed-in vendor product was tested, and no vendor app dimensions were reverse-engineered. Browser surfaces were unavailable, so official pages were inspected as retrieved documentation rather than new live screenshots. There was no user study or measured task-time experiment.

## Primary-source findings

**GitHub Primer provides the most concrete density precedent.** Its current size tokens define medium controls at **32px**, with **6px block / 12px normal inline padding**, and separate 28/40/48px tiers. Stack spacing uses 8/16/24px; responsive control gaps distinguish fine and coarse pointers. This supports a deliberate density system rather than making every desktop control 44–48px. Our 36px search/form tier is an adaptation, not a Primer token. [Primer size tokens](https://primer.style/product/primitives/size/).

Primer's TextInput guidance explicitly varies size by context. Its form guidance favors a vertical scan path, controls sized to their expected content, related fields grouped together and progressively disclosed optional fields. Redundant helper captions should be removed. Thus a short status field should not expand like a purpose editor, and a two-column form should not be chosen only to shorten the dialog. [TextInput](https://primer.style/product/components/text-input/), [forms](https://primer.style/product/ui-patterns/forms/).

**Vercel Geist distinguishes product copy from marketing copy.** Its most common copy/label size is **14px**; 13px supports secondary or space-constrained views, 16px copy fits more spacious contexts such as modals, while 18–24px copy is largely marketing. Input guidance separates free-text search from a known-option combobox. Adopt those distinctions, without copying its proprietary component implementation or claiming Next.js supplies Geist controls. [Typography](https://vercel.com/geist/typography), [Input](https://vercel.com/geist/input).

**Carbon also supplies density tiers.** Current input specifications list **24/32/40/48px** sizes and distinct label/helper spacing; no universal 48px desktop mandate exists. Its modal guidance sizes the container to content, separates header/body/footer, keeps actions reachable while the body scrolls, and avoids horizontal modal scrolling. [Input specifications](https://www.carbondesignsystem.com/building-blocks/core/components/text-input/specifications), [modal guidelines](https://www.carbondesignsystem.com/building-blocks/core/components/modal/guidelines).

**Linear's March 2026 refresh explains the visual hierarchy.** It reduces competing navigation emphasis, excess icons/backgrounds and unnecessary separators, and makes tabs more compact. Its article supports restrained chrome and predictable action placement, not any exact pixel values in our contract. [Linear: A calmer interface for a product in motion](https://linear.app/now/behind-the-latest-design-refresh).

**An overlay should match the job.** Geist reserves a modal for a blocking decision and suggests sheets/drawers for persistent associated context. Primer documents small through extra-large dialog sizes and asks whether extra-large content belongs on a separate page. Neither supports enlarging every filter or short form to the same big modal. [Geist Modal](https://vercel.com/geist/modal), [Primer Dialog](https://primer.style/product/components/dialog/).

## Apply the contract to Ground Truth

### Workspace proportions

Replace the marketing heading with **Public - Ground Truth** at 24/30px, one short subtitle and compact inline counts. Place detailed corpus caveats/provenance behind a named disclosure; keep proposal-vs-human status visible. The header's brand must remain smaller than the case content. Keep one small calm cat with reduced-motion still/pause behavior.

Place a 36px search with a 360px preferred width beside a 32px status filter and Filters trigger. Use the rest of the toolbar for flexible whitespace and right-aligned result/queue controls, not for stretching search to 780px. Label the search accessibly; its visible prompt is simply **Search repositories**. For optical alignment, controls in the same toolbar share a horizontal centerline, icons are 16px, and text starts at a consistent inset. Do not combine a label-inside status control with an unlabelled taller search as in v2.

At 1440px, use roughly **280px queue + remaining review canvas + 380px evidence**, with 12px gaps and 24px outer gutters. The review canvas must retain at least 480px before hiding a secondary pane; long purpose text remains comfortably readable. At about 1280px available layout width, collapse evidence into a reachable side sheet rather than shrinking all three panes. Offer Queue / Review / Evidence navigation on narrow screens. These are starting constraints to verify with content, not a requirement to force columns at a nominal device width.

The review region should begin within roughly **180–200px** of the desktop viewport top, leaving substantially more working height than v2's y≈304px. There is no hero band. Use one canvas boundary with internal section spacing and restrained dividers; avoid a card inside a card for every label group. Panel titles 16/24px, repository title 20/26px, citation links 13/18px, safe plain-text evidence 14/22px. Keep hashes and raw audit JSON in provenance details.

Queue items use 12px insets, a 14px name, at most two summary lines and a 12px status line; use spacing and a pale selected row rather than many boxed tiles. Label rows begin at 36px and grow for wrapped content; 32px evidence/remove targets fit desktop, 44px coarse targets. Reviewed checkboxes stay intentional and are aligned consistently at each group heading. Retained/removed/added states remain distinguishable without relying on color alone.

Use a 56–64px decision footer with concise dirty/saved state and a stable action row: Save draft secondary, Needs evidence tertiary, Confirm & next primary. Do not repeat a second long instruction beneath the actions. Any incomplete confirmation prerequisites remain available beside the reviewed count and accessible on focus/activation. A footer must not obscure the last form field or focused control; reserve scroll padding and test zoom/virtual keyboards.

### Filters, known-label picker and review dialogs

| Job | Proposed container | Content rules |
|---|---|---|
| Routine queue filters | Anchored panel **360–400px wide**, 16px inset, max body height ~480px; mobile sheet | Vertically stack sampling/assigned domains and a searchable known proposal concept. Show applied chips outside. Immediate reversible changes; no oversized submit CTA. Preserve the current single-concept API or clearly identify future combined-facet behavior. |
| Add/restore known labels | Anchored picker **360–400px**, 36px search, 32–36px option rows | Group Project/Topic/Tag; option name primary, definition secondary on focus/selection. Stable search and selection; no giant modal or extra Add step. |
| Leave unsaved work | **400–480px** dialog | Title 18/24px; one short consequence sentence; Stay / Discard / Save & continue. Body content determines height. |
| Evidence for a new positive / focused edit | **560px** preferred, **640px maximum** | Single vertical form: known concept, saved source, quote, optional note. Source/quote can fill width. 20–24px dialog inset, 16px field-group gap, 6px label gap, 4px helper gap. |
| Genuine multi-column comparison/setup | **800px exception** only when content needs it | Explicit main editor + useful context column; otherwise use 560–640px. Long adjudication belongs in the workspace/full page. |

Dialogs have 12px radius, 1px boundary, one restrained overlay shadow, and a neutral translucent scrim without heavy backdrop blur. Header title and body fields share the same left edge; close button sits on the title centerline. Footer actions share the field's right edge, 8px gaps, 32px desktop/44px coarse targets. Keep the dialog height content-driven with a maximum of `min(80dvh, 720px)`; only the body scrolls if necessary. The title/close/footer remain reachable. Do not insert explanatory copy simply to fill whitespace or make all forms two columns.

Optical completion matters: an opened filter should clearly show its current values, selected chips, result/empty state and a closing path; a dialog should reveal the complete task and its save/cancel actions without a floating unexplained control. Dropdown width must fit or wrap long labels, remain anchored to its field and avoid clipping into the footer. Focus, keyboard navigation and return-to-trigger behavior must be visible and predictable.

### Color and border restraint

Use shared semantic tokens: ink `#24263c`, secondary text `#535a73`, canvas white, workspace/rail `#f7f8fa`, decorative line `#e4e7ec`, approved Deep Purple primary `#673ab7`, Indigo navigation/selection `#3949ab`, Blue links `#1565c0`, selected wash `#eef1fc`. Keep Light Blue focus and Purple accents specific, not simultaneous large tinted surfaces. A single primary action gets a filled brand accent; secondary actions use neutral borders/dark text. No per-section gradient, colored KPI tile or colored badge for routine metadata. This refines emphasis within the approved palette rather than replacing it.

Decorative dividers may be subtle. Input boundaries, checked states and focus need sufficient contrast: use a stronger control border/state or other clear affordance, rather than assuming a pale panel line establishes an input. Reuse previously measured dark-ink/Indigo contrast pairs and verify actual rendered states. Preserve semantic error styling and explicit error text. WCAG AA's general target minimum is 24px with defined exceptions; our 32px desktop and 44px touch tiers are task choices, not claims that AA mandates44px. [WCAG target-size minimum](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html).

## What makes the next preview reviewable

Check the complete composition at 1920, 1440, 1280, 1024 and 390px and at 200% zoom: the selected repository/evidence owns the attention; the header is calm; search is useful but subordinate; field labels/values/helpers form a consistent ladder; control text/icons line up; purpose/quote editing has enough room; actions look related and complete; no arbitrary blank bands, clipped values, excessive card outlines or nested scrolling traps appear. Large displays should add reading room, not enlarge all controls. Small displays should change composition and hit targets, not simply scale down desktop.

Compare screenshots with v2 side by side and inspect opened filters, a long label menu, focused input, add-evidence form and dirty-leave dialog—not only the default page. Record actual rendered boxes/type/overflow/focus behavior. The first preview's smoke-test results do not establish these new visual criteria or production accessibility. Preserve all original artifacts; deliver the new isolated revision before any implementation approval.

Workflow requirements from the earlier plan continue: queue → evidence → deliberate label/dimension decision → successful save → next case; unsaved changes and concurrent revisions preserve human work; immutable originals remain visible; unlisted labels remain unknown; LLM comparison is marked planned/not run until genuine independent results exist. No visual refinement weakens those rules.
