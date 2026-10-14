from concurrent.futures import ThreadPoolExecutor

import httpx2
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.auth.sessions import SessionStore
from app.demo.ai import DemoAISettings, DemoProvider
from app.demo.allowance import AllowanceUpdate, ApplicationLedger, RequestAllowance
from app.local import LocalSettings, create_local_app
from app.pretest.ai.provider import ProviderBlocked
from app.pretest.ai.schemas import AccessProbe
from app.pretest.ai.storage import BudgetError, Ledger
from tests.demo.fixtures import USER, Adapter, Provider
from tests.pretest.ai.test_safety import transport_handler


def update(manager, action="RENEW", **values):
    return manager.update(
        AllowanceUpdate(
            action=action,
            expected_revision=manager.policy()["revision"],
            reason="Operator testing",
            **values,
        ),
        actor="local-test",
    )


def test_renew_preserves_history_cache_spend_reservations_and_survives_reopen(tmp_path):
    ledger = ApplicationLedger(tmp_path / "ai", initialize=True)
    manager = RequestAllowance(ledger)
    for _ in range(10):
        ledger.reserve("historical", "gpt-6-luna", 1, 1)
    ledger.cache_put("preserved", {"fixture": True})
    for _ in range(20):
        manager.take("/v1/responses/input_tokens")
    before, calls = ledger.summary(), ledger.calls()
    with pytest.raises(ProviderBlocked):
        manager.take("/v1/responses/input_tokens")
    with pytest.raises(BudgetError):
        ledger.reserve("blocked", "gpt-6-luna", 1, 1)
    renewed = update(manager, requests=20)
    assert renewed["http"]["used"] == renewed["generations"]["used"] == 0
    assert renewed["http"]["remaining"] == 20
    assert renewed["generations"]["remaining"] == 10
    assert ledger.summary() == before
    assert ledger.calls() == calls
    assert ledger.cache_get("preserved") == {"fixture": True}
    reopened = ApplicationLedger(tmp_path / "ai")
    assert RequestAllowance(reopened).policy() == renewed
    assert len(RequestAllowance(reopened).history()) == 1
    reopened.reserve("new", "gpt-6-luna", 1, 1, max_calls=10)
    assert manager.policy()["generations"]["used"] == 1


def test_selective_updates_and_concurrent_stale_renewal(tmp_path):
    ledger = ApplicationLedger(tmp_path / "ai", initialize=True)
    manager = RequestAllowance(ledger)
    manager.take("/v1/responses/input_tokens")
    changed = update(manager, "SET_LIMITS", requests=25)
    assert changed["http"]["used"] == 1
    assert changed["http"]["limit"] == 25
    assert changed["generations"]["limit"] == 10
    changed = update(manager, "SET_LIMITS", generations=4)
    assert changed["http"]["limit"] == 25
    assert changed["generations"]["limit"] == 4
    with pytest.raises(ValueError, match="lower than"):
        update(manager, "SET_LIMITS", requests=0)
    value = AllowanceUpdate(
        action="RENEW", expected_revision=2, requests=6, reason="Concurrent test"
    )

    def renew(_):
        try:
            manager.update(value, "test")
            return True
        except ValueError:
            return False

    with ThreadPoolExecutor(max_workers=4) as pool:
        assert sum(pool.map(renew, range(4))) == 1
    assert manager.policy()["http"]["remaining"] == 6
    assert len(manager.history()) == 3


def test_dynamic_generation_limit_is_atomic_and_dollar_budget_cannot_be_reset(tmp_path):
    ledger = ApplicationLedger(tmp_path / "ai", initialize=True)
    manager = RequestAllowance(ledger)
    update(manager, "SET_LIMITS", generations=2)

    def reserve(_):
        try:
            return ledger.reserve("test", "gpt-6-luna", 1, 1, max_calls=44)
        except BudgetError:
            return None

    with ThreadPoolExecutor(max_workers=8) as pool:
        assert len([r for r in pool.map(reserve, range(20)) if r]) == 2
    update(manager, "SET_LIMITS", generations=3)
    assert ledger.reserve("renewed", "gpt-6-luna", 1, 1)
    # All earlier uncertain reservations remain charged against admission.
    update(manager, requests=1000, generations=1000)
    with pytest.raises(BudgetError, match=r"\$5"):
        ledger.reserve("too-expensive", "gpt-6-astra", 1_000_000, 4096)
    with pytest.raises(BudgetError, match="cannot change"):
        Ledger(tmp_path / "ai", cap=4)


