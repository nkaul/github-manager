# github-manager
Framework for managing and organizing github repos

## Phase 0 local preflight

GitHub Manager now has a local Next.js/FastAPI OAuth App preflight. Start with the [localhost setup guide](docs/development/phase-0-localhost.md), [Phase 0 results](docs/validation/phase-0-results.md), and [implementation plan](docs/planning/implementation-plan.md).

From this checkout, run `bash scripts/dev-backend.sh` and `bash scripts/dev-frontend.sh` in separate terminals, then open http://127.0.0.1:3000. Configure the OAuth App in ignored `backend/.env`. Tokens stay in backend memory; access reports are Markdown.

Phase 0 is approved. Named private GitHub fixtures, organization discovery reconciliation, and eight authorized AWS scratch targets passed live checks; the scratch resources are retained at the user’s request. Review the Markdown results and remaining coverage limits before separately approving Phase 1.

## Phase 0.5 AI readiness preflight

Latest validation: [round 2 results](docs/validation/phase-0-5-round-2-results.md) — 20/20 LangChain/API calls passed in 17.078 seconds. Primary-label classification achieved 100% precision, 96.2% recall and 98.0% micro-F1; planned per-kind preflight targets pass. Total estimated experiment spending is $0.052212 of $5. The 34-attempt total ceiling is reached.

Validated server-only AI settings read `backend/.env`; `backend/.env.example` documents provisional models and limits. Live API calls remain disabled by default and require an explicit CLI flag plus environment override. The persistent SQLite ledger enforces the experiment allowance across reruns. Luna classification and Sol taxonomy are recommended preflight defaults. The outcome is CONDITIONAL GO for review-first AI; comparison/production-quality limits remain explicit. Phase 1 is unapproved.

## Phase 0.9 complete local app

The approved local application is implemented: GitHub OAuth and persisted exploration; taxonomy review/content management; manual, bulk and drag organization; rules; review-first AI; run history, activity and selective reset/restart. Cloud remains deferred.

Run `bash scripts/dev-demo.sh --live-ai`, then open **http://127.0.0.1:3000**. Use the [operator runbook](docs/development/phase-0-9-demo-runbook.md) and [actual validation report](docs/validation/phase-0-9-results.md). The [narrated 1080p walkthrough](demo-video.md) covers 26 chapters and 35 passed workflow checks. Start its chapter player with `python3 demo/tools/serve.py`, then open **http://127.0.0.1:8120**.

The completed recording used its original **20/20 HTTP requests**, with estimated cumulative spending **$0.060911/$5**. A subsequent user-authorized renewal restores a fresh **20-request / 10-generation window** while preserving lifetime history. Use **AI Organization → Manage API allowance** for renewal or selected limit overrides; see the [allowance guide](docs/development/ai-allowance.md). Sessions and organization resets cannot replenish it.

The October 13 refinement adds a Deep Purple Material palette, tree-first navigation, scoped compact KPIs, rounded tags, refined filters, automatic repository counts with exact preview, and operator-controlled adaptive run budgets. Adaptive mode defaults to $0.25 per run within the original cumulative $5 ceiling and can proceed after fixed-window exhaustion. See the [refinement report](docs/validation/phase-0-9-ui-and-ai-controls.md) and [current runbook](docs/development/phase-0-9-demo-runbook.md). The earlier video remains available with its original navigation.

The taxonomy/status update adds Projects, Topics and Tags browsing and assignment, distinct label coverage, grouped bulk review, durable AI analysis receipts, explicit previewed re-analysis for taxonomy/classification, and configurable automatic change thresholds. Previously analyzed repositories reconcile offline by default, including valid No match results; missing a Project does not trigger another paid call. See the [validation report](docs/validation/phase-0-9-taxonomy-and-analysis.md) and [ADR 0005](docs/adr/0005-durable-analysis-and-local-reconciliation.md). Earlier readiness reports, benchmarks, spending history and media are preserved.

Earlier pre-testing algorithms, tests, frozen samples, Markdown reports and all 34 historical API records are preserved. A protected local baseline and preservation verifier provide an audit. The original preflight entrypoint/UI remain usable. Run `bash scripts/check-phase09.sh` with ports 3000/8000 free for product and historical regression validation. No AWS resource or GitHub repository was changed.
