---
name: system-design
description: Review or design application architecture from requirements, repository evidence and recorded decisions; resolve material tradeoffs and produce phased, testable plans. Use for system design, architecture gap reviews or bounded design changes, with optional AI-system and product-workflow guidance.
---

# System Design

Turn a product need into a design whose behavior, boundaries and remaining uncertainties can be inspected. Ground decisions in the current repository and the user's latest direction. The GitHub Manager case study supplies lessons and counterexamples, not a mandatory technology stack.

## Choose the relevant depth

- For a new design, architecture review or ambiguous decision history, start with [requirements and decisions](references/requirements-and-decisions.md).
- For identity, ownership, relationships, APIs, concurrency or access, read [architecture and data](references/architecture-and-data.md).
- When models, retrieval or automated organization are involved, read [AI and evaluation](references/ai-and-evaluation.md).
- For sequencing, capability pretests, budgets, resets or operational readiness, read [execution and operations](references/execution-and-operations.md).
- For user workflows, demos or publication handoff, read [experience and communication](references/experience-and-communication.md).
- For concrete precedents and source provenance, consult the dated [GitHub Manager case study](references/github-manager-case-study.md).
- Before handing off a substantial design, apply the relevant questions in [design review](references/design-review.md).

Load references as their decisions arise. A narrow change needs a bounded design delta, not a new platform architecture.

## Essential working contract

1. Establish the problem, users, useful outcome, constraints and non-goals. Inspect existing implementation before proposing changes to an existing system. Identify the authoritative design and decision history; preserve the latest explicit user choices over superseded proposals.
2. Distinguish **implemented behavior**, **approved target**, **historical alternative**, **measured evidence** and **new proposal**. Cite relevant files or observations. A successful access probe does not prove the full application is production-ready.
3. Trace a representative user action through input, access checks, data ownership, processing, persistence and visible result. State the invariants that must hold when the request is repeated, interrupted, concurrent, stale or partially successful.
4. Compare alternatives where a decision changes cost, correctness, access, quality or delivery risk. Explain the chosen option, consequence, dependency and revisit condition. Do not add speculative components merely to resemble a reference architecture.
5. Separate external facts, user decisions, machine proposals and operational evidence. Design their identities, provenance and lifecycle before choosing storage. Do not conflate a completed analysis with accepted labels, current evidence or human approval.
6. Sequence useful vertical slices around unresolved dependencies. Use bounded pretests for risky access or AI assumptions, then an end-to-end product slice. Define concrete acceptance evidence, failure behavior and what remains deferred.
7. Preserve requested planning gates. When the user asks for a plan before implementation, deliver a reviewable plan and wait; when that scope is already approved, execute it without inventing another gate. Do not infer deployment, paid calls, external publication or destructive cleanup from permission to design.
8. Keep claims proportional to evidence. Record unresolved decisions and known limitations where they affect the conclusion. Preserve previous benchmarks and reports; dated evidence may support a decision without proving that every current path works.

Deliver only the artifacts the task needs: a design delta or architecture review, material decision records, data/API contracts, a dependency-ordered plan and appropriate validation. Prefer a coherent explanation of behavior over an inventory of services.

## Composition

This skill works independently. When available and relevant, use `$illustrated-explainers` for the visual explanation and `$engaging-technical-writing` for an article or publication adaptation. Settle facts, decisions and status first; carry their qualifications into figures and prose. Neither composition nor local artifact creation expands the user's authorization to publish or operate a live system.
