# GitHub Sync and local-session timeout: backend verification

Date: 2026-10-18 (America/New_York). Scope: the authorized local-app timeout fix; frontend integration and final production checks are recorded separately by the coordinating agent.

## Findings

The app session had a fixed, default 3,600-second lifetime with no browser-visible deadline or renewal endpoint. Reading `/me` did not renew that session. The local OAuth store is deliberately in memory, so a backend restart also requires sign-in again. These are app-session events, distinct from GitHub request timeouts or GitHub revoking an access token.

The worker already used bounded individual GitHub requests, but an entire Sync could traverse many pages and organizations without an overall deadline. GitHub inventory and activity helpers also treated some HTTP 401 responses as partial source coverage, hiding the need to sign in again. A queued Sync with an expired session could remain `WAITING_FOR_REAUTH`, hold the workspace's active-job slot, then resume after another sign-in.

The stored 180-second worker lease is not an in-process countdown: the current store does not reclaim running jobs when that timestamp passes. It is not evidence that this lease caused the reported silent timeout.

## Changes

### Explicit session warning and extension contract

`GET /api/v1/me` retains its existing identity/CSRF fields and adds:

```json
{
  "session": {
    "expires_in_seconds": 3600,
    "warning_seconds": 120,
    "renewable": true,
    "extension_seconds": 3600
  }
}
```

These are relative durations, not the server's monotonic-clock epoch. Default warning is 120 seconds, reduced for short configured local sessions. Passive polling does not extend a session.

`POST /api/v1/auth/session/extend` requires the existing, unexpired server session, exact configured Origin, and its CSRF token. It returns the same identity envelope and refreshes the existing HttpOnly/SameSite cookie's `Max-Age`. It does not rotate the identity, change scopes, make a GitHub request, or refresh a provider token. Expired sessions cannot be resurrected.

If the OAuth exchange supplies `expires_in`, the in-memory session retains that grant's hard deadline. Renewal is capped by it, and `renewable` becomes false when it cannot extend further. When no provider expiry is returned, the implementation does not invent an eight-hour provider lifetime. The existing policy of discarding provider refresh tokens remains unchanged.

All application HTTP 401 responses preserve readable `detail` and add `code: SESSION_EXPIRED` and `reauthentication_required: true`, allowing the client to leave a dead workspace and show sign-in explicitly.

### Bounded Sync and explicit recovery

`GITHUB_SYNC_TIMEOUT_SECONDS` defaults to 300 (validated range 30–1,800). The worker uses an async overall deadline in addition to individual request timeouts. Sync records `started_at`, `timeout_seconds`, and visible progress stages: `INVENTORY`, `ACTIVITY`, `COMMIT`, `DONE`.

| Failure | Run error code | Expected action |
|---|---|---|
| Local session ends before/during Sync | `SESSION_EXPIRED` | Sign in, explicitly retry Sync |
| GitHub returns 401 or changes numeric identity | `GITHUB_REAUTH_REQUIRED` | Sign in, explicitly retry Sync |
| GitHub request network/timeout error | `GITHUB_TIMEOUT` | Check connection, explicitly retry |
| Overall Sync deadline | `GITHUB_SYNC_TIMEOUT` | Check connection, explicitly retry |
| GitHub rate limit | `GITHUB_RATE_LIMITED` | Wait for reset, explicitly retry |
| Backend restarts during Sync | `GITHUB_SYNC_INTERRUPTED` | Sign in if needed, review and explicitly retry |

Failures become terminal `FAILED` records with `retryable` and `reauthentication_required` flags, a safe explanatory message, and no lingering active-job flag. An expired queued Sync fails visibly instead of automatically resuming after sign-in. Existing AI/reset queue policy is unchanged.

A provider 401 now propagates through parallel inventory sources, organization/team listing, activity pages, and activity-only repository discovery. Only sessions carrying the failed provider grant are invalidated; another newer grant is preserved. A revoked or signed-out session object cannot commit an old Sync merely because a different session for the same owner has appeared.

Sync still stages its remote inventory before one local commit. Deadline/session failures before that commit preserve the prior repository inventory, saved intelligence and organization decisions. Partial non-authentication source failures retain the existing explicit coverage reporting; a denied activity source does not erase the independently successful source.

## Validation

- Focused auth, session, GitHub, activity, and Sync checks: **58 passed**.
- Full demo regression suite plus auth/session/GitHub checks: **179 passed** before the final additive restart-metadata regression.
- Final Sync timeout/recovery suite plus existing AI restart-safety regression: **12 passed**, including the new Sync interruption metadata and unchanged inference recovery.
- Ruff checks passed for changed application/test files; formatting checked separately.
- Tests use temporary databases, controlled clocks, fake adapters and HTTP mock transports. They make no live GitHub/OpenAI/AWS calls and do not edit the user's corpus, human reviews, budget ledger, secrets or OAuth registration.

New checks cover explicit renewal versus passive countdown; Origin/CSRF rejection; cookie attributes; provider-deadline capping; expired and restarted sessions; failed-grant-only invalidation; overall async cancellation; rate/network errors; inventory/activity/identity 401; expiry or sign-out during Sync; queued expiry without replay; and normal completion. Preservation assertions include repository state, intelligence, organization memberships, human reviews and incomplete drafts.

## OAuth evidence and limits

GitHub now supports optional expiring OAuth App tokens. Its documentation describes `expires_in` and optional refresh tokens, including runtime opt-in through `offline_access`. This change respects returned expiry without introducing that scope or implementing a refresh flow. Sources: [Authorizing OAuth apps](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps), [GitHub's August 14, 2026 OAuth update](https://github.blog/changelog/2026-08-14-multiple-redirect-uris-and-token-refresh-for-oauth-apps/).

An explicit local extension can only honor locally known provider deadlines. A token revoked externally without a known expiry is detected on the next GitHub request; this endpoint does not claim to validate remote authority without making that request. Restart survival remains out of scope for the intentionally memory-only local session store. No architecture or persistent-data migration is introduced.
