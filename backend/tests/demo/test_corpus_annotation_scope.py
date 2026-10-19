"""A/B review pagination and continuation must stay within the validated pilot."""

import copy

import pytest

from tests.demo.fixtures import USER
from tests.demo.test_corpus import body

pytest_plugins = ["tests.demo.test_corpus"]


@pytest.fixture
def scoped_pilot(corpus_rig, monkeypatch):
    app, client, *_ = corpus_rig
    # Include repository 1 (the fixture with a verifiable dossier) and deliberately
    # noncontiguous IDs so accidentally taking the first page cannot pass.
    ids = [1, *range(102, 131)]
    pilot = {
        "state": "READY",
        "records": {
            str(rid): {
                "repository_id": rid,
                "audit_selection": "RISK_SELECTED" if index < 20 else None,
            }
            for index, rid in enumerate(ids)
        },
    }
    monkeypatch.setattr(app.state.corpus, "annotation_pilot", lambda: pilot)
    return app, client, pilot


def test_scope_filters_before_pagination_and_composes_with_filters(scoped_pilot):
    _, client, pilot = scoped_pilot
    assert client.get("/api/v1/corpus/repos").json()["total"] == 600
    first = client.get("/api/v1/corpus/repos?annotation_scope=pilot").json()
    second = client.get("/api/v1/corpus/repos?annotation_scope=pilot&offset=25").json()
    assert first["total"] == second["total"] == 30
    assert len(first["items"]) == 25 and len(second["items"]) == 5
    assert {r["repository_id"] for r in first["items"] + second["items"]} == {
        r["repository_id"] for r in pilot["records"].values()
    }
    queue = client.get("/api/v1/corpus/repos?annotation_scope=initial_queue").json()
    assert queue["total"] == 20 and queue["annotation_scope"] == "initial_queue"
    assert {r["repository_id"] for r in queue["items"]} == {
        r["repository_id"] for r in pilot["records"].values() if r["audit_selection"]
    }
    assert (
        client.get(
            "/api/v1/corpus/repos?annotation_scope=pilot&q=public/repo-102&domain=domain-1"
        ).json()["total"]
        == 1
    )
    assert (
        client.get("/api/v1/corpus/repos?annotation_scope=pilot&domain=domain-9").json()["total"]
        == 0
    )


def test_confirm_next_stays_in_pilot_even_when_current_leaves_status_filter(scoped_pilot):
    _, client, _ = scoped_pilot
    for scope, total in (("initial_queue", 20), ("pilot", 30)):
        value = client.get(
            f"/api/v1/corpus/repos/1/neighbors?annotation_scope={scope}&status=PROPOSED"
        ).json()
        assert value["previous"] is None
        assert value["next"]["repository_id"] == 102 and value["total"] == total
    saved = client.put("/api/v1/corpus/repos/1/review", json=body(client))
    assert saved.status_code == 200, saved.text
    value = client.get(
        "/api/v1/corpus/repos/1/neighbors?annotation_scope=initial_queue&status=PROPOSED"
    ).json()
    assert value["next"]["repository_id"] == 102
    assert value["next_index"] == 0 and value["total"] == 19
    assert (
        client.get("/api/v1/corpus/repos?annotation_scope=pilot&status=HUMAN_CONFIRMED").json()[
            "total"
        ]
        == 1
    )


@pytest.mark.parametrize("state", ["NOT_RUN", "PARTIAL", "INVALID"])
def test_unavailable_sidecar_is_explicit_and_all_corpus_remains_browsable(scoped_pilot, state):
    app, client, pilot = scoped_pilot
    pilot["state"] = state
    assert client.get("/api/v1/corpus/repos").json()["total"] == 600
    for suffix in ("", "/1/neighbors"):
        denied = client.get(f"/api/v1/corpus/repos{suffix}?annotation_scope=pilot")
        assert denied.status_code == 409 and "unavailable" in denied.text
    with pytest.raises(ValueError, match="Choose all"):
        app.state.corpus.search(f"{USER['id']}:ground-truth", annotation_scope="unknown")
    assert client.get("/api/v1/corpus/repos?annotation_scope=unknown").status_code == 422


def test_scope_browsing_is_read_only(scoped_pilot):
    app, client, _ = scoped_pilot
    workspace = f"{USER['id']}:ground-truth"
    before = copy.deepcopy(app.state.database.read(workspace))
    for scope in ("all", "pilot", "initial_queue"):
        assert client.get(f"/api/v1/corpus/repos?annotation_scope={scope}").status_code == 200
        assert (
            client.get(f"/api/v1/corpus/repos/1/neighbors?annotation_scope={scope}").status_code
            == 200
        )
    assert app.state.database.read(workspace) == before