def test_actual_provider_hooks_continue_after_44_with_mock_http_only(tmp_path, monkeypatch):
    ledger = ApplicationLedger(tmp_path / "ai", initialize=True)
    # Existing historical records are retained, including the original 44 ceiling.
    with ledger.connect() as db:
        for i in range(44):
            db.execute(
                "INSERT INTO calls VALUES (?,?,?,0,0,?,?,?)",
                (str(i), "historical", "gpt-6-luna", "SETTLED", "{}", str(i)),
            )
        db.commit()
    update(RequestAllowance(ledger), requests=2, generations=1)
    settings = DemoAISettings(
        _env_file=None, openai_api_key="fixture-only", ai_pretest_live_enabled=True
    )
    monkeypatch.setattr("app.demo.ai.private_json", lambda *args, **kwargs: None)
    calls = []
    provider = DemoProvider(
        settings,
        ledger,
        mode="LIVE",
        transport=httpx2.MockTransport(lambda request: transport_handler(request, calls)),
    )
    try:
        result = provider.invoke(
            "gpt-6-luna",
            "access",
            AccessProbe,
            "Return TEST true.",
            {"source": "SYNTHETIC", "private": False},
            lambda x: x,
            fresh=True,
            max_output=256,
        )
        assert result["status"] == "PASS", result
        assert ledger.summary()["calls"] == 45
        assert RequestAllowance(ledger).summary()["used"] == 2
        blocked = provider.invoke(
            "gpt-6-luna",
            "access",
            AccessProbe,
            "Return TEST true.",
            {"source": "SYNTHETIC", "private": False},
            lambda x: x,
            fresh=True,
            max_output=256,
        )
        assert blocked["status"] != "PASS"
        assert len(calls) == 2
    finally:
        provider.close()


@pytest.mark.parametrize(
    "fields",
    [
        {"action": "RENEW", "requests": 1},
        {"action": "SET_LIMITS"},
        {"action": "RENEW", "requests": 1001},
        {"action": "RENEW", "requests": True},
        {"action": "RENEW", "requests": 20, "cap_usd": 50},
    ],
)
def test_invalid_or_spending_overrides_rejected(fields):
    with pytest.raises(ValidationError):
        AllowanceUpdate(expected_revision=0, reason="Invalid override test", **fields)


def test_operator_api_csrf_audit_and_global_collection_scope(tmp_path):
    ledger = ApplicationLedger(tmp_path / "ai", initialize=True)
    sessions = SessionStore()
    cookie = sessions.create(USER, "fixture", ["repo"], 3600)
    app = create_local_app(
        LocalSettings(_env_file=None, demo_budget_operator_ids=str(USER["id"])),
        adapter=Adapter(),
        sessions=sessions,
        db_path=tmp_path / "app.sqlite3",
        provider_factory=Provider,
        allowance_ledger=ledger,
    )
    client = TestClient(app, base_url="http://127.0.0.1:8000")
    payload = {"action": "RENEW", "expected_revision": 0, "requests": 20, "reason": "API test"}
    assert client.post("/api/v1/ai/allowance", json=payload).status_code == 401
    client.cookies.set("gm_session", cookie)
    assert client.post("/api/v1/ai/allowance", json=payload).status_code == 403
    client.headers.update(
        {"Origin": "http://127.0.0.1:3000", "X-CSRF-Token": sessions.get(cookie).csrf_token}
    )
    assert client.post("/api/v1/ai/allowance", json=payload).status_code == 200
    assert client.post("/api/v1/ai/allowance", json=payload).status_code == 409
    for collection in ["samples", "github"]:
        workspace = client.get("/api/v1/workspace", params={"collection": collection}).json()
        assert workspace["can_manage_allowance"]
        assert workspace["budget"]["revision"] == 1
    assert len(client.get("/api/v1/ai/allowance/history").json()) == 1
    other = sessions.create({"id": 88, "login": "other"}, "fixture", ["repo"], 3600)
    client.cookies.set("gm_session", other)
    client.headers["X-CSRF-Token"] = sessions.get(other).csrf_token
    assert client.post("/api/v1/ai/allowance", json=payload).status_code == 403
    assert client.get("/api/v1/ai/allowance/history").status_code == 403
