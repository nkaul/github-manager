# Public - Ground Truth: corpus cleanup and local review

Status: implementation authorized by the request to complete the English corpus through two agents and expose it as a new app workspace. This is an additive Phase 0.9 local feature, not a cloud architecture replacement.

**October 17 annotation update:** the user separately authorized a thirty-repository development pilot using two independent Codex agents, without additional provider API calls. A validated sidecar now supplies comparison data and a human-review queue to this workspace. Original proposals and owner-scoped human reviews stay separate. See the [execution record](agent-annotation-pilot-execution.md) and [validation report](../validation/agent-annotation-pilot-2026-10-17.md). The historical initial-interface description below predates this addition.

## Behavior and boundaries

The workspace selector gains `Public - Ground Truth`. It opens a dedicated corpus browser, not the personal GitHub organizer. An English/relevance-screened 600-repository release supplies versioned inventory, proposed taxonomy, proposed labels and pinned source evidence. Search and four taxonomy facets help reviewers locate cases; sampling Domain and derived Domain remain distinct. A dossier shows purpose, eligibility, proposals, citations, README/supporting documents and read-scope limits. Reviewers can confirm, correct or leave unresolved; unlisted labels remain unknown, not negative.

The initial review interface supports per-repository review, known-label corrections, explicit evidence for newly added labels, purpose edits, dimension-completeness checkboxes and notes. Confirmation requires reviewing Projects, Topics and Tags and a substantive purpose. Original proposals remain visible. It does not invent LLM confidence, automatically approve 600 labels, run paid inference, or activate the app's ordinary classification/sync/reset controls against the corpus. A later co-annotation pass can add independent agent/LLM proposals without replacing human decisions.

## Data ownership and persistence

Immutable evidence and release files live in ignored `docs/validation/private/corpus-600-v2/`. The manifest binds the inventory, registry, label file and dossiers; each saved source binds its own SHA-256 and Git commit. Reused v1 source references are read-only. Backend access uses fixed release paths, manifest-bound dossier paths and an allowlist of the two corpus source roots. Source files are displayed as escaped plain text, including untrusted Markdown/HTML/instructions.

Human records live in the existing configured local SQLite database, default `docs/validation/private/demo/app.sqlite3`, under workspace `<GitHub user ID>:ground-truth`. Each review binds release ID, manifest hash, repository ID, source commit and proposal digest. Updates use optimistic per-repository revisions and append prior decisions to history. The review export includes that user's records. It contains no OAuth secrets. Personal GitHub and sample organization state, receipts and budgets are untouched.

## Validation gates

- Exactly 600 public numeric IDs, 60 per sampling domain; no duplicate identity, full retained language/relevance decisions, pinned sources and exact citations.
- Separate aggregate counts for screening, semantic reading, proposed/cross-reviewed/human-confirmed labels; report remaining family/Topic and split gaps.
- Existing release hashes remain unchanged. No paid model calls or GitHub writes.
- API tests cover authentication, CSRF, owner isolation, manifest/source tampering, invalid labels/evidence, concurrent edits and SQLite restart persistence.
- Browser checks cover selecting the workspace, facets, source display, review/save/reload and safe return to personal workspace. Frontend typecheck/lint and relevant backend regression checks pass.

## Next phase

After cleanup, use the agreed 30-repository pilot for independent agent/LLM/human co-annotation. Freeze taxonomy and a reviewed benchmark only after adjudication and random audits of high-agreement cases. The corpus browser is a review surface, not proof that proposals are gold.

## How to review in the app

1. Start the local app with `scripts/dev-demo.sh --production`, open `http://127.0.0.1:3000`, and sign in through the existing GitHub OAuth App. The corpus uses saved public snapshots; login identifies the owner of the review records.
2. Choose **Public - Ground Truth** in the header's Workspace selector. Opening it creates a local SQLite workspace reference for your numeric GitHub ID. It does not sync these public repositories into My Repos.
3. Filter by **Sampling domain** to inspect the balanced collection, or **Assigned domain** to inspect Domains derived from supported Project proposals. Project, Topic and Tag menus browse proposed memberships. One of those three label facets is active at a time. Facets intentionally show immutable proposals; edits remain visible as your separate review.
4. Choose **Review evidence**. The page scrolls to the dossier. Expand proposed labels to see definitions, rationale and exact quotes; select a saved README or supporting document in the source pane. Expand the eligibility/independent-audit section for reading scope and peer findings. Full source retention does not mean every byte was semantically read.
5. Keep or remove candidate labels. Add or restore a known label through the menu. A newly introduced positive needs an exact quote from a saved source; the server validates quote containment and source integrity. Use review notes to request a missing taxonomy concept rather than forcing an unrelated label.
6. Review Projects, Topics and Tags, then choose **Human confirmed**, **Needs review**, or **Unresolved / missing concept** and save. Confirmation requires a purpose and all three reviewed dimensions. Saving another revision preserves the prior decision. Original proposals, citations and files remain intact.
7. Use **Review status** to find disputed or unfinished records; use **Export my reviews** for your version-bound JSON decisions/history. Reloading or restarting the backend preserves saved decisions. Different GitHub logins have separate review records.

The immutable dataset contains no human-confirmed labels until actual reviewers save decisions. Legacy words such as `HIGH` in inherited agent annotations are uncalibrated descriptions; they are not probabilities or permission to auto-accept. The later co-annotation confidence policy must be calibrated against independent human audits.

Offline alternatives are `release/inventory.csv`, `release/human-review/README.md` and a copy of `release/human-review-decisions.template.json` under the v2 private data folder. Do not edit the frozen release in place. Offline decision files are not automatically imported into app review state; use the app to save persistent per-user decisions, or define a separately validated import in the subsequent phase.

For isolated browser QA, use `playwright.corpus.config.ts`. It uses ports 3015/8015, a disposable identity/SQLite database, the real frozen corpus and a separate `.next-corpus` build directory. Test confirmations never enter the real user's SQLite review records.
