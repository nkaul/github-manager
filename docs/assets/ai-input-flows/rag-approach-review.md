# Our RAG approach — final illustration companions

**Approved October 20, 2026 · Both final illustrations and the RAG explanation are now included in [Inside the GitHub Manager AI Pipeline](../../github-manager-ai-pipeline.md). The [root README](../../../README.md) links the illustrated walkthrough. This companion retains the detailed review rationale and source notes.**

## 1. Full picture — registry creation and RAG classification

![Repository collection evidence and RAKE phrases support an earlier taxonomy draft, human review and canonical publication. During classification, Retrieval includes local Evidence Parser selection and canonical label lookup. Parsed evidence feeds compact excerpts and RAKE phrases directly into augmentation; the approved registry and all retained evidence feed the Canonical Retriever, whose shortlisted definitions also augment the request. Generation returns structured selections for validation and human review.](rag-full-picture-wide-v1.png)

*The full picture retains both bands: the earlier evidence-to-registry process and the later classification workflow. The published registry is reused; it is not rebuilt for every classification. Manual concepts can also contribute to that registry.*

## 2. RAG only — Retrieval, Augment and Generate

![RAG classification alone: metadata and README content pass through the local Evidence Parser; retained evidence supplies compact excerpts, RAKE phrases and the canonical-search query. Approved registry definitions and the query produce label candidates. These three context inputs augment the model request, followed by structured generation, local validation and human review.](rag-classification-wide-v1.png)

*The focused version contains the bottom RAG workflow without repeating the earlier registry-building band. Evidence selection remains inside Retrieval. Compact evidence, RAKE phrases and shortlisted canonical definitions have distinct routes into augmentation. The classifier then returns structured selections for validation and review.*

Both variants use a wider landscape composition with more horizontal separation, retaining natural object and lettering proportions. The [previous full illustration](rag-approach-review-v5.png) is preserved unchanged. Kind/output cards are schematic, not a new model result; checking evidence IDs does not establish semantic support. The complete field definitions and limitations remain in the sections below.

## The name I recommend

**Fixed, single-pass sparse retrieval-augmented classification, with durable application memory.**

Both figures retain the original subtitle, **“Fixed, single-pass retrieval-augmented classification,”** and its supporting descriptor, **“Sparse label retrieval + durable application memory.”**

In plain language: we first obtain and select repository evidence, look up possible existing labels, put their definitions beside compact evidence and phrase clues, and ask the model which labels the evidence supports. “Sparse” describes the word-based **canonical-label search**. It does not describe how the Evidence Parser selects source passages.

### Where Retrieval starts in this explanation

We use **Retrieval as a broad preparation stage** in the illustration, covering source-evidence collection/selection and canonical-label lookup. These are distinct operations:

1. **Evidence Parser:** reads available GitHub metadata and README Markdown, constructs E0, and retains ordered README fragments as E1 onward. This is local, deterministic parsing and heading-based selection. It obtains relevant source material for the task; it is not an embedding search, an LLM summary, or a TF-IDF passage ranker. Profiles can be prepared earlier and reused.
2. **Canonical Retriever:** uses all retained evidence as its query and searches the approved label registry. This is the scored lexical lookup. It returns possible Project, Topic and Tag IDs rather than source passages.

The evidence does **not** reach augmentation only through those candidates. One route supplies compact source excerpts, a second supplies RAKE phrase strings, and a third supplies shortlisted canonical definitions. The full registry is not serialized into the classification request.

### How the canonical registry gets built

The AI-assisted path starts with a selected **collection of repository profiles**, produced with the same Evidence Parser and separate RAKE extraction. Compact collection evidence and phrase clues go to the taxonomy LLM. It proposes a draft containing kinds, names, descriptions, aliases, proposed Project-to-Domain parents and supporting repository IDs. Human review can edit, reject and resolve conflicts before publication reuses compatible concepts or assigns canonical IDs to new concepts. Discovery does not search an already approved registry in this application branch.

