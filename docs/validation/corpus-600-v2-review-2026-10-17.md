# English corpus v2 and Public - Ground Truth workspace

Review date: October 17, 2026 (curation began October 16). Release: `public-corpus-600-english-2026-10-16-v2-PROPOSED`. Collection, source audits and app activation complete. The updated production app is running at http://127.0.0.1:3000; sign in again if the restart expired your browser session.

## Outcome

Two agents completed a fresh English-first eligibility/relevance pass and replenished the collection to **600 distinct public repositories: 60 in each of ten sampling domains**. The active set retains **489 original repositories** and adds **111 replacements**. Two retained repositories were reassigned to more appropriate sampling buckets. The original v1 dataset, evidence, proposed references, tooling and reports are preserved: **2,416 manifest-bound original files checked, zero changes**.

The original active set lost 77 repositories with substantive non-English primary narratives, 18 with inadequate/off-domain evidence, and 16 valid English repositories reserved to improve coverage. These categories are different: a balancing reserve is not defective and is not a negative taxonomy label. Failed new acquisition attempts and new candidate reserves have separate local audits.

This corpus is ready for evidence review and the agreed co-annotation pilot. **It is not yet human-approved ground truth or a completed LLM classification benchmark.** Human-confirmed labels start at zero. Browser-test confirmations use disposable SQLite state and never enter the real corpus or the user's review records.

## Coverage and balance

| Sampling domain | Total | Original retained | New replacements | Repositories with supported Projects | Development / validation / held-out |
|---|---:|---:|---:|---:|---:|
| Ai | 60 | 42 | 18 | 30 | 18 / 12 / 30 |
| Cloud | 60 | 51 | 9 | 30 | 18 / 12 / 30 |
| Commerce | 60 | 51 | 9 | 37 | 18 / 12 / 30 |
| Data | 60 | 48 | 12 | 30 | 18 / 12 / 30 |
| Developer | 60 | 54 | 6 | 31 | 18 / 12 / 30 |
| Education | 60 | 39 | 21 | 31 | 18 / 12 / 30 |
| Finance | 60 | 51 | 9 | 33 | 18 / 12 / 30 |
| Healthcare | 60 | 50 | 10 | 36 | 18 / 12 / 30 |
| Science | 60 | 53 | 7 | 27 | 18 / 12 / 30 |
| Security | 60 | 50 | 10 | 23 | 18 / 12 / 30 |

Project counts above are distinct repositories with at least one **SUPPORTED** Project. UNKNOWN proposals do not count, and multiple Projects count a repository once. There are **308** such repositories overall. Independent implementations, instructional material and useful neighbors remain in the corpus; an empty Project list does not imply irrelevance or global no-match.

Balance is exact across sampling domains and splits. Family membership is intentionally uneven. For example, one family can have many dedicated components while another has only its canonical implementation. Report both macro scores by domain/family and overall scores later; do not allow a large family to conceal a weak one.

The registry contains **10 Domains, 64 Projects, 166 Topics and 97 Tags**. Supported proposals cover **63/64 Projects, 160/166 Topics and 97/97 Tags**. All planned data, AI and science families are represented. Trivy remains an acquisition gap after four pinned-commit acquisition requests returned HTTP 403; this does not establish a general OAuth failure, and its membership was not fabricated. Six proposed Topics have no current supported positives: Public Health Reporting, Hydrology, Schema Management, Compiler Construction, Data Privacy Protection and Facial Recognition. This can reflect source selection or incomplete annotations; it is not proof those capabilities are absent from the entire corpus.

## Did we build the taxonomy upfront?

**Yes, the initial Domains, named Project families, membership definitions and initial Topics were curated before discovery.** They guided the search, but were never an approved answer key. Source review added technology Tags and additional narrowly defined Topics. This pass adds four proposed Topics: Human Resource Management, Code Generation, Data Platform Integration and LLM Framework Integration. None is automatically human-approved.

A Domain is a broad area; a Project is an actual product/initiative/component relationship; a Topic describes primary purpose or capability; a Tag describes a technology/property. Domains derive through Project parents. Sampling Domain is a collection-control field, not an assigned taxonomy label.

For example, the NumPy dossier proposes Project **NumPy**, Topics **Scientific Computing** and **Numerical Linear Algebra**, and Tag **Python**. The Project supplies its Science Domain. An independent scientific tool can have useful Topics and Tags without belonging to NumPy merely because it uses NumPy.

The corpus exposes why source reading matters. Vercel Commerce lists other providers but explicitly maintains Shopify; that is not automatic Saleor/Medusa membership. Frappe HR describes a product split, so ERPNext membership is not inherited automatically. A payment-receipt adapter consumes an upstream risk decision; the peer audit corrected its overbroad Financial Risk Management proposal to UNKNOWN. Citation containment checks prove that text exists; they do not prove semantic entailment.

## Evidence, reading and verification

The active release retains **600 complete READMEs and 1,223 supporting files**, totaling **18,436,109 source bytes**. Each source is bound to a Git commit, repository numeric ID, path and SHA-256; Git blob integrity is separately checked during acquisition. Reused v1 files remain unchanged and are referenced directly. Public metadata is an acquisition-time snapshot; commit pinning applies to files, not an assertion that metadata never changes.

Every active repository has a source-backed English/relevance decision. Whole-file language screening is combined with agent inspection of purpose, suspicious passages, headings and relevant supporting evidence. Normal names, Unicode, code and translation links are not language failures. Optional translated documents are omitted from active English evidence where appropriate, while original snapshots and omission history remain available.

