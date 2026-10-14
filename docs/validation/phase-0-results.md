# Phase 0 pre-testing results

Date: October 11, 2026, America/New_York (UTC report filenames use October 12). Status: **requested private-repository, organization reconciliation and named AWS checks passed; conditional exit review remains**. Phase 1 is unapproved and unstarted.

## Scope and decisions

The user approved Phase 0, selected **GitHub OAuth App**, required Markdown reports, permitted optional user browser login, and selected AWS **default / us-east-1**. The latest instruction authorized completing fixture verification and creating isolated AWS targets for operation-level tests. After successful tests, the user explicitly requested **keeping the scratch resources for further testing**. [ADR 0001](../adr/0001-oauth-app-and-local-pretesting.md), [setup](../development/phase-0-localhost.md) and the [scratch scope](../planning/phase-0-aws-scratch-proposal.md) record these boundaries.

Delivered: Next.js page and fixed local API proxy, FastAPI OAuth state/PKCE/callback, opaque expiring HttpOnly session, CSRF-protected report/logout, source-aware paginated views, named and sampled GitHub checks, Markdown reports, isolated eight-resource AWS provisioning, inspection, synthetic canaries and cleanup verification. Tokens remain in backend memory. No production application deployment, AI invocation, IAM modification or GitHub repository mutation occurred.

## Automated and localhost evidence

| Check | Evidence | Status | Result / limit |
|---|---|---|---|
| Runtime/dependency setup | LIVE local | PASS | Local Node 24.21.0 LTS, Python 3.13.5, Next.js 16.4.0, React 19.3.0, FastAPI 0.143.0, boto3/botocore 1.43.111; npm/uv locks. Official Node archive digest verified |
| Ruff check and format | STATIC | PASS | Backend imports/style/format |
| `backend/.venv/bin/pytest backend/tests/pretest -q` | FIXTURE | PASS | **32 tests**, no live credentials or cloud writes; includes named private metadata versus discovery, content/report privacy, organization gaps and reconciliation, provisioning scope and private ownership-file safeguards |
| Frontend lint/typecheck/build | STATIC/build | PASS | Previously verified scaffold; no frontend source changes in this follow-up |
| Playwright localhost regressions | LIVE localhost + FIXTURE signed-in data | PASS | **4 Chromium tests**; rerun against the updated backend. Anonymous/setup, signed-in fixture workflow/report, phone layout, OAuth proxy/nonce/PKCE and invalid callback |
| Visual/layout and shell syntax | LIVE local/static | PASS | Desktop/phone inspected; no phone overflow; startup/check scripts parse |
| OAuth secret privacy | LIVE local artifact + FIXTURE | PASS | Secret absent from built browser JavaScript; tests verify no token/README leakage; secret never printed |
| Local startup and real OAuth login | LIVE local + GitHub | PASS | 127.0.0.1:3000 and :8000; correct callback and authenticated numeric identity confirmed in user-saved reports |
| CloudFormation validators | STATIC | PASS | cfn-lint 1.57.2: zero findings. Official Guard 3.2.1 digest verified: five project rules passed |

The backend suite additionally covers state replay/expiry/wrong browser, session/account rotation, Origin/CSRF/logout, host/local-only rules, scope-bound cursors/global filtering, source union/dedup/eligibility, API denial/SSO/rate/network/redirect/pagination/GraphQL failures, wrong AWS accounts/unsafe manifests, shared queues, foreign-message preservation and owner-conditioned transaction cleanup. Fixture success is not live permission evidence.

Tooling notes remain: Starlette TestClient emits an httpx deprecation warning; tests pass. ESLint 9.39.5 is retained because current Next.js plugin peer ranges reject ESLint 10; revisit the compatible set in Phase 1. The optional unrs-resolver install script remains disabled; lint/build passed without it. Local tooling lives under ignored `.tools`.

## Live GitHub access

The latest user-saved report at **9:56:57 PM EDT** contains **32 PASS, zero FAIL/BLOCKED, four NOT_TESTED**. Two named owned-private fixtures passed direct metadata/ID comparison, discovery/eligibility, root Contents and README access. Two sampled private rows repeat these same two repositories, so this is **two distinct private repositories**, not four. All returned private bodies were discarded.

A real organization completeness gap was found and fixed: organization affiliation from `/user/repos` alone missed 78 visible repositories. Discovery now also traverses each enumerated member organization's repository listing. Organization visibility remains insufficient for My Repos eligibility. The two independent endpoint cross-checks now observe **3 and 78 repositories, with zero missing IDs**. All four member organizations are enumerated by the inventory; sampled membership checks confirm active membership for two.

