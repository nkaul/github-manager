# Follow the data through taxonomy and classification

These examples use the retained Phase 0.5 public/synthetic records. **Provider answers are historical observations. Inputs are deterministic reconstructions whose logical cache keys match those saved calls.** Current LangChain request bodies were captured offline with a mock transport; original HTTP bodies were not retained.

The [provenance record](examples/provenance.json) contains source hashes and dependency versions. No model call, .env read, ledger initialization or live workspace mutation was performed. Gold labels appear only in separate evaluation fields, never in the model payloads.

## Artifact map

| Artifact | Inspectable content |
|---|---|
| [Taxonomy](examples/taxonomy.json) | Complete 30-repository payload, system instructions, schema, reconstructed serialized request and actual draft/usage |
| [Orion API](examples/orion-api.json) | Source metadata, full profile, lexical diagnostics, augmented payload, serialized request and actual answer |
| [FastAPI](examples/fastapi.json) | The public sample, retrieval distractors, actual compact-context weakness and recorded primary-label result |
| [Negated API](examples/negated-api.json) | High lexical scores for explicitly excluded initiatives, followed by the actual semantic classification |
| [Orion audit](examples/orion-audit.json) | A genuine saved two-Project classification of an authored fixture |
| [Unknown-empty](examples/unknown-empty.json) | A saved NO_MATCH response |
| [Registry](examples/registry.json) | The separately authored, approved 42-concept benchmark registry |
| [Prompts and schemas](examples/prompts-and-schemas.json) | Both complete application prompt constants and Pydantic JSON schemas |
| [Lifecycle replay](examples/lifecycle-replay.json) | A new in-memory application replay with simulated user actions, not historical user activity |
| [Reconstruction script](examples/reproduce.py) | Offline reproduction using existing dependencies and preserved local records |

Each classification artifact separates `source`, `profile`, `retrieval`, `payload`, `request`, `call` and `expected_labels_for_evaluation_only`. `call.result` is what the provider returned. `payload` is the human-message JSON, while `request` includes the system message, serialized response format and generation settings.

## 1. Start with source evidence

Orion is an authored synthetic initiative used in real API tests. Its API repository's Overview says:

> Patient intake API for the Orion Clinical Platform. Uses FastAPI and Python.

The selected profile retains two records:

```json
[
  {
    "id": "E0",
    "section": "GITHUB_METADATA",
    "text": "orion-api. Patient intake API for the Orion Clinical Platform. Uses FastAPI and Python. Topics: . Language: unknown"
  },
  {
    "id": "E1",
    "section": "overview",
    "text": "Patient intake API for the Orion Clinical Platform. Uses FastAPI and Python."
  }
]
```

The fixture's GitHub-style language field is null. Python is supported by its description/Overview, rather than invented metadata. E0 is the cleaned metadata representation; E1 is cleaned README text. IDs are local to this profile, not globally unique document IDs.

### Extraction and chunking

The current extractor uses CommonMark parsing and heading heuristics. H1 sections are enabled; certain purpose-related headings are included, while installation/license/changelog/usage-style headings are excluded. It keeps inline text, applies bounded cleanup and limits individual blocks to 700 characters, the selected README content to 8,000 characters and the metadata record to 600 characters. The README input ceiling is 262,144 bytes.

This is deterministic block selection, not semantic chunking or an LLM summary. The bounds can split sentences or omit important later evidence. The app's separately versioned wrapper removes observed RST directive/badge noise; it does not alter the frozen benchmark profiles.

### RAKE and YAKE

RAKE separates candidate phrases using punctuation and the project's stopword list, considers phrases of one to four words, and ranks them through word frequency/co-occurrence scores. The retained Orion phrases include `patient intake api` and `orion clinical platform`, both with score 9, and `fastapi`/`python`, each with score 1. Those scores are extraction weights, not relevance probabilities.

