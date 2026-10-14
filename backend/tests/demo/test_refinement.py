import asyncio
import copy
from concurrent.futures import ThreadPoolExecutor

import httpx2
import pytest
from fastapi.testclient import TestClient

from app.auth.sessions import SessionStore
from app.demo import cohorts, domain, pricing
from app.demo.ai import DemoAISettings, DemoProvider
from app.demo.allowance import ApplicationLedger, RequestAllowance
from app.demo.run_budget import RunBudgets
from app.local import LocalSettings, create_local_app
from app.pretest.ai.schemas import AccessProbe
from app.pretest.ai.storage import BudgetError, Ledger
from tests.demo.fixtures import USER, Adapter, Provider
from tests.pretest.ai.test_safety import transport_handler

W = str(USER["id"]) + ":samples"


@pytest.fixture
def rig(tmp_path):
    ledger = ApplicationLedger(tmp_path / "ledger", initialize=True)
    sessions = SessionStore()
    cookie = sessions.create(USER, "fixture-only", ["repo"], 3600)
    app = create_local_app(
        LocalSettings(_env_file=None, demo_live_ai=True, demo_budget_operator_ids=str(USER["id"])),
        adapter=Adapter(),
        sessions=sessions,
        db_path=tmp_path / "app.sqlite3",
        provider_factory=Provider,
        allowance_ledger=ledger,
    )
    client = TestClient(app, base_url="http://127.0.0.1:8000")
    client.cookies.set("gm_session", cookie)
    client.headers.update(
        {"Origin": "http://127.0.0.1:3000", "X-CSRF-Token": sessions.get(cookie).csrf_token}
    )
    app.state.service.load_samples(W)
    return app, client, ledger


def post(client, path, value):
    return client.post("/api/v1" + path, params={"collection": "samples"}, json=value)


def preview(client, **values):
    response = post(
        client,
        "/organizer/preview",
        {"mode": "DISCOVER", "ai_mode": "CACHE", "scope": {"view": "all"}, **values},
    )
    assert response.status_code == 200, response.text
    return response.json()


def add_many(app, count=40):
    def mutate(state):
        template = state["core"]["repos"]["synthetic/orion-api"]
        profile = state["intelligence"]["profiles"]["synthetic/orion-api"]
        for i in range(count):
            key = f"synthetic/repo-{i:03}"
            from app.demo.analysis import new_repository

            new_repository(state, key)
            state["core"]["repos"][key] = {
                **copy.deepcopy(template),
                "key": key,
                "name": f"repo-{i:03}",
                "owner": f"owner-{i % 3}",
                "language": ["Python", "TypeScript", None][i % 3],
            }
            state["intelligence"]["profiles"][key] = copy.deepcopy(profile)

    app.state.database.mutate(W, mutate)


def test_scoped_kpis_languages_selection_and_pagination(rig):
    app, client, _ = rig
    add_many(app)
    response = client.get(
        "/api/v1/repos", params={"collection": "samples", "view": "all", "q": "repo-", "limit": 1}
    ).json()
    assert len(response["items"]) == 1
    assert response["summary"]["repos"] == 40
    assert sum(x["count"] for x in response["languages"]) == 40
    assert any(x["label"] == "Unknown" for x in response["languages"])
    selected = post(
        client,
        "/repos/summary",
        {"repo_keys": ["synthetic/repo-001", "synthetic/repo-002", "synthetic/repo-001"]},
    ).json()
    assert selected["repos"] == 2
    assert selected["uncategorized"] == 2
    assert (
        post(client, "/repos/summary", {"repo_keys": ["another-owner/private"]}).status_code == 409
    )
    unknown = client.get("/api/v1/repos?collection=samples&view=all&language=__UNKNOWN__").json()
    assert unknown["total"] > 1
    assert all(not r["language"] for r in unknown["items"])


