"""Bounded Sync cancellation and explicit recovery, isolated from user databases/providers."""

import asyncio
import copy

import pytest

from app.auth.sessions import SessionStore
from app.demo.service import Service
from app.demo.store import Store
from app.github.client import GitHubError
from tests.demo.fixtures import USER, Adapter

W = str(USER["id"]) + ":github"


@pytest.fixture
def rig(tmp_path):
    now = [100.0]
    sessions = SessionStore(clock=lambda: now[0])
    key = sessions.create(USER, "old-fixture-grant", ["repo"], 60)
    store = Store(tmp_path / "app.sqlite3")
    store.mutate(
        W,
        lambda state: state.update(
            reference_reviews={"fixture-release": {"1": {"status": "HUMAN_CONFIRMED"}}},
            reference_drafts={"fixture-release": {"2": {"notes": "keep this draft"}}},
        ),
    )
    service = Service(store, Adapter(), sessions)
    return store, service, sessions, key, now


def execute(store, service):
    queued = service.queue(W, "SYNC")
    job = store.claim({W})
    assert job["id"] == queued["id"]
    asyncio.run(service.perform(job))
    state = store.read(W)
    return state["organization"]["runs"][job["id"]], state


def assert_safe(before, state):
    for section in ("core", "intelligence", "reference_reviews", "reference_drafts"):
        assert state[section] == before[section]
    assert state["organization"]["concepts"] == before["organization"]["concepts"]
    assert state["organization"]["edges"] == before["organization"]["edges"]
    assert state["organization"]["control"]["active_run"] is None


def test_total_sync_deadline_cancels_inflight_request_and_unblocks_explicit_retry(rig):
    store, service, _, _, _ = rig
    before = copy.deepcopy(store.read(W))
    cancelled = []

    class Slow(Adapter):
        async def inventory(self, token):
            try:
                await asyncio.Future()
            finally:
                cancelled.append(True)

    service.adapter = Slow()
    service.sync_timeout_seconds = 0.02
    run, state = execute(store, service)
    assert run["status"] == "FAILED" and run["error_code"] == "GITHUB_SYNC_TIMEOUT"
    assert run["retryable"] and not run["reauthentication_required"]
    assert run["stage"] == "INVENTORY" and run["timeout_seconds"] == 0.02
    assert "time limit" in run["message"] and "safe" in run["message"]
    assert cancelled == [True]
    assert_safe(before, state)
    with store.connect() as db:
        assert db.execute("SELECT status,lease FROM jobs").fetchone()["lease"] == 0
    assert service.queue(W, "SYNC")["status"] == "QUEUED"


@pytest.mark.parametrize(
    "error,code",
    [
        (GitHubError("network_or_timeout"), "GITHUB_TIMEOUT"),
        (GitHubError("rate_limited", 429), "GITHUB_RATE_LIMITED"),
    ],
)
def test_network_and_rate_limit_failures_are_actionable_without_revoking_session(rig, error, code):
    store, service, sessions, key, _ = rig
    before = store.read(W)

    class Failed(Adapter):
        async def inventory(self, token):
            raise error

    service.adapter = Failed()
    run, state = execute(store, service)
    assert run["status"] == "FAILED" and run["error_code"] == code
    assert run["retryable"] and not run["reauthentication_required"]
    assert sessions.get(key) is not None
    assert_safe(before, state)


@pytest.mark.parametrize("where", ["inventory", "activity", "identity"])
def test_revoked_or_changed_provider_grant_requires_signin_and_preserves_new_grant(rig, where):
    store, service, sessions, key, _ = rig
    before = store.read(W)
    newer = sessions.create(USER, "new-valid-fixture-grant", ["repo"], 3600)

    class Failed(Adapter):
        async def inventory(self, token):
            if where == "inventory":
                raise GitHubError("reauthorization_required", 401)
            result = await super().inventory(token)
            if where == "identity":
                result["identity"] = {"id": 123}
            return result

        async def request(self, *args, **kwargs):
            raise GitHubError("reauthorization_required", 401)

    service.adapter = Failed()
    run, state = execute(store, service)
    assert run["status"] == "FAILED" and run["error_code"] == "GITHUB_REAUTH_REQUIRED"
    assert not run["retryable"] and run["reauthentication_required"]
    assert sessions.get(key) is None and sessions.get(newer) is not None
    assert_safe(before, state)


@pytest.mark.parametrize("invalidate", ["expire", "signout"])
def test_session_ending_mid_sync_prevents_commit_even_after_another_signin(rig, invalidate):
    store, service, sessions, key, now = rig
    before = store.read(W)
    requests = []

    class Interrupted(Adapter):
        async def inventory(self, token):
            result = await super().inventory(token)
            if invalidate == "expire":
                now[0] += 61
            else:
                sessions.discard(key)
            sessions.create(USER, "new-valid-fixture-grant", ["repo"], 3600)
            return result

        async def request(self, *args, **kwargs):
            requests.append(True)
            raise AssertionError("Expired grant must not be used for activity")

    service.adapter = Interrupted()
    run, state = execute(store, service)
    assert run["status"] == "FAILED" and run["error_code"] == "SESSION_EXPIRED"
    assert run["reauthentication_required"]
    assert requests == []
    assert_safe(before, state)


def test_expired_queued_sync_requires_explicit_retry_instead_of_silent_resume(rig):
    store, service, sessions, _, now = rig
    queued = service.queue(W, "SYNC")
    before = store.read(W)
    now[0] += 61
    assert store.claim(set()) is None
    state = store.read(W)
    run = state["organization"]["runs"][queued["id"]]
    assert run["status"] == "FAILED" and run["error_code"] == "SESSION_EXPIRED"
    assert run["reauthentication_required"] and not run["retryable"]
    assert_safe(before, state)
    sessions.create(USER, "fresh-fixture-grant", ["repo"], 3600)
    assert store.claim({W}) is None
    assert service.queue(W, "SYNC")["status"] == "QUEUED"


def test_successful_sync_publishes_stages_and_completes_normally(rig):
    store, service, _, _, _ = rig
    run, state = execute(store, service)
    assert run["status"] == "COMPLETED" and run["stage"] == "DONE"
    assert run["processed"] == 2 and run["timeout_seconds"] == 300
    assert "up to date" in run["message"]
    assert state["organization"]["control"]["active_run"] is None
    assert state["reference_reviews"]["fixture-release"]["1"]["status"] == "HUMAN_CONFIRMED"


def test_backend_restart_interrupts_sync_visibly_without_replaying_it(rig):
    store, service, _, _, _ = rig
    queued = service.queue(W, "SYNC")
    store.claim({W})
    before = store.read(W)
    store.recover()
    state = store.read(W)
    run = state["organization"]["runs"][queued["id"]]
    assert run["status"] == "INTERRUPTED"
    assert run["error_code"] == "GITHUB_SYNC_INTERRUPTED"
    assert run["retryable"] and not run["reauthentication_required"]
    assert run["finished_at"]
    assert_safe(before, state)
    assert store.claim({W}) is None
    assert service.queue(W, "SYNC")["status"] == "QUEUED"
