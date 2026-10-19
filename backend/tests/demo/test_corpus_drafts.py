"""Unfinished review buffers never become gold; final writes fence both versions."""

import pytest

from app.demo.store import Store
from tests.demo.test_corpus import body

pytest_plugins = ["tests.demo.test_corpus"]


def draft_body(client):
    value = body(client)
    value.update(
        base_review_revision=0,
        status="HUMAN_CONFIRMED",
        purpose="",
        label_ids=["topic:sql", "tag:python"],
        dimensions={"projects": False, "topics": False, "tags": False},
        additional_evidence={"tag:python": {"path": "", "quote": "Unfinished quote"}},
    )
    return value


def test_incomplete_draft_persists_without_review_counts_or_export(corpus_rig):
    app, client, *_ = corpus_rig
    value = draft_body(client)
    saved = client.put("/api/v1/corpus/repos/1/draft", json=value)
    assert saved.status_code == 200, saved.text
    assert saved.json()["kind"] == "INCOMPLETE_DRAFT"
    assert saved.json()["revision"] == 1 and not saved.json()["stale"]
    # Even a draft's intended status cannot create a human confirmation.
    summary = client.get("/api/v1/corpus").json()
    assert summary["drafts"] == 1 and summary["reviewed"] == summary["human_confirmed"] == 0
    assert client.get("/api/v1/corpus/reviews/export").json()["reviews"] == []
    detail = client.get("/api/v1/corpus/repos/1").json()
    assert detail["review"] is None and detail["draft"]["purpose"] == ""
    row = client.get("/api/v1/corpus/repos?q=public/repo-1&limit=1").json()["items"][0]
    assert row["has_draft"] and row["review_status"] == "PROPOSED"
    state = Store(app.state.database.path).read("9009:ground-truth")
    assert (
        state["reference_drafts"]["test-release"]["1"]["additional_evidence"]
        == value["additional_evidence"]
    )


def test_draft_is_owner_scoped_and_requires_csrf(corpus_rig):
    _, client, sessions, *_ = corpus_rig
    value = draft_body(client)
    token = client.headers["X-CSRF-Token"]
    client.headers["X-CSRF-Token"] = "wrong"
    assert client.put("/api/v1/corpus/repos/1/draft", json=value).status_code == 403
    client.headers["X-CSRF-Token"] = token
    assert client.put("/api/v1/corpus/repos/1/draft", json=value).status_code == 200
    other = sessions.create({"id": 88, "login": "other"}, "fixture", ["repo"], 3600)
    client.cookies.set("gm_session", other)
    assert client.get("/api/v1/corpus/repos/1/draft").json() is None
    assert client.get("/api/v1/corpus/repos/1").json()["draft"] is None
    assert client.get("/api/v1/corpus").json()["drafts"] == 0


def test_concurrent_draft_cannot_be_overwritten_or_consumed(corpus_rig):
    _, client, *_ = corpus_rig
    value = draft_body(client)
    assert client.put("/api/v1/corpus/repos/1/draft", json=value).status_code == 200
    value.update(expected_revision=1, notes="Newer tab buffer")
    assert client.put("/api/v1/corpus/repos/1/draft", json=value).json()["revision"] == 2
    stale = client.put("/api/v1/corpus/repos/1/draft", json=value)
    assert stale.status_code == 409
    assert stale.json()["code"] == "CORPUS_DRAFT_CONFLICT"
    assert stale.json()["current_draft"]["notes"] == "Newer tab buffer"
    final = body(client) | {"expected_draft_revision": 1}
    denied = client.put("/api/v1/corpus/repos/1/review", json=final)
    assert denied.status_code == 409 and denied.json()["code"] == "CORPUS_DRAFT_CONFLICT"
    assert client.get("/api/v1/corpus").json()["human_confirmed"] == 0
    assert client.get("/api/v1/corpus/repos/1/draft").json()["revision"] == 2
    final["expected_draft_revision"] = 2
    assert client.put("/api/v1/corpus/repos/1/review", json=final).status_code == 200
    assert client.get("/api/v1/corpus/repos/1/draft").json() is None
    assert client.get("/api/v1/corpus").json()["human_confirmed"] == 1


def test_stale_final_review_does_not_clear_the_saved_draft(corpus_rig):
    _, client, *_ = corpus_rig
    draft = draft_body(client)
    assert client.put("/api/v1/corpus/repos/1/draft", json=draft).status_code == 200
    # An older client does not know which draft to consume and must preserve it.
    assert client.put("/api/v1/corpus/repos/1/review", json=body(client)).status_code == 200
    saved = client.get("/api/v1/corpus/repos/1").json()["draft"]
    assert saved["stale"] and "newer final review" in saved["stale_reasons"][0]
    denied = client.put("/api/v1/corpus/repos/1/draft", json=draft | {"expected_revision": 1})
    assert denied.status_code == 409 and denied.json()["code"] == "CORPUS_REVIEW_CONFLICT"
    assert denied.json()["current_review"]["revision"] == 1
    final = body(client) | {"expected_draft_revision": 1}
    assert client.put("/api/v1/corpus/repos/1/review", json=final).status_code == 409
    assert client.get("/api/v1/corpus/repos/1/draft").json()["revision"] == 1


