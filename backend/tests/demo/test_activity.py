"""Regression checks for actor-attributed Latest Work source reconciliation."""

import asyncio
import copy
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import httpx
import pytest

from app.auth.sessions import SessionStore
from app.config import Settings
from app.demo.activity import discover_activity_repositories, fetch_activity, merge_activity
from app.demo.explorer import repositories
from app.demo.service import Service
from app.demo.store import Store, initial_state
from app.github.client import GitHubError, OAuthAppAdapter

ACTOR = 42
NOW = datetime.now(UTC)
RECENT = (NOW - timedelta(days=2)).isoformat()


def event(ident=10, *, actor=ACTOR, kind="PushEvent", at=RECENT, event_id="push-1"):
    return {
        "id": event_id,
        "actor": {"id": actor},
        "repo": {"id": ident},
        "type": kind,
        "created_at": at,
    }


def graph(groups=None, *, actor=ACTOR):
    return {
        "data": {
            "viewer": {
                "databaseId": actor,
                "contributionsCollection": {
                    "commitContributionsByRepository": groups or [],
                },
            }
        }
    }


def group(ident=10, *, at=RECENT, more=False):
    return {
        "repository": {"databaseId": ident},
        "contributions": {
            "nodes": [{"occurredAt": at}],
            "pageInfo": {"hasNextPage": more},
        },
    }


def repo(ident=10, *, private=False):
    return {
        "id": ident,
        "full_name": f"fixture/repo-{ident}",
        "html_url": f"https://github.com/fixture/repo-{ident}",
        "private": private,
        "sources": ["OWNER"],
        "eligible": True,
        "favorite": False,
    }


def adapter_for(handle):
    return OAuthAppAdapter(Settings(_env_file=None), httpx.MockTransport(handle))


def fetch(adapter):
    return asyncio.run(fetch_activity(adapter, "fixture", ACTOR, "fixture"))


def test_user_push_fills_contribution_graph_gap_and_filters_other_activity():
    calls = []

    def handle(request):
        calls.append(request)
        assert request.headers["authorization"] == "Bearer fixture"
        if request.url.path == "/graphql":
            return httpx.Response(200, json=graph([group(10)]))
        assert request.url.path == "/users/fixture/events"
        return httpx.Response(
            200,
            json=[
                {**event(11), "public": False},
                event(12, actor=99),
                event(13, kind="WatchEvent"),
                event(14, kind="ForkEvent"),
                event(15, kind="CreateEvent"),
                event(16, at=(NOW - timedelta(days=31)).isoformat()),
                event(17, at=(NOW + timedelta(days=1)).isoformat()),
            ],
        )

    activity, coverage = fetch(adapter_for(handle))
    assert set(activity) == {"github.com#10", "github.com#11"}
    assert activity["github.com#11"][0]["kind"] == "PUSH"
    assert [row["status"] for row in coverage] == ["OBSERVED", "OBSERVED"]
    assert [row["window_days"] for row in coverage] == [90, 30]
    assert len(calls) == 2


@pytest.mark.parametrize("failed", ["graphql", "events"])
def test_activity_sources_fail_independently_without_leaking_upstream_content(failed):
    def handle(request):
        graphql = request.url.path == "/graphql"
        if graphql == (failed == "graphql"):
            return httpx.Response(403, json={"message": "PRIVATE_ERROR_NEVER_PERSIST"})
        return httpx.Response(200, json=graph([group()]) if graphql else [event()])

    activity, coverage = fetch(adapter_for(handle))
    assert "github.com#10" in activity
    assert [row["status"] for row in coverage].count("UNAVAILABLE") == 1
    assert "PRIVATE_ERROR" not in str(coverage)


def test_graphql_wrong_actor_never_attributes_commits_but_events_require_matching_actor():
    adapter = adapter_for(
        lambda request: httpx.Response(
            200,
            json=graph([group()], actor=99)
            if request.url.path == "/graphql"
            else [event(10, actor=99), event(11)],
        )
    )
    activity, coverage = fetch(adapter)
    assert set(activity) == {"github.com#11"}
    assert coverage[0]["status"] == "UNAVAILABLE"


