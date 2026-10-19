"""Local-session deadline/renewal boundaries without calling GitHub or exposing grants."""

from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi.testclient import TestClient

from app.auth.sessions import SessionStore
from app.config import Settings
from app.main import create_app

ORIGIN = "http://127.0.0.1:3000"
TOKEN = "session-renewal-fixture-must-not-leak"


class Adapter:
    def __init__(self, token_ttl=None):
        self.token_ttl = token_ttl

    def authorization_url(self, state, verifier):
        return "https://github.com/login/oauth/authorize?state=" + state

    async def exchange(self, code, verifier):
        value = {"access_token": TOKEN, "scope": "repo,read:org"}
        if self.token_ttl is not None:
            value["expires_in"] = self.token_ttl
        return value

    async def identity(self, token):
        return {"id": 42, "login": "session-fixture"}


@pytest.fixture
def rig():
    now = [100.0]
    store = SessionStore(clock=lambda: now[0])
    adapter = Adapter()
    settings = Settings(_env_file=None, github_client_id="fixture", github_client_secret="fixture")
    client = TestClient(create_app(settings, adapter, store), base_url=ORIGIN)
    return client, store, adapter, now


def login(client):
    start = client.get("/api/v1/auth/github/start", follow_redirects=False)
    state = parse_qs(urlsplit(start.headers["location"]).query)["state"][0]
    result = client.get(
        "/api/v1/auth/github/callback",
        params={"state": state, "code": "fixture"},
        follow_redirects=False,
    )
    assert result.status_code == 303
    identity = client.get("/api/v1/me").json()
    return {"Origin": ORIGIN, "X-CSRF-Token": identity["csrf_token"]}


def test_countdown_does_not_extend_until_explicit_csrf_protected_renewal(rig):
    client, store, _, now = rig
    headers = login(client)
    key = client.cookies["gm_session"]
    first = client.get("/api/v1/me")
    assert first.json()["session"] == {
        "expires_in_seconds": 3600,
        "warning_seconds": 120,
        "renewable": True,
        "extension_seconds": 3600,
    }
    now[0] += 3500
    assert client.get("/api/v1/me").json()["session"]["expires_in_seconds"] == 100
    deadline = store.get(key).expires_at
    for invalid in (
        {},
        {**headers, "Origin": "http://evil.example"},
        {**headers, "X-CSRF-Token": "wrong"},
    ):
        assert client.post("/api/v1/auth/session/extend", headers=invalid).status_code == 403
        assert store.get(key).expires_at == deadline
    response = client.post("/api/v1/auth/session/extend", headers=headers)
    assert response.status_code == 200
    assert response.json()["session"]["expires_in_seconds"] == 3600
    assert response.json()["csrf_token"] == headers["X-CSRF-Token"]
    assert client.cookies["gm_session"] == key
    assert "Max-Age=3600" in response.headers["set-cookie"]
    assert "HttpOnly" in response.headers["set-cookie"]
    assert "SameSite=lax" in response.headers["set-cookie"]
    assert TOKEN not in response.text and TOKEN not in first.text


def test_renewal_is_capped_by_explicit_provider_deadline_and_never_resurrects(rig):
    client, store, adapter, now = rig
    adapter.token_ttl = 4000
    headers = login(client)
    key = client.cookies["gm_session"]
    now[0] += 3500
    assert client.get("/api/v1/me").json()["session"]["renewable"] is True
    response = client.post("/api/v1/auth/session/extend", headers=headers)
    assert response.status_code == 200
    assert response.json()["session"]["expires_in_seconds"] == 500
    assert response.json()["session"]["renewable"] is False
    assert "Max-Age=500" in response.headers["set-cookie"]
    assert store.get(key).expires_at == 4100
    now[0] = 4100
    response = client.post("/api/v1/auth/session/extend", headers=headers)
    assert response.status_code == 401
    assert response.json()["code"] == "SESSION_EXPIRED"
    assert response.json()["reauthentication_required"] is True
    assert store.get(key) is None


def test_short_provider_grant_requires_signin_instead_of_claiming_it_can_extend(rig):
    client, _, adapter, _ = rig
    adapter.token_ttl = 120
    login(client)
    session = client.get("/api/v1/me").json()["session"]
    assert session["expires_in_seconds"] == 120
    assert session["renewable"] is False


def test_expired_local_session_and_backend_restart_require_fresh_signin(rig):
    client, store, _, now = rig
    headers = login(client)
    now[0] += 3600
    assert client.post("/api/v1/auth/session/extend", headers=headers).status_code == 401
    login(client)
    store.sessions.clear()  # Models the intentionally memory-only local auth store after restart.
    response = client.get("/api/v1/me")
    assert response.status_code == 401
    assert response.json()["code"] == "SESSION_EXPIRED"
    assert client.post("/api/v1/auth/session/extend", headers=headers).status_code == 401


def test_provider_revocation_does_not_discard_another_newer_grant(rig):
    client, store, _, _ = rig
    login(client)
    older = client.cookies["gm_session"]
    duplicate = store.create({"id": 42}, TOKEN, [], 3600)
    newer = store.create({"id": 42}, "another-grant", [], 3600)
    store.discard_token(TOKEN)
    assert store.get(older) is None and store.get(duplicate) is None
    assert store.get(newer) is not None
