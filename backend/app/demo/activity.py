"""Actor-scoped, bounded contribution and event observations; never uses pushed_at."""

import re
from datetime import UTC, datetime, timedelta
from urllib.parse import urlsplit

from app.github.client import GitHubError

HISTORY_DAYS = 90
EVENT_DAYS = 30
EVENT_LIMIT = 300
DISCOVERY_LIMIT = 20
EVENT_KINDS = {
    "PushEvent": "PUSH",
    "PullRequestEvent": "PULL_REQUEST",
    "PullRequestReviewEvent": "REVIEW",
    "PullRequestReviewCommentEvent": "REVIEW_COMMENT",
    "IssuesEvent": "ISSUE",
    "IssueCommentEvent": "ISSUE_COMMENT",
}


def timestamp(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.astimezone(UTC) if parsed.tzinfo else None
    except (AttributeError, TypeError, ValueError):
        return None


def merge_activity(previous, observed, user_id, *, now=None):
    """Retain actor evidence across shorter/failed refreshes, bounded to 90 days."""
    now = now or datetime.now(UTC)
    start = now - timedelta(days=HISTORY_DAYS)
    merged = {}
    for item in [*previous, *observed]:
        at = timestamp(item.get("at"))
        if item.get("actor_id") != user_id or at is None or not start <= at <= now:
            continue
        value = {**item, "at": at.isoformat()}
        # Event IDs preserve separate actions; old contribution records deduplicate by kind/date.
        key = (
            value.get("source", "GITHUB_CONTRIBUTIONS"),
            value.get("event_id"),
            value.get("kind"),
            value["at"],
        )
        merged[key] = value
    return sorted(merged.values(), key=lambda item: item["at"], reverse=True)


async def _contributions(adapter, token, user_id, now):
    start = (now - timedelta(days=HISTORY_DAYS)).isoformat()
    query = """query($from:DateTime!,$to:DateTime!) { viewer { databaseId
      contributionsCollection(from:$from,to:$to) {
        commitContributionsByRepository(maxRepositories:100) { repository {databaseId}
          contributions(first:100) {
            nodes {occurredAt} pageInfo {hasNextPage}} }
        issueContributionsByRepository(maxRepositories:100) { repository {databaseId}
          contributions(first:100) {
            nodes {occurredAt} pageInfo {hasNextPage}} }
        pullRequestContributionsByRepository(maxRepositories:100) { repository {databaseId}
          contributions(first:100) {
            nodes {occurredAt} pageInfo {hasNextPage}} }
        pullRequestReviewContributionsByRepository(maxRepositories:100) { repository {databaseId}
          contributions(first:100) {
            nodes {occurredAt} pageInfo {hasNextPage}} }
      } } }"""
    data, _ = await adapter.request(
        token,
        "/graphql",
        data={"query": query, "variables": {"from": start, "to": now.isoformat()}},
    )
    if data.get("errors") or data.get("data", {}).get("viewer", {}).get("databaseId") != user_id:
        raise ValueError("Contribution identity or query coverage unavailable")
    collection = data["data"]["viewer"]["contributionsCollection"]
    result, partial = {}, False
    for field, kind in [
        ("commitContributionsByRepository", "COMMIT"),
        ("issueContributionsByRepository", "ISSUE"),
        ("pullRequestContributionsByRepository", "PULL_REQUEST"),
        ("pullRequestReviewContributionsByRepository", "REVIEW"),
    ]:
        groups = collection.get(field, [])
        partial |= len(groups) >= 100
        for group in groups:
            ident = group["repository"]["databaseId"]
            if not isinstance(ident, int) or ident <= 0:
                partial = True
                continue
            key = "github.com#" + str(ident)
            values = group["contributions"]
            partial |= values["pageInfo"]["hasNextPage"]
            for item in values["nodes"]:
                at = timestamp(item["occurredAt"])
                if at is not None:
                    result.setdefault(key, []).append(
                        {
                            "actor_id": user_id,
                            "at": at.isoformat(),
                            "kind": kind,
                            "source": "GITHUB_CONTRIBUTIONS",
                        }
                    )
    return result, partial


async def _events(adapter, token, user_id, login, now):
    if not isinstance(login, str) or not re.fullmatch(r"[A-Za-z0-9-]+", login):
        raise ValueError("Activity identity unavailable")
    result, count, partial = {}, 0, False
    start = now - timedelta(days=EVENT_DAYS)
    # Construct each URL ourselves: never follow an upstream Link URL with the token.
    for page in range(1, 4):
        try:
            rows, response = await adapter.request(
                token, f"/users/{login}/events", params={"per_page": 100, "page": page}
            )
        except GitHubError as exc:
            if page == 1 or exc.status == 401:
                raise
            return result, True
        if not isinstance(rows, list):
            if page > 1:
                return result, True
            raise ValueError("Activity events unavailable")
        count += len(rows)
        for item in rows:
            if (item.get("actor") or {}).get("id") != user_id:
                continue
            kind = EVENT_KINDS.get(item.get("type"))
            ident = (item.get("repo") or {}).get("id")
            at = timestamp(item.get("created_at"))
            if not kind or not isinstance(ident, int) or ident <= 0 or at is None:
                continue
            if not start <= at <= now:
                continue
            result.setdefault("github.com#" + str(ident), []).append(
                {
                    "actor_id": user_id,
                    "at": at.isoformat(),
                    "kind": kind,
                    "source": "GITHUB_EVENTS",
                    "event_id": str(item["id"]),
                }
            )
        more = bool(response and response.links.get("next"))
        if not more:
            break
        if page == 3:
            partial = True
    return result, partial or count >= EVENT_LIMIT


async def fetch_activity(adapter, token, user_id, login=None):
    """Refresh independently so one denied/rate-limited source cannot hide the other."""
    now = datetime.now(UTC)
    result, coverage = {}, []
    for source, days, call, note in [
        (
            "GITHUB_CONTRIBUTIONS",
            HISTORY_DAYS,
            lambda: _contributions(adapter, token, user_id, now),
            "90-day contribution graph; commit eligibility and indexing can omit recent work",
        ),
        (
            "GITHUB_EVENTS",
            EVENT_DAYS,
            lambda: _events(adapter, token, user_id, login, now),
            "30-day actor-attributed events, at most 300; GitHub may delay events up to 6 hours",
        ),
    ]:
        try:
            observed, partial = await call()
            for key, values in observed.items():
                result[key] = merge_activity(result.get(key, []), values, user_id, now=now)
            status = "PARTIAL" if partial else "OBSERVED"
        except GitHubError as exc:
            if exc.status == 401:
                raise
            status = "UNAVAILABLE"
        except (ValueError, KeyError, TypeError, AttributeError):
            status = "UNAVAILABLE"
        coverage.append(
            {
                "source": source,
                "status": status,
                "window_days": days,
                "observed_at": now.isoformat(),
                "note": note,
            }
        )
    return result, coverage


async def discover_activity_repositories(adapter, token, snapshot, activity):
    """Resolve event-only candidates by stable ID and current accessible metadata."""
    for repo in snapshot["repos"]:
        if activity.get("github.com#" + str(repo["id"])):
            repo["sources"] = sorted(set(repo["sources"]) | {"CONTRIBUTOR"})
            repo["eligible"] = True
    known = {"github.com#" + str(repo["id"]) for repo in snapshot["repos"]}
    missing = sorted(
        (key for key, values in activity.items() if values and key not in known),
        key=lambda key: max(item["at"] for item in activity[key]),
        reverse=True,
    )
    if not missing:
        return
    found, partial = 0, len(missing) > DISCOVERY_LIMIT
    for key in missing[:DISCOVERY_LIMIT]:
        ident = int(key.split("#")[1])
        try:
            repo, _ = await adapter.request(token, f"/repositories/{ident}")
            link = urlsplit(repo.get("html_url", ""))
            name = repo.get("full_name", "")
            if (
                repo.get("id") != ident
                or not isinstance(repo.get("private"), bool)
                or not re.fullmatch(r"[A-Za-z0-9-]+/[A-Za-z0-9_.-]+", name)
                or link.scheme != "https"
                or link.netloc != "github.com"
                or link.path.rstrip("/").casefold() != ("/" + name).casefold()
            ):
                raise ValueError("Activity repository identity unavailable")
            snapshot["repos"].append(
                {
                    "id": ident,
                    "host": "github.com",
                    "full_name": name,
                    "html_url": repo["html_url"],
                    "private": repo["private"],
                    "language": repo.get("language"),
                    "default_branch": repo.get("default_branch"),
                    "branch_count": None,
                    "eligible": True,
                    "favorite": False,
                    "sources": ["CONTRIBUTOR"],
                }
            )
            found += 1
        except GitHubError as exc:
            if exc.status == 401:
                raise
            partial = True
        except (ValueError, KeyError, TypeError, AttributeError):
            partial = True
    snapshot["coverage"].append(
        {
            "source": "ACTIVITY_REPOSITORIES",
            "status": "PARTIAL" if partial else "OBSERVED",
            "count": found,
            "note": "Actor-attributed candidates verified with current repository metadata; "
            "at most 20 new repositories per sync",
        }
    )
