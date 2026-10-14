# Phase 0.9 — Local acceptance and demo test order

> October 13 taxonomy/status update: use **Browse taxonomy → Projects / Topics / Tags**, and **No project** in place of Uncategorized. Repeating classification reconciles recorded analysis offline. For intentional fresh taxonomy/classification inference, use Live AI → Re-analyze with AI → reason → preview → Start reviewed run. Automatic organization has configurable thresholds and never clears prior-analysis receipts. See the [current runbook](phase-0-9-demo-runbook.md) and [validation report](../validation/phase-0-9-taxonomy-and-analysis.md). The steps and original recording below also preserve the earlier demonstration context.


Readiness snapshot: October 12, 2026. **Ready for local use and operator acceptance.** The frontend returned HTTP 200 and the backend returned `{"status":"ok","phase":"0.9","storage":"local"}` during this readiness check. The complete automated suite previously passed: 111 backend tests, four original browser tests and four product browser tests. The separate real OpenAI integration and zero-call reset/replay checks passed. See the [validation results](../validation/phase-0-9-results.md).

At the initial readiness snapshot, a fresh real GitHub login, inventory sync and activity observation in the finished product UI still needed confirmation. Those checks have now been recorded, as described below. The manual rows remain intentionally unmarked for your own follow-along session.

**Subsequent recorded acceptance:** the [narrated walkthrough](../../demo-video.md) now contains the real authenticated GitHub checks plus the complete isolated sample workflow; 35 recorded checks passed. Both named private fixtures were found through global exact-name lookups. The personal checklist rows below remain unmarked for your own follow-along session. The fixed allowance is now 20/20 HTTP requests used, with no remaining fresh calls; the earlier 8/20 snapshot and fresh-call rehearsal instructions below are historical. Use cached AI/manual/rules for repetition until any additional allowance is explicitly approved.

## Before starting

**Subsequent allowance renewal:** the user requested continued testing and selective overrides. A fresh 20-HTTP / 10-generation window is granted, with lifetime usage preserved. Use **AI Organization → Manage API allowance** to inspect current counters and change selected limits; see the [allowance guide](ai-allowance.md). This supersedes the exhausted-window instructions above while retaining the original snapshots.

- Open **http://127.0.0.1:3000**. The app was already running at this snapshot. If it has stopped, run `bash scripts/dev-demo.sh --live-ai` from the repository root. Run only one backend instance.
- Keep **Automatic organization after significant edits** off until its dedicated test. Wait for each run to finish before changing taxonomy or making another run.
- Use **My GitHub workspace** for real access/exploration checks. Use **Public + synthetic demo** for AI, taxonomy experiments and every reset test. Sample changes do not change your GitHub collection.
- Check current counters in AI Organization before Live AI. At the October 13 canary, estimated cumulative usage is **$0.103264/$5**, with zero unresolved reservations/holds. The fixed HTTP window is exhausted; **Adaptive cost budget** can admit a reviewed run within its dollar maximum (default $0.25). One fresh generation normally uses two HTTP requests. The earlier video and reports retain their historical snapshots.
- Cached replay, extraction, manual changes and Rules only do not make new OpenAI requests. A cache miss is an explicit error; it does not fall back to paid inference. No private repository content is authorized for model inputs.

## Run in this order

Record PASS, FAIL or NOT RUN for each row, including a short note for any mismatch. A visible upstream partial/unavailable result must be recorded as such rather than treated as proof of complete access.

