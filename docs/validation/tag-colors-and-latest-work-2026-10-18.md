# Tag colors and Latest Work correction

October 18, 2026. Implementation and verification complete; local production restart health recorded below.

## Authorized scope and ownership

The user requested two independent agents: one to investigate the chip design and one to investigate missing GitHub Manager repositories in Latest Work. The design agent implemented shared label colors; the activity agent traced the missing source and corrected collection/reconciliation. The coordinating agent reviewed their changes, integrated freshness guidance, ran browser checks, and preserved the corpus, human-review and API-budget records.

## Tag-chip design

Canonical taxonomy labels now have compact rounded color chips across repository lists/details, taxonomy navigation/settings, suggestion review, and Ground Truth retained/original/derived labels and independent annotations. Twelve readable Material-inspired hues are assigned deterministically from the canonical ID, so renaming, filtering, sorting and reloading do not change a label's color. A larger taxonomy reuses the palette; colors are visual identity cues rather than confidence or review status. Label names and types remain explicit.

Every normal chip text/background pair exceeds 4.5:1 contrast; the measured minimum is 6.08:1. Active chips remain Indigo with white text, and selected repository rows retain white chip text on their Indigo selection surface. Existing compact proportions and review actions remain intact.

Actual running-app captures against disposable test data: [main workspace](../design/workspace-refinement/tag-colors/main-1440.png) and [Ground Truth](../design/workspace-refinement/tag-colors/ground-truth-1440.png).

## Latest Work diagnosis and correction

Both `nkaul/github-manager` and `nkaul/github-manager-demo` were already in the authenticated inventory. The demo had no saved personal activity, so it was excluded by the date filter. The existing collector only queried GitHub's contribution graph, omitting attributable pushes available in the user event feed. This was an activity-source gap rather than a repository-discovery or fourteen-day-window failure.

The activity agent verified actual public push events attributed to the account. Applying the implemented parser to those responses and merging into a read-only database copy in memory changed the matching fourteen-day view from one repository to two. The diagnostic did not write public replay data into the live workspace. See the [source investigation](latest-work-source-correction-2026-10-18.md) for dates, counts, official API references and limitations.

The correction combines the ninety-day contribution source with up to three hundred events from the past thirty days, requires matching actor IDs, handles sources independently, and merges retained evidence instead of replacing history with a shorter response. Another person's pushes and repository `pushed_at` do not establish personal work. Existing candidates with observed work gain Contributor eligibility; newly observed repository IDs require current accessible metadata with matching identity and a valid GitHub URL. New metadata resolution is limited to twenty candidates per sync.

Latest Work now displays last-sync time and the existing **Sync GitHub** action needed to refresh it. Upstream event availability, caps, failures and delay are disclosed. Local-only unpushed edits remain outside GitHub activity, and a ninety-day view cannot recover push events that were never observed before their upstream retention expired. Only the two named GitHub Manager repositories were verified; no third repository identity was inferred.

## Verification and preservation

- Eight corpus browser workflows passed, including three new palette/cross-view/selection/no-review-write cases. The three chip cases were repeated at the final 1440px screenshot size.
- All seventeen main-app browser regressions passed, including sync, Latest Work freshness guidance, taxonomy editing, classification/no-repeat controls, manual/bulk/drag assignments, allowance management and responsive selection/layout behavior. Together with the eight corpus cases, twenty-five browser workflows passed. The final Ground Truth image was recaptured after source/queue requests settled.
- ESLint, standalone TypeScript and the production Next.js build passed. Actual main/Ground Truth captures were visually inspected at 1440×900; mobile chips/review behavior was checked at 390px.
- The activity agent's full backend demo/GitHub regression run passed 148 cases; all thirteen focused activity cases and Ruff passed again after final query review. Source review caught an unnecessary GraphQL ordering argument whose type differed between contribution connections; it was removed to preserve the previously working contribution query.
- Read-only comparison after tests and the production restart verified all 548 protected artifact hashes and both logical application/budget databases unchanged. Production health is recorded below.

No dependency, OAuth scope, cloud resource, external model call or allowance reset was introduced. Automatic review writes use temporary databases; the public diagnostic uses an in-memory copy. Existing source corpus, independent annotation pilot, reference proposals and human-review authority are preserved.

## Using the correction

Refresh `http://127.0.0.1:3000`, sign in if the restart expired the in-memory session, click **Sync GitHub**, then open **Latest Work** with the desired activity window. This authenticated sync populates the saved workspace from the corrected sources. The real account was not silently modified by the diagnostic check.

## Local production health

The verified production build is running using the existing `scripts/dev-demo.sh --live-ai` mode. Frontend `http://127.0.0.1:3000`, backend `http://127.0.0.1:8000/health` and the actual-screen gallery `http://127.0.0.1:8132/workspace-refinement/` returned HTTP 200. Signing in again can be necessary because OAuth sessions are held in memory. Restart did not change saved reviews, corpus artifacts or the allowance ledger, and no live AI calls were made.
