# Phase 0.9 local application runbook

**October 13 UI and AI controls:** AI Organization, Content settings and Sync GitHub now live in the header. Browse taxonomy in the header and the sidebar both expose Projects (Domains → Projects), Topics and Tags, with alias search and separate accepted/pending counts. The earlier narrated video is preserved and shows the previous navigation. See the [refinement results](../validation/phase-0-9-ui-and-ai-controls.md) for current screenshots and validation. The [allowance guide](ai-allowance.md) covers both fixed windows and adaptive run budgets.

Approved scope: complete local application; cloud infrastructure and video planning remain deferred. Earlier pre-testing, benchmarking and readiness artifacts remain available unchanged. See [results](../validation/phase-0-9-results.md) and [local adapter ADR](../adr/0002-phase09-local-workspace.md).

For your first test session, follow the [ordered acceptance checklist](phase-0-9-acceptance-checklist.md). It starts with your real GitHub login/sync, covers the complete local feature set, puts reset tests last, and includes a Markdown results template and a rehearsal sequence within the remaining API allowance.

The [narrated 1080p walkthrough](../../demo-video.md) now demonstrates that sequence in 26 chapters, with captions, an audio-only copy and 35 passed recorded workflow checks. It includes a real operator-authenticated GitHub sync; destructive tests use an isolated sample database. Its current allowance snapshot supersedes the initial handoff numbers below.

## Start and sign in

From the repository root:

```bash
bash scripts/dev-demo.sh --live-ai
```

Open **http://127.0.0.1:3000**. Use this exact host, matching the existing OAuth App callback. The backend runs at 127.0.0.1:8000. Only one backend worker is supported. Stop an older preflight/demo instance before starting another. Ctrl+C stops this launcher and its backend. `--dev` uses the frontend development server; default `--production` uses the production build and leaves live AI disabled unless enabled in backend/.env.

Existing backend/.env contains the OAuth registration and server-only OpenAI key. The example documents `DEMO_DATABASE` and `DEMO_LIVE_AI`. No key belongs in frontend variables or browser storage. The startup live flag enables new inference within the existing allowance; it does not initialize or increase any budget. Rebuild after source changes with `NEXT_TELEMETRY_DISABLED=1 npm --prefix frontend run build` using the repository-local Node on PATH.

If dependencies need restoring, use the existing [setup guide](phase-0-localhost.md) and locked manifests, including the backend `dev` and `ai-pretest` groups. No new package installation was required for this phase.

Select **Continue with GitHub**, authorize the existing OAuth App, then **Sync GitHub** in the header. GitHub access is read-only in this application. OAuth's `repo` scope itself includes writes. Browse My Repos, Favorites and Access candidates independently. An access candidate can be explicitly included in My Repos in its details panel. Source observations disclose partial/unavailable upstream coverage.

Application state survives backend restart. GitHub tokens and sessions remain in memory, so sign in again after restart. Queued jobs wait for an authorized session. Interrupted inference stays interrupted until an explicit retry; uncertain remote calls are never blindly repeated. The initial real AI integration check used a synthetic app session. The subsequent narrated walkthrough verified a real operator-authenticated product UI session, sync, filters, pagination, private-evidence exclusion and activity-window controls; exact-name lookups also confirmed accessible private avimla and workshops fixtures. GitHub coverage remains bounded rather than exhaustive.

## Full workflow

