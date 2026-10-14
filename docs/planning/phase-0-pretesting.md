# Phase 0 — Localhost setup and access pre-testing

Date: October 11, 2026. Status: approved and implemented; named private GitHub fixtures, organization discovery reconciliation and required AWS developer checks passed. Full exit review and broader provenance/SSO/watch limitations remain open. See [results](../validation/phase-0-results.md).

Companions: [implementation plan](implementation-plan.md), [architecture review](architecture-review.md), [open decisions](open-decisions.md). This phase precedes Phase 1 without renumbering Phases 1–10. It adds early integration evidence to the approved architecture; it does not replace the production foundation or security gates.

## Purpose and recommendation

Build the smallest real localhost flow: open a basic Next.js page → sign in to GitHub through its authorization flow → retrieve the authenticated identity and paginated repositories through FastAPI → inspect repository eligibility and source coverage. Separately, run local AWS CLI/SDK probes using the intended local profile against named development resources.

The user selected **OAuth App**; the goal is to verify its delegated-access and coverage assumptions before investing in the full application. [ADR 0001](../adr/0001-oauth-app-and-local-pretesting.md) records the decision; no GitHub App comparison or implementation is required. Validate the localhost-to-AWS path early as well. A successful login or identity call is insufficient evidence of repository, team, private-content or resource-write access.

Use the existing `frontend/` and `backend/` roots so Phase 1 can reuse the scaffold, auth adapter interface, API client and tests. Keep diagnostic modules clearly isolated and disabled outside local development. Do not build a second throwaway application or add the taxonomy/AI pipelines during this phase.

Complexity: **M–L**, driven primarily by organization approvals, representative fixtures and AWS resource availability rather than UI complexity.

## What this phase delivers

1. Basic Next.js/TypeScript application with GitHub sign-in/sign-out, authenticated identity, paginated repository list, trusted GitHub links, and a small developer coverage view.
2. Minimal FastAPI backend for OAuth state/PKCE, callback/token exchange, server-only token storage, session validation and read-only GitHub API calls.
3. OAuth App source/scope/organization coverage verification; optional user browser login followed by identity/access confirmation. Save pre-testing reports as Markdown.
4. Local AWS identity/account/Region validation and a service-by-service access matrix, separating inspection, data-plane canaries, resource provisioning and future runtime-role access.
5. Automated localhost/security/contract tests, explicit live-test results, failure classifications, cleanup inventory, and recommendations for later phases.

No AWS dependency is required for the basic GitHub UI to work. Phase 0 does not persist real repo organization state, run an LLM, create production infrastructure, or mutate GitHub repositories.

## Inputs and prerequisites

| Input | Why it is needed / how it is handled |
|---|---|
| Approval of Phase 0 scope | Received: implement Phase 0 only; later phases remain unapproved |
| Node/Python/package tooling | Check installed tools and choose supported compatible pins; adopt npm/uv defaults unless an existing preference overrides them (D15) |
| Development OAuth App registration | Record auth mode, client ID, exact callback and configured permissions; use a dedicated development registration where available |
| OAuth client ID and secret | Supply via ignored backend environment or approved secret reference; never in `NEXT_PUBLIC_*`, frontend source, reports or Git |
| Representative repo fixture inventory | Known expected ownership/grants/contributions, visibility, starred/watched state and organization policies; aliases may replace private names in reports |
| At least two representative organizations | Use representative required organizations where available; include SSO/restricted-team policy where relevant; missing cases stay untested |
| Intended local AWS profile, account and Region | Use existing configured local credentials through CLI/SDK resolution; do not read or copy raw credential files |
| Named AWS test-resource manifest | Identify table names/ARNs, queue URLs, secret/key references, bus/log targets and optional bucket/model resources; avoid broad account enumeration |
| Approved scratch operations and ownership | Record test namespace, resource owners, allowed calls, cleanup and spending bounds before canary writes or resource creation |

Registrations or resources absent from the checkout are dependencies, not proof they do not exist. The implementation should obtain missing identifiers at setup time. Do not ask for secrets in chat or export credential caches.

