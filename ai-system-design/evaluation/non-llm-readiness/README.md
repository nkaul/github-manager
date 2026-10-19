# Can repository knowledge and reference labels be created without an LLM?

Date: October 16, 2026. Status: **bounded offline feasibility experiment completed; expanded implementation proposed**.

**Yes for a durable evidence record, extractive summaries and conservative proposed labels. The experiment does not establish human-equivalent semantic comprehension or human ground truth.** Richer preserved evidence is useful even when the classifier remains unchanged.

There are two different interpretations of “without an LLM”:

- **No external model/API calls:** an LLM-driven coding agent can read documents, interpret relationships and save knowledge once. That still uses the agent's LLM reasoning and allowance. It can reduce repeated API processing, but is not LLM-free reference creation.
- **No LLM inference in the processing pipeline:** parsers, lexical search, extractive ranking, explicit rules and classical supervised models can perform useful work locally. Their semantic coverage must be measured. Small learned encoders/parsers are another option if the constraint allows non-generative models; they are not rules-only processing.

The prototype below used the second interpretation: **no runtime language model, provider calls, network access, package installation or model download**. Codex authored the program and this interpretation. Its comparison references were previously proposed by agents and remain unapproved; that is not an independently human-labeled benchmark.

## 1. Preserve knowledge as layers, rather than one summary

A summary is a view into evidence. It cannot guarantee retention of every important fact, qualification, contradiction or later-relevant detail. Preserve the full sources alongside it:

1. **Immutable source layer:** all available README/supporting bytes, repository ID, commit, logical/resolved paths, hashes and collection time. Record artifacts not fetched or inaccessible. Complete retained files are not the complete repository.
2. **Searchable evidence layer:** section-aware passages and complete fallback chunks with source coordinates. Index all retained content; keep code, installation text, license notices and archived material distinguishable from purpose evidence.
3. **Extractive digest:** selected verbatim purpose, artifact-type, relationship and limitation passages. The digest helps review; it does not replace the source layer.
4. **Typed claim layer:** proposed subject–relation–object claims, polarity, maturity/version, uncertainty and supporting spans. An automatic cue flag is not an established claim.
5. **Taxonomy decision layer:** stable concept IDs, rule/model/policy versions, source bindings, reasons, uncertainty and actual human adjudication.

This separation lets later review recover omitted context without repeatedly fetching GitHub or regenerating summaries. A source change invalidates claims depending on that source; a taxonomy change can rematch retained claims without pretending the repository was newly understood. Preserve original claims and corrections instead of overwriting their history.

Useful relation types include `COMPONENT_OF`, `DEDICATED_INTEGRATION_FOR`, `USES_TECHNOLOGY`, `ALTERNATIVE_TO`, `TEACHES`, `PROVIDES_CAPABILITY`, `PLANNED_CAPABILITY` and `EXCLUDES_CAPABILITY`. Do not collapse them into generic “related to.” Using PyTorch can support a technology Tag while leaving PyTorch Project membership unknown. Domain membership still derives through approved Project parents.

**Implemented in this experiment:** immutable byte copies, searchable chunks, extractive digests and comparison candidates. **Proposed next:** manifest interpretation, a typed claim ledger, relation/negation extraction, human decisions and final label assignment. None of those proposed layers is being presented as implemented by the prototype.

## 2. What was tested

The [pilot script](tools/pilot.py) selected thirty repositories: three per sampling domain, **development split only**, using a fixed SHA-256 ordering. Selection did not use expected labels. Features and candidate IDs were built before the reference labels were loaded for scoring.

For each repository it:

- Verified stored SHA-256 and Git blob SHA-1.
- Copied complete retained sources into a private SQLite source table and verified byte-identical round trips.
- Indexed thirty-line windows with twenty-line strides in SQLite FTS5, asserting that every source line was covered. These are a completeness baseline, not a claim that fixed windows are the best semantic chunking strategy.
- Selected verbatim Markdown blocks using fixed purpose/heading/relationship/constraint cues, up to a 6,000-character digest. Oversized blocks stayed in the ledger rather than being silently truncated into a misleading complete passage.
- Verified all digest passages against exact source character ranges.
- Compared existing application extraction with all-source text and extractive-digest representations using unchanged candidate limits and the same proposed registry.
- Exercised a deliberately narrow English weak-rule baseline on twelve authored language controls.

