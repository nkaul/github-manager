"""Promptfoo provider/assertions over saved receipts; never constructs an LLM."""

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scoring import score

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "docs/validation/private/corpus-600-v2/evaluation-reviewed-30-v1"


def read(name):
    return json.loads((OUT / name).read_text())


def call_api(prompt, options, context):
    manifest = read("manifest.json")
    for name, expected in manifest["files"].items():
        if hashlib.sha256((OUT / name).read_bytes()).hexdigest() != expected:
            return {"error": "Frozen input hash mismatch; no live fallback"}
    rid = str(context["vars"]["repository_id"])
    record = read("predictions.json").get("primary:" + rid)
    if not record or record["status"] != "PASS":
        return {"error": "No valid saved prediction; no live fallback"}
    return {
        "output": json.dumps(record["call"]["result"]),
        "cached": True,
        "cost": 0,
        "tokenUsage": {"prompt": 0, "completion": 0, "total": 0},
    }


def get_assert(output, context):
    rid = str(context["vars"]["repository_id"])
    data = json.loads(output)
    case = read("reference-snapshot.json")[rid]
    registry = read("registry.json")
    inputs = read("classification-inputs.json")[rid]["payload"]
    assignments = data["assignments"]
    ids = [a["concept_id"] for a in assignments]
    valid = (
        len(ids) == len(set(ids))
        and set(ids) <= set(case["candidate_ids"])
        and all(
            a["kind"] == registry[a["concept_id"]]["kind"]
            and set(a["evidence_ids"]) <= {e["id"] for e in inputs["evidence"]}
            for a in assignments
        )
    )
    value = score([{**case, "predicted_ids": ids, "status": "PASS"}], registry)["ALL"]
    return {
        "pass": valid,
        "score": value["prediction_recall_of_reviewed_positives"],
        "reason": "Contract validity; numeric score is reviewed-positive recall, not exhaustive quality. Unknown predictions="
        + str(value["unjudged_predictions"]),
        "named_scores": {
            "reviewed_positive_recall": value["prediction_recall_of_reviewed_positives"],
            "unjudged_predictions": value["unjudged_predictions"],
            "contract_valid": int(valid),
        },
    }