## Workstream A — Localhost scaffold and authentication

### Recommended topology

Use one browser origin, provisionally `http://127.0.0.1:3000`, with Next.js forwarding `/api/v1/*` to FastAPI on `127.0.0.1:8000`. Register the callback exactly as `http://127.0.0.1:3000/api/v1/auth/github/callback` when supported by the development registration. Both services bind to loopback. Do not switch between `localhost` and `127.0.0.1` midway through login; cookies and callback matching must use the same chosen host.

GitHub documents loopback redirect URLs and recommends literal loopback addresses; verify the actual registration and auth mode rather than relying on implicit redirect matching. Use the same exact configured URI at authorization and token exchange, with wildcard matching disabled for the development registration where available. See [GitHub authorization and redirect documentation](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps).

FastAPI is useful even for this small spike: it keeps the GitHub token exchange and API access in the intended Python backend and tests the real browser/API boundary. Avoid a separate Next.js auth framework or a second browser-held token flow just for pre-testing.

### Minimal API and page contract

| Boundary | Behavior |
|---|---|
| `GET /health` | Process liveness; no secrets or cloud calls |
| `GET /api/v1/auth/github/start` | Create short-lived one-time state bound to the initiating browser's HttpOnly nonce/session and S256 PKCE where supported; redirect using the explicitly selected auth adapter |
| `GET /api/v1/auth/github/callback` | Validate state/expiry and exchange code server-side; call `/user` to establish numeric identity; rotate session; redirect to repo page |
| `GET /api/v1/me` | Session-derived identity and selected adapter/capability summary |
| `GET /api/v1/repos?view=my|favorites&limit=...&cursor=...` | Bounded pagination of trusted metadata; apply provisional eligibility policy without claiming unresolved provenance is confirmed |
| `POST /api/v1/auth/logout` | CSRF-protected local session invalidation and token discard; not automatic revocation of the user's GitHub authorization |
| `GET /api/v1/pretest/github/report` | Authenticated, local-only diagnostic counts/status for the approved source probes |
| Next.js `/` or `/repos` | Sign-in/out, name/owner/visibility/default branch/language/GitHub URL, source/eligibility/coverage, loading/error state and next-page action |

A bounded in-memory server session/state/token store is acceptable for this local single-process phase. Enforce explicit expiry, one-time state consumption, session rotation and ownership; discard tokens on sign-out/server shutdown. Clearly state that a restart requires sign-in again. Durable encrypted credentials and DynamoDB sessions remain Phase 1–2 work.

Cookies are HttpOnly and SameSite=Lax, with `Secure` disabled only for the explicitly local HTTP configuration. Production configuration must require Secure cookies, reject local-only diagnostics and forbid permissive callback origins. Validate CSRF/Origin on mutations; do not solve proxy problems with wildcard credentialed CORS. Tokens, authorization codes, state/PKCE verifiers and client secrets must be redacted from request logs, exceptions and reports.

## Workstream B — OAuth App access verification

OAuth App is the selected connector for this project. Exercise delegated user access without installing a GitHub App. Preserve source-specific coverage and actual granted scopes, and do not infer unrestricted organization access from successful sign-in. Browser verification is optional and user driven; when no browser tool is connected, review the Markdown report saved by the local page.

Maintain a fixture manifest with expected eligible/ineligible repos and known grant provenance. Compare actual IDs against that manifest, not against API counts alone. A small real set is sufficient if it covers the relationship cases below; force small page sizes to exercise pagination even for a small account.