def test_event_pagination_is_bounded_marks_cap_and_never_follows_link_url():
    pages = []

    def handle(request):
        if request.url.path == "/graphql":
            return httpx.Response(200, json=graph())
        page = int(request.url.params["page"])
        pages.append(page)
        assert request.url.host == "api.github.com"
        return httpx.Response(
            200,
            json=[event(ident=page, event_id=str(page))],
            headers={
                "Link": '<https://evil.example/steal-token>; rel="next"',
            },
        )

    activity, coverage = fetch(adapter_for(handle))
    assert pages == [1, 2, 3]
    assert len(activity) == 3 and coverage[1]["status"] == "PARTIAL"


def test_later_event_page_failure_retains_first_page_observations():
    def handle(request):
        if request.url.path == "/graphql":
            return httpx.Response(200, json=graph())
        if request.url.params["page"] == "2":
            return httpx.Response(429)
        return httpx.Response(
            200,
            json=[event()],
            headers={
                "Link": '<https://api.github.com/users/fixture/events?page=2>; rel="next"',
            },
        )

    activity, coverage = fetch(adapter_for(handle))
    assert "github.com#10" in activity and coverage[1]["status"] == "PARTIAL"


def test_contribution_caps_are_explicit_and_original_query_is_preserved():
    def handle(request):
        if request.url.path == "/graphql":
            assert b"orderBy" not in request.content
            assert request.content.count(b"contributions(first:100)") == 4
            return httpx.Response(200, json=graph([group(more=True)]))
        return httpx.Response(200, json=[])

    _, coverage = fetch(adapter_for(handle))
    assert coverage[0]["status"] == "PARTIAL"


def test_merge_preserves_older_evidence_deduplicates_and_rejects_other_actor_or_bad_dates():
    previous = [
        {"actor_id": ACTOR, "at": (NOW - timedelta(days=45)).isoformat(), "kind": "COMMIT"},
        {"actor_id": ACTOR, "at": (NOW - timedelta(days=91)).isoformat(), "kind": "COMMIT"},
        {"actor_id": ACTOR, "at": "not-a-date", "kind": "COMMIT"},
        {"actor_id": ACTOR, "at": "2026-01-01T12:00:00", "kind": "COMMIT"},
        {"actor_id": 99, "at": RECENT, "kind": "PUSH"},
    ]
    observed = {
        "actor_id": ACTOR,
        "at": RECENT,
        "kind": "PUSH",
        "source": "GITHUB_EVENTS",
        "event_id": "1",
    }
    merged = merge_activity(previous, [observed, observed], ACTOR, now=NOW)
    assert len(merged) == 2 and merged[0]["kind"] == "PUSH"
    assert len(merge_activity(merged, [], ACTOR, now=NOW)) == 2


def test_event_only_repositories_require_current_metadata_identity_and_access():
    calls = []

    def handle(request):
        ident = int(request.url.path.split("/")[-1])
        calls.append(ident)
        if ident == 12:
            return httpx.Response(404, json={"message": "hidden"})
        value = repo(ident)
        if ident == 13:
            value["html_url"] = "https://evil.example/fixture/repo-13"
        return httpx.Response(200, json=value)

    snapshot = {"repos": [repo(10)], "coverage": []}
    observed = {f"github.com#{ident}": [{"at": RECENT}] for ident in [10, 11, 12, 13]}
    asyncio.run(discover_activity_repositories(adapter_for(handle), "fixture", snapshot, observed))
    assert calls == [11, 12, 13]
    assert {row["id"] for row in snapshot["repos"]} == {10, 11}
    assert snapshot["repos"][1]["sources"] == ["CONTRIBUTOR"]
    assert snapshot["coverage"][0]["status"] == "PARTIAL"


def test_actor_activity_makes_already_accessible_star_candidate_eligible_without_lookup():
    snapshot = {
        "repos": [{**repo(), "sources": ["STAR"], "eligible": False, "favorite": True}],
        "coverage": [],
    }
    observed = {"github.com#10": [{"at": RECENT}]}

    def handle(request):
        raise AssertionError("Already discovered repository must not need another metadata lookup")

    asyncio.run(discover_activity_repositories(adapter_for(handle), "fixture", snapshot, observed))
    assert snapshot["repos"][0]["sources"] == ["CONTRIBUTOR", "STAR"]
    assert snapshot["repos"][0]["eligible"] and snapshot["repos"][0]["favorite"]


