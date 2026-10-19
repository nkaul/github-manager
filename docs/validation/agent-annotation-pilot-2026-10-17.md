# Agent annotation pilot: results and human-review handoff

Date: October 17, 2026. Status: **30 development repositories independently annotated twice; proposals ready for human review.** This is not a completed human ground-truth set or a production classifier benchmark.

**October 18 status check:** the app's read-only pilot integrity adapter returns `READY` / `INDEPENDENT_PROPOSALS_AWAITING_HUMAN_REVIEW` for all thirty repositories. The real local application database contains zero saved human reviews and zero incomplete review drafts. The initial twenty-card queue is ready. The subsequently authorized [live workspace redesign](live-workspace-redesign-2026-10-17.md) is implemented; its draft and confirmation workflow supersedes the original preview-only restrictions below. Pilot proposals and source bindings remain unchanged. Frontend and backend health checks return HTTP 200.

**Later October 18 update:** independent A/B summaries are now prominent, nonpilot coverage is explicit, and the initial twenty/full thirty-case queue stays selected through **Confirm & next**. See the [visibility and navigation verification](ground-truth-agent-inputs-2026-10-18.md). The real database now contains four human reviews, all outside the pilot; the earlier zero-review count above is a historical snapshot. The independent pilot still awaits human review. No agent annotation or source release changed.

The user authorized the pilot and app visibility, then chose the Codex agents' existing intelligence instead of additional provider API calls. Two independent agents performed the semantic work. A deterministic coordinator selected the sample, checked evidence integrity and compared their outputs. See the [execution record](../planning/agent-annotation-pilot-execution.md) and [methodology/schema guide](../../ai-system-design/evaluation/annotation-pilot/README.md).

## What was read and saved

The sample contains three development repositories from each of the ten sampling domains. Selection used a fixed SHA-256 ordering of repository IDs, without inspecting expected labels, old purposes or production predictions. No validation/test repository was included.

| Item | Result |
|---|---:|
| Selected repositories | 30 |
| Independent annotations | 60 |
| Known registry concepts available to both readers | 337 |
| Complete saved READMEs supplied | 30 |
| Retained supporting files supplied | 66 |
| Whitelisted saved GitHub metadata snapshots supplied | 30 |
| Total supplied source channels | 126 |
| Source-channel bytes across the thirty packets | 810,821 |
| Annotator A positive labels | 153 |
| Annotator B positive labels | 187 |
| Shared positive repository/concept decisions | 148 |
| A-only / B-only decisions | 5 / 39 |
| Additional external model API requests | 0 |
| Incremental external API spend | $0 |

Codex-agent allowance/token consumption is **unmeasured**, not zero. Producer records do not invent API receipts or an exact model identity unavailable to the agents. Independent reading turns do not guarantee different base models or independent errors.

Release manifest SHA-256: `64ddf1ff160eb817a965f88030dbdd68b4651e1557c5f530f2cdf2898092a14f`. Selection SHA-256: `750dc71e20fdc528e4ea4ca5c309a5bb103aaa89e91fbedf03f1900c2420ce49`.

The agents received source-first packets and the full registry. They did not receive the original corpus proposals, each other's answers, production predictions or the production retriever's shortlist. Repository instructions embedded in evidence were treated as untrusted content. Sources are retained snapshots, not a claim that the entire live GitHub repository was collected.

## Reading scope is explicit

Annotator B reports reading all 126 supplied channels. Annotator A reports reading 109: all thirty READMEs, metadata, supporting prose and configuration/manifests, with seventeen license/trademark-license artifacts left unread. A therefore declares complete supplied scope for fourteen repositories and PARTIAL scope for sixteen. It does not claim the unread licenses were reviewed.

The coordinator verifies coverage interval structure and complete-declaration consistency. It cannot prove semantic understanding from a reading ledger. Exact quotations and valid IDs also do not establish that a quoted fact entails a particular label. Human adjudication remains necessary.

A's further structured knowledge and exclusion notes are retained under [annotations/a](private/corpus-600-v2/annotation-pilot/annotations/a/); B's independent rows and audit history are under [annotations/b](private/corpus-600-v2/annotation-pilot/annotations/b/). The app exposes the validated purposes, labels, evidence, conflicts, missing concepts, caveats and declared scope. Extra reader working notes remain local audit artifacts.

