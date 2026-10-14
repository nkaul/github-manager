# ADR 0004 — Reviewed repository cohorts and finite adaptive budgets

Date: October 13, 2026. Status: accepted in the approved [UI and AI-controls plan](../planning/phase-0-9-ui-and-ai-controls.md).

The local demo needs automatic repository counts and a useful alternative to exhausted fixed request windows. Changing only a displayed counter would leave admission blocked; deleting the original ledger would destroy the readiness history. This extension retains the local Next.js/FastAPI/SQLite architecture and the review-first workflow.

## Cohorts and exact execution

The server resolves cohorts across the full filtered inventory, using the same access/view projection as the explorer and its summaries. Taxonomy samples rotate deterministically across owner/language buckets. Classification prioritizes repositories without project membership, then those without a completed classification at the current taxonomy revision, then recency and stable ID. Counts default to ten and remain bounded to thirty per local run. Manual selection remains available. Private/unverified evidence is excluded from model operations; local rules can use permitted metadata.

Preview performs no provider request. An owner/collection-scoped, five-minute plan stores the input scope, selected IDs, operation, state version, taxonomy/evidence fence, budget revision, price version, cost bound and finite generation/HTTP limits. Execution consumes that exact plan in the app SQLite transaction that enqueues its job. Repeated concurrent Start returns the same job. State, price or budget changes require another preview; execution never silently replaces the reviewed cohort.

Application-only taxonomy packing bounds combined compact evidence and keeps source profiles intact. Provider token counting still checks the complete actual LangChain request, including schema/instructions, before generation. Cached mode has no paid fallback. Live estimates conservatively assume no cache hits; actual cache/rule reuse can use fewer calls.

## Two admission modes, one historical spending ceiling

Fixed mode retains ADR 0003's audited renewal/selective-override controls. Adaptive mode reserves the reviewed run's conservative cost bound under an operator-selected dollar ceiling, initially $0.25. That hold derives a finite grant of at most two HTTP attempts per generation. It authorizes continuation beyond exhausted fixed count limits while preserving the original cumulative $5 ceiling. There is no unbounded grant or automatic renewal.

Run holds, HTTP scope and call-price records are additive tables in the existing spending SQLite database. HTTP admission and generation reservation use write transactions. Generation admission transfers money from the run hold into the call reservation, avoiding double counting. Fixed admissions account for outstanding adaptive holds as well as all earlier settled/uncertain calls. Fixed-window counts exclude adaptive-scoped calls; lifetime request/generation counts include them. Earlier rows and control audit remain unchanged.

New application calls pin their rate snapshot at reservation; settlement uses that saved snapshot. Older calls retain their original pricing behavior. The October 13 application snapshot is based on [official standard short-context pricing](https://developers.openai.com/api/docs/pricing), with conservative cache-write/output reservation and headroom. Estimates are application calculations, not provider invoices or credit-balance readings.

## Recovery and authorization

The app database and shared spending ledger cannot participate in one SQLite transaction. A plan ID links hold and enqueue idempotently. Failed enqueue releases its hold only when no job exists. Reconciliation attaches holds to queued jobs, releases unused money for terminal jobs, and expires unqueued holds after five minutes. A hash of the app database's resolved path prevents one isolated test app from releasing another app's holds. Restart marks interrupted inference without repeating it. Unknown provider calls retain their per-call reservations even when the remaining run hold is released.

Only server-configured numeric budget operators can start adaptive paid work or save adaptive defaults. Authenticated routes preserve Origin/CSRF checks and owner/collection isolation. Saved defaults do not start work. Automatic organization reuses an explicitly saved policy and retains the 90-second quiet period and 30-minute cooldown; it does not increase dollars or fixed limits itself. Each automatic run receives only the finite grant its saved policy admits.

No private content permission, provider destination, model selection, token/output ceiling, GitHub write scope or cloud runtime was added. UI rollback leaves ledger records and uncertain reservations intact. The implementation and measured verification are recorded in the [refinement report](../validation/phase-0-9-ui-and-ai-controls.md).
