"""Supplementary ChatGPT-authenticated Codex checks, never an API benchmark substitute."""

import argparse
import json
import os
import shutil
import subprocess
import time
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict

from app.pretest.ai.chains import CLASSIFY_SYSTEM, TAXONOMY_SYSTEM, classification_input
from app.pretest.ai.corpus import load_corpus, registry
from app.pretest.ai.evaluation import metrics, organization_simulation
from app.pretest.ai.evidence import Retriever, compact
from app.pretest.ai.schemas import (
    Classification,
    TaxonomyDraft,
    validate_classification,
    validate_taxonomy,
)
from app.pretest.ai.settings import PRIVATE_ROOT
from app.pretest.ai.storage import digest, private_json


class CaseResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    repo_id: str
    classification: Classification


class BatchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cases: list[CaseResult]


DISABLED = (
    "shell_tool",
    "unified_exec",
    "apps",
    "browser_use",
    "computer_use",
    "view_image",
    "multi_agent",
    "skill_search",
    "workspace_dependencies",
    "sleep_tool",
    "unbounded_connection_retries",
)


def run(task, model, *, retry_sandbox_blocked=False):
    directory = PRIVATE_ROOT / "ai-pretest"
    local = json.loads((directory / "offline.local.json").read_text())
    review = json.loads((directory / "reference-review.local.json").read_text())
    if not review.get("approved") or review.get("corpus_hash") != local["corpus_hash"]:
        raise ValueError("Reference review must match the frozen corpus")
    codex = shutil.which("codex")
    if not codex:
        raise ValueError("Codex CLI unavailable")
    env = {
        k: v
        for k, v in os.environ.items()
        if k not in {"OPENAI_API_KEY", "CODEX_API_KEY", "OPENAI_BASE_URL", "OPENAI_API_BASE"}
    }
    auth = subprocess.run(
        [codex, "login", "status"], env=env, capture_output=True, text=True, timeout=20
    )
    if auth.returncode or "Logged in using ChatGPT" not in auth.stdout + auth.stderr:
        raise ValueError("Only the existing ChatGPT login is authorized for auxiliary checks")
    # At most the four named checks; re-execution requires an explicit new decision.
    root = directory / "codex"
    root.mkdir(mode=0o700, exist_ok=True)
    key = f"{task}-{model}"
    path = root / f"{key}.local.json"
    if path.exists():
        previous = json.loads(path.read_text())
        events_path = root / key / "events.local.json"
        events = json.loads(events_path.read_text()) if events_path.exists() else {}
        if not (
            retry_sandbox_blocked
            and previous.get("status") == "BLOCKED"
            and previous.get("seconds", 999) < 1
            and not events.get("stdout")
            and "failed to initialize in-process app-server client" in events.get("stderr", "")
        ):
            raise ValueError("Auxiliary check already attempted; retain its evidence")
        path.rename(root / f"{key}-sandbox-blocked.local.json")
        (root / key).rename(root / f"{key}-sandbox-blocked")
    cases, concepts = load_corpus(directory), registry()
    profiles = local["profiles"]["rake"]
    contexts = {}
    if task == "classification":
        chosen = [r for r in cases if r["split"] == "heldout"]
        retriever = Retriever(concepts, local["retrieval_choice"])
        payloads = []
        for repo in chosen:
            prof = profiles[repo["id"]]
            payload, contexts[repo["id"]] = classification_input(
                repo, prof, retriever.candidates(prof), concepts
            )
            payloads.append(payload)
        instruction = CLASSIFY_SYSTEM + "\nClassify every case exactly once, independently."
        schema = BatchResult
        payload = {"cases": payloads}
    else:
        chosen = cases
        instruction = TAXONOMY_SYSTEM
        schema = TaxonomyDraft
        payload = {"collection": [{"repo_id": p["id"], **compact(p)} for p in profiles.values()]}
    prompt = (
        "This is a bounded inference check. Do not use tools, inspect files, search, or edit. "
        "Use only the supplied public/synthetic evidence. Return the requested JSON.\n"
        + instruction
        + "\n"
        + json.dumps(payload, ensure_ascii=False)
    )
    work = root / key
    work.mkdir(mode=0o700)
    schema_path, answer_path = work / "schema.local.json", work / "answer.local.json"
    private_json(schema_path, schema.model_json_schema())
    private_json(work / "prompt.local.json", {"prompt": prompt})
    output = {
        "evidence": "LIVE_CODEX_CHATGPT_SUPPLEMENTARY",
        "task": task,
        "requested_model": model,
        "returned_model": None,
        "started_utc": datetime.now(UTC).isoformat(),
        "corpus_hash": local["corpus_hash"],
        "prompt_hash": digest(prompt),
        "schema_hash": digest(schema.model_json_schema()),
        "status": "RUNNING",
        "api_benchmark_eligible": False,
        "api_ledger_charge_usd": 0,
        "subscription_usage_cost_usd": None,
    }
    private_json(path, output, exclusive=True)
    command = [
        codex,
        "exec",
        "--ignore-user-config",
        "--ephemeral",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--model",
        model,
        "--cd",
        str(work),
        "--output-schema",
        str(schema_path),
        "--output-last-message",
        str(answer_path),
        "--json",
        "--color",
        "never",
        "-c",
        'forced_login_method="chatgpt"',
        "-c",
        'model_reasoning_effort="low"',
        "-c",
        'web_search="disabled"',
    ]
    for feature in DISABLED:
        command.extend(["--disable", feature])
    command.append("-")
    start = time.perf_counter()
    try:
        result = subprocess.run(
            command, input=prompt, env=env, text=True, capture_output=True, timeout=180
        )
        private_json(work / "events.local.json", {"stdout": result.stdout, "stderr": result.stderr})
        output["exit_code"] = result.returncode
        events = []
        for line in result.stdout.splitlines():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        items = [e.get("item", {}) for e in events if e.get("type") == "item.completed"]
        tool_items = [i for i in items if i.get("type") not in {"agent_message", "reasoning"}]
        output["tool_items"] = [i.get("type") for i in tool_items]
        output["usage"] = [e.get("usage") for e in events if e.get("type") == "turn.completed"]
        if result.returncode or not answer_path.exists() or tool_items:
            output["status"] = "BLOCKED" if result.returncode else "FAIL"
            output["reason"] = "CLI did not complete a tool-free structured response"
        else:
            os.chmod(answer_path, 0o600)
            answer = schema.model_validate_json(answer_path.read_text())
            if task == "classification":
                expected = {r["id"] for r in chosen}
                actual = [item.repo_id for item in answer.cases]
                if set(actual) != expected or len(actual) != len(expected):
                    raise ValueError("Missing/duplicate/unexpected case")
                gold = {r["id"]: r for r in chosen}
                records = []
                for item in answer.cases:
                    validate_classification(item.classification, contexts[item.repo_id], concepts)
                    predicted = [a.concept_id for a in item.classification.assignments]
                    records.append(
                        {
                            "id": item.repo_id,
                            "gold": gold[item.repo_id]["labels"],
                            "predicted": predicted,
                        }
                    )
                output["records"] = records
                output["metrics"] = metrics(records, concepts)
                output["organization_example"] = organization_simulation(
                    [i for r in records for i in r["predicted"]], concepts
                )
            else:
                validate_taxonomy(answer, {r["id"] for r in chosen})
            output["result"] = answer.model_dump()
            output["status"] = "PASS_STRUCTURAL_HUMAN_QUALITY_REVIEW_PENDING"
    except Exception as error:
        output["status"] = "BLOCKED" if isinstance(error, subprocess.TimeoutExpired) else "FAIL"
        output["error_type"] = type(error).__name__
    output["seconds"] = round(time.perf_counter() - start, 3)
    private_json(path, output)
    print(
        json.dumps(
            {
                "task": task,
                "model": model,
                "status": output["status"],
                "report": str(path),
                "seconds": output["seconds"],
            }
        ),
        flush=True,
    )
    return 0 if output["status"].startswith("PASS") else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", required=True)
    parser.add_argument("--retry-sandbox-blocked", action="store_true")
    parser.add_argument("--task", choices=("classification", "taxonomy"), required=True)
    parser.add_argument(
        "--model", choices=("gpt-6.1-sol", "gpt-6-luna", "gpt-6-astra"), required=True
    )
    args = parser.parse_args()
    allowed = {
        ("classification", "gpt-6.1-sol"),
        ("classification", "gpt-6-luna"),
        ("taxonomy", "gpt-6.1-sol"),
        ("taxonomy", "gpt-6-astra"),
    }
    if (args.task, args.model) not in allowed:
        parser.error("Outside the four supplementary checks")
    return run(args.task, args.model, retry_sandbox_blocked=args.retry_sandbox_blocked)


if __name__ == "__main__":
    raise SystemExit(main())
