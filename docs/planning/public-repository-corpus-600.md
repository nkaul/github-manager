# Public repository corpus — approval plan

Date: October 16, 2026. Status: **Awaiting approval for full collection.**

Build a new, reproducible corpus of **600 distinct public GitHub repositories**, with their complete README snapshots, selected supporting content and evidence-backed proposed reference labels. Use this as the basis for evaluating the implemented evidence extraction, sparse retrieval, taxonomy and structured classification workflows. Preserve previous fixtures, benchmarks and reports.

## Coverage and search seeds

Target sixty repositories in each of ten sampling domains. These are collection buckets, not automatic ground-truth Domain assignments. Project names below are search hypotheses: actual membership requires purpose, dedicated integration, documentation or explicit relationship evidence. Shared owner, language, dependency or GitHub topic is insufficient by itself.

| Sampling domain | Candidate product / initiative families | Example Topics |
|---|---|---|
| Healthcare and life sciences | OpenMRS, OpenEMR, DHIS2, Medplum | Electronic medical records, clinical workflows, interoperability |
| Finance and payments | Apache Fineract, Mifos, OpenBB, Kill Bill | Lending, payments, financial analysis, billing |
| Commerce and business operations | ERPNext, Odoo, Saleor, Medusa | ERP, inventory, e-commerce, order management |
| Education and knowledge management | Moodle, Open edX, BookStack, Wiki.js | Learning management, assessment, documentation, knowledge bases |
| Science, geospatial and climate | QGIS, Open Data Cube, Astropy, OpenMM | Geospatial analysis, earth observation, astronomy, simulation |
| Data engineering and analytics | Dagster, Airbyte, Apache Airflow, dbt | Data orchestration, ingestion, transformation, data quality |
| AI and machine learning | PyTorch, Transformers, LangChain, MLflow | Model training, inference, retrieval, experiment tracking |
| Cloud, infrastructure and DevOps | Kubernetes, OpenTofu, Argo CD, OpenTelemetry | Infrastructure as code, deployment, observability, container orchestration |
| Security and identity | Keycloak, Authentik, OpenBao, Trivy | Identity, authorization, secrets management, vulnerability scanning |
| Developer platforms and collaboration | Backstage, Gitea, VS Code, Eclipse Theia | Developer portals, source collaboration, IDEs, language tooling |

These are not verified lists of related repositories or published canonical concepts. Agents must establish relationships from sources and record uncertainty. Topics cross domains; Tags represent primary implementation technologies. Repository Domains derive through approved Project parents, as in the current application.

## Six execution steps

1. **Freeze collection rules.** Write a versioned query catalog, sampling targets, product-family definitions and annotation rubric. Use GitHub topic search, README/purpose search, and verified family/organization discovery together. Search terms select candidates; they never become labels automatically.
2. **Collect with two agents.** Agent A handles the first five domains; Agent B handles the remaining five. Each targets 300 accepted repositories, working in resumable small batches through a shared request budget and cache. Discover up to 1,800 candidates to obtain 600 suitable, deduplicated records.
3. **Read and preserve evidence.** Resolve each default branch to a commit; save the complete README and up to four relevant supporting files at that commit. Read the README in bounded chunks, recording read coverage and evidence locations. Select purpose, architecture and relationship passages; inspect manifests/docs when relevant. Do not execute repository code, clone entire histories or follow arbitrary external links.
4. **Create proposed references.** Produce a dossier for every repository: purpose, candidate Projects, primary Topics and technology Tags, supported and excluded relationships, exact evidence locations, ambiguity and confidence in the annotation. Keep automated proposals distinct from human-approved ground truth. Secondary files can inform reference review but must not be silently treated as content the current app receives.
5. **Review and split.** Cross-review at least 120 dossiers between the two agents, including all disputed or high-risk memberships where practical. Supply human review sheets in batches. Aim for roughly 180 development, 120 validation and 300 locked-test repositories, keeping related initiative/lineage groups together; exact counts can vary to preserve group integrity. Freeze registry definitions and aliases before classifier tuning. Disclose all registry source overlap; do not claim unseen-family generalization where it does not apply.
6. **Deliver the versioned corpus.** Provide inventory CSV/JSONL, complete local source snapshots, per-repository dossiers, proposed/reviewed labels, source hashes, split manifest, collection coverage and Markdown validation reports. Run offline extraction/retrieval checks against saved data. Paid classification or model-based judging is a separate later activity.

## Search criteria and balance

Base discovery examples:

```text
topic:electronic-health-record is:public fork:false archived:false
"data orchestration" in:readme is:public fork:false archived:false
org:openmrs is:public fork:false archived:false
"Keycloak" in:name,description,readme is:public fork:false archived:false
```

Vary language, star bands and search ordering rather than selecting only the most popular results. Use explicit queries for minority-language READMEs and less popular repositories. Repartition searches that exceed GitHub's result cap; record `incomplete_results` and missing coverage. Queries and source links remain attached to every candidate.

