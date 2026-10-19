# Ground-truth creation: living publication package

> **Latest checkpoint — October 19, 2026: evaluations complete.** Thirty human-confirmed repositories retain 83 positives. Real classification recovers **66/83 (79.5%)**, with **69/83 (83.1%)** supplied by retrieval. Promptfoo replay and Ragas checks are complete. The approved 50-generation limit is exhausted; the new estimated charge is **$0.133941**. Read the [completed evaluation addendum](evaluation-results-2026-10-19.md), [aggregate statistics](evaluation-statistics-2026-10-19.json) and [detailed report](../../docs/validation/ground-truth-evaluation-2026-10-19.md). Unjudged extras remain unknown; exhaustive precision/F1 are unavailable. Revision 2 and its progress numbers below remain the preserved October 18 snapshot.

**Publication-ready local draft; not externally published.** Updated October 18, 2026, revision 2. The 22:09 America/New_York snapshot contains five real corpus confirmations, including one within the 30-case pilot and initial 20-case queue. Human review remains in progress. The package preserves previous articles and diagrams and does not modify frozen corpus, annotation, benchmark or application records.

Start with [the complete article](article.md). It explains the product problem, taxonomy semantics, corpus cleanup, two independent LLM-powered Codex readers, deterministic checks, real proposal disagreements, human review and the later evaluation plan. No extra external model call or separate judge is claimed.

## Files

| File | Purpose |
|---|---|
| [evaluation-results-2026-10-19.md](evaluation-results-2026-10-19.md) | Completed retrieval/classification/framework results and their interpretation, following the historical illustrated story. |
| [evaluation-statistics-2026-10-19.json](evaluation-statistics-2026-10-19.json) | Aggregate measured results, costs, token usage and private-evidence hashes; individual owner references excluded. |
| [article.md](article.md) | Main publishable living narrative, with current/planned boundaries. |
| [statistics.json](statistics.json) | Dated aggregate snapshot, source hashes, frozen experiment facts and separate live human-review counts. |
| [worked-example.json](worked-example.json) | Exact public-repository ID/commit/source bindings and observed canonical proposal sets; no human outcome invented. |
| [figures/](figures/) | Three new illustrated figures in the established paper/ink/marker style. |
| [figures/prompts.json](figures/prompts.json) | Complete built-in image-generation prompts, source references and export metadata. |
| [editorial-and-claim-review.md](editorial-and-claim-review.md) | Claims, caveats, refinement passes and QA limits. |
| [validation-evidence.md](validation-evidence.md) | Dated completed validation, detailed guarantees and proposed human/retrieval/classification protocol. |
| [verification.json](verification.json) | Link, exact-source, numerical and actual-export checks. |
| [scripts/refresh_statistics.py](scripts/refresh_statistics.py) | Read-only local aggregate updater; refuses to overwrite snapshots or write outside this package. |
| [scripts/verify_package.py](scripts/verify_package.py) | Reproduce source/agreement/link/image/history/article checks, optionally including current SQLite aggregates. |
| [Revision 1 archive](history/ground-truth-creation-2026-10-18-revision-01.zip) | Exact prior complete package before this update; [hash manifest](history/revision-01-preservation.json). |
| [Revision 2 update record](history/revision-02-update.md) | Changes, selected timestamped snapshot, preserved earlier counts and data-preservation checks. |

## Update this document safely

1. Capture a **new** snapshot without overwriting an old one. Revision 1's complete package is already archived, and its original statistics are also retained separately. From the repository root:

   ```sh
   python3 ai-system-design/ground-truth-creation/scripts/refresh_statistics.py \
     --output ai-system-design/ground-truth-creation/history/statistics-YYYY-MM-DD-N.json
   ```

   The script reads the existing frozen release/pilot and opens SQLite in read-only mode. It exports aggregate counts and hashes only. No credentials, actor identity, purpose text or individual human label decisions are exported. It makes no network or model requests. The private evidence files must exist on the author's machine; an external reader can inspect the public methodology and retained snapshot without possessing them.

2. Compare live corpus-review count, **pilot intersection**, initial-queue intersection, status and pilot-binding count. Do not copy the frozen sidecar's historical `human_confirmed: 0` into a live-progress claim. Multiple owner-scoped records are not automatically independent expert consensus or a globally deduplicated gold set.
3. To make a new snapshot the current `statistics.json`, first move the previous file to a unique dated history name, then run the updater with `--output ai-system-design/ground-truth-creation/statistics.json`. Update the article's date, status table and “Where we stand” section together. Record old/new counts and relevant policy/source changes in a dated note. User-facing calendar dates follow the supplied America/New_York client date; the machine capture timestamp is separate.
4. Preserve immutable sources, original proposals and previous human revisions. New taxonomy definitions require a new version and explicit re-review/rebinding where relevant. Never silently replace evidence under a published hash.
5. Keep **curation peer audits**, **independent annotation**, **human adjudication**, **functional UI tests** and **classifier/RAG evaluation** separate. They measure different things. Run a link/image/claim audit and inspect the actual exports after material edits.
6. Before reporting precision/recall/F1 or a confidence threshold, freeze the reference semantics: reviewed positives, reviewed negatives, unknowns, completeness and split boundaries. Before generalizing a correction rate, separate targeted and random sample outcomes with denominators and uncertainty.

Reproduce this revision's checks from the repository root:

```sh
python3 ai-system-design/ground-truth-creation/scripts/verify_package.py --check-live
```

This checks the article against the snapshot, recounts immutable pilot agreement and corpus statistics, checks evidence hashes and Markdown links, verifies the original package archive and unchanged illustration bytes/dimensions, and optionally compares live read-only review aggregates. It updates only `verification.json`. No app/browser tests, network requests or model calls run. If human review progresses after the snapshot, `--check-live` will correctly request a progress refresh; a dated historical snapshot is not a live counter.

The 57 backend and 12 Ground Truth suite checks cited in this revision come from the latest application validation report. They are not rerun by the publication verifier, are not summed with overlapping historical runs, and do not establish label correctness. The next human checkpoint is to complete the initial twenty-case review (one confirmed at this snapshot), analyze corrections and audit outcomes, then settle explicit reference completeness/negative semantics before conventional exhaustive classifier metrics.

No publisher, platform or hosting update is authorized or performed by this artifact task. Public READMEs can be quoted only briefly here; the article uses a short excerpt plus paraphrase and pinned-source links. Retained full source snapshots are not copied into this publication folder.

## Reuse the illustration/writing approach

This package applies [engaging-technical-writing](../../skills/engaging-technical-writing/SKILL.md) and [illustrated-explainers](../../skills/illustrated-explainers/SKILL.md), with the built-in imagegen skill/tool. Four built-in image-generation calls created three figures and a corrected third figure. These illustration calls are separate from the annotation experiment's zero-extra-provider-request claim; no app API key, annotation budget reset or direct provider API runner was used.

Use the prompts with a real style-reference image. Preserve authority boundaries: robots propose; deterministic software checks integrity; a person adjudicates; future evaluation stays visibly planned. Semantic objects—not architecture boxes—carry the explanation. A current review-count change should generally update prose/statistics rather than force a new illustration.

## Short publication description

An AI repository organizer needs a trustworthy answer key before its accuracy means anything. This case study follows six hundred public repositories into a thirty-repository double-annotation pilot, showing what two independent AI readers agree on, where they differ, what evidence checks can prove, and why human review still owns the final decision.
