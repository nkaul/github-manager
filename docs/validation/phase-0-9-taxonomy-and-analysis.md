# Phase 0.9 — Taxonomy browsing, durable analysis and configurable automation

Date: October 13, 2026. Status: **PASS — implementation and local validation complete.**

Approved scope: [taxonomy/status plan](../planning/phase-0-9-taxonomy-browsing-and-status.md), including the user's requirement to retain explicit taxonomy/classification re-analysis and configure automatic change thresholds. Cloud infrastructure remains deferred. Architecture rationale: [ADR 0005](../adr/0005-durable-analysis-and-local-reconciliation.md). Usage: [current runbook](../development/phase-0-9-demo-runbook.md).

## Delivered behavior

### Durable analysis and deliberate re-analysis

- Classification and taxonomy have separate owner/repository receipts. Actual validated AI/replay success, including NO_MATCH, records AI completion per repository. Successes in a partially failed run remain recorded. Rules/manual assignments and deterministic fixtures do not manufacture real AI completion.
- Preview and the common worker enforce admission before provider construction/token counting. Ordinary classification reconciles successful, failed/uncertain and legacy-unrecorded repositories offline. Newly ingested repositories are explicitly NEW and can be admitted for first analysis. Manual selection and the legacy endpoint do not bypass the guard.
- **Live AI → Re-analyze with AI → reason → operation preview → Start reviewed run** intentionally refreshes taxonomy or classification. The exact cohort, prior inputs, generations/HTTP bound and conservative dollars are reviewable. The worker passes `fresh=True`; an identical provider cache key cannot suppress an explicitly requested refresh. Existing fixed/adaptive controls and the original $5 cumulative cap still apply.
- Transactional attempt claims prevent simultaneous dispatches for the same repository/operation. Interrupted/unknown remote attempts require explicit review/re-analysis. Successful responses leave historical receipts even if their association commit is stale; stale assignment references are discarded.
- History deletion, association changes, rejection, reload and restart retain compact receipts. Taxonomy/evidence/association resets invalidate incompatible stored assignments without granting new paid inference. Reset fences and current access remain authoritative.
- Local reconciliation applies approved rules and offers compatible stored assignments or canonical/alias matches among TF-IDF candidates for human review. Provenance distinguishes STORED_ANALYSIS, LOCAL_MATCH and LOCAL_RULES from actual AI. USER memberships and rejection tombstones retain precedence.

### Coverage, browsing and assignment

- Five compact cards: **In this view, Labeled, No project, Needs review, Selected**. Topics/tags count toward Labeled. No project retains its precise meaning of no active Project edge. Additional coverage shows repositories with Projects, Topics, Tags and no accepted labels; those sets can overlap.
- Repository rows show independent analysis status/freshness. Historical input fingerprints that cannot be reconstructed say **Input history unavailable**. Organization views include No labels, No project, Needs review, No AI match, Failed/blocked and Stale analysis.
- Sidebar and **Browse taxonomy** header menu expose **Projects | Topics | Tags**, alias search and distinct accepted/pending counts across accessible filtered repositories, independent of loaded pages. Projects retains the Domain → Project tree. Opening/changing modes starts no repository fetch; choosing a node does. Content settings cards include counts and **View repositories**.
- Both browsers accept repository drops onto Projects/Topics/Tags. A selected-row drag carries its explicit selected set; an unselected row carries only itself. Multi-repository additions show the exact set for confirmation. A Domain drop expands the Domain and opens an existing-Project picker; it never writes a direct Domain edge. Duplicate assignment is idempotent; existing memberships and AI receipts are preserved. Keyboard/mobile details and bulk controls remain available.
- Review can filter by type/concept/repository, group by repository/concept and show current memberships beside proposals. Selected acceptance/rejection has a review summary. The server validates all selected items against one snapshot, applies valid siblings and reports stale/missing/inaccessible items individually.

### Automatic trigger controls

Open **AI Organization → Automatic organization → Configure thresholds**. Settings persist across reload/restart and show current weighted changes, distinct entities, new projects and remaining waits.

| Setting | Default |
|---|---:|
| Weighted-change threshold | 6 |
| Distinct entities required with weight threshold | 3 |
| Alternative new-project threshold; zero disables | 2 |
| Change accumulation window | 900 seconds |
| Quiet period | 90 seconds |
| Cooldown between automatic runs | 1800 seconds |
| Eligible types | Create, Create Project, Edit, Archive, Merge, Rule, Evidence |

The condition is **weight AND entity count**, OR the enabled new-project count, followed by quiet/cooldown checks. Cosmetic edits are excluded. Consumed event sequences prevent repeating the same trigger. Automatic runs use the saved cohort/budget policy and the same durable admission guard: prior analysis reconciles offline, genuinely new eligible inputs can use AI. Thresholds **do not authorize automatic paid re-analysis**. The feature's existing on/off state was preserved.

## Validation evidence

