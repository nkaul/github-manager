import asyncio
import copy
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.auth.sessions import SessionStore
from app.demo import domain
from app.demo.ai import RequestAllowance
from app.demo.evidence import build_profile, model_allowed
from app.demo.store import Store
from app.local import LocalSettings, create_local_app
from app.pretest.ai.provider import ProviderBlocked
from app.pretest.ai.storage import Ledger
from tests.demo.fixtures import USER, Adapter, Provider, concept

W = str(USER["id"]) + ":samples"


@pytest.fixture
def rig(tmp_path):
    sessions = SessionStore()
    cookie = sessions.create(USER, "fixture-only", ["repo"], 3600)
    app = create_local_app(
        LocalSettings(demo_live_ai=True),
        adapter=Adapter(),
        sessions=sessions,
        db_path=tmp_path / "app.sqlite3",
        provider_factory=Provider,
    )
    client = TestClient(app, base_url="http://127.0.0.1:8000")
    client.cookies.set("gm_session", cookie)
    client.headers.update(
        {"Origin": "http://127.0.0.1:3000", "X-CSRF-Token": sessions.get(cookie).csrf_token}
    )
    return app, client, sessions


def post(client, path, value=None, collection="samples"):
    return client.post("/api/v1" + path, params={"collection": collection}, json=value)


def work(app, workspace=W):
    job = app.state.database.claim({workspace})
    assert job
    asyncio.run(app.state.service.perform(job))
    return app.state.database.read(workspace)["organization"]["runs"][job["id"]]


def seed(rig):
    app, client, _ = rig
    assert post(client, "/samples/load").status_code == 200
    return app, client


def published(rig):
    app, client = seed(rig)
    assert (
        post(client, "/organizer/reorganize", {"mode": "DISCOVER", "ai_mode": "LIVE"}).status_code
        == 202
    )
    assert work(app)["status"] == "COMPLETED"
    org = app.state.database.read(W)["organization"]
    draft = next(iter(org["drafts"].values()))
    values = [
        {k: p[k] for k in ("kind", "name", "description", "aliases")}
        | {"domain": p["parent_domain"]}
        for p in draft["proposals"]
    ]
    response = post(
        client,
        "/taxonomy/drafts/publish",
        {"draft_id": draft["id"], "proposals": values, "expected_revision": 0},
    )
    assert response.status_code == 200, response.text
    return app, client, response.json()["concepts"]


def test_owner_auth_csrf_and_sample_isolation(rig):
    app, client, sessions = rig
    seed(rig)
    assert client.get("/api/v1/repos?view=all&collection=github").json()["total"] == 0
    assert client.get("/api/v1/repos?view=my&collection=samples").json()["total"] == 0
    assert client.get("/api/v1/repos?view=favorites&collection=samples").json()["total"] == 0
    client.headers["X-CSRF-Token"] = "wrong"
    assert post(client, "/samples/load").status_code == 403
    other = sessions.create({"id": 88, "login": "other"}, "other", ["repo"], 3600)
    client.cookies.set("gm_session", other)
    assert client.get("/api/v1/repos?view=all&collection=samples").json()["total"] == 0
    assert (
        client.get("/api/v1/repos/detail?key=synthetic/orion-api&collection=samples").status_code
        == 404
    )
    client.cookies.clear()
    assert client.get("/api/v1/workspace").status_code == 401


def test_alias_transaction_and_stable_rename(tmp_path):
    store = Store(tmp_path / "state.db")
    c = concept(store, W, "TOPIC", "Web APIs", aliases=["HTTP services"])
    store.mutate(W, lambda s: domain.edit_concept(s, c["id"], {"name": "API Design"}))
    assert store.read(W)["organization"]["concepts"][c["id"]]["name"] == "API Design"
    before = store.read(W)
    with pytest.raises(ValueError):
        concept(store, W, "TOPIC", "http-services")
    assert store.read(W) == before

    def create(_):
        try:
            return concept(store, W, "TAG", "Python")["id"]
        except ValueError:
            return None

    with ThreadPoolExecutor(max_workers=4) as pool:
        assert sum(bool(x) for x in pool.map(create, range(4))) == 1