The profile checks that a phrase occurs in selected evidence and stores matching spans. For `patient intake api`, E1's span is `[0, 18)`; `orion clinical platform` occupies `[27, 50)`. Offsets refer to cleaned selected text, not original README lines or raw bytes. Current matching retains the first occurrence per evidence record, not every occurrence.

The compact request includes metadata, up to two selected README records and up to eight phrase strings. Full phrase scores/spans remain local. YAKE phrases from the saved offline comparison are exported in each case artifact; YAKE was not rerun and is not a second production inference layer. Repeated tokens and stopword removal can lose relationships, which is why source prose remains necessary.

## 2. Taxonomy discovery: decide the vocabulary

The recorded `taxonomy-limited` call used all 30 profiles: ten public repositories and twenty authored fixtures. Its human-message payload contains `source`, `private` and `collection`. Each collection entry contains `repo_id`, compact `evidence` and `phrases`.

For Orion API, the collection entry is:

```json
{
  "repo_id": "synthetic/orion-api",
  "evidence": [
    {"id": "E0", "section": "GITHUB_METADATA", "text": "orion-api. Patient intake API for the Orion Clinical Platform. Uses FastAPI and Python. Topics: . Language: unknown"},
    {"id": "E1", "section": "overview", "text": "Patient intake API for the Orion Clinical Platform. Uses FastAPI and Python."}
  ],
  "phrases": ["patient intake api", "orion clinical platform", "language unknown", "topics", "python", "orion-api", "fastapi"]
}
```

The model receives comparable records for the UI, booking, audit and other repositories, enabling collection-level proposals. **There is no canonical candidate retrieval step in this discovery call.**

The system instructions require reviewable DOMAIN/PROJECT/TOPIC/TAG proposals, supporting repository IDs, purpose-based Project relationships, deduplication and a proposed parent Domain for every Project. They prohibit auto-publication and GitHub changes. The complete prompt and schema are in the linked artifact. This one request did not execute a batch/consolidation loop.

The current application's planned-run path adds collection packing in `cohorts.taxonomy_collection`. It uses a conservative UTF-8-byte allowance derived from the input limit, leaves overhead for instructions/schema, prunes phrase lists and shortens evidence if the collection does not fit. Exact provider token counting remains the final gate. This is a current application mechanism, not a claim that the historical taxonomy request used that newer packing path.

The saved Sol answer contains 20 proposals. Two actual entries are:

```json
[
  {
    "kind": "DOMAIN",
    "name": "Clinical Operations",
    "description": "Software supporting patient intake, appointments and clinical operational workflows.",
    "aliases": ["Clinical workflow software"],
    "parent_domain": null,
    "supporting_repo_ids": ["synthetic/orion-api", "synthetic/orion-ui", "synthetic/orion-booking", "synthetic/orion-audit"]
  },
  {
    "kind": "PROJECT",
    "name": "Orion Clinical Platform",
    "description": "Connected patient intake API, dashboard, appointment scheduling and shared audit bridge.",
    "aliases": ["Orion"],
    "parent_domain": "Clinical Operations",
    "supporting_repo_ids": ["synthetic/orion-api", "synthetic/orion-ui", "synthetic/orion-booking", "synthetic/orion-audit"]
  }
]
```

Recorded counted input: **4,897 tokens**, including the request's instructions/schema. Recorded output: **2,106 tokens**, including 95 reasoning tokens. These are historical provider usage values, not new offline token estimates.

### From draft to canonical state

The app validates draft names, kinds, supporting IDs and hierarchy, then stores a reviewable draft. Review can edit concepts and aliases. Publication checks normalized same-kind terms against active and archived reservations, offers conflict details and opt-in remediation, resolves Project→Domain links and creates/reuses canonical concepts only after the user's action.

The taxonomy prompt requests at most 20 proposals; the general validator currently allows 50. That mismatch is an identified gap, not silently fixed by this article.

