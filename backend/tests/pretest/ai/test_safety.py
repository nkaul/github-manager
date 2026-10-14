import json
from copy import deepcopy

import httpx2
import pytest

from app.pretest.ai.corpus import registry, synthetic
from app.pretest.ai.evidence import document_frequency, profile, selected_evidence
from app.pretest.ai.provider import BudgetedProvider
from app.pretest.ai.schemas import AccessProbe, Classification, validate_classification
from app.pretest.ai.settings import AISettings
from app.pretest.ai.storage import BudgetError, Ledger


@pytest.fixture
def settings(tmp_path):
    return AISettings(
        _env_file=None, openai_api_key="synthetic-test-key", ai_pretest_live_enabled=True
    )


@pytest.fixture
def ledger(tmp_path):
    return Ledger(tmp_path / "private", initialize=True)


def test_reservations_survive_restart_and_failed_requests(ledger):
    ident = ledger.reserve("test", "gpt-6-astra", 12000, 4096)
    reopened = Ledger(ledger.directory)
    assert reopened.summary()["reserved_usd"] > 0
    with pytest.raises(BudgetError):
        for _ in range(50):
            reopened.reserve("test", "gpt-6-astra", 12000, 4096)
    assert reopened.summary()["remaining_usd"] >= 0
    reopened.settle(ident, {"input_tokens": 100, "output_tokens": 100})
    assert reopened.summary()["estimated_usd"] == 0.006


def test_ledger_cannot_be_reinitialized_or_change_cap(ledger):
    with pytest.raises(BudgetError):
        Ledger(ledger.directory, initialize=True)
    with pytest.raises(BudgetError):
        Ledger(ledger.directory, cap=4)
    ledger.path.unlink()
    with pytest.raises(BudgetError):
        Ledger(ledger.directory)
    with pytest.raises(BudgetError):
        Ledger(ledger.directory, initialize=True)


def test_unknown_usage_keeps_maximum_reservation(ledger):
    ident = ledger.reserve("test", "gpt-6.1-sol", 100, 256)
    before = ledger.summary()
    ledger.settle(ident, {})
    assert ledger.summary() == before


def test_cache_hashes_are_scoped_and_restartable(ledger):
    ledger.cache_put("workspace-a:revision-1:profile-v1", {"status": "PASS"})
    assert Ledger(ledger.directory).cache_get("workspace-a:revision-1:profile-v1")
    assert ledger.cache_get("workspace-b:revision-1:profile-v1") is None
    assert ledger.cache_get("workspace-a:revision-2:profile-v1") is None


@pytest.mark.parametrize(
    "key,value",
    [
        ("private", True),
        ("private", None),
        ("source", "PRIVATE_GITHUB"),
    ],
)
def test_private_unknown_visibility_and_source_rejected(key, value):
    repo = synthetic()[0]
    repo[key] = value
    with pytest.raises(ValueError):
        selected_evidence(repo)


def test_injection_and_secret_marker_excluded_from_model_evidence():
    repo = next(r for r in synthetic() if r["name"] == "injection")
    result = json.dumps(profile(repo))
    assert "synthetic-secret-marker" not in result
    assert "Ignore all previous" not in result
    assert "HTTP client" in result


def test_install_only_change_does_not_invalidate_selected_profile():
    repo = synthetic()[0]
    first = profile(repo)
    repo["readme"] += "\n## Installation\nInstall Helios Python package.\n"
    repo["sha"] = "changed"
    assert profile(repo)["hash"] == first["hash"]


def test_document_frequency_counts_distinct_repositories():
    one = {"evidence": [{"text": "LIMS " * 1000}]}
    two = {"evidence": [{"text": "LIMS scheduling"}]}
    assert document_frequency([one, two])["lims"] == 2


def context():
    return {
        "revision": 1,
        "active_revision": 1,
        "profile_hash": "v1",
        "active_profile_hash": "v1",
        "workspace": "fixture",
        "candidates": ["p-orion"],
        "evidence_ids": ["E0"],
        "rejections": [],
    }


def classification():
    return Classification(
        status="CLASSIFIED",
        assignments=[
            {
                "kind": "PROJECT",
                "concept_id": "p-orion",
                "confidence": 0.9,
                "evidence_ids": ["E0"],
                "reason": "Explicit project purpose",
            }
        ],
        summary="Orion service",
    )