## Multiple associations are supported

There is no one-label-per-kind restriction. Primary purpose can support multiple Topics; primary implementation can support multiple Tags; distinct evidenced initiative relationships can support multiple Projects. Assigned Domains are the union of all retained Project parents. A sampling domain never imposes an assignment.

| Observation | Annotator A | Annotator B |
|---|---:|---:|
| Project decisions | 17 | 17 |
| Topic decisions | 77 | 100 |
| Tag decisions | 59 | 70 |
| Repositories with multiple Topics | 23 | 29 |
| Repositories with multiple Tags | 20 | 25 |
| Repositories with multiple known Projects | 0 | 0 |

No selected packet supported two **known registered** families strongly enough for either reader to assert both. Missing own/secondary initiatives are recorded as missing concepts instead of forced into a nearby family. This is an evidence/registry outcome, not an application cap. A synthetic contract test verifies retaining multiple Projects, Topics and Tags and deriving both Domain parents. The design preview demonstrates the same relationship with a clearly synthetic example.

## Agreement and the initial review queue

The exact full label set agrees for five of thirty repositories. Per-kind exact set agreement, including cases where both chose no known Project, is 28/30 for Projects, 10/30 for Topics and 19/30 for Tags. These are descriptive agreement counts, **not precision, recall, F1 or accuracy against human truth**. Unlisted labels remain unknown.

The conservative evidence bands are two Green, twelve Amber and sixteen Red. Red here is triggered by A's incomplete supplied reading, which is license-only after its follow-up. It must not be interpreted as sixteen repositories with missing semantic documentation or sixteen proven incorrect annotations. This exposes a next-step improvement: distinguish required semantic evidence from incidental retained artifacts in a predeclared relevance policy, while preserving honest whole-packet coverage. Do not silently regrade this run to improve its headline.

The twenty initial human-review cards are:

- **10 risk-selected cases**, selected by the documented band/disagreement policy.
- **2 random Green agreement cases**; only two met the strict Green criteria.
- **8 deterministic random fill cases**, recorded separately rather than mislabeled as Green agreements.

All thirty pilot repositories remain accessible. Reviewing only disagreements would miss shared mistakes. Random-fill outcomes must remain separate from the Green audit and targeted-risk outcomes.

Useful adjudication questions include whether deployment tooling, Docker/Node.js, data ingestion, accounting or bundled commerce modules are primary capabilities/technologies rather than incidental implementation detail. For example, the Backstage demo and deployment repositories have differing purpose/capability interpretations; Lago has differing secondary technology/capability choices. Retain the source and definition beside each decision instead of choosing the longer label list automatically.

## Use the app for human review

