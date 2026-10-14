"""No external requests: durable admission, explicit fresh inference and local organization."""

import copy
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from app.demo import analysis, domain
from app.demo.store import Store
from tests.demo.fixtures import Provider, concept
from tests.demo.test_refinement import preview
from tests.demo.test_refinement import rig as refinement_rig
from tests.demo.test_workspace import W, post, published, work


@pytest.fixture
def rig(tmp_path):
    return refinement_rig.__wrapped__(tmp_path)


class RecordedProvider(Provider):
    """Mock validated real-provider provenance; never sends network traffic."""

    fresh_calls = []

    def invoke(self, *args, **kwargs):
        result = super().invoke(*args, **kwargs)
        self.fresh_calls.append(bool(kwargs.get("fresh")))
        result["evidence"] = "LIVE_PROVIDER"
        return result


def classify(app, client, **values):
    plan = preview(client, mode="FULL_CLASSIFICATION", ai_mode="LIVE", **values)
    assert plan["can_start"], plan
    response = post(client, "/organizer/execute", {"plan_id": plan["plan_id"]})
    assert response.status_code == 202, response.text
    return plan, work(app)


def test_no_repeat_before_provider_construction_even_after_revision_and_history_deletion(rig):
    app, client, _ = published(rig)
    app.state.service.provider_factory = RecordedProvider
    plan, run = classify(app, client)
    assert plan["generations"] == 3 and run["status"] == "COMPLETED"
    state = app.state.database.read(W)
    assert all(analysis.receipt(state, k)["ai_analyzed"] for k in plan["keys"])

    def never(*args, **kwargs):
        pytest.fail("Even provider construction/counting must be skipped")

    app.state.service.provider_factory = never
    concept(app.state.database, W, "TAG", "new-category")
    app.state.database.mutate(W, lambda s: s["organization"]["runs"].clear())
    plan, run = classify(app, client)
    assert plan["generations"] == plan["http_requests"] == 0
    assert plan["offline"] == 3 and plan["upper_usd"] == 0
    assert all(o["status"] == "OFFLINE_RECONCILED" for o in run["outcomes"].values())
    # Legacy route receives the same worker guard.
    assert (
        post(
            client, "/organizer/reorganize", {"mode": "FULL_CLASSIFICATION", "ai_mode": "LIVE"}
        ).status_code
        == 202
    )
    assert work(app)["status"] == "COMPLETED"
    reopened = Store(app.state.database.path)
    assert all(analysis.receipt(reopened.read(W), k)["ai_analyzed"] for k in plan["keys"])
    assert not reopened.read("88:samples")["organization"]["analysis"]


def test_no_match_is_success_and_explicit_reanalysis_is_fresh(rig):
    app, client, _ = published(rig)

    class NoMatch(RecordedProvider):
        def invoke(self, *args, **kwargs):
            result = super().invoke(*args, **kwargs)
            if args[1] == "classification-demo":
                result["result"] = {
                    "status": "NO_MATCH",
                    "assignments": [],
                    "summary": "Mock no match",
                }
            return result

    app.state.service.provider_factory = NoMatch
    before = len(RecordedProvider.fresh_calls)
    _, run = classify(app, client)
    assert all(o["status"] == "NO_MATCH" for o in run["outcomes"].values())
    assert client.get("/api/v1/repos?collection=samples&view=no_match").json()["total"] == 3
    _, repeated = classify(app, client)
    assert repeated["status"] == "COMPLETED" and len(RecordedProvider.fresh_calls) == before + 3
    # An explicit reviewed force operation sends fresh=True, even if cache inputs match.
    plan, _ = classify(
        app,
        client,
        selection="MANUAL",
        repo_keys=["synthetic/orion-api"],
        reanalyze=True,
        reanalysis_reason="README changed; reviewed retry",
    )
    assert plan["fresh_ai"] == plan["generations"] == 1
    assert RecordedProvider.fresh_calls[-1] is True
    invalid = post(
        client,
        "/organizer/preview",
        {
            "mode": "FULL_CLASSIFICATION",
            "ai_mode": "LIVE",
            "reanalyze": True,
            "scope": {"view": "all"},
        },
    )
    assert invalid.status_code == 422
    invalid = post(
        client,
        "/organizer/reorganize",
        {"mode": "FULL_CLASSIFICATION", "ai_mode": "LIVE", "reanalyze": True},
    )
    assert invalid.status_code == 422  # No unpreviewed bypass in the legacy endpoint.


