# Agent B: English-first corpus curation and source audit

Date: October 16, 2026. Completed **300 public repositories**, sixty each in data, AI, cloud, security and developer tooling. All references remain **PROPOSED**, with zero human-approved labels and no calibrated confidence claim. The original v1 dataset, source snapshots and prior benchmark reports remain unchanged.

## Active composition

| Sampling bucket | V1 retained | New v2 | Total | Repositories with supported Projects |
|---|---:|---:|---:|---:|
| data | 48 | 12 | 60 | 30 |
| ai | 42 | 18 | 60 | 30 |
| cloud | 51 | 9 | 60 | 30 |
| security | 50 | 10 | 60 | 23 |
| developer | 54 | 6 | 60 | 31 |

Project counts are distinct repositories with at least one **SUPPORTED** Project. UNKNOWN proposals are excluded; multiple supported Projects on one repository count once.

**245 v1 records remain active and 55 new records replace or rebalance the cohort.** The source-reviewed pool covers 357 unique candidate dossiers: active records plus excluded/reserve records. Screening removed 41 primary non-English narratives, one generic MLflow example heading and one primarily generic compiler from the security sampling bucket. An additionally collected thirty-byte Airflow Java heading was rejected. Thirteen valid English artifacts were moved to balancing reserves, with no assertion that they are defective or taxonomy negatives.

## English and relevance decisions

Every active README received a whole-file language screen, followed by agent inspection of actual purpose and relevance passages and suspicious language text. This is **targeted semantic screening**, not a claim that every long document was comprehensively understood. Full knowledge extraction and independent co-annotation are subsequent work. Script detection alone is inadequate: German NETSHIELD and Portuguese FaceSafety required narrative inspection. Chinese, Portuguese, Spanish, Korean, German and substantive bilingual narratives were excluded from this English-first cohort. Normal Unicode names and language-selector links are allowed. LuaLS retains a minor Chinese contribution footer while its substantive purpose/feature narrative is English.

Fourteen supporting translations are omitted from active English evidence lists; original raw bytes remain preserved. Historical read-coverage entries for removed translations were moved to provenance history instead of claiming those files are still active. Source acquisition, machine language screening, actual agent-read intervals, proposed labels and human approval are separate states.

## Balanced taxonomy coverage

The taxonomy existed upfront as a **proposed sampling vocabulary**, not an approved human answer key. Project membership requires a dedicated initiative/component/integration relationship; shared owner, dependency or a search hit does not assign membership. Topics describe primary purpose/capability and Tags describe primary technologies. A sampling bucket does not automatically assign a Domain; Domains derive through supported Project parents.

All twelve planned data families and all twelve planned AI families now have source-backed examples. Six data balancing substitutions add OpenLineage, Prefect, Apache Iceberg, DataHub, dlt and DuckDB while reserving repetitive CI/website/skill/course artifacts from already represented families. Seven AI substitutions add DeepEval, Ragas, Datasets, LlamaIndex, scikit-learn, Ultralytics and canonical vLLM. Ragas was resolved to its current `vibrantlabsai/ragas` identity. PyTorch moved components were resolved to `meta-pytorch`; numeric identity and source pinning prevent duplicate counting.

Cloud retains its four intended families and useful independent observability, deployment, cost and learning neighbors. Developer tooling retains all four intended families while adding English UI assets, developer analytics, API clients and version-control interfaces. Security retains authentik, Keycloak and OpenBao; **Trivy remains an explicitly uncovered family** after four fresh HTTP403 commit-acquisition failures. Authentication was not rotated or bypassed. Source quality takes priority over inventing family membership.

Three narrow Topic proposals are saved separately for human taxonomy review: **Code Generation**, **Data Platform Integration**, and **LLM Framework Integration**. Existing definitions were not silently broadened. TorchData has direct PyTorch membership but its precise primary Topic remains UNKNOWN because dataloading is not the same as learning a model or curating dataset quality. Dagster Cloud has direct family membership but its agent repository does not inherit every marketed enterprise-product capability.

## Source and proposal validation

Final owned audit: **300 complete README snapshots plus 655 active supporting files**, **10,011,841 bytes**, with zero file-hash, quote, coordinate or referenced-source errors. Nested English Redis and Neo4j package READMEs were collected at pinned commits to avoid relying on short integration headings. Their feature evidence is explicitly REFERENCE_ONLY for the current app input.

New proposals record concise purpose, artifact type, direct relationships, exact source passages, uncertainty and actual read intervals. Dominant-language metadata is flagged as shared-input evidence, not an independent code audit; Makefile/Mustache detections are not blindly promoted as primary implementation technologies. Generated authentik API clients explicitly retain TypeScript evidence. Vendor speed/security/scale statements were not independently benchmarked. Vault/OpenBao lineage is grouped without assigning Vault to OpenBao. A DeepEval README mention of Jev does not add a Jev implementation to GitHub Manager.

## Persistence and review status

Detailed data persists locally under ignored `docs/validation/private/corpus-600-v2/`. Active dossiers are `shards/b/<bucket>/records/*.local.json`; original immutable sources may be referenced from v1 by commit and SHA256. New snapshots live under v2 sources. Exclusions, balancing reserves, acquisition attempts and translation omissions have separate audits. Complete third-party sources are not copied into tracked documentation. Public visibility does not establish unrestricted redistribution rights.

Key private artifacts: `eligibility-audit.local.json`, `eligibility-original-cohort-final.local.json`, `whole-file-language-screen.local.json`, `final-composition.local.json`, `new-topic-proposals.local.json`, collection/rename audits and actual reading packets. The final dataset uses the current `eligibility_audit` contract. No paid model API, package install, app configuration change, code execution from repositories, private GitHub content, GitHub write or AWS operation occurred in this agent work.

Independent targeted review of sixty Agent A final dossiers is complete, twelve per domain with risk-selected and reproducible random halves. All sixty current proposed claim sets are supported at the inspected scope. One initial correction was resolved: a post-payment email receipt adapter consumes an upstream risk decision and must not be credited with independent Financial Risk Management. Its corrected reference leaves that Topic UNKNOWN. Original findings, corrected proposals, exact inspected source intervals and hash bindings are preserved under `cross-review/b/`. This is an agent quality audit, not human ground truth, exhaustive label completeness or a classification benchmark.