@pytest.mark.parametrize(
    "mutation",
    [
        "unknown",
        "wrong_kind",
        "evidence",
        "duplicate",
        "confidence",
        "no_match",
        "inactive",
        "other_workspace",
        "not_candidate",
        "rejected",
        "stale",
        "stale_profile",
        "stale_policy",
    ],
)
def test_invalid_results_never_accepted(mutation):
    result, ctx, concepts = classification(), context(), registry()
    item = result.assignments[0]
    if mutation == "unknown":
        item.concept_id = "invented"
    elif mutation == "wrong_kind":
        item.kind = "TAG"
    elif mutation == "evidence":
        item.evidence_ids = ["invented"]
    elif mutation == "duplicate":
        result.assignments.append(deepcopy(item))
    elif mutation == "confidence":
        item.confidence = 2
    elif mutation == "no_match":
        result.status = "NO_MATCH"
    elif mutation == "inactive":
        concepts["p-orion"]["active"] = False
    elif mutation == "other_workspace":
        concepts["p-orion"]["workspace"] = "another"
    elif mutation == "not_candidate":
        ctx["candidates"] = []
    elif mutation == "rejected":
        ctx["rejections"] = ["p-orion"]
    elif mutation == "stale":
        ctx["active_revision"] = 2
    elif mutation == "stale_profile":
        ctx["active_profile_hash"] = "new"
    else:
        ctx["active_policy_version"] = 2
    with pytest.raises(ValueError):
        validate_classification(result, ctx, concepts)


def transport_handler(request, calls, *, count=42):
    body = json.loads(request.content)
    calls.append((request.url.path, body))
    if request.url.path.endswith("input_tokens"):
        return httpx2.Response(200, json={"object": "response.input_tokens", "input_tokens": count})
    return httpx2.Response(
        200,
        json={
            "id": "resp_synthetic",
            "object": "response",
            "created_at": 0,
            "status": "completed",
            "model": body["model"],
            "output": [
                {
                    "type": "message",
                    "id": "msg_synthetic",
                    "role": "assistant",
                    "status": "completed",
                    "content": [
                        {
                            "type": "output_text",
                            "annotations": [],
                            "text": '{"authenticated":true,"category":"TEST"}',
                        }
                    ],
                }
            ],
            "usage": {
                "input_tokens": 42,
                "output_tokens": 10,
                "total_tokens": 52,
                "input_tokens_details": {"cached_tokens": 0},
                "output_tokens_details": {"reasoning_tokens": 0},
            },
        },
    )


def test_actual_langchain_payload_is_counted_before_reserved_generation(settings, ledger):
    calls = []
    adapter = BudgetedProvider(
        settings,
        ledger,
        transport=httpx2.MockTransport(lambda request: transport_handler(request, calls)),
    )
    try:
        result = adapter.invoke(
            "gpt-6-luna",
            "access",
            AccessProbe,
            "Return TEST true.",
            {"source": "SYNTHETIC", "private": False},
            lambda x: x,
            max_output=256,
        )
        assert result["status"] == "PASS", result
        assert [path for path, _ in calls] == ["/v1/responses/input_tokens", "/v1/responses"]
        count_payload, generation_payload = calls[0][1], calls[1][1]
        assert count_payload["text"] == generation_payload["text"]
        assert count_payload["input"] == generation_payload["input"]
        assert generation_payload["text"]["format"]["strict"] is True
        assert generation_payload["store"] is False
        assert generation_payload["max_output_tokens"] == 256
        assert ledger.summary()["reserved_usd"] == 0
        replay = adapter.invoke(
            "gpt-6-luna",
            "access",
            AccessProbe,
            "Return TEST true.",
            {"source": "SYNTHETIC", "private": False},
            lambda x: x,
            max_output=256,
        )
        assert replay["evidence"] == "REPLAY"
        assert len(calls) == 2
    finally:
        adapter.close()


def test_over_budget_input_never_generates(settings, ledger):
    calls = []
    adapter = BudgetedProvider(
        settings,
        ledger,
        transport=httpx2.MockTransport(
            lambda request: transport_handler(request, calls, count=2001)
        ),
    )
    try:
        result = adapter.invoke(
            "gpt-6-luna",
            "access",
            AccessProbe,
            "TEST",
            {"source": "SYNTHETIC", "private": False},
            lambda x: x,
        )
        assert result["status"] == "BLOCKED"
        assert len(calls) == 1
        assert ledger.summary()["calls"] == 0
    finally:
        adapter.close()


def test_key_never_in_settings_repr_or_public_dump(settings, monkeypatch):
    assert "synthetic-test-key" not in repr(settings)
    assert "synthetic-test-key" not in settings.model_dump_json()
    settings.require_live(True)
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    with pytest.raises(ValueError):
        settings.require_live(True)