The later classification benchmark uses a **separately seeded approved registry**, not IDs minted from this saved draft. For example, its Orion Project is `p-orion` under Domain `d-health` (Healthcare), while the generated draft proposed Clinical Operations. The two traces demonstrate the same architectural division but are not one historical publish-and-classify run.

## 3. Classification: retrieve possible approved concepts

The benchmark registry contains four Domains and 38 searchable Projects/Topics/Tags. Search documents concatenate each concept's name, description and aliases. The repository query uses **all selected profile evidence**, not just the compact model input and not only RAKE phrases.

The app's method named `tfidf` uses binary term presence with IDF-weighted cosine:

```text
idf(w) = log((1 + N) / (1 + df(w))) + 1

cosine(Q, D) = sum(idf(w)^2 for w in Q ∩ D)
               / sqrt(sum(query weights^2) × sum(document weights^2))

score = cosine + 3 if any canonical-name/alias token set is contained in Q
```

Unseen query tokens receive weight 1 in the query norm. The alias boost applies once, even when several aliases match. Results with a positive score are ranked per kind, with deterministic ID tie-breaking and caps of 8 Projects, 10 Topics and 12 Tags. Domains are excluded. The script recomputes each score and asserts that the resulting shortlist equals the actual retriever's output.

Orion's complete shortlist is:

| Candidate | Kind | Cosine | Alias boost | Final score |
|---|---|---:|---:|---:|
| `p-orion` / Orion Clinical Platform | Project | 0.738168 | 3 | 3.738168 |
| `p-forge` / Forge Build Platform | Project | 0.111179 | 0 | 0.111179 |
| `t-api` / Web APIs | Topic | 0.119897 | 3 | 3.119897 |
| `t-packaging` / Package Management | Topic | 0.119067 | 0 | 0.119067 |
| `g-fastapi` / fastapi | Tag | 0.244630 | 3 | 3.244630 |
| `g-python` / python | Tag | 0.157589 | 3 | 3.157589 |

Scores are rounded here; full values and overlap tokens are in JSON. `platform` retrieves Forge weakly, while `python` retrieves Package Management. The Web APIs alias `FastAPI` supplies its boost. These are legitimate retrieval possibilities, not supported final assignments.

In the live app, candidates are also filtered against protected rejections, manual relationships, applicable approved rules and existing associations. This benchmark has no such user decisions. The in-memory lifecycle example demonstrates their effects separately.

BM25 and alias-only shortlists are exported for comparison. BM25 uses term-frequency saturation and length normalization; the cosine baseline collapses repeated tokens. The earlier development evaluation tied on candidate coverage, so the simpler cosine baseline was retained. Neither result establishes a winner on a broad corpus.

## 4. Augmentation: assemble what the LLM sees

The full Orion `payload` contains the two evidence records above, seven phrase strings, six candidate objects and trusted source/revision/hash/policy fields. Candidate objects contain only `id`, `kind`, `name` and `description`. Aliases help retrieval but are not included in those model-facing candidate objects. Reference labels are excluded.

The system message supplies the decision policy: only supported canonical IDs, primary-purpose Topics and primary implementation/dependency Tags; multiple Projects allowed; shared frameworks do not prove Project membership; respect negation and user decisions; cite supplied E IDs; no Domain assignments; use NO_MATCH or NEEDS_MORE_CONTEXT when appropriate.

LangChain binds the strict Classification schema. The serialized Responses request includes `model`, `input`, `max_output_tokens`, `reasoning`, `store: false`, `stream: false`, `service_tier: default` and `text.format` with the strict JSON schema. The full concrete body is `request` in each artifact. It contains no tools or conversation continuation.

The provider intercepts that body before sending generation, submits its model/input/instructions/text/reasoning fields to the input-count endpoint, enforces the configured ceiling and reserves the conservative maximum. In the saved Orion call, the counted input was **760**, output ceiling **2,048** and returned output **195**. Offline reconstruction does not call the count endpoint again.

