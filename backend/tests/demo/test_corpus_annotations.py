"""Pilot proposals inform explicit, owner-scoped reviews; they never become gold."""

import pytest

from tests.demo.test_corpus import body

pytest_plugins = ["tests.demo.test_corpus"]


@pytest.fixture
def pilot(corpus_rig, monkeypatch):
    app, client, *_ = corpus_rig
    record = {
        "repository_id": 1,
        "full_name": "public/repo-1",
        "sampling_domain": "domain-0",
        "annotations": {"a": {"purpose": "A cited proposal"}, "b": {"purpose": "Another proposal"}},
        "comparison": {
            "review_band": "AMBER",
            "agreed_ids": [],
            "a_only_ids": ["topic:sql"],
            "b_only_ids": [],
        },
        "audit_selection": "RISK_SELECTED",
    }
    value = {
        "state": "READY",
        "status": "INDEPENDENT_PROPOSALS_AWAITING_HUMAN_REVIEW",
        "summary": {
            "repositories": 1,
            "human_queue": {"RISK_SELECTED": 1},
            "review_bands": {"AMBER": 1},
        },
        "provenance": {"mode": "CODEX_AGENTS_OFFLINE", "external_api_calls": 0},
        "sidecar_manifest_sha256": "b" * 64,
        "records": {"1": record},
    }
    monkeypatch.setattr(app.state.corpus, "annotation_pilot", lambda: value)
    return client, value


def test_proposals_are_visible_without_creating_human_records(pilot):
    client, value = pilot
    summary = client.get("/api/v1/corpus").json()
    assert summary["human_confirmed"] == summary["reviewed"] == 0
    view = summary["annotation_pilot"]
    assert view["queue"][0]["audit_selection"] == "RISK_SELECTED"
    assert view["queue"][0]["review_status"] == "PROPOSED"
    detail = client.get("/api/v1/corpus/repos/1").json()
    assert detail["annotation_pilot"]["record"] == value["records"]["1"]
    assert detail["review"] is None
    assert detail["proposal"]["purpose"] == "A data pipeline"


def test_pilot_context_binding_cannot_be_forged_or_reused_after_change(pilot):
    client, value = pilot
    payload = body(client) | {"annotation_pilot_sha256": "c" * 64}
    response = client.put("/api/v1/corpus/repos/1/review", json=payload)
    assert response.status_code == 409
    assert client.get("/api/v1/corpus").json()["human_confirmed"] == 0
    payload["annotation_pilot_sha256"] = value["sidecar_manifest_sha256"]
    value["state"] = "INVALID"
    assert client.put("/api/v1/corpus/repos/1/review", json=payload).status_code == 409


def test_explicit_human_save_binds_pilot_and_counts_only_that_users_decisions(pilot):
    client, value = pilot
    payload = body(client) | {"annotation_pilot_sha256": value["sidecar_manifest_sha256"]}
    response = client.put("/api/v1/corpus/repos/1/review", json=payload)
    assert response.status_code == 200, response.text
    assert response.json()["annotation_pilot_sha256"] == value["sidecar_manifest_sha256"]
    summary = client.get("/api/v1/corpus").json()["annotation_pilot"]
    assert summary["confirmed_by_you"] == summary["reviewed_by_you"] == 1
    assert summary["queue"][0]["review_status"] == "HUMAN_CONFIRMED"
    # A new revision remains a human action; the original pilot and proposals do not change.
    payload.update(expected_revision=1, status="UNRESOLVED")
    saved = client.put("/api/v1/corpus/repos/1/review", json=payload).json()
    assert saved["history"][0]["annotation_pilot_sha256"] == value["sidecar_manifest_sha256"]
    assert client.get("/api/v1/corpus").json()["annotation_pilot"]["confirmed_by_you"] == 0


def test_existing_review_flow_does_not_require_an_annotation_pilot(corpus_rig):
    _, client, *_ = corpus_rig
    assert client.get("/api/v1/corpus").json()["annotation_pilot"]["state"] == "NOT_RUN"
    response = client.put("/api/v1/corpus/repos/1/review", json=body(client))
    assert response.status_code == 200
    assert response.json()["annotation_pilot_sha256"] is None


def test_multiple_projects_topics_and_tags_keep_all_derived_domains(corpus_rig):
    app, client, *_ = corpus_rig
    corpus = app.state.corpus
    corpus.load()
    # A deliberately constructed multi-initiative review tests the many-to-many contract.
    for ident, kind, parent in (
        ("domain:other", "DOMAIN", None),
        ("project:one", "PROJECT", "domain:data"),
        ("project:two", "PROJECT", "domain:other"),
        ("topic:other", "TOPIC", None),
        ("tag:other", "TAG", None),
    ):
        corpus.registry[ident] = {
            "id": ident,
            "kind": kind,
            "name": ident,
            "description": "Synthetic contract case",
            "domain": parent,
        }
    payload = body(client)
    payload["label_ids"] = [
        "project:one",
        "project:two",
        "topic:sql",
        "topic:other",
        "tag:python",
        "tag:other",
    ]
    payload["additional_evidence"] = {
        ident: {"path": "README.md", "quote": "An English data pipeline"}
        for ident in payload["label_ids"]
        if ident != "topic:sql"
    }
    saved = client.put("/api/v1/corpus/repos/1/review", json=payload)
    assert saved.status_code == 200, saved.text
    assert set(saved.json()["label_ids"]) == set(payload["label_ids"])
    assert saved.json()["derived_domains"] == ["domain:data", "domain:other"]


def test_pinned_metadata_is_distinct_and_new_labels_require_an_exact_quote(pilot, monkeypatch):
    from hashlib import sha256

    client, value = pilot
    text = '{"primary_language": "Python"}\n'
    metadata = {
        "path": "@github-metadata.json",
        "role": "GITHUB_METADATA",
        "text": text,
        "bytes": len(text.encode()),
        "sha256": sha256(text.encode()).hexdigest(),
    }
    value["records"]["1"]["annotations"]["a"]["source_reading"] = [
        {"path": metadata["path"], "complete": True}
    ]
    monkeypatch.setattr(
        "app.demo.annotation_pilot.source_packet", lambda *args: {"sources": [metadata]}
    )
    source = client.get("/api/v1/corpus/repos/1/source?path=@github-metadata.json").json()
    assert source["role"] == "GITHUB_METADATA" and source["text"] == text
    detail = client.get("/api/v1/corpus/repos/1").json()
    assert detail["files"][-1]["role"] == "GITHUB_METADATA"
    payload = body(client) | {
        "label_ids": ["topic:sql", "tag:python"],
        "additional_evidence": {"tag:python": {"path": metadata["path"], "quote": "Rust"}},
    }
    assert client.put("/api/v1/corpus/repos/1/review", json=payload).status_code == 409
    payload["additional_evidence"]["tag:python"]["quote"] = '"primary_language": "Python"'
    saved = client.put("/api/v1/corpus/repos/1/review", json=payload)
    assert saved.status_code == 200, saved.text
    assert saved.json()["additional_evidence"]["tag:python"]["path"] == metadata["path"]
