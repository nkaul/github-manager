"""Current Ragas collections API, isolated from the app and provider credentials."""

import argparse
import asyncio
import hashlib
import json
import os
import socket
import subprocess
from pathlib import Path

os.environ["RAGAS_DO_NOT_TRACK"] = "true"
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / "docs/validation/private/corpus-600-v2/evaluation-reviewed-30-v1"


def forbidden(*args, **kwargs):
    raise RuntimeError("Ragas worker forbids direct networking; use budgeted subprocess")


socket.socket.connect = forbidden
socket.socket.connect_ex = forbidden

from ragas.dataset_schema import SingleTurnSample
from ragas.llms.base import InstructorBaseRagasLLM
from ragas.metrics import IDBasedContextRecall
from ragas.metrics.collections import Faithfulness


def read(path):
    return json.loads(Path(path).read_text())


class GuardedLLM(InstructorBaseRagasLLM):
    def __init__(self, case_id, stub=False):
        self.case_id, self.stub, self.calls = case_id, stub, 0

    def generate(self, prompt, response_model):
        self.calls += 1
        if self.calls > 2:
            raise RuntimeError("Faithfulness fanout exceeded two calls per sample")
        if self.stub:
            data = (
                {"statements": ["The repository provides testing."]}
                if response_model.__name__ == "StatementGeneratorOutput"
                else {
                    "statements": [
                        {
                            "statement": "The repository provides testing.",
                            "reason": "Explicit supplied context",
                            "verdict": 1,
                        }
                    ]
                }
            )
            return response_model.model_validate(data)
        identity = hashlib.sha256(
            (self.case_id + response_model.__name__ + prompt).encode()
        ).hexdigest()
        path = OUT / "ragas-requests" / (identity + ".json")
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(
                json.dumps(
                    {"case_id": self.case_id, "schema": response_model.__name__, "prompt": prompt},
                    indent=2,
                )
                + "\n"
            )
            path.chmod(0o600)
        result_path = path.with_suffix(".result.json")
        if not result_path.exists():
            subprocess.run(
                [str(ROOT / "backend/.venv/bin/python"), str(HERE / "judge_bridge.py"), str(path)],
                check=True,
                cwd=ROOT,
                stdout=subprocess.DEVNULL,
            )
        result = read(result_path)
        if result["status"] != "PASS":
            raise RuntimeError("Saved judge failure requires explicit handling; no live fallback")
        return response_model.model_validate(result["result"])

    async def agenerate(self, prompt, response_model):
        return self.generate(prompt, response_model)


async def main(stub=False):
    if stub:
        llm = GuardedLLM("contract-probe", stub=True)
        result = await Faithfulness(llm=llm).ascore(
            user_input="What does this repository provide?",
            response="The repository provides testing.",
            retrieved_contexts=["The repository provides testing."],
        )
        assert result.value == 1.0 and llm.calls == 2
        print("Current collections Faithfulness stub: exact two-call fanout PASS; no network.")
        return
    cases, registry = read(OUT / "reference-snapshot.json"), read(OUT / "registry.json")
    by_kind = {}
    metric = IDBasedContextRecall()
    for kind in ("PROJECT", "TOPIC", "TAG", "ALL"):
        rows = []
        for rid, case in cases.items():
            gold = [i for i in case["positive_ids"] if kind == "ALL" or registry[i]["kind"] == kind]
            candidates = [
                i for i in case["candidate_ids"] if kind == "ALL" or registry[i]["kind"] == kind
            ]
            if gold:
                value = await metric.single_turn_ascore(
                    SingleTurnSample(retrieved_context_ids=candidates, reference_context_ids=gold)
                )
                expected = len(set(candidates) & set(gold)) / len(gold)
                assert abs(value - expected) < 1e-12
                rows.append({"id": rid, "positive_count": len(gold), "score": value})
        by_kind[kind] = {
            "cases_with_positive_support": len(rows),
            "micro_candidate_recall": sum(r["positive_count"] * r["score"] for r in rows)
            / sum(r["positive_count"] for r in rows),
            "records": rows,
        }
    output = {
        "ragas_version": "0.4.3",
        "candidate_concept_id_recall": by_kind,
        "faithfulness": [],
        "scope": "ID candidate coverage, not passage relevance; semantic sample is development-only and not judge calibration.",
    }
    config, inputs, predictions = (
        read(OUT / "config.json"),
        read(OUT / "classification-inputs.json"),
        read(OUT / "predictions.json"),
    )
    for rid in config["judge_cases"][:3]:
        prediction = predictions["primary:" + rid]
        if prediction["status"] != "PASS":
            raise ValueError("Repair producer contract failure before judging")
        assignments = prediction["call"]["result"]["assignments"]
        claims = [
            "The repository's primary "
            + (
                "initiative relationship is "
                if a["kind"] == "PROJECT"
                else "capability is "
                if a["kind"] == "TOPIC"
                else "technology is "
            )
            + registry[a["concept_id"]]["name"]
            + "."
            for a in assignments
        ]
        if not claims:
            output["faithfulness"].append(
                {"id": rid, "status": "NOT_APPLICABLE_NO_POSITIVE_CLAIMS", "calls": 0}
            )
            continue
        definitions = "\n".join(
            registry[a["concept_id"]]["name"] + ": " + registry[a["concept_id"]]["description"]
            for a in assignments
        )
        question = (
            "Which primary repository relationships/capabilities/technologies are supported? Candidate meanings (not repository facts):\n"
            + definitions
        )
        contexts = [e["id"] + ": " + e["text"] for e in inputs[rid]["payload"]["evidence"]]
        llm = GuardedLLM(rid)
        result = await Faithfulness(llm=llm).ascore(
            user_input=question, response=" ".join(claims), retrieved_contexts=contexts
        )
        output["faithfulness"].append(
            {
                "id": rid,
                "status": "MEASURED",
                "value": result.value,
                "calls": llm.calls,
                "claims": claims,
                "actual_supplied_evidence_only": True,
            }
        )
        (OUT / "ragas-results.json").write_text(
            json.dumps(output, indent=2, allow_nan=False) + "\n"
        )
    (OUT / "ragas-results.json").write_text(json.dumps(output, indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {"candidate_id_recall_matches_local": True, "faithfulness": output["faithfulness"]},
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stub", action="store_true")
    asyncio.run(main(parser.parse_args().stub))