The results are saved locally under `docs/validation/private/corpus-600/non-llm-pilot-v2/`. The earlier v1 run is retained. A fresh v2 run reproduced the same repository selection, candidate IDs and proxy recall; it also records producer-script and original-corpus-manifest hashes.

| Check | Result |
| --- | ---: |
| Repositories | 30 |
| Retained README/supporting files | 85 |
| Source bytes copied and round-trip verified | 830,110 |
| Indexed overlapping chunks | 796 |
| Source-bound extractive passages | 156 |
| Digest characters: median / maximum observed | 1,263 / 3,010 |
| Empty digests | 0 |
| Model/provider/network calls in runtime | 0 |
| New packages/model downloads | 0 |
| Human-approved comparison references | 0 |

SQLite search returned a matching passage in a parameterized query. This verifies index operation, not retrieval relevance or semantic understanding. Every retained line is indexed, but no machine indexing step is claimed as semantic reading or proof of comprehension.

## 3. Candidate-retrieval findings

The candidate budgets remained eight Projects, ten Topics and twelve Tags. Results are **known-positive recall against proposed agent references**, not final classification, precision/F1 or human agreement.

| Representation/ranker | Project positives retrieved | Topic positives retrieved | Tag positives retrieved |
| --- | ---: | ---: | ---: |
| Current app profile + existing `tfidf` ranker | 11/11 | 21/35 (60.0%) | 32/33 |
| All retained source text + same ranker | 11/11 | 21/35 (60.0%) | 32/33 |
| Extractive digest + same ranker | 11/11 | 20/35 (57.1%) | 33/33 |
| Extractive digest + existing BM25 | 11/11 | 21/35 (60.0%) | 33/33 |

The small Tag change is one proposed label, not established quality improvement. Project support is only eleven labels, so its ceiling score cannot support a general accuracy claim. Native language/topics are shared input features; some technology references are therefore input-correlated. The registry itself was curated with corpus access.

**The main finding:** preserving more text did not resolve Topic matching on this sample. Some misses involve wording variants, subject versus artifact distinctions and multilingual descriptions. Examples include `ecommerce` versus the E-commerce concept, a Portuguese icon-catalog description and a Chinese plugin-resource index. Normalization/glossaries can address some cases; they do not by themselves solve arbitrary semantic interpretation.

The digest also sometimes selected individual catalog entries from `Shubhamsaboo/awesome-llm-apps` as purpose passages. Each passage was quoted accurately, yet the selection could misrepresent the repository's collection-level purpose. On LangChain and TensorFlow, it retained clear overview text. This illustrates why extractive text fidelity and purpose accuracy require separate evaluation.

The all-source variant included supporting/manifests/license text as a naive reference representation. It is not a production prompt, and the digest uses different evidence selection/bounds from the compact application request. Downstream token cost, latency and generation quality were not measured. No candidate set was automatically accepted as a label assignment.

The prototype uses CommonMark parsing for narrative text; it does not provide a dedicated reStructuredText parser or understand diagrams, screenshots and external linked documentation. Manifests are retained/indexed as text, not yet interpreted as structured facts. A production workbench needs format-aware processing and an explicit missing-artifact inventory before making broader completeness claims.

## 4. Where simple rules failed

The weak-rule baseline matched its authored expectation on **eight of twelve controls**. This is a narrow contract probe, not a linguistic benchmark or estimated human-equivalent accuracy.