1. Select **Public + synthetic demo**, then **Load demo samples**. This collection contains the approved public FastAPI sample and two labeled synthetic Orion repositories. It is isolated from your GitHub collection. Synthetic entries have no fabricated GitHub URL; their test activity is labeled FIXTURE.
2. Inspect repository details to see the versioned RAKE evidence profile, phrases and supporting sections. Public GitHub extraction rechecks current public access; private README-derived evidence never enters the model path. Missing README can use verified public metadata only. Branch counts may remain unknown until optional enrichment.
3. Open **AI Organization** in the header. Existing drafts can be reviewed immediately. For a genuinely new sample collection, keep **Reuse validated cached AI**, choose a taxonomy sample size of 3, preview **Discover taxonomy**, then **Start reviewed run** if a validated cache entry exists. Cache misses never fall back to paid inference. Previously submitted taxonomy inputs are protected: to intentionally refresh them, select **Live AI**, enable **Re-analyze with AI**, enter a reason, preview **Rediscover taxonomy**, inspect the cohort and dollar bound, then start. Use adaptive mode if the fixed window is exhausted; this does not renew it.
4. **Review draft**. Edit names, definitions, aliases and project parent domains; exclude unwanted concepts. To combine equivalents, retain one row and add aliases. Separate concepts remain distinct; the app never auto-merges them. **Approve & publish taxonomy** exposes one atomic revision. Draft publication does not itself spend on classification.
5. Preview **Full classification** for the chosen scope/count. Previously analyzed repositories (including valid No match results) reconcile locally by default, with zero provider/count HTTP requests. The preview shows fresh AI, offline reconciliation and protected/unknown cases. To intentionally refresh classification, select **Live AI**, enable **Re-analyze with AI**, enter why the evidence/taxonomy changed or why a failed attempt is being retried, then preview again. Choose **Adaptive cost budget**, normally $0.25 maximum, and inspect the exact cohort and conservative bound before **Start reviewed run**. Up to three fresh classifications can require six HTTP attempts. Review additions by type/concept/repository and group by repository or concept; accept/reject individually or select a reviewed batch. Acceptance is a USER decision; rejection remains protected. Existing memberships appear alongside proposals. Disable re-analysis again for routine offline work.
6. Use **Content settings** to create/edit/rename/archive/merge concepts and change project domains. Canonical IDs survive rename. Conflicting normalized names/aliases are rejected atomically. Archiving a domain moves surviving projects to protected Unassigned. Merge retains the target ID and reconciles memberships.
7. Use row checkboxes and the bulk toolbar to add/remove memberships. Drag a repository onto a Project, Topic or Tag in either browser to add another membership. Dragging a selected row carries the explicit selected set and asks for confirmation; an unselected row carries only itself. Dropping on a Domain expands it and asks you to choose an existing Project in that Domain. Removing one membership preserves the others. Manual actions work without AI.
8. Create a rule in Content settings, preview its exact metadata/name matches, then approve. Use **Rules only** classification to apply rules with zero model calls, including on accessible private metadata. Rejections and USER mappings retain precedence.
9. **Reorganize incremental** and **Full classification** reconcile the reviewed cohort against the current taxonomy. **Rediscover taxonomy** is a separate draft operation. Neither publishes or accepts output automatically. A durable per-repository receipt is independent of detailed history, membership coverage and freshness. Topic/tag-only repositories are **Labeled** and may still have **No project**; they do not need another paid call for that reason. Use the **Organization view** selector for No labels, No project, Needs review, No AI match, Failed/blocked or Stale analysis. Historical records without an input fingerprint explicitly say Input history unavailable. Use **Extract evidence** to refresh public metadata/README evidence without calling a model; observed evidence changes mark old analysis stale. No background GitHub README polling is implied.
10. Save run counts/budget defaults, then expand **Automatic organization → Configure thresholds**. Configure weighted changes AND distinct entities, OR new projects (0 disables that branch), eligible change types, change window, quiet period and cooldown. Defaults are six weighted changes across three entities OR two new projects within 900 seconds, followed by 90 seconds quiet and 1800 seconds cooldown. Saving settings shows current counts and waits. It is disabled initially. Automatic runs reconcile already analyzed repositories offline; only genuinely new eligible repositories can consume the saved AI budget. Failed, unknown and legacy-unrecorded attempts need explicit re-analysis. Cosmetic edits are excluded. Adaptive live work requires a configured budget operator. Thresholds never clear analysis receipts or authorize automatic paid re-analysis.
11. **Latest Work** filters numeric user identity and actual contribution dates within 7/14/30/90 days. The GitHub query observes bounded 90-day contribution coverage and does not substitute repository push times. Empty/partial/unavailable live data is disclosed. Samples show separately labeled synthetic activity.
12. **Preview reset** offers independent AI-state and user-taxonomy/content selections. Review the exact server counts, then type exactly `DELETE`. Any workspace change or five-minute expiry requires a new preview. AI-only reset preserves USER mappings/rejections. Deleting concept kinds removes their dependent mappings; domain-only deletion reparents projects. Full taxonomy reset starts revision zero in a new epoch. Core metadata, GitHub access, prior reports, compact AI analysis receipts and budget records survive. Deleted taxonomy/evidence invalidates stored assignment references without clearing the no-repeat guard. Optional restart begins only after cleanup verification, uses cached/local reconciliation and honors durable receipts. Another paid analysis requires the explicit re-analysis control and preview. A full taxonomy reset produces new IDs, so old classification results cannot be blindly replayed.

## Logo and appearance

Open **Content settings → Appearance** to choose **Blue zen rays** (the default, tail-free cat) or **Continuous blue aura**. Toggle **Animate logo** to pause/resume. Reduced-motion browser settings automatically use a still icon. The choice is saved in this browser and applies to the header, sign-in screen and static browser-tab icon. **Restore default logo** clears that browser override.

App-wide defaults are in [frontend/src/config/branding.ts](../../frontend/src/config/branding.ts); rebuild after editing them. All five KPI cards now have matching icons. See [validation and screenshots](../validation/phase-0-9-logo-and-kpi-icons.md). The original video is retained and predates these controls.

## Taxonomy conflicts and repairs