def test_draft_does_not_weaken_final_quote_or_source_integrity(corpus_rig):
    _, client, _, source, *_ = corpus_rig
    draft = draft_body(client)
    draft["additional_evidence"]["tag:python"] = {"path": "README.md", "quote": "Unfinished quote"}
    assert client.put("/api/v1/corpus/repos/1/draft", json=draft).status_code == 200
    final = body(client) | {
        "label_ids": draft["label_ids"],
        "additional_evidence": draft["additional_evidence"],
        "expected_draft_revision": 1,
    }
    assert client.put("/api/v1/corpus/repos/1/review", json=final).status_code == 409
    assert client.get("/api/v1/corpus/repos/1/draft").json()["revision"] == 1
    source.write_text("changed source")
    assert (
        client.put(
            "/api/v1/corpus/repos/1/draft", json=draft | {"expected_revision": 1}
        ).status_code
        == 409
    )


@pytest.mark.parametrize(
    "patch",
    [
        {"label_ids": ["domain:data"]},
        {"label_ids": ["unknown"]},
        {"label_ids": ["topic:sql", "topic:sql"]},
        {"manifest_sha256": "0" * 64},
    ],
)
def test_draft_keeps_canonical_and_release_bindings(corpus_rig, patch):
    _, client, *_ = corpus_rig
    assert (
        client.put("/api/v1/corpus/repos/1/draft", json=draft_body(client) | patch).status_code
        == 409
    )
    assert client.get("/api/v1/corpus").json()["drafts"] == 0


def test_multi_facet_or_within_kind_and_across_kinds_and_explicit_basis(corpus_rig):
    app, client, *_ = corpus_rig
    corpus = app.state.corpus
    corpus.load()
    corpus.registry["topic:other"] = {
        "id": "topic:other",
        "kind": "TOPIC",
        "name": "Other",
        "domain": None,
    }
    corpus.proposals[2]["labels"] = [
        {"id": "topic:other", "name": "Other", "kind": "TOPIC", "evidence": []}
    ]
    corpus.proposals[3]["labels"].append(
        {"id": "tag:python", "name": "Python", "kind": "TAG", "evidence": []}
    )
    topics = [("concept_ids", "topic:sql"), ("concept_ids", "topic:other")]
    assert client.get("/api/v1/corpus/repos", params=topics).json()["total"] == 600
    both = client.get(
        "/api/v1/corpus/repos", params=topics + [("concept_ids", "tag:python")]
    ).json()
    assert both["total"] == 1 and both["items"][0]["repository_id"] == 3
    assert client.put("/api/v1/corpus/repos/1/review", json=body(client)).status_code == 200
    query = {"concept_ids": "topic:sql", "label_basis": "reviewed"}
    assert client.get("/api/v1/corpus/repos", params=query).json()["total"] == 1
    assert client.get("/api/v1/corpus/repos?concept=topic:sql").json()["total"] == 599
    assert client.get("/api/v1/corpus/repos?concept_ids=unknown").status_code == 409
    assert client.get("/api/v1/corpus/repos?concept_ids=domain:data").status_code == 409
    assert (
        client.get("/api/v1/corpus/repos?concept_ids=topic:sql&concept_ids=topic:sql").status_code
        == 409
    )


def test_next_seek_does_not_skip_at_a_page_boundary_when_confirmation_removes_row(
    corpus_rig, monkeypatch
):
    app, client, *_ = corpus_rig
    first = client.get("/api/v1/corpus/repos?status=PROPOSED&limit=25").json()["items"]
    second = client.get("/api/v1/corpus/repos?status=PROPOSED&offset=25").json()["items"]
    current, successor = first[-1]["repository_id"], second[0]["repository_id"]
    # The compact fixture has one physical dossier. Give this boundary case the
    # same validated source packet; production identity checks remain unchanged.
    packet = app.state.corpus.dossier(1)
    monkeypatch.setattr(app.state.corpus, "dossier", lambda rid: {**packet, "numeric_id": rid})
    before = client.get(f"/api/v1/corpus/repos/{current}/neighbors?status=PROPOSED").json()
    assert before["next"]["repository_id"] == successor and before["next_index"] == 25
    assert (
        client.put(f"/api/v1/corpus/repos/{current}/review", json=body(client)).status_code == 200
    )
    after = client.get(f"/api/v1/corpus/repos/{current}/neighbors?status=PROPOSED").json()
    assert after["next"]["repository_id"] == successor and after["next_index"] == 24
    assert after["total"] == 599
    assert client.get("/api/v1/corpus/repos/601/neighbors").status_code == 404


def test_next_seek_obeys_filters_and_reports_end_without_wrapping(corpus_rig):
    _, client, *_ = corpus_rig
    matches = client.get("/api/v1/corpus/repos?q=public/repo-12&limit=100").json()["items"]
    first = matches[0]["repository_id"]
    last = matches[-1]["repository_id"]
    start = client.get(f"/api/v1/corpus/repos/{first}/neighbors?q=public/repo-12").json()
    end = client.get(f"/api/v1/corpus/repos/{last}/neighbors?q=public/repo-12").json()
    assert start["previous"] is None and start["previous_index"] is None
    assert start["next"]["repository_id"] == matches[1]["repository_id"]
    assert end["next"] is None and end["next_index"] is None
    assert end["previous"]["repository_id"] == matches[-2]["repository_id"]