| Control | Expected interpretation | Observed failure |
| --- | --- | --- |
| “Does not lack payments.” | Positive capability signal | A simple negation window produced a negative hint |
| “No Docker is required; this service provides payments.” | Payments signal positive | Negation from another clause contaminated the decision |
| “Payments are not implemented.” | Negative implementation signal | A prefix-only rule missed negation following the term |
| “Este projeto suporta pagamentos.” | Portuguese payment-support statement | English term matching abstained |

Simple patterns did distinguish a dedicated plugin from merely using a framework, and recognized some planned/hedged cases. Their successes cover the patterns they were written for. They do not establish robust subject attribution, anaphora, temporal scope, hypothetical examples or negation composition.

Abstaining on unfamiliar wording is safer than fabricating certainty, but lowers automatic coverage. More rules can improve bounded coverage while increasing maintenance and interaction complexity. Even a sophisticated non-generative parser/classifier still needs evaluation on the actual repo-policy task.

## 5. Viable software approaches

| Approach | Tools and role | Strength | Main tradeoff |
| --- | --- | --- | --- |
| Full-source evidence workbench | Existing markdown-it-py; SQLite FTS5/BM25; JSON/SQLite provenance | Cheap local persistence, exact source recovery and inspectable review | Preserving/searching text does not determine its meaning |
| Extractive summarization | Heading/position/relationship rules; optionally TextRank/LexRank comparisons | Copies source sentences without a generation call | Can omit qualifiers or select an example as the main purpose |
| Terminology and relation rules | spaCy PhraseMatcher/Matcher/EntityRuler, approved aliases and typed patterns | Strong for explicit technologies and bounded relationships | Language/domain coverage and rule interactions; parse-dependent patterns need a learned parser |
| Weak supervision | Snorkel labeling functions, conflict/coverage analysis and abstention | Organizes several noisy signals and identifies review needs | Correlated rules can share errors; estimated consensus is not human gold |
| Classical supervised classification | scikit-learn word/character TF-IDF with logistic regression or linear SVM, trained on reviewed labels | Local, inexpensive, non-generative classification | Needs suitable positive/negative judgments and support per label; partial unknowns cannot become negative training examples |
| Non-generative semantic models | Optional sentence encoders, dependency parsers or NLI models | Can generalize beyond exact words or assess particular relations | Model download/inference, multilingual/domain errors and calibration; embeddings alone do not prove entailment |
| Agent-assisted one-time interpretation | Agents read context and persist cited claims with explicit uncertainty | Flexible interpretation with reusable durable evidence | Uses an LLM agent; reference/production-model bias and human verification remain |

