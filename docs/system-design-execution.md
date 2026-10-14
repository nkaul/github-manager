# GitHub Manager — Codex System Design Review & Execution Readiness

**File:** `system-design-execution.md`  
**Companion specification:** [`system-design.md`](./system-design.md)  
**Purpose:** Instructions for using **Codex in VS Code** to review the agreed GitHub Manager MVP design, inspect the actual codebase, formulate an implementation plan, and prepare for either execution or design refinement.  
**Mode:** **Planning and review only** until the user explicitly approves implementation.

## 1. How to use this document

1. Place `system-design.md` and this file at the root of the GitHub Manager workspace, or give Codex their actual relative paths.
2. Open the target repository in VS Code and start a new Codex agent conversation.
3. Ask Codex to read **both documents completely**, inspect the existing repository, and follow the workflow below.
4. Review the proposed design changes, open decisions, phased plan, and acceptance criteria **before authorizing code changes**.
5. After approval, ask Codex to execute **one implementation phase at a time**, showing test results and changes before continuing.

> **Important:** These instructions do not authorize coding, package installation, deployment, AWS resource creation, database deletion, credential access, or GitHub writes. Codex may propose changes and create *planning documents* only. Ask for explicit user approval before taking implementation actions.

## 2. Design baseline: decisions to preserve

Treat `system-design.md` as the **current approved MVP architecture baseline**. Check the codebase against it; do not silently replace the decisions below.

| Area | Agreed approach |
|---|---|
| Frontend | Next.js, TypeScript; repository explorer, content settings, AI status and reset UX |
| Backend | Python/FastAPI with Pydantic, modular API/services/workers |
| GitHub | OAuth-based sign-in and a GitHub App/OAuth App connector abstraction; REST + GraphQL |
| Persistence | **Three DynamoDB On-Demand tables:** Core, Intelligence, Organization |
| Workflows | SQS-backed background sync, extraction, taxonomy discovery and classification |
| First-run taxonomy | Local README parsing, RAKE or appropriately licensed YAKE, corpus TF-IDF; hosted LLM drafts canonical domains/projects/topics/tags; user approval |
| Taxonomy after setup | Full user create/edit/archive/merge, aliases, deduplication and revision tracking |
| Repo association | Cached metadata/phrases and short purpose evidence; LangChain + **strict structured Pydantic output**; validated canonical IDs |
| Source of truth | GitHub owns repo URLs/metadata/access/activity; users own confirmed taxonomy/manual mappings |
| Latest Work | User-specific qualifying work, configurable window (14-day default) |
| AI organization controls | Visible status/history, automatic triggers for significant taxonomy changes, manual incremental/full reorganization |
| Reset | Two independent scope checklists, server preview, type `DELETE`, generation/epoch fencing, selective physical cleanup |
| Explicit MVP exclusions | KeyBERT, local embedding model deployment, vector database, code-wide indexing and AI modification of GitHub repos |

Flag any contradiction between this checklist, `system-design.md`, and the actual codebase. The full design document takes precedence over this shortened checklist; ask the user to resolve any remaining ambiguities.

## 3. Review workflow for Codex

### Step A — Understand the repository and baseline

- Read `system-design.md` **end-to-end**, including diagrams, DynamoDB keys, API contracts, implementation phases, acceptance tests and open decisions.
- Inspect the existing repository structure, package manifests, Python/Node versions, infrastructure-as-code, CI/CD, tests and configuration patterns. **Do not assume it is an empty repository.**
- Identify what exists, what is partially implemented, what is missing and what conflicts with the design.
- Identify relevant local conventions and any `AGENTS.md` or repo-specific developer instructions. Respect them.
- Report missing access, AWS resources, GitHub permissions, model-provider credentials or test fixtures as **dependencies**, not reasons to invent credentials or bypass controls.

### Step B — Perform an architecture consistency review

Check the complete flow, including:

