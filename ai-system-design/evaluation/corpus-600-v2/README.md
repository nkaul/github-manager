# Corpus 600 v2: English evidence and relevance first

This version implements the requested cleanup before agent/LLM/human co-annotation. The original `corpus-600` release, source snapshots, benchmarks and reports remain intact. A new release will replace the active evaluation input only after its validation gates pass.

## Execution contract

1. Two agents split the ten existing sampling domains: healthcare, finance, commerce, education and science; data, AI, cloud, security and developer tools. Each domain retains exactly 60 distinct public repositories, for 600 overall. Global numeric GitHub identity deduplicates across domains.
2. Screen every retained README in full for language signals, then inspect purpose-bearing prose, suspicious passages and relevant supporting evidence. English must carry the primary narrative. Names, translated links and code do not disqualify a repository. A complete saved English equivalent can qualify; mixed substantive narratives without such evidence cannot. Machine screening is recorded separately from semantic reading.
3. Exclude thin placeholders, unrelated boilerplate and repositories whose domain association depends on an incidental mention. Preserve exclusions, reasons, quotes and source hashes. Retain relevant tutorials, standards and curated resources only when their actual purpose fits the sampling domain, with an explicit artifact type.
4. Replenish each domain through public, read-only GitHub requests. Prefer evidence-backed family components and useful Topic diversity over dependency mentions. Aim for 30 genuine Project-family members per domain where available; report shortfalls and unsupported concepts rather than inventing associations. Owner caps and duplicate/family controls remain in force.
5. Rebuild inventory, source references, proposed labels, taxonomy coverage, group-preserving splits and review artifacts. Validate hashes and exact evidence against the saved sources. Preserve provenance when a pinned v1 source is reused.
6. Add an authenticated local app collection named **Public - Ground Truth**. Show proposed labels, supporting passages and source documents separately from personal GitHub organization. Persist individual human decisions with version, source identity and revision history. Importing the corpus never means approving its labels.

## Taxonomy status

The v1 seed vocabulary was built upfront to guide discovery: Domains define broad areas; Projects mean actual product/initiative membership; Topics describe purpose/capabilities; Tags describe technologies or properties. Repository assignments can span Projects, Topics and Tags; a Project has a primary Domain. A sampling bucket is not evidence of an assigned Domain. The registry and existing agent labels are **PROPOSED**, with zero human-approved corpus labels at the start of this pass.

The cleanup keeps these definitions explicit, removes unsupported proposals and measures actual coverage. Human approval will freeze a later taxonomy version before the held-out benchmark is used. Missing concepts and ambiguous repositories remain reviewable. Full knowledge extraction, independent LLM labeling, calibrated audit sampling and benchmark evaluation are subsequent steps under the agreed co-annotation approach.

## Persistence and collection controls

Public methodology and tools live here. Ignored local data lives at `docs/validation/private/corpus-600-v2/`: immutable source snapshots, two shards, eligibility decisions, inventory, proposed registry/labels, release manifest and review artifacts. Retained v1 source files may be referenced without copying or modifying them; every reference binds a commit and SHA-256.

The replacement crawl uses a **separate v2 SQLite ledger**, capped at 6,000 upstream HTTP attempts, 120 repository searches and 512 MiB of newly retained content. These are ceilings, not targets. Prior successful public cache entries may be copied as historical cache, with their age and provenance recorded; old requests and old limits are not reset. One credential-isolated loopback broker shares rate limits, claims and deduplication between both agents. No paid model calls or GitHub writes are part of this cleanup.

App review records persist in the existing local SQLite database, namespaced by signed-in user, dataset release and repository. The immutable files remain the evidence source; review edits never overwrite raw snapshots or proposal history. No cloud deployment is introduced.
