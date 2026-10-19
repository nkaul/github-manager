import asyncio
import base64
import hashlib
import re
from urllib.parse import urlencode, urlsplit

import httpx

from app.config import Settings


class GitHubError(Exception):
    def __init__(self, category: str, status: int = 502, sso: bool = False):
        self.category, self.status, self.sso = category, status, sso
        super().__init__(category)


class OAuthAppAdapter:
    """Fixed GitHub.com endpoints; the only POSTs are token exchange and read-only GraphQL."""

    def __init__(self, settings: Settings, transport=None, page_size=100, max_pages=30):
        self.settings = settings
        self.transport = transport
        self.page_size, self.max_pages = page_size, max_pages

    def authorization_url(self, state: str, verifier: str) -> str:
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        return "https://github.com/login/oauth/authorize?" + urlencode(
            {
                "client_id": self.settings.github_client_id,
                "redirect_uri": self.settings.callback_url,
                "scope": self.settings.github_scopes,
                "state": state,
                "code_challenge": challenge.decode().rstrip("="),
                "code_challenge_method": "S256",
                "allow_signup": "false",
            }
        )

    async def request(self, token, path, *, data=None, params=None):
        if not path.startswith("/") or path.startswith("//") or ".." in path:
            raise GitHubError("invalid_endpoint")
        url = "https://api.github.com" + path
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": self.settings.github_api_version,
        }
        try:
            async with httpx.AsyncClient(
                timeout=20, transport=self.transport, follow_redirects=False
            ) as client:
                response = await client.request(
                    "POST" if data else "GET", url, headers=headers, json=data, params=params
                )
        except httpx.RequestError:
            raise GitHubError("network_or_timeout") from None
        if response.status_code != 200:
            status = response.status_code
            category = {
                401: "reauthorization_required",
                403: "permission_or_policy_denied",
                404: "not_found_or_hidden",
                429: "rate_limited",
            }.get(status, "upstream_error")
            if response.headers.get("x-ratelimit-remaining") == "0":
                category = "rate_limited"
            raise GitHubError(category, status, "x-github-sso" in response.headers)
        try:
            return response.json(), response
        except ValueError:
            raise GitHubError("invalid_response") from None

    async def exchange(self, code: str, verifier: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=20, transport=self.transport) as client:
                response = await client.post(
                    "https://github.com/login/oauth/access_token",
                    headers={"Accept": "application/json"},
                    data={
                        "client_id": self.settings.github_client_id,
                        "client_secret": self.settings.github_client_secret,
                        "code": code,
                        "code_verifier": verifier,
                        "redirect_uri": self.settings.callback_url,
                    },
                )
                value = response.json()
        except (httpx.RequestError, ValueError):
            raise GitHubError("token_exchange_failed") from None
        if (
            response.status_code != 200
            or not isinstance(value, dict)
            or not isinstance(value.get("access_token"), str)
            or not value["access_token"]
        ):
            raise GitHubError("token_exchange_failed")
        # Refresh tokens are intentionally discarded in this local phase.
        return {k: value[k] for k in ("access_token", "scope", "expires_in") if k in value}

    async def identity(self, token: str) -> dict:
        value, _ = await self.request(token, "/user")
        if (
            not isinstance(value, dict)
            or not isinstance(value.get("id"), int)
            or not isinstance(value.get("login"), str)
        ):
            raise GitHubError("invalid_identity")
        return {"id": value["id"], "login": value["login"], "name": value.get("name")}

    async def pages(self, token, path, **params):
        items = []
        for page in range(1, self.max_pages + 1):
            value, response = await self.request(
                token, path, params={**params, "per_page": self.page_size, "page": page}
            )
            if not isinstance(value, list):
                raise GitHubError("invalid_response")
            items.extend(value)
            if not response.links.get("next"):
                return items, False
            # Never follow an untrusted Link URL with the user's token.
            link = urlsplit(response.links["next"]["url"])
            if link.scheme != "https" or link.netloc != "api.github.com" or link.path != path:
                raise GitHubError("untrusted_pagination_link")
        return items, True

    async def contributions(self, token):
        nodes, cursor = [], None
        query = """query($size:Int!, $cursor:String) {
          viewer { repositoriesContributedTo(first:$size, after:$cursor,
            contributionTypes:[COMMIT, ISSUE, PULL_REQUEST, REPOSITORY],
            includeUserRepositories:true) {
            nodes { databaseId name nameWithOwner url isPrivate primaryLanguage {name}
              defaultBranchRef {name} owner {login} }
            pageInfo {hasNextPage endCursor}
          } }
        }"""
        for _ in range(self.max_pages):
            value, _ = await self.request(
                token,
                "/graphql",
                data={"query": query, "variables": {"size": self.page_size, "cursor": cursor}},
            )
            if value.get("errors"):
                raise GitHubError("graphql_partial_or_denied")
            try:
                connection = value["data"]["viewer"]["repositoriesContributedTo"]
                for node in connection["nodes"]:
                    if node:
                        nodes.append(
                            {
                                "id": node["databaseId"],
                                "name": node["name"],
                                "full_name": node["nameWithOwner"],
                                "html_url": node["url"],
                                "private": node["isPrivate"],
                                "owner": node["owner"],
                                "language": (node.get("primaryLanguage") or {}).get("name"),
                                "default_branch": (node.get("defaultBranchRef") or {}).get("name"),
                            }
                        )
                info = connection["pageInfo"]
                if not info["hasNextPage"]:
                    return nodes, False
                next_cursor = info["endCursor"]
                if not next_cursor or next_cursor == cursor:
                    raise GitHubError("invalid_graphql_cursor")
                cursor = next_cursor
            except (KeyError, TypeError):
                raise GitHubError("invalid_response") from None
        return nodes, True

    async def inventory(self, token: str) -> dict:
        user = await self.identity(token)
        coverage, collected = [], {}

        async def source(name, call, note=""):
            try:
                rows, capped = await call
                collected[name] = rows
                coverage.append(
                    {
                        "source": name,
                        "status": "PARTIAL" if capped else "OBSERVED",
                        "count": len(rows),
                        "note": note or "API traversal completed; fixture comparison pending",
                    }
                )
            except GitHubError as exc:
                if exc.status == 401:
                    raise
                coverage.append(
                    {
                        "source": name,
                        "status": "UNAVAILABLE",
                        "count": None,
                        "note": exc.category + ("; SSO authorization required" if exc.sso else ""),
                    }
                )

        results = await asyncio.gather(
            source("OWNER", self.pages(token, "/user/repos", affiliation="owner")),
            source(
                "DIRECT",
                self.pages(token, "/user/repos", affiliation="collaborator"),
                "Collaborator API affiliation; confirm direct grant against known fixtures",
            ),
            source(
                "ORG_GENERAL", self.pages(token, "/user/repos", affiliation="organization_member")
            ),
            source("STAR", self.pages(token, "/user/starred")),
            source(
                "WATCH",
                self.pages(token, "/user/subscriptions"),
                "Authenticated endpoint observations; completeness requires known-watch fixtures",
            ),
            source(
                "CONTRIBUTOR",
                self.contributions(token),
                "GitHub contribution window; lifetime completeness is not claimed",
            ),
            source("TEAM_MEMBERSHIP", self.pages(token, "/user/teams")),
            source("ORG_MEMBERSHIP", self.pages(token, "/user/orgs")),
            return_exceptions=True,
        )
        for result in results:
            if isinstance(result, BaseException):
                raise result
        organizations = collected.pop("ORG_MEMBERSHIP", [])
        org_coverage = next(c for c in coverage if c["source"] == "ORG_GENERAL")
        membership_coverage = next(c for c in coverage if c["source"] == "ORG_MEMBERSHIP")
        org_rows = list(collected.get("ORG_GENERAL", []))
        org_partial = (
            org_coverage["status"] != "OBSERVED"
            or membership_coverage["status"] != "OBSERVED"
            or len(organizations) > 20
        )
        # /user/repos affiliation=organization_member omits some visible organization
        # repositories. Reconcile each membership listing without changing eligibility.
        for organization in organizations[:20]:
            login = organization.get("login", "")
            if not re.fullmatch(r"[A-Za-z0-9-]+", login):
                org_partial = True
                continue
            try:
                rows, capped = await self.pages(token, f"/orgs/{login}/repos", type="all")
                org_rows.extend(rows)
                org_partial |= capped
            except GitHubError as exc:
                if exc.status == 401:
                    raise
                org_partial = True
        collected["ORG_GENERAL"] = list(
            {row["id"]: row for row in org_rows if isinstance(row.get("id"), int)}.values()
        )
        org_coverage.update(
            status="PARTIAL" if org_partial else "OBSERVED",
            count=len(collected["ORG_GENERAL"]),
            note="Organization affiliation plus member-organization listings; "
            "visibility alone does not establish My Repos eligibility",
        )
        team_repos, team_partial, team_failed = [], False, False
        teams = collected.pop("TEAM_MEMBERSHIP", [])
        # Bounded to avoid an unexpectedly large organization consuming the whole quota.
        for team in teams[:20]:
            org, slug = (team.get("organization") or {}).get("login", ""), team.get("slug", "")
            if not re.fullmatch(r"[\w-]+", org) or not re.fullmatch(r"[\w-]+", slug):
                team_failed = True
                continue
            try:
                rows, capped = await self.pages(token, f"/orgs/{org}/teams/{slug}/repos")
                team_repos.extend(rows)
                team_partial |= capped
            except GitHubError as exc:
                if exc.status == 401:
                    raise
                team_failed = True
        collected["TEAM"] = team_repos
        membership = next(c for c in coverage if c["source"] == "TEAM_MEMBERSHIP")
        coverage.append(
            {
                "source": "TEAM",
                "count": len(team_repos),
                "status": "UNAVAILABLE"
                if membership["status"] == "UNAVAILABLE"
                else "PARTIAL"
                if team_failed
                or team_partial
                or len(teams) > 20
                or membership["status"] == "PARTIAL"
                else "OBSERVED",
                "note": "Current team repos, including inherited access; fixtures pending",
            }
        )
        repos = {}
        for name, rows in collected.items():
            for row in rows:
                ident, link = row.get("id"), row.get("html_url", "")
                parsed = urlsplit(link)
                if (
                    not isinstance(ident, int)
                    or parsed.scheme != "https"
                    or parsed.netloc != "github.com"
                    or parsed.username
                    or parsed.password
                ):
                    continue
                repo = repos.setdefault(
                    ident,
                    {
                        "id": ident,
                        "host": "github.com",
                        "name": row.get("name", ""),
                        "full_name": row.get("full_name", ""),
                        "html_url": link,
                        "private": bool(row.get("private")),
                        "language": row.get("language"),
                        "default_branch": row.get("default_branch"),
                        "branch_count": None,
                        "sources": [],
                    },
                )
                if name not in repo["sources"]:
                    repo["sources"].append(name)
        for repo in repos.values():
            repo["eligible"] = bool(
                set(repo["sources"]) & {"OWNER", "DIRECT", "TEAM", "CONTRIBUTOR"}
            )
            repo["favorite"] = bool(set(repo["sources"]) & {"STAR", "WATCH"})
        return {
            "identity": user,
            "repos": sorted(repos.values(), key=lambda r: r["full_name"].lower()),
            "coverage": sorted(coverage, key=lambda c: c["source"]),
        }