def test_deterministic_global_cohort_and_private_exclusion(rig):
    app, client, ledger = rig
    add_many(app)
    app.state.database.mutate(
        W, lambda s: s["core"]["repos"]["synthetic/repo-000"].update(private=True)
    )
    before = ledger.summary()
    first = preview(client, count=10)
    second = preview(client, count=10)
    assert first["keys"] == second["keys"]
    assert first["chosen"] == 10
    assert first["eligible"] == 42
    assert "synthetic/repo-000" not in first["keys"]
    assert len({r["language"] for r in first["repositories"]}) >= 2
    assert first["http_requests"] == 0
    assert ledger.summary() == before
    assert preview(client, ai_mode="LIVE", count=30)["http_requests"] == 2


def test_exact_plan_execution_idempotency_staleness_owner_and_expiry(rig):
    app, client, _ = rig
    plan = preview(client, count=2)
    response = post(client, "/organizer/execute", {"plan_id": plan["plan_id"]})
    assert response.status_code == 202, response.text
    repeated = post(client, "/organizer/execute", {"plan_id": plan["plan_id"]})
    assert repeated.status_code == 202
    assert repeated.json()["id"] == response.json()["id"]
    job = app.state.database.claim({W})
    assert job["payload"]["repo_keys"] == plan["keys"]
    asyncio.run(app.state.service.perform(job))
    stale = preview(client)
    app.state.database.mutate(W, lambda s: s.update(preferences={"taxonomy_count": 2}))
    assert post(client, "/organizer/execute", {"plan_id": stale["plan_id"]}).status_code == 409
    fresh = preview(client)
    assert (
        client.post(
            "/api/v1/organizer/execute?collection=github", json={"plan_id": fresh["plan_id"]}
        ).status_code
        == 409
    )
    with app.state.database.connect() as db:
        db.execute("UPDATE run_previews SET expires=0 WHERE id=?", (fresh["plan_id"],))
    assert post(client, "/organizer/execute", {"plan_id": fresh["plan_id"]}).status_code == 409


def test_adaptive_fit_and_budget_revision(rig):
    app, client, ledger = rig
    app.state.database.mutate(
        W,
        lambda s: domain.create_concept(
            s,
            {
                "kind": "TAG",
                "name": "Python",
                "description": "Primary language",
                "aliases": [],
                "domain": None,
            },
        ),
    )
    plan = preview(
        client,
        mode="FULL_CLASSIFICATION",
        ai_mode="LIVE",
        count=3,
        budget_mode="ADAPTIVE",
        budget_usd=0.002,
    )
    assert plan["chosen"] == 1
    assert plan["can_start"]
    assert len(plan["excluded"]) == 2
    assert plan["upper_usd"] <= 0.002
    manager = RequestAllowance(ledger)
    from app.demo.allowance import AllowanceUpdate

    manager.update(
        AllowanceUpdate(
            action="SET_LIMITS", requests=30, expected_revision=0, reason="Revision test"
        ),
        "test",
    )
    assert post(client, "/organizer/execute", {"plan_id": plan["plan_id"]}).status_code == 409
    assert RunBudgets(ledger).summary()["held_usd"] == 0


