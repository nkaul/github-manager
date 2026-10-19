# Corpus 600: collection, reference review and offline validation

Date: October 16, 2026. Release: **public-corpus-600-2026-10-16-r1-PROPOSED**.

The approved collection is complete: **600 distinct public repositories, sixty in each of ten sampling domains**, with complete commit-pinned READMEs, selected supporting content and source-backed proposed annotations. Three agents performed collection and primary review; 120 different repositories received an independent source review. **No reference is human-approved yet.** This is a reviewable evaluation dataset, not a classifier accuracy claim or a gold release.

## What is available

Detailed data lives under the ignored, locally restricted `docs/validation/private/corpus-600/`. Begin with its [release guide](../../../../docs/validation/private/corpus-600/release/START-HERE.md), [inventory](../../../../docs/validation/private/corpus-600/release/inventory.csv) or [human review index](../../../../docs/validation/private/corpus-600/release/human-review/README.md).

The release includes separate inventory CSV/JSONL, model inputs, proposed labels, a canonical registry, provisional split manifest, current-app profiles, retrieval results, offline request previews, complete source-content reference JSONL and ten review sheets. Each dossier retains source/version/hash information, exact passages, actual reading scope, exclusions and uncertainty. Full source-content exports are for reference review; they are not model input. `manifest.local.json` binds the release files, source snapshots, dossiers and relevant application/tool versions with SHA-256 hashes.

The original [approval plan](../../../../docs/planning/public-repository-corpus-600.md) is preserved. Later approval and the third-agent instruction supersede its historical two-agent/awaiting-approval wording. Query catalogs and per-agent findings remain beside this report.

## Collection and composition

| Sampling bucket | Repositories | Supported Project membership¹ | Observed non-English/multilingual README² | Below 100 stars |
| --- | ---: | ---: | ---: | ---: |
| Healthcare | 60 | 31 | 7 | 43 |
| Finance | 60 | 30 | 3 | 40 |
| Commerce | 60 | 33 | 6 | 32 |
| Education/knowledge | 60 | 16 | 15 | 31 |
| Science/geospatial/climate | 60 | 20 | 4 | 6 |
| Data engineering | 60 | 23 | 6 | 2 |
| AI/ML | 60 | 12 | 10 | 4 |
| Cloud/DevOps | 60 | 30 | 9 | 11 |
| Security/identity | 60 | 22 | 9 | 22 |
| Developer platforms | 60 | 31 | 6 | 19 |
| **Total** | **600** | **248** | **75** | **210** |

¹ Counts repositories with at least one source-supported proposed relationship, not relationship count. Owner identity, a dependency and a search match do not establish membership. Sampling buckets do not assign Domains; those derive through Project parents. No supported Project means unknown membership against this registry, not a global negative.

² These observations come from actually reviewed narrative passages, not programming-language detection, translation links or a whole-file language classifier. They are a documented lower bound over inspected text. The global target of sixty is met; individual buckets such as finance and science fall short of six.

There are 376 distinct owners and 36 non-unknown GitHub language buckets, including artifact languages such as Markdown and Makefile; these are not 36 independently audited implementation languages. Python is the largest bucket at 136/600. The largest owner is Apache at sixteen, below the hard global cap of thirty. Disclosed soft-preference exceptions include thirteen OpenMF repositories in finance and seven Apache repositories in data. Popularity coverage is uneven, especially in AI, data and science.

The approximately 300 initiative-positive target produced 248 supported repositories rather than invented memberships. The intended independent/challenge mix is not a verified exclusive 300/240/60 partition; challenge annotations overlap and uncertainty remains. Discovery sampled up to thirty results per query and round-robin staged candidates. Among 179 successful cached search responses, two reported `incomplete_results`, and 92 had more than 1,000 results. Broad queries were **not exhaustively repartitioned or enumerated**. The corpus is search-driven and useful for diagnostic coverage, not representative of all GitHub repositories.

## Source integrity and review

- **600 complete READMEs + 1,162 supporting files**: 19,291,908 bytes in accepted records. All 1,762 files match stored lengths, SHA-256 and Git blob SHA-1, with immutable-commit directory binding verified.
- **78 READMEs fully read; 522 received targeted semantic reading.** Full raw retention does not mean every file was read completely. Supporting files not inspected remain explicitly unreviewed.
- **1,726 quoted source-evidence items** match recorded reading scope across whole-line, line-character and global-character producer formats. This is record consistency, not independent proof of comprehension.
- **120 independent reviews** bind current annotation/source hashes; no stale or same-author approvals remain. Five substantive/citation findings were corrected and re-reviewed: two learning-content type errors, an overbroad negative analysis claim, unsupported payment/maturity attribution and weak templating evidence. Earlier findings remain preserved. Additional final coordinate/read-scope corrections preserved source bytes and semantic labels. One duplicate optional reference to the primary nested README was removed with a metadata audit; its raw bytes and annotations were retained.
- The proposed registry contains **10 Domains, 64 Projects, 162 Topics and 99 Tags**. Kind-aware IDs distinguish technologies such as C/C++/C#. Seven self-duplicate or colliding aliases were removed from the proposed export with an audit; original catalogs remain unchanged. No canonical-name collision or conflicting Project parent remains in the export. Concept scope still needs human review.