def test_taxonomy_reanalysis_is_separate_and_explicit(rig):
    app, client, _ = published(rig)
    before = Provider.calls
    plan = preview(client, mode="REDISCOVER", ai_mode="LIVE")
    assert not plan["can_start"] and plan["chosen"] == 0 and len(plan["skipped"]) == 3
    assert Provider.calls == before
    app.state.service.provider_factory = RecordedProvider
    plan = preview(
        client,
        mode="REDISCOVER",
        ai_mode="LIVE",
        reanalyze=True,
        reanalysis_reason="Review new collection taxonomy",
    )
    assert plan["generations"] == 1 and plan["previously_analyzed_inputs"] == 3
    assert post(client, "/organizer/execute", {"plan_id": plan["plan_id"]}).status_code == 202
    assert work(app)["status"] == "COMPLETED"
    assert RecordedProvider.fresh_calls[-1] is True
    state = app.state.database.read(W)
    assert analysis.receipt(state, plan["keys"][0], "taxonomy")["ai_analyzed"]
    assert not analysis.receipt(state, plan["keys"][0])["ai_analyzed"]


def test_partial_failure_keeps_successes_and_does_not_silently_retry_failures(rig):
    app, client, _ = published(rig)

    class Partial(RecordedProvider):
        def invoke(self, *args, **kwargs):
            if args[4].get("repo_id") == "synthetic/orion-api":
                return {"status": "FAIL", "evidence": "POLICY", "error_type": "ProviderBlocked"}
            return super().invoke(*args, **kwargs)

    app.state.service.provider_factory = Partial
    _, run = classify(app, client)
    assert run["status"] == "PARTIAL_FAILED" and run["failed"] == 1
    state = app.state.database.read(W)
    assert analysis.receipt(state, "synthetic/orion-api")["state"] == "FAILED"
    assert (
        sum(analysis.receipt(state, k).get("ai_analyzed", False) for k in state["core"]["repos"])
        == 2
    )
    before = len(RecordedProvider.fresh_calls)
    plan, _ = classify(app, client)
    assert plan["generations"] == 0 and len(RecordedProvider.fresh_calls) == before
    assert client.get("/api/v1/repos?collection=samples&view=failed").json()["total"] == 1


def test_atomic_claim_recovery_and_unknown_history_require_explicit_action(rig):
    app, client, _ = published(rig)
    store = app.state.database
    plan = preview(client, mode="FULL_CLASSIFICATION", ai_mode="LIVE", count=1)
    assert post(client, "/organizer/execute", {"plan_id": plan["plan_id"]}).status_code == 202
    job = store.claim({W})
    key = plan["keys"][0]

    def claim(_):
        return store.mutate(
            W,
            lambda s: analysis.claim(
                s, [key], "classification", job["id"], False, "TEST", plan["fence"]
            ),
        )

    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(bool(x) for x in pool.map(claim, range(8))) == 1
    store.recover()
    assert analysis.receipt(store.read(W), key)["state"] == "UNCERTAIN"
    assert not analysis.admission(store.read(W), key)[0]
    assert analysis.admission(store.read(W), key, force=True)[0]
    store.mutate(W, lambda s: s["organization"]["analysis"].pop(key))
    plan = preview(
        client, mode="FULL_CLASSIFICATION", ai_mode="LIVE", selection="MANUAL", repo_keys=[key]
    )
    assert plan["generations"] == 0 and plan["offline"] == 1


