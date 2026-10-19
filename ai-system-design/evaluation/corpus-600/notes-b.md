# Agent B corpus collection and semantic-review notes

Checkpoint: 2026-10-16. Catalog revision **18**. Collection and agent review are complete for **180 distinct public repository IDs**, with **60 science, 60 data and 60 AI**. All references remain **PROPOSED**, with `human_approved=false`; these are reviewable reference candidates, not human-approved gold or measured model performance.

## Scope, registry and search

The approved plan is [public-repository-corpus-600.md](../../../docs/planning/public-repository-corpus-600.md). The catalog records 36 named Project hypotheses, 59 distinct Topic names across the three buckets, and 54 bounded discovery queries. Each bucket used at most 18 queries, 30 results per request and 180 staged candidates. Existing parent-owned OAuth App public-data access and the common localhost broker provided bounded, audited GitHub reads. No private account content, app database, `.env`, secrets, packages, paid model APIs, repository code execution or GitHub writes were used by this work.

The approved primary science families were QGIS, Open Data Cube, Astropy and OpenMM; data families were Dagster, Airbyte, Apache Airflow and dbt; AI families were PyTorch, Transformers, LangChain and MLflow. Additional catalog families are documented alternative hypotheses. Organization membership, repository names, topics, SDK imports and common dependencies never establish a Project reference by themselves. Dedicated canonical components, clients, adapters and integrations require a purpose/relationship passage. Monorepos count once.

Sampling buckets are exclusive and are **not Domain labels**. The application derives Domains through approved Project parents. A source-supported independent tool can have Topics/Tags while its Project and therefore Domain remain unknown. Topic capabilities are not automatically inherited from a parent product: Airflow CI infrastructure is CI, and an OpenMRS deployment role is configuration management, even when their initiative relationships are clear.

Discovery combined named-family, primary-purpose, low-star, implementation-language and non-English queries. Actual README narrative determines observed language. Broad search produced irrelevant neighbors, which were source-reviewed and replaced rather than retained to satisfy diversity counts. A one-repository `apache` owner preference exception is disclosed below; family caps were not exceeded.

## Completion and evidence audit

| Measure | Result |
|---|---:|
| Accepted current dossiers | 180 |
| Distinct IDs per bucket | 60 / 60 / 60 |
| Source files retained and SHA256-checked | 539: 180 READMEs plus 359 supporting text files |
| Accepted source bytes | 5,498,755 |
| Citation quotes checked against immutable sources and actual review scope | 592 |
| Final source/citation/read-scope errors | 0 |
| Primary semantic reviews | 173 by Agent B; 7 delegated to Agent C |
| READMEs semantically read in full | 26 |
| READMEs reviewed through targeted purpose/relationship/capability passages | 154 |
| Supporting documents read in full | 4 |
| Observed non-English or multilingual README narratives | 20 |
| Independent B reviews of Agent A dossiers | 40, ten per assigned A bucket |

Complete pinned README snapshots and up to four bounded supporting text files are retained locally. **Complete collection is not complete semantic reading.** Every dossier records actual line or character intervals and completeness; unviewed paragraphs, code, images and external links are not claimed read. Many supporting files are retained but unreviewed. The final audit supports exact full-line citations and exact within-line substrings, bound to file SHA256 and their recorded review intervals. Wide quotes spanning unviewed paragraph gaps were split to the actually read intervals without changing the proposed semantic label.

Audit and private materials:

- `docs/validation/private/corpus-600/shards/b/final-annotation-audit.local.json`
- `docs/validation/private/corpus-600/shards/b/{science,data,ai}/records/*.local.json`
- `docs/validation/private/corpus-600/shards/b/review-packets/`
- `docs/validation/private/corpus-600/cross-review/b/results.local.json`
- `docs/validation/private/corpus-600/cross-review/b/review-history.local.jsonl`

No complete third-party README was copied into these tracked notes. Sources and dossiers remain in the ignored local validation directory. Metadata is a retrieval-time snapshot; pinned commits bind Git content, not mutable star counts, descriptions or GitHub language detection. Metadata-based technology references are explicitly input-correlated proposals, not independent code audits. Supporting-source evidence is `REFERENCE_ONLY` and must not be presented as something the current application necessarily received. Compact-request evidence availability remains a separate offline measurement.

## Composition and limits

| Bucket | Source-supported Project records | Observed non-English/multilingual | Repositories below 100 stars |
|---|---:|---:|---:|
| Science | 20 | 4 | 6 |
| Data | 23 | 6 | 2 |
| AI | 12 | 10 | 4 |

The suggested 30 initiative positives per bucket was a **soft target**, not a license to infer membership. Strict source evidence produced fewer positives, especially in AI. The remaining independent/near-neighbor and uncertainty cases remain useful for testing overassignment, but are not automatic negative gold. Non-English/multilingual observation totals are Spanish 10, Chinese 6 and Portuguese 4; seven reviewed records also contain English narrative. These are observations over reviewed passages, not an automatic measurement of every source language or translated README.

The data bucket contains seven `apache`-owned repositories, one above the six-owner preference, spanning distinct Airflow, Hudi and GraphAr purposes. Retention was proposed to the parent and is explicitly disclosed; no Project family exceeds the eight-repository preference. Low-star representation is limited, especially in data, and should not be described as balanced across popularity. Sampling is search-driven rather than representative of GitHub as a whole.