1. Open **http://127.0.0.1:3000**, sign in again after the backend restart, and choose **Public - Ground Truth** from the workspace selector.
2. Set **Repository review scope → Initial human review · 20**, then open a repository from the queue. Alternatively, open **Annotation pilot · 30** (or **Open Agent A/B pilot queue** in a repository's availability notice) and click **Review** on a card. Opening a card sets the corresponding initial twenty-case or full thirty-case scope and clears conflicting search/status/taxonomy filters. **Confirm & next** stays within that scope. **All repositories · 600** remains available for browsing the wider corpus.
3. The **Agent A & B inputs** section now appears immediately below repository metadata, with both purpose summaries and Project/Topic/Tag suggestions. Click its **Compare independent annotations** button for each annotator's rationale, exact evidence, agreed/differing labels, derived Domains, missing concepts and reading scope. Expand evidence and open the saved document or pinned metadata. Original corpus proposals remain separately available in **Original proposed labels**. Repositories outside the thirty-case pilot explicitly say that they do not have Agent A/B annotations; their original recommendations are not independent agreement.
4. Optionally choose **Stage annotator A/B in my review**. This replaces only the editable form after an explicit choice, clears all three reviewed checks and leaves saved human records unchanged. Correct the purpose and retained known labels; multiple associations remain available. A missing registry concept belongs in notes/Unresolved until a separately versioned registry update.
5. New positives require exact matching evidence. The app attaches a saved-document or whitelisted pinned-metadata quotation where available. Metadata is visibly a separate channel, generated from the manifest-bound public snapshot; it is never presented as a README passage. Inspect incomplete or conflicting evidence before saving.
6. Deliberately check Projects, Topics and Tags, then choose **Confirm & next** to save a human confirmation and continue. Use **Save draft** for unfinished work or **Needs evidence** for an explicit unresolved decision. Purpose edits clear all checks; label/evidence edits clear the affected group. Export your own final decisions with **Export reviews**; incomplete drafts are separate from that export and from human-confirmed counts.

The current live interface includes **Confirm & next** and persistent incomplete drafts following the subsequent explicit redesign approval. Confirmation saves first and only then advances; a failed next-record fetch can be retried without repeating the save. Drafts restore separately from final human decisions, and revision conflicts retain local edits for explicit resolution. See the [live verification report](live-workspace-redesign-2026-10-17.md).

Human records remain owner-scoped in the existing SQLite database, default `docs/validation/private/demo/app.sqlite3`. Staged decisions save the pilot manifest hash alongside the original release/proposal/source binding, revision and history. A changed pilot binding is rejected. No agent automatically creates a HUMAN_CONFIRMED record. Unsaved navigation is guarded, stale detail/source responses cannot replace the selected case, and a failed summary refresh is distinguished from a successful save.

## Persistence and artifacts

The ignored [annotation-pilot folder](private/corpus-600-v2/annotation-pilot/) is separate from the immutable release. It contains:

- [Selection and source bindings](private/corpus-600-v2/annotation-pilot/selection.json), blind packets, registry and strict annotation schema.
- [Validated A](private/corpus-600-v2/annotation-pilot/agent-a.validated.json) and [validated B](private/corpus-600-v2/annotation-pilot/agent-b.validated.json).
- [App comparison sidecar](private/corpus-600-v2/annotation-pilot/review.json), [comparison report](private/corpus-600-v2/annotation-pilot/comparison-report.json), and [human-review queue](private/corpus-600-v2/annotation-pilot/human-review-queue.json).
- [Sidecar manifest](private/corpus-600-v2/annotation-pilot/manifest.json), which binds preparation, packets, schema, registry and published outputs. The app rechecks original release/source bindings and withholds proposals on integrity failure.

## Verification and preservation

- Full backend suite: **190 passed**, including twenty coordinator tests and six app integration/contract cases for explicit review, revision binding, multiple associations and exact pinned-metadata quotes.
- Browser workflows: **2 passed** on isolated ports 3015/8015 with a disposable identity/database. They cover real corpus browsing/sources, staging without writes or confirmation, metadata channel display, correction invalidation, dirty navigation, explicit save/history/export and workspace isolation. These are functional QA actions, not actual human annotation.
- [Pilot comparison screenshot](private/corpus-600-v2/app-review-artifacts/pilot-comparison-1080p.png), captured with the disposable QA identity and real validated public pilot proposals.
- Frontend lint, TypeScript and production build, plus backend Ruff: checked for the final changes.
- **4,849 manifest-bound release/evidence files** verified unchanged across original and V2 corpora. Existing API ledger and retained data/reviews in all three existing workspaces were fingerprint-checked unchanged.
- No new package, cloud resource, OAuth scope, external model call or budget reset. The app keeps its previous live-AI setting; this pilot never invokes it.

The related visual work is available in the [design review hub](http://127.0.0.1:8132/workspace-refinement/) and [shared refinement plan](../planning/workspace-ux-refinement-plan.md). Historical prototype checks remain preserved. The subsequent authorized live redesign passed seventeen main-app and five Ground Truth browser workflows, plus 121 backend demo tests, static checks and a production build. Its preservation checks verified 548 protected artifacts and both application/budget databases unchanged after tests and restart. These UI checks do not count as human annotation.

## Next decisions

Review the twenty cards, separating targeted and random outcomes. Resolve primary-capability/technology granularity and missing-family definitions before revising the registry. Use actual human corrections to assess the bands and required audit rate. Preserve explicit unknowns and review scope. Then decide whether to extend to the remaining ten pilot cases and a further bounded development batch; do not auto-promote the other 570 repositories, replace synthetic failure-mode fixtures or claim a locked benchmark result from agent agreement alone.