def test_adaptive_actual_provider_bypasses_exhausted_fixed_caps_without_losing_history(
    tmp_path, monkeypatch
):
    base = Ledger(tmp_path / "ledger", initialize=True)
    for _ in range(44):
        ident = base.reserve("historical", "gpt-6-luna", 1, 1)
        base.settle(ident, {}, no_charge=True)
    ledger = ApplicationLedger(tmp_path / "ledger")
    fixed = RequestAllowance(ledger)
    for _ in range(20):
        fixed.take("/v1/responses/input_tokens")
    history = ledger.calls()
    budget = RunBudgets(ledger)
    ceiling = pricing.reserve_amount("gpt-6-luna", 2000, 2048)
    budget.reserve("approved-plan", W, ceiling, 1, "operator", 0)
    budget.activate("approved-plan", W)
    settings = DemoAISettings(
        _env_file=None, openai_api_key="fixture-only", ai_pretest_live_enabled=True
    )
    monkeypatch.setattr("app.demo.ai.private_json", lambda *args, **kwargs: None)
    requests = []
    provider = DemoProvider(
        settings,
        ledger,
        mode="LIVE",
        transport=httpx2.MockTransport(lambda r: transport_handler(r, requests)),
    )
    provider.bind_budget("approved-plan")
    try:
        result = provider.invoke(
            "gpt-6-luna",
            "access",
            AccessProbe,
            "Return TEST true.",
            {"source": "SYNTHETIC", "private": False},
            lambda v: v,
            fresh=True,
            max_output=256,
        )
        assert result["status"] == "PASS", result
        assert ledger.summary()["calls"] == 45
        assert ledger.calls()[:44] == history
        assert fixed.summary()["used"] == 20
        assert fixed.summary()["lifetime_used"] == 22
        assert fixed.policy()["generations"]["used"] == 10
        assert len(requests) == 2
        assert (
            provider.invoke(
                "gpt-6-luna",
                "access",
                AccessProbe,
                "Return TEST true.",
                {"source": "SYNTHETIC", "private": False},
                lambda v: v,
                fresh=True,
                max_output=256,
            )["status"]
            != "PASS"
        )
        assert len(requests) == 2
    finally:
        provider.close()
        budget.finish("approved-plan")
    assert budget.summary()["held_usd"] == 0


def test_atomic_holds_transfer_uncertainty_and_recovery(tmp_path):
    ledger = ApplicationLedger(tmp_path / "ledger", cap=0.01, initialize=True)
    budget = RunBudgets(ledger)

    def hold(i):
        try:
            budget.reserve(str(i), W, 8000, 3, "test", 0)
            return str(i)
        except BudgetError:
            return None

    with ThreadPoolExecutor(max_workers=4) as pool:
        accepted = [x for x in pool.map(hold, range(4)) if x is not None]
    assert len(accepted) == 1
    plan_id = accepted[0]
    budget.activate(plan_id, W)
    ledger.plan_id = plan_id
    reservation = ledger.reserve("unknown", "gpt-6-luna", 2000, 2048)
    assert budget.available() == 2000  # Hold became a call reservation, not a second charge.
    budget.finish(plan_id)
    assert budget.available() == 10000 - pricing.reserve_amount("gpt-6-luna", 2000, 2048)
    assert ledger.calls()[0]["id"] == reservation
    assert ledger.summary()["reserved_usd"] > 0


def test_taxonomy_packing_is_bounded_and_does_not_mutate_profiles(rig):
    app, _, _ = rig
    add_many(app, 30)
    profiles = app.state.database.read(W)["intelligence"]["profiles"]
    original = copy.deepcopy(profiles)
    packed = cohorts.taxonomy_collection(profiles, 12000)
    import json

    assert len(json.dumps(packed).encode()) < 10000
    assert profiles == original


def test_adaptive_permission_and_preferences(rig):
    app, client, ledger = rig
    prefs = {
        "taxonomy_count": 4,
        "classification_count": 2,
        "budget_mode": "ADAPTIVE",
        "budget_usd": 0.1,
    }
    assert (
        client.patch("/api/v1/organizer/preferences?collection=samples", json=prefs).status_code
        == 200
    )
    assert client.get("/api/v1/workspace?collection=samples").json()["preferences"] == prefs
    plan = preview(client, ai_mode="LIVE", budget_mode="ADAPTIVE")
    # Revocation at execution is checked even if the plan was previewed earlier.
    app.state.service.budget_operators.clear()
    app_settings = LocalSettings(_env_file=None)
    other_app = create_local_app(
        app_settings,
        adapter=Adapter(),
        sessions=app.state.sessions,
        db_path=app.state.database.path,
        provider_factory=Provider,
        allowance_ledger=ledger,
    )
    other = TestClient(other_app, base_url="http://127.0.0.1:8000")
    other.cookies.update(client.cookies)
    other.headers.update(client.headers)
    assert post(other, "/organizer/execute", {"plan_id": plan["plan_id"]}).status_code == 403
    assert (
        other.patch("/api/v1/organizer/preferences?collection=samples", json=prefs).status_code
        == 403
    )