def test_manual_memberships_archive_merge_and_rejection(rig):
    app, client = seed(rig)
    store = app.state.database
    d = concept(store, W, "DOMAIN", "Products")
    a = concept(store, W, "PROJECT", "Orion", d["id"])
    b = concept(store, W, "PROJECT", "Client", d["id"])
    key = "synthetic/orion-api"
    body = {"repo_keys": [key], "concept_ids": [a["id"], b["id"]]}
    assert post(client, "/repos/associations", body).status_code == 200
    assert domain.coverage(store.read(W))["organized"] == 1
    assert post(client, "/repos/associations", {**body, "operation": "REMOVE"}).status_code == 200
    store.mutate(W, lambda s: domain.mapping(s, [key], [a["id"]], "ADD", "RULE"))
    assert not store.read(W)["organization"]["edges"][key]
    store.mutate(W, lambda s: domain.mapping(s, [key], [a["id"]], "ADD"))
    store.mutate(W, lambda s: domain.merge_concepts(s, a["id"], b["id"]))
    state = store.read(W)
    assert state["organization"]["edges"][key][b["id"]]["source"] == "USER"
    assert b["id"] not in state["organization"]["rejections"][key]
    store.mutate(W, lambda s: domain.remove_concept(s, d["id"]))
    state = store.read(W)
    assert state["organization"]["concepts"][b["id"]]["domain"] != d["id"]
    assert any(c.get("protected") for c in state["organization"]["concepts"].values())


def test_complete_review_first_flow_and_duplicate_delivery(rig):
    app, client, concepts = published(rig)
    assert app.state.database.read(W)["organization"]["control"]["revision"] == 1
    assert not app.state.database.read(W)["organization"]["edges"]
    response = post(
        client, "/organizer/reorganize", {"mode": "FULL_CLASSIFICATION", "ai_mode": "LIVE"}
    )
    assert response.status_code == 202
    job = app.state.database.claim({W})
    before = Provider.calls
    asyncio.run(app.state.service.perform(job))
    asyncio.run(app.state.service.perform(job))
    assert Provider.calls - before == 3
    org = app.state.database.read(W)["organization"]
    assert org["runs"][job["id"]]["processed"] == 3
    assert domain.coverage(app.state.database.read(W))["organized"] == 0
    suggestions = list(org["suggestions"].values())
    assert len(suggestions) == 3
    sid = next(s["id"] for s in suggestions if s["kind"] == "PROJECT")
    assert "/" not in sid
    assert post(client, "/organizer/suggestions/" + sid + "/accept").status_code == 200
    assert post(client, "/organizer/suggestions/" + sid + "/accept").status_code == 409
    assert domain.coverage(app.state.database.read(W))["organized"] == 1
    second = next(s for s in suggestions if s["id"] != sid)
    assert post(client, "/organizer/suggestions/" + second["id"] + "/reject").status_code == 200
    assert (
        second["concept_id"]
        in app.state.database.read(W)["organization"]["rejections"][second["repo_key"]]
    )


