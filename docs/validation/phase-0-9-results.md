# Phase 0.9 — Complete local application results

Date: October 12, 2026 (America/New_York). Status: **implementation and local validation PASS; operator review available**. The user approved the full Phase 0.9 plan and explicitly required preservation of earlier testing, benchmarks and readiness evidence. Cloud remains deferred; the subsequent video request is completed below.

**Subsequent user-authorized video acceptance, October 12:** the [narrated walkthrough and guide](../../demo-video.md) record 26 chapters at 1920×1080 and 35 passed workflow checks. A real operator-authenticated GitHub session synced 310 repositories, exercised filters/pagination/private AI exclusion and activity windows, with OBSERVED contribution coverage. Supplemental global exact-name lookups found one accessible private match each for avimla and workshops. Remaining feature/reset tests used a disposable recording database; three classifications used fresh real OpenAI, taxonomy reused validated cache, and the actual 90-second scheduler used explicitly labeled fixture AI. The working account's taxonomy/mappings were not reset or edited. Recording resumed after a harness-only pending-badge selector correction, preserving completed footage and avoiding repeated paid calls. See [recorded validation](../../demo/validation.json) for provenance and limitations. This later user request authorized the video work that was deferred at initial handoff.

Post-video accounting: 20/20 approved HTTP slots used, 44/44 cumulative generation reservations, estimated cumulative $0.060911/$5 and zero outstanding reservation. Six HTTP requests were used by this recording; six other requests had been consumed between initial handoff and capture. Earlier snapshots below remain historical. The preservation verifier passed again for all 163 protected files, 34 historical API records and 29 historical cached records.

The production local app is served at **http://127.0.0.1:3000**, with FastAPI on 127.0.0.1:8000. Start/restart with `bash scripts/dev-demo.sh --live-ai`. The [runbook](../development/phase-0-9-demo-runbook.md) covers the complete operator workflow and recovery. GitHub OAuth is configured; the initial production anonymous check returned 401 at /me and health reported phase 0.9. The subsequent recording used the operator's real sign-in for product-UI login/sync verification. Earlier live OAuth/private/org access observations remain in their original reports.

The remaining sections preserve the original implementation handoff and its accounting snapshot. The recorded acceptance and post-video accounting above supersede statements about pending live checks and remaining requests.

## Delivered application

