# Session, Sync recovery and Home navigation

October 18, 2026. Implemented in the local app. This record includes the fixture-port incident discovered during validation and its correction.

## User-visible behavior

- The default one-hour application session warns two minutes before expiry. **Extend session** explicitly extends a still-valid session by the configured duration, capped by any known GitHub token deadline. Passive browsing does not extend it. **Save work first** returns to the editor, including during the final ten seconds. A final warning can follow an earlier dismissal.
- Expired authenticated requests return the app to its sign-in page with an explanation and clear disabled/busy UI state. Saved work remains in the database. Unsaved edits still need to be saved before expiry; the warning does not silently confirm or save a human review.
- GitHub Sync has an overall configurable five-minute deadline in addition to individual request limits. It exposes progress stages, warns near the deadline, and shows actionable timeout/failure recovery. A failed/interrupted Sync clears its active-job slot. A persistent notice lets the user reopen recovery options. **Retry sync** is explicit; expiry/restart does not silently replay Sync.
- Browser API requests have a thirty-second limit covering response headers and body. Network/transport failures are distinguished from authentication expiry. An uncertain mutation is never automatically repeated.
- The GitHub Manager brand returns to the GitHub home view. Ground Truth preserves its unsaved-changes guard before leaving a review. Repeated “runs locally on your computer” and workspace-mode copy was removed from navigation, sign-in and footers.

The [backend verification](github-sync-timeout-backend-2026-10-18.md) describes the API, provider deadlines, source errors and tests. The session extension does not refresh a GitHub token or change OAuth scopes. Known provider expiry requires a fresh sign-in when it cannot be extended.

## Integration safety

Countdowns retain their original client receipt timestamp when switching workspaces. Focus/visibility checks reconcile another tab's extension or account change. A changed numeric account clears the previous workspace/editor and remounts Ground Truth. Session/request generations and mounted-state checks reject stale responses, preventing a delayed identity check from undoing sign-out. Review acknowledgements, drafts, source bindings and human-confirmation requirements remain intact.

Actual test-screen captures: [session warning](../design/workspace-refinement/session-recovery/session-warning.png), [Sync recovery](../design/workspace-refinement/session-recovery/sync-timeout.png). These use disposable identities, not the user's connected account.

## Fixture-port incident and correction

The original main-app Playwright configuration used ports 3000/8000. During the validation run, the real app was briefly stopped and the fixture entrypoint occupied those ports. The user visited the normal app URL and saw `@phase09-fixture`. This was a test-process routing mistake; it was not a conversion of the user's real GitHub account or replacement of the production database.

The fixture services were stopped and the real app restored. Read-only checks verified HTTP 200 for the real frontend/API, a 302 OAuth redirect to GitHub's authorization endpoint with a non-fixture client, and 404 for the test-only login route. The user was asked to refresh and sign in again because the fixture cookie is not a valid session in the real backend.

Main browser tests now use **3016/8016**, a separate `.next-main-test` build directory and an explicit test origin. Their proxy chooses a fixed test loopback port only in test mode; request content cannot choose the upstream. The fixture entrypoint refuses requests when bound to normal app ports 3000/8000. Ground Truth tests retain their isolated 3015/8015 services. Future main-app tests can run while the real app remains available.

## Verification

- Backend: 179 demo/auth/session/GitHub regression cases passed, then twelve focused Sync/recovery checks after the additive interruption metadata change.
- Six additional fixture-port protection checks passed for both main and corpus fixture entrypoints; Ruff and formatting passed for the added isolation tests/server guards.
- Frontend: all **22 main-suite checks passed on isolated ports 3016/8016**. All **10 corpus-suite checks passed**, with the two session/countdown cases repeated successfully after the final startup lifecycle correction. The suites include small transport/palette utility checks as well as browser journeys. The earlier nonisolated main run was interrupted and is not claimed as passing.
- ESLint and standalone TypeScript passed. The production build passed for the integrated session UI; the running real app was restored from that verified build. Subsequent test-isolation wiring was exercised on separate test build directories while the real app stayed running.

## Preservation

All 548 protected corpus/pilot/readiness artifact hashes match the fresh baseline. The API-budget database is unchanged. The real application has three human confirmations, all outside the thirty-repository pilot. Two existed at this task's baseline; the third was saved by the user during the task. A read-only reconstruction excluding only that new revision-one review and its control-version increment exactly matches the baseline workspace-table hash. The saved review is retained; no rollback was performed.

Automated mutations use disposable databases. No app taxonomy/classification provider call, cloud deployment, OAuth scope change, dependency installation or budget reset was performed. The publication figures used the built-in image-generation tool separately, as documented in that package's prompt manifest. Previous corpus, pilot, benchmarks, articles and illustrations remain preserved.

## Final availability

The real application is running at `http://127.0.0.1:3000` with its existing `--live-ai` launch mode. Frontend and backend health returned HTTP 200. Sign-in redirects to `github.com/login/oauth/authorize` using the configured non-fixture client; the real backend returns 404 for the test-only login route. A browser that visited the temporary fixture service needs a refresh and a fresh GitHub sign-in. The publication package requested during this task is complete under `eval/ai-system-design/ground-truth-creation/`, including the living article, three illustrated figures and dated statistics/update instructions.
