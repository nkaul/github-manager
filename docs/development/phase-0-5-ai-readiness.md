# Phase 0.5 AI readiness — local setup and reruns

Phase 0.5 implementation is approved. Public repository samples plus synthetic fixtures and a **$5 total OpenAI experiment allowance** are authorized. The current [results](../validation/phase-0-5-results.md) distinguish completed offline checks, ten successful limited API checks after credit restoration, and separately attributed Codex checks. Quality/coverage review remains open. Phase 1 remains separately gated.

## Installed local tools and configuration

Reuse Phase 0's Python 3.13 environment and repository-local uv. The `ai-pretest` dependency group is locked in `backend/uv.lock`: LangChain Core/OpenAI, OpenAI SDK, RAKE-NLTK, rank-bm25 and markdown-it-py. YAKE lives in a separate ignored environment, pinned with its transitive dependencies in `backend/requirements-ai-yake.txt`; it is not a production dependency. The installed YAKE artifact identifies AGPLv3/commercial licensing. RAKE uses project-authored stopwords and tokenizer callbacks; no NLTK data download is needed.

From the repository root, restore the approved local evaluation environments if necessary:

```bash
UV_CACHE_DIR=.tools/uv-cache .tools/bootstrap/bin/uv sync --project backend --group ai-pretest
UV_CACHE_DIR=.tools/uv-cache .tools/bootstrap/bin/uv venv .tools/yake --python backend/.venv/bin/python
UV_CACHE_DIR=.tools/uv-cache .tools/bootstrap/bin/uv pip sync --python .tools/yake/bin/python backend/requirements-ai-yake.txt
```

Preserve the existing `.tools/yake` environment if already installed. Do not recreate the spending ledger during dependency setup. Python 3.12–3.14 remains the project manifest range; this evaluation was actually run on 3.13.5.

`backend/.env` holds the server-only `OPENAI_API_KEY`, separate task/comparison models and evaluation limits. The key is never exposed through the UI. The file remains ignored and mode 0600. Current models are provisional:

| Role | Model | Comparison |
|---|---|---|
| Taxonomy | `gpt-6.1-sol` | `gpt-6-astra` |
| Classification | `gpt-6-luna` | `gpt-6.1-sol` |

Keep `AI_PRETEST_LIVE_ENABLED=false` in the file; enable it per approved CLI invocation below. Inherited alternate OpenAI destinations or enabled LangSmith tracing are rejected. Public/synthetic data is the only supported external data mode.

## Credential-free verification and offline algorithms

```bash
bash scripts/check-phase05.sh
PYTHONPATH=backend backend/.venv/bin/python -m app.pretest.ai --stage offline
```

Offline runs reuse the downloaded, SHA-pinned public corpus. A first approved download can use `--fetch-public`; this performs read-only GitHub calls and does not send data to OpenAI. Once frozen, a changed corpus, split, label set or registry is rejected rather than silently retuning held-out results. Read the [reference sheet](../validation/phase-0-5-reference-review.md) and provide corrections explicitly.

The current checkout already has an initialized experiment ledger. **Do not use `--init` again.** On a genuinely fresh first setup only, the first offline run accepts `--init` to establish the one experiment allowance. Existing/missing/mismatched state prevents accidental reinitialization; retain both `runs.sqlite3` and `docs/validation/private/ai-budget.local.json`. Do not delete or reset them to regain budget.

## Real provider access and benchmark

Initial calls returned HTTP 429 `credit_balance_exhausted`. After the user restored credit, Luna and Sol passed actual LangChain/API generation and ten limited calls completed. A subsequent 20-generation Luna round passed the primary-label preflight targets in 17.078 seconds. Total estimated spending is $0.052212, with no outstanding reservations. The current hard limit is 34 total generation attempts (14 before round 2 + 20 newly authorized), and it is reached. **Do not run more paid checks under this limit.** Each generation also made one prerequisite token-count request; these are recorded separately. The full benchmark commands below are documented for a separately agreed continuation; they will be blocked by the current count gate. No credit purchase or billing change is performed by the harness.

```bash
AI_PRETEST_LIVE_ENABLED=true PYTHONPATH=backend backend/.venv/bin/python -m app.pretest.ai --stage access --live
AI_PRETEST_LIVE_ENABLED=true PYTHONPATH=backend backend/.venv/bin/python -m app.pretest.ai --stage benchmark --live
PYTHONPATH=backend backend/.venv/bin/python -m app.pretest.ai --stage report
```

