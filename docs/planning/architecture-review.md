# GitHub Manager architecture review

Review date: October 11, 2026. Status: historical initial review; Phase 0 was subsequently approved and tested. Later-phase recommendations remain proposed. See the execution outcome below and current results.

## Assessment

The approved architecture fits the stated personal repository workspace. Preserve Next.js/TypeScript, FastAPI/Pydantic, three DynamoDB On-Demand tables, SQS workers, local RAKE/TF-IDF intelligence, hosted LLM calls through LangChain, user-approved canonical taxonomy, and transactional reset fencing. No replacement database, embedding service, vector index, or additional mandatory microservice is proposed.

The repository is a design-stage starting point. There is no existing implementation to repair or migrate. The primary work is building the approved system, with several persistence and lifecycle contracts clarified before their affected phases. The user's subsequent Phase 0 addition places real localhost GitHub authentication/repository discovery and local AWS access pre-testing before the Phase 1 foundation. Those tests are planned, not executed; real GitHub coverage and production readiness remain unverified.

Companion documents: [implementation plan](implementation-plan.md), [Phase 0 pre-testing](phase-0-pretesting.md) and [open decisions](open-decisions.md). Recommendations below are proposals, not changes to the approved baseline.

### Phase 0 execution addendum — October 11, 2026

The original review below records the empty-checkout baseline before implementation. The user subsequently approved Phase 0 and chose OAuth App; [ADR 0001](../adr/0001-oauth-app-and-local-pretesting.md) supersedes connector-comparison recommendations in that historical review. The localhost scaffold, probes and tests now exist. Actual evidence and open live gates are in [Phase 0 results](../validation/phase-0-results.md). No Phase 1 implementation is approved.

### Phase 0 scope

Add a minimal, reusable Next.js/FastAPI localhost scaffold and test live GitHub user authorization, known repository relationships, paginated retrieval, organization/SSO/team constraints and star/watch coverage. Validate the selected OAuth App and document organization approvals/coverage gaps. D01 connector choice is resolved; D01 coverage and D02 watches still require live evidence.

Independently validate the intended local AWS profile/account/Region and named project resources (D16). Separate identity and resource inspection from synthetic data-plane canaries, provisioning and future runtime-role access. Cover DynamoDB's three table roles, SQS/DLQ, Secrets Manager, applicable KMS, EventBridge and CloudWatch; conditionally cover S3/model/compute/IaC after selection. Missing resources or permissions stay explicit dependencies. Full write/least-privilege/runtime readiness is not established by STS or Describe/List calls alone.

Phase 0 has no durable application organization state and no AI pipeline; Phase 1 reuses its scaffold and replaces the bounded local-only session/token storage with the approved persistence/security contracts. This preserves the architecture while moving access uncertainty earlier. See the dedicated plan for exact API, test, scratch-resource, evidence and cleanup boundaries.

## Evidence and review boundaries

- Read [AGENTS.md](../../AGENTS.md), [system-design.md](../system-design.md), and [system-design-execution.md](../system-design-execution.md) in full.
- Read [design-conversation.md](../design-conversation.md); inspected the original user decisions and relevant rationale in [design-conversation-full.md](../design-conversation-full.md), especially Messages 24, 26, 29, 32–38 and the DynamoDB/reset discussion.
- Inspected tracked and untracked files, hidden-file inventory, directories, Git status, and recent local history. No additional applicable ancestor or nested AGENTS.md was found.
- Checked current primary documentation for GitHub permissions/watching, DynamoDB API constraints, extractor licenses, and LangChain structured output. This is documentation validation, not account-specific integration testing.
- No application code, package installation, credential access, cloud inspection/provisioning, GitHub mutation, migration, or deployment was performed. Only planning documents were added.

### Actual repository state

| Area | Observed evidence | Implication |
|---|---|---|
| Git | Branch `develop`, tracking `origin/develop`; local HEAD `beb2290` (`Initial commit`) | Local history contains one initial commit; remote freshness was not checked |
| Tracked files | `git ls-files --stage` lists only `README.md` | Guidance/design files are present locally but untracked |
| Existing local additions | `AGENTS.md` and four design/history documents were untracked before review | Preserve them; committing them is a later explicit action |
| `frontend/`, `backend/`, `infrastructure/` | Existing, empty directories, including hidden-file inspection | Use these roots; there are no code conventions or frameworks already installed |
| Manifests/runtime | No package manifest, Python project configuration, lockfile, or runtime pin | Establish compatible pins/startup in Phase 0 and extend reproducible setup in Phase 1 |
| Tests/automation | No tests, fixtures, CI workflow, containers, or developer commands | No executable application test suite exists yet |
| Infrastructure/configuration | No IaC, environment template, resource identifiers, or IAM definitions | AWS resources and credentials are dependencies, not known existing assets |
| README | Project title and one-line description | Developer onboarding must be authored after approval |

