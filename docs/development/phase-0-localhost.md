# Phase 0 localhost and access checks

Phase 0 is approved. OAuth App is selected in [ADR 0001](../adr/0001-oauth-app-and-local-pretesting.md). [Results and remaining live gates](../validation/phase-0-results.md) distinguish local fixture checks from live coverage. Phase 1 is not approved.

## Install and run

Use Node 24.21.0 (`.node-version`), Python 3.13 (`backend/.python-version`), npm and uv. Lockfiles record exact dependencies. This workstation also has an ignored Node installation in `.tools/node` and uv in `.tools/bootstrap/bin`; the scripts use local Node automatically. No global runtime installation was made.

From the repository root:

```bash
export PATH="$PWD/.tools/node/bin:$PATH" # only when using the bundled local Node
npm --prefix frontend ci
uv sync --project backend --frozen
cp backend/.env.example backend/.env # first setup only; preserve existing values
chmod 600 backend/.env
```

If uv is not on PATH, use `.tools/bootstrap/bin/uv` in its place. On another machine install supported runtimes normally; `.tools` is not committed.

Use two terminals:

```bash
bash scripts/dev-backend.sh
```

```bash
bash scripts/dev-frontend.sh
```

Open **http://127.0.0.1:3000**. Backend liveness is http://127.0.0.1:8000/health. Both servers bind loopback. Stop with Ctrl+C. Backend restart clears all OAuth state, sessions and tokens and requires sign-in again. Restart the backend after changing `.env`; frontend edits reload automatically. Do not substitute `localhost` halfway through an authorization flow because cookies and state are host bound.

## Register the GitHub OAuth App