1. **GitHub onboarding:** OAuth/App decisions, repo eligibility, stable IDs, permission coverage, stars/watches, activity and durable repo hyperlinks.
2. **Core persistence:** workspace isolation, read models, paginated `Query`/`BatchGetItem`, materialized My Repos/Favorites/Latest Work views.
3. **Intelligence:** section-aware README extraction, source hashes, keyphrase evidence, TF-IDF aggregation, caching and private-content policy.
4. **Taxonomy:** bootstrap draft, dedup/aliases, canonical ID uniqueness, approval, user CRUD, merges, archives, rejected concepts and revision handling.
5. **Classification:** candidate recall, bounded prompt inputs, structured Pydantic outputs, validation, manual precedence, evidence references and the ability to return no match.
6. **Organization workflows:** async job idempotency, progress/status, auto-trigger debounce, manual reorganization and stale-taxonomy handling.
7. **Reset:** dependent deletion impact, `DELETE` confirmation, preview expiry, epoch/generation fencing **inside write transactions**, physical cleanup and post-reset rediscovery.
8. **Security and reliability:** scoped IAM, server-only tokens, privacy, rate limits, retry/backoff, logging, cost visibility and cross-workspace isolation.

Give special attention to **DynamoDB correctness**: exact PK/SK access patterns, forward/reverse relationship writes, conditional alias reservations, transaction limits, item sizes, pagination, concurrency, stale projections and query costs. Identify where code requires a transaction versus eventual consistency.

### Step C — Identify and prioritize design gaps

Classify findings as:

- **P0 — Blocking:** correctness, security, missing API authorization, permission-model uncertainty, data loss, broken reset safety or unworkable access patterns.
- **P1 — Resolve before the affected phase:** important implementation choices, scalability/cost, user workflows, model evaluation or partial failure recovery.
- **P2 — Refinement:** optional ergonomics, observability improvements and later optimization.

For each finding, include **where in the spec/code it occurs, why it matters, a recommended resolution, alternatives where meaningful, and the decision required**. Distinguish confirmed defects from assumptions needing verification.

Specifically validate the outstanding decisions in section 18 of `system-design.md`; do not silently choose GitHub App over OAuth App, enable private README submission, or substitute a licensed extractor.

### Step D — Create a dependency-ordered implementation plan

Derive a practical build plan from **the actual codebase** and section 16 of `system-design.md`. Organize the work into independently demoable phases:

1. Foundation, repository structure, auth/session shell and DynamoDB infrastructure.
2. GitHub connection, repository discovery, trusted metadata and My Repos/Favorites.
3. Local README/keyword intelligence and persisted repository evidence.
4. Canonical taxonomy registry, alias uniqueness, user CRUD and review interfaces.
5. First-run AI taxonomy discovery and approval.
6. Structured repository association, manual mappings and classification validation.
7. Organization status, change-triggered and manual reorganization.
8. Latest Work and incremental synchronization hardening.
9. Selective Reset & Rediscovery with user confirmation and stale-worker protection.
10. Integration/security/performance validation and deployment readiness.

For **each phase**, specify:

- Objective and user-visible demonstration.
- Dependencies and prerequisite decisions.
- Proposed files/modules to create or change, aligned with existing repo conventions.
- DynamoDB items/indexes and API endpoints involved.
- Implementation sequence and deliberately out-of-scope work.
- Unit/integration/contract tests, fixtures and acceptance criteria.
- Failure cases, rollback/recovery approach, and validation commands.
- Rough complexity (S/M/L) and major uncertainties (avoid false-precision estimates).

Prefer a thin **vertical slice** first: GitHub sign-in → relevant repos → persisted DynamoDB metadata → usable UI, before adding AI features. Use local stubs/fixtures where access to GitHub, AWS or an LLM is not yet available; never present mocked verification as a live integration test.

### Step E — Present results and wait for approval

Create or propose these planning deliverables, using existing repo document conventions (otherwise `docs/planning/`):

