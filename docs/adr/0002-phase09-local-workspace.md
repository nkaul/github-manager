# ADR 0002 — Approved local application adapter for Phase 0.9

Date: October 12, 2026. Status: accepted for the local demo by the user's Phase 0.9 plan approval.

The user requested a complete working local MVP before cloud infrastructure or video planning. This brings the product workflows from later phases into an operable local app while preserving the approved production architecture and all earlier readiness evidence.

Use Next.js, the existing OAuth App connector/session protections, FastAPI, and a single-process durable SQLite job runner. The workspace repository boundary exposes read/mutate transactions and atomic job creation. SQLite stores owner/collection-scoped Core, Intelligence and Organization aggregates; transactions also bind normalized concept reservations, assignments, reset previews and generation fences. This bounded adapter supports 500 concepts and 30 repositories per organization run. Durable jobs wait for reauthentication; interrupted inference requires explicit review/retry, while local reset cleanup is resumable. Distributed queue/lease semantics remain production work.

`app.main` remains the historical preflight entrypoint. `app.local` extends it without altering earlier pre-testing algorithms, tests or reports. The original UI is retained as `Preflight.tsx` and selected with `GHM_UI=preflight`. The product UI is the default. New extraction corrections are versioned in the application wrapper rather than rewriting frozen benchmark outputs.

GitHub credentials stay in memory. Application state uses ignored private storage and is independent of historical reports and the original API ledger. Owner and sample collection boundaries apply to all reads and writes. Domains derive through projects; accepted suggestions become USER decisions. Explicit removals create protected rejection tombstones. AI remains review-first and receives only verified public or labeled synthetic evidence. Metadata-only local rules may operate on private repositories.

The approved bounded renewal is 20 additional OpenAI HTTP attempts, including token counts, with at most ten additional generations and the original cumulative $5 ceiling. A separate durable request table is added to the original ledger, preserving all earlier call records, cached results and experiment identity. Reset cannot regain requests or money. Unknown requests consume slots; uncertain charges stay reserved. The original Phase 0.5 generation ceiling remains unchanged; only the new application adapter permits the approved extension.

Reset binds the exact scope/counts, owner, aggregate version, expiry and a one-use plan. Exact `DELETE` advances generation/epoch fences before cleanup. Selected application records are removed transactionally, dependencies reconciled and verified before optional restart. AI-only reset preserves USER mappings and rejections. Full taxonomy reset starts revision zero in a new epoch. The audit and GitHub/Core state remain. This is application-record deletion, not forensic erasure or deletion of historical benchmark/provider caches.

Production DynamoDB/SQS, AWS changes, hosting, GitHub writes, private model inputs, broad auto-acceptance and recording/submission remain outside this approval. The retained AWS scratch stack is untouched. D03/D04/D06/D08/D09/D13 directions are adopted locally; their production implementations remain open. D18/D19/D20 are approved for this phase.

References: [approved plan](../planning/phase-0-9-functional-demo.md), [system design](../system-design.md), [validation](../validation/phase-0-9-results.md).