Successful access is required per model before its taxonomy/classification path runs. The benchmark reuses saved access outcomes; rerun `--stage access` explicitly after account access changes. Exit 2 indicates a blocked access/budget gate. A report-only run never generates model output.

Every generation goes through LangChain provider-native strict JSON Schema and a guarded official API client. The actual payload is counted with schema overhead before reservation. No implicit SDK/LangChain retries occur. Unknown charges retain their maximum reservation; a usage-bound violation stops future paid calls. One justified classification candidate expansion is bounded; repeated stability calls and development ablations use the same ledger. Results from cache are marked REPLAY.

The benchmark does not publish taxonomy, apply organization mappings, alter GitHub, deploy AWS infrastructure or replace DynamoDB/SQS. Browser login is unnecessary for public/synthetic CLI checks. No paid-run HTTP endpoint was introduced.

## Reports and review

Private, ignored mode-0600 artifacts are under `docs/validation/private/ai-pretest/`:

- `ai*.md` plus paired JSON: immutable actual run evidence, including blocked/failed attempts.
- `runs.sqlite3`: experiment-wide reservations, settled estimates and validated result cache.
- `public-corpus.local.json`, `frozen-corpus.local.json`, `offline.local.json`: source, split, reference and algorithm artifacts.
- `access.local.json`, `benchmark.local.json`: most recent access and benchmark outcomes.
- `dependencies.local.json`, `validation.local.json`: exact dependency/license inspection and actual check evidence.

`--stage report` regenerates [the sanitized consolidated report](../validation/phase-0-5-results.md). Detailed public README caches stay local. No raw prompts, READMEs, GitHub tokens or OpenAI keys are included in the shareable summary.

Public reference labels and phrase usefulness require independent review. Synthetic labels are authored fixtures, not evidence of broad production quality. Human review of taxonomy drafts uses relevance, support, hierarchy/type correctness, aliases/distinctness and useful logical projects (1–5 each). Provider metrics cannot replace that review or the later 100–200 repository benchmark.

## Limited continuation and supplementary Codex evidence

The completed `--stage limited --live` run froze three Luna cases (FastAPI, Orion Audit, Negated API), one paired Sol case, a 30-case Sol taxonomy draft, baseline/RAKE/YAKE checks on FastAPI, and one fresh repeat. It refuses silent reruns. The atomic SQLite reservation checks both the $5 cap and `AI_PRETEST_MAX_GENERATION_CALLS=14`, including rejected calls and restarts. No automatic retry or full benchmark followed the limited run.

At the user's request, `python -m app.pretest.ai.codex_check --run --task … --model …` used the existing ChatGPT login for three supplementary structured calls while API credit was unavailable. It enforces ChatGPT authentication, removes API-key environment variables, disables shell/browser/app features, supplies only public/synthetic evidence, checks for tool events, and saves private prompt/schema/event/output evidence. Two pre-inference CLI setup/sandbox failures are retained separately. Do not rerun completed auxiliary checks silently. This route does not validate the LangChain/API path or provide an API dollar-cost estimate. See [Codex results](../validation/phase-0-5-codex-results.md).

Reviewer sheets are `docs/validation/private/ai-pretest/extraction-review.md` (ten public samples) and `taxonomy-review.md` (separately attributed API and Codex drafts). Reference labels/registry semantics are already approved; the user said “looks ok” (qualitative acceptance); numeric scores were not supplied. Phase 1 remains unapproved.

## Latest authorized validation round

The user authorized up to 20 additional model calls. The unchanged primary-only prompt was applied to all 20 frozen evaluation cases with four isolated clients: 20/20 API contracts passed in 17.078 seconds. Aggregate precision 100%, recall 96.2%, micro-F1 98.0%; all planned per-kind preflight targets pass. Eight public cases scored 100% micro-F1; 12 synthetic cases scored 97.1%. Two measured misses (Telemetry, python) remain recorded. No labels/extractor outputs were changed, and no retry or expansion was attempted.

The cumulative ceiling is now 34 attempts: four rejected historical attempts, ten smoke calls and twenty newly authorized calls. Estimated spending totals $0.052212, with zero outstanding reservations. Further calls do not follow automatically. Recommend Luna classification and Sol taxonomy for review-first use; Astra/full paired Sol comparison, numeric human ratings, README-format noise correction, broader stability/compaction and independent production evaluation remain explicit limits. This reused corpus includes three previously reviewed cases and is not an independent production generalization estimate. Phase 1 remains unapproved. [Detailed results](../validation/phase-0-5-round-2-results.md).
