# Ground Truth review UI: implementation impact and acceptance

Status: design/planning only, 2026-10-17. Production implementation requires approval. The isolated [interactive preview](../design/ground-truth-review-v2/preview.html) is a review artifact, not application code. It reads no corpus files and calls no API. Public repository examples, labels, citations, source excerpts, revisions and review outcomes are illustrative. It writes nothing to SQLite, GitHub or browser storage.

Related: [workspace contract](public-ground-truth-workspace.md), [UX research](ground-truth-ux-research.md). The Phase 0.9 local corpus continues to use its existing owner-scoped SQLite review store; this proposal does not replace the approved cloud architecture or modify the frozen release, taxonomy, sources or historical benchmarks.

## What changes for the reviewer

- A compact, independently scrolling queue, a central decision canvas and an adjacent evidence pane replace the long browser-then-dossier page. The selected repository is visible without scrolling past 25 records.
- One generous search field, status selector and Filters button replace the seven squeezed columns. Secondary filters remain available in a dialog. Every filter has an explicit label, selected state and clear control.
- Projects, Topics and Tags have visible retained labels, source actions and deliberate reviewed checkboxes beside each group. Empty groups are reviewable. Opening a group, viewing a quote or accepting an agent proposal never marks it reviewed.
- Searchable grouped checkboxes add/restore known labels immediately to the editable draft; there is no separate Add action. Removing a label remains explicit and reversible. Editing a group clears that group's reviewed flag; purpose changes require the user to check meaning again before confirmation.
- The sticky action bar offers **Save draft**, **Needs evidence**, **Confirm & next**. Confirm & next is disabled until purpose, explicit group checks and additional-evidence requirements are satisfied. No dropdown navigation is needed for the common confirmation path.
- At narrow widths, Queue / Review / Evidence tabs progressively disclose the same state. The decision actions stay accessible. Source text wraps and the page has no horizontal overflow.

The proposed Material component system is MUI Core, with one shared theme and demo-like indigo, pale blue and neutral surfaces. Validate its exact App Router integration against the installed Next 16.4 / React 19.3 lock before selecting package versions or an `@mui/material-nextjs` adapter subpath. No packages were installed for this preview. The preview uses ordinary HTML/CSS with approximately 44–48px main controls, a 16px root, larger headings, and dark supporting text; it is a visual/control-sizing target, not a production accessibility certification.

## Confirmed code gaps and their consequences

| Existing behavior | Consequence | Proposed resolution |
|---|---|---|
| `globals.css` applies `main { width: calc(100% - 246px) }`; `.corpus-main` resets margin/padding but not width | The corpus inherits a sidebar allowance despite having no ordinary sidebar | Explicitly scope/reset the corpus root width and audit other generic `main`, `aside`, `header`, button and form rules. Keep tokens scoped to this workspace. |
| `CorpusWorkspace.tsx` and `Corpus.search()` share one `concept` value | Project, Topic and Tag cannot be combined; choosing one silently replaces another | Add validated repeated concept IDs. OR within each kind; AND across selected kinds. Sampling domain, assigned domain, status and text search combine with AND. Default facets operate on immutable supported proposals; label the basis **Original proposals**. A future **My decisions** basis needs its own explicit API contract. |
| The current monolith appends the dossier below the full paginated list | Frequent jumps and loss of queue context | Split queue, editor, evidence and action bar; keep selected numeric ID, filters and scroll positions distinct. |
| `inspect()` clears detail and overwrites local fields; close/workspace/sign-out have no dirty guard | Drafts can disappear during navigation | Central draft state, explicit leave guard and a separate persistent draft contract; never infer confirmation from navigation. |
| Detail/source requests have no active repository/path generation check | A slow response can replace the currently selected record/source | Cancel stale requests and check repository ID + source path + request generation before committing state. Prevent actions during loading; keep loading/error independent per pane. |
| `save_review()` requires exact source evidence for added labels even for `NEEDS_REVIEW`/`UNRESOLVED` | Calling the existing review PUT cannot save an incomplete label draft | Add owner/release/repository-scoped draft storage separately from final review records. Preserve strict final review validation. Do not advertise existing `NEEDS_REVIEW` save as an incomplete draft. |
| Revision and release mismatch currently use `ValueError` with a generic message | The frontend cannot reliably distinguish a recoverable conflict from validation or tampering | Structured conflict/error codes and explicit recovery UI. Do not parse English error strings or silently retry an overwrite. |
| PUT success and summary refresh share one `try` block | A failed GET can make a successful write look unsuccessful | Commit the returned review and revision immediately after PUT; if refresh fails say “Review saved; queue refresh failed.” Retry only the refresh. |
| List API uses offset pagination and immutable alphabetic sorting | Saving an item can remove it from a status filter and shift later offsets | Capture next numeric ID before save, advance only after PUT succeeds, and introduce filter-bound queue snapshot/seek-neighbor support for page boundaries. |
| Generic `unknown[]` audit types and an unstructured JSON block | Reading scope, citations and cross-review are difficult to scan safely | Typed view models for audit/citation provenance with explicit unknown/missing states; keep raw details available secondarily. |

