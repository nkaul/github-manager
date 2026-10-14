# Theme feedback and taxonomy conflict remediation

Date: October 13, 2026. Technical status: **PASS**. Revised visual design remains open for user feedback.

The user requested a less Deep-Purple-heavy theme, a clearly meditating/superpowered cat, consistent sync/run presentation, and actionable explanations/remediation for reserved taxonomy names. These changes implement that feedback on the approved local application.

## Revised theme

Deep Purple remains the primary action/brand color. Indigo identifies navigation/content, Blue identifies sync and links, Light Blue provides informational/progress surfaces, and Purple identifies AI/review. KPI cards have distinct, pale role-specific accents. Neutral page surfaces reduce the overall purple tint. Colors follow the [official Material UI palette](https://mui.com/material-ui/customization/color/) and [contrast guidance](https://mui.com/material-ui/customization/palette/).

The original SVG mascot now has crossed legs, mudra paws, closed eyes, a forehead light and a blue energy aura. Hover/focus adds a subtle aura effect; reduced motion disables it. It is original artwork rather than a modified GitHub logo.

Run labels now use explicit display names, including **GitHub Sync · Running**, **Full Classification**, **Completed**, **Partially Failed**, **Live AI** and **Cached AI**. Status pills no longer force uppercase. Progress uses a Light Blue panel, Indigo spinner and Blue/Indigo bar, with a readable message and accessible progress label; unknown totals use indeterminate progress. Outcome and reset labels share the display formatter. Earlier muted green progress styling is overridden.

Previews: [1920×1080 explorer](private/demo/ui-feedback-20261013/refinement-1920.png), [sync progress](private/demo/ui-feedback-20261013/feedback-sync-progress-1920.png), [meditating cat](private/demo/ui-feedback-20261013/feedback-zen-cat.png), [mobile](private/demo/ui-feedback-20261013/refinement-390.png), and [AI run setup](private/demo/ui-feedback-20261013/refinement-run-preview.png). These use clearly labeled disposable fixtures rather than the user's private repository content.

## Meaning of “already reserved”

A canonical name or alias is unique **within its concept type**, after Unicode/case/punctuation normalization. Archived concepts retain their reservations to prevent unwanted recreation. Two included draft rows can also conflict, or an alias can duplicate its own canonical name. Different types can share a term.

The user's workspace currently contains an archived Domain named **AI**. The longer name **AI - Atrificial Intelligence** is valid on its own; a Domain alias `AI` would collide with that archived reservation. The implementation does not assume which field caused an earlier attempt when its submitted values are no longer available. An automated test reproduces that exact long name plus alias against an archived `AI` Domain.

Single-concept create/edit errors now identify the incoming canonical/alias field, exact text, matching existing canonical/alias, owning concept/type and active/archived status. Structured conflict details accompany the HTTP 409 response; existing clients still receive a readable `detail` string. Concept forms offer a distinct-name suggestion or removal of the offending alias where applicable.

## Taxonomy review and user-controlled repairs

The review dialog checks included proposals locally on the server and displays every detected conflict before publication. It identifies cross-proposal duplicates and missing project parents as well as registry reservations. No model call is needed.

For each applicable conflict, the user can:

- Edit the specific field manually using the focus shortcut.
- Remove the conflicting alias, or remove conflicting aliases across the submitted draft.
- Apply a suggested distinct canonical name.
- Reuse the matching **active** concept when its meaning is equivalent, retaining its ID/metadata.
- Exclude the proposal.

Repairs update submitted form values only and retain supporting repository examples while editing. **Undo last repair** restores the previous local form. Save draft persists reviewed edits without publishing; Approve & publish taxonomy remains the explicit live-taxon action. A failed check/publication leaves live state unchanged. Archived concepts cannot be silently restored or reused, and their reservations are not released by repairs. Reusing/renaming a Domain rewrites dependent draft project parent references. Excluding a parent exposes any remaining missing-parent conflicts rather than inventing replacements.

Exact canonical reuse retains the earlier publication behavior but is now disclosed in the review panel: existing aliases/descriptions remain unchanged. New aliases are not silently installed on an existing concept. User-directed reuse is an equivalence decision, not an automatic semantic merge.

Implementation: `domain.py` supplies detailed shared term validation; `taxonomy_review.py` performs pure checks/repairs and shared publication validation. New authenticated, owner/collection-scoped, Origin/CSRF-protected local routes are `POST /taxonomy/drafts/check` and `POST /taxonomy/drafts/remediate`. They validate the draft revision/fence and return proposed values without writing live taxonomy. Publication rechecks inside its existing app SQLite write transaction. Stale/tampered conflict actions are rejected. No cloud architecture, GitHub write operation, model/budget change or live user-data repair was added.

Previews: [conflict details and choices](private/demo/ui-feedback-20261013/feedback-taxonomy-conflicts-1920.png) and [repaired form awaiting approval](private/demo/ui-feedback-20261013/feedback-taxonomy-repaired-1920.png).

## Verification and preservation

| Check | Result |
|---|---|
| Full backend suite | **142 passed**, 9.82s; nine new taxonomy-review cases. |
| Full product browser suite | **10 passed**, 52.9s; includes two new theme/remediation workflows. |
| Final focused browser rerun | **2 passed**, 17.9s after presentation cleanup; final evidence-preservation workflow **1 passed**, 15.1s. |
| Historical preflight browser suite | **4 passed**, 6.2s without modifying the preflight UI. |
| Static/build/runtime | **PASS**: Ruff, TypeScript, ESLint and production build. Restarted frontend/health return 200, anonymous identity returns 401, OAuth is configured, and the rendered sign-in screen has no page errors. |
| Layout/contrast | No document overflow at 1920×1080, 1440×900, 1280×800 or 390×844. Tested desktop text pairs have minimum 5.33:1 contrast, including the conservative tinted end of KPI gradients. KPI labels are 13px; card heights 84–90.6px. |
| Earlier evidence | Preservation verifier passes: 163 protected files, 34 original call rows, 29 original cache rows, original experiment and identical preflight copy. Eight original demo artifacts match their SHA-256 manifest. Earlier UI previews/report remain available unchanged. |

New backend coverage includes the reported long-name/archived-alias example, multiple simultaneous conflicts, no mutation during checks/repairs, atomic failed publication, alias cleanup, stable-ID reuse, domain-reference rewrite, unique rename, Unicode/punctuation duplicates, cross-type allowance, missing parents, owner/collection/CSRF/revision/fence checks and stale/tampered repair rejection. Browser coverage includes manual focus, repair, undo, saved draft, explicit publication, preserved archived status, progress labels/colors, five distinct KPI roles and reduced-motion mascot behavior.

Diagnostics and screenshots are in `docs/validation/private/demo/ui-feedback-20261013/`. Validation uses disposable app/ledger fixtures. No paid AI calls were issued for this revision; no normal workspace concept/draft was repaired, archived, reset or published by the agent. User action remains required to resolve their own draft.

Local app: **http://127.0.0.1:3000**. A backend restart requires sign-in again. Follow the [current runbook](../development/phase-0-9-demo-runbook.md); the original video/audio is preserved and still shows the previous layout.