| Probe / fixture | Calls / observations | Decision evidence |
|---|---|---|
| Identity and permissions | `/user`, returned numeric ID, actual granted scopes or configured app permissions, token mode/expiry behavior | Establish correct user after every callback and handle reduced permissions |
| Owned public/private | Paginated `/user/repos`, direct repo metadata for known expected IDs | Confirm access; preserve `(host,numeric repo ID)` and trusted `html_url` |
| Direct collaborator | Known fixture with a verified direct grant; API provenance where permitted | Separate effective permission from direct relationship; inability to enumerate collaborators is not proof of no grant |
| Team-granted | `/user/teams` and authorized team-repo listing on known fixture | Confirm team provenance when possible; record organization restrictions rather than inferring from broad read access |
| Organization-general access | Known accessible repo without ownership/direct/team/contribution relevance | It may be discoverable but stays excluded from My Repos by default |
| Recent contribution | GraphQL `viewer.repositoriesContributedTo` plus an accessible known contribution fixture | Verify useful coverage and pagination; do not infer lifetime contribution completeness |
| OAuth organization policy / SSO | Required org third-party restrictions, SSO authorization/session requirements and API error headers | Identify approval/SSO prerequisites; never respond by silently increasing scopes |
| Stars | Paginated `/user/starred`; known starred repo outside My Repos | Verify independent Favorites membership and deduplication |
| Watches | Authenticated `/user/subscriptions`; known watched repo(s); capability/error/empty-response observations | Resolve D02 for the tested token/policy; unknown or unavailable listing is not “zero watches” |
| README/metadata | Known public and, if authorized, private README plus languages/default branch/optional branch count | Verify Contents permission and missing/forbidden behavior; retain only bounded diagnostic metadata, not report copies of private README text |
| Basic personal activity | Known user-authored and other-author examples using available contribution/event APIs | Check feasibility of the later Latest Work design; full activity ingestion is still Phase 8 |

OAuth App `repo` scope includes write privileges; the application makes repository read calls only. No automatic scope escalation or GitHub writes. See [OAuth scopes](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps).