Important exceptions are retained. Dagster's logical root README resolves a Git symlink; its exact link blob, resolved target bytes and corrected pinned citation path are recorded. A wrapper-like prefix in `vuejs/awesome-vue` is byte-consistent with its API/blob/directory evidence; its origin is not independently established, and it remains untrusted literal source text. Eight Trivy-family commit requests returned HTTP 403, leaving a family-coverage gap; the exact server cause is unknown. Integrity-failing README candidates were quarantined/excluded, while invalid optional supporting bytes were omitted with audits. A bot-directed destructive instruction in an off-domain README was treated only as text and never executed.

There are **179 unknown or NOASSERTION license records**. Repository license metadata can lag source notices and does not license linked books, datasets or external models. Raw copies remain local; no source redistribution was performed.

## Access and allowance

The existing OAuth App's credential-isolated public-data access passed authenticated probes; browser authentication was unnecessary. Agents used a loopback broker rather than receiving secrets. Fixed public GET endpoints, verified TLS, shared deduplication/cache/attempt accounting and live rate-limit checkpoints governed collection.

The authenticated execution ledger contains **5,391 HTTP attempts**, including **181 searches**, versus ceilings of 12,000/200. Outcomes: 5,376 HTTP 200, nine 403, five 404 and one 422; failures count toward allowance. Retained source accounting is **23,700,707 bytes**, including excluded/history material, below 1 GiB. All 600 accepted claims are accounted for; 131 rejected claims and preserved review exclusions explain unsuccessful candidates without adding them to the core corpus. The earlier anonymous confirmation pilot remains separately documented in the approval plan.

No paid model/judge API calls, GitHub mutations, AWS changes or application database changes occurred. The collection broker is stopped after handoff; saved data and offline tools remain usable.

## Offline results from the implemented pipeline

All 600 inputs passed the application's deterministic profile builder and its existing `tfidf` sparse candidate retriever with unchanged defaults. The implementation uses weighted lexical overlap and alias boosting; these results do not describe dense embeddings, neural reranking or Jev. The proposed registry was curated with corpus access, so this is not an unseen-registry generalization experiment.

| Type | Proposed supported positive labels | Retrieved within current per-type candidates | Positive recall |
| --- | ---: | ---: | ---: |
| Project | 252 | 249 | 98.81% |
| Topic | 689 | 436 | 63.28% |
| Tag | 634 | 606 | 95.58% |

These denominators are **agent-proposed positives, not human-approved gold**. Unknown/unlisted labels are not negatives, so precision and F1 are intentionally absent. Technology references partly use the same metadata supplied to retrieval and are therefore input-correlated. No generations or judge evaluations were run, and no generation accuracy, calibrated confidence or semantic faithfulness score is established.

Of 1,575 supported positive labels, 1,571 have at least one README/metadata evidence channel; four rely only on supporting sources the application does not receive. Lexical quote-token containment is found for 1,293 labels in the extracted profile and 1,035 in the compact payload. These are **omission diagnostics**, not entailment tests: text cleaning, equivalent wording and token matching affect the count. Saved compact requests are deterministic offline reconstructions for a fresh isolated workspace, not transmitted requests or real-account wire captures.

The practical next investigation is Topic candidate loss, followed by evidence packing. Use the development split to inspect missing IDs and relevant passages before changing aliases, ranker fields, candidate cutoffs or excerpt selection. Compare any improvement against this unchanged baseline; do not tune on reserved test examples.

## Splits, tests and the remaining reference gate

The provisional allocation is **180 development / 120 validation / 300 test-reserved**, using 362 groups. Related Projects, known lineage, exact README copies, conservative shared-owner groups and detected near-duplicates remain together; every saved grouping edge stays within one split. The largest connected group has thirty repositories. Near-duplicate screening uses five-word shingles, bounded bottom-hash candidates and Jaccard ≥ 0.8; it is not exhaustive. Shared-owner grouping reduces leakage without asserting Project membership.

Twelve offline tooling tests passed, covering pinned public endpoints, atomic allowance/cache behavior, corrupt-source rejection, optional-file omission, nested-README deduplication, distinct IDs, input/label separation, independent current review bindings, CRLF coordinates and the three reading-scope schemas. Assembly, directory binding, reading-scope, inventory uniqueness and split-edge checks all passed. Existing app defaults and earlier benchmarks were preserved.

Before promoting this dataset to the primary quality benchmark: review registry definitions and the ten reference sheets, record actual human decisions and any missing-positive/negative/unknown masks, resolve remaining scope ambiguities, then freeze a version and lock the test groups. Only afterward should bounded paid classification or judge evaluation be planned. Keep synthetic/unit fixtures for controlled privacy, negation, budget, race, reset and recovery cases. **No fixture replacement or model-quality certification is implied by collection completion.**

Reproduction commands and artifact navigation are in the [methodology README](README.md) and local release guide. Reassembly changes generated artifacts and therefore requires a new manifest/version before another benchmark is reported.