The revised theme uses Indigo navigation, Blue sync/links, Light Blue progress panels and Purple AI accents alongside Deep Purple primary actions. Sync/run labels use readable capitalization. See the [feedback revision and previews](../validation/phase-0-9-theme-feedback.md).

Review taxonomy draft now checks all included names/aliases before publication. A conflict identifies the exact field/text and the owning active or archived concept of the same type. Case, Unicode and punctuation normalization apply. Archived names remain reserved; an alias repeating its own name also conflicts.

Use Edit manually, Remove alias, a suggested distinct name, Reuse existing (active concepts only), or Exclude this proposal. Remove conflicting aliases applies a bulk form repair. Choose reuse only when the meanings are equivalent; choose a distinct name for separate concepts. Repairs change this form only and provide Undo last repair. Save draft stores edits; Approve & publish taxonomy is still required for live changes. Domain reuse/rename updates dependent draft project parents. Existing concept IDs, descriptions, aliases and memberships remain intact during reuse. Archived reservations are preserved. No AI request is needed for checks or repairs.

## Allowance and recovery

The earlier recording ended at 20/20 HTTP requests, 44 cumulative generations and $0.060911 estimated usage. Those are historical snapshots. **At the October 13 adaptive canary, cumulative usage is $0.103264/$5, 65 generation reservations and 62 application HTTP attempts, with no unresolved call reservation or run hold.** The fixed window remains exhausted (20 used); adaptive mode completed the canary without changing that window. Check current counters in the app because subsequent use changes them.

For fixed mode, use **Manage API allowance** to explicitly renew or selectively change limits. For adaptive mode, choose a per-run dollar maximum and preview a count-based cohort, then **Start reviewed run**. The preview makes no model requests and may admit fewer repositories than requested; inspect its exclusions. Automatic and manual selection both remain bounded to 30 repositories per local run. Full classification reconciles the chosen cohort. Cached AI, extraction, manual organization and local rules remain available without fresh inference.

The adaptive ceiling is a conservative run bound, not a promise to spend that amount. Start reserves only the reviewed plan's upper bound, derives finite HTTP/generation slots, then releases demonstrably unused money. Unknown calls retain reservations. All modes share the original $5 ceiling; resets, restarts and new workspaces do not restore money. See [ADR 0004](../adr/0004-cohorts-and-adaptive-budgets.md).

If a live run fails, inspect its saved outcome before retrying. A successful remote result may still be rejected if taxonomy, cache/privacy epochs or manual decisions changed. Retained reservations cover unknown remote costs. Cached results require matching evidence, current IDs, policy and validation; model confidence is uncalibrated. The app remains usable for manual organization and local rules after allowance exhaustion.

Private local state is under `docs/validation/private/demo`; provider diagnostics are under the existing ignored AI experiment's `phase09-calls` directory. Reset removes selected live application records, not historical benchmark evidence, shared model replay entries, provider retention or forensic disk remnants. Do not delete the original AI ledger/sentinel or retained AWS scratch resources.

## Verification and historical tools

Stop the app before isolated browser checks (they use ports 3000/8000):

```bash
bash scripts/check-phase09.sh
python3 scripts/verify-pretest-preservation.py .tools/phase09-baseline-20261012T045829Z
```

The check script runs backend regression/product tests, Ruff, frontend lint/types/build, the four original preflight browser tests and the product browser workflows, including responsive layout, scoped metrics, on-demand header fetching and reviewed cohort/adaptive execution. Browser tests use fake external providers clearly labeled FIXTURE, real local routes/auth/session/CSRF and disposable databases. They make no paid calls. Repository-local Chromium is already installed under `.tools/playwright`.

The latest [one-generation adaptive canary](../validation/phase-0-9-adaptive-live-20261013T145429Z.md) already passed. For a separately authorized broader real AI proof, `cd backend && .venv/bin/python -m app.demo.validate_live --live` uses up to four generations/eight slots and saves another Markdown report. Do not rerun it simply to rehearse: the initial proof already passed and requests are intentionally limited.

The original preflight remains available through `scripts/dev-backend.sh` + `scripts/dev-frontend.sh`. Its UI source is preserved verbatim in `Preflight.tsx`. The original extraction, BM25/YAKE checks, quality reports, frozen corpus, tests and budget history are retained. The protected baseline is ignored/local and contains no .env copy. Future cloud phases should replace the SQLite/job adapter and reuse these product workflows and evidence.

## October 13 taxonomy and analysis validation

See [the implementation/validation report](../validation/phase-0-9-taxonomy-and-analysis.md) and [ADR 0005](../adr/0005-durable-analysis-and-local-reconciliation.md). Earlier benchmark/readiness reports and the original narrated video remain unchanged; the recording predates these navigation and admission updates. No new paid model calls were needed for this validation.
