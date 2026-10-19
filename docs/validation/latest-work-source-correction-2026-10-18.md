# Latest Work source correction — 2026-10-18

## Confirmed cause

Both `nkaul/github-manager` and `nkaul/github-manager-demo` were already discovered in the saved authenticated inventory as Owner + Contributor. The demo repository had no saved personal activity, while the app repository had commits and pull requests. The previous Latest Work implementation read only GitHub's GraphQL contribution collection; it did not read actor-attributed push events. Thus the demo repository failed the activity-date filter even though discovery and the 14-day window were correct.

## Live public verification

A read-only, unauthenticated call to the account's public Events API confirmed the account's own push events. No OAuth token, private repository content, credentials or full event payload was saved. The implemented event parser was exercised against these real responses. The existing production workspace was loaded with SQLite `mode=ro`; observations were merged into an in-memory copy only. No saved application state or API spending ledger was changed.

| Repository | Public matching-actor push events | Latest observed push (UTC) | Included in corrected 14-day view |
|---|---:|---|---|
| `nkaul/github-manager` | 11 | 2026-10-14T03:07:19+00:00 | Yes |
| `nkaul/github-manager-demo` | 5 | 2026-10-14T02:34:26+00:00 | Yes |

Before the in-memory source union, the GitHub Manager name filter returned 1 repository; afterward it returned 2. Events traversal hit a configured cap: **no**. The public check does not establish private event availability or lifetime completeness. Only the two known GitHub Manager repositories were verified; a third expected repository has not been named.

A second read-only public check sampled the five latest commits on `nkaul/github-manager-demo`. All five returned no associated GitHub author or committer account (`author: null`, `committer: null`), while the corresponding push events identified the authenticated account's stable ID. This is consistent with the absent account-attributed commit contributions: pushing a commit and being its associated author are different facts. We did not inspect or record author email addresses, and this five-commit sample does not prove the attribution of every historical commit. The application now correctly recognizes the user's own push as personal work independently of commit-author association.

## Implemented correction

- Keep the 90-day GraphQL contribution source and add the authenticated user's event stream, independently. A denied source does not erase successful observations from another source.
- Require the event actor's stable GitHub ID to match the authenticated account. Accept pushes, PR/issue actions and review/comment work. Stars, watches, forks and another actor's pushes do not count. Repository `pushed_at` never establishes personal work.
- Construct pagination URLs locally; traverse at most three 100-event pages. Preserve completed-page observations if a later page fails and mark coverage Partial. Display bounded source coverage and last sync time.
- Merge and deduplicate observed activity, retaining verified account observations for up to 90 days, instead of replacing old history with the shorter event response.
- Activity-only unknown repository IDs require successful current metadata access, matching stable ID and a trusted GitHub URL. At most 20 such new metadata resolutions occur per sync. Inaccessible repositories are not added.

## Limits and expected user action

GitHub's event stream supplies at most 300 events from the past 30 days and can lag by up to six hours. Contribution-graph commit eligibility and indexing differ from push activity. Local-only, unpushed edits are not GitHub events. A 90-day UI window retains previously observed evidence but cannot recover unobserved historical pushes beyond the upstream event window. This local phase has no webhook-based instant refresh.

After the updated app restarts, **Sync GitHub** refreshes the authenticated sources. This investigation did not replay public diagnostic data into the saved workspace or trigger AI analysis. No new OpenAI calls are needed.

## Validation

- 13 new focused regression cases passed: source union, actor rejection, independent source failures, source caps, safe pagination, retention/deduplication, metadata/access validation, bounded discovery, confirmed-contributor eligibility, sync integration, and 14/30/90-day filtering.
- Ruff format/check passed for changed Python files.
- Full backend demo and GitHub adapter regression suite: **148 passed** in 40.77 seconds before the final query-argument correction below. After that correction, all **13 focused activity regressions** and Ruff format/check passed again. All test state was isolated from the production workspace.
- Final official-schema review preserved the original GraphQL connection arguments (`contributions(first:100)`): commit ordering uses `CommitContributionOrder`, while issue/PR/review ordering uses `ContributionOrder`, which accepts direction only. An unnecessary uniform ordering argument was removed before finalization. The actor-event correction does not depend on changing contribution ordering.

## Official references

- [GitHub Events API](https://docs.github.com/en/rest/activity/events): authenticated user private visibility, 30-day/300-event bound, pagination and latency.
- [GitHub event types](https://docs.github.com/en/rest/using-the-rest-api/github-event-types): actor attribution and PushEvent semantics.
- [GraphQL contributions collection](https://docs.github.com/en/graphql/reference/users#contributionscollection): grouped contribution source and scope restrictions.
- [Troubleshooting missing contributions](https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/troubleshooting-missing-contributions): commit-author association and contribution eligibility.
- [ContributionOrder input](https://docs.github.com/en/graphql/reference/users#contributionorder) and [CommitContributionsByRepository](https://docs.github.com/en/graphql/reference/commits#commitcontributionsbyrepository): contribution connection argument compatibility.

The design already required attributable pushes in Latest Work (`docs/system-design.md`, section 4.4); this correction closes an implementation gap rather than changing its semantics.