def test_rules_only_can_use_private_metadata_without_provider(rig):
    app, client, _ = rig
    assert post(client, "/sync", collection="github").status_code == 202
    assert work(app, str(USER["id"]) + ":github")["status"] == "COMPLETED"
    workspace = str(USER["id"]) + ":github"
    c = concept(app.state.database, workspace, "TAG", "python")
    rule = {
        "name": "Python rule",
        "field": "language",
        "operator": "equals",
        "value": "Python",
        "concept_id": c["id"],
    }
    assert post(client, "/content/rules/preview", rule, "github").json()["matches"] == [
        "github.com#10",
        "github.com#11",
    ]
    assert post(client, "/content/rules", rule, "github").status_code == 200
    before = Provider.calls
    assert (
        post(
            client,
            "/organizer/reorganize",
            {"mode": "FULL_CLASSIFICATION", "ai_mode": "RULES"},
            "github",
        ).status_code
        == 202
    )
    assert work(app, workspace)["status"] == "COMPLETED"
    assert Provider.calls == before
    state = app.state.database.read(workspace)
    assert state["organization"]["edges"]["github.com#11"][c["id"]]["source"] == "RULE"
    assert not state["intelligence"]["profiles"]
    assert (
        post(
            client,
            "/organizer/reorganize",
            {"mode": "EXTRACT", "repo_keys": ["github.com#11"]},
            "github",
        ).status_code
        == 409
    )


def test_global_filter_cursor_binding_and_actor_window(rig):
    app, client = seed(rig)
    first = client.get("/api/v1/repos?collection=samples&view=all&limit=1").json()
    assert first["total"] == 3 and first["next_cursor"]
    assert (
        client.get(
            "/api/v1/repos",
            params={
                "collection": "samples",
                "view": "all",
                "limit": 1,
                "cursor": first["next_cursor"],
            },
        ).json()["items"][0]["key"]
        != first["items"][0]["key"]
    )
    assert (
        client.get(
            "/api/v1/repos",
            params={
                "collection": "samples",
                "view": "all",
                "q": "orion",
                "cursor": first["next_cursor"],
            },
        ).status_code
        == 400
    )
    assert (
        client.get("/api/v1/repos?collection=samples&view=all&q=orion&limit=1").json()["total"] == 2
    )

    def activity(s):
        repos = s["core"]["repos"]
        repos["synthetic/orion-api"]["activities"] = [{"actor_id": 1, "at": domain.now()}]
        repos["synthetic/orion-ui"]["activities"] = [
            {"actor_id": USER["id"], "at": (datetime.now(UTC) - timedelta(days=20)).isoformat()}
        ]

    app.state.database.mutate(W, activity)
    assert client.get("/api/v1/repos?collection=samples&view=latest&days=14").json()["total"] == 0
    assert client.get("/api/v1/repos?collection=samples&view=latest&days=30").json()["total"] == 1


@pytest.mark.parametrize("confirmation", ["delete", " DELETE", "DELETE ", ""])
def test_reset_exact_confirmation(rig, confirmation):
    app, client = seed(rig)
    preview = post(client, "/organizer/reset/preview", {}).json()
    before = app.state.database.read(W)
    assert (
        post(
            client,
            "/organizer/reset/execute",
            {"plan_id": preview["plan_id"], "confirmation": confirmation},
        ).status_code
        == 409
    )
    assert app.state.database.read(W) == before


def test_reset_preview_expiry_reuse_staleness_and_ownership(rig):
    app, client = seed(rig)
    plan = post(client, "/organizer/reset/preview", {}).json()
    concept(app.state.database, W, "TAG", "new")
    assert (
        post(
            client,
            "/organizer/reset/execute",
            {"plan_id": plan["plan_id"], "confirmation": "DELETE"},
        ).status_code
        == 409
    )
    plan = post(client, "/organizer/reset/preview", {}).json()
    with app.state.database.connect() as db:
        db.execute("UPDATE previews SET expires=0 WHERE id=?", (plan["plan_id"],))
    assert (
        post(
            client,
            "/organizer/reset/execute",
            {"plan_id": plan["plan_id"], "confirmation": "DELETE"},
        ).status_code
        == 409
    )
    plan = post(client, "/organizer/reset/preview", {}).json()
    payload = {"plan_id": plan["plan_id"], "confirmation": "DELETE"}
    assert post(client, "/organizer/reset/execute", payload, "github").status_code == 409
    assert post(client, "/organizer/reset/execute", payload).status_code == 202
    assert work(app)["status"] == "COMPLETED"
    assert post(client, "/organizer/reset/execute", payload).status_code == 409


