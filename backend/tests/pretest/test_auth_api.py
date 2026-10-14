import base64
import json
from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi.testclient import TestClient

from app.auth.sessions import SessionStore
from app.config import Settings
from app.github.client import GitHubError, OAuthAppAdapter
from app.main import create_app

TOKEN = "fixture-token-must-not-leak"


class Adapter:
    calls = 0

    def authorization_url(self, state, verifier):
        return "https://github.com/login/oauth/authorize?state=" + state

    async def exchange(self, code, verifier):
        assert code == "fixture-code" and verifier
        return {"access_token": TOKEN, "scope": "repo,read:org", "expires_in": 120}

    async def identity(self, token):
        assert token == TOKEN
        return {"id": 42, "login": "fixture-user", "name": "Fixture User"}

    async def inventory(self, token):
        self.calls += 1
        return {
            "identity": await self.identity(token),
            "repos": [
                {
                    "id": i,
                    "full_name": f"fixture/repo-{i}",
                    "sources": ["OWNER"],
                    "eligible": i != 3,
                    "favorite": i == 3,
                }
                for i in range(1, 5)
            ],
            "coverage": [{"source": "OWNER", "status": "OBSERVED", "count": 3, "note": "fixture"}],
        }


@pytest.fixture
def setup(tmp_path):
    settings = Settings(
        _env_file=None,
        github_client_id="fixture-client",
        github_client_secret="fixture-secret",
        reports_directory=tmp_path,
    )
    adapter, store = Adapter(), SessionStore()
    app = create_app(settings, adapter, store)
    with TestClient(app, base_url="http://127.0.0.1:3000") as client:
        yield client, store, adapter


def signin(client):
    start = client.get("/api/v1/auth/github/start", follow_redirects=False)
    state = parse_qs(urlsplit(start.headers["location"]).query)["state"][0]
    return client.get(
        "/api/v1/auth/github/callback",
        params={"state": state, "code": "fixture-code"},
        follow_redirects=False,
    ), state


def test_success_rotation_logout_and_token_privacy(setup):
    client, store, _ = setup
    first, _ = signin(client)
    assert first.status_code == 303
    cookie = first.headers["set-cookie"]
    assert "HttpOnly" in cookie and "SameSite=lax" in cookie
    original = client.cookies.get("gm_session")
    assert store.get(original).token == TOKEN
    me = client.get("/api/v1/me")
    assert me.json()["user"]["id"] == 42
    assert TOKEN not in me.text and "fixture-secret" not in me.text
    signin(client)
    assert client.cookies.get("gm_session") != original
    assert store.get(original) is None
    csrf = client.get("/api/v1/me").json()["csrf_token"]
    for headers in (
        {},
        {"Origin": "http://evil.example", "X-CSRF-Token": csrf},
        {"Origin": "http://127.0.0.1:3000", "X-CSRF-Token": "wrong"},
    ):
        assert client.post("/api/v1/auth/logout", headers=headers).status_code == 403
    assert (
        client.post(
            "/api/v1/auth/logout", headers={"Origin": "http://127.0.0.1:3000", "X-CSRF-Token": csrf}
        ).status_code
        == 200
    )
    assert client.get("/api/v1/me").status_code == 401


def test_state_replay_wrong_browser_and_cancel(setup):
    client, _, _ = setup
    start = client.get("/api/v1/auth/github/start", follow_redirects=False)
    state = parse_qs(urlsplit(start.headers["location"]).query)["state"][0]
    nonce = client.cookies.get("gm_oauth_browser")
    client.cookies.clear()
    assert (
        client.get(
            "/api/v1/auth/github/callback", params={"state": state, "code": "fixture-code"}
        ).status_code
        == 400
    )
    client.cookies.set("gm_oauth_browser", nonce, path="/api/v1/auth/github")
    response = client.get(
        "/api/v1/auth/github/callback",
        params={"state": state, "error": "access_denied"},
        follow_redirects=False,
    )
    assert response.status_code == 303 and "cancelled" in response.headers["location"]
    assert (
        client.get(
            "/api/v1/auth/github/callback", params={"state": state, "code": "fixture-code"}
        ).status_code
        == 400
    )


def test_session_and_state_expiry():
    now = [100.0]
    store = SessionStore(clock=lambda: now[0], capacity=1)
    state, _ = store.begin("browser", 30)
    with pytest.raises(ValueError):
        store.begin("browser", 30)
    key = store.create({"id": 1}, TOKEN, [], 30)
    now[0] = 130
    assert store.consume(state, "browser") is None
    assert store.get(key) is None
    state, _ = store.begin("browser", 30)
    assert store.consume(state, "wrong") is None
    assert store.consume(state, "browser") is not None
    assert store.consume(state, "browser") is None