def test_valid_response_receipt_survives_stale_application(rig):
    app, client, _ = published(rig)

    class ChangedDuringInference(RecordedProvider):
        def invoke(self, *args, **kwargs):
            result = super().invoke(*args, **kwargs)
            concept(app.state.database, W, "TAG", "Changed during response")
            return result

    app.state.service.provider_factory = ChangedDuringInference
    plan, run = classify(app, client, count=1)
    assert run["status"] == "CANCELLED_STALE"
    state = app.state.database.read(W)
    assert analysis.receipt(state, plan["keys"][0])["ai_analyzed"]
    assert analysis.projection(state, plan["keys"][0])["stale"]
    assert analysis.receipt(state, plan["keys"][0])["last_success"]["result"] is None
    assert not state["organization"]["suggestions"]


@pytest.mark.parametrize(
    "scope", [{"history": True}, {"kinds": ["DOMAIN", "PROJECT", "TOPIC", "TAG"], "cache": True}]
)
def test_resets_preserve_receipts_and_budget_without_reusing_invalid_references(rig, scope):
    app, client, ledger = rig
    app, client, _ = published((app, client, ledger))
    app.state.service.provider_factory = RecordedProvider
    plan, _ = classify(app, client)
    before = ledger.summary()
    reset = post(client, "/organizer/reset/preview", scope).json()
    assert (
        post(
            client,
            "/organizer/reset/execute",
            {"plan_id": reset["plan_id"], "confirmation": "DELETE"},
        ).status_code
        == 202
    )
    assert work(app)["status"] == "COMPLETED"
    state = Store(app.state.database.path).read(W)
    assert all(analysis.receipt(state, k)["ai_analyzed"] for k in plan["keys"])
    if scope.get("kinds") or reset["scope"]["associations"]:
        assert all(
            analysis.receipt(state, k)["last_success"]["result"] is None for k in plan["keys"]
        )
    assert ledger.summary() == before


def test_offline_migration_backfills_partial_run_success_and_draft_without_fabricating_inputs(rig):
    app, client, _ = published(rig)
    store = app.state.database
    key = "synthetic/orion-api"

    def legacy(s):
        org = s["organization"]
        org.pop("analysis_schema")
        org["analysis"] = {}
        org["runs"]["legacy"] = {
            "id": "legacy",
            "kind": "FULL_CLASSIFICATION",
            "status": "PARTIAL_FAILED",
            "created_at": "2026-10-13",
            "revision": 1,
            "outcomes": {
                key: {
                    "status": "NO_MATCH",
                    "evidence": "LIVE_PROVIDER",
                    "model": "historical-model",
                },
                "synthetic/orion-ui": {"status": "FAILED", "evidence": "POLICY"},
            },
        }

    store.mutate(W, legacy)
    before = Provider.calls
    state = Store(store.path).read(W)
    rec = analysis.receipt(state, key)
    assert rec["ai_analyzed"] and rec["last_success"]["backfilled"]
    assert not rec["last_success"]["fingerprint_known"]
    assert analysis.receipt(state, "synthetic/orion-ui")["state"] == "FAILED"
    other = next(k for k in state["core"]["repos"] if k not in {key, "synthetic/orion-ui"})
    assert analysis.receipt(state, other)["state"] == "UNKNOWN"
    assert analysis.receipt(state, key, "taxonomy")["last_success"]["backfilled"]
    assert Provider.calls == before


def test_label_coverage_facets_domains_and_idempotent_manual_assignment(rig):
    app, client, concepts = published(rig)
    store = app.state.database
    topic = next(c for c in concepts if c["kind"] == "TOPIC")
    project = next(c for c in concepts if c["kind"] == "PROJECT")
    key = "synthetic/orion-api"
    post(client, "/repos/associations", {"repo_keys": [key], "concept_ids": [topic["id"]]})
    result = client.get("/api/v1/repos?collection=samples&view=uncategorized&limit=1").json()
    assert result["summary"]["labeled"] == 1 and result["summary"]["uncategorized"] == 3
    assert result["summary"]["topics"] == 1 and result["summary"]["no_labels"] == 2
    assert result["concept_counts"][topic["id"]] == {"accepted": 1, "pending": 0}
    assert client.get("/api/v1/repos?collection=samples&view=no_labels").json()["total"] == 2
    before = copy.deepcopy(store.read(W)["core"]["repos"][key])
    post(client, "/repos/associations", {"repo_keys": [key], "concept_ids": [topic["id"]]})
    assert store.read(W)["core"]["repos"][key] == before
    post(client, "/repos/associations", {"repo_keys": [key], "concept_ids": [project["id"]]})
    result = client.get(
        "/api/v1/repos?collection=samples&view=all&concept=" + project["domain"]
    ).json()
    assert result["total"] == 1 and result["concept_counts"][project["domain"]]["accepted"] == 1
    assert not analysis.receipt(store.read(W), key)["ai_analyzed"]


