import asyncio
import json
from urllib.parse import parse_qs

import httpx
import pytest

from app.config import Settings
from app.github.client import GitHubError, OAuthAppAdapter
from app.pretest.github_probe import fixture_checks


def repo(ident):
    return {
        "id": ident,
        "name": f"repo-{ident}",
        "full_name": f"org/repo-{ident}",
        "html_url": f"https://github.com/org/repo-{ident}",
        "private": ident == 1,
    }


def test_source_union_pagination_partial_and_org_policy():
    requests = []

    def handle(request):
        requests.append(request)
        assert request.headers["authorization"] == "Bearer fixture"
        path, params = request.url.path, dict(request.url.params)
        if path == "/user":
            value = {"id": 42, "login": "fixture"}
        elif path == "/graphql":
            value = {
                "data": {
                    "viewer": {
                        "repositoriesContributedTo": {
                            "nodes": [],
                            "pageInfo": {"hasNextPage": False},
                        }
                    }
                }
            }
        elif path == "/user/teams":
            return httpx.Response(403, headers={"x-github-sso": "required; private-url"})
        elif path == "/user/orgs":
            value = []
        elif path == "/user/repos":
            affiliation = params["affiliation"]
            if affiliation == "owner" and params["page"] == "1":
                return httpx.Response(
                    200,
                    json=[repo(1)],
                    headers={"Link": '<https://api.github.com/user/repos?page=2>; rel="next"'},
                )
            value = (
                [repo(2)]
                if affiliation == "owner"
                else [repo(3)]
                if affiliation == "collaborator"
                else [repo(4)]
            )
        elif path == "/user/starred":
            value = [repo(1), repo(5), {**repo(99), "html_url": "https://evil.example/repo"}]
        elif path == "/user/subscriptions":
            return httpx.Response(429, json={"message": "fixture secret should be discarded"})
        else:
            raise AssertionError(path)
        return httpx.Response(200, json=value)

    adapter = OAuthAppAdapter(Settings(_env_file=None), httpx.MockTransport(handle), page_size=1)
    value = asyncio.run(adapter.inventory("fixture"))
    by_id = {r["id"]: r for r in value["repos"]}
    assert set(by_id) == {1, 2, 3, 4, 5}
    assert set(by_id[1]["sources"]) == {"OWNER", "STAR"}
    assert by_id[1]["eligible"] and by_id[1]["favorite"]
    assert by_id[3]["eligible"]
    assert not by_id[4]["eligible"] and not by_id[4]["favorite"]
    assert by_id[5]["favorite"] and not by_id[5]["eligible"]
    coverage = {r["source"]: r for r in value["coverage"]}
    assert coverage["WATCH"]["status"] == "UNAVAILABLE" and coverage["WATCH"]["count"] is None
    assert coverage["TEAM"]["status"] == "UNAVAILABLE"
    assert "SSO" in coverage["TEAM_MEMBERSHIP"]["note"]
    assert "private-url" not in json.dumps(value)
    assert all(request.method == "GET" or request.url.path == "/graphql" for request in requests)


@pytest.mark.parametrize(
    "status,category",
    [
        (401, "reauthorization_required"),
        (403, "permission_or_policy_denied"),
        (404, "not_found_or_hidden"),
        (429, "rate_limited"),
        (500, "upstream_error"),
    ],
)
def test_errors_are_sanitized(status, category):
    adapter = OAuthAppAdapter(
        Settings(_env_file=None),
        httpx.MockTransport(lambda _: httpx.Response(status, json={"secret": "never-leak"})),
    )
    with pytest.raises(GitHubError, match=category) as exc:
        asyncio.run(adapter.identity("fixture"))
    assert "never-leak" not in str(exc.value)


def test_timeout_redirect_and_untrusted_link():
    def timeout(request):
        raise httpx.ReadTimeout("fixture secret", request=request)

    adapter = OAuthAppAdapter(Settings(_env_file=None), httpx.MockTransport(timeout))
    with pytest.raises(GitHubError, match="network_or_timeout"):
        asyncio.run(adapter.identity("fixture"))
    adapter.transport = httpx.MockTransport(
        lambda _: httpx.Response(
            200,
            json=[repo(1)],
            headers={"Link": '<https://evil.example/user/repos?page=2>; rel="next"'},
        )
    )
    with pytest.raises(GitHubError, match="untrusted_pagination_link"):
        asyncio.run(adapter.pages("fixture", "/user/repos"))
    adapter.transport = httpx.MockTransport(
        lambda _: httpx.Response(302, headers={"Location": "https://evil.example"})
    )
    with pytest.raises(GitHubError, match="upstream_error"):
        asyncio.run(adapter.identity("fixture"))


