"""Build explanatory figures and selected evidence from saved results; no model calls."""

import csv
import hashlib
import json
import os
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
DATA = ROOT / "docs/validation/private/corpus-600-v2/evaluation-reviewed-30-v1"
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".tools/eval-report-mpl"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch

PAPER, INK, MUTED = "#fffdf8", "#16223c", "#52617b"
INDIGO, BLUE, TEAL, ORANGE, RED = "#3949ab", "#039be5", "#00897b", "#ef8b24", "#c95659"
GRID = "#e5e8ee"
plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 12,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": MUTED,
        "ytick.color": INK,
        "axes.edgecolor": GRID,
        "axes.facecolor": PAPER,
        "figure.facecolor": PAPER,
        "svg.fonttype": "none",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.spines.bottom": False,
    }
)


def read(name):
    return json.loads((DATA / name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(exist_ok=True, parents=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


FIGURES = []


def canvas(title, subtitle, *, size=(12, 5.7), left=0.24):
    fig, ax = plt.subplots(figsize=size)
    fig.subplots_adjust(left=left, right=0.93, bottom=0.22, top=0.73)
    fig.text(0.045, 0.93, title, fontsize=21, weight="bold", va="top")
    fig.text(0.045, 0.84, subtitle, fontsize=12, color=MUTED, va="top")
    ax.set_axisbelow(True)
    return fig, ax


def finish(fig, slug, footer):
    fig.text(0.045, 0.055, footer, fontsize=11, color=MUTED, va="bottom")
    folder = HERE / "figures"
    folder.mkdir(exist_ok=True)
    files = []
    for extension in ("png", "svg"):
        path = folder / f"{slug}.{extension}"
        fig.savefig(path, dpi=180, metadata={"Title": slug})
        files.append({"path": str(path.relative_to(HERE)), "sha256": sha(path)})
    FIGURES.append({"name": slug, "files": files})
    plt.close(fig)


def bar_labels(ax, bars, labels):
    for bar, label in zip(bars, labels, strict=True):
        ax.annotate(
            label,
            (bar.get_width(), bar.get_y() + bar.get_height() / 2),
            xytext=(7, 0),
            textcoords="offset points",
            va="center",
            fontsize=12,
        )


def main():
    summary, cases, predictions, config, ragas, inputs, registry = (
        read(name)
        for name in (
            "evaluation-summary.json",
            "reference-snapshot.json",
            "predictions.json",
            "config.json",
            "ragas-results.json",
            "classification-inputs.json",
            "registry.json",
        )
    )
    local, checks = read("local-results.json"), read("final-checks.json")
    assert summary["overall"]["ALL"]["selected_positives"] == 66
    assert summary["budgets"]["run_grant"]["state"] == "FINISHED"
    promptfoo = read("promptfoo-results.json")["results"]
    runs = []
    for row in promptfoo["results"]:
        rid = str(row["vars"]["repository_id"])
        case = cases[rid]
        predicted = set(predictions["primary:" + rid]["predicted_ids"])
        positives = set(case["positive_ids"])
        selected = len(positives & predicted)
        assert row["success"]
        assert abs(row["score"] - selected / len(positives)) < 1e-12
        runs.append(
            {
                "repository": case["name"],
                "repository_id": rid,
                "split": case["split"],
                "reviewed_positive_labels": len(positives),
                "positive_labels_retrieved": len(positives & set(case["candidate_ids"])),
                "positive_labels_selected": selected,
                "unjudged_predictions": len(predicted - positives),
                "reviewed_positive_recall": row["score"],
                "contract_pass": row["success"],
                "replay_model_tokens": row["response"]["tokenUsage"]["total"],
                "replay_cost_usd": row["response"]["cost"],
            }
        )
    assert len(runs) == 30 and sum(r["positive_labels_selected"] for r in runs) == 66
    runs.sort(key=lambda r: (r["split"], r["repository"].casefold()))
    judge_rows = []
    for result in ragas["faithfulness"]:
        rid = result["id"]
        matched = []
        for path in (DATA / "ragas-requests").glob("*.json"):
            if path.name.endswith(".result.json"):
                continue
            request = json.loads(path.read_text())
            if request["case_id"] == rid and request["schema"] == "NLIStatementOutput":
                response = json.loads(path.with_suffix(".result.json").read_text())
                matched = response["result"]["statements"]
        assert matched
        supported = sum(r["verdict"] for r in matched)
        assert abs(supported / len(matched) - result["value"]) < 1e-12
        judge_rows.append(
            {
                "repository": cases[rid]["name"],
                "claims_judged": len(matched),
                "claims_supported": supported,
                "score": result["value"],
                "statements": matched,
            }
        )
    split_file = ROOT / "docs/validation/private/corpus-600-v2/release/splits.provisional.json"
    full_splits = json.loads(split_file.read_text())["actual"]
    example_id = "886018089"
    example = {
        "repository": cases[example_id]["name"],
        "repository_id": example_id,
        "commit": cases[example_id]["commit"],
        "split": cases[example_id]["split"],
        "candidates_in_actual_order": inputs[example_id]["payload"]["candidates"],
        "human_retained_label_names": [
            registry[cid]["name"] for cid in cases[example_id]["positive_ids"]
        ],
        "saved_model_output": predictions["primary:" + example_id]["call"]["result"],
        "note": "One observed public-repository example. Full README text and owner identity are not exported. Evidence text in the Markdown is explicitly paraphrased.",
    }
    evidence_files = [
        "manifest.json",
        "test-freeze.json",
        "config.json",
        "classification-inputs.json",
        "evaluation-summary.json",
        "predictions.json",
        "taxonomy.json",
        "ragas-results.json",
        "promptfoo-results.json",
        "final-checks.json",
        "preservation-check.json",
    ]
    write(
        HERE / "evidence/observed-results.json",
        {
            "client_date": "2026-10-19",
            "source_run_capture_utc": summary["captured_at_utc"],
            "generation_calls_for_this_walkthrough": 0,
            "source_evidence_sha256": {name: sha(DATA / name) for name in evidence_files},
            "full_corpus_splits": full_splits,
            "reference_splits": dict(Counter(c["split"] for c in cases.values())),
            "reference_groups_by_split": {
                s: len({c["group"] for c in cases.values() if c["split"] == s})
                for s in ("development", "test_reserved")
            },
            "primary_replay_results": runs,
            "grounding_judge_results": judge_rows,
            "worked_example": example,
            "aggregate_results": {k: summary[k] for k in ("overall", "splits", "budgets")},
            "limits": "Selected single-reviewer positive references; extra predictions remain unknown. Software PASS is not a semantic quality gate.",
        },
    )
    (HERE / "evidence").mkdir(exist_ok=True)
    with (HERE / "evidence/repository-results.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(runs[0]))
        writer.writeheader()
        writer.writerows(runs)
    lines = [
        "# Thirty saved classification results",
        "",
        "October 19, 2026. These are actual saved-output results, not newly generated answers. A contract PASS means the IDs/evidence references meet software rules. Recall measures selected human-confirmed labels divided by all human-confirmed labels for that repository. Extras remain unknown, not errors.",
        "",
        "| Repository | Split | Human-confirmed labels | Found in shortlist | Selected positives | Extra unjudged | Recall of confirmed labels | Contract |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in runs:
        split = "Development" if row["split"] == "development" else "Test-reserved"
        lines.append(
            f"| [{row['repository']}](https://github.com/{row['repository']}) | {split} | "
            f"{row['reviewed_positive_labels']} | {row['positive_labels_retrieved']} | "
            f"{row['positive_labels_selected']} | {row['unjudged_predictions']} | "
            f"{row['reviewed_positive_recall']:.1%} | PASS |"
        )
    lines += [
        "| **All 30** | Both | **83** | **69** | **66** | **16** | **79.5%** | **30/30 PASS** |",
        "",
        "The total recall uses 66 divided by 83, not the average of the thirty percentages. No exhaustive accuracy/precision/F1 is claimed. Replay used zero new model tokens and zero generation charges.",
        "",
        "[Back to the plain-language explanation](../../ground-truth-evaluation-explained.md) · [Selected recorded evidence](observed-results.json) · [CSV](repository-results.csv)",
    ]
    (HERE / "evidence/repository-results.md").write_text("\n".join(lines) + "\n")

    # A reading guide: keep the human answer sheet outside the model's input path.
    fig, ax = plt.subplots(figsize=(13.5, 5.1))
    ax.axis("off")
    ax.set(xlim=(-0.55, 5.55), ylim=(-1.2, 1.35))
    fig.subplots_adjust(left=0.04, right=0.96, bottom=0.10, top=0.80)
    fig.text(
        0.045,
        0.94,
        "Follow a repository from evidence to a measured result",
        fontsize=21,
        weight="bold",
        va="top",
    )
    labels = [
        "Read saved\nrepository evidence",
        "Extract useful\nphrases",
        "Find possible\nexisting labels",
        "Pack evidence\nand label meanings",
        "Ask the model\nto choose labels",
        "Check the answer\nand calculate scores",
    ]
    details = [
        "Metadata + README",
        "RAKE · local code",
        "TF-IDF + alias boost",
        "Augmentation",
        "LangChain + Luna",
        "Rules + human comparison",
    ]
    for i, (label, detail) in enumerate(zip(labels, details, strict=True)):
        ax.add_patch(
            Circle((i, 0.35), 0.21, facecolor=INDIGO if i != 4 else TEAL, edgecolor="none")
        )
        ax.text(
            i, 0.35, str(i + 1), color="white", ha="center", va="center", fontsize=17, weight="bold"
        )
        ax.text(
            i, -0.01, label, ha="center", va="top", fontsize=11.6, weight="bold", linespacing=1.5
        )
        ax.text(i, -0.48, detail, ha="center", va="top", fontsize=9.5, color=MUTED)
        if i < 5:
            ax.add_patch(
                FancyArrowPatch(
                    (i + 0.25, 0.35),
                    (i + 0.75, 0.35),
                    arrowstyle="->",
                    mutation_scale=16,
                    color="#a3acca",
                )
            )
    ax.text(
        3.1,
        -0.96,
        "The saved human answer sheet enters only at comparison",
        color=INDIGO,
        ha="center",
        fontsize=12,
    )
    ax.add_patch(
        FancyArrowPatch((4.85, -0.89), (5, -0.45), arrowstyle="->", mutation_scale=16, color=INDIGO)
    )
    finish(
        fig,
        "00-classification-path",
        "Classification uses a fixed vocabulary. Taxonomy discovery is a separate experiment.",
    )

    fig, ax = canvas(
        "600 saved repositories; 30 with completed human reviews",
        "The reviewed set inherited its split from the larger collection.",
        size=(12, 5.5),
        left=0.25,
    )
    labels = ["Entire saved collection\n600 repositories", "Human-reviewed subset\n30 repositories"]
    for y, total, values in ((1, 600, [180, 120, 300]), (0, 30, [15, 0, 15])):
        left = 0
        for value, color, name in zip(
            values,
            [BLUE, "#b3bedf", INDIGO],
            ["Development", "Validation", "Test-reserved"],
            strict=True,
        ):
            width = 100 * value / total
            ax.barh(y, width, left=left, color=color, height=0.43)
            if value:
                ax.text(
                    left + width / 2,
                    y,
                    f"{name}\n{value}",
                    ha="center",
                    va="center",
                    color=INK if name == "Validation" else "white",
                    fontsize=11,
                    weight="bold",
                )
            left += width
    ax.set(
        yticks=[1, 0],
        yticklabels=labels,
        xlim=(0, 100),
        xlabel="Share of each separate dataset (%)",
    )
    ax.set_ylim(-0.55, 1.55)
    finish(
        fig,
        "01-dataset-splits",
        "The reviewed set includes no validation cases. The other 570 have no human-approved answers in this run.",
    )

    fig, ax = canvas(
        "Where did the 83 human-confirmed labels go?",
        "Count labels across repositories, not repositories themselves.",
        left=0.29,
    )
    values = [83, 69, 66]
    bars = ax.barh([2, 1, 0], values, color=["#a6b1d5", BLUE, INDIGO], height=0.48)
    ax.set(
        yticks=[2, 1, 0],
        yticklabels=["Human-confirmed labels", "Found in the shortlist", "Selected by the model"],
        xlim=(0, 100),
        xlabel="Number of the original 83 confirmed labels",
    )
    ax.xaxis.grid(True, color=GRID)
    bar_labels(ax, bars, ["83 / 83", "69 / 83 · 83.1%", "66 / 83 · 79.5%"])
    finish(
        fig,
        "02-label-recovery",
        "14 missed before generation + 3 missed after retrieval = 17 missed positives. Extras are counted separately.",
    )

    fig, ax = canvas(
        "Topics are the largest retrieval gap",
        "Each percentage uses the human-confirmed labels for that facet.",
        left=0.18,
    )
    kinds, names = (
        ["PROJECT", "TOPIC", "TAG"],
        ["Project · 15 labels", "Topic · 35 labels", "Tag · 33 labels"],
    )
    ys = [2, 1, 0]
    for offset, field, color, label in (
        (0.16, "retrieved_positives", BLUE, "Found in shortlist"),
        (-0.16, "selected_positives", INDIGO, "Selected by model"),
    ):
        vals = [
            summary["overall"][k][field] / summary["overall"][k]["reviewed_positives"] * 100
            for k in kinds
        ]
        bars = ax.barh([y + offset for y in ys], vals, height=0.27, color=color, label=label)
        bar_labels(
            ax,
            bars,
            [
                f"{summary['overall'][k][field]}/{summary['overall'][k]['reviewed_positives']}"
                for k in kinds
            ],
        )
    ax.set(
        yticks=ys,
        yticklabels=names,
        xlim=(0, 113),
        xlabel="Recovery of reviewed positive labels (%)",
    )
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.xaxis.grid(True, color=GRID)
    ax.legend(loc="upper left", bbox_to_anchor=(0, 1.10), ncol=2, frameon=False, fontsize=10)
    finish(
        fig,
        "03-facet-recovery",
        "12 of 35 confirmed Topics were absent from the model's candidate list. The model selected all 23 supplied Topics.",
    )

    fig, ax = canvas(
        "Development and test-reserved results",
        "These bars measure label recovery, not repository accuracy.",
        left=0.24,
    )
    for offset, field, color, label in (
        (0.16, "retrieved_positives", BLUE, "Found in shortlist"),
        (-0.16, "selected_positives", INDIGO, "Selected by model"),
    ):
        keys = ["development", "test_reserved"]
        rows = [summary["splits"][key]["ALL"] for key in keys]
        bars = ax.barh(
            [1 + offset, offset],
            [r[field] / r["reviewed_positives"] * 100 for r in rows],
            height=0.27,
            color=color,
            label=label,
        )
        bar_labels(
            ax,
            bars,
            [
                f"{r[field]}/{r['reviewed_positives']} · {r[field] / r['reviewed_positives']:.1%}"
                for r in rows
            ],
        )
    ax.set(
        yticks=[1, 0],
        yticklabels=[
            "Development\n15 repositories · 42 labels",
            "Test-reserved\n15 repositories · 41 labels",
        ],
        xlim=(0, 117),
        xlabel="Recovery of reviewed positive labels (%)",
    )
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.xaxis.grid(True, color=GRID)
    ax.legend(loc="upper left", bbox_to_anchor=(0, 1.10), ncol=2, frameon=False, fontsize=10)
    finish(
        fig,
        "04-split-results",
        "The test configuration was frozen before test generation. Prior vocabulary curation limits any unseen-data claim.",
    )

    fig, ax = canvas(
        "Could another local retrieval method find more labels?",
        "These are shortlist experiments only — no replacement model answers were generated.",
        size=(12.8, 6.0),
        left=0.36,
    )
    methods = ["alias", "tfidf", "bm25", "tfidf_expanded", "bm25_expanded"]
    labels = [
        "Alias-token matches only",
        "Current TF-IDF + alias boost",
        "BM25 + alias boost",
        "TF-IDF · twice the candidate limits",
        "BM25 · twice the candidate limits",
    ]
    vals = [local["rankers"][m]["ALL"]["retrieved_positives"] for m in methods]
    bars = ax.barh(
        list(reversed(range(5))),
        vals,
        color=["#a6b1d5", INDIGO, BLUE, "#6ea3c0", TEAL],
        height=0.55,
    )
    ax.set(
        yticks=list(reversed(range(5))),
        yticklabels=labels,
        xlim=(0, 92),
        xlabel="Human-confirmed labels retrieved (out of 83)",
    )
    ax.set_xticks([0, 20, 40, 60, 83])
    ax.xaxis.grid(True, color=GRID)
    bar_labels(ax, bars, [f"{v}/83 · {v / 83:.1%}" for v in vals])
    finish(
        fig,
        "05-retrieval-comparison",
        "Larger candidate lists can cost more and change generation behavior. No alternative was promoted into the app.",
    )

    fig, ax = canvas(
        "Ragas: is each model claim supported by its supplied evidence?",
        "Three development cases; a score was measured, with no automatic quality-pass threshold.",
        left=0.32,
    )
    bars = ax.barh(
        [2, 1, 0], [r["score"] * 100 for r in judge_rows], color=[TEAL, TEAL, ORANGE], height=0.48
    )
    ax.set(
        yticks=[2, 1, 0],
        yticklabels=["Airbyte platform", "Seldon Core", "Airbyte Python CDK"],
        xlim=(0, 120),
        xlabel="Claims judged supported in each response (%)",
    )
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.xaxis.grid(True, color=GRID)
    bar_labels(
        ax, bars, [f"{r['claims_supported']}/{r['claims_judged']} claims" for r in judge_rows]
    )
    finish(
        fig,
        "06-grounding-results",
        "Mean of the three case scores: 91.7%. A supported answer can still omit a human-confirmed label.",
    )

    fig, ax = canvas(
        "The reviewed sample is not balanced across domains",
        "The full collection has 60 repositories per bucket; this chart shows only the 30 reviewed ones.",
        size=(12, 6.6),
        left=0.23,
    )
    domains = [
        "data",
        "finance",
        "ai",
        "commerce",
        "education",
        "science",
        "security",
        "developer",
        "healthcare",
        "cloud",
    ]
    names = [
        "Data",
        "Finance",
        "AI",
        "Commerce",
        "Education",
        "Science",
        "Security",
        "Developer tools",
        "Healthcare",
        "Cloud",
    ]
    counts = Counter(c["sampling_domain"] for c in cases.values())
    bars = ax.barh(
        list(reversed(range(10))),
        [counts[d] for d in domains],
        height=0.55,
        color=[INDIGO] * 9 + [ORANGE],
    )
    ax.set(
        yticks=list(reversed(range(10))),
        yticklabels=names,
        xlim=(0, 12),
        xlabel="Human-reviewed repositories",
    )
    ax.set_xticks([0, 2, 4, 6, 8, 10])
    ax.xaxis.grid(True, color=GRID)
    bar_labels(ax, bars, [str(counts[d]) for d in domains])
    finish(
        fig,
        "07-review-coverage",
        "There is no reviewed cloud case. High scores in one- or two-repository slices cannot establish broad reliability.",
    )

    fig, ax = canvas(
        "What did this evaluation cost?",
        "Estimated recorded API charges, including all eight rejected adapter attempts.",
        left=0.31,
    )
    task = checks["task_usage"]
    values = [
        task["eval-classification-primary"]["charge_micros"],
        task["eval-classification-comparison"]["charge_micros"],
        sum(v["charge_micros"] for k, v in task.items() if k.startswith("taxonomy-")),
        sum(v["charge_micros"] for k, v in task.items() if k.startswith("eval-ragas-")),
    ]
    bars = ax.barh(
        [3, 2, 1, 0], [v / 1e6 for v in values], color=[INDIGO, BLUE, TEAL, ORANGE], height=0.48
    )
    ax.set(
        yticks=[3, 2, 1, 0],
        yticklabels=[
            "Primary classification · 38 attempts",
            "Comparison model · 3 attempts",
            "Taxonomy drafts + merge · 3 calls",
            "Ragas judges · 6 calls",
        ],
        xlim=(0, 0.082),
        xlabel="Estimated recorded US dollars",
    )
    ax.set_xticks([0, 0.02, 0.04, 0.06])
    ax.xaxis.grid(True, color=GRID)
    bar_labels(ax, bars, [f"${v / 1e6:.6f}" for v in values])
    finish(
        fig,
        "08-evaluation-cost",
        "Total: $0.133941 · 50 generation attempts · 100 HTTP attempts. This walkthrough adds zero model calls.",
    )
    write(
        HERE / "figures/manifest.json",
        {
            "source": "Saved October 19 evaluation results",
            "plotting_library": "matplotlib " + matplotlib.__version__,
            "figures": FIGURES,
        },
    )
    print(
        json.dumps(
            {
                "figures": len(FIGURES),
                "formats": ["png", "svg"],
                "replay_cases": len(runs),
                "new_model_calls": 0,
            }
        )
    )


if __name__ == "__main__":
    main()
