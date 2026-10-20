# Taxonomy and classification: inputs, prompts, and illustrations

Companion artifacts for the [plain-language code walkthrough](../../github-manager-ai-pipeline.md), created October 20, 2026.

## Selected parser and prompt illustrations

| Figure | What it explains |
|---|---|
| [Building the taxonomy — parser/retriever clarification](taxonomy-flow-v3.png) | GitHub metadata/README → local Evidence Parser and ordered E0/E1+ records → separate RAKE phrase extraction → system prompt, collection JSON and schema → LLM draft → human review and canonical IDs. Explicitly notes that discovery does not use the Canonical Retriever. |
| [Classifying a repository — parser/retriever clarification](classification-flow-v3.png) | Local Evidence Parser → organized evidence → Canonical Retriever searches existing labels, alongside separate phrase extraction and compact selection → complete bounded request → LLM selects existing IDs → validation and suggestions. |

The classification figure deliberately uses a simple four-stop reading path.
RAKE phrases are not drawn as TF-IDF's input; the candidate search uses selected
evidence text and the canonical registry. The model request includes evidence,
phrases and candidate objects, while the system prompt and output schema have
their own roles. Domains follow Projects.

**Evidence Parser** is the documentation name for the existing local
`selected_evidence()` code: MarkdownIt recognizes Markdown tokens and our Python
rules select headings/passages, clean text, construct E0, and append E1 onward
in document order with `id`, `section` and `text`. It is not a new service or LLM.
The illustrations' E1/Overview and E2/Features cards are schematic section-label
examples, not exact Orion output or fixed section-to-ID assignments. Multiple
records can have the same section, and a retained heading itself can receive an ID.

The figures simplify some bounds to the usual compact representation. Planned
taxonomy requests can shrink further to fit their input allowance. E1+ means
README evidence; it does not mean a guaranteed purpose statement. The full
document gives the exact algorithms, field lists and current limitations.

Used the locally preserved Illustrated Explainers skill, inspected its
`assets/style-evidence.png`, and generated the artwork with the built-in image
tool. White paper, navy pen, blue/indigo accents, illustrated documents and
reviewers match the established style. Both selected images were visually
inspected for wording, relationships, layout and margins.

[Original prompts](illustration-prompts.json) and [edit prompts](illustration-edits.json)
are preserved. Two original generations and two classification edits were made.
The first classification export is retained as `classification-flow-v1.png`;
its ambiguous arrows caused the revision and it is not the selected figure.
The intermediate edit remained in the tool's original output storage. The final
four-stop composition replaces complicated branch routing with explicit request
contents. These built-in illustration requests are separate from the closed
application evaluation allowance; no live classification/judge requests were made.

## Evidence Parser documentation revision · October 20, 2026

The two selected `*-v2.png` exports name the Evidence Parser and show how its
records are organized while preserving the established taxonomy and four-stop
classification flows. [Focused revision prompts and selected image manifest](illustration-evidence-parser-revision.json)
record the built-in edit requests, content contract, actual dimensions and hashes.
Both original selected exports, `taxonomy-flow.png` and `classification-flow.png`,
remain unchanged. The [before-revision archive](revision-2026-10-20-before.zip)
also retains the previous walkthrough and companion README with those exports.

The [dated revision verification](verification-evidence-parser-2026-10-20.json)
checks source/prompt/payload preservation, record organization, source-code
correspondence, selected exports and local links. The original `verification.json`
is retained as the earlier verification record rather than overwritten.

The final selected `*-v3.png` siblings add the **Canonical Retriever** explicitly
in classification and the factual **“Discovery: no Canonical Retriever”** note
in taxonomy. The existing Python `Retriever` searches canonical label documents,
not repositories or README passages. It returns ordered label IDs; application
filtering and model selection happen afterward. All original and v2 images remain
preserved. [Retriever revision prompts and selected-image manifest](illustration-retriever-revision.json)
record the two additional focused built-in edits and final reading-size review.

The user subsequently authorized a brief [plain-language alias-boost explanation](alias-boost-review-draft.md).
The main walkthrough now includes its actual stored `FastAPI` alias for Web APIs,
the once-per-label bonus, and the token-matching limitation. The fuller supporting
note remains available; the earlier verification receipt preserves its historical
draft status. Existing technical descriptions and figure labels remain in place.

## Approved RAG illustrations · October 20, 2026

The user approved both final wide illustrations and their explanation for
inclusion in the main walkthrough. The [RAG companion](rag-approach-review.md)
retains the type comparison, evidence/registry distinction and review rationale.

| Final figure | Placement and purpose |
|---|---|
| [RAG only — Retrieval → Augment → Generate](rag-classification-wide-v1.png) | The walkthrough's RAG overview; shows the Evidence Parser and Canonical Retriever, distinct context inputs, structured generation and review. |
| [Full picture — registry creation + RAG](rag-full-picture-wide-v1.png) | After taxonomy publication; adds parsed collection evidence, taxonomy drafting, human approval and registry reuse. |

Both images are 1672 × 941 pixels, use wide 16:9 compositions and retain the
original subtitle. The previous full illustration and all earlier variants
remain unchanged. The root README uses its compact pipeline banner and a short
reader-facing introduction to link the walkthrough, which contains both final
images and the taxonomy/classification illustrations.

[Wide-variant prompts](illustration-rag-wide-variants.json), the
[pre-integration archive](revision-2026-10-20-before-final-rag-integration.zip)
and [final integration verification](verification-final-rag-integration-2026-10-20.json)
record provenance and preservation. Earlier verification receipts retain their
historical pending-review status rather than being rewritten.

## Exact local request examples

The two authored Orion sample profiles and the published authored example registry
were read locally. No private repository text, account identity, `.env` contents,
API credential or human evaluation answer is exported. Workspace `0:samples`
and taxonomy revision `1` are documentation examples. The example registry is
not claimed to have been generated by the displayed two-repository taxonomy call.

- [Source repository records](source-repositories.json), [profiles](profiles.json),
  [registry](registry.json), and [retrieval calculations](retrieval.json).
- Taxonomy: [system prompt](taxonomy-system-prompt.txt), [user payload](taxonomy-payload.json),
  [messages](taxonomy-messages.json), [schema](taxonomy-schema.json),
  [serialized request body](taxonomy-request.json).
- Classification: [system prompt](classification-system-prompt.txt),
  [user payload](classification-payload.json), [messages](classification-messages.json),
  [schema](classification-schema.json), [serialized request body](classification-request.json).
- [Classification server validation context](classification-server-context.json),
  which is not a third model message.

The request bodies are generated using LangChain with a **mock-only HTTP
transport** and code-default settings. They are neither live provider results
nor old wire captures. No real network request occurs. Full source hashes and
scope are recorded in [provenance](provenance.json). The builder does not
instantiate the real budgeted provider or read `.env`.

Run the [example builder](build_examples.py) from the repository root using the
command in the main walkthrough. It writes documentation artifacts only.
[Verification](verification.json) checks prompt identity, payload/schema consistency,
sources, image exports, and local links. This is documentation verification,
not a new accuracy evaluation or a change to application algorithms.
