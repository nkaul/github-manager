# Phase 0 live GitHub OAuth access review

Review date: October 11, 2026, America/New_York. Outcome: **named private access and representative organization discovery checks passed; a 78-repository gap was fixed and verified live**. Independent exhaustive expectations and policy/provenance edge cases remain unverified.

## Latest evidence and outcome

The user signed in with the selected OAuth App and saved the report at **9:56:57 PM EDT** after the discovery fix. The same numeric user identity and actual scopes (`notifications`, `read:org`, `read:user`, `repo`) were confirmed. The report contains **32 PASS, zero FAIL/BLOCKED, four NOT_TESTED**. Identity details stay in ignored private evidence.

Both user-named fixtures were owned-private repositories. Direct metadata resolved their stable numeric IDs into the inventory, OWNER eligibility matched, and the Contents and README endpoints were accessible. Two automatically selected private samples were these same two repositories, not additional distinct fixtures. No file list or README body was persisted or sent to a model.

Organization affiliation from `/user/repos` originally omitted 78 repositories visible through one member organization's API. The adapter now also traverses paginated listings for each enumerated member organization and merges numeric repository IDs into ORG_GENERAL. Organization visibility alone still does not establish My Repos eligibility. A regression test verifies this distinction.

Four member organizations were enumerated. Two sampled memberships were active, and their independent repository-listing cross-checks returned **3 and 78 repositories with zero missing inventory IDs**. ORG_GENERAL increased from 5 to **83 unique source IDs** after reconciliation. The inventory now has **310 unique accessible repositories, two private, 106 eligible My Repos, and 224 deduplicated Favorites**.

| Source | Latest observations |
|---|---:|
| OWNER / DIRECT | 103 / 0 |
| ORG_GENERAL / ORG_MEMBERSHIP | 83 / 4 |
| CONTRIBUTOR | 2 |
| TEAM / TEAM_MEMBERSHIP | 3 / 6 |
| STAR / WATCH | 93 / 187 |

All sources are OBSERVED, without a reported denial or pagination cap. Source counts overlap and must not be summed as unique repositories; TEAM can contain duplicates across teams. The owned/watch counts exceed the configured 100-row REST page size. Earlier reports' ORG_GENERAL=5 was successful endpoint retrieval but incomplete discovery; the cross-check exposed that distinction.

## Evidence provenance

Protected local reports under ignored `docs/validation/private/` use mode 600. Reports contain identity, aliases, counts and sanitized outcomes; repository name fields and content bodies are omitted. User-chosen aliases can themselves reveal a name, so treat detailed reports as private. No token, authorization code or verifier is retained.

| Private report | SHA-256 | Purpose |
|---|---|---|
| `github-20261012T012158550723Z.md` | `2d7c35932142bab5d1d897f4fe607f805d1fd1f5afad0172773b5e533c699d8c` | Initial login/source traversal |
| `github-20261012T012257361008Z.md` | `0c53e3eec27589de1fce938d3faa3a1042f74cd4c01bdae9cf640998e3879b6d` | Repeated initial observations |
| `github-20261012T015030065300Z.md` | `e5d136d98173f17ac5938f2458f43b4aff1976e5f0566bb6652b3155cb864c82` | Private fixture success and discovery of organization gap |
| `github-20261012T015657652939Z.md` | `d9f519c004b11bf35f0da007dd01230207e02d8dfc2be3ebfcf9432e50cf4dbb` | Successful live verification after fix |

The agent reviewed saved reports; browser-control surfaces were unavailable. User-driven browser login and report generation supplied live evidence without exporting browser cookies or server tokens. Backend restart/re-login also succeeded during this follow-up.

## Remaining limits and recommendation

- No independently supplied complete organization expected-ID set exists. Cross-API consistency under this token passed; repositories hidden by third-party policy or SSO cannot be inferred from visible results.
- DIRECT=0 is an observed empty endpoint response. No known independent direct-grant fixture or restrictive SSO organization was supplied; direct/team attribution against human-known grants remains limited.
- Authenticated watches are usable and returned 187 observations. No independently complete known-watch set exists, so D02 exhaustive completeness remains open.
- No known recent-actor fixture was supplied. Durable token encryption/refresh, background access and deployed sessions remain Phase 1/2 work.

The measured results support the user-selected OAuth App; no broader scopes or connector change were needed. Recommend conditional Phase 0 exit review with the above limitations explicit, then separate Phase 1 approval. The previously missing named AWS evidence now passes too: see [AWS review](aws-access-review-2026-10-11.md) and [combined results](phase-0-results.md). Production IAM, model and hosting choices remain separate.
