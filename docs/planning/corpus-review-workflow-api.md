# Corpus review workflow: drafts, facets and continuation

October 17, 2026. Implements the bounded local workflow extensions required by the authorized [live workspace redesign](live-workspace-redesign-2026-10-17.md).

The previous app could persist a complete review but could not save unfinished evidence, safely continue through a filtered queue, or combine a Project filter with a Topic and Tag filter. These changes use the existing authenticated FastAPI and owner-scoped SQLite aggregate. They add no service, dependency, model call or cloud resource. Frozen corpus files remain read-only.

## Incomplete work and final decisions are separate

`GET /api/v1/corpus/repos/{id}` now includes `draft: null | {...}`. The same draft is available from `GET .../{id}/draft`. `PUT .../{id}/draft` requires the normal session, Origin and CSRF checks, and accepts:

| Field | Meaning |
|---|---|
| `release_id`, `manifest_sha256` | The exact source release the reviewer opened |
| `expected_revision` | The last observed **draft** revision, initially zero |
| `base_review_revision` | The final review revision on which these edits were based, initially zero |
| `purpose`, `label_ids`, `dimensions`, `notes` | The editable buffer, including incomplete work |
| `additional_evidence` | Canonical label → `{path, quote}`; these strings may be unfinished |
| `annotation_pilot_sha256` | Optional binding to the staged independent annotation comparison |
| `status` | Intended later decision, default `NEEDS_REVIEW`; never a final review authority |

Drafts validate canonical IDs, source paths/integrity, source release, annotation context and both revision fences. They deliberately permit empty purpose, unchecked dimensions and unfinished exact quotes. Those fields stay inside `reference_drafts[release][repository]`, distinct from `reference_reviews`. Drafts never increase reviewed/confirmed counts, change review status or enter the final review export. The response includes its new `revision`, `kind: INCOMPLETE_DRAFT` and `stale`/`stale_reasons` context.

The existing final review PUT retains purpose/dimension and exact-source-quote validation. It additionally accepts `expected_draft_revision` so the live client can fence the buffer it observed. A successful final write consumes that exact draft atomically. Another tab's newer draft causes a conflict and remains intact. A legacy client that omits the draft fence leaves any draft intact; if it creates a newer final review, that old buffer becomes visibly stale.

Conflicts return HTTP 409, a readable `detail`, `code: CORPUS_REVIEW_CONFLICT | CORPUS_DRAFT_CONFLICT`, and the owner's `current_review`/`current_draft`. The frontend request error retains this payload for explicit comparison/reload. It must preserve local edits and must never automatically retry an overwrite.

## Independent filters and explicit label basis

Repository search retains its single `concept` query for compatibility and adds repeated `concept_ids`. IDs combine with **OR within a taxonomy kind and AND across kinds**. Thus two Topics allow either Topic, while adding a Tag requires that Tag as well. IDs must be distinct known Projects, Topics or Tags; assigned Domains use the separate `assigned_domain` filter and derive from Project membership.

`label_basis=proposals|reviewed` explicitly chooses which positive labels and derived Domains these facets inspect. The default remains original proposals; a saved human correction does not silently change that basis. The live redesign labels its proposal-filter basis. The sampling domain always represents corpus coverage, not an assigned taxonomy membership.

Queue items include `has_draft`/`draft_revision`; the summary includes a distinct `drafts` count. Unlisted labels remain unknown, never implied negatives.

## Safe next/previous navigation

`GET /api/v1/corpus/repos/{id}/neighbors` accepts the same search/facet/status/basis filters and returns `next`, `previous`, their zero-based indices, and the current matching total. The immutable `(case-folded full_name, repository_id)` anchor remains usable even after saving removes the current repository from a status filter.

The frontend saves first, then requests the successor and opens its page using `floor(next_index / page_size) * page_size`. It never advances on a failed final write. If the write succeeds and navigation fails, it reports that the review was saved, keeps the current saved form, and offers navigation retry without submitting the review again. End-of-queue returns null; there is no silent wrap or repeated confirmation.

## Verification

Twelve focused API tests cover incomplete persistence, final authority/count/export boundaries, restart and owner isolation, CSRF, concurrent buffers/reviews, source and exact-quote integrity, canonical/release constraints, combined facets and basis, and filtered next navigation at a page boundary and end-of-queue. They use disposable databases and synthetic source packets. The existing backend demo regressions also remain required. Actual UI checks and final results are recorded with the redesign validation report.
