import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from live import Counters, validate_evaluation_classification  # isort: skip
from app.pretest.ai.schemas import Classification


def test_corpus_and_extension_namespaces_validate_without_changing_canonical_ids():
    registry = {"base": {"kind": "TOPIC", "workspace": "corpus600"}, "extension": {"kind": "TOPIC"}}
    context = {
        "workspace": "fixture",
        "revision": 2,
        "active_revision": 2,
        "profile_hash": "p",
        "active_profile_hash": "p",
        "candidates": ["base", "extension"],
        "evidence_ids": ["E0"],
    }
    value = Classification.model_validate(
        {
            "status": "CLASSIFIED",
            "assignments": [
                {
                    "kind": "TOPIC",
                    "concept_id": cid,
                    "confidence": 0.8,
                    "evidence_ids": ["E0"],
                    "reason": "Contract probe",
                }
                for cid in registry
            ],
            "summary": "Probe",
        }
    )
    assert validate_evaluation_classification(value, context, registry) == value
    assert registry["base"]["workspace"] == "corpus600"
    value.assignments[0].concept_id = "foreign"
    with pytest.raises(ValueError, match="canonical"):
        validate_evaluation_classification(value, context, registry)


from scoring import score


def test_unknown_predictions_are_not_false_positives_and_failed_cases_keep_denominator():
    registry = {i: {"kind": "TOPIC"} for i in ("known", "unknown", "unsupported")}
    rows = [
        {
            "positive_ids": ["known"],
            "candidate_ids": ["known", "unknown"],
            "predicted_ids": ["known", "unknown", "unsupported"],
            "explicit_negative_ids": ["unsupported"],
            "status": "PASS",
        },
        {"positive_ids": ["known"], "candidate_ids": [], "status": "BLOCKED"},
    ]
    result = score(rows, registry)["ALL"]
    assert result["unjudged_predictions"] == 1
    assert result["explicitly_unsupported_predictions"] == 1
    assert result["prediction_recall_of_reviewed_positives"] == 0.5
    assert result["judged_precision"] == 0.5
    assert result["predicted_judgement_coverage"] == pytest.approx(2 / 3)
    assert result["exhaustive_f1"] is None


def test_counters_are_durable_and_cannot_bypass_batch_or_total_with_new_process(
    tmp_path,
):
    path = tmp_path / "counter.sqlite3"
    counter = Counters(path)
    for _ in range(10):
        counter.take("1", "/v1/responses")
        counter.take("1", "/v1/responses/input_tokens")
    with pytest.raises(ValueError, match="ceiling"):
        Counters(path).take("1", "/v1/responses")
    for batch in ("2", "3", "4", "5"):
        for _ in range(10):
            counter.take(batch, "/v1/responses")
            counter.take(batch, "/v1/responses/input_tokens")
    with pytest.raises(ValueError, match="ceiling"):
        counter.take("6", "/v1/responses")
    assert counter.summary()["generation_attempt_admissions"] == 50


def test_generation_reserves_room_for_its_counter_request_and_rejects_unknown_endpoint(
    tmp_path,
):
    counter = Counters(tmp_path / "counter.sqlite3")
    for _ in range(19):
        counter.take("1", "/v1/responses/input_tokens")
    with pytest.raises(ValueError):
        counter.take("1", "/v1/responses")
    with pytest.raises(ValueError):
        counter.take("7", "/v1/responses")
    with pytest.raises(ValueError):
        counter.take("2", "/v1/embeddings")
