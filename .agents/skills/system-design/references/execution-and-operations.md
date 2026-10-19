# Execution, capability proofs and operations

## Phase by risk and useful behavior

GitHub Manager used three early slices before full cloud buildout. Treat these as a reusable sequencing example, not required numbering:

1. **Capability pretesting:** minimal localhost sign-in, real inventory/content access and named AWS resource checks. Verify the chosen OAuth approach with known fixtures, not only a public repository. Save Markdown evidence and explicit remaining gates.
2. **AI readiness:** offline extraction/retrieval comparisons, schema and registry checks, then bounded real model calls against approved public/synthetic content. Record actual request count, spending, quality and unresolved human review. Restore provider credit without changing the application's authorized cap.
3. **Functional local slice:** complete user workflows using a local persistence adapter while cloud infrastructure remains deferred. Demonstrate authentication, sync, navigation, taxonomy review, classification, manual correction, status, controls and recovery. Preserve earlier readiness work.

For each phase specify inputs/dependencies, exact work, acceptance evidence, failure handling, artifacts and what remains deferred. Avoid declaring “all capabilities established” equivalent to end-to-end readiness. Test order should follow dependencies: start services → authenticate → inventory/content → local organization → bounded live AI when authorized → review/correct → recovery → demo rehearsal.

## Finite budgets and external work

Distinguish HTTP attempts, model generations, count requests, dollars and elapsed time. A “20 calls” limit needs a precise denominator. Provider SDK retries can hide extra HTTP attempts; make retries explicit and count every actual attempt. Reserve conservatively before sending a request, settle on actual usage, and retain unresolved-outcome holds after interruption.

Fixed allowance windows and adaptive budgets solve different needs. Adaptive admission still needs a finite grant, cumulative ceiling and conservative next-call estimate. Selective limit changes must say whether the number is total allowance or additional remaining calls. Renewing a window must not erase cumulative money, receipts or prior reports. Use model-specific, dated pricing and document cache-read/write accounting; do not reuse an old price table as current fact.

GitHub Manager's historical controls used 20 HTTP attempts and 10 generations per default window within a cumulative $5 experiment ceiling. Selectively raising HTTP to 40 after 12 uses leaves 28 attempts. These are case values, not defaults for another product.

## Explicit resets and change triggers

Reset is a product operation with a dependency graph. Show impact by selected scope, bind preview to revision and exact cohort, expire or consume confirmation where needed, then apply atomically. Distinguish deleting mutable organization state, evidence, detailed history and operational receipts. Preserve forensic/cost records according to the approved lifecycle; do not manufacture a fresh allowance by deleting counters.

Automatic organization needs explainable triggers: eligible change types, weighted amount, distinct entities, lookback, quiet period and cooldown. Cosmetic changes should not accidentally trigger expensive work. Meeting a threshold authorizes only the saved behavior and budget policy; it need not imply fresh inference for previously analyzed items. Explicit re-analysis should remain available when the user judges it necessary.

## Validation and preservation

Use offline tests for deterministic behavior and narrow live tests for actual access/model/remote contracts. Test the important failure path, not only the happy path. Mark blocked versus failed versus untested accurately. A browser sign-in or human review may be an optional step; do independent preparation before asking for it.

Save dated Markdown reports with scope, fixture/source version, commands or scenario, measured outcomes, cost/attempt accounting, exclusions and next gates. Keep secrets and private raw material outside publishable reports. Preserve previous benchmarks, ledgers, articles and media. New demos and datasets should not silently replace controlled synthetic fixtures or historical reference scores.

Bind review evidence to the source and annotation version actually inspected. When a binding drifts, compare preserved snapshots before deciding whether another semantic review is needed. Rebinding after a nonsemantic clarification requires proof that the previously reviewed content is otherwise unchanged, plus review of the clarification itself; never overwrite hashes merely to make a gate pass. Preserve substantive corrections and earlier outcomes.

When creating scratch cloud resources, name/tag the exact scope, test real operations and record cleanup status. Access success does not authorize deletion: in GitHub Manager the user explicitly retained the tested stack for further checks. Respect current resource-specific authorization and relevant tool requirements without imposing a new approval ceremony on unrelated reversible work.
