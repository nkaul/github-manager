# Agent A — applied-domain collection and review notes

Catalog: `domains-a.json`, version `2026-10-16-agent-a-v1.5`. The approved collection shard contains 240 accepted public repository snapshots: healthcare, finance, commerce and education 60each. Agent A completed 180 primary semantic dossiers for healthcare/finance/commerce; Agent C completed the 60 education dossiers after the parent reassigned that review. All labels remain `PROPOSED`, `human_approved=false`.

## Search and sampling

The versioned catalog defines 16 product-family hypotheses,32 Topic concepts and 72 explicit searches:18 per domain, at most30results per query, with180initial staged candidates per domain. Family owners and seeds, purpose terms, low-star bands, programming languages and non-English README phrases are discovery hypotheses. Search results, shared owners and native GitHub Topics never become independent reference truth.

The original balance goals were approximately 30initiative members,24 independent/near-neighbor repositories and 6naturally challenging cases per 60; these are goals, not automatic labels. Sampling buckets do not become repository Domains. Under the current application semantics, Domain association follows supported Project parents. A repository can have supported Topics/Tags without a supported registry Project, and that is distinct from global `NO_MATCH`. An unregistered real-world initiative, such as Spree or Magento, is not thereby absent from reality.

No further searches were needed during refill. Existing staged candidates were prioritized for likely family relevance, then verified from actual sources. The final independent commerce replacement was a Portuguese-described Django ecommerce repository, verified against its full retained README and annotated with a template/maturity caveat. Candidate reordering is audited locally and does not establish a label.

## Final primary-review checkpoint — October 16,2026

| Sampling bucket | Accepted snapshots | Primary dossiers | Primary reviewer | Full README semantic reads by A | Non-English README observations by A |
|---|---:|---:|---|---:|---:|
| Healthcare |60|60|A|17|7|
| Finance |60|60|A|8|3|
| Commerce |60|60|A|10|6|
| Education |60|60|C|Delegated|Delegated|

A completed 180 source-reviewed primary dossiers; 35 include complete retained README semantic reads and 145use explicitly recorded targeted line/character intervals. Complete source retention and complete semantic reading are different states. Education uses C’s coverage schema and is counted by the shared assembler; the table does not infer missing C observations as zero. Full README snapshots and selected supporting texts are retained for all 240accepted records. No collection process is running and no own-primary IDs remain pending. The parent reassigned A’s additional 40cross-reviews to itself; A has no remaining cross-review assignment.

Source-reviewed off-domain rejections retained: healthcare 18including the original ERPNext dossier transferred outside the normal records glob; finance 19; commerce 22; education 6reviewed by C. This excludes collector-level duplicate, README404, oversize/integrity and other technical exclusions. Every source-reviewed rejection remains auditable and was replaced to preserve the accepted quotas. ERPNext was transferred healthcare→commerce through the parent’s atomic broker correction with its original source audit preserved.

The soft twelve-per-owner goal is exceeded by `openMF` with 13finance repositories. Healthcare tops out at 8per owner; commerce at 11for Saleor and 11for Medusa. The six non-English goal is met/exceeded for healthcare and commerce but misses for finance, which has 3observed non-English READMEs. These are actual observed prose languages, not programming-language metadata or exhaustive whole-document language analysis. Quality/relevance took precedence over retaining irrelevant hits for balance.

## Evidence and semantic boundaries

Each proposed relationship carries exact inspected passages, commit-pinned path/blob/SHA256 provenance, line or line/character spans and rationale. Complete source snapshots are ignored local data. Short READMEs were often read in full; longer documents were read selectively for primary purpose, identity, supported relationships, maturity and contradictory claims. Uninspected source remains a disclosed limitation; neither downloading nor automated keyword drafting counts as full reading. Human adjudication is still required before calling the corpus ground truth.

The app-visible evidence channels remain distinct: current public metadata and README can support a relationship; supporting manifests/licenses are `REFERENCE_ONLY` unless also supported by app-visible inputs. Public metadata snapshots are timestamped, not commit-pinned. A primary programming language is a metadata input, not independent semantic verification. Explicit descriptions were used conservatively for WooCommerce ecommerce purpose, iClassify server inventory and the Fineract Open Banking app; boilerplate/thin README limitations remain visible.

Product-family membership requires dedicated purpose or participation. ERPNext does not follow from arbitrary Frappe use; Odoo does not follow from ownership alone; Mifos and Apache Fineract are separate unless source evidence supports both. Owl explicitly powers Odoo’s web client, so its foundation role is supported. Standalone o-spreadsheet and Paper-Muncher lacked equivalent inspected purpose evidence and were rejected from core commerce. Saleor’s generic internal company CI actions were also excluded rather than treating company use as product membership; their useful owner-neighbor audit is retained for a future explicitly negative panel.

Topics describe primary purpose/capability/subject, not every dependency, optional module or marketing footer. Medusa/Saleor starters, extension SDKs, language tooling, documentation and MCP integrations retain their artifact roles. A read-only MCP server is not credited with write actions. Mock payment-scheme tests are not real payment integrations. Character inventory in a game is not business inventory. Clinical icon libraries are not medical imaging.

Implementation maturity is separate from intended subject. VidaSys-IBV’s independent cross-review found financial/academic modules still planned. Payments was corrected to `UNKNOWN`; Learning Management is stated intended subject, with design/early-implementation maturity explicit. Its payment-processing and financial-ledger capabilities are not established. The final Django ecommerce README contains placeholders and template instructions, so its stated online-store purpose is supported while working functionality remains unverified. No repository code was executed.

## Leakage and adjudication cases

Solidus explicitly states Spree fork lineage; Saleor Merch’s README identifies Nimara and points to `mirumee/nimara-ecommerce`; Medusa admin-demo-cloud repeats DTC starter prose despite its repository name. These are flagged for lineage/near-duplicate split grouping. GitHub `fork:false` does not eliminate copied documentation or shared-family leakage. Identical/near-identical content, common product families and repeated templates require group-aware splits and a separate novelty/generalization analysis.

Source disagreements, missing identity information, unimplemented goals, optional integrations, natural-language/code-language differences and primary-vs-secondary taxonomy choices are explicit adjudication material. Independent agent review improves error discovery; it is not human sign-off. The parent owns the final 120cross-review panel and aggregate audit. A’s bulk annotation-scope clarification adds registry-relative noProject semantics and corrects stale global-noMatch states without changing semantic labels/evidence; the VidaSys correction is separately recorded.

## Controls and artifacts

Only the parent’s local credential-isolated broker and common collector were used; no direct GitHub calls, credential/.env reads, paid models, installs, repository execution, clones, GitHub writes or app-state changes were performed. Shared caps remain 12,000GitHub attempts,200 searches,1 GiBsource and1800staged candidates; broker accounting governs the aggregate totals. A’s original72searches/720 staged candidates are unchanged. Optional supporting-source integrity failures remain quarantined by the shared collector; hash guards were not relaxed.

Machine-readable counters, exact remaining IDs, annotations, read intervals, metadata snapshots, rejection audits and reusable helper scripts are under ignored `docs/validation/private/corpus-600/shards/a/`. `checkpoint-a.local.json` and `CONTINUE-a.md` record this completed-primary state. The original anonymous readiness smoke check remains unchanged under `planning/readiness-agent-a.*`; all previous fixtures and historical validation evidence are preserved. The shared assembler audits hashes and source-span quotes before the corpus is handed to human adjudication.