def test_page_cap_and_graphql_errors():
    adapter = OAuthAppAdapter(
        Settings(_env_file=None),
        httpx.MockTransport(
            lambda _: httpx.Response(
                200,
                json=[repo(1)],
                headers={"Link": '<https://api.github.com/user/starred?page=2>; rel="next"'},
            )
        ),
        max_pages=1,
    )
    rows, capped = asyncio.run(adapter.pages("fixture", "/user/starred"))
    assert len(rows) == 1 and capped
    adapter.transport = httpx.MockTransport(
        lambda _: httpx.Response(200, json={"errors": [{"message": "private diagnostic"}]})
    )
    with pytest.raises(GitHubError, match="graphql_partial_or_denied"):
        asyncio.run(adapter.contributions("fixture"))


def test_token_exchange_pkce_and_expiry():
    def handle(request):
        assert request.url.host == "github.com" and request.method == "POST"
        params = parse_qs(request.content.decode())
        assert params["code_verifier"] == ["verifier"]
        assert params["redirect_uri"] == ["http://127.0.0.1:3000/api/v1/auth/github/callback"]
        return httpx.Response(
            200,
            json={
                "access_token": "fixture",
                "refresh_token": "discard",
                "expires_in": 99,
                "scope": "repo",
            },
        )

    adapter = OAuthAppAdapter(Settings(_env_file=None), httpx.MockTransport(handle))
    assert asyncio.run(adapter.exchange("code", "verifier")) == {
        "access_token": "fixture",
        "expires_in": 99,
        "scope": "repo",
    }


def test_known_fixtures_and_readme_body_not_reported(tmp_path):
    path = tmp_path / "fixtures.json"
    path.write_text(
        json.dumps(
            {
                "repositories": [
                    {
                        "alias": "owned",
                        "repo_id": 1,
                        "expected_sources": ["OWNER"],
                        "eligible": True,
                        "readme_present": True,
                    }
                ]
            }
        )
    )
    snapshot = {
        "repos": [{**repo(1), "sources": ["OWNER"], "eligible": True, "favorite": False}],
        "identity": {"id": 42, "login": "fixture"},
    }
    adapter = OAuthAppAdapter(
        Settings(_env_file=None),
        httpx.MockTransport(
            lambda _: httpx.Response(200, json={"content": "PRIVATE README CONTENT"})
        ),
    )
    rows = asyncio.run(fixture_checks(path, snapshot, adapter, "fixture"))
    assert all(row["status"] == "PASS" for row in rows)
    assert "PRIVATE README CONTENT" not in json.dumps(rows)
    snapshot["repos"][0]["eligible"] = False
    assert asyncio.run(fixture_checks(path, snapshot, adapter, "fixture"))[0]["status"] == "FAIL"


def test_named_private_fixture_detects_metadata_access_but_missing_discovery(tmp_path):
    path = tmp_path / "fixtures.json"
    path.write_text(
        json.dumps(
            {
                "repositories": [
                    {
                        "alias": "private-known",
                        "full_name": "org/repo-1",
                        "repo_id": 1,
                        "eligible": True,
                        "private": True,
                    }
                ]
            }
        )
    )
    adapter = OAuthAppAdapter(
        Settings(_env_file=None),
        httpx.MockTransport(lambda request: httpx.Response(200, json=repo(1))),
    )
    rows = asyncio.run(
        fixture_checks(path, {"repos": [], "identity": {"id": 42}}, adapter, "fixture")
    )
    assert [row["status"] for row in rows] == ["PASS", "FAIL"]
    assert "org/repo-1" not in json.dumps(rows)


