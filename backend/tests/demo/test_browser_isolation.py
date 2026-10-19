"""Fixture entrypoints must not impersonate the normal application."""

import pytest
from fastapi.testclient import TestClient

from tests.demo.corpus_server import app as corpus_app
from tests.demo.server import app


@pytest.mark.parametrize("port", [3000, 8000])
@pytest.mark.parametrize("fixture_app", [app, corpus_app], ids=["main", "corpus"])
def test_fixture_server_rejects_normal_app_ports_before_authentication(port, fixture_app):
    client = TestClient(fixture_app, base_url=f"http://127.0.0.1:{port}")
    before = len(fixture_app.state.sessions.sessions)
    assert client.get("/api/v1/auth/github/start", follow_redirects=False).status_code == 503
    assert client.post("/api/v1/test/login", json={"id": 9171}).status_code == 503
    assert len(fixture_app.state.sessions.sessions) == before


@pytest.mark.parametrize(
    "fixture_app,port,origin", [(app, 8016, 3016), (corpus_app, 8015, 3015)], ids=["main", "corpus"]
)
def test_fixture_server_uses_only_its_explicit_test_origin(fixture_app, port, origin):
    client = TestClient(fixture_app, base_url=f"http://127.0.0.1:{port}")
    response = client.get("/api/v1/pretest/config")
    assert response.status_code == 200
    assert response.json()["callback_url"].startswith(f"http://127.0.0.1:{origin}/")