@pytest.mark.parametrize(
    "kinds", [[], ["DOMAIN"], ["TOPIC"], ["DOMAIN", "PROJECT", "TOPIC", "TAG"]]
)
def test_selected_reset_dependencies_preserve_core_and_user_decisions(rig, kinds):
    app, client, concepts = published(rig)
    store = app.state.database
    bykind = {c["kind"]: c["id"] for c in concepts}
    key = "synthetic/orion-api"
    store.mutate(W, lambda s: domain.mapping(s, [key], [bykind["PROJECT"]], "ADD"))
    store.mutate(W, lambda s: domain.mapping(s, [key], [bykind["TAG"]], "REMOVE"))
    before = copy.deepcopy(store.read(W)["core"])
    oldfence = domain.fence(store.read(W))
    plan = post(client, "/organizer/reset/preview", {"kinds": kinds, "cache": True}).json()
    assert (
        post(
            client,
            "/organizer/reset/execute",
            {"plan_id": plan["plan_id"], "confirmation": "DELETE"},
        ).status_code
        == 202
    )
    with pytest.raises(ValueError):
        store.mutate(W, lambda s: domain.check_fence(s, oldfence))
    assert work(app)["status"] == "COMPLETED"
    state = store.read(W)
    assert state["core"] == before and not state["intelligence"]["profiles"]
    assert state["organization"]["audit"][-1]["verified"]
    if "PROJECT" not in kinds:
        assert bykind["PROJECT"] in state["organization"]["edges"][key]
    if "TAG" not in kinds:
        assert bykind["TAG"] in state["organization"]["rejections"][key]
    if "DOMAIN" in kinds and "PROJECT" not in kinds:
        assert state["organization"]["concepts"][bykind["PROJECT"]]["domain"] != bykind["DOMAIN"]
    if len(kinds) == 4:
        assert state["organization"]["control"]["revision"] == 0
    with pytest.raises(ValueError):
        store.mutate(W, lambda s: domain.check_fence(s, oldfence))


def test_queued_old_job_and_restart_recovery_are_safe(rig):
    app, client = seed(rig)
    post(client, "/organizer/reorganize", {"mode": "DISCOVER", "ai_mode": "LIVE"})
    plan = post(client, "/organizer/reset/preview", {}).json()
    post(client, "/organizer/reset/execute", {"plan_id": plan["plan_id"], "confirmation": "DELETE"})
    job = app.state.database.claim({W})
    assert job["kind"] == "RESET"
    app.state.database.recover()
    job = app.state.database.claim({W})
    assert job["kind"] == "RESET"
    asyncio.run(app.state.service.perform(job))
    assert not app.state.database.claim({W})
    post(client, "/organizer/reorganize", {"mode": "DISCOVER", "ai_mode": "LIVE"})
    job = app.state.database.claim({W})
    app.state.database.recover()
    assert app.state.database.read(W)["organization"]["runs"][job["id"]]["status"] == "INTERRUPTED"
    assert app.state.database.claim({W}) is None
    reopened = Store(app.state.database.path)
    assert reopened.read(W)["core"]["repos"]


def test_reauth_queue_and_late_profile_commit(rig):
    app, client, sessions = rig
    seed(rig)
    post(client, "/organizer/reorganize", {"mode": "EXTRACT"})
    assert not app.state.database.claim(set())
    assert app.state.database.claim({W})
    expected = domain.fence(app.state.database.read(W))
    app.state.database.mutate(W, lambda s: s["organization"]["control"].update(cache_epoch=2))
    with pytest.raises(ValueError, match="Stale"):
        asyncio.run(app.state.service.ensure_profile(W, "synthetic/orion-api", expected))


