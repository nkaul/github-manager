import copy

from app.demo import domain
from tests.demo.fixtures import concept
from tests.demo.test_workspace import W, post
from tests.demo.test_workspace import rig as rig


def value(kind, name, aliases=None, parent=None):
    return {
        "kind": kind,
        "name": name,
        "aliases": aliases or [],
        "description": "Reviewed test concept",
        "domain": parent,
    }


def draft(app, proposals):
    def mutate(s):
        s["organization"]["drafts"]["test-draft"] = {
            "id": "test-draft",
            "status": "DRAFT",
            "proposals": proposals,
            "fence": domain.fence(s),
            "notes": "Fixture only",
            "evidence": "FIXTURE",
        }

    app.state.database.mutate(W, mutate)
    return {
        "draft_id": "test-draft",
        "proposals": proposals,
        "expected_revision": app.state.database.read(W)["organization"]["control"]["revision"],
    }


def check(client, payload):
    response = post(client, "/taxonomy/drafts/check", payload)
    assert response.status_code == 200, response.text
    return response.json()


def repair(client, payload, conflict, action):
    response = post(
        client,
        "/taxonomy/drafts/remediate",
        {
            **payload,
            "conflict_id": conflict["id"] if conflict else None,
            "action": action,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_exact_archived_alias_error_and_manual_remedy(rig):
    app, client, _ = rig
    existing = concept(app.state.database, W, "DOMAIN", "AI")
    assert (
        client.delete(f"/api/v1/taxonomy/concepts/{existing['id']}?collection=samples").status_code
        == 200
    )
    proposal = value("DOMAIN", "AI - Atrificial Intelligence", ["AI"])
    response = post(client, "/taxonomy/concepts", proposal)
    assert response.status_code == 409
    error = response.json()
    assert error["code"] == "TAXONOMY_CONFLICT"
    c = error["conflicts"][0]
    assert c["field"] == "alias" and c["term"] == "AI"
    assert c["existing"]["id"] == existing["id"] and not c["existing"]["active"]
    assert "archived domain “AI”" in error["detail"]
    assert post(client, "/taxonomy/concepts", {**proposal, "aliases": []}).status_code == 200


def test_all_conflicts_checked_without_mutation_and_failed_publish_is_atomic(rig):
    app, client, _ = rig
    concept(app.state.database, W, "TAG", "Python", aliases=["Py"])
    payload = draft(
        app,
        [
            value("TOPIC", "New Topic"),
            value("TAG", "New Language", ["PY"]),
            value("TOPIC", "Web APIs", ["web-apis"]),
        ],
    )
    before = copy.deepcopy(app.state.database.read(W))
    result = check(client, payload)
    assert not result["valid"]
    assert {c["type"] for c in result["conflicts"]} == {"RESERVED_TERM", "DUPLICATE_TERM"}
    assert app.state.database.read(W) == before
    failed = post(client, "/taxonomy/drafts/publish", payload)
    assert failed.status_code == 409 and len(failed.json()["conflicts"]) == 2
    assert app.state.database.read(W) == before


def test_opt_in_alias_cleanup_keeps_registry_and_draft_unchanged_until_publish(rig):
    app, client, _ = rig
    existing = concept(app.state.database, W, "TAG", "Machine Learning", aliases=["ML"])
    app.state.database.mutate(W, lambda s: domain.remove_concept(s, existing["id"]))
    payload = draft(app, [value("TAG", "Learning", ["ml", "LEARNING", "Useful"])])
    before = app.state.database.read(W)
    result = repair(client, payload, None, "CLEAN_ALIASES")
    assert result["proposals"][0]["aliases"] == ["Useful"] and result["check"]["valid"]
    assert app.state.database.read(W) == before
    assert (
        post(
            client, "/taxonomy/drafts/publish", {**payload, "proposals": result["proposals"]}
        ).status_code
        == 200
    )
    assert not app.state.database.read(W)["organization"]["concepts"][existing["id"]]["active"]


def test_reuse_existing_domain_rewrites_parent_and_preserves_identity_metadata(rig):
    app, client, _ = rig
    existing = concept(app.state.database, W, "DOMAIN", "Artificial Intelligence", aliases=["AI"])
    original = copy.deepcopy(existing)
    payload = draft(
        app,
        [
            value("DOMAIN", "AI - Atrificial Intelligence", ["AI"]),
            value("PROJECT", "AI Workbench", parent="AI - Atrificial Intelligence"),
        ],
    )
    result = repair(client, payload, check(client, payload)["conflicts"][0], "REUSE")
    assert result["check"]["valid"]
    assert result["proposals"][1]["domain"] == "Artificial Intelligence"
    assert app.state.database.read(W)["organization"]["concepts"][existing["id"]] == original
    response = post(
        client, "/taxonomy/drafts/publish", {**payload, "proposals": result["proposals"]}
    )
    assert response.status_code == 200, response.text
    published = response.json()["concepts"]
    assert published[0]["id"] == existing["id"] and published[1]["domain"] == existing["id"]
    assert app.state.database.read(W)["organization"]["concepts"][existing["id"]] == original


def test_unique_domain_rename_keeps_project_links_and_archived_reservation(rig):
    app, client, _ = rig
    existing = concept(app.state.database, W, "DOMAIN", "AI")
    app.state.database.mutate(W, lambda s: domain.remove_concept(s, existing["id"]))
    payload = draft(app, [value("DOMAIN", "ai"), value("PROJECT", "Workbench", parent="AI")])
    conflict = check(client, payload)["conflicts"][0]
    assert "REUSE" not in {a["kind"] for a in conflict["actions"]}
    result = repair(client, payload, conflict, "RENAME")
    assert result["proposals"][0]["name"] == "ai (2)"
    assert result["proposals"][1]["domain"] == "ai (2)" and result["check"]["valid"]
    assert (
        post(
            client, "/taxonomy/drafts/publish", {**payload, "proposals": result["proposals"]}
        ).status_code
        == 200
    )
    assert not app.state.database.read(W)["organization"]["concepts"][existing["id"]]["active"]


def test_duplicate_draft_names_normalization_and_exclusion(rig):
    app, client, _ = rig
    payload = draft(
        app,
        [value("TOPIC", "Web APIs"), value("TOPIC", "Ｗｅｂ-ＡＰＩｓ"), value("TAG", "Web APIs")],
    )
    result = check(client, payload)
    assert len(result["conflicts"]) == 1
    conflict = result["conflicts"][0]
    assert conflict["type"] == "DUPLICATE_PROPOSAL"
    repaired = repair(client, payload, conflict, "EXCLUDE")
    assert len(repaired["proposals"]) == 2 and repaired["check"]["valid"]


def test_missing_parent_is_identified_and_prevents_partial_publication(rig):
    app, client, _ = rig
    payload = draft(app, [value("TAG", "Valid Tag"), value("PROJECT", "Orphan", parent="Absent")])
    before = app.state.database.read(W)
    result = check(client, payload)
    assert result["conflicts"][0]["field"] == "domain"
    assert "Absent" in result["conflicts"][0]["message"]
    assert post(client, "/taxonomy/drafts/publish", payload).status_code == 409
    assert app.state.database.read(W) == before


def test_checks_repairs_and_publication_reject_stale_owner_csrf_and_fence(rig):
    app, client, _ = rig
    payload = draft(app, [value("TOPIC", "First")])
    assert post(client, "/taxonomy/drafts/check", payload, collection="github").status_code == 409
    good = client.headers["X-CSRF-Token"]
    client.headers["X-CSRF-Token"] = "wrong"
    assert post(client, "/taxonomy/drafts/check", payload).status_code == 403
    client.headers["X-CSRF-Token"] = good
    concept(app.state.database, W, "TOPIC", "Concurrent Edit")
    assert post(client, "/taxonomy/drafts/check", payload).status_code == 409
    assert (
        post(
            client, "/taxonomy/drafts/remediate", {**payload, "action": "CLEAN_ALIASES"}
        ).status_code
        == 409
    )
    payload["expected_revision"] += 1
    assert (
        post(client, "/taxonomy/drafts/publish", payload).status_code == 409
    )  # Original draft fence.


def test_repair_requires_current_conflict_and_never_mutates_archive(rig):
    app, client, _ = rig
    existing = concept(app.state.database, W, "TAG", "Archived")
    app.state.database.mutate(W, lambda s: domain.remove_concept(s, existing["id"]))
    payload = draft(app, [value("TAG", "Archived")])
    conflict = check(client, payload)["conflicts"][0]
    assert (
        post(
            client,
            "/taxonomy/drafts/remediate",
            {**payload, "action": "REUSE", "conflict_id": conflict["id"]},
        ).status_code
        == 409
    )
    assert (
        post(
            client,
            "/taxonomy/drafts/remediate",
            {**payload, "action": "RENAME", "conflict_id": "tampered"},
        ).status_code
        == 409
    )
    payload["proposals"][0]["name"] = "Distinct"
    assert (
        post(
            client,
            "/taxonomy/drafts/remediate",
            {**payload, "action": "RENAME", "conflict_id": conflict["id"]},
        ).status_code
        == 409
    )