## Draft, save and conflict contracts

1. **Memory buffer:** scope to authenticated reviewer + release ID + manifest hash + numeric repository ID + pinned source commit + base review revision. Purpose, retained IDs, dimension checks, notes and partial evidence belong to that buffer. No raw source content, session/auth secrets or personal data in browser storage. The browser unload prompt is only a fallback; in-app navigation must offer Keep reviewing / Discard changes / Save & continue.
2. **Explicit Save draft:** propose `PUT /api/v1/corpus/repos/{id}/draft` and `GET`/`DELETE` companion operations, or equivalent detail read integration. Store separate `reference_drafts` with `draft_revision`, `base_review_revision`, release/manifest/commit/proposal bindings, actor, updated time and incomplete content. Check ownership, CSRF, supported registry IDs, bounds and optimistic draft revision. Permit unfinished purpose and evidence; the draft is never a human review, never increments confirmation/review metrics and never weakens `CorpusReview` citation rules. Detail should return both saved review and draft, with a visible recovery choice if their bases differ.
3. **Final review:** existing review PUT remains the single atomic decision/history write. Confirm & next submits `HUMAN_CONFIRMED` only from explicit user intent, with deliberate Projects/Topics/Tags flags, purpose and exact saved-source evidence for new positives. Needs evidence maps to `UNRESOLVED`; its final payload still meets the added-label citation rule. For incomplete new evidence, Save draft remains available.
4. **Revision conflict:** return HTTP 409 with `code: REVIEW_REVISION_CONFLICT`, expected/current revisions and a safe latest-review representation. Keep the user's draft and focus. Offer compare, reload latest with explicit discard, or reapply selected edits onto the latest base; show the diff before a fresh explicit save. Reapply does not automatically confirm. A draft revision conflict follows the same pattern.
5. **Integrity mismatch:** structured release/source/proposal mismatch blocks confirmation and identifies the changed binding. Preserve editable work for comparison; do not automatically migrate quotes to a new source snapshot. Unknown exact quotes are validation errors with label IDs and field paths.
6. **Partial success:** after PUT success adopt returned revision before any secondary requests. Keep write and refresh outcomes distinct. Confirm & next must not repeat a successful PUT because summary/queue loading failed.
7. **Queue continuation:** capture immutable next ID using the pre-save queue view, including across a server page. Seek/filter tokens bind release, normalized filters, label basis, ordering and tie-break numeric ID. Never derive the next item from a post-save offset that may have shifted. End-of-queue, empty matches, loading and retry states must be visible; no automatic bulk confirmation.

## Source and annotation rules

- Render saved README/supporting documents as React text children (`<pre>`/line spans), never `dangerouslySetInnerHTML`, evaluated Markdown, active HTML or interpreted source instructions. Safe highlighting operates on text offsets; line numbers are navigation aids and cannot replace the exact quote.
- A citation includes input channel, saved path/metadata field, exact excerpt, available line range, source hash, pinned commit, release/manifest and proposal identity. **GitHub metadata** is visibly distinct from a saved-document quote; metadata-only evidence does not create a fake source link.
- Retained labels are the user's editable layer. Keep immutable proposal IDs/decisions, rationale, independent audit and source references inspectable. Removed/absent labels remain unknown, not negative. Restore uses the original supported-label evidence rules.
- Registry search covers names, descriptions and approved aliases when the API supplies them. Add-only known IDs in this phase; request missing concepts through notes. Domains derive from Projects and are not manually retained label IDs.
- Default is current proposals only. Future Agent / LLM comparison requires independently run, version-bound provenance and a separately approved pilot. “Not run” is distinct from a missing result, zero confidence or agreement. No invented model scores and no inference or paid calls from the review UI.

## Component/file work breakdown after approval