def test_http_allowance_is_durable_atomic_and_separate_from_cost_ledger(tmp_path):
    ledger = Ledger(tmp_path / "experiment", initialize=True)
    ledger.reserve("historical", "gpt-6-luna", 10, 10)
    before = ledger.calls()
    allowance = RequestAllowance(ledger)

    def take(_):
        try:
            return allowance.take("/v1/responses/input_tokens")
        except ProviderBlocked:
            return None

    with ThreadPoolExecutor(max_workers=8) as pool:
        assert len([x for x in pool.map(take, range(30)) if x]) == 20
    assert RequestAllowance(ledger).summary()["remaining"] == 0
    assert ledger.calls() == before
    with pytest.raises(ProviderBlocked):
        allowance.take("/v1/responses")


@pytest.mark.parametrize(
    "field,value",
    [
        ("private", True),
        ("policy_verified", False),
        ("source", "PRIVATE_GITHUB"),
        ("unavailable", True),
    ],
)
def test_private_unverified_extraction_policy(field, value):
    repo = {
        "key": "r",
        "name": "r",
        "private": False,
        "source": "PUBLIC_GITHUB",
        "policy_verified": True,
        field: value,
    }
    assert not model_allowed(repo)
    with pytest.raises(ValueError):
        build_profile(repo, "Sensitive material")


def test_scheduler_threshold_quiet_and_cooldown(rig):
    app, client, concepts = published(rig)
    store = app.state.database
    store.mutate(W, lambda s: s["organization"]["control"].update(auto_enabled=True))
    app.state.service.schedule({W})
    assert not store.read(W)["organization"]["control"]["active_run"]
    parent = next(c["id"] for c in concepts if c["kind"] == "DOMAIN")
    concept(store, W, "PROJECT", "Other", parent)

    def age(s):
        for event in s["organization"]["changes"]:
            event["at"] = time.time() - 100

    store.mutate(W, age)
    app.state.service.schedule({W})
    state = store.read(W)
    rid = state["organization"]["control"]["active_run"]
    assert rid and state["organization"]["runs"][rid]["reason"] == "AUTO"
    assert state["organization"]["runs"][rid]["ai_mode"] == "LIVE"


def test_delayed_model_result_is_fenced_by_actual_reset(rig):
    app, client, _ = published(rig)
    base = Provider

    class Delayed(base):
        def invoke(self, *args, **kwargs):
            result = super().invoke(*args, **kwargs)
            plan = post(client, "/organizer/reset/preview", {"history": False}).json()
            response = post(
                client,
                "/organizer/reset/execute",
                {"plan_id": plan["plan_id"], "confirmation": "DELETE"},
            )
            assert response.status_code == 202
            return result

    app.state.service.provider_factory = Delayed
    post(client, "/organizer/reorganize", {"mode": "FULL_CLASSIFICATION", "ai_mode": "LIVE"})
    run = work(app)
    assert run["status"] == "CANCELLED_STALE"
    assert not app.state.database.read(W)["organization"]["suggestions"]
    assert work(app)["kind"] == "RESET"
    assert not app.state.database.read(W)["organization"]["control"]["resetting"]


def test_manual_decision_wins_over_inflight_model_output(rig):
    app, client, concepts = published(rig)
    target = next(c["id"] for c in concepts if c["kind"] == "TAG")

    class ManualRace(Provider):
        def invoke(self, *args, **kwargs):
            result = super().invoke(*args, **kwargs)
            key = args[4]["repo_id"]
            app.state.database.mutate(W, lambda s: domain.mapping(s, [key], [target], "ADD"))
            return result

    app.state.service.provider_factory = ManualRace
    post(client, "/organizer/reorganize", {"mode": "FULL_CLASSIFICATION", "ai_mode": "LIVE"})
    run = work(app)
    assert run["stale"] == 3 and run["processed"] == 3
    assert run["status"] == "PARTIAL_FAILED"
    assert not app.state.database.read(W)["organization"]["suggestions"]
    assert all(
        e[target]["source"] == "USER"
        for e in app.state.database.read(W)["organization"]["edges"].values()
    )


