"""Local reviewer sheets and separately attributed supplementary model evidence."""

import json
import os

from app.config import REPO_ROOT
from app.pretest.ai.corpus import registry
from app.pretest.ai.evaluation import metrics
from app.pretest.report import cell


def private_markdown(path, rows):
    # Reviewer annotations are owned by the user; regeneration must preserve them.
    if path.exists():
        return
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        stream.write("\n".join(rows) + "\n")


def reviews(directory):
    local = json.loads((directory / "offline.local.json").read_text())
    rows = [
        "# Phase 0.5 extraction usefulness review",
        "",
        "Status: HUMAN RATINGS PENDING. Score usefulness 1–5; check purpose, negation, "
        "technical terms and noise. Reference-label approval did not rate these phrases.",
        "",
        f"Corpus: `{local['corpus_hash']}`.",
        "",
        "| Public sample | RAKE top phrases | YAKE top phrases | Human score/comments |",
        "|---|---|---|---|",
    ]
    for ident, prof in local["profiles"]["rake"].items():
        if prof["source"] != "PUBLIC_GITHUB":
            continue
        values = [
            "; ".join(p["text"] for p in local["profiles"][method][ident]["phrases"][:4])
            for method in ("rake", "yake")
        ]
        rows.append("| " + " | ".join(cell(v) for v in (ident, *values, "PENDING")) + " |")
    private_markdown(directory / "extraction-review.md", rows)
    codex = []
    root = directory / "codex"
    for task, model in (
        ("classification", "gpt-6.1-sol"),
        ("classification", "gpt-6-luna"),
        ("taxonomy", "gpt-6.1-sol"),
        ("taxonomy", "gpt-6-astra"),
    ):
        path = root / f"{task}-{model}.local.json"
        if path.exists():
            codex.append(json.loads(path.read_text()))
    rows = [
        "# Phase 0.5 supplementary Codex checks",
        "",
        "Evidence: **LIVE_CODEX_CHATGPT_SUPPLEMENTARY**. User authorized this route while "
        "API credit was unavailable. Existing ChatGPT login, ephemeral CLI sessions, "
        "public/synthetic inputs, explicit JSON Schema and local semantic validators were used. "
        "No API key was supplied to this route; no API spending-ledger allowance was reset.",
        "",
        "Codex client instructions, batched context, model routing and subscription accounting "
        "differ from LangChain/API requests. These results establish supplementary feasibility; "
        "they cannot close API access, per-repository token/latency, compaction or model-choice "
        "gates. Requested model IDs are recorded; no returned snapshot ID was exposed. "
        "Elapsed time is for an entire CLI batch, not one repository. No tool-use events "
        "were observed in the completed checks.",
        "",
        "Reference labels/registry semantics were user-approved before these runs. Both "
        "classification batches contain the same 20 held-out cases: 8 public + 12 synthetic. "
        "No reference labels were included in prompts. Small support limits inference; "
        "errors below are relative to the frozen minimum expected label sets.",
        "",
        "| Requested model/task | Status | Whole-call seconds | Input / output tokens |",
        "|---|---|---|---|",
    ]
    for result in codex:
        usage = result.get("usage", [{}]) or [{}]
        item = usage[0] or {}
        rows.append(
            f"| {result['requested_model']} / {result['task']} | {result['status']} | "
            f"{result.get('seconds', '—')} | {item.get('input_tokens', '—')} / "
            f"{item.get('output_tokens', '—')} |"
        )
    rows += [
        "",
        "| Model | Kind | TP / FP / FN | Precision | Recall | F1 |",
        "|---|---|---|---|---|---|",
    ]
    for result in codex:
        for kind, item in result.get("metrics", {}).items():
            values = [
                "—" if item[k] is None else f"{item[k]:.1%}" for k in ("precision", "recall", "f1")
            ]
            rows.append(
                f"| {result['requested_model']} | {kind} | "
                f"{item['tp']} / {item['fp']} / {item['fn']} | " + " | ".join(values) + " |"
            )
    rows += [
        "",
        "## Public and synthetic slices",
        "",
        "| Model | Source | Repositories | Micro TP / FP / FN | Micro F1 |",
        "|---|---|---|---|---|",
    ]
    for result in codex:
        if result["task"] != "classification" or not result.get("records"):
            continue
        for public in (True, False):
            records = [r for r in result["records"] if r["id"].startswith("synthetic/") != public]
            item = metrics(records, registry())["ALL"]
            rows.append(
                f"| {result['requested_model']} | {'PUBLIC' if public else 'SYNTHETIC'} | "
                f"{len(records)} | {item['tp']} / {item['fp']} / {item['fn']} | "
                f"{item['f1']:.1%} |"
            )
    rows += [
        "",
        "## Classification disagreements with references",
        "",
        "| Model / case | Extra labels | Missing labels |",
        "|---|---|---|",
    ]
    concepts = registry()
    for result in codex:
        for record in result.get("records", []):
            extra = set(record["predicted"]) - set(record["gold"])
            missing = set(record["gold"]) - set(record["predicted"])
            if extra or missing:

                def labels(values):
                    return ", ".join(concepts[i]["name"] for i in sorted(values)) or "—"

                rows.append(
                    f"| {result['requested_model']} / {record['id']} | "
                    f"{cell(labels(extra))} | {cell(labels(missing))} |"
                )
    rows += [
        "",
        "Sol and Luna produced identical assignment sets on this batch; this single "
        "observation does not establish repeat stability or equal capability. A 20-proposal "
        "Sol taxonomy draft passed structural/support/hierarchy validation and awaits human "
        "rubric scoring. No Astra Codex check was started after API credit returned.",
        "",
        "Actual draft and phrase-review sheets are kept in ignored local storage: "
        "`docs/validation/private/ai-pretest/taxonomy-review.md` and `extraction-review.md`. "
        "Subscription dollar cost is unavailable; API cost is reported separately.",
        "",
        "References: [Codex structured execution]"
        "(https://learn.chatgpt.com/docs/non-interactive-mode), "
        "[authentication](https://learn.chatgpt.com/docs/auth).",
    ]
    review_path = directory / "quality-review.local.json"
    if review_path.exists():
        rows += [
            "",
            "## Subsequent user review",
            "",
            "The user reviewed the taxonomy/extraction sheets and said **looks ok**. "
            "This is qualitative acceptance; no numeric score is inferred. The user also "
            "requires primary labels only. Extra secondary labels remain errors against "
            "the original references. The clarified prompt has not been rerun under the "
            "reached API call ceiling; original results are preserved.",
        ]
    (REPO_ROOT / "docs/validation/phase-0-5-codex-results.md").write_text("\n".join(rows) + "\n")
    rows = [
        "# Phase 0.5 taxonomy draft review",
        "",
        "Status: HUMAN RATINGS PENDING. No draft was published. Rate relevance, evidence "
        "support, hierarchy/type, alias/distinctness and logical grouping, each 1–5. "
        "Record corrections, accepted/rejected concepts and reviewer identity.",
        "",
    ]
    drafts = [r for r in codex if r["task"] == "taxonomy"]
    limited = directory / "limited.local.json"
    if limited.exists():
        drafts.extend(json.loads(limited.read_text()).get("taxonomy", []))
    for draft in drafts:
        rows += [
            f"## {draft['requested_model']} — {draft.get('evidence', 'LIVE_PROVIDER')}",
            "",
            f"Status: {draft['status']}; rubric: PENDING.",
            "",
            "| Kind | Name / parent | Description | Supporting repository IDs | Decision |",
            "|---|---|---|---|---|",
        ]
        for proposal in draft.get("result", {}).get("proposals", []):
            rows.append(
                "| "
                + " | ".join(
                    cell(v)
                    for v in (
                        proposal["kind"],
                        proposal["name"] + " / " + (proposal["parent_domain"] or "—"),
                        proposal["description"],
                        ", ".join(proposal["supporting_repo_ids"]),
                        "PENDING",
                    )
                )
                + " |"
            )
        rows += ["", "Notes: " + draft.get("result", {}).get("notes", "No generated draft"), ""]
    private_markdown(directory / "taxonomy-review.md", rows)
