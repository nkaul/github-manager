# Phase 0.5 supplementary Codex checks

Evidence: **LIVE_CODEX_CHATGPT_SUPPLEMENTARY**. User authorized this route while API credit was unavailable. Existing ChatGPT login, ephemeral CLI sessions, public/synthetic inputs, explicit JSON Schema and local semantic validators were used. No API key was supplied to this route; no API spending-ledger allowance was reset.

Codex client instructions, batched context, model routing and subscription accounting differ from LangChain/API requests. These results establish supplementary feasibility; they cannot close API access, per-repository token/latency, compaction or model-choice gates. Requested model IDs are recorded; no returned snapshot ID was exposed. Elapsed time is for an entire CLI batch, not one repository. No tool-use events were observed in the completed checks.

Reference labels/registry semantics were user-approved before these runs. Both classification batches contain the same 20 held-out cases: 8 public + 12 synthetic. No reference labels were included in prompts. Small support limits inference; errors below are relative to the frozen minimum expected label sets.

| Requested model/task | Status | Whole-call seconds | Input / output tokens |
|---|---|---|---|
| gpt-6.1-sol / classification | PASS_STRUCTURAL_HUMAN_QUALITY_REVIEW_PENDING | 67.318 | 24010 / 2648 |
| gpt-6-luna / classification | PASS_STRUCTURAL_HUMAN_QUALITY_REVIEW_PENDING | 20.287 | 23315 / 2838 |
| gpt-6.1-sol / taxonomy | PASS_STRUCTURAL_HUMAN_QUALITY_REVIEW_PENDING | 58.578 | 19557 / 2106 |

| Model | Kind | TP / FP / FN | Precision | Recall | F1 |
|---|---|---|---|---|---|
| gpt-6.1-sol | PROJECT | 10 / 0 / 0 | 100.0% | 100.0% | 100.0% |
| gpt-6.1-sol | TOPIC | 19 / 3 / 0 | 86.4% | 100.0% | 92.7% |
| gpt-6.1-sol | TAG | 23 / 1 / 0 | 95.8% | 100.0% | 97.9% |
| gpt-6.1-sol | ALL | 52 / 4 / 0 | 92.9% | 100.0% | 96.3% |
| gpt-6-luna | PROJECT | 10 / 0 / 0 | 100.0% | 100.0% | 100.0% |
| gpt-6-luna | TOPIC | 19 / 3 / 0 | 86.4% | 100.0% | 92.7% |
| gpt-6-luna | TAG | 23 / 1 / 0 | 95.8% | 100.0% | 97.9% |
| gpt-6-luna | ALL | 52 / 4 / 0 | 92.9% | 100.0% | 96.3% |

## Public and synthetic slices

| Model | Source | Repositories | Micro TP / FP / FN | Micro F1 |
|---|---|---|---|---|
| gpt-6.1-sol | PUBLIC | 8 | 16 / 4 / 0 | 88.9% |
| gpt-6.1-sol | SYNTHETIC | 12 | 36 / 0 / 0 | 100.0% |
| gpt-6-luna | PUBLIC | 8 | 16 / 4 / 0 | 88.9% |
| gpt-6-luna | SYNTHETIC | 12 | 36 / 0 / 0 | 100.0% |

## Classification disagreements with references

| Model / case | Extra labels | Missing labels |
|---|---|---|
| gpt-6.1-sol / fastapi/fastapi | fastapi, Data Validation | — |
| gpt-6.1-sol / encode/httpx | Command Line Interfaces | — |
| gpt-6.1-sol / pallets/flask | Templating | — |
| gpt-6-luna / fastapi/fastapi | fastapi, Data Validation | — |
| gpt-6-luna / encode/httpx | Command Line Interfaces | — |
| gpt-6-luna / pallets/flask | Templating | — |

Sol and Luna produced identical assignment sets on this batch; this single observation does not establish repeat stability or equal capability. A 20-proposal Sol taxonomy draft passed structural/support/hierarchy validation and awaits human rubric scoring. No Astra Codex check was started after API credit returned.

Actual draft and phrase-review sheets are kept in ignored local storage: `docs/validation/private/ai-pretest/taxonomy-review.md` and `extraction-review.md`. Subscription dollar cost is unavailable; API cost is reported separately.

References: [Codex structured execution](https://learn.chatgpt.com/docs/non-interactive-mode), [authentication](https://learn.chatgpt.com/docs/auth).

## Subsequent user review

The user reviewed the taxonomy/extraction sheets and said **looks ok**. This is qualitative acceptance; no numeric score is inferred. The user also requires primary labels only. Extra secondary labels remain errors against the original references. The clarified prompt has not been rerun under the reached API call ceiling; original results are preserved.
