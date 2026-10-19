# Design quality review

Use the questions relevant to the requested change. They are a review aid, not a required new report for every small task.

## Intent and authority

- Does the design solve the user's stated problem and preserve current choices?
- Were current code and approved documents inspected before history supplied rationale?
- Are implemented, approved, historical and proposed components clearly distinguished?
- Is a prior approval honored? Is a requested plan-only gate still respected?

## Behavior and boundaries

- Can a reader trace one real user action from input to visible result?
- Are stable identity, ownership, cardinalities and derived relationships explicit?
- Are user decisions protected from machine proposals, retries and local reconciliation?
- What happens on repeat, concurrency, access loss, partial failure, restart and stale response?
- Are ambiguous remote outcomes retained rather than silently repeated?

## Cost, quality and delivery

- Are external attempts, generation count, dollars and scope independently bounded?
- Does the plan test the access/AI assumptions most likely to block delivery?
- Are current local behavior and deferred infrastructure separated?
- Do evaluation claims match the actual dataset, references, metric denominator and independence?
- Can each phase produce a useful, concrete acceptance artifact?

## Communication and scope

- Do status labels and UI actions reflect system semantics?
- Can a user understand and remediate a conflict without guessing hidden state?
- Does the plan preserve prior reports and user data?
- Are diagrams/articles faithful to the same decisions and evidence?
- Are open questions material, and are defaults marked as project choices rather than universal rules?

For a substantial review, record the issues found, their resolutions and remaining uncertainty. Formatting validation proves skill structure; it does not prove architecture quality, usability, production readiness or real-world model accuracy.
