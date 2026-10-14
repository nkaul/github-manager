# Local AI allowance controls

The allowance limits OpenAI use; it does not limit GitHub sync, browsing, manual organization, extraction or rules. Each fresh model generation normally needs two HTTP requests: one token count and one generation. Taxonomy discovery and classification share the same allowance.

## Adaptive cost budget

Open **AI Organization** in the header. Set separate **Taxonomy sample size** and **Classification batch size**, choose **Choose a number automatically** or **Manual selection**, and confirm the current-filter or entire-collection scope. Each local run is bounded to 30 repositories.

Select **Adaptive cost budget**, initially **$0.25 maximum per run**. Click an operation to preview; inspect the requested, eligible, chosen and excluded counts, exact repositories, conservative dollar bound and finite HTTP/generation grant. Then click **Start reviewed run**. Preview and Save defaults use no OpenAI calls. Taxonomy still needs draft approval; classification still produces suggestions for review.

Adaptive mode can proceed when the fixed count window is exhausted. Its reviewed grant is bounded by dollars and derived finite calls, with the original cumulative $5 ceiling. The chosen count may be smaller than requested if fewer fit. No private/unverified model evidence is admitted. Only configured budget operators can start adaptive paid work or save adaptive defaults. Automatic organization can reuse saved defaults when explicitly enabled, with its existing quiet period/cooldown.

The **Available for runs** and **Run holds** amounts disclose unreserved funds and pending run commitments. Run history records adaptive attempts and estimated usage. Unknown calls retain conservative reservations; unused run holds are released after completion/recovery. The app does not read the provider's credit balance. See [ADR 0004](../adr/0004-cohorts-and-adaptive-budgets.md).

## Renew or selectively change fixed limits

1. Sign in and open **AI Organization → Manage API allowance**. Finish any current run first.
2. To repeat testing, choose **Start a fresh allowance window**. The default grants **20 HTTP requests and 10 generations**. Review the values and enter a reason, then click **Renew allowance window**.
3. To change only one limit, choose **Selectively update current window limits**. Check the limit(s) you want to change, enter their total allowance for this window, and click **Save selected limits**. For example, changing HTTP from 20 to 40 after using 12 leaves 28 HTTP attempts; the generation limit stays unchanged unless selected too. To permit 20 generations in that window, select the generation limit and set it to 20 as well.

The fixed counters show current-window fixed-mode usage; adaptive-scoped attempts use their own run grants. Lifetime totals include both modes; recent allowance changes are also visible. Changes survive restart and apply across both collections and all local logins. No model request is made by either control.

The **cumulative $5 spending ceiling remains enforced**. Historical spending, outstanding reservations, request rows, generation records, model caches and Markdown reports are retained. Organization reset and allowance renewal are separate operations. Additional provider credit does not automatically change these application limits.

## Operator configuration

`backend/.env` contains the server-only `DEMO_BUDGET_OPERATOR_IDS` setting. Use the numeric GitHub user ID, with commas for multiple trusted operators. This setting also authorizes adaptive paid runs and adaptive saved policies. The current workspace owner is configured in this checkout. Empty disables changes through the web UI. Changes to that setting require a backend restart and sign-in again.

Live inference must also be enabled (`bash scripts/dev-demo.sh --live-ai`) and a valid OpenAI key must already be configured. Only the previously approved public/synthetic input scope is enabled.

## Local CLI

Run from `backend`:

```bash
.venv/bin/python -m app.demo.manage_allowance status
.venv/bin/python -m app.demo.manage_allowance renew --requests 20 --reason "Another local rehearsal"
.venv/bin/python -m app.demo.manage_allowance set --requests 40 --reason "Extend current HTTP window"
.venv/bin/python -m app.demo.manage_allowance set --generations 20 --reason "Extend current generation window"
```

For scripts, pass `--expected-revision` from the status response to reject stale changes. The CLI requires local filesystem access to the existing ledger; it does not create a replacement experiment or clear history. Avoid editing SQLite counters, deleting budget files or resetting the original Phase 0.5 ceiling.

## Access candidates

**Access candidates** contains all repositories discovered through the account's configured GitHub sources. It can include organization-visible repositories and favorites whose relationship is insufficient for automatic inclusion in My Repos. It is a review pool, not a search of all public GitHub repositories or a way to request new GitHub permissions.

**My Repos** contains repositories with an eligible owner/collaborator/team/contributor relationship, plus your explicit inclusions. Open a candidate's **Details → Include in My Repos** to include relevant accessible work locally. You can later remove that explicit inclusion. GitHub permissions, repository contents and stars/watches are unaffected.