**Machine processing is not full semantic reading.** The release records 88 complete README semantic reads and 512 targeted/partial reads; full source retention is separate. The next co-annotation phase must extract fuller knowledge where required. The read-scope audit verifies 1,746 quoted evidence items against actual recorded source intervals; it is a consistency audit, not a comprehension score.

Each agent independently reviewed 60 cases from the other cohort: twelve per owned domain, with risk-selected and reproducible random halves. **120 distinct final reviews have current source/annotation bindings**, with the receipt-risk correction and original finding retained. Peer agreement supports the inspected claims; it does not prove exhaustive label completeness, human correctness or calibrated confidence. Legacy HIGH wording remains explicitly uncalibrated and cannot authorize auto-acceptance.

Source/hash/coordinate, directory binding, registry reservation and reading-scope audits pass. The grouped splits preserve related Project families, shared-owner groups, recorded lineage and detected near-duplicates. They achieve exactly **18 development, 12 validation and 30 held-out repositories per domain**, while keeping every leakage group intact. The largest group contains 36 repositories. Splits remain provisional until taxonomy/reference approval; corpus-informed taxonomy design is not an unseen-registry benchmark.

One raw dossier contains two proofs of the same Python label, one README-based and one metadata-based. The app merges these into one selectable label while preserving both evidence items and the immutable raw proposal. Evaluation adapters must score unique canonical IDs, not duplicate evidence occurrences.

## Collection allowance and persistence

The new collector used **902 upstream HTTP attempts, including nine repository searches**, and retained 3,457,838 new source bytes including rejected/reserve content. Its separate ceiling was 6,000 HTTP attempts, 120 searches and 512 MiB. Cached successful public responses were copied from the old ledger; old request history was not reset. Historical pinned snapshots were reused rather than claiming every retained repository was fetched live again. The temporary broker is stopped. **Paid model API calls for this cleanup: zero.**

Data locations:

- `docs/validation/private/corpus-600/`: preserved v1.
- `docs/validation/private/corpus-600-v2/shards/a/` and `shards/b/`: dossiers, eligibility decisions, exclusions, balancing reserves, reading intervals and producer histories.
- `docs/validation/private/corpus-600-v2/sources/`: newly retained pinned sources; reused v1 source references remain in v1.
- `docs/validation/private/corpus-600-v2/release/`: manifest, inventory CSV/JSONL, proposed labels/registry, annotation-free input allowlist, grouped splits, combined reference-only content, review sheets and audits.
- `docs/validation/private/corpus-600-v2/cross-review/`: independent packets, final verdicts and correction history.
- `docs/validation/private/demo/app.sqlite3`: application state and owner-scoped review records; a backup was taken before activation.

The combined reference-content JSONL includes labels and must not become model input. `inputs.jsonl` explicitly excludes annotations, eligibility decisions, discovery queries and review outcomes. Original source text is displayed as escaped plain text, including any embedded HTML/instructions.

## App review interface

Open the local app, authenticate, and select **Public - Ground Truth** in the top Workspace selector. This creates a version-bound workspace reference under `<GitHub numeric ID>:ground-truth` in SQLite. It is separate from My GitHub workspace and the controlled public/synthetic demo.

Search by repository/purpose; filter Sampling Domain or assigned Domain, and proposed Project/Topic/Tag memberships. Open **Review evidence** for the purpose, definition, rationale, exact quotes, complete saved sources and independent-audit details. Correct the purpose or label set; newly introduced positives require an exact saved-source quote. Missing concepts can be recorded in notes and left unresolved.

Save **Human confirmed**, **Needs review**, or **Unresolved / missing concept**. Confirmation requires reviewing Projects, Topics and Tags and a substantive purpose. Saving another revision retains prior decisions. Every record binds release ID, manifest hash, repository/commit, proposal hash, actor and revision. Concurrent edits are rejected for reload. Unlisted labels remain UNKNOWN, not negatives. Header export downloads that user's records and history.

[Detailed app walkthrough and architecture](../planning/public-ground-truth-workspace.md) explains every control. There is no automatic approval of imported labels, no normal AI/sync/reset action against this reference collection, and no silent import of offline decision templates.

## Validation and next steps

Automated verification covers authentication/CSRF, user isolation, source/dossier/manifest tampering, stale/concurrent revisions, metadata citations, repeated-proof merging and SQLite restart persistence. Full backend suite: **164 passing tests**. Corpus tools: **14 passing tests**. The real-corpus browser workflow passes at **1920×1080** and mobile sizes, including source display, review/save/reload/export, personal-workspace isolation and zero browser runtime errors. Existing app UI checks also pass; an initial concurrent artifact-cleanup failure was rerun after separating corpus output. All 13 existing app UI cases pass (twelve in the initial suite, the artifact-affected layout case in an isolated rerun), as does the corpus UI case. Frontend lint, typecheck and production build pass. Localhost health and protected corpus read/open/review routes were verified after activation. The two original app workspace states match their pre-activation hashes; one new ground-truth workspace reference is persisted and zero real human review records were created.

Next, run the agreed **30-development-repository pilot**, three per domain: fuller source-backed knowledge cards; an independent LLM labeler against explicit definitions; disagreement/evidence verification; human adjudication of uncertain cases plus random audits of high-agreement cases. Calibrate acceptance bands from audited outcomes, freeze taxonomy/reference versions, then scale in batches. Keep AI-verified proposals distinct from human-confirmed references. Only after that should the held-out corpus supply retrieval/classification scores or compare candidate RAG strategies. Existing safety fixtures remain useful for controlled boundary tests.
