# Ground Truth: create missing concepts and assign them

October 18, 2026. **Approved and implemented.** See the [current user guide](../development/ground-truth-create-and-assign.md) and [creation-flow validation report](../validation/ground-truth-create-and-assign-2026-10-18.md). Existing-concept assignment controls were implemented separately in [the earlier assignment-control verification](../validation/ground-truth-assignment-controls-2026-10-18.md); that dated report describes the controls before this extension.

## Problem and intended behavior

The current Ground Truth review can add/remove existing Projects, Topics and Tags, but cannot create missing concepts. Domains derive from selected Projects. The immutable corpus registry contains proposed reference definitions, not a human-approved universal vocabulary. Human review must be able to discover gaps without editing that manifest-bound evidence in place or forcing an unsuitable existing label.

Add an explicit **Create and assign** path inside each label picker and a **Create Domain** action beside the derived-Domain display. Existing concepts remain searchable and reusable. The creation form asks for name, definition and optional aliases; Projects additionally require one parent Domain. Show matching canonical names/aliases and possible similar concepts before creating a new ID. Conflicts identify the existing concept and conflicting term, with reuse/correction choices; no silent merge or LLM call.

| Missing concept | Review workflow |
|---|---|
| Domain | Create its name/definition, then use it as a Project's parent. Creating a Domain alone does not assign the repository. |
| Project | Create its name/definition, choose an existing or newly created Domain, then stage the Project on the repository. |
| Topic | Create its reusable capability/subject definition and stage it on the repository. |
| Tag | Create its technology/property definition and stage it on the repository. |

Creating a parent Domain from the Project form must retain unfinished Project fields. Use one coherent form flow, rather than stacked dialogs. Stage the resulting assignment in the editable review; do not check Reviewed boxes or confirm a reference automatically. A new positive assignment still needs an exact saved-source quote before final confirmation. Incomplete work can be saved as a draft.

This preserves [the current Domain → Project → repositories model](../system-design.md#22-taxonomy-semantics). Direct repository-to-Domain assignment would be a separate policy change and is not included. Likewise, changing an existing Project's parent affects other reviewed repositories and needs an explicit impact-preview workflow; it must not be hidden inside this creation feature.

## Persistence and reference versions

Preserve the base corpus release, registry, source hashes, original proposals and A/B annotations. Store user-approved additions in a persistent, owner-scoped Ground Truth registry extension in the existing SQLite workspace aggregate, separate from personal GitHub organization state. This remains a local feature; it adds no shared workspace, cloud service or provider call.

Use stable new concept IDs and version/hash the effective registry formed from the base plus extensions. Creation approval makes a concept available locally; it does not silently promote a new shared benchmark registry or modify the other 599 repositories. Cross-reviewer consolidation and publishing a later reference release remain explicit operations.

New drafts/reviews/export records bind the effective registry version as well as the existing release, repository, source/proposal and revision bindings. Legacy records without an extension binding resolve against the original base registry. Preserve definition snapshots/history so old reviews remain intelligible. Concurrent registry/review changes must fail with a visible conflict while keeping the editor's unsaved work.

Validate canonical/alias uniqueness within each kind across base and extension concepts, valid active Domain parents, canonical IDs, owner isolation, Origin/CSRF, source evidence and optimistic revision checks. Reuse or extract pure normalization/conflict validation from the main application's taxonomy code; do not route Ground Truth writes into the personal organization controller or start AI jobs.

## Bounded implementation sequence

1. Add a corpus-registry adapter/DTOs and additive API reads/creation under `/api/v1/corpus/registry`; return effective definitions and their version/hash.
2. Extend corpus draft/review validation and export to bind the effective registry, retaining base-only compatibility and exact-source evidence rules.
3. Add the reusable creation form, picker creation actions, parent-Domain flow, duplicate remediation and clear staged-versus-saved feedback.
4. Verify isolated API/browser flows and publish a dated Markdown validation report. Update the human-review guide to distinguish base-only agent proposals from human-created concepts.

Implemented touchpoints: `backend/app/demo/corpus.py`, `backend/app/demo/corpus_registry.py`, `backend/app/local.py`, `frontend/src/components/workspace/CorpusWorkspace.tsx`, `CorpusConceptDialog.tsx`, shared searchable-select options and isolated corpus tests. No dependency installation or data migration was required; existing JSON workspace records gain additive versioned sections/fields when the user saves new work.

## Acceptance gates

- Create a missing Domain and Project, stage the Project, attach source evidence, save/reload/export, and observe the derived Domain.
- Create and assign a missing Topic and Tag; preserve multiple associations and explicit review acknowledgements.
- Reuse a name/alias match or correct a conflict without creating duplicate IDs. Cancellation preserves the existing editor.
- New assignments without evidence cannot become confirmed; drafts remain separate and unknown labels are not silently converted to negatives.
- Different users cannot read/write each other's extensions; concurrent edits and stale registry bindings are handled explicitly.
- Existing base-only reviews, frozen source/registry/A/B files, personal workspaces and budget ledgers remain preserved.
- Validate desktop/mobile controls on isolated ports 3015/8015; no fixture service touches the live 3000/8000 app.

## Evaluation consequence

A human-created concept was unavailable to the original fixed-registry A/B readers. Preserve that distinction in scoring: report a registry-gap discovery separately from a missed known label. Do not retroactively score old predictions against an expanded vocabulary as though the vocabulary had been unchanged. Freeze the selected effective registry and reviewed scope before the corresponding application evaluation.
