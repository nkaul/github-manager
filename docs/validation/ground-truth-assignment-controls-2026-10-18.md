# Ground Truth assignment controls

October 18, 2026. Implemented and loaded in the local app. This corrects discoverability of existing assignments; creating a missing taxonomy concept remains a separate proposed extension.

The screenshot supplied by the user showed an empty Projects section without an assignment control. The previous shared picker was below all three label groups. Each group now has its own searchable **Add Project**, **Add Topic** or **Add Tag** picker beside the review control. Selected labels retain their remove action; a replacement is remove plus add. The shared bottom picker was removed.

The Domain display explains that Domains appear automatically from retained Projects. Adding/removing a Project immediately updates the displayed parent Domains. This preserves the current hierarchy and does not introduce direct repository-to-Domain assignment. **Project not listed? Add a review note** opens and focuses the existing missing-concepts notes field. It does not create a concept or confirm a review.

The group pickers search canonical names and recorded aliases. For example, `ML` finds the existing Machine Learning Topic. Each picker offers only its own taxonomy kind and excludes already selected IDs. Adding/removing a label clears the affected reviewed acknowledgement; new positive labels still require exact saved-source evidence. Existing source proposals and A/B outputs remain read-only.

## Verification

- All **13 Ground Truth suite checks passed** on isolated ports 3015/8015, including existing persistence, navigation, session, A/B, responsive and palette checks. The new browser journey starts with no Project, adds an actual retained agent proposal as disposable QA data, checks Domain derivation and evidence, saves/reloads a draft, checks alias search, removes the Project and verifies missing-note focus. Its suggested Kubernetes relationship for Flux is test input from Agent A, not a human adjudication or new semantic correctness claim.
- All **4 shared-selector browser checks passed** on isolated main-app ports 3016/8016, covering committed selection, Escape/Tab, required/disabled choices, keyboard and touch/modal behavior.
- Desktop layouts at 1920, 1440 and 1280 pixels and a 390-pixel mobile layout were checked. Actual desktop/mobile exports were visually inspected; no horizontal page overflow was observed.
- Frontend ESLint, TypeScript, production build and whitespace checks passed. No backend contract changed, and historical backend test results were not rerun or added to these counts.
- The real application restarted with its prior live-AI setting. Frontend `/` and backend `/health` returned HTTP 200; OAuth start returned HTTP 302 to GitHub using a non-fixture client, and the test-only login route returned 404. The restart may require a fresh sign-in; saved data stays in SQLite.
- All 548 protected corpus, pilot and readiness artifact hashes match the fresh baseline. Automated writes used disposable databases; the real app, corpus release, registry, independent annotations and API-budget ledger were not edited by QA. The local preservation audit is `.tools/ground-truth-assignment-controls-result.json`.

Screens: [empty Projects with picker](../design/workspace-refinement/assignment-controls-2026-10-18/empty-projects-1920.png), [assigned Project at 1920](../design/workspace-refinement/assignment-controls-2026-10-18/assigned-project-1920.png), [mobile controls](../design/workspace-refinement/assignment-controls-2026-10-18/assigned-project-390.png).

This change supports assigning existing concepts. The API still accepts only known canonical IDs from the frozen registry. Missing Domain/Project/Topic/Tag creation needs a versioned review-registry extension and cannot be simulated by editing the frozen release or creating unrelated concepts in My GitHub workspace.