def test_missing_readme_retains_verified_metadata_and_failed_access_does_not(rig):
    from app.github.client import GitHubError

    app, client, _ = rig
    post(client, "/sync", collection="github")
    workspace = str(USER["id"]) + ":github"
    work(app, workspace)

    class Missing(Adapter):
        async def request(self, token, path, **kwargs):
            if path.endswith("/readme"):
                raise GitHubError("missing_readme", 404)
            return await super().request(token, path, **kwargs)

    app.state.service.adapter = Missing()
    prof = asyncio.run(app.state.service.ensure_profile(workspace, "github.com#10"))
    assert prof["sha"] is None and len(prof["evidence"]) == 1
    assert not app.state.database.read(workspace)["core"]["repos"]["github.com#10"]["unavailable"]

    class Denied(Adapter):
        async def request(self, *args, **kwargs):
            raise GitHubError("permission_denied", 403)

    app.state.service.adapter = Denied()
    with pytest.raises(ValueError, match="not verified"):
        asyncio.run(app.state.service.ensure_profile(workspace, "github.com#10"))
    state = app.state.database.read(workspace)
    assert state["core"]["repos"]["github.com#10"]["unavailable"]
    assert "github.com#10" not in state["intelligence"]["profiles"]


def test_private_rows_missing_from_partial_sync_are_hidden(rig):
    app, client, _ = rig
    workspace = str(USER["id"]) + ":github"
    post(client, "/sync", collection="github")
    work(app, workspace)

    class Partial(Adapter):
        async def inventory(self, token):
            result = await super().inventory(token)
            result["repos"] = result["repos"][:1]
            result["coverage"][0]["status"] = "PARTIAL"
            return result

    app.state.service.adapter = Partial()
    post(client, "/sync", collection="github")
    work(app, workspace)
    assert client.get("/api/v1/repos?collection=github&view=all").json()["total"] == 1
    assert (
        client.get("/api/v1/repos/detail?collection=github&key=github.com%2311").status_code == 404
    )


def test_invalid_nullable_patch_is_validation_error(rig):
    app, client, _ = rig
    c = concept(app.state.database, W, "TAG", "python")
    for field in ("name", "description", "aliases"):
        response = client.patch(
            "/api/v1/taxonomy/concepts/" + c["id"],
            params={"collection": "samples"},
            json={field: None},
        )
        assert response.status_code == 422


def test_resetting_reads_hide_old_organization_and_evidence(rig):
    app, client, concepts = published(rig)
    cid = next(c["id"] for c in concepts if c["kind"] == "PROJECT")
    app.state.database.mutate(W, lambda s: domain.mapping(s, ["synthetic/orion-api"], [cid], "ADD"))
    plan = post(client, "/organizer/reset/preview", {"cache": True}).json()
    post(client, "/organizer/reset/execute", {"plan_id": plan["plan_id"], "confirmation": "DELETE"})
    response = client.get("/api/v1/workspace?collection=samples").json()
    assert response["coverage"]["organized"] == 0 and not response["organization"]["concepts"]
    detail = client.get("/api/v1/repos/detail?collection=samples&key=synthetic/orion-api").json()
    assert not detail["edges"] and detail["profile"] is None


def test_large_inventory_can_resync_and_ai_runs_are_bounded(rig):
    app, client, _ = rig
    workspace = str(USER["id"]) + ":github"

    def seed_many(s):
        s["core"]["repos"] = {
            str(i): {
                "private": False,
                "source": "PUBLIC_GITHUB",
                "policy_verified": True,
                "key": str(i),
            }
            for i in range(80)
        }

    app.state.database.mutate(workspace, seed_many)
    assert post(client, "/organizer/reorganize", {"mode": "EXTRACT"}, "github").status_code == 409
    assert post(client, "/sync", collection="github").status_code == 202
    run = work(app, workspace)
    assert run["status"] == "COMPLETED" and run["processed"] == 2 and run["total"] == 2
