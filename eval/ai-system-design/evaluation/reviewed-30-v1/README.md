# Reviewed-30 evaluation, version 1

**Start here:** [How we evaluated GitHub Manager, in plain language](ground-truth-evaluation-explained.md). It explains every input and split, taxonomy versus classification, the algorithms, metric calculations and framework evidence, with nine figures and a thirty-case results table.

**Revision 2:** now includes the three-agent collection/English-first refresh history, all ten area counts, detailed internal performance tables and eight explicitly named Ragas checks. The separate [public illustration kit](public-illustrations/README.md) provides three hand-drawn explainers for sharing. The [previous complete guide/chart package](history/plain-language-evaluation-v1-2026-10-19.zip) is preserved.

Approved October 19, 2026. Evaluate the actual 30 human confirmations without changing app state, original corpus/proposals, prior benchmark paths or review history. Sources/owner decisions/receipts stay in the ignored `docs/validation/private/corpus-600-v2/evaluation-reviewed-30-v1/` directory.

See the [approved contract and schedule](../../../../docs/planning/ground-truth-evaluation-completion-2026-10-19.md) and [completed results](../../../../docs/validation/ground-truth-evaluation-2026-10-19.md). The run used all 50 generation/100 HTTP attempts, recorded $0.133941 estimated charges, and its grant is FINISHED. Do not renew it or dispatch additional generations without explicit user approval.

From the repository root:

```sh
backend/.venv/bin/python eval/ai-system-design/evaluation/reviewed-30-v1/runner.py freeze
backend/.venv/bin/python eval/ai-system-design/evaluation/reviewed-30-v1/runner.py offline --all-corpus
backend/.venv/bin/python -m pytest eval/ai-system-design/evaluation/reviewed-30-v1/test_evaluation.py -q
```

The freeze refuses to replace an existing reference. It preserves historical registry contexts, snapshots effective definitions and separates producer requests from human reference labels. Reproduction checks immutable input/producer hashes. Deterministic extraction/candidate diagnostics need no login, API key or network.

`live.py` delegates to the existing guarded LangChain provider and original monetary ledger, with an explicit evaluation run grant. A separate SQLite counter records durable per-batch/total attempt bounds; it is not a new monetary ledger and cannot reset historical spend. Failed count/generation admissions also consume the conservative attempt allowance. Narrative-media reservations and copied-demo increments count towards the existing cumulative ceiling. Live calls are authorized only for this fixed schedule; do not use the script as an unrestricted provider client.

`scoring.py` reports reviewed-positive recall, judgement coverage and unjudged predictions. Unknown is never silently converted to negative. Exhaustive precision/F1 stays unavailable until the corresponding reference scope is explicitly adjudicated. Full-corpus diagnostics do not turn 570 unreviewed proposals into gold.

The production app remains on its shipped TF-IDF/RAKE baseline. BM25 and larger candidate lists are diagnostic comparisons, not unreported production changes. Test-reserved generation requires an explicit configuration freeze receipt. No references are prefilled as manual app associations to inflate scores.

## Replay and inspect the completed experiment

From the repository root, these commands use saved evidence and make no provider requests:

```sh
backend/.venv/bin/python eval/ai-system-design/evaluation/reviewed-30-v1/write_results.py
backend/.venv/bin/python eval/ai-system-design/evaluation/reviewed-30-v1/finish_checks.py
backend/.venv/bin/python eval/ai-system-design/evaluation/reviewed-30-v1/preservation_check.py
RAGAS_DO_NOT_TRACK=true LANGSMITH_TRACING=false .tools/evaluation-venv/bin/python eval/ai-system-design/evaluation/reviewed-30-v1/ragas_worker.py --stub
```

`finish_checks.py` cross-checks all thirty Promptfoo per-case scores and weighted Ragas candidate-ID scores against the local scorer. It also creates explicitly exploratory representation/budget diagnostics and measures stored timings/usage. It does not create an LLM provider. `preservation_check.py` compares 2,423 source/dossier hashes, 548 prior artifacts, the archived publication and all raw workspace states against saved baselines. It separately verifies Ground Truth/sample states, thirty reference records and registry history. A final live GitHub sync changed that separate workspace during reporting; the script records that observation rather than rolling it back or claiming all workspace bytes stayed identical.

Promptfoo 0.124.1 is pinned with its complete npm dependency tree under [frameworks/](frameworks). To repeat its local saved-output replay using the installed isolated copy:

Create a separate configuration with the current provider paths first. This preserves
the original configuration and its historical hash:

```sh
backend/.venv/bin/python eval/ai-system-design/evaluation/reviewed-30-v1/prepare_frameworks.py \
  --output docs/validation/private/corpus-600-v2/evaluation-reviewed-30-v1/promptfoo-config-relocated.json
```

```sh
PROMPTFOO_DISABLE_TELEMETRY=1 PROMPTFOO_DISABLE_VERSION_CHECK=1 \
PROMPTFOO_CONFIG_DIR="$PWD/.tools/evaluation-promptfoo/state" \
PROMPTFOO_PYTHON="$PWD/backend/.venv/bin/python" PATH="$PWD/.tools/node/bin:$PATH" \
.tools/evaluation-promptfoo/node_modules/.bin/promptfoo eval \
  -c docs/validation/private/corpus-600-v2/evaluation-reviewed-30-v1/promptfoo-config-relocated.json \
  --no-cache --no-share --no-write --no-table --no-progress-bar -j 1 \
  -o docs/validation/private/corpus-600-v2/evaluation-reviewed-30-v1/promptfoo-results-relocated.json
```

The file provider has no live fallback. Its 30/30 success means contract validity, while its numeric score remains reviewed-positive recall. Framework replay does not request a replacement prediction when one is missing. Re-export aggregates only after checking any newly generated local artifact hashes:

```sh
backend/.venv/bin/python eval/ai-system-design/evaluation/reviewed-30-v1/export_aggregate.py
```

Ragas 0.4.3 and its compatible LangChain 0.3 dependencies are pinned in [requirements-ragas.lock.txt](requirements-ragas.lock.txt). The isolated environment passes `pip check`; application dependencies were not modified. Faithfulness uses the collections API. The installed version still requires the legacy IDBasedContextRecall export; a future framework upgrade must explicitly recheck that adapter and its no-network fanout test. Normal Ragas execution reuses saved judge receipts when present; do not remove receipts or enable new judge requests to reproduce an existing score.

Private `exceptions.md` and `exceptions.json` identify only the sixteen extra unjudged assignments and seventeen positive misses across twenty repositories. They do not invalidate the completed thirty human confirmations. Unknown labels remain unknown until an explicit human decision is recorded. The public [aggregate export](../../ground-truth-creation/evaluation-statistics-2026-10-19.json) excludes individual reference records and full source text.