| Order | Test and actions | Expected result | Operator result |
|---|---|---|---|
| 1 | **Real sign-in.** Continue with GitHub using the existing OAuth App. | Your account appears; the connected workspace opens without exposing credentials. | NOT RUN |
| 2 | **Real inventory.** Sync GitHub and wait for its terminal status. Search for `avimla` and `workshops` under My Repos and Access candidates; check the owner and visibility on the actual matches. | Accessible expected repositories appear. Access-only candidates can be explicitly included in My Repos. Source coverage and any partial failures are visible. A missing expected fixture remains an access issue to investigate. | NOT RUN |
| 3 | **Explorer and real activity.** Check My Repos, Favorites, Access candidates and Uncategorized; search, language/visibility filters, pagination and repository details/links. Check Latest Work at 7/14/30/90 days. | Views reflect their own relationships. Private metadata can be browsed locally, with private AI evidence blocked. Latest Work shows your dated contributions or an honest empty/partial/unavailable result; it is bounded, not an exhaustive activity log. | NOT RUN |
| 4 | **Isolated sample collection and extraction.** Switch to Public + synthetic demo and load the three samples. In AI Organization, preview Extract evidence, inspect the cohort, click Start reviewed run, then inspect details. | FastAPI and the two synthetic Orion examples appear separately from your GitHub inventory. Phrases, evidence and extractor version appear. Synthetic data/activity is labeled; extraction spends zero OpenAI requests. | NOT RUN |
| 5 | **Taxonomy discovery and review.** Use Reuse validated cached AI, set automatic Taxonomy sample size to 3, preview Discover taxonomy, inspect the exact three chosen samples and click Start reviewed run. Review/edit/select the draft and approve publication. | Validated cached output is labeled REPLAY. Nothing is published before approval. Published domains/projects/topics/tags become navigable; publication changes the taxonomy revision without paid classification. | NOT RUN |
| 6 | **One fresh AI classification.** Choose Live AI, automatic Classification batch size 3 and Adaptive cost budget ($0.25). Preview Full classification, check the chosen cohort/cost, then Start reviewed run once. Manual selection remains an alternative. Inspect evidence/reasons; accept one useful project suggestion and reject another. | Persisted progress/outcomes and suggestions appear. Accepted assignments become USER decisions; rejected assignments stay protected. Suggestions alone do not organize a repository. Normally uses at most six HTTP slots for three repositories. | NOT RUN |
| 7 | **Manual organization and taxonomy management.** Bulk-assign samples, drag one onto an additional project, then remove just one membership. In Content settings, create/edit/rename concepts and aliases, change a project domain, merge temporary concepts and archive a temporary domain. Try a conflicting alias. | Multiple memberships work and removal preserves the others. Rename retains the concept ID. Merge retains the target; domain archive reparents surviving projects to Unassigned. Invalid duplicates show a clear error without partial changes. No model calls. | NOT RUN |
| 8 | **Rules and both reorganization controls.** Create a simple name/language rule, preview its matches and approve it. Use Rules only to preview/start Reorganize incremental, then Full classification. Use cached Rediscover taxonomy and leave that proposal unpublished or reject it. | Preview matches are inspectable; rules apply locally while USER decisions/rejections win. Runs and outcomes persist. Both classification modes use the current taxonomy; the local incremental mode currently visits its selected cohort. Rediscovery does not replace published content automatically. No new model calls. | NOT RUN |
| 9 | **Automatic organization, if wanted in the acceptance rehearsal.** Follow the separate procedure below. | One delayed run appears with AUTO provenance and honors existing manual decisions. No repeated loop. | NOT RUN |
| 10 | **Continuity.** Reload the browser; log out and back in. If testing process recovery, stop/restart the launcher and sign in again. | Inventory, taxonomy, mappings and completed run history persist. A backend restart requires login because credentials stay in memory. Interrupted paid work is disclosed rather than silently repeated. | NOT RUN |
| 11 | **AI-only reset on samples.** Keep an accepted/manual mapping and a rejected mapping as witnesses. Preview only AI-state selections, inspect the counts, type exactly DELETE and wait for Cleanup verified. Optionally request cached restart. | Core/sample records, USER mappings, rejections and published taxonomy remain. Selected AI state is removed, cleanup is verified, and cached restart remains a reviewable proposal. Budget/history from earlier readiness work is retained. | NOT RUN |
| 12 | **Partial then full taxonomy reset on samples, last.** First delete DOMAIN content only and verify surviving projects move to Unassigned. Then preview/select all user taxonomy kinds/rules and desired AI state; confirm the new exact impact. | Partial dependencies match the preview. Full taxonomy reset removes selected concepts and dependent memberships, starts revision zero in a new epoch, and retains repository metadata and earlier reports/allowance. Cached discovery can start another draft; old classification IDs are not reused blindly. | NOT RUN |

After destructive sample testing, publish a cached draft and restore a few manual/rule assignments for your next rehearsal. Fresh classification against newly created concept IDs needs fresh model calls; do not assume old classification results will replay.

## Automatic organization procedure and request limits

