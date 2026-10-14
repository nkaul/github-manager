# Phase 0.9 — Complete working local MVP demo

Date: October 12, 2026 (America/New_York).

Status: **APPROVED AND IMPLEMENTED — local operator review available.** The user approved Phase 0.9, including the local adapter and bounded request renewal, then required preservation of all earlier testing/benchmark/readiness work. Cloud and video planning remain deferred. See [actual results](../validation/phase-0-9-results.md), [runbook](../development/phase-0-9-demo-runbook.md), and [ADR 0002](../adr/0002-phase09-local-workspace.md). The planning language below records the approved proposal; current evidence/limits are in the results record.

## 1. Objective and recommendation

Build a complete working local GitHub Manager that the user can operate and demonstrate. Complete the user journey from GitHub sign-in through repository exploration, AI taxonomy review, classification, manual corrections, reorganization, personal activity and safe reset/rediscovery. Cloud provisioning/deployment and video walkthrough planning come later.

Recommend Next.js + FastAPI with a temporary SQLite application adapter and a durable local background-job runner. Preserve the approved domain contracts and service boundaries so the later DynamoDB/SQS implementation can reuse the UI, APIs, schemas, validators and workflow services. This is a proposed local-demo exception, not a replacement for the approved three-table DynamoDB/SQS architecture.

Phase 0 established representative GitHub and AWS access. Phase 0.5 established extraction/retrieval and bounded LangChain/OpenAI feasibility, with a conditional go for human-reviewed AI. These results do not establish an integrated product: the browser currently provides access preflight, while AI runs through CLI experiments. Phase 0.9 is substantial application work, with overall complexity **L**, rather than another capability test.

The user confirmed the local functional-demo priority on October 12. Deadline, judging criteria, video duration, narration and recording/submission requirements can be handled when the user resumes video planning. They are not prerequisites for this phase. A future hosted-review requirement would need a separate hosting/HTTPS/OAuth deployment plan.

## 2. Repository findings and reuse

| Area | Existing evidence/code | Phase 0.9 gap |
|---|---|---|
| Sign-in | Phase 0 OAuth App, browser-bound state, PKCE, session/CSRF and logout in backend/app/main.py and app/auth/sessions.py | Promote into product routes; authorize every new operation; make restart/relogin behavior explicit |
| Repository explorer | My Repos, Favorites, candidate list, name search, signed pagination and trusted links in frontend/src/app/page.tsx | Persist inventory; add details, organization chips/tree, richer filters, bulk actions and usable loading/error states |
| GitHub discovery | Stable numeric IDs, separate source observations and organization reconciliation | Background sync/enrichment, persistent freshness, explicit inclusion and access-loss reconciliation |
| Personal activity | Contributed-to repository discovery | Actual actor/timestamp activity aggregation; current contribution discovery cannot implement a 14-day Latest Work view |
| Intelligence | RAKE/YAKE/TF-IDF/BM25 experiments and cached public evidence | App-owned profiles, policy gates and inspection UI; version corrections for README-format noise without altering the frozen benchmark |
| Taxonomy | Structured draft/schema checks; user qualitatively accepted samples | Durable registry, aliases, draft editing/publishing, CRUD/archive/merge, domain dependencies and review UI |
| Classification | Twenty latest API results; primary-label precision 100%, recall 96.2%, micro-F1 98.0% on the reused 20-case corpus | Real workspace/canonical IDs, persistent suggestions, acceptance/rejection, protected manual decisions and commit-time fences |
| Organization | In-memory LocalOrganizationRun fixture | Durable jobs, accurate progress/history, retries/recovery, revision changes and local auto-trigger evaluation |
| Reset | Approved design and proposed safety contracts | Entire preview/confirmation/cleanup/restart application flow |
| Demonstration | Access and AI Markdown reports; existing browser pretest suite | Cohesive UI, complete end-to-end checks, operator walkthrough and demo results report |

Reuse the existing package managers, locked runtime versions, same-origin frontend API proxy, GitHub adapter, auth controls, extraction/retrieval algorithms, Pydantic validators and model budgeting patterns. Preserve all historical evidence. The pretest controller and benchmark registry are fixtures, not product state or publication services.

