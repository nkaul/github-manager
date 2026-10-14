"""Actor-scoped, bounded contribution-date observations; never substitutes pushed_at."""

from datetime import UTC, datetime, timedelta


async def fetch_activity(adapter, token, user_id):
    start = (datetime.now(UTC) - timedelta(days=90)).isoformat()
    query = """query($from:DateTime!,$to:DateTime!) { viewer { databaseId
      contributionsCollection(from:$from,to:$to) {
        commitContributionsByRepository(maxRepositories:100) { repository {databaseId}
          contributions(first:100) {nodes {occurredAt} pageInfo {hasNextPage}} }
        issueContributionsByRepository(maxRepositories:100) { repository {databaseId}
          contributions(first:100) {nodes {occurredAt} pageInfo {hasNextPage}} }
        pullRequestContributionsByRepository(maxRepositories:100) { repository {databaseId}
          contributions(first:100) {nodes {occurredAt} pageInfo {hasNextPage}} }
        pullRequestReviewContributionsByRepository(maxRepositories:100) { repository {databaseId}
          contributions(first:100) {nodes {occurredAt} pageInfo {hasNextPage}} }
      } } }"""
    data, _ = await adapter.request(
        token,
        "/graphql",
        data={"query": query, "variables": {"from": start, "to": datetime.now(UTC).isoformat()}},
    )
    if data.get("errors") or data.get("data", {}).get("viewer", {}).get("databaseId") != user_id:
        raise ValueError("Contribution identity or query coverage unavailable")
    collection = data["data"]["viewer"]["contributionsCollection"]
    result = {}
    partial = False
    for field, kind in [
        ("commitContributionsByRepository", "COMMIT"),
        ("issueContributionsByRepository", "ISSUE"),
        ("pullRequestContributionsByRepository", "PULL_REQUEST"),
        ("pullRequestReviewContributionsByRepository", "REVIEW"),
    ]:
        groups = collection.get(field, [])
        partial |= len(groups) >= 100
        for group in groups:
            key = "github.com#" + str(group["repository"]["databaseId"])
            values = group["contributions"]
            partial |= values["pageInfo"]["hasNextPage"]
            for item in values["nodes"]:
                at = datetime.fromisoformat(item["occurredAt"].replace("Z", "+00:00"))
                result.setdefault(key, []).append(
                    {"actor_id": user_id, "at": at.isoformat(), "kind": kind}
                )
    return result, [
        {
            "source": "GITHUB_CONTRIBUTIONS",
            "status": "PARTIAL" if partial else "OBSERVED",
            "note": "90-day bounded contributions; no lifetime or push completeness guarantee",
        }
    ]