| Check | Result |
|---|---|
| Complete backend suite | **157 passed** |
| New admission/re-analysis/reset/automation/coverage/bulk cases | **15 passed**, included above |
| Product browser suite | **12 passed**; isolated local routes, real session/CSRF, fixture external providers |
| Focused final navigation/re-analysis checks | **3 passed**; final 1080p/icon capture **2 passed** |
| Preserved original preflight browser suite | **4 passed** |
| Ruff formatting/lint | **PASS** |
| Frontend TypeScript and ESLint | **PASS** |
| Next.js production build | **PASS** |
| Production smoke | Frontend/backend 200; anonymous identity 401; OAuth configured; login visible; no page errors or horizontal overflow at 1920×1080 |

The new cases exercise zero provider construction on repeated classification; NO_MATCH success; explicit fresh inference for both operations; partial-run successes; atomic concurrent claims; uncertain restart recovery; stale response receipts; association/history/full-taxonomy/cache reset behavior; offline migration; independent label/Project coverage; cross-page counts/assignments; idempotence; invalid/archive/access rollback; per-item bulk review; durable input-access failures; dispatch checks after manual-decision changes; and configurable type/weight/entity/window/quiet/cooldown scheduling. Automatic reconciliation of previously analyzed repositories makes zero provider calls.

Browser checks cover selected-set drop confirmation, Domain picker, header/sidebar parity, alias search, all three facets, scoped cards, grouped filtered bulk review, explicit fresh-preview invalidation and persisted threshold settings. Existing responsive/focus/reduced-motion/contrast checks pass at 1920×1080, 1440×900, 1280×800 and 390×844. A new test initially assumed all three fixture proposals were Projects; the actual fixture correctly supplies two Projects and a Topic. The corrected test verifies both the filtered Project batch and the remaining Topic.

These tests use mock providers/transport and make **no new real quality-benchmark claim**. This validation made **zero generation reservations and zero application provider HTTP attempts**, verified against ledger timestamps after the pre-change backup. The existing model readiness/benchmark evidence remains authoritative.

Local review artifacts (ignored, fixture content): [Topics at 1080p](private/demo/taxonomy-status-20261013/taxonomy-topics-1080p.png), [automatic controls at 1080p](private/demo/taxonomy-status-20261013/analysis-controls-1080p.png), [full organizer capture](private/demo/taxonomy-status-20261013/analysis-controls-1920-fullpage.png), [responsive layout audit](private/demo/taxonomy-status-20261013/refinement-layout-audit.json), [production smoke](private/demo/taxonomy-status-20261013/production-smoke.json).

## Saved collection and preservation audit

The pre-change app database/source backup is under ignored `.tools/taxonomy-status-baseline-20261013`; no environment file was copied. Comparing saved workspaces with that database found **only additive analysis/schema fields and the corresponding workspace version increment**. Existing repository metadata, concepts/IDs/aliases, memberships, rules, suggestions, detailed runs, control preferences and audit history match the backup.

Read-only GitHub snapshot after migration: 310 accessible repositories; 17 labeled; 3 with Projects; 14 with Topics; 6 with Tags; 307 with no Project; 293 with no accepted labels. Backfill establishes **40 trustworthy AI successes** and **19 failed attempts**. Six repositories with old NO_MATCH outcomes have only local/non-model success evidence and were deliberately not counted as AI completion. Unrecorded/ambiguous inputs remain explicit and protected from automatic paid submission. Fifteen historical analyses have a different taxonomy revision and show an update available. These are dated collection measurements, not GitHub-wide completeness assertions.

Shared ledger snapshot: **91 cumulative generation reservations, 114 lifetime application HTTP attempts, $0.127619/$5 estimated spending, zero unresolved call reservation and zero run hold**. The existing fixed window is **0/50 HTTP attempts**. These counters predate this work; no allowance was renewed and no new calls were made during this validation. Check the live app for subsequent usage.

The original preservation verifier passes: **163 protected files**, original experiment row, **34 historical call rows**, **29 historical cache rows**, and an identical preflight UI copy. All **eight original media SHA-256/size records match**. Earlier Phase 0/0.5 reports, extraction/BM25/RAKE/YAKE tests, corpora, benchmark sources, model references, ledger/sentinel and narrated video/audio/captions were retained. Retained AWS scratch resources were not touched.

## Operational limits

The app is local and bounded to 30 repositories per AI run. Automatic runs reconcile their configured cohort, not the entire account. New collection-wide taxonomy output still requires review/publication; assignments still require review/acceptance. Local lexical proposals cannot guarantee correct new Projects/Topics/Tags.

The app cannot observe un-fetched upstream README changes. **Extract evidence** refreshes verified public metadata/README evidence with no model calls; observed changes can mark freshness stale and contribute EVIDENCE events. Private README-derived inputs remain excluded. Legacy input fingerprints are not reconstructed by guessing. Cloud webhooks/polling and infrastructure remain deferred.

The rebuilt production app runs at **http://127.0.0.1:3000**. Sign in again after the backend restart; persisted organization data remains available. The original video predates this UI revision and remains preserved as historical evidence.