def test_grouped_bulk_review_validates_once_and_reports_stale_items(rig):
    app, client, concepts = published(rig)
    _, run = classify(app, client)
    org = app.state.database.read(W)["organization"]
    suggestions = list(org["suggestions"].values())
    first = suggestions[0]
    topic = next(c for c in concepts if c["kind"] == "TOPIC")

    def sibling(s):
        other = {**first, "id": "sibling", "concept_id": topic["id"], "kind": "TOPIC"}
        stale = {**first, "id": "stale", "profile_hash": "old"}
        s["organization"]["suggestions"].update(sibling=other, stale=stale)

    app.state.database.mutate(W, sibling)
    result = post(
        client,
        "/organizer/suggestions/batch",
        {"ids": [first["id"], "sibling", "stale"], "decision": "accept"},
    ).json()
    assert sum(o["status"] == "ACCEPTED" for o in result["outcomes"]) == 2
    assert sum(o["status"] == "SKIPPED" for o in result["outcomes"]) == 1
    assert (
        post(
            client,
            "/organizer/suggestions/batch",
            {"ids": ["missing"], "decision": "reject"},
            "github",
        ).json()["outcomes"][0]["status"]
        == "SKIPPED"
    )
    assert run["failed"] == 0


def test_configurable_trigger_types_counts_debounce_cooldown_and_no_paid_repeat(rig):
    app, client, _ = published(rig)
    app.state.service.provider_factory = RecordedProvider
    classify(app, client)
    store = app.state.database
    patch = {
        "auto_enabled": True,
        "auto_weight_threshold": 2,
        "auto_entity_threshold": 1,
        "auto_project_threshold": 0,
        "auto_window_seconds": 900,
        "quiet_seconds": 0,
        "cooldown_seconds": 0,
        "auto_change_types": ["RULE"],
    }
    assert (
        client.patch("/api/v1/organizer/settings?collection=samples", json=patch).status_code == 200
    )
    assert not analysis.automation(store.read(W))["threshold_met"]
    store.mutate(W, lambda s: domain.changed(s, "rule1", "RULE", 2))
    before = len(RecordedProvider.fresh_calls)
    app.state.service.schedule({W})
    assert store.read(W)["organization"]["control"]["active_run"]
    assert work(app)["status"] == "COMPLETED"
    assert len(RecordedProvider.fresh_calls) == before
    app.state.service.schedule({W})
    assert not store.read(W)["organization"]["control"]["active_run"]
    store.mutate(W, lambda s: domain.changed(s, "x", "COSMETIC", 0))
    assert not analysis.automation(store.read(W))["ready"]
    store.mutate(W, lambda s: domain.change_event(s, "README", "EVIDENCE", 2))
    assert not analysis.automation(store.read(W))["ready"]  # Type excluded.
    patch.update(auto_change_types=["EVIDENCE"], quiet_seconds=10, cooldown_seconds=30)
    assert (
        client.patch("/api/v1/organizer/settings?collection=samples", json=patch).status_code == 200
    )
    status = analysis.automation(store.read(W))
    assert status["threshold_met"] and not status["ready"]
    state = store.read(W)
    for event in state["organization"]["changes"]:
        event["at"] = time.time() - 100
    state["organization"]["control"]["last_auto"] = 0
    assert analysis.automation(state)["ready"]
    for event in state["organization"]["changes"]:
        event["at"] = time.time() - 1000
    assert not analysis.automation(state)["threshold_met"]
    assert (
        client.patch(
            "/api/v1/organizer/settings?collection=samples", json={"auto_weight_threshold": 0}
        ).status_code
        == 422
    )
    assert (
        client.patch(
            "/api/v1/organizer/settings?collection=samples",
            json={"auto_change_types": ["COSMETIC"]},
        ).status_code
        == 422
    )
    assert (
        client.patch(
            "/api/v1/organizer/settings?collection=samples", json={"quiet_seconds": 900}
        ).status_code
        == 409
    )