Important promotion gap: pretest chains construct public/synthetic payloads for their fixed corpus. Product routes must derive visibility and source policy from trusted server records; they must never accept a browser-supplied public/private flag or merely relabel arbitrary repository content as public.

## 3. Local architecture and its limits

Proposed flow:

    Next.js browser → same-origin API proxy → FastAPI routes/services
                                           ├─ GitHub OAuth/read-only connector
                                           ├─ local SQLite application store
                                           └─ durable job runner → extraction / LangChain / cleanup

Use one local application database with three logical data areas: Core, Intelligence and Organization. Jobs/outbox, change events and state transitions share that database where atomicity is required. Repository interfaces own storage details; UI and workflow services use domain operations rather than SQL or DynamoDB keys. SQLite supports atomic, durable transactions; implementation still needs explicit transaction and recovery tests. [SQLite transaction documentation](https://www.sqlite.org/transactional.html).

Keep the existing AI spending ledger/sentinel and immutable reports separate from resettable application data. Reset must never clear cost accounting, restore a request allowance or erase unknown-charge reservations. A provider call and an application database commit are separate operations: record/recover that boundary without promising exactly-once inference.

The first demo backend runs as **one process**, with bounded background work and durable job records. A persisted outbox/job transition, leases, idempotent per-item commits and startup recovery avoid depending on FastAPI fire-and-forget tasks. Poll status initially; SSE is an optional transport improvement once the polling flow works. No distributed queue is required for this local mode.

Retain server-memory-only GitHub tokens for this phase. A backend restart requires sign-in again, while taxonomy, assignments, inventory and run history survive. Jobs requiring an active connection pause for reauthentication; logout/disconnect stops new GitHub or paid work. Do not persist tokens in SQLite/job payloads, browser storage, reports or prompts. Bind only to loopback and refuse public-host configuration in demo mode. This does not satisfy production session/token storage requirements.

All application records remain scoped to an authenticated owner/workspace even when the main demonstration uses one account. Use mode-0600 ignored local database/artifact files. Cross-owner tests remain required. Private GitHub metadata may be displayed locally within the existing authorized account access; it cannot enter model inputs or submission artifacts under the current public/synthetic allowance.

| Option | Benefit | Cost / disposition |
|---|---|---|
| SQLite + local durable runner — recommended | Smallest local setup; complete transactional application workflows before cloud deployment | Temporary persistence/dispatch adapters; later DynamoDB/SQS correctness must be implemented and tested separately |
| DynamoDB Local + queue emulator | Earlier exercise of final storage access patterns | Adds emulator/tooling and queue setup to the demo critical path; choose now only if that fidelity is more important than demo speed |
| Retained AWS scratch resources | Existing access evidence and real services | Scratch resources are test targets, not an approved app deployment; using them as app storage needs a reviewed resource/data plan |

After the local demo, reconcile reusable Phase 0.9 work with Phases 1–10 instead of rebuilding features. Implement three DynamoDB repositories, transaction/key/query contracts and SQS dispatch/runtime roles, then rerun the same domain/browser tests plus AWS-specific tests. Local SQLite success cannot close DynamoDB contention, IAM, SQS delivery, throughput or cloud-operational gates. Demo data migration is a separate choice; a fresh dev import is the default proposal.

## 4. Functional scope required for demo acceptance

All rows below must have working user actions and persisted outcomes. Do not expose dead buttons or claim an unimplemented feature is complete.

| Workflow | Required behavior |
|---|---|
| Connect and sync | Real OAuth App login; background import/refresh; repo rows appear independently of AI; partial coverage and last-sync state remain visible |
| Explore | My Repos, independent starred/watched Favorites, Latest Work and Uncategorized; stable GitHub links/details; pagination; global supported filtering before paging; project/topic/tag navigation |
| Inspect evidence | View source-backed public/synthetic phrases and short purpose evidence, extraction version and source freshness; missing README falls back safely |
| Discover taxonomy | Explicit first-run discovery; compact evidence; edit/select/reject/merge proposals; publish only on user approval; stable IDs and a single visible revision boundary |
| Manage content | Create/edit descriptions/aliases, rename, archive and merge domains/projects/topics/tags; duplicate-name validation; project domain changes and an explicit Unassigned domain |
| Assign and review | Add multiple project memberships, topics and tags; keyboard-accessible bulk assignment plus drag/drop that adds membership; accept/reject AI suggestions with evidence; preserve manual choices and rejection tombstones |
| Rules | A small explicit rule builder for supported exact metadata/name conditions; preview matches and user approval; do not add an unrestricted expression language |
| Reorganize | Separate incremental/full classification and proposal-only rediscovery; one active run; progress, history and stale/partial/no-match outcomes; new projects may attract already-organized repos |
| Automatic updates | Meaningful edits update freshness and schedule one debounced local run when enabled; cosmetic edits/proposals do not loop; existing default thresholds remain unless explicitly configured |
| Personal activity | Numeric actor identity and real timestamps within a supported selectable window, default 14 days; exclude other users' pushes and disclose incomplete upstream coverage |
| Reset and restart | Two independent checklists, exact server impact preview, expiring plan, exact DELETE confirmation, stale-preview rejection, transactional generation/epoch fencing, verified cleanup, then optional restart |
| Continuity | Browser reload retains state; backend restart retains application state but asks for login; permission loss hides restricted content; failed jobs can recover without duplicate mappings or automatic extra spending |

Domains are derived through project membership for this demo. A topic/tag alone does not remove a repository from Uncategorized, and a pending project suggestion does not count as an accepted project association. Accepted AI mappings become USER decisions. AI never rewrites GitHub URLs, IDs, permissions, timestamps, stars/watches, language or native topics.

Use review-first AI. Do not enable broad automatic acceptance based on the small preflight, model confidence or the user's qualitative taxonomy review. Keep primary-purpose TOPICs and primary implementation/dependency TAGs. RAKE + TF-IDF are the initial application defaults; BM25 remains an evaluated optional candidate ranker and YAKE remains outside the default app path pending adoption/license review.

## 5. Demo data and API-call boundaries

Use an owner-isolated **demo sample workspace/collection** restricted to approved public samples and clearly labeled synthetic examples. Keep sample collections distinct from My Repos/Favorites: a public library is not the user's repository or favorite merely because it is readable. Only actual upstream relationships populate those views. Existing public/synthetic samples can show multi-repository initiatives without exposing private work; synthetic entries must never have fabricated GitHub links or be presented as real contributions.

For the first live proof, select a small three-repository AI cohort within a larger browsable sample collection: a public sample plus two related synthetic examples. Expand only if functional acceptance needs it and the call allowance permits it. User-owned public examples can replace synthetic data after selection and server-side policy verification; private material requires separate permission. Shared language alone must not manufacture a logical project.

Sample-workspace isolation must apply on the server and across search suggestions, navigation counts, details, history, errors and exports. A public sample view must not reveal another collection's private metadata. Do not expose environment values, OAuth callback codes or tokens in the demo UI or reports. A specific recording mode/redaction audit can be planned later with the video requirements.

The prior dollar budget is $5 total, estimated spending $0.052212, with no outstanding reservation. The prior **34-generation-attempt ceiling is reached** and remains unchanged during planning. Phase 0.9 needs explicit renewed call authorization; having remaining dollars does not grant extra requests.

Recommended bounded renewal in the Phase 0.9 approval: **at most 20 additional OpenAI HTTP requests in total**, counting token-count requests, model generations, access probes and any retries. With the current mandatory pre-count and retries disabled, this permits **at most 10 new generations**. Preserve the original cumulative $5 cap and existing ledger; extend the generation ceiling by no more than 10 only after approval, and add a durable phase-specific HTTP-request allowance. Unknown outcomes consume their request slots and retain conservative cost reservations.

Indicative allocation: one initial taxonomy call, three classifications, one targeted reorganization, one post-full-reset taxonomy call and three post-reset classifications; one generation-equivalent reserve. This is a ceiling and proposed allocation, not guaranteed successful output. Cached replay and credential-free workflow fixtures cover repeated rehearsals. A cached result must be labeled as reused and revalidated against current concepts, evidence, policy, manual decisions and epochs before any write; never replay invalid old IDs into a new taxonomy. Budget exhaustion yields a saved partial run, not an automatic cap increase.

Reuse the preflight defaults in backend/.env: Sol for taxonomy and Luna for classification. Recheck configured model identifiers/rates before approved live work; do not run another model competition or authentication probe when current access evidence is sufficient. Direct LangChain structured model output plus backend validation remains the path; no agent/tool loop or extra summarizing model. [LangChain model structured output](https://docs.langchain.com/oss/python/langchain/models#structured-output).

The demo must operate actual software. Reused inference can make walkthroughs repeatable, but must be identified as reused. New inference, cached inference, synthetic inputs and real GitHub observations must remain distinguishable in the UI and results report. Video editing/narration is outside this phase.

## 6. Dependency-ordered implementation steps

Approval of Phase 0.9 would authorize these steps as one local-demo phase. Show a working slice after each milestone; continue within that approved scope unless a blocker changes the requested behavior or requires new data/spending/hosting authorization.

| Step | Work and proposed files | Exit demonstration / tests | Complexity |
|---|---|---|---|
| 0.9A Contracts and demo boundaries | ADR for local adapter; app/schemas; owner policy; app/persistence/interfaces.py; demo configuration and sample manifest | Confirm permitted data, call accounting and complete feature checklist; explicit local-only startup | S–M |
| 0.9B Durable connected explorer | app/persistence/sqlite, app/jobs, app/api/auth/repositories/sync, GitHub enrichment; workspace layout/details/search | Login → durable inventory → usable My Repos/Favorites; reload/relogin preserves data; signed cursors, cross-owner and partial-sync tests | M |
| 0.9C Canonical manual organization | app/taxonomy/registry/review/merge, association services, Content screens, tree/bulk/drag actions and rule preview | Complete organization without AI first; stable rename, alias collision, multi-project, archive/merge and protected rejection tests | L |
| 0.9D Integrated intelligence and AI | Promote reusable pretest algorithms into app/intelligence and app/organizer; app/ai budgeted provider boundary; bootstrap/review/classification routes and screens | Source evidence → real draft → edit/publish → classification suggestions → accept/reject; schema, source-policy and budget failures leave trusted metadata unchanged | L |
| 0.9E Organization and activity | Durable run controller/history, change events/local scheduler, app/github/activity.py and Latest Work; polling UI | Incremental/full runs and rediscovery are distinct; manual decisions survive reorganization; exact-once counters, revision races and actor/window tests | M–L |
| 0.9F Safe repeatable reset | app/reset preview/execute/cleanup, durable audit and worker fences; two-checklist settings screen | AI-only/partial/full reset with verified app cleanup and restart; stale preview and delayed worker writes fail; GitHub/Core and cost ledger remain intact | L |
| 0.9G Product polish and acceptance | Shared UI components, responsive/a11y states; backend/tests/demo and frontend/tests/demo; startup/check scripts; runbook/results | Complete browser walkthrough, production frontend build, fresh-session rehearsal, restart recovery and saved actual validation; user can operate the demo | M |

Build the real browser flow early: complete 0.9B/0.9C before broad AI integration, and complete one live 0.9D path before visual polish. Avoid another open-ended evaluation round. Parallel independent model requests may use the tested isolated-client pattern only where budgets and job commits remain safe; no parallel-agent execution is assumed.

## 7. API and transactional contracts

Promote FastAPI routes into modules rather than expanding the current preflight-only main.py indefinitely. Keep /api/v1 boundaries compatible with the approved baseline: /me and auth/logout; /sync and status; /repos and detail/associations; /activity/latest; /taxonomy drafts/concepts/publish/merge/rediscover; /content/rules; /organizer status/settings/reorganize/suggestions/runs; /organizer/reset preview/execute/status. Exact wire schemas must be frozen in 0.9A. Refactor the frontend API client for typed JSON request bodies and PATCH/PUT/DELETE, as it currently only supports GET and CSRF-protected POST.

Mutations require authenticated workspace ownership, Origin/CSRF checks, validation and bounded bulk sizes. Background requests return a durable run ID promptly. Polling reads committed state. No browser route directly invokes an unbounded model loop.

Required atomic application transactions:

- Create/rename reserves normalized canonical names and aliases uniquely within workspace/kind/epoch, with concept/revision changes committed together. Publication exposes one complete reviewed revision, never a partial draft.
- Association writes update the authoritative mapping, reverse lookup and summary consistently. USER/AUTO provenance remains separate; manual decision versions protect accept/reject/edit races.
- Worker commits check organization generation, taxonomy/cache epochs, revision, concept ACTIVE state, owner/access policy and manual decision version inside the same transaction as their result writes. A successful model response can still be stale and must be rejected.
- Reset previews bind selection/dependency counts, owner, version, epochs, expiry and plan identity. Execute consumes the plan once and advances the appropriate fences atomically. Cleanup is bounded and resumable; restart waits for verification. Clear only selected kinds/namespaces, preserve manual rejection decisions unless explicitly selected by a separately disclosed destructive scope, and never use database-file deletion as reset.
- Job/outbox creation, lease ownership, item completion and counters are idempotent. A process restart reclaims expired local leases; uncertain provider calls are not automatically retried. GitHub jobs wait for an active authorized connection.

These contracts adopt the proposed D03/D04/D06/D08/D09/D13 safety directions for the local demo. Approval must record that direction explicitly; it does not claim their DynamoDB implementations exist.

## 8. Acceptance and verification

Existing baseline: 81 backend tests and Ruff passed in Phase 0.5; four earlier browser tests cover Phase 0 access preflight. These are historical results, not Phase 0.9 evidence. Add meaningful product tests for the new stateful behavior and run relevant existing regression checks.

| Gate | Required new evidence |
|---|---|
| Complete browser journey | Sign-in or explicitly labeled test session → sync → search/details → draft edit/publish → suggestions/review → manual multi-project action → reorganization → Latest Work → reset/restart |
| Registry correctness | Concurrent duplicate aliases, rename preserving IDs, distinct concepts, archive/domain dependency, merge interruption/recovery and both mapping directions |
| Human ownership | Accept promotes USER; manual rejection survives rerun/AI-only reset; new project can suggest an additional membership without removing existing USER edges |
| Durable workflow | Reload/restart, duplicate delivery, expired lease, partial failure, paused reauth, stale revision and accurate counters; no duplicate inference caused by UI double-submit |
| Reset correctness | Exact DELETE, no mutation for bad/expired/reused/stale plans, AI-only versus partial/full dependencies, in-flight stale commit blocked, cleanup verified before restart |
| Source/privacy/auth | Real GitHub metadata remains unchanged after invalid AI, no private source enters model prompts/public-demo exports, sample isolation applies everywhere, unauthenticated/CSRF/cross-owner writes fail |
| Budget | Generation and all OpenAI HTTP requests bounded atomically across concurrent work/restart; cached replay costs zero new requests; app reset cannot regain allowance |
| Activity and coverage | Actor/window semantics proven with fixtures; real supported activity observation if available; empty/partial live coverage is disclosed rather than filled with invented events |
| Frontend quality | Production build, lint/typecheck, accessible keyboard workflows, responsive layout, useful empty/loading/error states and no dead primary actions |
| Live integration | One fresh authorized app taxonomy/classification path with actual usage and returned-model IDs; provider failures/caches never labeled as new live results |

Proposed commands to add during implementation: scripts/dev-demo.sh, scripts/check-phase09.sh and a dedicated browser test:demo package command. The check script should cover Ruff/pytest, frontend lint/typecheck/build and credential-free browser workflows; live checks are separately gated. These scripts do not exist yet and were not run during this planning task.

Generate docs/validation/phase-0-9-results.md with commit/worktree context, configuration versions, actual test commands/results, live versus fixture/replay evidence, model/HTTP request counts, tokens/estimated cumulative cost, measured demo timings, reset counts/cleanup verification and known limitations. Keep detailed raw payloads and local state ignored/private. Save a submission-safe report separately from private diagnostics.

## 9. Operator walkthrough and handoff

Create docs/development/phase-0-9-demo-runbook.md during implementation. Include clean startup, safe sample selection, readiness checks, normal/logout/restart behavior, the complete browser workflow and how to recover without changing the ledger. Provide a short functional acceptance checklist the user can follow independently.

The walkthrough must exercise connection/exploration, evidence inspection, taxonomy draft/edit/publish, suggestions/accept/reject, manual multi-project organization, taxonomy CRUD/rules, incremental/full reorganization, automatic debounce, Latest Work and AI-only/partial/full reset with restart. Show real status, persisted outcomes and current coverage limitations. Do not silently accelerate the default scheduler or simulate progress.

If the user has no suitable recent public activity, show the real empty/partial state plus a separate labeled activity fixture; that proves UI/logic, not live GitHub completeness. Prefer a production frontend build served on localhost for final acceptance. A cached result or labeled offline sample can support repeatable walkthroughs; a failed live check remains recorded rather than silently replaced.

Video length, storyboard, narration, recording/redaction rehearsal, MP4 creation, uploads and submission are explicitly deferred at the user's request.

## 10. Deferred infrastructure and production gates

Defer AWS app deployment, production DynamoDB/SQS implementations, IAM/runtime credentials, Secrets Manager token persistence, EventBridge/webhook delivery, distributed workers/DLQ, domain/TLS/hosting, production observability/backup policy and CI/CD deployment. Keep the retained Phase 0 AWS stack untouched. No GitHub write operations are introduced.

Also defer broad production auto-apply, the 100–200 fresh human-reviewed benchmark, full comparative model selection, broad multilingual/extractor evaluation and 1,000/5,000-repository performance claims. A curated small workspace demonstrates functionality; it does not establish production scale, exhaustive watch/team/SSO coverage or production data erasure guarantees. Local reset verifies removal from live application records/files selected by policy, not secure forensic deletion, backups or provider retention.

Do not defer core user ownership, source privacy, authorization or reset race safety. If a required functional row cannot be delivered safely, present that exact gap and obtain an explicit scope adjustment; do not call a partially wired shell fully functional.

## 11. Recorded approval and delivery

The user approved the complete Phase 0.9 plan and requested a fully functional local app. This authorizes 0.9A–G, the temporary SQLite/single-process durable runner, the proposed local safety contracts and up to 20 additional OpenAI HTTP requests (at most ten generations) within the unchanged cumulative $5 ledger. Public/synthetic inputs remain the only authorized model data. User-directed preservation of all earlier readiness evidence is an explicit delivery requirement.

The local product is implemented with separate historical entrypoints and owner-isolated application state. Actual fresh AI proof, zero-call reset/replay proof, product/regression validation, remaining limitations and the artifact preservation audit are recorded in [Phase 0.9 results](../validation/phase-0-9-results.md). The user can operate it using the [runbook](../development/phase-0-9-demo-runbook.md).

Normal destructive UI actions still require the app's exact preview and DELETE confirmation. Automated reset tests operate only on isolated disposable fixtures. Approval does not authorize cloud deployment, new AWS work, GitHub writes, private model inputs, deleting historical reports/ledgers or recording/submitting a video. Phases 1–10 remain separately gated.

References: [approved system design](../system-design.md), [execution instructions](../system-design-execution.md), [design history](../design-conversation.md), [full historical discussion](../design-conversation-full.md), [Phase 0 evidence](../validation/phase-0-results.md), [Phase 0.5 results](../validation/phase-0-5-results.md), [latest AI validation](../validation/phase-0-5-round-2-results.md), [implementation plan](implementation-plan.md), [open decisions](open-decisions.md).