def test_private_contents_sample_and_organization_completeness_gap(tmp_path):
    path = tmp_path / "fixtures.json"
    path.write_text(
        json.dumps(
            {"repositories": [], "sample_private_repositories": 1, "sample_member_organizations": 1}
        )
    )

    def handle(request):
        path = request.url.path
        if path == "/repos/org/repo-1":
            value = repo(1)
        elif path.endswith("/contents"):
            value = [{"name": "PRIVATE_FILENAME"}]
        elif path.endswith("/readme"):
            value = {"content": "PRIVATE_CONTENT"}
        elif path == "/user/orgs":
            value = [{"login": "org"}]
        elif path == "/user/memberships/orgs/org":
            value = {"state": "active"}
        elif path == "/orgs/org/repos":
            value = [repo(1), repo(2)]
        else:
            raise AssertionError(path)
        return httpx.Response(200, json=value)

    snapshot = {
        "repos": [{**repo(1), "sources": ["TEAM"], "eligible": True, "favorite": False}],
        "identity": {"id": 42, "login": "fixture"},
    }
    adapter = OAuthAppAdapter(Settings(_env_file=None), httpx.MockTransport(handle))
    rows = asyncio.run(fixture_checks(path, snapshot, adapter, "fixture"))
    by_check = {row["check"]: row for row in rows}
    assert by_check["private-sample-1/contents"]["status"] == "PASS"
    assert by_check["private-sample-1/readme"]["status"] == "PASS"
    assert by_check["organization-sample-1/discovery-cross-check"]["status"] == "FAIL"
    assert by_check["organization-sample-1/expected-repositories"]["status"] == "NOT_TESTED"
    assert "PRIVATE_CONTENT" not in json.dumps(rows) and "PRIVATE_FILENAME" not in json.dumps(rows)


def test_named_fixture_policy_denial_is_sanitized(tmp_path):
    path = tmp_path / "fixtures.json"
    path.write_text(
        json.dumps(
            {"repositories": [{"alias": "known", "full_name": "org/private", "eligible": True}]}
        )
    )
    adapter = OAuthAppAdapter(
        Settings(_env_file=None),
        httpx.MockTransport(
            lambda request: httpx.Response(
                403,
                json={"message": "PRIVATE_ORG_POLICY"},
                headers={"x-github-sso": "required; PRIVATE_SSO_URL"},
            )
        ),
    )
    rows = asyncio.run(fixture_checks(path, {"repos": []}, adapter, "fixture"))
    assert rows[0]["status"] == "FAIL" and "SSO" in rows[0]["detail"]
    assert "PRIVATE_" not in json.dumps(rows)


def test_organization_listing_fills_affiliation_gap_without_my_repos_inclusion():
    def handle(request):
        path = request.url.path
        if path == "/user":
            value = {"id": 42, "login": "fixture"}
        elif path == "/graphql":
            value = {
                "data": {
                    "viewer": {
                        "repositoriesContributedTo": {
                            "nodes": [],
                            "pageInfo": {"hasNextPage": False},
                        }
                    }
                }
            }
        elif path == "/user/orgs":
            value = [{"login": "org"}]
        elif path == "/orgs/org/repos":
            value = [repo(7)]
        else:
            value = []
        return httpx.Response(200, json=value)

    adapter = OAuthAppAdapter(Settings(_env_file=None), httpx.MockTransport(handle))
    value = asyncio.run(adapter.inventory("fixture"))
    assert len(value["repos"]) == 1
    assert value["repos"][0]["sources"] == ["ORG_GENERAL"]
    assert not value["repos"][0]["eligible"] and not value["repos"][0]["favorite"]
    coverage = {row["source"]: row for row in value["coverage"]}
    assert coverage["ORG_GENERAL"]["count"] == 1
    assert coverage["ORG_GENERAL"]["status"] == "OBSERVED"


@pytest.mark.parametrize("denied", ["/user/repos", "/orgs/org/repos", "/orgs/org/teams/dev/repos"])
def test_revoked_grant_is_not_misreported_as_a_partial_inventory(denied):
    def handle(request):
        path = request.url.path
        if path == denied:
            return httpx.Response(401, json={"message": "PRIVATE_PROVIDER_DIAGNOSTIC"})
        if path == "/user":
            value = {"id": 42, "login": "fixture"}
        elif path == "/graphql":
            value = {
                "data": {
                    "viewer": {
                        "repositoriesContributedTo": {
                            "nodes": [],
                            "pageInfo": {"hasNextPage": False},
                        }
                    }
                }
            }
        elif path == "/user/orgs":
            value = [{"login": "org"}]
        elif path == "/user/teams":
            value = [{"organization": {"login": "org"}, "slug": "dev"}]
        else:
            value = []
        return httpx.Response(200, json=value)

    adapter = OAuthAppAdapter(Settings(_env_file=None), httpx.MockTransport(handle))
    with pytest.raises(GitHubError, match="reauthorization_required") as error:
        asyncio.run(adapter.inventory("fixture"))
    assert error.value.status == 401 and "PRIVATE_PROVIDER" not in str(error.value)