def test_cross_page_multi_assignment_is_atomic_and_preserves_other_memberships(rig):
    app, client, concepts = published(rig)
    store = app.state.database
    topic = next(c for c in concepts if c["kind"] == "TOPIC")
    tag = next(c for c in concepts if c["kind"] == "TAG")

    def ingest(s):
        template = s["core"]["repos"]["synthetic/orion-api"]
        for i in range(45):
            key = f"synthetic/cross-page-{i:02}"
            s["core"]["repos"][key] = {**template, "key": key, "name": key}
            analysis.new_repository(s, key)

    store.mutate(W, ingest)
    keys = [f"synthetic/cross-page-{i:02}" for i in (0, 44)]
    before = Provider.calls
    assert (
        post(
            client, "/repos/associations", {"repo_keys": keys, "concept_ids": [tag["id"]]}
        ).status_code
        == 200
    )
    assert (
        post(
            client, "/repos/associations", {"repo_keys": keys, "concept_ids": [topic["id"]]}
        ).status_code
        == 200
    )
    result = client.get("/api/v1/repos?collection=samples&view=all&limit=1").json()
    assert result["concept_counts"][topic["id"]]["accepted"] == 2
    assert all(
        set(store.read(W)["organization"]["edges"][k]) == {tag["id"], topic["id"]} for k in keys
    )
    snapshot = store.read(W)
    assert (
        post(
            client,
            "/repos/associations",
            {
                "repo_keys": [keys[0], "another-owner/private"],
                "concept_ids": [topic["id"]],
                "operation": "REMOVE",
            },
        ).status_code
        == 409
    )
    assert store.read(W) == snapshot
    store.mutate(W, lambda s: domain.remove_concept(s, topic["id"]))
    snapshot = store.read(W)
    assert (
        post(
            client, "/repos/associations", {"repo_keys": keys, "concept_ids": [topic["id"]]}
        ).status_code
        == 409
    )
    assert store.read(W) == snapshot and Provider.calls == before


def test_input_failure_is_durable_and_needs_explicit_retry(rig):
    app, client, _ = published(rig)

    async def unavailable(*args, **kwargs):
        raise ValueError("Public access could not be verified")

    app.state.service.ensure_profile = unavailable
    before = Provider.calls
    _, run = classify(app, client)
    assert run["failed"] == 3 and Provider.calls == before
    state = app.state.database.read(W)
    assert all(analysis.receipt(state, k)["state"] == "FAILED" for k in state["core"]["repos"])
    plan, run = classify(app, client)
    assert plan["fresh_ai"] == 0 and plan["offline"] == 3
    assert run["status"] == "COMPLETED" and Provider.calls == before


def test_dispatch_authorization_rechecks_manual_decisions(rig):
    app, client, concepts = published(rig)
    tag = next(c for c in concepts if c["kind"] == "TAG")

    class ChangedBeforeDispatch(Provider):
        def invoke(self, model, task, schema, system, evidence, validator, **kwargs):
            app.state.database.mutate(
                W, lambda s: domain.mapping(s, [evidence["repo_id"]], [tag["id"]], "ADD")
            )
            assert not self.authorized()
            return {"status": "BLOCKED", "evidence": "POLICY", "error_type": "ProviderBlocked"}

    app.state.service.provider_factory = ChangedBeforeDispatch
    plan, run = classify(app, client, count=1)
    assert run["failed"] == 0 and run["stale"] == 1
    receipt = analysis.receipt(app.state.database.read(W), plan["keys"][0])
    assert receipt["state"] == "FAILED" and not receipt["ai_analyzed"]
