"""Reference additions preserve vocabulary versions, ownership and evidence gates."""

import hashlib

import pytest

from tests.demo.fixtures import USER
from tests.demo.test_corpus import body

pytest_plugins = ["tests.demo.test_corpus"]


def vocabulary(client):
    response = client.get("/api/v1/corpus/registry")
    assert response.status_code == 200, response.text
    return response.json()


def create(client, kind, name, **extra):
    value = {
        "kind": kind,
        "name": name,
        "description": f"Definition for {name}",
        "registry_context": vocabulary(client)["registry_context"],
        **extra,
    }
    response = client.post("/api/v1/corpus/registry/concepts", json=value)
    assert response.status_code == 200, response.text
    return response.json()


def review_body(client, **extra):
    return body(client) | {"registry_context": vocabulary(client)["registry_context"], **extra}


def test_create_all_kinds_assign_persist_export_and_keep_base_immutable(corpus_rig):
    app, client, *_ = corpus_rig
    before = {
        p: hashlib.sha256(p.read_bytes()).hexdigest() for p in app.state.corpus.release.iterdir()
    }
    domain = create(client, "DOMAIN", "Pipeline Systems")["concept"]
    project = create(client, "PROJECT", "Sample Pipeline", domain=domain["id"])["concept"]
    topic = create(client, "TOPIC", "Pipeline Processing", aliases=["ETL work"])["concept"]
    tag = create(client, "TAG", "Sample Runtime")["concept"]
    additions = [project["id"], topic["id"], tag["id"]]
    value = review_body(
        client,
        label_ids=["topic:sql", *additions],
        additional_evidence={
            cid: {"path": "README.md", "quote": "An English data pipeline"} for cid in additions
        },
    )
    saved = client.put("/api/v1/corpus/repos/1/review", json=value)
    assert saved.status_code == 200, saved.text
    assert saved.json()["derived_domains"] == [domain["id"]]
    assert saved.json()["registry_context"]["revision"] == 4
    detail = client.get("/api/v1/corpus/repos/1").json()
    assert set(detail["review"]["label_ids"]) == set(value["label_ids"])
    assert any(c["id"] == project["id"] for c in detail["registry"])
    found = client.get(
        f"/api/v1/corpus/repos?label_basis=reviewed&concept_ids={topic['id']}"
    ).json()
    assert found["total"] == 1
    assert topic["id"] in {c["id"] for c in found["items"][0]["labels"]}
    assert found["items"][0]["derived_domains"] == [domain["id"]]
    summary = client.get("/api/v1/corpus").json()
    project_count = next(c for c in summary["registry"] if c["id"] == project["id"])
    assert (
        project_count["repository_count"] == 0 and project_count["reviewed_repository_count"] == 1
    )
    exported = client.get("/api/v1/corpus/reviews/export").json()
    versions = exported["reference_registry"]["versions"]
    assert [v["registry_context"]["revision"] for v in versions] == [0, 1, 2, 3, 4]
    assert versions[0]["extensions"] == []
    assert [c["id"] for c in versions[1]["extensions"]] == [domain["id"]]
    assert all(hashlib.sha256(p.read_bytes()).hexdigest() == h for p, h in before.items())
    assert not app.state.database.read(f"{USER['id']}:github")["organization"]["concepts"]


def test_draft_accepts_incomplete_new_evidence_but_confirmation_does_not(corpus_rig):
    _, client, *_ = corpus_rig
    tag = create(client, "TAG", "New Runtime")["concept"]
    value = review_body(
        client, label_ids=[tag["id"]], additional_evidence={}, base_review_revision=0
    )
    draft = client.put("/api/v1/corpus/repos/1/draft", json=value)
    assert draft.status_code == 200, draft.text
    assert not draft.json()["stale"] and draft.json()["registry_context"]["revision"] == 1
    value.pop("base_review_revision")
    value["expected_draft_revision"] = 1
    denied = client.put("/api/v1/corpus/repos/1/review", json=value)
    assert denied.status_code == 409 and "exact source quote" in denied.text
    value["additional_evidence"] = {tag["id"]: {"path": "README.md", "quote": "fabricated"}}
    assert client.put("/api/v1/corpus/repos/1/review", json=value).status_code == 409
    value["additional_evidence"][tag["id"]]["quote"] = "Python"
    assert client.put("/api/v1/corpus/repos/1/review", json=value).status_code == 200
    assert client.get("/api/v1/corpus/repos/1").json()["draft"] is None


@pytest.mark.parametrize(
    "name,aliases", [("ＳＱＬ", []), ("New Topic", ["sQl"]), ("New Topic", ["new-topic"])]
)
def test_duplicate_name_aliases_explain_the_conflict(corpus_rig, name, aliases):
    _, client, *_ = corpus_rig
    before = vocabulary(client)
    response = client.post(
        "/api/v1/corpus/registry/concepts",
        json={
            "kind": "TOPIC",
            "name": name,
            "description": "A useful topic",
            "aliases": aliases,
            "registry_context": before["registry_context"],
        },
    )
    assert response.status_code == 409
    assert response.json()["code"] == "CORPUS_REGISTRY_NAME_CONFLICT"
    assert response.json()["conflicts"][0]["term"]
    if name == "ＳＱＬ" or aliases == ["sQl"]:
        assert response.json()["conflicts"][0]["existing"]["id"] == "topic:sql"
    assert vocabulary(client) == before