| Deliverable | Minimum contents |
|---|---|
| `architecture-review.md` | Current repo assessment, architecture alignment, gaps/risks, recommendations and decision register |
| `implementation-plan.md` | Dependency-ordered phases, module/file touchpoints, APIs/data changes, acceptance tests and phase gates |
| `open-decisions.md` *(optional)* | Decisions needing the user, recommended default, options and impacts |

**Stop after the review and plan.** Present a concise executive summary and a clear approval question: **“Approve Phase 1 implementation, or refine the design/plan first?”** Do not create infrastructure or modify application code before that approval.

## 4. Quality gates for an execution-ready plan

Codex should explicitly report pass / needs work / blocked for these gates:

- [ ] Design requirements are mapped to proposed services, APIs, data access patterns and UI workflows.
- [ ] Existing repository state and conventions are reflected in the plan.
- [ ] GitHub authorization/eligibility/coverage assumptions are called out.
- [ ] DynamoDB keys, item ownership, index/query paths, transaction boundaries and costs are feasible.
- [ ] Taxonomy bootstrap, user edits, deduplication and manual precedence are covered.
- [ ] LLM prompts use limited evidence; structured output and **server-side ID validation** are specified.
- [ ] Trusted GitHub URL/metadata preservation is demonstrated in contracts and tests.
- [ ] Organization runs, revisions, retries and active-job serialization are specified.
- [ ] Reset preview, exact confirmation, physical cleanup and stale-worker fencing are testable.
- [ ] Private-content controls, token handling, workspace isolation and auditability are covered.
- [ ] Each phase has a working demo, automated tests, rollback/recovery strategy and approval gate.
- [ ] Outstanding P0/P1 decisions have an owner or explicit recommendation.

If a gate is unresolved, flag it rather than claiming implementation readiness.

## 5. Ready-to-paste Codex kickoff prompt

Copy the following into the **Codex chat in VS Code** after opening the repository:

```text
Read system-design.md and system-design-execution.md in full and inspect this
repository before proposing changes.

Operate in PLANNING / DESIGN REVIEW mode only. Do not write application code,
install packages, run migrations, create AWS resources, deploy, or modify
GitHub until I explicitly approve implementation.

1. Summarize the proposed GitHub Manager MVP architecture and the current
   state of this repository.
2. Review the design end-to-end, emphasizing GitHub permissions, the three
   DynamoDB tables and access patterns, canonical taxonomy/deduplication,
   token-efficient LangChain classification with structured output,
   organization status/reorganization, and selective reset safety.
3. Identify inconsistencies, missing decisions, security/cost/scalability
   risks, and propose precise refinements ranked P0/P1/P2.
4. Produce an executable, dependency-ordered implementation plan with
   phases, file/module touchpoints, API/data contracts, tests, demos,
   acceptance gates, and dependencies on credentials/cloud setup.
5. Write planning documents architecture-review.md and
   implementation-plan.md under the repository's existing docs convention,
   or docs/planning/ if no convention exists.
6. Give me a short review summary, the unresolved decisions, and your
   recommended Phase 1 scope. STOP and ask whether to approve Phase 1 or
   refine the design/plan. Do not begin implementation.

Keep the accepted MVP constraints: Next.js, FastAPI, three DynamoDB
On-Demand tables, SQS workers, RAKE/YAKE + TF-IDF, hosted LLM via LangChain,
canonical user-controlled domains/projects/topics/tags, structured output,
trusted GitHub metadata, and generation-fenced reset. No KeyBERT,
locally deployed embedding model, or vector database in MVP.
```

## 6. After approval: how to proceed

Once the user approves a specific phase, Codex should:

1. Restate the **approved** phase scope and files to change.
2. Implement only that slice; keep API/data contracts and previous invariants intact.
3. Add tests and fixtures as part of the implementation, not afterward.
4. Run relevant checks and report **commands, results, and any tests that could not run**.
5. Summarize changed files, key decisions, remaining risks and a working demonstration.
6. Stop at the next phase gate and ask for approval or refinement.

Do not interpret approval of a *plan* as blanket approval for destructive operations, production AWS changes, credential access, or deleting GitHub data. Those actions require separate explicit authorization.