Proposed composition across the 600: approximately 300 repositories with source-supported initiative relationships, 240 independent repositories or plausible near-neighbors, and 60 natural challenge cases. These are targets, not permission to invent relationships or negative labels. Include at least ten implementation languages, target sixty non-English/multilingual READMEs, and avoid a single owner or language dominating. Monorepos count once. Deduplicate by numeric repository ID and detect copied README/fork lineage. Any deliberate fork-lineage challenge stays in one split.

Every accepted core record must have an accessible complete README. Missing/oversized sources are recorded and replaced from the candidate pool rather than silently truncated. A proposed cap is 256 KiB per README, 128 KiB per supporting file and four supporting files per repository. Preserve thin READMEs as an explicit challenge slice. Do not manufacture natural negation or global `NO_MATCH` cases when the public sources do not contain them; preserve existing synthetic stress tests separately.

## Reference quality and evaluation boundaries

- Store `PROPOSED`, `CROSS_REVIEWED`, `HUMAN_APPROVED`, `DISPUTED` and `UNKNOWN` explicitly. Unreviewed labels are not ground truth; unknown membership is not a negative label.
- Record evidence path, commit/blob SHA, line/character offsets and the actual supporting passage for every proposed relationship. Record explicit contradictions separately.
- Distinguish full-source support, support available in the current app profile, and support actually transmitted in the compact request. Report omissions separately from retrieval misses and unsupported generation.
- Keep expected labels, search-derived annotations and review notes out of classifier inputs. Native GitHub topics remain input metadata, not independent reference truth.
- Evaluate taxonomy drafts with reviewed relevance/support/hierarchy/distinctness/grouping criteria; do not demand exact draft names when several useful vocabularies are possible.
- The public corpus replaces synthetic examples as the primary quality benchmark after reference approval. Existing synthetic/unit fixtures remain for controlled privacy, reset, race, negation and recovery tests that a public crawl cannot establish.

## Access, limits and storage

Reuse the existing OAuth App's authorized server-side public-data access, subject to a successful quota check after approval; no new GitHub App or CLI installation is proposed. An OAuth client ID alone is not a user access token. Credentials remain local and must not appear in reports or agent messages.

Use official GitHub read-only API endpoints, verified TLS, conditional requests and a shared rate limiter. Proposed run ceilings: **12,000 GitHub HTTP attempts**, **200 search requests** within that total, and **1 GiB retained source content**. Count failures/retries globally across both agents, obey lower server quotas and `Retry-After`, checkpoint at limits, and never rotate identities to evade throttling. Authentication normally provides a much larger allowance than anonymous requests, but actual response headers govern admission. No paid model API calls, AWS changes, GitHub mutations or app database changes are included.

Put source snapshots and detailed datasets under the already ignored `docs/validation/private/corpus-600/`, with restrictive local file permissions. Store license metadata and source notices, flag unknown licenses, and do not publish complete README copies as part of this work. Keep the query catalog, methodology and aggregate reports under `eval/ai-system-design/evaluation/corpus-600/`. Existing app extraction limits remain unchanged.

## Two-agent confirmation test

Both requested subagents started and completed a bounded public-read test on October 16, 2026:

| Agent | Inspected repository | Verified |
|---|---|---|
| A | `openmrs/openmrs-core` | Repository search, public metadata, pinned commit, complete README and `pom.xml` |
| B | `dagster-io/dagster` | Repository search, public metadata, pinned commit, complete README and root `pyproject.toml` |

There were fifteen attempts: four local system-Python CA-store failures followed by eleven HTTP 200 responses using the existing backend HTTPX transport with verified TLS. No packages were installed, TLS verification was not disabled, and no credentials or paid models were used. Both agents stopped after their one-repository checks.

The anonymous responses showed a 60/hour core allowance and 10/minute search allowance; that is insufficient for an uninterrupted 600-repository collection. Authenticated scale access remains an execution prerequisite, not a confirmed result of the anonymous test.

Agent A also found differing Java-version statements between README and manifest, demonstrating why evidence conflicts must be recorded. Agent B found that a topic search spans different product purposes, demonstrating why search hits cannot establish membership.

Reports: [Agent A](../../eval/ai-system-design/evaluation/corpus-600/planning/readiness-agent-a.md), [Agent B](../../eval/ai-system-design/evaluation/corpus-600/planning/readiness-agent-b.md).

GitHub documentation: [repository search syntax](https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories), [search limits](https://docs.github.com/en/rest/search/search), [contents API](https://docs.github.com/en/rest/repos/contents), [rate limits and OAuth public-data access](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api).

## Approval requested

Approve the 600-repository public-corpus collection, the ten-domain scope, two-agent execution, local source storage and reuse of existing authorized OAuth App access for read-only public requests. This authorizes collection and proposed annotations; human approval remains required before proposed references are released as ground truth. Full crawling has not begun.
