# Agent A — English-first corpus v2 audit and replacements

This agent owns healthcare, finance, commerce, education and science, targeting 60 repositories in each. The original corpus v1, its source snapshots, dossiers, proposed references and reports remain unchanged. This pass checks English evidence, relevance and sampling balance; it is not the later full knowledge-extraction/co-annotation pass and does not establish human ground truth.

## Initial audit of 300 v1 repositories

| Original sampling bucket | Retain in bucket | Non-English narrative exclusion | Applicability/evidence exclusion | Valid balance reserve | Reassign |
| --- | ---: | ---: | ---: | ---: | ---: |
| Healthcare | 50 | 8 | 1 | 0 | 1 to science |
| Finance | 51 | 3 | 5 | 0 | 1 to education |
| Commerce | 51 | 6 | 3 | 0 | 0 |
| Education | 38 | 15 | 7 | 0 | 0 |
| Science | 52 | 4 | 0 | 4 | 0 |

The initial retained copies therefore contain healthcare 50, finance 51, commerce 51, education 39 and science 53: 244 total, requiring 56 replacements. Two source-backed reassignments correct sampling rather than automatically assigning taxonomy Domains: Open Climate Service explicitly operates independently of DHIS2 and provides climate/geospatial data services; JPMorgan's Python training teaches numerical computing and visualization, with an analyst/trader audience that alone does not establish financial-software purpose.

Every decision has a source-bound private audit under `docs/validation/private/corpus-600-v2/shards/a/eligibility/`. Copies of retained dossiers are under the new v2 shard, with `v1_provenance` and `v2_eligibility`; complete unchanged v1 source files are referenced by pinned commit, path and hash. Full-file deterministic language screening is supplemented by agent reading of actual purpose, headings, language-bearing spans and ambiguous/short sources. Recorded semantic scope is targeted and does not claim complete interpretation of long catalogs, generated API tables or all source code.

## What changed and why

English eligibility concerns the primary narrative and purpose-defining evidence, not owner nationality, product-interface language, programming language, Unicode names or translation links. The old Inventory application advertises Spanish and English interfaces but its entire README is English; it is retained. Conversely, one English abstract does not make the rest of a Chinese/Spanish narrative English. Translation-only supporting snapshots can remain archived in v1 but are excluded from the v2 active supporting-evidence set. The English primary README still provides the source of truth for those retained repositories.

Examples removed for weak purpose evidence include a two-line Finova placeholder, an explicit PaymentHub description placeholder, generic React/Vite and Rails scaffold READMEs, and generic GitHub Actions text without a dedicated financial relationship. Broad developer/security/career catalogs are not treated as education simply because they contain links. Relevant instructional repositories, documentation, learning platforms, knowledge systems and domain resource collections remain eligible with their real artifact type.

Fresh source inspection also found that the design-token specification repository mentioned Open edX only among represented organizations. That is not dedicated Open edX membership; the source remains preserved in v1 and is excluded from education core. Four valid English scientific resources are explicitly reserved for balancing, rather than falsely called irrelevant or non-English, so seven previously absent seeded science families can be represented.

## Replacement method and current status

Replacements use only the parent's credential-isolated read-only public GitHub broker, its separate v2 request ledger and shared deduplication. Seed names/searches remain hypotheses until README/source verification. No repository content is executed, no credentials are read by this agent, and no paid model calls or external writes are performed. Exact 60-per-domain quotas must pass final assembly; topics, technologies and family relationships remain proposed and source-backed, with unknown membership preserved.

## Final verified composition — October 16, 2026

| Sampling bucket | Retained/reassigned source references | New English replacements | Final repositories | Supported Project records | Active supporting files |
| --- | ---: | ---: | ---: | ---: | ---: |
| Healthcare | 50 | 10 | 60 | 36 | 112 |
| Finance | 51 | 9 | 60 | 33 | 98 |
| Commerce | 51 | 9 | 60 | 37 | 106 |
| Education | 39 | 21 | 60 | 31 | 125 |
| Science | 53 | 7 | 60 | 27 | 127 |
| **Total** | **244** | **56** | **300** | **164** | **568** |

