# Ground Truth: create and assign validation

October 18, 2026, America/New_York. The [approved plan](../planning/ground-truth-create-and-assign.md) is implemented and loaded in the local app at `http://127.0.0.1:3000`. See the [reviewer instructions](../development/ground-truth-create-and-assign.md).

## Result and scope

Reviewers can reuse existing concepts or create missing Domains, Projects, Topics and Tags without editing the frozen corpus. Every assignment group has a searchable Add picker with a creation action. Projects also have an explicit **Create missing Project** action. A Project requires a Domain; its form can create the parent inline while preserving unfinished Project fields. A standalone Domain does not assign a repository: Domains derive from retained Projects.

Creation saves an owner-scoped reusable definition, then stages the non-Domain assignment in the review editor. It never marks a group Reviewed or confirms a reference automatically. New positives need exact saved-source quotes before confirmation; incomplete work can be saved as a draft. A persisted definition remains available if its staged assignment is later discarded. The original Agent A/B proposals remain available for comparison.

Canonical names and aliases are checked against original and new concepts within the same kind. A duplicate error identifies the conflicting term and existing concept, displays its definition and offers reuse. There is no silent merge. Concurrent vocabulary changes preserve form/review edits and require an explicit refresh before retrying. Changing vocabulary clears group acknowledgements for another inspection.

**Filters → Label filter basis → Your saved reviews** makes new saved assignments browseable by their concepts. Original proposals retain their own filter basis and counts. Drafts and unsaved changes are excluded from saved-review assignment counts.

## Persistence and API

`backend/app/demo/corpus_registry.py` combines the immutable base registry with append-only extensions in the existing SQLite workspace aggregate. Extensions are scoped by authenticated owner and corpus release, have stable IDs, creator/timestamp metadata and revision snapshots, and are separate from personal organization state. The effective registry carries a revision and SHA-256 binding. The local extension limit is 200 concepts.

| Operation | Contract |
|---|---|
| `GET /api/v1/corpus/registry` | Authenticated effective definitions and current registry context |
| `POST /api/v1/corpus/registry/concepts` | Authenticated, Origin/CSRF-protected creation; current context required; exact conflict details on HTTP 409 |
| Save draft or review | Validates effective canonical IDs, parent relationships, owner/source/revision bindings and registry context, including a second registry check inside the write transaction |
| Export reviews | Adds effective definitions, registry context and revision history alongside original saved review bodies |

Legacy records without a registry context resolve against base revision 0 and are not rewritten. Old drafts are marked stale when their bound vocabulary changes. A stale client cannot overwrite newer vocabulary or silently submit against it. Historical extension definitions remain exportable so older review IDs remain interpretable.

The database remains `docs/validation/private/demo/app.sqlite3`; the `reference_registries` section is added only when a user creates a concept. No new dependency, cloud service, model call or base-corpus migration was required.

## Verification evidence

| Check | Result |
|---|---|
| Targeted backend corpus/annotation/registry checks | **66 passed**, including 9 new registry cases |
| Full Ground Truth browser suite | **17 passed** on isolated 3015/8015 |
| Final focused creation journeys | **4 passed** after the final submission guard; these overlap the 17 cases above |
| Shared main-app searchable selectors | **4 passed** on isolated 3016/8016 |
| Frontend ESLint, TypeScript and production build | Passed; final in-app guide wording was included in the production build and checked with ESLint |
| Ruff lint/format for affected backend files | Passed |
| Git whitespace check | Passed |
| Real frontend and backend health after restart | HTTP 200 for `/` and `/health` |
| OAuth start after restart | HTTP 302 to `github.com`, configured non-fixture client |
| Test-only login route on the live app | HTTP 404 |

Backend checks cover all four concept kinds, parent validation, normalization/name/alias collisions, incomplete drafts versus confirmed evidence, owner/auth/CSRF isolation, stale creation/review/draft requests, a registry change during source validation, immutable base files, legacy records, exports and reviewed-assignment filtering.

Browser journeys create a parent Domain and Project without losing form fields; add Topic/Tag concepts; attach quotes; save/reload a draft; confirm and export; filter by the new saved Project; reuse an alias conflict; cancel without losing unsaved edits; refresh after external vocabulary changes; and complete the mobile parent/Project flow. Disposable owners are separate from earlier browser cases, preventing registry extensions from leaking between scenarios. Shared-selector cases cover keyboard commitment/cancellation, required and disabled options, and touch behavior inside a modal.

Actual [desktop/mobile screen captures](../design/workspace-refinement/create-and-assign-2026-10-18/README.md) were visually inspected. The 390px Project dialog keeps its actions visible within a bounded, scrolling modal. Test labels prefixed `QA` are synthetic inputs in disposable test databases. Their quotes test source validation, not semantic correctness or human ground-truth quality.

## Preservation and running state

The pre-change baseline covers **548 protected corpus, annotation and readiness files** and top-level state sections in **three saved workspaces**. Read-only comparison after testing and again after the live restart found **zero changed protected files, zero changed workspace sections, and no added or missing workspaces**. Original source/registry/A/B evidence and saved reviews were preserved. The local audit script and result are `.tools/audit-create-assign-preservation.py` and `.tools/create-assign-preservation-result.json`.

Automated writes used disposable test databases and isolated ports. No fixture service bound the live 3000/8000 app. The app restarted through `scripts/dev-demo.sh --live-ai`, retaining its prior mode. No model generation or AWS operation was performed for this feature. The live smoke result is `.tools/create-assign-live-smoke.json`.

Because OAuth sessions are held in memory, the backend restart may require sign-in again. Saved workspace data remains in SQLite. A new successful GitHub sign-in after this restart was not performed by the automated smoke check; the check verified the real OAuth redirect, not an end-to-end login.

## Evaluation limits and next use

These tests establish functional behavior and preservation. They do not measure label accuracy, annotator agreement or RAG quality. New human-created concepts were unavailable to the original fixed-registry annotators; report vocabulary gaps separately from missed known labels. Extensions remain local reference additions rather than automatically approved shared benchmark changes.

Use the new controls to finish corrections and attach meaningful evidence. Freeze the selected effective vocabulary and human-reviewed scope before application evaluation. Unlisted labels remain unknown; the feature does not create exhaustive negative judgements. Editing/reparenting existing definitions, cross-reviewer consolidation and a published new benchmark release remain separate work.