SQLite FTS5 provides BM25 ranking and highlighting/snippet functions; the prototype tested indexing and a search query, while concept BM25 comparisons used the existing Python ranker. These are two distinct retrieval uses. [SQLite FTS5 documentation](https://www.sqlite.org/fts5.html).

TextRank is an extractive graph-ranking alternative worth comparing to fixed paragraph rules, not a tested component here. It ranks sentences/keywords; it does not create a complete repository meaning representation. [Original TextRank paper](https://aclanthology.org/W04-3252/).

spaCy supports phrase/token matching for defined terminology. Its DependencyMatcher requires a parser model; choosing it is already a learned-NLP option even if no generative LLM is used. [spaCy rule-based matching](https://spacy.io/usage/rule-based-matching/).

Snorkel supplies labeling-function analysis and a LabelModel for combining outputs. For this multi-label registry, each repo/concept decision needs an appropriate positive/negative/abstain formulation. Do not count several aliases of the same rule as independent evidence or train confidence estimates using unreviewed labels as truth. [Snorkel labeling package](https://snorkel.readthedocs.io/en/v0.9.7/packages/labeling.html).

scikit-learn supports text feature extraction for classifiers. Start only with frequent, adequately reviewed labels; sixty reviewed repositories will not automatically supply enough examples for all 335 concepts. Keep related families together across training/evaluation. [scikit-learn feature extraction](https://scikit-learn.org/stable/modules/feature_extraction.html).

Sentence Transformers provides semantic-search encoders as an optional research path if non-generative learned models are acceptable. Similarity is a candidate-retrieval signal, not Project-membership proof. This prototype downloaded none, and no such service is proposed for the approved MVP without a separate scope decision. [Sentence Transformers semantic search](https://sbert.net/examples/sentence_transformer/applications/semantic-search/README.html).

A typed claim graph can initially be ordinary SQLite tables. RDFLib is an optional representation when triple queries/interchange become useful; it does not extract correct triples automatically or make them true. [RDFLib creating triples](https://rdflib.readthedocs.io/en/stable/intro_to_creating_rdf/).

Only existing Markdown, SQLite, RAKE and sparse-retrieval dependencies were used locally. spaCy, Snorkel, scikit-learn, TextRank implementations, RDFLib and semantic models were researched as alternatives, not installed or benchmarked.

## 6. Recommended next steps

1. **Extend the planned human-review pilot with durable evidence packets.** Build source-first packets from complete retained artifacts, with relevant context and optional search. Keep the current corpus release immutable. This is useful under either interpretation of “no LLM.”
2. **Add typed claims conservatively.** Parse explicit manifest fields; separate implementation languages from development dependencies. Add a small set of relation/polarity/maturity rules. Persist the exact supporting spans and UNKNOWN/CONFLICT rather than manufacturing a polished narrative.
3. **Match claims to the known registry.** Use approved aliases, concept definitions and relationship-specific rules. A component/integration relation can propose a Project; a usage relation can propose a technology Tag. Topic assignment needs a primary-purpose policy, not keyword occurrence alone.
4. **Human-verify sixty repositories.** Require missing-positive discovery, explicit reviewed scope and independent adjudication where possible. Compare source-only versus assisted review time, correction rates, label completeness and evidence support. Keep the original proposed labels visible only after initial source assessment.
5. **Choose the semantic branch from measured gaps.** If zero learned models is a hard constraint, favor conservative rules with larger human review. If local non-generative models are acceptable, compare a small supervised baseline on adequately supported labels. If the constraint is only avoiding additional API calls, an agent-assisted full-context pass can populate proposed claims once, with actual read coverage and later human adjudication.
6. **Evaluate the same human-reviewed cases across branches.** Measure per-kind precision/recall on complete scopes, coverage/abstention, contradictory/unsupported claims, purpose-summary quality, missing-evidence rate, multilingual/artifact-type errors, reviewer effort and processing cost. Keep retrieval metrics distinct from final labels and full-source truth distinct from app-visible answerability.

Promote proposals to human-approved references only when actual review is recorded. A framework's confidence, a rule vote, a detailed summary or two agreeing agents does not substitute for that provenance. This preserves the earlier [human verification plan](../../../docs/planning/corpus-600-human-verification-and-evaluation.md), while improving the evidence available to its reviewers.

## 7. Reproduce and inspect

From the repository root, choose a new run ID to preserve prior outputs:

```bash
backend/.venv/bin/python ai-system-design/evaluation/non-llm-readiness/tools/pilot.py --run-id non-llm-pilot-v3
```

The script refuses to overwrite an existing experiment database. It requires saved corpus files and the existing backend environment; it needs no GitHub authentication, API key or running collector. It imports the current deterministic app/profile/ranker modules but constructs no provider. Repository artifacts are treated only as data and are never executed.

Private v2 artifacts: [results](../../../docs/validation/private/corpus-600/non-llm-pilot-v2/result.local.json), [extractive packets](../../../docs/validation/private/corpus-600/non-llm-pilot-v2/packets.local.json), [source manifest](../../../docs/validation/private/corpus-600/non-llm-pilot-v2/source-manifest.local.json), [candidate comparisons](../../../docs/validation/private/corpus-600/non-llm-pilot-v2/retrieval.local.json), and `evidence.sqlite3` in that folder. These links work only with the local dataset; raw sources remain unpublished.

The feasibility result supports building a reliable evidence workbench. It does not justify replacing the human reference gate, claiming complete understanding, changing production extraction or adding a semantic-model service automatically.