def test_concurrent_start_has_one_job_and_one_hold(rig):
    app, client, ledger = rig
    plan = preview(client, ai_mode="LIVE", budget_mode="ADAPTIVE", count=2)

    def start(_):
        return app.state.service.start_plan(W, plan["plan_id"], actor="operator", operator=True)[
            "id"
        ]

    with ThreadPoolExecutor(max_workers=4) as pool:
        ids = list(pool.map(start, range(4)))
    assert set(ids) == {plan["plan_id"]}
    with app.state.database.connect() as db:
        assert (
            db.execute("SELECT COUNT(*) FROM jobs WHERE id=?", (plan["plan_id"],)).fetchone()[0]
            == 1
        )
    budget = RunBudgets(ledger)
    assert budget.summary()["held_usd"] == plan["upper_usd"]
    assert budget.outcome(plan["plan_id"])["state"] == "QUEUED"


def test_restart_releases_unused_hold_and_keeps_unknown_calls_and_other_stores(rig, tmp_path):
    from app.demo.store import Store

    app, client, ledger = rig
    budget = RunBudgets(ledger)
    plan = preview(client, ai_mode="LIVE", budget_mode="ADAPTIVE", count=2)
    app.state.service.start_plan(W, plan["plan_id"], actor="operator", operator=True)
    app.state.database.claim({W})
    budget.activate(plan["plan_id"], W)
    ledger.plan_id = plan["plan_id"]
    ledger.reserve("unknown", "gpt-6.1-sol", 10, 10)
    outstanding = ledger.summary()["reserved_usd"]
    app.state.database.recover()
    budget.reconcile(app.state.database)
    assert budget.summary()["held_usd"] == 0
    assert ledger.summary()["reserved_usd"] == outstanding > 0
    budget.reserve("orphan", W, 100, 1, "test", 0, budget.store_id(app.state.database))
    with ledger.connect() as db:
        db.execute("UPDATE app_run_budgets SET expires=0 WHERE id='orphan'")
        db.commit()
    budget.reconcile(Store(tmp_path / "other.sqlite3"))
    assert budget.summary()["held_usd"] > 0
    budget.reconcile(app.state.database)
    assert budget.summary()["held_usd"] == 0


def test_price_snapshot_is_pinned_at_reservation(tmp_path, monkeypatch):
    ledger = ApplicationLedger(tmp_path / "ledger", initialize=True)
    ident = ledger.reserve("price", "gpt-6-luna", 42, 256)
    monkeypatch.setitem(
        pricing.RATES, "gpt-6-luna", {k: "100" for k in pricing.RATES["gpt-6-luna"]}
    )
    ledger.settle(ident, {"input_tokens": 42, "output_tokens": 10})
    assert ledger.calls()[0]["charged"] == 10


def test_fixed_reservation_and_adaptive_hold_compete_atomically(tmp_path):
    ledger = ApplicationLedger(tmp_path / "ledger", cap=0.002, initialize=True)
    budget = RunBudgets(ledger)
    amount = pricing.reserve_amount("gpt-6-luna", 2000, 2048)

    def admit(mode):
        try:
            if mode == "adaptive":
                budget.reserve("competing-run", W, amount, 1, "test", 0)
            else:
                ledger.reserve("fixed", "gpt-6-luna", 2000, 2048)
            return True
        except BudgetError:
            return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        accepted = list(pool.map(admit, ["fixed", "adaptive"]))
    assert sum(accepted) == 1
    assert ledger.summary()["reserved_usd"] + budget.summary()["held_usd"] == amount / 1e6
    assert budget.available() == 2000 - amount
