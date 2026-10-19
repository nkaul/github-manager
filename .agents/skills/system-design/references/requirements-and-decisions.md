# Requirements and decision history

## Recover intent before architecture

For an existing project, locate its agent instructions, approved design, execution plan, current code and historical conversation. Read the current design before using history to explain its rationale. Keep a small evidence ledger: requirement or decision, source/date, current status, consequence, unresolved question. A reconstructed conversation is historical evidence, not a verbatim transcript.

Use the project's declared source priority. GitHub Manager used latest explicit user instruction → approved system design → approved plan → historical conversation. Another project may designate a different authority. If sources conflict, state the conflict and resolve it with current authorization; do not silently revive an abandoned option.

Define the product with a concrete trigger and outcome. For example: a user has hundreds of accessible repositories, needs to find related work, and should review a proposed organization without repeatedly paying to analyze the same repository. “Add AI” does not specify that behavior. Ask only for missing information that materially changes the design; advance independent review while clarification is pending.

## Review the actual system

Trace at least the requested path in code, configuration and existing validation. Record gaps as:

| Gap | Observed behavior | Required behavior | Dependency | Acceptance evidence |
| --- | --- | --- | --- | --- |
| Example: analysis repeated | Missing Project schedules another call | Prior successful analysis remains recognized | Durable receipt + common admission guard | Repeat run makes no provider requests, including count calls |

Separate a documentation gap from a functional gap. Distinguish unavailable evidence from a demonstrated defect. Read-only inspection and reversible preparation can proceed within scope; writing a plan does not authorize the implementation the user asked to review first.

## Make material decisions reviewable

Use a lightweight decision record when alternatives matter:

- **Context and constraint:** what user action or risk forces this choice?
- **Options:** viable alternatives, including retaining current behavior when useful.
- **Decision and status:** proposed, approved, implemented, superseded or deferred.
- **Consequences:** gains, costs, failure modes and operational burden.
- **Dependencies and validation:** what must be true, and how will we know?
- **Revisit condition:** a measurable change that would justify reconsidering it.

Avoid scoring matrices with invented precision. A local SQLite demo versus an AWS deployment is a delivery-sequencing choice as well as a database choice. OAuth App versus GitHub App is an access and product choice; use the chosen approach and test its actual limitations rather than replacing it because another option is fashionable.

## Plan around uncertainty

Rank unresolved issues by their ability to block the next useful slice. Authentication, organization/private visibility, named cloud resources and real model access are often worth early bounded tests. Cosmetic decisions rarely justify blocking access tests. Time-box a probe by attempts, data scope and acceptance criteria rather than retrying until something works.

Do not convert every uncertainty into a permission question. Use evidence and reasonable implementation judgment inside approved scope. Surface only decisions whose answer materially changes user-visible behavior, commitments or authorized side effects.