- Persistent owner/collection-scoped explorer: GitHub sync, My Repos, independent Favorites, access candidates/inclusion, search, language/visibility/concept filters, signed pagination, details and source coverage. Large inventories can resync independently of the 30-repository AI cohort limit. Selected repositories carry into the organizer.
- Canonical DOMAIN/PROJECT/TOPIC/TAG management: create/edit descriptions and aliases, stable-ID rename, normalized reservations, atomic reviewed draft publication, archive/domain dependencies and merge. Protected Unassigned parents preserve surviving projects.
- Manual multi-project/topic/tag organization with bulk and drag actions. Removal creates a protected rejection. Accepted AI suggestions become USER decisions. Rules support bounded metadata/name conditions, preview and explicit approval; private metadata can use local rules without model calls.
- Integrated versioned RAKE evidence profiles and TF-IDF candidate ranking, LangChain structured OpenAI taxonomy/classification, editable/selectable drafts and evidence-backed suggestion review. AI never publishes or accepts itself and never overwrites GitHub metadata. Private/unverified inputs are blocked; current public access is checked before extraction for connected repositories.
- Durable single-process jobs, one active workspace run, committed counters/history, partial/stale/error outcomes, restart interruption handling and reauthentication waits. Significant-edit automatic scheduling is optional, with the approved 90-second quiet period/30-minute cooldown. Incremental/full classification reconcile against the current taxonomy; rediscovery remains proposal-only.
- Numeric-actor/date Latest Work with selectable windows and disclosed bounded 90-day contribution coverage. Synthetic activity is visibly FIXTURE, separate from live observations. The contribution adapter uses the [GitHub contribution fields](https://docs.github.com/en/graphql/reference/users) and records its own traversal limits.
- Independent reset checklists, exact server impact counts, owner/version/expiry-bound one-use preview, exact DELETE, generation/epoch fencing, hidden old organization during cleanup, verified selective removal and optional cached restart. USER decisions/Core survive AI-only reset. Full taxonomy reset starts revision zero in a new epoch. Cost history/earlier readiness evidence are outside reset.

The approved local exception and future adapter handoff are documented in [ADR 0002](../adr/0002-phase09-local-workspace.md). Historical `app.main` and preflight UI remain usable; the product entrypoint is `app.local`. No dependency installation, deployment, GitHub writes or AWS changes were needed.

## Actual validation

Working tree at base commit `beb2290`; implementation remains uncommitted. The initial repository has substantial existing untracked project work; no files were staged or committed. Runtime: repository-local Node 24.21.0, Next.js 16.4.0/React 19.3.0, Python 3.13.5 and the existing locked backend/LangChain dependencies.

| Check | Actual result |
|---|---|
| `bash scripts/check-phase09.sh` | Exit 0; final complete validation log saved privately |
| Backend `pytest -q` | **111 passed** in 6.66s: original 81 plus 30 new product cases |
| Ruff check / format check | PASS; 52 Python files formatted |
| Frontend ESLint / TypeScript | PASS |
| Production Next.js build | PASS; no external asset/font dependency |
| Original Phase 0 browser regression | **4 passed**, original test source unchanged, 7.7s |
| Product browser acceptance | **4 passed**: full app journey; keyboard editor/rule/private details/mobile; bulk/drag multi-project controls; retained bounded organizer selection |
| Production anonymous smoke | Product title/login rendered; OAuth configured; /me=401; health phase=0.9; screenshot visually inspected |
| Preservation audit | **PASS**, 163 protected files and all historical ledger/cache rows unchanged |

The product tests use disposable SQLite stores and explicitly fake GitHub/model providers, with real local OAuth-state/session/CSRF routes and HTTP proxy mutations. They are credential-free workflow evidence, not live model or GitHub claims. Tests cover concurrent alias uniqueness, ownership/sample isolation, global filtering/cursor binding, actor/window behavior, manual races, partial outcomes, missing README/access loss, queue/restart recovery, reset preview expiry/reuse/staleness/exact confirmation, selected dependencies and old-worker fencing. The request allowance is tested concurrently across reopening and cannot exceed 20. Browser screenshots were inspected at desktop and 390px mobile width, and saved separately under ignored private diagnostics.

An early browser pass found selector/accessibility-label issues; subsequent passes fixed them. A final inventory test found selection loss and a sync/AI-limit coupling; both were fixed and the complete validation script rerun. No unresolved test failure is hidden by the final result.

## Fresh real AI proof and zero-call replay

[Fresh integration report](phase-0-9-live-ai-20261012T053557Z.md): one real Sol taxonomy generation and three real Luna classifications passed through the product service and strict schemas in **21.815s**. Inputs were the approved cached public FastAPI sample and two labeled synthetic Orion examples. The authenticated app session was explicitly synthetic; no private repository data or GitHub token was used. Publication in that isolated harness exercises the API; normal product publication requires user review.

| Task / returned model | Input tokens | Output tokens | Estimated new cost |
|---|---:|---:|---:|
| Taxonomy / gpt-6.1-sol | 828 | 511 | $0.006766 |
| FastAPI classification / gpt-6-luna | 920 | 214 | $0.000199 |
| Orion API classification / gpt-6-luna | 839 | 251 | $0.000210 |
| Orion UI classification / gpt-6-luna | 760 | 251 | $0.000202 |
| Total | 3,347 | 1,227 | **$0.007377** |

[Reset/replay proof](phase-0-9-reset-replay.md): accepted one real model PROJECT suggestion as USER, performed an exact preview/DELETE AI-only reset including app evidence cache, verified cleanup, then automatically restarted discovery from a revalidated cached result. Core and USER edges were identical before/after. Provenance was REPLAY; new HTTP/generation/cost use was **zero**.

The phase used **8/20 HTTP slots**: four generation attempts and four mandatory token counts, with retries disabled. **12 slots remain** at handoff. Cumulative generation accounting is **38/44**, retaining all 34 historical attempts. Estimated cumulative spending is **$0.059589/$5**, with **$0 outstanding**. Reset/restart/new owners cannot regain these allowances. Unknown remote outcomes consume slots and retain conservative reservations. Pricing is an estimate under the existing configured rates, not a billing invoice; [official pricing](https://developers.openai.com/api/docs/pricing) was rechecked before the bounded proof. No new model competition, benchmark relabeling or additional paid probe was performed.

## Preservation and limits

[Preservation audit](phase-0-9-preservation.md) proves that previous source tests, frozen corpus/reference labels, public/private Markdown reports, all 34 historical API records, all 29 historical replay records and the experiment identity/sentinel remain intact. A 186-file protected local baseline was captured before implementation. The application has separate private state and versioned extraction; the old readiness/benchmark files were not overwritten. Retained AWS scratch resources were not touched.

This is a complete bounded local product, with cloud components intentionally deferred. It uses one backend process and an aggregate SQLite adapter, not distributed DynamoDB/SQS semantics. Organization runs are bounded to 30 selected repositories and the local registry to 500 concepts; large inventories remain browsable. Incremental runs currently visit their selected cohort rather than using production delta indexes. Branch counts may be unknown; README extraction is bounded and metadata-only fallback is explicit. Upstream watch/team/direct/SSO completeness remains subject to the earlier reports. Activity is a bounded contribution observation, not exhaustive push/lifetime history; fresh live activity coverage in this new app awaits the user's optional login/sync.

The small fresh integration check establishes wiring, not production generalization or calibrated confidence. Earlier Phase 0.5 conditional quality/comparison/license limits remain. All AI is review-first; private model inputs remain unauthorized. Interrupted remote inference requires explicit operator review before retry. Optional reset restart uses cached results; changed/new IDs can require explicit live classification. Reset verifies removal of selected live application records, not provider retention, shared historical replay entries or forensic disk erasure.

The app/runbook are ready for local operator review. No hosted deployment, recording/upload/submission or Phase 1 cloud implementation was performed.