| File/module | Responsibility | Impact |
|---|---|---|
| `frontend/src/components/workspace/CorpusWorkspace.tsx` | Workspace coordinator, filters/selected ID, pane composition, dirty-navigation guard | Refactor the current client entry point; preserve identity and collection boundary. |
| Proposed `workspace/corpus/CorpusToolbar.tsx`, `CorpusFilterDialog.tsx`, `CorpusQueue.tsx` | Sized search, searchable multi-facets, selected chips, loading/empty/error/page/next behavior | New small components with explicit keyboard labels. |
| Proposed `workspace/corpus/ReviewCanvas.tsx`, `LabelGroup.tsx`, `KnownLabelPicker.tsx`, `ReviewActionBar.tsx` | Purpose, retained labels, intentional checks, evidence attachment and save actions | Separate presentation from review state; no automatic confirmation. |
| Proposed `workspace/corpus/EvidencePane.tsx`, `CitationCard.tsx`, `ReviewHistory.tsx`, `ReviewConflictDialog.tsx` | Plain-text sources, provenance, audit history and recovery | Typed document vs metadata evidence; safe highlighting and focus restoration. |
| Proposed `workspace/corpus/useCorpusReview.ts`, `frontend/src/lib/corpus.ts` | Typed DTOs, memory draft reducer, request generation guards, save sequencing, structured errors | Reuse existing same-origin `request`/CSRF behavior; avoid unrelated auth rewrite. |
| `frontend/src/components/workspace/corpus.css`, scoped theme/provider | Responsive pane layout, readable tokens, focused controls | Reset inherited corpus width; avoid leaking changes into personal workspace. |
| `backend/app/demo/corpus.py`, `backend/app/local.py`, existing store helper as needed | Multi-facet validation/search, draft storage, seek-neighbor reads, structured conflicts | Owner-scoped additive API; no change to immutable release or final review semantics. |
| `backend/tests/demo/test_corpus.py` and `frontend/tests/corpus/workspace.spec.ts` | Contract/security/persistence plus meaningful UI task checks | Use disposable identity/database on 3015/8015. Never QA-confirm the user's real records. |

The bundled Next guides reviewed were Server and Client Components, `use client`, and CSS. Keep browser state/handlers within the existing client boundary; pass serializable data across server boundaries. Do not add an obsolete Pages Router wrapper. Validate the chosen MUI integration against the bundled Next docs and lockfile during the approved compatibility spike.

## Acceptance and click budget

Click counts exclude reading, typing and any evidence inspection the reviewer needs. They are interaction targets, not permission to skip semantic review.

| Task from selected record | Target |
|---|---|
| Confirm an unchanged supported record after reading | 3 group checks + 1 Confirm & next = **4**; no decision dropdown and next record opens only after success |
| Select any queue record | **1** click, no page scroll to find the editor |
| Inspect evidence for a retained label | **1** click to focus the adjacent source/citation; mobile **1** click switches to Evidence |
| Save an incomplete draft | **1** click; no confirmation increment |
| Mark a complete payload unresolved | **1** Needs evidence action; a reason is encouraged, not fabricated |
| Add/restore a known label | Open picker + checkbox + Done = **3**; repeat selection within the open multiselect, no separate Add button |
| Attach already selected exact text to a new label | **1** explicit attach action; actual selection/reading excluded, new evidence remains reviewable |
| Navigate away while dirty | **1** destination + **1** explicit Stay / Discard / Save & continue choice |

Required browser checks: 1920×1080, 1440×900, 1024×768, 390×844 and zoom/reflow; readable long names; no horizontal document overflow; 44px primary controls; keyboard search/pickers/dialogs/tabs; Escape and focus return; visible focus; screen-reader group names and live save errors; no reliance on color alone. Contrast pairs should meet WCAG AA; automated checks supplement manual task QA.

Required behavior checks: combined facet semantics, reset and preserved selected chips; original-proposal basis remains stable after human edits; same-record source race and cross-record detail race; dirty leave and incomplete draft reload; successful save followed by failed GET; 409 conflict/reapply; invalid quote/integrity mismatch; per-user isolation; SQLite restart persistence; next across page boundary when current item leaves active filter; empty/end-of-queue; export of final reviews remains explicit and drafts are separately identified. No live app writes are required to validate the design prototype.

## Preview validation and limitations

Initial desktop screenshots are [1920×1080](../design/ground-truth-review-v2/desktop-1920.png) and [1440×900](../design/ground-truth-review-v2/desktop-1440.png). The central canvas and evidence panel intentionally scroll independently on desktop; the action bar stays visible. Mobile sections use tabs. The prototype demonstrates in-memory incomplete drafts, a dirty-navigation guard, explicit confirmation, multiselect filters and metadata/document distinction. The separate draft/combined-facet/seek-neighbor backend capabilities are **planned**, not existing functionality. It cannot demonstrate durable persistence, server concurrency, source integrity, OAuth or real corpus correctness.

Prototype smoke checks passed: search, searchable Topic+Tag combined facets, unchecked confirmation gate, dirty navigation/Keep reviewing, incomplete new-label draft save/restore without confirmation, explicit confirmation then next with clear group checks, metadata channel/plain-text safety, and no horizontal overflow at 1920×1080, 1440×900, 1024×768, 390×844. Zero browser page/console errors and zero HTTP/API requests. Evidence: [prototype-checks.json](../design/ground-truth-review-v2/prototype-checks.json), [mobile screenshot](../design/ground-truth-review-v2/mobile-390.png), [filter dialog](../design/ground-truth-review-v2/filters-desktop.png). The existing Zen Cat poster is reused unchanged in the preview. These checks validate the design artifact only.
