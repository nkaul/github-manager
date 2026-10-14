import json
from concurrent.futures import ThreadPoolExecutor

import httpx
import httpx2
import pytest

from app.pretest.ai.corpus import bounded_json, registry, synthetic
from app.pretest.ai.evaluation import metrics, organization_simulation
from app.pretest.ai.evidence import Retriever, profile
from app.pretest.ai.provider import BudgetedProvider, ProviderBlocked
from app.pretest.ai.runner import freeze
from app.pretest.ai.schemas import AccessProbe, TaxonomyDraft, validate_taxonomy
from app.pretest.ai.settings import AISettings
from app.pretest.ai.storage import BudgetError, Ledger


def test_concurrent_reservations_cannot_overspend(tmp_path):
    ledger = Ledger(tmp_path / "private", cap=0.1, initialize=True)

    def attempt(_):
        try:
            ledger.reserve("test", "gpt-6-astra", 500, 256)
            return True
        except BudgetError:
            return False

    with ThreadPoolExecutor(max_workers=8) as pool:
        accepted = list(pool.map(attempt, range(40)))
    assert 0 < sum(accepted) < 40
    assert ledger.summary()["remaining_usd"] >= 0


def test_usage_bound_violation_stops_future_requests(tmp_path):
    ledger = Ledger(tmp_path / "private", initialize=True)
    ident = ledger.reserve("test", "gpt-6-astra", 1, 1)
    ledger.settle(ident, {"input_tokens": 100, "output_tokens": 100})
    with pytest.raises(BudgetError):
        ledger.reserve("test", "gpt-6-astra", 1, 1)


def test_generation_call_limit_survives_restart_even_for_rejected_calls(tmp_path):
    directory = tmp_path / "private"
    ledger = Ledger(directory, initialize=True)
    ident = ledger.reserve("test", "gpt-6-luna", 1, 1, max_calls=1)
    ledger.settle(ident, {}, no_charge=True)
    with pytest.raises(BudgetError):
        Ledger(directory).reserve("test", "gpt-6-luna", 1, 1, max_calls=1)
    assert ledger.summary()["calls"] == 1


def test_concurrent_requests_cannot_exceed_authorized_call_count(tmp_path):
    ledger = Ledger(tmp_path / "private", initialize=True)

    def attempt(_):
        try:
            ledger.reserve("test", "gpt-6-luna", 1, 1, max_calls=5)
            return True
        except BudgetError:
            return False

    with ThreadPoolExecutor(max_workers=4) as pool:
        accepted = list(pool.map(attempt, range(20)))
    assert sum(accepted) == ledger.summary()["calls"] == 5


def test_frozen_corpus_rejects_label_and_split_drift(tmp_path):
    cases = synthetic()
    first = freeze(tmp_path, cases, registry())
    assert freeze(tmp_path, cases, registry()) == first
    cases[0]["labels"] = []
    with pytest.raises(ValueError):
        freeze(tmp_path, cases, registry())


def test_manual_edges_and_rejections_survive_simulated_organization():
    result = organization_simulation(["p-orion", "p-helios"], registry())
    assert result["associations"]["USER"] == ["p-audit"]
    assert result["associations"]["PROPOSED"] == ["p-orion"]
    assert result["canonical_published"] is False
    assert result["github_mutations"] == 0


def test_new_concept_reconsiders_an_already_classified_cached_profile():
    prof = profile(synthetic()[0])
    concepts = registry()
    before = Retriever(concepts).candidates(prof)
    concepts["p-new"] = {
        **concepts["p-orion"],
        "id": "p-new",
        "name": "Patient intake",
        "aliases": ["patient intake"],
    }
    after = Retriever(concepts).candidates(prof)
    assert "p-new" not in before and "p-new" in after
    assert prof["sha"] == profile(synthetic()[0])["sha"]


def test_precision_recall_are_independent_of_model_confidence():
    result = metrics(
        [{"gold": ["p-orion", "p-audit"], "predicted": ["p-orion", "p-helios"]}], registry()
    )["PROJECT"]
    assert result["precision"] == result["recall"] == result["f1"] == 0.5
    assert metrics([], registry())["PROJECT"]["precision"] is None