This test is separate because it can spend money and waits for the real scheduler. In Run setup, save a small classification count and the intended fixed/adaptive budget policy before enabling automation. A three-repository fresh classification uses at most six HTTP attempts; valid cache/rules hits can use fewer. Automatic work receives finite grants and cannot increase the original cumulative $5 ceiling. If admission or provider access fails, record the result honestly and inspect the run; do not reset usage or repeat paid calls merely to rehearse.

1. In the sample collection, verify no active run, no unpublished edits in progress, and sufficient available dollars (or fixed HTTP/generation slots when using fixed mode). Leave the published taxonomy in place.
2. Enable Automatic organization after significant edits. With live AI enabled on the backend, this scheduler uses LIVE regardless of the organizer's manual inference selector.
3. Create two distinct temporary PROJECT concepts with parent domains. This meets the documented significant-change threshold. Make no further edits for at least 90 seconds. A prior automatic run may impose the 30-minute cooldown; the test must respect it.
4. Observe one AUTO run, inspect its outcomes and confirm existing USER decisions/rejections remain. Disable automatic organization again before resets or further editing.

Rehearsals can otherwise use cached taxonomy, manual actions and Rules only repeatedly. The existing real AI proof need not be rerun. A cached classification is reusable only when its evidence and canonical-ID context still match; explicit cache misses are expected after some taxonomy/reset changes.

## Refined explorer and run setup checks

- At 1920×1080, verify the compact collections group leaves the domain/project tree most of the sidebar. Collapse Collections to gain more space. At mobile width, use the navigation drawer.
- Open Domains & Projects in the header: it should show structure without a repository fetch until a node is selected. Select a project and confirm its repository list and In this view count agree.
- Select a repository and check Selected plus its metric subtotals. Changing a filter clears selection with feedback; pagination and opening AI Organization retain it.
- Change search, language and visibility; remove individual pills or Clear filters. Counts cover the matching scope across pages.
- In AI Organization, test different taxonomy/classification counts, current-view versus entire-collection scope, and manual selection. Operation buttons create a preview; only Start reviewed run queues work. Save defaults starts no work and survives reload.
- Compare Fixed count limits and Adaptive cost budget. Adaptive preview shows a conservative upper bound and finite call grant, can proceed beyond the fixed count cap, and retains historical usage. Taxonomy publication and classification acceptance still require review.

See the [refinement report](../validation/phase-0-9-ui-and-ai-controls.md) for measured browser/backend evidence and the real two-HTTP adaptive canary.

## What readiness covers

The local app includes exploration, details/evidence, reviewed taxonomy discovery, classification/review, manual multi-membership, concept management, rules, reorganization, optional automation, activity, persistence and selective reset/restart. Automated coverage and the real AI proof are saved; this checklist supplies your account-specific acceptance evidence.

Cloud hosting/runtime integration is deferred. The app uses local SQLite and one backend process; retained AWS scratch resources are not its runtime. Private AI inputs, exhaustive GitHub relationship/activity completeness, unknown branch counts, production scaling and broad model-quality guarantees are outside this acceptance claim. Earlier BM25/YAKE/model benchmarks remain preserved; the application default is RAKE plus TF-IDF, with review-first AI.

The preservation verifier was rerun during this readiness check: PASS for 163 protected files, 34 historical API records, 29 cached records and the unchanged preflight UI copy. App reset does not delete those artifacts.

## Record your acceptance

Copy this result block into a new Markdown report under `docs/validation/private/demo/` for account-specific details. Do not include tokens, keys or private README text. Use the row numbers above to keep reports comparable.

```markdown
# Phase 0.9 operator acceptance
Date:
Account checked locally:
Rows passed:
Rows failed / observations:
Rows not run and why:
Expected repositories found (owner/name; private local report only):
GitHub coverage / Latest Work observations:
OpenAI HTTP counters before / after:
Reset cleanup verified:
Persistence verified:
Ready for my demo: YES / NO
Remaining issues:
```

For the longer operational instructions, use the [runbook](phase-0-9-demo-runbook.md). To rerun the full credential-free automated suite, stop the local app first, run `bash scripts/check-phase09.sh`, then restart it. Those browser tests use disposable fixtures and make no OpenAI calls; they do not replace the real account checks above.
