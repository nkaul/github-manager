# Agent B — public GitHub corpus readiness

Date: 2026-10-16. Single-repository smoke test only; full crawl awaits approval.

- HTTP attempts: 8 / 8. No automatic retries.
- Authentication: none. No app, database, .env or credential files read.
- Public content treated as untrusted static data. No external links followed, package installs, cloning, paid model calls or code execution.

System Python urllib could not verify local CA chain. Existing backend virtualenv httpx uses default verified TLS; verification was never disabled.

## Endpoint results

| Endpoint | Status | Rate remaining | Resource |
|---|---:|---:|---|
| `https://api.github.com/rate_limit` | None | None | None |
| `https://api.github.com/search/repositories?q=topic%3Adata-orchestration%20is%3Apublic%20fork%3Afalse%20archived%3Afalse&per_page=5` | None | None | None |
| `https://api.github.com/repos/dagster-io/dagster` | None | None | None |
| `https://api.github.com/search/repositories?q=topic%3Adata-orchestration%20is%3Apublic%20fork%3Afalse%20archived%3Afalse&per_page=5` | 200 | 9 | search |
| `https://api.github.com/repos/dagster-io/dagster` | 200 | 59 | core |
| `https://api.github.com/repos/dagster-io/dagster/commits/master` | 200 | 58 | core |
| `https://api.github.com/repos/dagster-io/dagster/readme?ref=c97898c3e4a8a3cc5e32fcc2ca97aea810342ed9` | 200 | 57 | core |
| `https://api.github.com/repos/dagster-io/dagster/contents/pyproject.toml?ref=c97898c3e4a8a3cc5e32fcc2ca97aea810342ed9` | 200 | 56 | core |

Exact rate limit/reset/retry headers and failures are recorded in the JSON report.

## Snapshot

- Repository: `dagster-io/dagster`, numeric ID `131619646`.
- Visibility: `public`; private: `False`; license `Apache-2.0`.
- Default branch: `master`.
- Pinned commit: `c97898c3e4a8a3cc5e32fcc2ca97aea810342ed9`.
- README: [README.md](https://github.com/dagster-io/dagster/blob/c97898c3e4a8a3cc5e32fcc2ca97aea810342ed9/README.md); 6831 bytes, 149 lines; blob `93aed1dec84d15801939d969d284f84ccd145143`; SHA-256 `c67be78a0355a34b38964ba3e64fa615604e175afbc00bef4506afd4bf0a0b34`.

> Dagster as a robust orchestration engine

Pinned evidence: [README line 103](https://github.com/dagster-io/dagster/blob/c97898c3e4a8a3cc5e32fcc2ca97aea810342ed9/README.md#L103) (6 words).

Supporting file: [pyproject.toml](https://github.com/dagster-io/dagster/blob/c97898c3e4a8a3cc5e32fcc2ca97aea810342ed9/pyproject.toml); 6604 bytes; blob `d658bf47aef160779292ebff1d8c644446a35b9c`; SHA-256 `edb9d2914bcb435e5681d1894bb853e7b1454cf6fe611919784cabe76014e6a6`.

TOML tables: `tool.pytest.ini_options`, `tool.ruff`, `tool.ruff.lint`, `tool.ruff.lint.per-file-ignores`, `tool.dagster`.

Root TOML contains pytest, Ruff and Dagster tool configuration. These tool settings do not establish runtime dependencies, repository language coverage or initiative membership. Static inspection only; nothing executed.

## Candidate annotations

All proposed labels are provisional; none are human approved.
- **DOMAIN: Data Engineering** — Broad inferred analytical domain; requires an agreed definition and human review.
- **PROJECT: Dagster** — Canonical dagster-io/dagster repository represents the Dagster initiative. Merely using Dagster elsewhere does not establish membership.
- **TOPIC: Data Orchestration** — README purpose statement and repository topic provide direct supporting evidence.

One repository ID equals one corpus item. Dagster monorepo packages do not count as additional repositories.

## Scale and limitations

Smoke check is public and unauthenticated. Current core/search response headers provide the available quota. A 600-repository corpus with metadata, commit, README and supporting content needs thousands of reads; an authenticated read-only GitHub identity is recommended to avoid the unauthenticated core quota. Search has a separate quota. Full crawl must coordinate rate limits across both agents.

Search topic membership is a discovery signal, not ground truth. Canonical ownership and explicit README purpose support Project membership; dependency, SDK and shared-technology mentions alone do not.

Complete README and manifest text were read only in memory and were not stored in tracked planning documentation. A full corpus should preserve bounded, commit-pinned evidence snapshots with hashes and license metadata in an appropriate data directory.

Failures: 3 local verified-TLS failures before the corrected transport; see JSON for exact endpoints/errors.
