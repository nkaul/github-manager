# ADR 0001 — OAuth App and Phase 0 evidence

Date: October 11, 2026. Status: accepted by explicit user instruction.

## Decision

Use a **GitHub OAuth App** as the selected connector. The user approved Phase 0 implementation, selected OAuth App to use the signed-in user's access without installation configuration, required Markdown pre-testing reports, and requested optional browser sign-in followed by access confirmation. Use AWS profile `default` and Region `us-east-1`.

This supersedes D01's proposed GitHub App/OAuth App comparison and preference for GitHub App. Do not implement a GitHub App or require installation tests during Phase 0. Keep the small adapter interface so future changes remain possible if explicitly approved.

## Consequences

- User authorization supplies identity and delegated access. OAuth scopes, organization third-party application policies, SSO and API coverage can still restrict results; test these rather than assuming the user's browser access guarantees every API source.
- The OAuth `repo` scope includes write privileges. Phase 0 implements only repository read calls; GraphQL POST is a fixed read query. No repository mutation or automatic scope escalation.
- Local FastAPI owns token exchange, PKCE and tokens in bounded expiring memory. Next.js proxies a fixed backend and exposes only an opaque HttpOnly session cookie. This local exception does not satisfy production encryption, durable sessions, refresh or disconnect requirements.
- Next.js uses a catch-all route proxy instead of a generic rewrite so upstream connection failures return a sanitized error without logging callback URLs containing authorization codes. Incoming callback request logging and browser console forwarding are suppressed.
- Explicit backend settings reject nonlocal operation. No hosted Site, IAM modification, production deployment, AI pipeline or durable app data is introduced. A subsequent user instruction authorized the eight isolated Phase 0 AWS scratch targets; all passed creation and access tests, and the user requested retaining them for further testing. This does not select production IaC or hosting.
- Sanitized Markdown summaries live under `docs/validation/`. Live per-session GitHub reports default to ignored `docs/validation/private/`, retain the signed-in GitHub login and numeric ID for access confirmation, omit repo names and token/content values, and use file mode 600. Named fixtures and AWS targets are ignored local manifests.
- Browser sign-in is user driven. A connected browser can be inspected to confirm identity and source coverage; absent browser tooling, the user signs in locally and saves a report for review. Do not reuse browser credentials or export GitHub tokens.
- AWS STS, resource inspection, approved scratch canaries, provisioning and future runtime-role permissions are distinct evidence. Missing named targets remain blocked; Phase 0 approval does not silently authorize resource creation.
- A live cross-check found 78 organization repositories omitted by `/user/repos` affiliation alone. Add paginated member-organization repository listings to ORG_GENERAL discovery; keep the approved My Repos eligibility rule unchanged. Named private metadata/Contents/README and two organization cross-checks subsequently passed. Independent direct/SSO/watch expectations remain open.

## Approval boundary

Only Phase 0 is approved. Its code can be delivered while external checks remain blocked, but the phase's live acceptance stays open until reports and dependencies are reviewed. Phase 1 requires separate approval.

References: [OAuth registration](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app), [authorization/PKCE/expiry](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps), [scopes](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps), [Phase 0 plan](../planning/phase-0-pretesting.md).