All 28 seeded Project families in these five buckets have at least one source-supported proposed member. The seven previously absent science families now have canonical examples: GDAL, xclim, GeoPandas, NumPy, Pangeo, xarray and Rasterio. Pangeo is explicitly a community website and coordination point; its README says there is no single software package called Pangeo. Education now has BookStack 6, Moodle 11, Open edX 9 and Wiki.js 5 supported members, with additional independent learning/knowledge systems.

Domain quotas are equal; family membership counts are **not** equal. Commerce contains ERPNext 3, Odoo 12, Saleor 11 and Medusa 11; finance contains OpenBB 3, Kill Bill 12, Mifos 9 and Apache Fineract 11 relationships, with two multi-family repositories. Actual dedicated-purpose evidence took precedence over manufacturing equal family counts. Evaluation must report per-family support and grouped uncertainty, and may use predeclared sampling weights or a later balancing supplement. These are sampling buckets, not automatic repository Domain assignments.

Four targeted repository searches were used for official and third-party OpenBB/BookStack components. Official active organizations yielded only the canonical repository, so source-verified dedicated connectors, clients, exporters and deployment integrations supplied useful family examples. Search results stayed hypotheses. One result contained enormous unrelated keyword-stuffed metadata and was discarded. An unavailable Synthea seed, an empty/oversized OpenMRS README, a blob-integrity-failing Fineract README, two Wiki.js README 404s, an archived/forked Moodle seed and a Wiki.js link-only README were not accepted. The guard was not weakened to fill quotas.

## Independent verification and limits

Agent A independently checked 60 of Agent B's final dossiers: 12 per sampling bucket, half selected for risk and half by deterministic pseudo-random ordering. Current results are `SUPPORTED` for the inspected source-backed proposals, with valid annotation/README digests and actual displayed source intervals. This does not establish exhaustive label completeness, human accuracy or calibrated confidence. Extra raw-source checks verified PyAirbyte's explicit lack of orchestration/scheduling, LangGraph's ecosystem-layer distinction, Bruno's local/offline collection storage and the Backstage TechDocs link target.

Agent B independently checked 60 of A's dossiers. It found one inherited overbroad Topic: the payment-receipt adapter consumes an upstream risk decision and gates email delivery; it does not assess financial risk or execute transactions. `Financial Risk Management` was moved from `SUPPORTED` to `UNKNOWN`, the purpose and Payments integration boundary were clarified, and the original dossier/finding plus corrected re-review remain preserved. All current review bindings were checked after correction.

The local source audit verified 300 READMEs and 568 active supporting files totaling 8,424,268 bytes, with zero hash, length, citation-quote or source-coordinate issues. Archived translations remain available through preserved v1 references but are excluded from active English supporting evidence. One additional proposed Topic, **Human Resource Management**, is documented from Frappe HR's primary standalone HR/payroll purpose; it is not approved human taxonomy. Frappe HR's historic ERPNext origin is not automatically current ERPNext membership, and Vercel Commerce's alternative-provider list does not make its explicitly Shopify version a Saleor/Medusa component.

The terse `edx-enterprise-subsidy-client` service purpose has Open edX package authorship/context but insufficient dedicated-purpose evidence for an automatic Project assignment; that relationship remains unassigned/unknown for co-annotation. Legacy v1 words such as `HIGH` on inherited annotation confidence are uncalibrated agent wording, not an auto-acceptance score. Every active record remains `PROPOSED`, `human_approved=false`; full knowledge extraction, independent LLM labeling, confidence calibration and human adjudication are still separate next steps.

Detailed local artifacts: `shards/a/eligibility-audit.md`, `eligibility-audit.local.json`, per-record `eligibility/`, `final-audit.local.json`, replacement source proposals, rejected-source audits and independent `cross-review/a/results.local.json`. The parent owns aggregate assembly, app-workspace import, final manifests and human-review handoff. Collection is stopped; no further network or source mutation is required by this agent.
