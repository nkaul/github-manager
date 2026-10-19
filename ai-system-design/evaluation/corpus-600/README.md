# Public repository evaluation corpus

**Collection and source review complete: 600 distinct public repositories, 600 complete READMEs, 1,162 supporting files and 120 independent cross-reviews.** Human reference approval is pending. See the [dated validation report](validation-2026-10-16.md) for composition, offline diagnostics and limitations.

The approved scope covers ten sampling domains, pinned sources and source-backed **proposed** references for the implemented repository-organization pipeline. It does not add an embedding service or decision model.

The original [approval plan](../../../docs/planning/public-repository-corpus-600.md) is preserved as historical planning. Subsequent user approval and the request for a third agent supersede its awaiting-approval/two-agent wording. Execution uses three agents:

| Agent | Domains | Target |
| --- | --- | --- |
| A | Healthcare, finance, commerce, education | 240 |
| B | Science/geospatial/climate, data, AI/ML | 180 |
| C | Cloud/DevOps, security/identity, developer platforms | 180 |

Each domain contains 60 repositories. C additionally primary-reviewed the 60 education dossiers and seven restored AI candidates, preserving collector attribution; these were excluded from its independent cross-review queue. Catalogs [`domains-a.json`](domains-a.json), [`domains-b.json`](domains-b.json) and [`domains-c.json`](domains-c.json) contain query criteria, proposed family definitions, Topics and provenance. Sampling buckets do not assign repository Domains. Domains derive through supported Projects; Topics/Tags are independent facets.

## Access and collection

The authenticated confirmation succeeded using the existing OAuth App's server-side public-data access. No new browser login was required. The credential-isolated loopback broker owns the shared cache, request ledger, public-only endpoint checks and quotas. Agents receive no GitHub secret. Fixed read-only GitHub endpoints, verified TLS, pinned commits and Git-blob/SHA-256 verification protect source fidelity.

The approved ceilings remain 12,000 HTTP attempts, 200 searches and 1 GiB retained source. Execution used 5,391 attempts, including 181 searches, and retained 23,700,707 source bytes including excluded/history material. The broker obeys the lower live server quota and rate-limit checkpoints; cached responses do not make another upstream request. Source files are capped at 256 KiB per complete README and 128 KiB per supporting file, up to four supporting files. Missing/oversized/integrity-failing READMEs are excluded; invalid optional supporting bytes are omitted with an audit. Unknown licenses and inaccessible sources remain visible limitations.

Original sources and detailed datasets stay under the ignored `docs/validation/private/corpus-600/` with restrictive permissions. They are not published by this work. No paid model calls, AWS changes, GitHub mutations or application database changes are part of collection.

## References and validation

Agents read the sources and record purpose, primary Topics, technology Tags, supported family relationships, exclusions, uncertainty and actual reading intervals. Full raw retention is separate from semantic reading coverage. Long files may receive targeted reading; no truncated view is claimed as a complete read. Dependency use, owner identity or a search keyword alone does not establish Project membership. Empty/unknown membership is not a gold negative.

The 120 independent cross-reviews are complete, with initial findings and corrections retained. Cross-review is not human approval. Exported dossiers are 480 PROPOSED and 120 CROSS_REVIEWED; unsupported/unlisted relationships remain UNKNOWN. Current synthetic fixtures remain for controlled privacy, races, reset and recovery tests.

Offline assembly creates separate model-input and label files, a kind-aware registry, grouped provisional splits and inventory CSV/JSONL. It audits pinned sources and cited quotes/coordinates. It can run the current application's deterministic extractor and sparse retriever without constructing an API provider. Positive recall against proposed labels is diagnostic; incomplete references do not justify precision/F1 claims. Definitions curated with corpus access do not support an unseen-registry generalization claim.

## Tools

From the repository root, use the existing backend virtual environment:

```bash
backend/.venv/bin/python ai-system-design/evaluation/corpus-600/tools/collect.py stats
backend/.venv/bin/python ai-system-design/evaluation/corpus-600/tools/collect.py discover --agent a
backend/.venv/bin/python ai-system-design/evaluation/corpus-600/tools/collect.py harvest --agent a
backend/.venv/bin/python ai-system-design/evaluation/corpus-600/tools/assemble.py --require-complete --offline-check
backend/.venv/bin/python ai-system-design/evaluation/corpus-600/tools/audit_read_scope.py
backend/.venv/bin/python -m unittest discover -s ai-system-design/evaluation/corpus-600/tools -p 'test_*.py' -v
```

Collection requires the running local broker and its private capability file. Do not print that file or environment credentials. Start `tools/broker.py` only when no existing broker owns the port. Do not bypass its allowance with direct agent HTTP calls. Offline assembly and tests require neither network nor credentials.

Start with the local [release guide](../../../docs/validation/private/corpus-600/release/START-HERE.md), [inventory CSV](../../../docs/validation/private/corpus-600/release/inventory.csv) and [ten human review sheets](../../../docs/validation/private/corpus-600/release/human-review/README.md). Full-content JSONL, separated inputs/references, offline payload previews and a hash manifest are in the same local release folder. These private paths travel only with the local dataset, not a public documentation checkout.

The collection broker is stopped after handoff. Offline assembly/tests use no credentials. Reassembly regenerates derived artifacts; refresh the release manifest afterward. Preserve actual human decisions in a separate copy of the supplied template. This release does not declare human-approved gold or replace fixtures automatically.