def test_event_only_discovery_has_bounded_metadata_cost():
    snapshot = {"repos": [], "coverage": []}
    observed = {f"github.com#{ident}": [{"at": RECENT}] for ident in range(1, 23)}
    calls = []

    def handle(request):
        ident = int(request.url.path.split("/")[-1])
        calls.append(ident)
        return httpx.Response(200, json=repo(ident))

    asyncio.run(discover_activity_repositories(adapter_for(handle), "fixture", snapshot, observed))
    assert len(calls) == len(snapshot["repos"]) == 20
    assert snapshot["coverage"][0]["status"] == "PARTIAL"


def test_sync_merges_activity_and_latest_work_without_using_repository_pushes(tmp_path):
    class Adapter:
        async def inventory(self, token):
            return {
                "identity": {"id": ACTOR, "login": "fixture"},
                "repos": [repo(10), repo(11), repo(12)],
                "coverage": [],
            }

        async def request(self, token, path, **kwargs):
            if path == "/graphql":
                return graph([group(10)]), None
            return [event(11), event(12, actor=99)], SimpleNamespace(links={})

    store = Store(tmp_path / "state.sqlite3")
    sessions = SessionStore()
    sessions.create({"id": ACTOR, "login": "fixture"}, "fixture", ["repo"], 3600)
    service = Service(store, Adapter(), sessions)
    workspace = f"{ACTOR}:github"
    older = {"actor_id": ACTOR, "at": (NOW - timedelta(days=45)).isoformat(), "kind": "COMMIT"}
    store.mutate(
        workspace,
        lambda state: state["core"]["repos"].update(
            {
                "github.com#11": {**repo(11), "activities": [older]},
            }
        ),
    )
    assert asyncio.run(service.sync(workspace)) == 3
    state = store.read(workspace)
    assert len(state["core"]["repos"]["github.com#11"]["activities"]) == 2
    state["core"]["repos"]["github.com#12"]["pushed_at"] = RECENT
    latest = repositories(state, workspace, ACTOR, {"view": "latest", "days": 14})
    assert {row["id"] for row in latest} == {10, 11}
    assert state["core"]["activity_coverage"][1]["source"] == "GITHUB_EVENTS"


def test_latest_work_respects_window_and_all_observed_timestamps():
    state = initial_state()
    for ident, days in [(10, 2), (11, 20), (12, 45)]:
        state["core"]["repos"][f"github.com#{ident}"] = {
            **repo(ident),
            "key": f"github.com#{ident}",
            "name": f"fixture/repo-{ident}",
            "activities": [
                {"actor_id": ACTOR, "at": (NOW - timedelta(days=days)).isoformat(), "kind": "PUSH"}
            ],
        }
    before = copy.deepcopy(state)
    for days, expected in [(14, {10}), (30, {10, 11}), (90, {10, 11, 12})]:
        assert {
            r["id"]
            for r in repositories(state, "42:github", ACTOR, {"view": "latest", "days": days})
        } == expected
    assert state == before


@pytest.mark.parametrize("failed", ["graphql", "events", "later-events"])
def test_revoked_grant_propagates_instead_of_disappearing_into_activity_coverage(failed):
    def handle(request):
        path = request.url.path
        if (path == "/graphql" and failed == "graphql") or (
            path != "/graphql" and (failed == "events" or request.url.params.get("page") == "2")
        ):
            return httpx.Response(401, json={"message": "PRIVATE_DIAGNOSTIC"})
        if path == "/graphql":
            return httpx.Response(200, json=graph([group()]))
        return httpx.Response(
            200,
            json=[event()],
            headers={"Link": '<https://api.github.com/users/fixture/events?page=2>; rel="next"'},
        )

    with pytest.raises(GitHubError, match="reauthorization_required"):
        fetch(adapter_for(handle))


def test_activity_candidate_revocation_is_not_treated_as_missing_repository():
    snapshot = {"repos": [], "coverage": []}
    observed = {"github.com#10": [{"at": RECENT}]}
    adapter = adapter_for(lambda _: httpx.Response(401))
    with pytest.raises(GitHubError, match="reauthorization_required"):
        asyncio.run(discover_activity_repositories(adapter, "fixture", snapshot, observed))
    assert snapshot == {"repos": [], "coverage": []}