| Measurement | Latest observation |
|---|---:|
| Unique accessible inventory | 310 |
| Accessible private repositories | 2 |
| Eligible My Repos | 106 |
| Favorites (star/watch union, deduplicated) | 224 |
| OWNER / DIRECT | 103 / 0 |
| ORG_GENERAL / ORG_MEMBERSHIP | 83 / 4 |
| TEAM / TEAM_MEMBERSHIP | 3 / 6 |
| CONTRIBUTOR / STAR / WATCH | 2 / 93 / 187 |

All sources are OBSERVED without a reported denial or pagination cap. Counts overlap; TEAM can repeat a repository across teams. The [GitHub review](github-access-review-2026-10-11.md) records evidence hashes and the corrected gap.

Remaining limitations are explicit: an independently supplied complete organization expected-ID set is unavailable; hidden-policy repositories cannot be inferred from API responses. No independently verified direct grant, restrictive SSO organization, complete watch expectation or known recent-actor fixture was supplied. DIRECT=0 is an observed empty result, not proof of no possible direct grant. Watch endpoint usability is demonstrated; exhaustive watch completeness remains open. Production token persistence/refresh belongs to Phase 1/2. Browser-control surfaces are unavailable; user-driven login and saved-report review succeeded.

## Live AWS access

All eight required targets were created under one unique tagged scratch stack in the selected account, then inspected before synthetic writes. The [AWS review](aws-access-review-2026-10-11.md) records validation, audit controls, provisioning and operation evidence separately.

| Target / operation | Status | Evidence |
|---|---|---|
| Expected account, profile and Region | PASS | STS matched the pinned account before operations |
| Eight-target provisioning | PASS | Validated change set contained exactly eight additions; all reached CREATE_COMPLETE |
| Core / Organization / Intelligence tables | PASS | DescribeTable, conditional transactions, consistent reads, owner-conditioned cleanup |
| DynamoDB cross-table operations | PASS | Conditional PutItem, Query, BatchGet, three-table commit and expected failed-condition atomic rollback |
| Job queue and DLQ | PASS | Exact attributes and correlated send/receive/change-visibility/delete on both exclusive queues |
| Dummy secret | PASS | Generated synthetic marker verified; Describe/Get/hash comparison, no real OAuth credentials |
| Isolated EventBridge bus | PASS | Describe and accepted PutEvents; no downstream consumers or delivery claim |
| CloudWatch Logs | PASS | Stream create/event write/exact readback/delete |
| Canary cleanup and independent audit | PASS | Ten cleanup checks; subsequent consistent Queries found both run partitions empty in every table, queue counters were zero and owned log stream was absent |
| Runtime roles, production scheduling/delivery, GSIs/load | NOT_TESTED | Later configuration-specific gates; no production deployment occurred |
| Customer-managed KMS, S3, Bedrock/model, Lambda/ECS/ECR | NOT_APPLICABLE | No such optional target/provider/hosting choice selected for Phase 0 |

The canary report contains **28 PASS, zero FAIL/BLOCKED**, plus a future-runtime-role NOT_TESTED row. The cleanup audit contains **seven PASS**. Creation/inspection/data-plane permissions are demonstrated for this scratch configuration using the developer identity; they do not establish least-privilege deployed-role permissions.

Protected Markdown evidence is under ignored `docs/validation/private/`, with mode 600. The shareable AWS review lists exact report filenames. No test rows, messages or log streams remain. The user chose to **retain the eight resources for further testing**; the UTC expiry/review tag is October 13, not automatic deletion. No deletion was attempted. The one-day under-USD-1 estimate is not a bill or spending cap. Reusing the existing manifest avoids duplicate provisioning.

## Acceptance and handoff

**Recommend CONDITIONAL GO for Phase 0 review.** The requested private access, measured organization reconciliation and required developer AWS tests pass. Accepting broader GitHub provenance/watch/SSO limitations remains a user decision; do not silently convert NOT_TESTED cases into passes or start Phase 1.

| Work / decision | Owner | Disposition |
|---|---|---|
| Known private fixtures and representative organization cross-checks | User/implementer | Completed; 78-repository gap fixed and verified live |
| Named AWS creation, inspection, canaries and artifact cleanup | Implementer | Completed; no failed/blocked required checks |
| Retain scratch resources for further testing | User | Explicitly requested; ownership and exact manifest preserved |
| Additional direct/team/SSO/watch/activity expectations | User/org owner + implementer | Missing independent expectations remain documented; propose revalidation in Phase 2, subject to acceptance |
| Full Phase 0 exit and separate Phase 1 approval | User | Pending review; Phase 1 unstarted |

Local servers remain available for further browser testing. Backend restart clears OAuth sessions/tokens. Changes are local and uncommitted; original approved design/history documents are preserved.