def test_cursor_filters_scope_and_cache(setup):
    client, store, adapter = setup
    signin(client)
    first = client.get("/api/v1/repos?limit=1").json()
    assert first["total"] == 3 and first["items"][0]["id"] == 1
    cursor = first["next_cursor"]
    assert (
        client.get("/api/v1/repos", params={"cursor": cursor, "limit": 1}).json()["items"][0]["id"]
        == 2
    )
    for params in (
        {"cursor": cursor, "view": "favorites"},
        {"cursor": cursor + "broken"},
        {"cursor": cursor, "q": "repo-1"},
    ):
        assert client.get("/api/v1/repos", params=params).status_code == 400
    assert client.get("/api/v1/repos?q=repo-4").json()["total"] == 1
    assert client.get("/api/v1/repos?view=favorites").json()["items"][0]["id"] == 3
    assert client.get("/api/v1/repos?view=all").json()["total"] == 4
    assert adapter.calls == 1
    # A cursor copied to a different session has no authority.
    signin(client)
    assert client.get("/api/v1/repos", params={"cursor": cursor}).status_code == 400
    assert store.sessions


def test_report_authenticated_csrf_and_markdown(setup, tmp_path):
    client, _, _ = setup
    assert client.get("/api/v1/pretest/github/report").status_code == 401
    signin(client)
    assert client.post("/api/v1/pretest/github/run").status_code == 403
    csrf = client.get("/api/v1/me").json()["csrf_token"]
    value = client.post(
        "/api/v1/pretest/github/run",
        headers={"Origin": "http://127.0.0.1:3000", "X-CSRF-Token": csrf},
    )
    assert value.status_code == 200
    report = client.get("/api/v1/pretest/github/report")
    assert "text/markdown" in report.headers["content-type"]
    for secret in (TOKEN, "fixture-code", "fixture-secret", "fixture/repo"):
        assert secret not in report.text
    assert "@fixture-user" in report.text and "GitHub numeric ID: 42" in report.text
    assert "BLOCKED" in report.text
    assert len(list(tmp_path.glob("*.md"))) == 1
    assert list(tmp_path.glob("*.md"))[0].stat().st_mode & 0o777 == 0o600


def test_config_fail_closed_and_pkce(tmp_path):
    for values in (
        {"app_env": "production"},
        {"app_origin": "https://example.com"},
        {"app_origin": "http://evil.example"},
        {"app_origin": "http://localhost/path"},
    ):
        with pytest.raises(ValueError):
            Settings(_env_file=None, **values)
    settings = Settings(_env_file=None)
    with TestClient(create_app(settings), base_url="http://127.0.0.1:3000") as client:
        assert client.get("/health").json()["status"] == "ok"
        assert client.get("/api/v1/auth/github/start").status_code == 503
        assert client.get("/health", headers={"host": "attacker.example"}).status_code == 400
    url = OAuthAppAdapter(settings).authorization_url("state", "verifier")
    params = parse_qs(urlsplit(url).query)
    assert params["code_challenge_method"] == ["S256"]
    assert "verifier" not in url
    assert len(params["code_challenge"][0]) == 43


def test_github_auth_failure_invalidates_session(setup):
    client, store, adapter = setup
    signin(client)

    async def denied(token):
        raise GitHubError("reauthorization_required", 401)

    adapter.inventory = denied
    assert client.get("/api/v1/repos").status_code == 401
    assert client.get("/api/v1/me").status_code == 401


def test_changed_numeric_identity_discards_local_authority(setup):
    client, _, adapter = setup
    signin(client)

    async def changed(token):
        return {"identity": {"id": 99}, "repos": [], "coverage": []}

    adapter.inventory = changed
    response = client.get("/api/v1/repos")
    assert response.status_code == 401 and "identity_changed" in response.text
    assert client.get("/api/v1/me").status_code == 401


def test_malformed_cursor_does_not_crash(setup):
    client, _, _ = setup
    signin(client)
    for cursor in (
        "!",
        "a.b",
        "____.broken",
        base64.urlsafe_b64encode(json.dumps([]).encode()).decode() + ".wrong",
    ):
        assert client.get("/api/v1/repos", params={"cursor": cursor}).status_code == 400