These are confirmed inventory findings, not implementation defects. Cloud resources, registered GitHub apps, model access, and organization permissions might exist outside this checkout; their existence was not established.

## Architectural decisions preserved from history

| Historical evolution | Review conclusion |
|---|---|
| PostgreSQL was proposed before the DynamoDB decision (full history Message 32 onward) | No SQL migration is needed; there is no SQL implementation and DynamoDB is the approved target |
| KeyBERT was explored, then explicitly excluded (Message 24) | Do not introduce embeddings or a model deployment for phrase extraction |
| Initial classification evolved into discovery plus association | Keep separate workflows sharing persisted evidence; approved concepts supply stable IDs |
| Post-bootstrap user control and multi-project membership were reaffirmed | Drag/drop adds membership; accepting AI decisions promotes them to protected user state |
| Reset became an MVP demonstration requirement (Message 26) | Design generations, cleanup ownership, and write fencing from the foundation |
| Phrase reuse was added to compact prompts (Message 29) | Preserve purpose sentences and evidence IDs; a keyword bag alone is insufficient project evidence |

## Requirements compared with the checkout

All implementation rows below are missing in code. The distinction is whether the design is sufficiently specified to build them.

| Design requirement | Planned owner / data / API / UI | Design readiness |
|---|---|---|
| Sessions, GitHub connection, workspace ownership (§4, §14) | `auth`, GitHub adapters, Core session/connection items; `/auth/*`, `/me`; login/coverage | Needs session lifecycle contract and real permission spike |
| Relevant repo discovery and Favorites (§4, §9.2) | Sync worker + Core views; `/sync`, `/repos`; explorer/sidebar | Eligibility and watch completeness require validation |
| Local reusable evidence (§5, §7, §9.3) | Intelligence worker, versioned Intelligence partitions; README parser/RAKE/TF-IDF | Needs cache/privacy versions and retention decision |
| Canonical taxonomy (§6, §9.4) | Registry, term reservations, proposals; `/taxonomy/*`; Content/review | Needs publication and merge recovery protocols |
| Manual and structured AI association (§8, §9.5) | Association repository, validator, feedback; membership/review endpoints; chips/drag/drop | Needs projection provenance and concurrent rejection protection |
| Status/reorganization (§10) | Controller, runs, outbox, scheduling; `/organizer/*`; dashboard/SSE | Needs durable dispatch and recoverable run leases |
| Latest Work (§4.4) | Activity worker + Core aggregate/view; `/activity/latest`; smart view | Needs actor attribution and configurable history bounds |
| Reset (§11) | Reset planner, mutation versions, partition catalog, cleanup worker; reset APIs/UI | Blocking physical enumeration and preview concurrency gaps |
| Search/filtering/performance (§9.8, §15) | View queries, reverse-edge merge cursors, bounded inventory filtering | Needs explicit whole-result filtering semantics and cost validation |

## Prioritized findings

Priority describes the consequence if left unresolved. A P0 finding blocks the affected feature or rollout; it does not require abandoning the architecture. Findings are specification gaps unless explicitly identified as externally verified constraints. There are no application-code defects to report.

### P0-01 — Authentication coverage and least privilege are an unresolved product gate

Evidence: design §4.1–4.2, §18; no connector exists. GitHub App resource access is limited by both user access and app access. OAuth `repo` scope includes write privileges, even when this application only calls read endpoints. Both facts are confirmed in [GitHub App token documentation](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-user-access-token-for-a-github-app) and [OAuth scope documentation](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps).

Impact: selecting an app mode without testing could omit required organizations or obtain broader privileges than expected. Effective read permission does not establish direct/team relationship provenance.

Recommendation: preserve both adapters behind one contract; use Phase 0 to compare required coverage with at least two representative organizations, including installed/uninstalled and restricted-team cases, then revalidate in Phase 2. Record each source's confirmed/inferred/unknown provenance. Unknown org-wide access stays excluded by default, with an explicit local inclusion override and visible warning. No silent token escalation. Owner: user for integration choice and organization approvals; implementer for fixtures/spike. Decision D01, Phase 0 evidence and Phase 2 live acceptance.