No neural reranker, hosted summarizer or embedding step occurred between retrieval and generation. The augmentation is an inspectable assembly of evidence, possibilities, policy and schema.

## 5. Generation and validation

The actual Luna result selected `p-orion`, `t-api`, `g-fastapi` and `g-python`, citing E1 for each. It omitted Forge and Package Management. For example:

```json
{
  "kind": "PROJECT",
  "concept_id": "p-orion",
  "confidence": 0.99,
  "evidence_ids": ["E1"],
  "reason": "Described as a patient intake API for the Orion Clinical Platform, matching the project’s intake services."
}
```

That confidence is a model-reported value, not measured calibration. The schema constrains shape. Application validation checks canonical membership, kind, workspace, activity, candidate membership, duplicates, rejections, bounded strings and evidence IDs. Commit-time checks prevent a stale result from overwriting a changed workspace or user decision.

The app's evidence-ID validator currently accepts IDs from the full profile, while compact input may include fewer IDs. The frozen benchmark helper uses transmitted IDs. Tightening the app check to the exact transmitted set remains proposed work. Even a valid ID does not prove that the cited passage entails the assignment.

## 6. Two revealing counterexamples

### FastAPI: the full profile and compact prompt differ

Full evidence E3 contains the library's purpose sentence. The compact payload instead contains E0 metadata plus E1/E2 documentation/source links. The profile labels pre-heading text `TITLE`, while compaction tests against lowercase `title`; those link records qualify and fill the two slots.

This is visible in the reconstructed request, not a hypothetical failure. Full-profile retrieval also surfaces the Go Tag because the README compares framework performance with Go; that comparison is not evidence that FastAPI is implemented in Go. The final saved answer selects Web APIs and Python, citing E0.

An earlier prompt also returned Data Validation and the library's own `fastapi` Tag. The user clarified that primary-purpose/implementation labels were wanted. The later result follows that policy, but a reused example does not establish a causal gain on unseen repositories.

### Negated API: strong matches can be explicit exclusions

The fixture says it is a Python HTTP client and **NOT part of Helios or Orion**, and not a web API server. Retrieval nevertheless scores Helios **3.300038** and Orion **3.162874**, because their names occur in the text. Stopword-based lexical matching cannot preserve the sentence's negation relationship.

The actual answer selects HTTP Clients and Python, with no Project. Keeping source prose alongside phrases gives the classifier the information needed to reject those retrieved possibilities. Truncating the denial would remove that support.

## 7. Review and subsequent work

The [lifecycle replay](examples/lifecycle-replay.json) uses actual app functions in an isolated in-memory state and a saved Orion answer. Analysis alone records a completed receipt without creating accepted user relationships. Simulated acceptance adds the four relationships as USER decisions and derives Healthcare through `p-orion`. Simulated removal of `p-orion` leaves Topics/Tags and a protected rejection.

At every completed stage, ordinary admission returns `Already analyzed; reconcile offline`. Explicit force admission returns `Explicit re-analysis`; the live app additionally requires the authorized plan, reason and budget before executing it. This replay makes no provider request and is not a claim about a historical user action.

The unknown-empty case's saved result is NO_MATCH with no assignments. Successful abstention still counts as completed analysis. Missing labels, stale evidence, review status and eligibility for paid inference are separate dimensions.

## Reproduce the deterministic stages

```bash
LANGCHAIN_TRACING_V2=false LANGSMITH_TRACING=false backend/.venv/bin/python ai-system-design/publication/v2/examples/reproduce.py
```

The command requires the existing repository environment and retained ignored Phase 0.5 records. It writes only the v2 example JSON files. It does not reproduce hosted generations. Full raw README snapshots are not redistributed; exports contain selected evidence, source attribution and historical responses. Public reviewers can inspect the exported traces, but complete historical reproduction still depends on the preserved local inputs.