@pytest.mark.parametrize(
    "field,value",
    [
        ("ai_pretest_budget_usd", 5.01),
        ("app_env", "production"),
        ("openai_classification_model", "unapproved-model"),
        ("ai_pretest_allowed_data", "private"),
        ("ai_pretest_state_directory", "/tmp/unapproved"),
    ],
)
def test_unapproved_configuration_rejected(field, value):
    with pytest.raises(ValueError):
        AISettings(_env_file=None, **{field: value})


@pytest.mark.parametrize("failure", ["refusal", "incomplete", "missing_usage", "quota"])
def test_provider_failures_are_not_successfully_cached(tmp_path, failure):
    ledger = Ledger(tmp_path / "private", initialize=True)
    settings = AISettings(_env_file=None, openai_api_key="synthetic", ai_pretest_live_enabled=True)
    calls = []

    def handler(request):
        calls.append(request.url.path)
        if request.url.path.endswith("input_tokens"):
            return httpx2.Response(200, json={"input_tokens": 30})
        if failure == "quota":
            return httpx2.Response(
                429,
                json={"error": {"type": "credit_balance_exhausted", "message": "synthetic error"}},
            )
        body = {
            "id": "resp_test",
            "object": "response",
            "created_at": 0,
            "status": "incomplete" if failure == "incomplete" else "completed",
            "model": "gpt-6-luna",
            "output": [
                {
                    "type": "message",
                    "id": "msg_test",
                    "role": "assistant",
                    "status": "completed",
                    "content": [
                        {"type": "refusal", "refusal": "Synthetic refusal"}
                        if failure == "refusal"
                        else {
                            "type": "output_text",
                            "annotations": [],
                            "text": '{"authenticated":true,"category":"TEST"}',
                        },
                    ],
                }
            ],
        }
        if failure != "missing_usage":
            body["usage"] = {"input_tokens": 30, "output_tokens": 20, "total_tokens": 50}
        return httpx2.Response(200, json=body)

    provider = BudgetedProvider(settings, ledger, transport=httpx2.MockTransport(handler))
    try:
        result = provider.invoke(
            "gpt-6-luna",
            "access",
            AccessProbe,
            "TEST",
            {"source": "SYNTHETIC", "private": False},
            lambda x: x,
        )
        assert result["status"] != "PASS"
        assert ledger.cache_get(result["cache_key"]) is None
        assert len(calls) == 2
        if failure == "quota":
            assert result["provider_error_code"] == "credit_balance_exhausted"
            assert ledger.summary()["estimated_usd"] == ledger.summary()["reserved_usd"] == 0
        if failure == "missing_usage":
            assert ledger.summary()["reserved_usd"] > 0
    finally:
        provider.close()


def test_private_evidence_and_wrong_destination_never_sent(tmp_path):
    ledger = Ledger(tmp_path / "private", initialize=True)
    settings = AISettings(_env_file=None, openai_api_key="synthetic", ai_pretest_live_enabled=True)
    provider = BudgetedProvider(settings, ledger)
    try:
        result = provider.invoke(
            "gpt-6-luna",
            "access",
            AccessProbe,
            "TEST",
            {"source": "PRIVATE_GITHUB", "private": True},
            lambda x: x,
        )
        assert result["evidence"] == "POLICY"
        assert ledger.summary()["calls"] == 0
        with pytest.raises(ProviderBlocked):
            provider.before(httpx2.Request("POST", "https://example.com/v1/responses"))
    finally:
        provider.close()


def test_public_redirect_cannot_leave_trusted_api_host():
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                301, headers={"location": "https://untrusted.example/README"}
            )
        )
    )
    with client, pytest.raises(ValueError):
        bounded_json(client, "/repos/encode/starlette")


def test_taxonomy_draft_rejects_invented_support_and_parent():
    draft = TaxonomyDraft(
        proposals=[
            {
                "kind": "PROJECT",
                "name": "Example",
                "description": "Test",
                "aliases": [],
                "parent_domain": "Unknown",
                "supporting_repo_ids": ["invented"],
            }
        ],
        notes="Test",
    )
    with pytest.raises(ValueError):
        validate_taxonomy(draft, {"allowed"})


def test_every_retained_phrase_has_actual_source_span():
    prof = profile(synthetic()[0])
    evidence = {e["id"]: e["text"] for e in prof["evidence"]}
    for phrase in prof["phrases"]:
        assert phrase["spans"]
        for span in phrase["spans"]:
            assert evidence[span["id"]][span["start"] : span["end"]]
    assert "synthetic-secret-marker" not in json.dumps(prof)
