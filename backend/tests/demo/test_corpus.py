import hashlib
import json

import pytest
from fastapi.testclient import TestClient

from app.auth.sessions import SessionStore
from app.demo.corpus import merged_labels
from app.demo.store import Store
from app.local import LocalSettings, create_local_app
from tests.demo.fixtures import USER, Adapter


def write(path, value, lines=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(v) for v in value) + "\n" if lines else json.dumps(value))
    raw = path.read_bytes()
    return {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


@pytest.fixture
def corpus_rig(tmp_path):
    root = tmp_path
    base = root / "docs/validation/private/corpus-600-v2"
    release = base / "release"
    source = base / "sources/1" / ("a" * 40) / "README.md"
    source.parent.mkdir(parents=True)
    source.write_text(
        "# Sample\nAn English data pipeline with SQL and Python.\n<script>untrusted()</script>\n"
    )
    raw = source.read_bytes()
    file = {
        "path": "README.md",
        "local_path": str(source.relative_to(root)),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "role": "README",
    }
    dossier = base / "shards/a/data/records/1.local.json"
    binding = write(
        dossier,
        {
            "numeric_id": 1,
            "private": False,
            "commit": "a" * 40,
            "readme": file,
            "supporting_files": [],
            "v2_eligibility": {"decision": "RETAIN"},
        },
    )
    registry = {
        "domain:data": {
            "id": "domain:data",
            "kind": "DOMAIN",
            "name": "Data",
            "description": "Data systems",
            "domain": None,
        },
        "topic:sql": {
            "id": "topic:sql",
            "kind": "TOPIC",
            "name": "SQL",
            "description": "Querying",
            "domain": None,
        },
        "tag:python": {
            "id": "tag:python",
            "kind": "TAG",
            "name": "Python",
            "description": "Technology",
            "domain": None,
        },
    }
    inventory, labels = [], []
    for rid in range(1, 601):
        inventory.append(
            {
                "repository_id": rid,
                "sampling_domain": "domain-" + str((rid - 1) // 60),
                "full_name": f"public/repo-{rid}",
                "description": "English evidence",
                "url": f"https://github.com/public/repo-{rid}",
                "commit": "a" * 40,
                "dossier_path": str(dossier.relative_to(root)),
            }
        )
        labels.append(
            {
                "repository_id": rid,
                "purpose": "A data pipeline",
                "derived_domains": [],
                "conflicts": [],
                "labels": [
                    {
                        "id": "topic:sql",
                        "name": "SQL",
                        "kind": "TOPIC",
                        "evidence": [{"path": "README.md", "quote": "SQL"}],
                    }
                ],
            }
        )
    files = {
        name: write(release / name, value, lines)
        for name, value, lines in (
            ("inventory.jsonl", inventory, True),
            ("labels.proposed.jsonl", labels, True),
            ("registry.proposed.json", registry, False),
        )
    }
    write(
        release / "manifest.local.json",
        {
            "release_id": "test-release",
            "repositories": 600,
            "status": "PROPOSED_REFERENCES_NOT_GOLD",
            "release_files": files,
            "sources_and_dossiers_sha256": {str(dossier.relative_to(root)): binding["sha256"]},
        },
    )
    sessions = SessionStore()
    cookie = sessions.create(USER, "fixture-only", ["repo"], 3600)
    app = create_local_app(
        LocalSettings(),
        adapter=Adapter(),
        sessions=sessions,
        db_path=root / "app.sqlite3",
        corpus_release=release,
    )
    app.state.corpus.root = root.resolve()
    client = TestClient(app, base_url="http://127.0.0.1:8000")
    client.cookies.set("gm_session", cookie)
    client.headers.update(
        {"Origin": "http://127.0.0.1:3000", "X-CSRF-Token": sessions.get(cookie).csrf_token}
    )
    return app, client, sessions, source, dossier


def body(client):
    detail = client.get("/api/v1/corpus/repos/1").json()
    return {
        "release_id": detail["release_id"],
        "manifest_sha256": detail["manifest_sha256"],
        "expected_revision": 0,
        "status": "HUMAN_CONFIRMED",
        "purpose": "A data pipeline",
        "label_ids": ["topic:sql"],
        "dimensions": {"projects": True, "topics": True, "tags": True},
        "notes": "Inspected saved evidence",
    }


def test_authenticated_browse_source_and_collection_isolation(corpus_rig):
    app, client, _, _, _ = corpus_rig
    response = client.get("/api/v1/corpus?collection=ground-truth")
    assert response.status_code == 200
    assert response.json()["total"] == 600
    assert client.post("/api/v1/corpus/open").status_code == 200
    state = app.state.database.read(str(USER["id"]) + ":ground-truth")
    assert state["reference_dataset"]["release_id"] == "test-release"
    assert not state["organization"]["concepts"] and not state["organization"]["edges"]
    assert client.get("/api/v1/corpus/repos?concept=topic:sql").json()["total"] == 600
    assert client.get("/api/v1/corpus/repos?domain=domain-1").json()["total"] == 60
    assert client.get("/api/v1/corpus/repos?concept=tag:python").json()["total"] == 0
    source = client.get("/api/v1/corpus/repos/1/source?path=README.md").json()
    assert "<script>untrusted()</script>" in source["text"]  # Plain JSON, never rendered as HTML.
    assert client.get("/api/v1/corpus/repos/1/source?path=../../app.sqlite3").status_code == 404
    assert client.get("/api/v1/corpus/repos/601").status_code == 404
    assert client.post("/api/v1/sync?collection=ground-truth").status_code == 422
    assert not app.state.database.read(str(USER["id"]) + ":github")["core"]["repos"]
    client.cookies.clear()
    assert client.get("/api/v1/corpus").status_code == 401


def test_review_persistence_revision_history_owner_and_csrf(corpus_rig):
    app, client, sessions, _, _ = corpus_rig
    value = body(client)
    client.headers["X-CSRF-Token"] = "wrong"
    assert client.put("/api/v1/corpus/repos/1/review", json=value).status_code == 403
    client.headers["X-CSRF-Token"] = sessions.get(client.cookies["gm_session"]).csrf_token
    response = client.put("/api/v1/corpus/repos/1/review", json=value)
    assert response.status_code == 200, response.text
    assert client.get("/api/v1/corpus").json()["human_confirmed"] == 1
    assert client.put("/api/v1/corpus/repos/1/review", json=value).status_code == 409
    value.update(expected_revision=1, status="UNRESOLVED", notes="Need additional evidence")
    assert client.put("/api/v1/corpus/repos/1/review", json=value).json()["revision"] == 2
    restarted = Store(app.state.database.path)
    saved = restarted.read(str(USER["id"]) + ":ground-truth")["reference_reviews"]["test-release"][
        "1"
    ]
    assert saved["history"][0]["status"] == "HUMAN_CONFIRMED"
    assert saved["unlisted_labels"] == "UNKNOWN_NOT_NEGATIVE"
    assert client.get("/api/v1/corpus/reviews/export").json()["reviews"][0]["revision"] == 2
    other = sessions.create({"id": 88, "login": "other"}, "fixture-only", ["repo"], 3600)
    client.cookies.set("gm_session", other)
    assert client.get("/api/v1/corpus").json()["reviewed"] == 0
    assert client.get("/api/v1/corpus/repos/1").json()["review"] is None


def test_added_labels_need_real_evidence_and_complete_confirmation(corpus_rig):
    _, client, _, _, _ = corpus_rig
    value = body(client)
    value["dimensions"]["tags"] = False
    assert client.put("/api/v1/corpus/repos/1/review", json=value).status_code == 409
    value["dimensions"]["tags"] = True
    value["label_ids"].append("tag:python")
    assert client.put("/api/v1/corpus/repos/1/review", json=value).status_code == 409
    value["additional_evidence"] = {"tag:python": {"path": "README.md", "quote": "Invented quote"}}
    assert client.put("/api/v1/corpus/repos/1/review", json=value).status_code == 409
    value["additional_evidence"]["tag:python"]["quote"] = (
        "An English data pipeline with SQL and Python."
    )
    assert client.put("/api/v1/corpus/repos/1/review", json=value).status_code == 200
    value["label_ids"] = ["domain:data"]
    assert client.put("/api/v1/corpus/repos/1/review", json=value).status_code == 409


def test_source_and_dossier_integrity_block_modified_evidence(corpus_rig):
    _, client, _, source, dossier = corpus_rig
    value = body(client)
    source.write_text("Replaced after release")
    assert client.get("/api/v1/corpus/repos/1/source?path=README.md").status_code == 409
    dossier.write_text("{}")
    assert client.get("/api/v1/corpus/repos/1").status_code == 409
    assert client.put("/api/v1/corpus/repos/1/review", json=value).status_code == 409


def test_release_integrity_and_stale_manifest_block_review(corpus_rig):
    app, client, _, _, _ = corpus_rig
    value = body(client)
    value["manifest_sha256"] = "0" * 64
    assert client.put("/api/v1/corpus/repos/1/review", json=value).status_code == 409
    (app.state.corpus.release / "inventory.jsonl").write_text("{}")
    app.state.corpus._manifest_hash = None
    assert client.get("/api/v1/corpus").status_code == 409


def test_original_metadata_citation_is_not_treated_as_a_source_file(corpus_rig):
    app, client, _, _, _ = corpus_rig
    release = app.state.corpus.release
    path = release / "labels.proposed.jsonl"
    labels = [json.loads(line) for line in path.read_text().splitlines()]
    labels[0]["labels"].append(
        {
            "id": "tag:python",
            "name": "Python",
            "kind": "TAG",
            "evidence": [
                {
                    "path": "__github_metadata__.primary_language",
                    "quote": "Python",
                    "app_input_channel": "METADATA",
                }
            ],
        }
    )
    manifest = json.loads((release / "manifest.local.json").read_text())
    manifest["release_files"]["labels.proposed.jsonl"] = write(path, labels, True)
    write(release / "manifest.local.json", manifest)
    value = body(client)
    value["label_ids"].append("tag:python")
    response = client.put("/api/v1/corpus/repos/1/review", json=value)
    assert response.status_code == 200, response.text


def test_multiple_proofs_of_one_label_do_not_duplicate_the_review_choice():
    source = {"path": "README.md", "quote": "Python client", "app_input_channel": "README"}
    metadata = {
        "path": "__github_metadata__.primary_language",
        "quote": "Python",
        "app_input_channel": "METADATA",
    }
    proposals = {
        "labels": [
            {
                "id": "tag:python",
                "name": "Python",
                "kind": "TAG",
                "evidence": [source],
                "rationale": "Explicit client implementation",
            },
            {
                "id": "tag:python",
                "name": "Python",
                "kind": "TAG",
                "evidence": [metadata],
                "rationale": "GitHub language metadata",
            },
        ]
    }
    result = merged_labels(proposals)
    assert len(result) == 1
    assert result[0]["evidence"] == [source, metadata]
    assert "Explicit client implementation" in result[0]["rationale"]
    assert len(proposals["labels"]) == 2