At [New OAuth App](https://github.com/settings/applications/new), enter:

| Field | Value |
|---|---|
| Application name | GitHub Manager Local |
| Homepage URL | `http://127.0.0.1:3000` |
| Authorization callback URL | `http://127.0.0.1:3000/api/v1/auth/github/callback` |
| Enable device flow | Disabled |
| Expire user access tokens | May stay enabled; local sessions cap lifetime and require sign-in again, without refreshing tokens |

Register, copy the client ID, generate a client secret, and set `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` in ignored `backend/.env`. Never use `NEXT_PUBLIC_*` for secrets or paste them into reports/chat. Restart the backend, then reload the page. [GitHub registration guide](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app).

Default scopes are `read:user repo read:org notifications`. The OAuth consent includes broad repository permission because private access uses `repo`; this code makes read-only repository calls. Organization approval and SSO may still be necessary. Reduced scopes are allowed for deliberate tests; results must disclose missing coverage. [OAuth scopes](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps).

Choose **Continue with GitHub**, complete GitHub login and authorization yourself, then confirm the displayed username and numeric GitHub ID. Review **My repositories**, **Favorites**, **Access candidates** and source coverage. Organization visibility alone stays excluded from My repositories. Direct affiliation and team provenance still need representative fixtures. A successful traversal is OBSERVED, not a completeness claim.

## Optional browser verification and Markdown report

You can sign in whenever convenient. With a connected browser tab, the agent can inspect the displayed identity and source results after you finish login; passwords, MFA and GitHub authorization stay in your browser. If no browser surface is connected, use the local page and choose **Verify access & save report**. The agent can review the saved report without reading tokens or exporting cookies.

The action refreshes the live inventory, runs configured fixtures, and writes `docs/validation/private/github-<UTC-run>.md`. This directory is ignored. Reports retain the signed-in GitHub login and numeric ID for identity confirmation, but omit repo names, raw API bodies, README content, tokens, codes and verifiers. The page offers an authenticated Markdown download. Report files use mode 600; retention is manual for this local phase. Logout discards this app's local token/session; it does not revoke your GitHub authorization. Review/revoke authorization separately in GitHub settings if desired.

For representative expectations, copy `backend/github-fixtures.example.json` to ignored `backend/github-fixtures.local.json`. **Replace every illustrative ID** with a repository you are authorized to test, remove inapplicable examples and set expected sources/eligibility/Favorites. Include public/private ownership, verified direct/team grant, org-general-only, contribution, a star outside My Repos and a known watch where available. Include representative restricted/SSO organizations when relevant. Set `GITHUB_FIXTURES_FILE=github-fixtures.local.json` in `.env` and restart before signing in. Relative fixture paths resolve against the backend directory.

Each repository fixture can use a numeric `repo_id`, an `owner/repo` `full_name`, or both. Named fixtures first fetch direct metadata and compare its stable ID with the inventory, so an omitted repository can be distinguished from inaccessible metadata. `private` checks expected visibility; `contents_access` checks the root file-list and README access, discarding their responses. `readme_present` asserts known README presence/absence. `recent_commit_by_user` checks at most ten commits from the past 14 days; it does not prove complete activity history.

`sample_private_repositories` (0–3) selects observed private examples for content-access tests. `sample_member_organizations` (0–2) selects active memberships and cross-checks organization repository IDs against the inventory. Samples establish access and consistency, not independently known complete sets. Explicit `organizations` fixtures accept `alias`, `login`, `expected_repository_ids` and `exact_accessible_set`; exact comparison requires an independently supplied expected set. Unsupported relationships/SSO policies remain documented gaps. Reports use aliases; avoid sensitive aliases. Fixture files are re-read on each report run, so changing the manifest alone does not require restarting the backend.

The live user-named fixtures were configured locally and both passed private metadata, discovery, Contents and README access. Organization cross-checking exposed 78 missing candidates: discovery now unions `/user/repos` organization affiliation with paginated `/orgs/{org}/repos` for enumerated memberships. Organization visibility alone still does not make a repository eligible for My repositories.

## AWS inspection

The user selected `default` / `us-east-1`. Existing credentials are reused; there are no access keys in app config. STS proves identity only.

```bash
aws sts get-caller-identity --profile default --region us-east-1
PYTHONPATH=backend backend/.venv/bin/python -m app.pretest.aws_smoke --mode inspect
```

With no manifest this saves a Markdown report and marks required resource checks BLOCKED. Exit code 1 means failed/blocked evidence; it is intentional when target IDs are absent. Optional services remain NOT_APPLICABLE until selected.

Copy `infrastructure/phase0/resource-manifest.example.json` to `infrastructure/phase0/resource-manifest.local.json`. Set the expected account and exact authorized identifiers. Use table names for the Core/Organization/Intelligence scratch roles, queue URLs for SQS, a known dummy secret ID, event bus name and log group name. KMS, S3, Bedrock, Lambda and ECS are conditional. No account-wide resource scan is performed.

```bash
PYTHONPATH=backend backend/.venv/bin/python -m app.pretest.aws_smoke \
  --manifest infrastructure/phase0/resource-manifest.local.json --mode inspect
```

Reports default to ignored `docs/validation/private/aws-<UTC-run>.md`. `--output docs/validation` saves a sanitized shareable report. Never pass credentials on the command line.

## Approved scratch canaries

Review exact target ownership and operations before setting `approved_canary: true`. All canaries require an expected account matching STS. **The example defaults to false.** The smoke runner does not create resources, modify IAM or prove deployed-role permissions. The separate scratch provisioner below creates only the authorized eight-resource set.

```bash
PYTHONPATH=backend backend/.venv/bin/python -m app.pretest.aws_smoke \
  --manifest infrastructure/phase0/resource-manifest.local.json --mode canary
```

| Service | Canary / cleanup boundary |
|---|---|
| DynamoDB | Two-item transaction/readback per table; when all three approved roles use PK/SK, also conditional PutItem, Query, BatchGet, three-table transaction and expected failed-condition rollback. Owner-conditioned deletes and cross-table cleanup absence checks. No Scan or foreign-row overwrite. |
| SQS | Send/receive/change visibility/delete own message; requires `exclusive_scratch: true` and initially empty queue. Foreign messages are restored and never deleted. Timeout may leave a message identified by run ID. No purge. DLQ round trip does not prove redrive routing. |
| Secrets Manager | Read only a known dummy value and compare its SHA-256 against `dummy_sha256`; value discarded. No real token secrets. |
| KMS | Encrypt/decrypt random bytes with run-specific context; no persisted artifact. |
| EventBridge | Put one event on an exclusive scratch bus with no real consumers; event acceptance is not delivery/Scheduler access. An event cannot be retracted. |
| CloudWatch Logs | Create run-owned stream, put synthetic event, bounded exact readback, delete that stream; cleanup is reported separately. |
| S3 | Put/get a unique run-owned object, then delete its returned version where versioned. No broad-prefix deletion. |
| Model/compute | Metadata inspection only. Model invocation, ECR, task execution, runtime IAM, Scheduler invocation and deployment remain separate gates. |

Each run generates an unpredictable owner ID. Cleanup failures remain FAIL rows even if the canary passed. Network ambiguity during a write can leave residual artifacts; investigate only the reported owned run. The user authorized the scratch creation/canaries, which passed on this workstation; see [AWS evidence](../validation/aws-access-review-2026-10-11.md).

## Isolated scratch provisioning

The [template](../../infrastructure/phase0/scratch-stack.json) creates three on-demand tables, two encrypted queues, one generated dummy secret, one bus without consumers and one short-retention log group. It creates no IAM resources, production app, compute, VPC or model invocation. This does not select production IaC.

```bash
.tools/cloudformation/bin/cfn-lint --format json --regions us-east-1 \
  --template infrastructure/phase0/scratch-stack.json
.tools/guard/cfn-guard-v3-x86_64-macos-latest/cfn-guard validate \
  --rules infrastructure/phase0/scratch.guard \
  --data infrastructure/phase0/scratch-stack.json --output-format json --show-summary none
PYTHONPATH=backend backend/.venv/bin/python -m app.pretest.aws_scratch prepare \
  --expected-account <approved-account-id>
PYTHONPATH=backend backend/.venv/bin/python -m app.pretest.aws_scratch execute \
  --expected-account <approved-account-id>
```

The installed local validators are cfn-lint 1.57.2 and Guard 3.2.1 (official release digest verified); other machines need their own compatible installation. `prepare` reserves a private ownership file and creates a validated eight-addition change set, without provisioning targets. `execute` verifies identity, local/remote template, change set tags and exact stack ARN before creation. It saves the exact target manifest and synthetic hash baseline with mode 600. Default ownership state is `docs/validation/private/aws-scratch.local.json`; an existing ownership file is never adopted or overwritten by preparation. Do not rerun these commands to create duplicate resources when reusing the existing local manifest suffices.

The `Expires` tag is a review date, not automatic deletion. Resource teardown is separately approved and must check ownership; preserve all reports afterwards. Do not repoint a deleted scratch manifest at another resource. The [scratch scope](../planning/phase-0-aws-scratch-proposal.md) records cost/lifetime and teardown state.

## Automated checks

With the backend running, install Chromium once and run:

```bash
export PATH="$PWD/.tools/node/bin:$PATH" # if using local Node
export PLAYWRIGHT_BROWSERS_PATH="$PWD/.tools/playwright"
frontend/node_modules/.bin/playwright install chromium
bash scripts/check-phase0.sh
```

Browser tests reuse an existing frontend or start one on loopback. They use fresh isolated contexts and fixture intercepts for signed-in behavior; they do not log in to GitHub or touch the user's session. Backend tests use MockTransport and Stubber/fakes. Live authorization, representative source completeness and AWS writes require separate live evidence.

No production persistence/security, model quality, reset, high-volume performance or deployment acceptance is implied by these checks.