### P0-02 — Watch discovery must be capability-aware

Evidence: design §2.3, §4.2, §18. [GitHub's June 30, 2026 changelog](https://github.blog/changelog/2026-06-30-upcoming-access-restrictions-to-public-api-endpoints-and-ui-views/) explicitly deprecates `/users/{username}/subscriptions` and describes empty responses. The [watching reference](https://docs.github.com/en/rest/activity/watching) still separately documents `/user/subscriptions`. The named public endpoint restriction does not by itself establish complete or absent authenticated coverage.

Impact: treating an unsupported or restricted empty response as proof of no watched repositories makes Favorites misleading.

Recommendation: exercise `/user/subscriptions` in Phase 0 with the approved token and known watched fixtures; maintain separate star/watch coverage and freshness fields. Preserve known positive observations on transient failures. Mark watch coverage UNKNOWN/PARTIAL/UNAVAILABLE when completeness cannot be established. Favorites remains the union of available trusted sources; do not promise exhaustive watches. Owner: implementer; user approves any documented product limitation. D02, Phase 0 evidence and Phase 2 revalidation.

### P0-03 — Physical reset cannot enumerate the proposed partition layout

Evidence: §9.4–9.6 splits edges by repo/concept/user/automatic epoch and run details by run ID. §11.5 says cleanup will paginate an obsolete epoch, but no catalog enumerates those partition keys. A [DynamoDB Query requires partition-key equality](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Query.KeyConditionExpressions.html); it cannot discover all PKs beginning with an epoch prefix.

Impact: orphaned old partitions, incomplete previews/deletion, or an eventual whole-table scan would violate reset and isolation requirements. Core inventory alone misses associations for repositories no longer in that inventory and old run partitions.

Recommendation: add a workspace-scoped durable partition catalog in Organization before asynchronous writers. Example: `PK=WS#W#PARTITIONS`, `SK=PART#<encoded-table-and-PK>` with table, exact PK, record family, taxonomy/AI/cache epochs, and cleanup state. Register a partition before or atomically with its first data write; retain its entry until deletion is verified. Fixed partitions are explicitly listed too. Cleanup queries the catalog, then exact target partitions, with resumable checkpoints. Alternatively enumerate every entity through equally durable inventories; do not rely on a PK prefix Query or table Scan. D03, Phase 1 contract; verified in Phase 9.

### P0-04 — Reset preview needs a mutation snapshot, not only taxonomy revision

Evidence: §11.2 requires exact counts and rejection when state changed. §9.6 supplies revisions/epochs, but manual edges, accepted suggestions, run records, and cached evidence can change without a taxonomy revision.

Impact: a previously reviewed preview could authorize deletion of newly added manual mappings or misstate selected data. This is a missing concurrency protocol, not a demonstrated bug.

Recommendation: define a `resettableStateVersion` in CONTROL incremented transactionally by every reset-impacting Organization/Intelligence mutation; include it, scope hash, epochs, owner, restart policy and explicit expiry in the reset plan. Freeze relevant writers only after execute wins a conditional CONTROL transition to RESETTING. Preview reads control before/after counting and retries if the version changes. Execute compares the same version and consumes the plan atomically; concurrent changes return conflict and require another preview. Keep transient heartbeats out of impact counts. Measure contention; a scoped version tuple is an alternative if one counter is too hot. D04, foundation contract and Phase 9 implementation.

### P0-05 — Revoked access and changed privacy policy need their own fences

Evidence: §7, §14 require private-content protection and revocation cleanup; §11 counters only represent organization reset. Intelligence keys in §9.3 do not include cache epoch. A delayed worker could otherwise reuse obsolete private content after access/policy changes.

Recommendation: use cache-epoch namespaces for every profile, term, group, discovery artifact and optional S3 object. Gate external-model submission on current connection/repo access and privacy policy, then fence persistence with connection/access/policy versions plus organization/cache versions. On revocation, block reads/submissions and remove restricted cached/derived content through the same catalog. A request already sent to a provider cannot be recalled; define retention separately. Private metadata permission must also be explicit: “metadata-only” does not mean “public.” D05, contracts in Phases 1–3; live-model gate in Phase 5.

### P0-06 — Manual precedence must survive an in-flight classifier

Evidence: §8.4 and §9.5 require locked USER edges/rejections to win, but the listed CONTROL tuple does not change on a manual edge edit. Checking feedback before an LLM call is insufficient.

Recommendation: add per-repo `decisionVersion`; all manual membership changes, acceptance and rejection increment it. Classification commits condition on its captured value inside the association transaction, plus current ACTIVE concepts and CONTROL. On conflict re-read and preserve the user decision. Protect RULE writes too. D06, Phase 4 manual slice and Phase 6 classifier. Test rejection while classification is paused before commit.

### P1-01 — Large taxonomy publication needs one visibility boundary

Evidence: §5.4 publishes revision 1 through bounded transactions; §9.7 limits transaction size. Multiple successful batches followed by failure could expose a partial approved taxonomy.

Recommendation: stage approved concepts/reservations under a publication manifest, hide staged concepts from normal reads, validate all batches, then perform one conditional activation/revision update. Serialize publication against taxonomy edits/reset; support resume and cleanup of abandoned staging. Bootstrap and expansion must both preserve earlier canonical IDs. Do not advance taxonomy epoch for ordinary publishing. D07, Phases 4–5.

### P1-02 — Durable dispatch and run recovery are missing contracts

Evidence: §3 and §10 require idempotency and one active run; no items describe DB-write/SQS-send recovery or a crashed worker's lease.

Recommendation: transactional outbox records with an exact workspace Query path; periodic dispatch recovery from durable workspace inventory; application-level per-item idempotency; recoverable leases with expiry/heartbeat; deduplicated counters committed with outcomes. DynamoDB request tokens alone do not cover arbitrary queue redelivery. A stale worker must not recreate selected history merely to record its cancellation. D08, Phase 1 and all workers; scheduler/status UX in Phase 7.

### P1-03 — Explorer summaries can lose manual topic/tag provenance

Evidence: §9.5 splits manual/automatic projects, but combines `topicIds` and `tagIds` under one `autoEpoch`. Ignoring those combined lists on AI reset cannot selectively preserve manual labels.

Recommendation: separate USER and AUTO IDs for every supported kind, plus per-repo decision/projection versions and a projection-dirty marker. During partial archive/reset, read APIs suppress inactive concepts immediately rather than waiting for summary cleanup. Forward/reverse edges remain authoritative. D06, Phases 4 and 6; reset tests in Phase 9.

### P1-04 — Sessions and small API boundaries are underspecified

Evidence: §4.1 and §12 specify a cookie but no session/state persistence, logout/disconnect route, explicit inclusion override route, or privacy-settings contract. Domain edges appear in §9.5, while §8.4 derives domains from projects and §12 has no manual domain route.

Recommendation: opaque server sessions and one-time OAuth state with explicit expiry checks; session rotation/revocation and CSRF for mutations. Add proposed logout, connection-disconnect, repo-inclusion and privacy-policy routes. Decide whether direct domain membership is allowed; recommend deriving repository domains from projects for MVP, while retaining full Domain CRUD. This is a user-visible ambiguity requiring D09 approval, not a silently removed capability.

### P1-05 — Paging/filtering and edge unions need explicit semantics

Evidence: §9.7–9.8, §13 support filters, pagination and USER/AUTO reverse-edge unions without cursor contracts.

Recommendation: opaque cursors bound to workspace, view, filters, sort and epochs; merge sorted reverse-edge streams with deduplication and independent continuation positions. For initial MVP complex filtering, query a bounded complete compact workspace inventory and filter/sort before pagination; never label a filter over one page as a global result. Budget inventory bytes and expose an explicit supported limit. Uncategorized uses zero active project edges, not classification status or tags. D10, Phases 2/4/6; benchmarks in Phase 10.

### P1-06 — Classification safety limits and evaluation are not selected

Evidence: §8.2–8.4 and §18 define targets, but the response example lacks list/string bounds on several fields; provider, model, token counting and quality thresholds remain open.

Recommendation: bounded strict Pydantic fields, status/assignment consistency, valid candidate/evidence IDs, deduplication and per-kind caps. Provider-specific refusal/timeout handling and actual schema-inclusive token accounting. Start with review-first AI; rules apply only when user-approved. Evaluate 100–200 labeled repos and candidate recall before broad automatic application. A valid schema never establishes a valid workspace concept. D11, Phases 5–6.

### P1-07 — Bulk operations and transactions need an action budget

Evidence: §6.3, §9.4–9.7 call for alias uniqueness, mirrored edges, summaries, counters and control fencing. No exact action budget or merge checkpoint schema is provided.

Recommendation: budget actions and bytes before submission; deduplicate per-concept checks and normalized aliases. Use one conditional Update when also changing CONTROL, rather than a separate check of the same item. Merges use a redirect and resumable per-repo migration, resolving USER/rejection conflicts conservatively. Archiving a domain moves surviving projects to a protected explicit Unassigned domain. D07/D09, Phases 1/4/6.

### P1-08 — Latest Work and destructive cleanup sequencing need policy gates

Evidence: §4.4 counts user activity, not repo pushes; §11.6 allows policy-dependent cleanup/restart overlap. Neither actor-event coverage nor retained history bounds are fixed.

Recommendation: use durable GitHub actor IDs and documented event coverage, bounded history retention supporting the configurable window, and unknown coverage flags. Recommend verified physical cleanup before reset restart for the initial MVP; concurrent rediscovery is a later option requiring clear UI and retention approval. D12/D13, Phases 8–9.

### P2 — Hosting and advanced search are evidence-driven refinements

Evidence: §15 and §18 leave API hosting and compound-filter scaling open. No IaC choice exists.

Recommendation: keep compute-independent service/worker entrypoints and polling fallback; benchmark idle cost, callback behavior, worker duration and SSE support before choosing production Fargate/Lambda placement. Do not add OpenSearch or an extra service preemptively. Hosting choice becomes a prerequisite to deployment rather than remaining P2 at launch. D14/D15.

## Persistence feasibility and transaction ownership

### Preserve the three table boundaries

| Table | Authoritative items | Read paths | Reset/access behavior |
|---|---|---|---|
| Core | User/connection/workspace; repos keyed by host + numeric ID; sync/activity; proposed sessions/state | Exact Get, view Query, bounded BatchGet; workspace directory Query for scheduling | Organization reset preserves it; disconnect/access revocation has separate policy |
| Intelligence | Profiles, evidence, corpus terms/groups and discovery inputs under cache epoch | Exact current-profile Get; workspace/cache Query with continuation keys | Selected cache reset changes namespace; every writer is fenced |
| Organization | CONTROL, taxonomy/terms, USER/AUTO mirrored edges, summaries, runs/feedback/reset; proposed catalogs/outbox/manifests | Exact Get/transaction; exact-PK paginated Query; BatchGet summaries | Epoch-aware reads; explicit cleanup using catalog; minimal reset audit retained |

The optional pending-control GSI is only a scheduling hint. Base-table authorization and commit fencing remain authoritative. Single-workspace partitions and CONTROL contention are acceptable hypotheses for a personal MVP, not proven performance results.

### Required atomic units

| Operation | Same-transaction invariants | May be eventual/resumable |
|---|---|---|
| Create/edit concept | Concept + normalized name/alias reservations + revision/change/outbox + conditional CONTROL update | Large merge/migration and nonauthoritative counters |
| Manual assignment/remove/accept/reject | Both edge directions + USER feedback + repo decision version + summary or dirty marker + reset mutation version | Rebuild projection only if explicitly marked dirty |
| Classifier result | CONTROL fence + repo decision/access/policy fence + concept ACTIVE checks + mirrored edges/suggestion + per-item outcome/idempotency + reset version | Fan-out over other repos; dashboard aggregation |
| Intelligence result | Organization/cache/policy/access fence + versioned profile/corpus contribution + reset version | Corpus rebuild from a versioned snapshot |
| Execute reset | Validate/consume plan + compare snapshot + advance only selected epochs/generation + RESETTING + audit + cleanup outbox | Physical deletion/checkpointing and restart |
| Job request | Durable run/request + outbox + conditional active-run claim/lease | SQS delivery and retry; not an unguarded DB-then-send operation |

AWS permits at most 100 transaction actions/4 MB and prohibits two actions targeting one item; a conditional Update must carry its own fence. Keep all three tables in one account/Region for cross-table fencing. See [TransactWriteItems](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_TransactWriteItems.html).

Use roughly `fixed actions + 3 × distinct concepts + reservations/feedback` as an initial classifier sizing model (two edge writes plus one concept check); compute actual counts, including replaced edges, manifests and summary writes, per operation. Cap assignments/aliases and split bulk operations into resumable units. Never split one logical edge pair across transactions.

Query pages require `LastEvaluatedKey`, including empty filtered pages; hydration must retry unprocessed keys, preserve order by key, and respect the 100-item/16-MB batch cap. See [Query pagination](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Query.Pagination.html) and [BatchGetItem](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_BatchGetItem.html). No GSI or eventually consistent summary can prove deletion or authorize a reset. TTL is only housekeeping, not physical-reset verification ([AWS TTL documentation](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/TTL.html)).

## Dependencies and readiness gates

| Dependency | Needed by | Owner / evidence required |
|---|---|---|
| Approved Phase 0 scope and named GitHub/AWS test targets | Phase 0 | User; local scaffolding and operation-level probes remain pending approval |
| Approved phase scope and proposed persistence refinements | Phase 1 | User; this plan is pending review |
| Compatible Node/Python/package tooling and IaC convention | Phase 0 tooling; Phase 1 IaC | Implementer pins supported versions after approval; proposed defaults in D15 |
| Local DynamoDB/SQS integration environment | Phase 1 | Implementer defines reproducible local setup; emulator results labeled as such |
| Registered app, callback URLs, organization permissions and known repo/watch fixtures | Phase 0 live pre-testing; Phase 2 revalidation | User supplies authorized integration path; no credentials requested or inspected in review |
| AWS local profile/account/Region/IAM and named sandbox resources | Phase 0 operation-level access; later live integration/deployment | D16 scope and approved scratch operations; mocks cannot satisfy AWS acceptance; local developer success does not prove runtime-role access |
| Private metadata/README policy, access revocation and retention | Before private external-model calls | User/organization policy owner; D05 |
| Exact RAKE dependency and bundled tokenizer/stopword resources | Phase 3 | Implementer verifies pinned package/license; YAKE needs its separate review |
| Hosted model provider, allowed data/region, quota, budget and provider retention | Phase 5 | User policy/billing owner; implementer contract tests |
| 100–200 reviewed repo labels, including multi-project and no-match examples | Phase 6 quality gate | User/domain reviewer plus implementer; synthetic fixtures do not replace quality evidence |
| Production hosting/domain/secrets/CI permissions | Phase 10 | User and implementer; explicitly unresolved, no deployment authorized |

### Execution-document quality gates

| Gate | Review status | Remaining evidence |
|---|---|---|
| Requirements mapped to services/APIs/data/UI | PASS for planning | Traceability above and phase contracts |
| Actual checkout/conventions reflected | PASS | Empty implementation roots reused; no migration assumed |
| GitHub eligibility/coverage assumptions called out | NEEDS WORK | Phase 0 two-organization spike and authenticated watch test, then Phase 2 revalidation |
| DynamoDB key/query/transaction/cost feasibility | NEEDS WORK | Approve catalog/version/publication refinements; emulator and AWS contention checks |
| Bootstrap, dedup, edits and manual precedence covered | PASS for planning | Race tests and workflow demos remain future work |
| Bounded prompts and semantic ID validation specified | PASS for planning | Model adapter/token accounting still unverified |
| GitHub URL/metadata preservation demonstrated | NEEDS WORK | Contracts planned; executable tests do not exist yet |
| Runs/revisions/retries/serialization specified | NEEDS WORK | Outbox/lease and fault-injection tests pending |
| Reset preview/cleanup/stale fencing testable | NEEDS WORK | D03–D06 refinements and Phase 9 race suite |
| Privacy/tokens/isolation/audit covered | NEEDS WORK | Policy approval and auth/security tests pending |
| Each phase has demo/tests/recovery/approval gate | PASS for planning | See plan; none of those tests has run |
| P0/P1 decisions have owners/recommendations | PASS for planning | See decision register; pending is not approved |

Live-integration gates are BLOCKED until authorized services, permissions and fixtures are available. Phase 0 adds the earliest real-service evidence; local fixture-based development can proceed within an approved phase but cannot close those live gates. Overall: planning ready for review; production implementation readiness is not claimed.

## Proposed approval boundary

Current execution outcome: the latest user-authorized Phase 0 work verified both named private fixtures, fixed and live-verified a 78-repository organization discovery omission, and passed all eight required AWS scratch targets through creation/inspection/canaries. The user requested retaining the scratch resources. See [combined results](../validation/phase-0-results.md) for remaining policy/provenance limitations and the conditional exit recommendation. This adds no new production architecture or Phase 1 authorization.

Phase 0 was approved after this review: localhost Next.js/FastAPI, OAuth App authorization/repo fetching, source coverage and local AWS access pre-testing within named approved targets. Scratch writes/provisioning require the concrete manifest and allowed operations to be covered by that authorization. The baseline above predates implementation; follow the execution addendum and current results for actual status.

Review Phase 0 results and unresolved access dependencies before approving Phase 1's durable sessions/workspace authorization, persistence/job contracts, three-table local schema, catalog/fencing/outbox foundations and CI. Private-content submission, production AWS changes and deployment retain their separate prerequisites.
