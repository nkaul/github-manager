# Architecture review or bounded design change

Replace the parameters with your task details; omit irrelevant fields.

```text
Use $system-design at {{skill-folder}}/SKILL.md.

Project/repository: {{path}}
User problem and desired outcome: {{problem}}
Scope and non-goals: {{scope}}
Authoritative design/instructions: {{paths-or-provided-content}}
Known decisions and constraints: {{decisions}}
Execution authorization: {{planning-only | approved-implementation-scope}}

Inspect the current implementation and relevant decision history. Separate
implemented behavior from approved targets and new proposals. Explain material
tradeoffs, ownership, failure behavior and dependencies. Produce the design
delta or phased plan needed for this scope, with concrete acceptance evidence.
Use the GitHub Manager case only as an optional precedent, not a required stack.
Save outputs to {{destination}} and preserve {{existing-artifacts}}.
```

For a narrow feature, request a bounded design delta. For an AI system, identify the actual retrieval/model boundary and evaluation evidence. For planning only, explicitly retain the approval gate before implementation.
