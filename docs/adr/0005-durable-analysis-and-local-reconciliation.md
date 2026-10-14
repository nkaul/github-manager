# ADR 0005 — Durable analysis receipts and local reconciliation

Date: October 13, 2026. Status: Accepted under the user-approved taxonomy/status plan and explicit re-analysis requirement.

## Decision

Keep compact, owner/repository-scoped analysis receipts in Organization data, independently of optional run history, suggestions, accepted memberships and the provider replay cache. The local SQLite adapter stores these additive fields transactionally in the workspace aggregate. A future cloud adapter should preserve the same invariant in the Organization table; no cloud deployment is introduced here.

Classification and collection taxonomy discovery have separate receipts. Validated actual model/replay success, including NO_MATCH, records `ai_analyzed`; test fixtures stay labeled FIXTURE and do not claim real AI completion. Successful per-repository outcomes from partial runs are eligible for offline backfill. Legacy unknown provenance remains unknown. Surviving validated taxonomy drafts can establish prior taxonomy inputs. Backfill makes no provider requests.

Admission is checked in both the preview and the shared worker, before provider construction or token counting. Ordinary processing skips previously successful, failed/uncertain and legacy-unknown attempts for fresh inference. Newly ingested repositories have an explicit NEW state. A transaction claims each approved attempt before dispatch; an interrupted attempt is uncertain and is not automatically repeated.

An explicitly reviewed Live AI re-analysis plan, with a reason and exact cohort/cost bound, can authorize fresh taxonomy or classification inference. It passes `fresh=True` through the existing provider, retaining its schema/privacy/access checks, finite fixed/adaptive admission and original cumulative $5 ceiling. The legacy route cannot request this bypass. Previewing or saving settings makes no model calls.

Persist a validated response receipt before attempting its fenced association commit. If the workspace changed, keep the historical processing fact and discard stored assignment references. Resets invalidate incompatible references while retaining the processing fact. History deletion, manual/drag assignments, rejection and lack of a Project do not grant new inference permission. Provider cache deletion does not reset the durable guard or spending.

## Automatic organization

Expose weighted change, distinct-entity and new-project thresholds, eligible types, lookback window, quiet period and cooldown. The default condition is weight ≥6 AND entities ≥3, OR ≥2 new projects, within 900 seconds; wait 90 quiet seconds and 1800 cooldown seconds. The project branch can be disabled with zero. Cosmetic edits are excluded. Evidence refresh can record an EVIDENCE event without changing taxonomy revision. Consumed event sequences prevent unchanged edits from scheduling repeated runs.

Automatic jobs use the shared preview/admission path and saved count/budget policy. Previously analyzed repositories reconcile offline. Genuinely new eligible inputs may use AI. Automatic paid re-analysis is not enabled by changing these thresholds. Unobserved upstream README changes cannot be detected locally: Extract evidence refreshes verified public metadata/README evidence, while GitHub sync can observe metadata changes. Cloud webhooks/polling remain deferred.

## Local organization and presentation

Label coverage, analysis outcome, freshness and pending review remain independent. No project means no active Project edge; Topics and Tags are useful accepted labels in their own right. Domains derive through Project membership. Counts use accessible repositories across the filtered scope, independently of pagination.

Manual mapping and approved rules remain local. Compatible stored assignments may be proposed again with STORED_ANALYSIS provenance. TF-IDF candidate retrieval followed by canonical/alias evidence matching can produce LOCAL_MATCH proposals for human review. Neither is a new AI analysis. USER decisions and rejection tombstones take precedence.

Both taxonomy browsers support Project/Topic/Tag additions and a Domain-to-Project picker. Selected-set drops show the exact set before saving. Duplicate mappings are idempotent. Batch suggestion review validates each selected item against one snapshot, reports stale/inaccessible cases and preserves valid siblings.

## Consequences

Repositories can be labeled, have no Project and have completed AI analysis at the same time. Unknown historical input fingerprints are disclosed rather than inferred. A changed taxonomy marks old analysis stale without making it eligible for another paid request. Local heuristics cannot guarantee correct new assignments and always require review. Re-analysis stays available when the user decides that new evidence or taxonomy justifies another bounded model call.

See [the approved plan](../planning/phase-0-9-taxonomy-browsing-and-status.md), [runbook](../development/phase-0-9-demo-runbook.md) and [validation report](../validation/phase-0-9-taxonomy-and-analysis.md).
