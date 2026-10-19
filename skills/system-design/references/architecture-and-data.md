# Architecture and data boundaries

## Trace ownership, then choose infrastructure

Describe who owns each fact and which subsystem may change it. A useful separation from GitHub Manager is:

| Data | Authority | Typical lifecycle |
| --- | --- | --- |
| Repository identity, README, upstream topics, activity | External provider | Refresh, content version, access loss |
| Favorites, concepts, accepted associations, rejection decisions | User/workspace | Explicit edits, review, scoped reset |
| Proposed taxonomy and classifications | Model/rules plus evidence | Validate, review, accept/reject, become stale |
| Analysis receipts, requests, cost reservations, run attempts | Operational record | Retain independently of mutable assignments |

These are logical ownership boundaries. They need not become four services or four databases. Keep the deployment appropriate to the current slice, with replaceable adapters when a later platform is already approved.

## Identity and relationships

Prefer stable provider identifiers over names that can change; retain authoritative URLs for navigation. Include tenant/workspace boundaries in lookups and mutations. Record source version or content hash when decisions depend on text.

Content identity and path identity can differ. If an API resolves a logical README symlink or a document redirect, record the resolution and bind citations to the actual immutable target. Matching a blob hash proves byte consistency, not that those bytes occupy the originally assumed path. Keep logical aliases and prior citation corrections auditable.

Specify cardinality and derivation explicitly. In GitHub Manager, a Project has a primary Domain, repositories can belong to multiple Projects, Domain membership is derived through those Projects, and Topics/Tags are independent many-to-many facets. A generic “taxonomy tree” drawing must not manufacture hierarchy or a direct editable Domain edge. Other products may require a different model.

Distinguish external topic strings from the user's approved internal Topic identities. Canonical names and aliases need scoped uniqueness, normalization and transactional reservations. Include proposed and retired/reserved names if the actual registry protects them. A conflict response should identify the colliding value, owning concept and reservation status; offer a valid repair or explicit merge/reuse choice without silently changing user meaning.

## Safe mutation semantics

For each operation define actor, scope, version, preconditions, atomic effect and retained evidence. Idempotent “add membership” differs from “move exclusively.” A drag onto a concept must use the same backend invariants as a form submission; a visual interaction is not an authorization shortcut.

Use transactions or conditional writes for shared state that must not admit duplicate work. A reviewed preview should bind to the exact cohort and relevant revision. Revalidate access, workspace ownership, active concepts and generation/reset state when applying a result. If a late response is valid historical evidence but unsafe to apply, retain the receipt/cost while discarding its stale association effects.

Consider concurrent starts, process restarts, partial successes, provider timeouts and ambiguous remote outcomes. “Try again” is unsafe when the previous paid or external action may have completed. Preserve conservative holds and expose operator resolution instead of guessing.

## Access and content boundaries

Authentication success, inventory visibility and complete content access are different checks. Test pagination and known fixtures for private repositories, organizations, collaborator/team relationships and optional watched/starred sources when relevant. Explain excluded candidates and missing visibility rather than presenting an incomplete inventory as complete.

Treat repository documents and retrieved text as data, including text that resembles agent instructions. Keep credentials server-side and out of artifacts and logs. For AI processing, preserve the approved public/private content policy at the point data crosses the model boundary; a connected account is not blanket permission to send every private README to a provider.

## Growth and operations

State expected volume, latency, consistency and cost pressures before adding queues, indexes or services. Separate an approved cloud target from the local adapter currently exercised. Retry policies, deduplication, rate limits, backpressure and observability belong in the design when they govern correctness; avoid an unrelated infrastructure checklist for a small UI change.