The [2026 watching change](https://github.blog/changelog/2026-06-30-upcoming-access-restrictions-to-public-api-endpoints-and-ui-views/) explicitly names `/users/{username}/subscriptions`; it does not establish authenticated `/user/subscriptions` completeness. Record the actual authenticated result and known-watch comparison, alongside the [watching API reference](https://docs.github.com/en/rest/activity/watching).

For every source: follow REST Link/GraphQL cursors; record API version, requested/granted permission context, pages, unique IDs, missing fixture aliases, status, rate-limit headers and sanitized error reason. Handle GraphQL partial errors even on HTTP 200. Use a read-only endpoint/query allowlist; token exchange is the required authentication POST, not permission to issue repository mutations. Conditional caching is optional here, but capture ETag/rate-limit feasibility for Phase 2.

Do not create, star, watch, rename or change GitHub repositories merely to seed tests. Use existing known fixtures or separately approved test-account setup. Unexpected 404/empty results may mean visibility restrictions; classify the evidence rather than declaring the repository absent.

### Required GitHub decision output

For the selected OAuth App, report: required permission scopes, organization approvals, expected/observed eligible repo IDs, direct/team attribution coverage, star/watch coverage, private README access, known exclusions, setup burden and recommendation. No alternate connector comparison is required by the latest user decision. Test representative organizations where available; unavailable relationships remain explicitly unverified; D01/D02 are not closed by a synthetic response or undocumented assumption.

If an alternative is ruled out by a documented organization installation policy, record that policy limitation and user acceptance. If required coverage cannot be established, Phase 0 reports the dependency and does not claim that it eliminated all GitHub access uncertainty.

## Workstream C — Local AWS access preflight

“All AWS resources” means the services/resources required or conditionally proposed by this project, not every resource in the account. Start with a manifest of exact development targets. Resource **inspection**, data-plane **use**, resource **creation**, and future deployed-role access are separate evidence columns.

1. Check local AWS CLI/SDK versions and the intended named profile/Region without printing credential material.
2. Use `aws sts get-caller-identity --profile <profile> --region <region>`; match the returned account/principal to the selected development target before proceeding. Identify network/credential/Region failures separately.
3. Reuse valid existing local credentials through the normal CLI/SDK provider chain. Preserve existing IAM Identity Center/SSO workflows. Do not switch profiles, overwrite defaults or authenticate again unnecessarily.
4. If credentials are expired/missing, follow the existing profile's authentication method. If using the installed `signing-in-to-aws` skill's `aws login` flow, it explicitly requires confirmation before invocation; obtain that only if this branch is needed. No login or AWS calls are being run while editing this plan.
5. Run the resource-specific read probes below with bounded timeouts/retries and explicit targets. Then run only the approved scratch canaries needed to establish data-plane permissions.
6. Compare local developer permissions with intended API/worker/deployment-role requirements. If an approved test role exists, optionally assume it and repeat relevant probes. Developer/admin success does not prove least-privilege runtime access.

STS GetCallerIdentity establishes identity, not service authorization ([AWS CLI reference](https://docs.aws.amazon.com/cli/latest/reference/sts/get-caller-identity.html)). IAM policy simulation may help diagnose an action but does not replace real service calls or cover every resource-policy/SCP situation ([IAM simulator limitations](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_testing-policies.html)). Do not attach policies or grant administrator access to make a failing probe green.

### AWS resource and operation matrix

| Service / scope | Basic named-target probe | Approved scratch canary / limits | What remains for later phases |
|---|---|---|---|
| **STS / identity — required** | GetCallerIdentity; account/principal/Region and credential expiry behavior | Optional AssumeRole only to an agreed existing test role | Deployed workload identity/OIDC and role trust validation |
| **DynamoDB — required, all three table roles** | DescribeTable for named Core/Intelligence/Organization dev or scratch tables; confirm PK/SK and state | Conditional PutItem/GetItem/Query/BatchGet and a small cross-table TransactWriteItems using only `PRETEST#<runId>` synthetic records; expected failed condition rolls back; delete own records and verify absence | Full catalog/alias/edge/reset schema, load/cost and concurrency correctness. DescribeTable alone is metadata access ([reference](https://docs.aws.amazon.com/cli/latest/reference/dynamodb/describe-table.html)) |
| **SQS — required, queue and DLQ** | GetQueueAttributes on exact URLs, including redrive/encryption settings | Send/receive/visibility-change/delete a correlated synthetic message in an **exclusive** scratch queue; bounded optional redrive-to-DLQ test. Never poll/purge a live worker queue | Production workers, retries, poison-message policy and scaling. GetQueueAttributes is an inspection operation ([reference](https://docs.aws.amazon.com/cli/latest/reference/sqs/get-queue-attributes.html)) |
| **Secrets Manager — required** | DescribeSecret on a designated non-sensitive canary secret | GetSecretValue on that known dummy value, compare in memory and report only boolean success; no actual OAuth/user token secrets fetched for a smoke test | Credential encryption/rotation/service-role secret access. Metadata inspection does not retrieve the value ([reference](https://docs.aws.amazon.com/cli/latest/reference/secretsmanager/describe-secret.html)) |
| **KMS — conditional on selected customer-managed keys** | DescribeKey/alias on exact key if the dev resources use one | Known synthetic encrypt/decrypt with appropriate encryption context, or verify through the intended encrypted service integration when policy permits service-only use | Production key/resource policy. Direct KMS denial may be expected under service-only conditions; no customer-managed key is required just for testing service-managed encryption ([reference](https://docs.aws.amazon.com/cli/latest/reference/kms/describe-key.html)) |
| **EventBridge — required for planned refresh/evaluation scheduling** | DescribeEventBus and existing relevant rule/target configuration where permitted; use Scheduler-specific read APIs instead if that is the selected scheduling service | PutEvents only to an isolated approved test bus; verify per-entry failures. If a scratch SQS target/rule exists, observe the correlated event delivery; otherwise report ingestion only. Scheduler execution canary is separate if selected | Actual schedule execution/target-role permissions; bus access does not prove Scheduler access ([EventBridge reference](https://docs.aws.amazon.com/cli/latest/reference/events/describe-event-bus.html)) |
| **CloudWatch Logs / metrics — required observability path** | Inspect the designated test log group/configuration, not private application log content | Write one synthetic log event to a test stream and optionally a metric in the agreed pretest namespace; verify delivery with bounded eventual-consistency retry | Runtime log roles, alarms, dashboards and costs; inspection alone is not write proof |
| **S3 — optional content/artifact cache** | HeadBucket on exact approved bucket/Region if S3 will be used | Put/Get/Delete one synthetic object under the agreed pretest prefix; account for versions if versioning is enabled | No S3 cache introduced merely to run a probe; permissions depend on chosen object/encryption policy ([HeadBucket reference](https://docs.aws.amazon.com/cli/latest/reference/s3api/head-bucket.html)) |
| **Hosted LLM / Bedrock — conditional candidate** | Record provider endpoint/Region/model availability and required auth path if already selected | Optional one tiny synthetic schema-output request with agreed spend cap; no repo/private text. Availability listing is not invocation proof | Final provider/schema/token-quality evaluation remains D11/Phase 5–6; do not select Bedrock merely because AWS is used |
| **Compute/registry/IaC/IAM deployment — conditional/deferred** | Named ECS/Lambda/ECR/CloudFormation targets only after hosting selection; inspect approved role/trust requirements | No deploy/image push/role change by default; no generic `iam:PassRole` smoke call is claimed | D14/D15 hosting/IaC decision, scoped deployment identity and real workload-role tests in Phase 10 |

Read probes can fail because target resources do not exist, credentials expired, account/Region is wrong, endpoints are private/network-restricted, or IAM/resource/key/SCP policy denies an action. Preserve the distinct cause and remediation owner; do not collapse everything into “AWS access failed.” Account-wide List permissions are not a prerequisite when exact target identifiers are known.

### When test resources do not exist

Do not mark resource access as tested using only STS or an IAM simulation. Offer a concrete, minimal development scratch-resource manifest and estimated test spend for review. Resource creation must be within approved scope; no automatic production stack deployment or policy changes. Where approved, scratch tables/queues/bus/log group/dummy secret support the listed canaries, while final application schemas stay Phase 1 work. Optional services can be NOT_APPLICABLE or DEFERRED with an explicit reason; required unexercised operations remain NOT_TESTED/BLOCKED.

Every canary carries a run ID and owner manifest; cleanup may remove only records/messages/objects created by that run. Record residual artifacts and cleanup failures; never use queue purge, table deletion or broad-prefix cleanup against shared targets. Resource teardown itself must follow the agreed scratch-resource ownership/approval scope.

## Workstream D — Additional pre-tests

| Test group | Required cases / why it belongs in Phase 0 |
|---|---|
| OAuth/callback security | Valid flow, user cancellation, missing/mismatched/expired/replayed state, callback opened in the wrong browser session, wrong callback, account switch, session fixation, sign-out and restart. Actual flow live; invalid/expired-token branches may use labeled fixtures |
| Browser/API boundary | HttpOnly cookie is not readable by JS; no token in localStorage/sessionStorage, response JSON, frontend bundle or logs; proxy preserves callback/cookie behavior; mutations reject foreign Origin/CSRF |
| Network/tooling | Free local ports, loopback binding, package/runtime compatibility, GitHub REST/GraphQL/token endpoints and required AWS endpoint TLS; corporate proxy/CA/clock-skew diagnosis without disabling verification |
| Pagination and failures | Small-page traversal with unique-ID dedup; REST Link and GraphQL cursors; 401/403/404/429/5xx, GraphQL partial errors, timeouts and rate-limit backoff. Do not deliberately exhaust live quotas |
| Repo semantics | Owned/direct/team/contributor/ORG_GENERAL comparison, private versus public, Favorites-only repo, unsupported watches, source union duplicates and unknown metadata values |
| Token/session lifecycle | Expiring/reduced-scope tokens, refresh capability when applicable, reauthorization and stale session; no forced real-user revocation without a controlled approved fixture |
| AWS operation-level permission | Read versus write versus create versus runtime identity; one intended conditional DynamoDB transaction and SQS round trip are stronger evidence than a list call |
| Negative authorization | Controlled missing-scope/denied-resource fixture where practical; fail closed without exposing tokens. No probing unrelated accounts/resources to manufacture a denial |
| Privacy and costs | Reports contain counts/aliases and sanitized error metadata, not credentials/private README bodies; bounded calls/canary sizes, retention of local diagnostic output, observed API usage and cleanup |
| Repeatability | Stop/start, fresh browser session, duplicate probe retry and rerun with new run ID; successful behavior must not depend on leaked browser tokens or leftover test data |

README extraction quality, full activity history, taxonomy/AI correctness, high-volume load tests, production deployment and reset implementation remain later-phase work. These pre-tests establish feasibility and permissions rather than closing those feature gates.

## Proposed files and execution sequence

The Phase 0 scaffold and probes now exist; later production extensions remain proposals. See the setup guide and actual results for executable interfaces.

| Paths | Phase 0 purpose / later disposition |
|---|---|
| `frontend/package.json`, lockfile, `next.config.*`, `src/app/{layout,page}.tsx`, `src/lib/api.ts` | Minimal Next.js app and same-origin API proxy; reuse in Phase 1 |
| `backend/pyproject.toml`, lockfile, `app/{main,config}.py` | Minimal FastAPI startup/configuration; reuse and harden |
| `backend/app/auth/`, `github/{adapter,client}.py`, `api/{auth,repositories}.py` | Small auth/session/read adapter boundary; Phase 1–2 add durable state, lifecycle and worker integration |
| `backend/app/pretest/{github_probe,aws_smoke,report}.py` | Bounded CLI/diagnostic probes; local-only, never exposed as a production AWS-execution API |
| `backend/tests/pretest/`, `frontend/tests/pretest/` | Contract/browser tests and fixtures, including clearly labeled live markers |
| `.gitignore`, backend ignored local environment, `.env.example`, `docs/development/phase-0-localhost.md` | Setup/restart/callback/profile/resource instructions without secret values |
| `infrastructure/phase0/resource-manifest.example.json` | Example identifiers/ownership/allowed canary actions; actual identifiers in an ignored local file |
| `docs/validation/phase-0-results.md`, sanitized report schema | Test evidence, connector/access recommendation and cleanup; private detailed reports remain ignored local artifacts |

Sequence: **0A** confirm approved inputs/targets → **0B** pin tools and start Next.js/FastAPI → **0C** implement OAuth callback/session and minimal repo page → **0D** run known-fixture OAuth coverage/pagination/security tests → **0E** run AWS identity/named-target probes and approved canaries → **0F** cleanup, evidence review and decision updates → **Phase 1 approval**.

GitHub and AWS probes are independent: the repo page remains usable if a named AWS resource is missing, and the results report shows that AWS dependency separately. Running unapproved canary/provisioning actions is not a prerequisite for delivering a partial, candid report.

## Planned validation commands

Run the implemented commands in [localhost setup](../development/phase-0-localhost.md). The live GitHub entrypoint is the authenticated page action, not a credential-loading pytest command.

| Command / context | Evidence |
|---|---|
| `npm --prefix frontend run dev` and `uv run --project backend uvicorn app.main:app --host 127.0.0.1 --port 8000` | Local UI/API startup; frontend dev script must also bind loopback |
| `npm --prefix frontend run typecheck`, `run lint`, `run build`, `run test:pretest` | Minimal scaffold/browser checks; full commands documented in setup |
| `uv run --project backend pytest backend/tests/pretest -m "not live"` | Credential-free callback/session/API/failure fixtures |
| Browser: **Verify access & save report** | Explicit live OAuth source/fixture checks; saved Markdown |
| `aws sts get-caller-identity --profile <profile> --region <region>` | Selected local identity only; no service-access assertion |
| `uv run --project backend python -m app.pretest.aws_smoke --manifest <local-manifest> --mode inspect` | Named-resource read results with explicit profile/account/Region checks |
| Same smoke command with `--mode canary` (generated run ID) | Only manifest-approved scratch operations and cleanup; not provisioning |
| `docs/validation/phase-0-results.md` plus generated Markdown reports | Combined evidence and decisions; report.py is a writer library, not a CLI |

Use the AWS SDK for Python skill when implementing boto3 probes. Use the relevant service/IaC guidance if approved scratch resource creation is needed. CLI/SDK profiles stay server-side; a browser action must not accept arbitrary AWS operation/resource arguments.

## Results and exit criteria

Track each test with status **PASS**, **FAIL**, **BLOCKED**, **NOT_TESTED**, or **NOT_APPLICABLE**, and evidence type **LIVE**, **FIXTURE**, or **POLICY/DOCUMENTATION**. A separate DEFERRED disposition requires an owner, affected future phase and user acceptance; it is not a passing test. Expected-denied negative cases can PASS only when the expected denial is explicit.

Report run/date, test ID, auth mode or AWS principal alias, account/Region, resource/repo alias, action/source, observed versus expected outcome, sanitized error category, permissions/setup needed, owner/next step and cleanup state. Record API request IDs where useful; no tokens, full raw responses or private source text. The committed summary may redact account/resource identifiers; local protected evidence can retain the identifiers needed to diagnose access.

Current live evidence: user-saved reports confirm private metadata/Contents/README access for both named fixtures. Organization reconciliation fixed a 78-repository discovery gap; two organization cross-checks now have zero missing IDs. Inventory totals 310 unique repositories, including two private, with 106 My Repos and 224 Favorites. Required AWS targets were created and passed inspection, 28 canary/cleanup checks and a separate artifact audit. See the [GitHub review](../validation/github-access-review-2026-10-11.md) and [AWS review](../validation/aws-access-review-2026-10-11.md). Unchecked limitations below are not implied to pass.

Phase 0 is complete when:

- [x] Next.js/FastAPI starts reproducibly and the live OAuth callback establishes the correct GitHub identity.
- [x] The UI fetches and paginates real repos through the backend, exposes trusted GitHub links, and shows source/eligibility/coverage without AI or DynamoDB. Pagination/link safety also has regression coverage.
- [x] OAuth App is documented as user selected; named private fixtures and two representative organization cross-checks confirm tested access. Hidden-policy, direct-grant and complete independently supplied organization expectations remain documented limitations.
- [ ] D02 authenticated watches and direct/team/SSO limitations have measured results or specifically accepted limitations; missing evidence is not marked resolved.
- [x] OAuth/browser security and failure tests pass; live versus fixture evidence is clearly distinguished.
- [x] Intended local AWS identity/account/Region is established; every required named service has an operation-level result, with inspection, provisioning and data-plane evidence separated.
- [x] Required scratch canaries passed; conditional services remain NOT_APPLICABLE because no customer-managed key, bucket, model or compute placement is selected. Runtime-role/deployment tests remain later gates.
- [x] No unrelated GitHub/AWS data was modified. Owned canary artifacts were removed and audited; scratch resource teardown is separately tracked.
- [x] Results update D01/D02/D15 and the new D16 AWS access decision; later security/quality/deployment gates remain open.
- [ ] User reviews results, accepts any conditional exit/dependencies, and approves Phase 1 separately.

Recommend a **GO** only with essential GitHub discovery demonstrated and AWS evidence sufficient for the next phase. A **CONDITIONAL GO** may permit local Phase 1 scaffolding with named AWS/optional-provider gaps, but does not close affected live-integration gates. A **NO-GO** applies when required GitHub coverage cannot satisfy the product or safe authentication cannot be demonstrated.

## Recovery and handoff

On denied/expired GitHub access, discard the local session/token and present the source-specific reauthorization/approval dependency; never downgrade to an unexplained privileged token. On AWS failure, stop that target's mutations, preserve sanitized diagnostics and use the same approved profile until an intentional change is made. Run cleanup by manifest/run ID, with retry and residual reporting.

Stopping the local backend removes in-memory OAuth state/sessions; no application-data reset is needed. Resource deletion/authorization revocation is separate from stopping the app and must follow the agreed test-resource scope. Promote the scaffold and proven adapters/tests into Phase 1, replace local-only session/token storage with the approved production-safe contracts, and retain regression evidence for Phase 2.

Phase 0 implementation is authorized and delivered locally. Basic live GitHub access now passes; [actual results](../validation/phase-0-results.md) record local checks, two reviewed OAuth reports, AWS identity and remaining fixture/target dependencies. Review the full results before any Phase 1 approval.