| Registry content | How it gets there | Role later |
|---|---|---|
| Stable canonical ID | Assigned to new accepted concepts at publication, or reused for compatible existing ones. | The classifier selects existing IDs; display-name changes do not require a new identity. |
| Kind, name and definition/description | Proposed from the collection, then reviewed; users may also create or edit concepts directly. | Defines what each available label means. |
| Aliases | Proposed/reviewed or manually maintained, subject to name/alias conflict checks. | Used in local search and the name/alias bonus. Not copied into model candidate objects. |
| Project-to-Domain association | Reviewed parent relationship resolved during publication. | Domains follow assigned Projects; Domains are not searched as classification candidates. |
| Workspace and active status | Maintained by the application. | Bounds which concepts are available for this workspace's search. |

The parser therefore supplies the **evidence for building the vocabulary**, rather than directly turning passages into approved labels. The registry is durable application knowledge and can also include manual additions. A repository being classified need not be one of the repositories originally used to draft that vocabulary.

This description is an interpretation of the current code, not a new component or a claim of measured performance. Its control flow resembles **simple / two-step RAG**: retrieval precedes generation. LangChain distinguishes that fixed pattern from agentic retrieval, where the model decides when and how to search. Our application performs structured classification rather than an open-ended question-answering task. [LangChain retrieval architectures](https://docs.langchain.com/oss/python/deepagents/retrieval).

## How the common RAG types compare

These names describe different design choices, so they are not a single, mutually exclusive checklist. **Control flow** asks who decides when to retrieve. **Search strategy** asks how matching works. **Memory** asks what is retained and reused.

| Common name | Plain-language meaning | Where GitHub Manager fits |
|---|---|---|
| Simple / two-step RAG | Retrieve relevant knowledge, assemble context, then generate in a fixed order. | **Best description of our classification control flow.** The application prepares the search and request; the model selects labels. The three explanatory stages below expand what happens between retrieval and generation. |
| Agentic RAG | The model chooses retrieval tools and follow-up searches. | Not implemented in this path. Coding agents helped build the app, but the running classifier has no model-directed search tools. |
| Adaptive RAG | Choose a retrieval strategy according to the input's complexity or need for evidence. | Not implemented. Budget controls and freshness/reanalysis rules decide whether work is admitted; they do not route a query among different retrieval strategies. |
| Hybrid RAG architecture | A broad label for combining fixed retrieval with additional checking or more flexible control. | We have local preparation and validation, but no autonomous retrieval loop. The precise “fixed sparse retrieval-augmented classification” description is less ambiguous. |
| RAG with memory | Add retained information that can influence later work. This describes an extra capability rather than one universally defined architecture. | We persist **application state**: profiles, taxonomy, decisions and receipts. There is no semantic search over chat histories or model memories in this path. |

The fixed/agentic/hybrid terminology follows [LangChain's architecture comparison](https://docs.langchain.com/oss/python/deepagents/retrieval). The complexity-based meaning of Adaptive-RAG comes from the [research paper](https://arxiv.org/abs/2403.14403). The mapping to our implementation is a code-based assessment, not a claim that these labels have one universal definition.

Research also uses **Naive, Advanced and Modular RAG**. Gao and colleagues describe a basic retrieve-read pipeline, improvements before/after retrieval, and more composable modules and flows. Our context selection and validation are explicit engineering improvements, but naming separate Python functions does not establish that we implement every method in an “Advanced” or “Modular” research architecture. [RAG survey, sections II-A–II-C](https://arxiv.org/html/2312.10997v5).

| Retrieval strategy | How it matches knowledge | Our current classification path |
|---|---|---|
| Sparse / lexical | Match words and weight their usefulness. | **Used:** IDF-weighted cosine over canonical label documents, plus the stored-name/alias bonus. |
| Dense / embedding | Compare learned representations that can capture semantic similarity. | Not used in this path. |
| Hybrid search | Combine lexical and dense retrieval signals. | Not used. Cosine plus an alias bonus still uses lexical evidence; it does not add an embedding retriever. |

Dense/sparse mixtures are a retrieval choice, distinct from a “hybrid RAG” control architecture. The [survey's mixed/hybrid retrieval discussion](https://arxiv.org/html/2312.10997v5) describes this distinction in retrieval techniques. Our code supports the lexical assessment above; it contains no embedding/vector-store or separate neural reranking step in this flow.

## Retrieval → Augment → Generate: our actual work

| Stage and purpose | Inputs | What happens locally or in the model | Output |
|---|---|---|---|
| **Retrieval A — obtain and select repository evidence** | GitHub metadata and README content, or an already saved profile. | The Evidence Parser assembles E0 and applies local Markdown heading/passage rules to retain ordered E1+ source fragments. Separate RAKE extraction prepares phrase clues from the evidence. | Saved evidence records (`id`, `section`, `text`) and phrase records. Evidence has a direct route to augmentation and also acts as the canonical-label search query. |
| **Retrieval B — find possible existing labels** | All retained evidence plus the approved canonical Project/Topic/Tag registry. | Local binary-presence IDF cosine plus a once-per-label name/alias bonus ranks labels. Per-kind caps apply, then the application removes already handled or rejected choices. | Candidate IDs; the application expands surviving IDs into `id`, `kind`, `name`, `description` objects. This scored lookup returns labels, while Retrieval A selects source passages. |
| **Augment — build the model's context** | Candidate objects plus the stored repository profile. | Local `compact()` keeps E0 and up to two early README fragments and up to eight RAKE phrase strings. The app adds source/workspace/revision/policy fields, the fixed classification system instruction and the strict answer schema. | Two model messages, system + JSON user, with a structured-output requirement. Local scores, aliases and full stored decision history are not candidate payload fields. |
| **Generate — select supported labels** | The bounded request assembled above. | The LLM is instructed to evaluate the supplied candidates against the supplied evidence and return a structured classification using existing IDs. It has no retrieval tools; local validation rejects invalid selections. | `status`, `summary`, and `assignments`; each assignment has `kind`, `concept_id`, `confidence`, `evidence_ids`, `reason`. Local validation and human review follow generation. |

For the existing authored **Orion API** example, E1 says: “Patient intake API for the Orion Clinical Platform. Uses FastAPI and Python.” Local retrieval therefore considers labels including **Orion Clinical Platform**, **Web APIs**, **fastapi**, and **python**. It also retrieves weaker lexical matches such as **Forge Build Platform** and **Package Management**. Retrieval supplies possibilities, not accepted truth.

Augmentation includes that short evidence and phrase strings such as `patient intake api`, beside candidate definitions. The `t-api` candidate becomes this actual object from the [saved documentation payload](classification-payload.json):

```json
{
  "id": "t-api",
  "kind": "TOPIC",
  "name": "Web APIs",
  "description": "HTTP services, ASGI and web frameworks"
}
```

The model can now judge the repository evidence against a defined, existing choice. A matching word or alias alone is insufficient: unsupported weak candidates should be rejected. This revision generates **no new classification result**; output cards in the illustration explain the expected structure. The full exact system instruction, JSON input and schema remain in the main walkthrough and its saved artifacts.

## Detailed boundaries behind the three stages

| Question | What the code does | Consequence |
|---|---|---|
| What acts as the search query? | All locally retained repository evidence, including E0 and selected README records. | Search can use more source evidence than the compact subset later sent to the model. RAKE phrases are not the search query. |
| What source knowledge is obtained? | The Evidence Parser constructs metadata evidence and retains README passages using local rules. | Compact source evidence reaches the request directly; it is not replaced by label candidates or model-generated summaries. |
| What label knowledge is looked up? | Existing Project, Topic and Tag definitions: canonical name, description and aliases, searched locally. | The model chooses among existing IDs. Domains follow assigned Projects. The registry itself was published earlier, following review, and may also contain manual concepts. |
| What is the retrieval algorithm? | Binary-presence, IDF-weighted cosine, configured as `tfidf`, with a once-per-label `+3` name/alias bonus and per-kind caps. | It is lexical retrieval. There are no dense embeddings or a separate neural reranker in this path. The bonus improves name matching but can also promote broad aliases. |
| What is augmentation? | Candidate `id`/`kind`/`name`/`description` objects are assembled with compact source evidence and RAKE phrase strings; fixed instructions and a strict answer schema bound the task. | The LLM sees a small, explicit set of choices rather than the full registry. Scores and aliases remain local. |
| What is generation? | One prepared classification request asks for supported canonical IDs, evidence citations and the other fields of the existing structured schema. | “Generation” produces structured selections, not a free-form article or a new vocabulary. One pass describes the retrieval plan; transport retries do not create an agentic search loop. |
| What happens after generation? | Local schema/ID/evidence checks and application rules gate reviewable suggestions. | A valid citation ID does not itself prove that the cited text supports the label. Human review and measured evaluation remain necessary. |
| What memory exists? | Local SQLite application state retains repository profiles, canonical taxonomy, decisions and analysis receipts. | The app can reuse work, respect decisions and avoid repeated analysis. It does not retrieve conversation history or send the entire saved state to the LLM. |
| Where does taxonomy discovery fit? | It uses compact collection profiles from the same parsing/extraction code to propose vocabulary, without the Canonical Retriever. Human publication establishes the registry later searched during classification. | The full-picture variant shows that upstream dependency; the focused variant begins with the already approved vocabulary. They are separate jobs, not a discovery call repeated for every classification. Local rules/reconciliation may also bypass generation. |

We should **not call the implementation agentic RAG**: the model does not choose retrieval tools or launch follow-up searches. Nor does adaptive budgeting establish the query-complexity routing described in **Adaptive-RAG**, whose paper selects among no-retrieval, single-step and iterative strategies. That router is absent here. [Adaptive-RAG paper](https://arxiv.org/abs/2403.14403).

“Memory” is a separate property from retrieval control. The precise wording above avoids implying a semantic memory system simply because the application persists state. Similarly, combining cosine scoring and an alias rule does not constitute dense-plus-sparse hybrid search.

## Code and evidence behind the picture

- [Evidence Parser, RAKE, compact selection and Retriever](../../../backend/app/pretest/ai/evidence.py): `selected_evidence()`, `profile()`, `compact()`, `Retriever.candidates()`.
- [Application orchestration](../../../backend/app/demo/service.py): the discovery branch returns before classification constructs `Retriever(..., method="tfidf")`; classification expands surviving candidate IDs into bounded request fields.
- [Taxonomy review and publication](../../../backend/app/demo/taxonomy_review.py): review, conflict handling, compatible canonical reuse, creation and Project-to-Domain resolution.
- [Provider](../../../backend/app/pretest/ai/provider.py): fixed system and JSON user messages, structured output and local validation; no model-selected retrieval tools.
- [Persistent application state](../../../backend/app/demo/store.py) and [analysis admission/receipts](../../../backend/app/demo/analysis.py): stored state and the “Already analyzed; reconcile offline” gate.
- [Exact authored example request](classification-payload.json), [registry](registry.json) and [ranking trace](retrieval.json). These are existing documentation examples, not new live evaluation results.
- [Exact illustration prompts](illustration-alias-readme-rag-2026-10-20-prompts.json). Built-in image generation; original pipeline figures and application algorithms are preserved.
- [Focused correction prompt](illustration-rag-review-correction.json), [three-stage style revision](illustration-rag-review-v3.json), [evidence/registry provenance revision](illustration-rag-review-v4.json), and [query-route refinement](illustration-rag-review-v5.json) preserve the earlier work. The full `rag-approach-review-v5.png` remains available unchanged.
- [Wide-variant prompts](illustration-rag-wide-variants.json) record the two new built-in edits: full picture and RAG-only. The previous review text is preserved in [the v5 archive](rag-review-v5-before-wide.zip); an earlier revision remains in [the v3 archive](rag-review-v3-before-v4.zip).

## Placement in the main walkthrough

The RAG-only illustration appears in the [RAG overview](../../github-manager-ai-pipeline.md#rag-overview), after the taxonomy-versus-classification distinction. The full picture appears in [From published taxonomy to RAG classification](../../github-manager-ai-pipeline.md#from-published-taxonomy-to-rag-classification). The detailed parser, retrieval, prompt and payload sections remain intact. The README uses a compact navigation graphic and a short introduction linking the illustrated document.