License metadata: Apache-2.0 59; MIT 42; BSD-3-Clause 8; GPL-3.0 4; CC0-1.0 4; GPL-2.0 2; one each AGPL-3.0, BSD-2-Clause, LGPL-2.1 and MPL-2.0; **32 NOASSERTION and 25 absent**. Public visibility does not establish unrestricted reuse. The VerifyWise README describes a source-available license/change even where repository metadata may lag. Captured repository licenses do not license external books, datasets, remote models or linked content; none of those external artifacts were downloaded. Publication/redistribution and frozen split eligibility require the parent policy and later review.

## Source-driven corrections and natural challenge cases

- **Current dbt implementation differs from historical expectations.** The pinned `dbt-labs/dbt` README describes a Rust v2 rewrite and directs Python v1 users elsewhere. Technology references follow this snapshot rather than memorized associations. Fusion has separate migration/beta wording, retained as source-version context.
- **A connector library is not the complete orchestration product.** PyAirbyte explicitly excludes orchestration/scheduling/logging/alerts. Its Airbyte relationship is supported, while the orchestration claim is contradicted in that scoped case.
- **Product membership is narrower than using a framework.** Independent TS-TCC, VisionMamba and book examples can use PyTorch without becoming PyTorch Project members. SentenceTransformers is not assigned Transformers from an owner/name overlap. LangGraph/Deep Agents retain a LangChain umbrella-scope question. `openmm-torch` has an explicit OpenMM relationship but PyTorch Project membership remains unknown; PyTorch can still be a technology Tag.
- **README and manifest visibility differ.** `odc-stac` has Open Data Cube relationship evidence in a supporting manifest. It is reference-only evidence rather than an assumed README-visible application input. Other sources, such as `odc-geo`, state the origin explicitly in their README.
- **Artifact type matters.** Educational courses/books/notebooks use the shared **Learning Content** Topic. Curated external-tool/research indexes use **Technical Resource Discovery**. System/API/operational reference guidance uses **Technical Documentation**. Subject Topics on a course describe taught examples, not a standalone production engine. Initial educational/documentation mismatches were corrected after independent review.
- **Negation must retain its scope.** `rnoaa` says it does little plotting/analysis; that supports data access as primary purpose, not complete absence of analysis. Climate Analysis is unknown rather than a universal negative. Lifecycle/support warnings remain explicit despite `archived:false` metadata.
- **Metadata language detection can be misleading.** OpenMM force-field resources report Rich Text Format; dbt-utils reports Makefile while its README describes SQL/Jinja helpers. Those detections are not blindly promoted to primary-use technologies. Turf's JavaScript API versus TypeScript implementation and CGA.js source/build language differences remain disclosed.
- **Maintenance and deployment claims are distinct from purpose.** RAGBuilder says it is no longer maintained; PipeRider says it is superseded; some educational projects use explicitly fictional seeded business examples. Alluxio's enterprise-only capabilities are not attributed wholesale to its open-source snapshot. Author-reported speed, benchmark, compliance, accuracy and production-readiness claims were not reproduced.
- **Logical README paths can resolve Git symlinks.** The parent verified Dagster's root README as an exact 32-byte Git symlink target string. Its resolved pinned README has the verified full content. Logical and resolved paths, link/blob proof and corrected target citation URLs are retained; source integrity checks were not relaxed.
- **Natural prompt injection appeared in a real source.** An off-domain Home Assistant README addressed bots and requested a destructive shell operation. It was treated solely as untrusted text, never executed, and retained with an audit outside the core corpus. It can inform a later adversarial evaluation subject to scope review.

There are 36 preserved source-review exclusion dossiers, including nine origin dossiers later restored through audited within-Agent-B bucket reassignment. Those origin records are historical, not additional accepted repositories. Twenty-seven currently excluded repositories remain outside the core 180. The parent atomically updated broker claims before restoration; immutable source bytes were reused, avoiding unnecessary GitHub reads. Two earlier integrity quarantines, PaddleRS and PyTorch tutorials, are retained separately. The shared collector now distinguishes an invalid README from an optional supporting-file mismatch, preserving detailed failure evidence without weakening blob/hash validation.

## Independent review and remaining gates

Agent C independently reviewed 40 B dossiers and completed seven explicitly delegated AI primary reviews. The delegated seven were outside the independent-review queue, preserving independence. Agent B independently inspected the real source passages for 40 A dossiers, balanced across commerce, education, finance and healthcare. One substantive finding on Vidasys-IBV was corrected: fee/payment administration did not establish payment execution, and its academic/financial modules were still planned. Payments is now unknown and maturity is explicit; the original finding and the re-review of corrected annotations are both retained. Current review results bind the exact annotation and source digests.

These agent checks establish traceable, source-supported proposals. They do not constitute human-approved ground truth, test-split independence, calibrated model quality or RAG-evaluation results. Before scoring or replacing evaluation fixtures, complete human adjudication, canonical/alias registry reconciliation, exact/near-duplicate and initiative grouping, frozen groupwise splits, license/publication decisions and application-visible/compact-context evidence measurements. Preserve prior synthetic/unit fixtures for privacy, reset, races, budget and failure modes that public repositories cannot replace. No production app or application taxonomy was changed.

Historical checkpoint: catalog preparation initially used no network and awaited the common broker. The subsequent approved collection/review supersedes that preparation checkpoint; prior smoke-test and earlier project evidence remain preserved.
