# ADR 0003 — Operator-managed local AI allowance windows

Date: October 12, 2026. Status: accepted by the user's request to reset and selectively override the exhausted application allowance.

The original Phase 0.9 proof exhausted both its 20 HTTP attempts and its 44 cumulative generation reservations. Raising only the displayed HTTP limit would leave generation blocked. Deleting the ledger would destroy the testing, spending and cache history the user required us to preserve.

The local application now has a durable allowance control row and append-only change audit beside the existing ledger tables. A renewal records the current lifetime request/generation counts as window baselines, then grants a bounded new window. The display starts at zero for that window; lifetime totals and original authorization remain intact. Selective updates change only the chosen current-window HTTP or generation limits, retaining usage. Limits cannot be lower than recorded window usage, and no unlimited setting is provided. Each selected window limit is bounded to 1,000; zero can pause an unused limit.

HTTP admission and generation admission use the current control row inside SQLite write transactions. The application-specific ledger applies generation admission and the original spending/reservation checks atomically. The frozen Phase 0.5 settings, provider, storage algorithms, records, reports and benchmark references remain unchanged. The cumulative $5 ceiling, uncertain reservations and earlier bound-violation stop remain enforced; renewal does not reset money, authorize private inputs or invoke a model.

Web updates require a real app session, same-origin/CSRF protections and a numeric GitHub ID configured server-side in `DEMO_BUDGET_OPERATOR_IDS`. The allowance is shared by the local provider account across collections and logins; it is not a per-workspace grant. A local filesystem operator can also use the explicit CLI. Changes require a reason and expected policy revision; concurrent/stale submissions cannot renew twice accidentally. Normal organization reset/logout/restart never renews an allowance.

The current user request authorizes one fresh 20-HTTP / 10-generation window for continued testing. Future renewals or selected overrides are explicit operator actions in the app or CLI. This does not expand the production/cloud phase.