def test_stale_registry_cannot_create_or_save_and_old_history_is_preserved(corpus_rig):
    app, client, *_ = corpus_rig
    original = client.put("/api/v1/corpus/repos/1/review", json=body(client)).json()
    initial = vocabulary(client)["registry_context"]
    create(client, "DOMAIN", "New Area")
    stale = body(client) | {"expected_revision": 1, "registry_context": initial}
    denied = client.put("/api/v1/corpus/repos/1/review", json=stale)
    assert denied.status_code == 409 and denied.json()["code"] == "CORPUS_REGISTRY_CONFLICT"
    assert denied.json()["registry"]["registry_context"]["revision"] == 1
    assert client.get("/api/v1/corpus/repos/1").json()["review"] == original
    stale.update(base_review_revision=1, expected_revision=0)
    assert client.put("/api/v1/corpus/repos/1/draft", json=stale).status_code == 409
    assert (
        client.post(
            "/api/v1/corpus/registry/concepts",
            json={
                "kind": "TAG",
                "name": "Stale Tag",
                "description": "A stale write",
                "registry_context": initial,
            },
        ).json()["code"]
        == "CORPUS_REGISTRY_CONFLICT"
    )
    fresh = review_body(client, expected_revision=1, notes="Reviewed using the expanded vocabulary")
    saved = client.put("/api/v1/corpus/repos/1/review", json=fresh).json()
    assert saved["history"] == [{key: value for key, value in original.items() if key != "history"}]
    assert saved["history"][0]["registry_context"] == initial
    state = app.state.database.read(f"{USER['id']}:ground-truth")
    assert len(state["reference_registries"]["test-release"]["versions"]) == 1


def test_owner_isolation_auth_csrf_and_valid_domain_parent(corpus_rig):
    app, client, sessions, *_ = corpus_rig
    topic = create(client, "TOPIC", "Owner's Topic")["concept"]
    first = vocabulary(client)
    for kind, parent in [("PROJECT", None), ("PROJECT", "topic:sql"), ("TOPIC", "domain:data")]:
        denied = client.post(
            "/api/v1/corpus/registry/concepts",
            json={
                "kind": kind,
                "name": "Invalid Parent",
                "description": "Check parent",
                "domain": parent,
                "registry_context": first["registry_context"],
            },
        )
        assert denied.status_code == 409
    client.headers["X-CSRF-Token"] = "wrong"
    assert (
        client.post(
            "/api/v1/corpus/registry/concepts",
            json={
                "kind": "TAG",
                "name": "Blocked",
                "description": "No write",
                "registry_context": first["registry_context"],
            },
        ).status_code
        == 403
    )
    other = sessions.create({"id": 88, "login": "other"}, "fixture", ["repo"], 3600)
    client.cookies.set("gm_session", other)
    client.headers["X-CSRF-Token"] = sessions.get(other).csrf_token
    second = vocabulary(client)
    assert second["registry_context"]["revision"] == 0
    assert topic["id"] not in {c["id"] for c in second["registry"]}
    wrong_id = review_body(client, label_ids=[topic["id"]])
    assert client.put("/api/v1/corpus/repos/1/review", json=wrong_id).status_code == 409
    assert client.get("/api/v1/corpus/reviews/export").json()["reviews"] == []
    assert not app.state.database.read("88:github")["organization"]["concepts"]
    client.cookies.clear()
    assert client.get("/api/v1/corpus/registry").status_code == 401


def test_registry_changes_during_source_validation_are_fenced_at_commit(corpus_rig, monkeypatch):
    app, client, *_ = corpus_rig
    tag = create(client, "TAG", "Race Runtime")["concept"]
    value = review_body(
        client,
        label_ids=[tag["id"]],
        additional_evidence={tag["id"]: {"path": "README.md", "quote": "Python"}},
    )
    source = app.state.corpus.source
    attempts = 0

    def racing_source(*args, **kwargs):
        nonlocal attempts
        attempts += 1
        result = source(*args, **kwargs)
        if attempts == 2:
            create(client, "DOMAIN", "Concurrent Domain")
        return result

    monkeypatch.setattr(app.state.corpus, "source", racing_source)
    result = client.put("/api/v1/corpus/repos/1/review", json=value)
    assert result.status_code == 409 and result.json()["code"] == "CORPUS_REGISTRY_CONFLICT"
    assert client.get("/api/v1/corpus/repos/1").json()["review"] is None


def test_legacy_records_and_stale_drafts_remain_inspectable(corpus_rig):
    app, client, *_ = corpus_rig
    saved = client.put("/api/v1/corpus/repos/1/review", json=body(client)).json()

    def legacy(state):
        state["reference_reviews"]["test-release"]["1"].pop("registry_context")

    app.state.database.mutate(f"{USER['id']}:ground-truth", legacy)
    old = client.get("/api/v1/corpus/repos/1").json()["review"]
    draft_value = review_body(client, expected_revision=0, base_review_revision=1)
    assert client.put("/api/v1/corpus/repos/1/draft", json=draft_value).status_code == 200
    create(client, "TAG", "Later Runtime")
    detail = client.get("/api/v1/corpus/repos/1").json()
    assert detail["review"] == old
    assert detail["review_registry_context"] == saved["registry_context"]
    assert detail["draft"]["stale"] and "vocabulary" in " ".join(detail["draft"]["stale_reasons"])
    exported = client.get("/api/v1/corpus/reviews/export").json()
    assert exported["reviews"] == [old]
    assert (
        exported["reference_registry"]["versions"][0]["registry_context"]
        == saved["registry_context"]
    )
