# GitHub Manager — illustrated AI system design

AI-generated Cedar narration. Slower delivery and explicit section introductions, incorporating pilot feedback.

## The problem and the product

Purpose: Find repositories by their purpose and relationships, then keep your decisions.

### The problem and the product

Section one. The problem and the product. GitHub Manager helps you discover, understand, and organize repositories. The purpose is to turn a scattered collection into a workspace whose relationships you can inspect and change.

### A list does not explain the relationships

Imagine starting an API project. You have your own services, shared repositories, and libraries starred for later. Names and programming languages help you search. They do not explain which pieces support the same initiative. Two Python repositories may serve entirely different purposes.

### Source facts and organization have owners

GitHub remains the source of repository facts: identity, links, visibility, and available metadata. The application builds selected evidence locally. AI proposes an organization, and the user reviews it. This separation matters because a convenient suggestion must not quietly replace a fact or a deliberate decision.

### Follow one example through the system

We will follow Orion, an authored synthetic patient-intake application. Its displayed classification comes from a saved real API test. We will also use a public FastAPI library as a contrast. These examples explain the mechanics; they are not a new account recording or a new benchmark.

## Organization vocabulary

Purpose: Give initiative, subject and technology different meanings.

### Organization vocabulary

Section two. Organization vocabulary. Before classification, we need to define what a relationship means. The purpose is to keep an initiative, a capability, and a technology from becoming one confusing pile of labels.

### Four questions, four concept types

A Project answers which product or initiative a repository supports. A Domain groups those Projects into a broader area. A Topic describes a primary capability or subject. A Tag describes technology or another useful characteristic. For Orion, the examples are the clinical platform, Healthcare, Web APIs, and Python.

### Relationships are not exclusive folders

A repository may support more than one Project. Its Domains derive through those Project memberships; the classifier does not assign Domains independently. Topics and Tags remain useful when no Project applies. The application's Topics are separate from the native topics supplied by GitHub.

### Sharing a framework is not sharing an initiative

The Orion application uses FastAPI and Python. The FastAPI library is itself a reusable framework. Sharing those words does not make the library part of Orion. Under the primary-label policy, incidental capabilities are omitted, and a library's own name is not automatically its dependency Tag. Next, we decide what evidence can support that distinction.

## Context engineering

Purpose: Select, authorize and structure the information needed for a decision.

### Context engineering

Section three. Context engineering. Its purpose is to choose what information the model sees, what that information means, and which boundaries remain outside the model. A longer prompt is not automatically a better decision.

### Four kinds of context have different authority

We separate trusted source facts, untrusted repository prose, user-owned organization, and execution identity. Canonical IDs, rejections, revisions, and evidence hashes constrain the operation. The application does not send every stored record to the model. For example, protected decisions filter candidates before prompting rather than becoming an entire conversation history.

### Privacy is a gate before counting

Hosted input is restricted to verified public repositories and synthetic fixtures in this implementation. Private or unknown visibility fails closed, including phrases derived from private text. Local rules can still help organization. Narrow cleaning patterns are hygiene, not a complete secret scanner or prompt-injection defense. The model has no tools with which to act on README instructions.

### Runtime context is different from development context

The working runtime is local Next.js, FastAPI, and SQLite. LangChain connects structured requests; it does not own the application's memory. During development, user decisions outrank approved design, plans, and historical discussion. Phase zero checked access; phase zero point five checked AI readiness; phase zero point nine delivered the local app. Cloud runtime remains deferred.

## Evidence and chunking

Purpose: Preserve source-linked purpose text while keeping the request bounded.

### Evidence and chunking

Section four. Evidence and chunking. The purpose is to preserve the sentence that explains a repository, while excluding material that is unlikely to help organization. We begin with a README, not an AI-generated summary.

### Select purpose blocks, retain their source

The extractor parses Markdown blocks and applies heading-based selection. Metadata becomes evidence zero; selected README text receives additional IDs. For Orion, evidence one says: patient intake API for the Orion Clinical Platform. Uses FastAPI and Python. The language metadata is empty, so Python is supported by prose rather than an invented GitHub value.

### Bytes, characters and tokens are different bounds

The input byte ceiling limits the fetched document. Selected blocks and total evidence have character bounds. The compact classification profile then keeps metadata, up to two README records, and up to eight phrase strings. Exact request tokens are counted later. Hashes bind the selected content and configuration. Offsets identify cleaned text, not original README line numbers.

### A simple selector has visible weaknesses

Heading rules are inspectable and avoid a hosted summarization pass, but can cut sentences or crowd out better evidence. Format noise, late negation, and multilingual headings need tests. The app received a separately versioned cleanup wrapper; frozen benchmark profiles stayed unchanged. Retrieval can see full selected evidence that compact generation omits, so both stages need their own checks.

## Local algorithms

Purpose: Extract useful signals without confusing keyword scores with meaning.

### Local algorithms

Section five. Local algorithms. Their purpose is to expose compact signals before an expensive decision. We use phrase extraction and corpus counts, but those numbers do not establish initiative membership or semantic understanding.

### RAKE turns selected text into ranked phrases

RAKE splits around stopwords and punctuation. Word frequency and co-occurrence contribute to phrase scores. Our configuration considers one to four words, retains up to twenty candidates, normalizes duplicates, and checks source spans. In Orion, patient intake API and Orion clinical platform each score nine. FastAPI and Python score one. Those are weights, not probabilities.

### YAKE and corpus frequency answer other questions

YAKE was compared offline using local document features such as position, capitalization, and frequency. It is not the production extractor. Its measured runtime included repeated process startup, so the ratio is not an intrinsic speed comparison. Corpus document frequency counts a term once per repository. That pretest table is different from the concept-document IDF used in retrieval. The installed YAKE artifact's licensing also remained an adoption concern.

### Keywords help matching but can add noise

A bag of phrases loses relationships, including the word not. Purpose prose must survive. In one historical FastAPI ablation, adding RAKE phrases used more input tokens without changing the unwanted secondary labels. That single case proves neither that phrases always help nor that they are unnecessary. The product also has no learned project-clustering engine or automatically learned rules.

## Taxonomy intelligence

Purpose: Propose a useful collection vocabulary, then publish only reviewed concepts.

### Taxonomy intelligence

Section six. Taxonomy intelligence. The purpose is to propose a vocabulary for a collection. This is different from assigning labels to one repository. Discovery can suggest new concepts; classification must use concepts already approved.

### Collection context reveals connected initiatives

The saved discovery request contained thirty compact profiles: ten public samples and twenty authored fixtures. Orion's API, UI, booking, and audit records supplied related purpose evidence. The model proposed Orion Clinical Platform with a Clinical Operations parent and supporting repository IDs. Its twenty proposals were a draft, not a published organization.

### Sampling and packing preserve a bounded collection

The app samples owner and language buckets using a deterministic round-robin approach. Collection packing uses a conservative byte allowance before exact token counting, shortening records and pruning phrases where necessary. This can miss structure outside the cohort. The saved direct collection request used its original packing path, so its token counts cannot be attributed to a later optimization.

### Reserved terms can hide in aliases and archives

Publication normalizes names and aliases, including Unicode handling, and checks reservations. A visible name can conflict with an alias or archived concept. The app exposes the conflicting record and offers opt-in reuse, renaming, removal, or exclusion. These deterministic checks protect canonical consistency. Similar language is not permission for an automatic semantic merge.

## Retrieval

Purpose: Find plausible approved concepts before deciding which relationships hold.

### Retrieval

Section seven. Retrieval. Its purpose is to find plausible concepts from the approved vocabulary. The repository evidence is the query; concept names, definitions, and aliases are the searchable documents. A shortlist is not a decision.

### Sparse scoring exposes why a candidate surfaced

The method called TF-IDF in the code is actually binary-IDF cosine. It weights less common registry terms and normalizes overlap, while repeated terms do not increase frequency. A name or alias whose tokens all appear adds three once. Token order and positive assertion are not required. Positive candidates are ranked by kind, with stable-ID ties and bounded limits.

### Follow the actual six-candidate Orion shortlist

Orion retrieves its own Project, Web APIs, FastAPI, and Python. Forge also surfaces through platform, and Package Management through Python. The strong Orion score includes the alias boost. These are ranking scores, not membership probabilities. The next stage must distinguish actual purpose evidence from distracting shared words.

### BM25 was a comparison, not a hidden extra layer

BM25 was compared offline with the same alias boost and candidate caps. It adds saturated term frequency and document-length normalization. On the small reused comparison, both lexical methods covered the expected evaluation labels; alias-only missed four Topics. That supports feasibility, not sparse superiority over dense search. There is no embedding query, neural reranker, or autonomous retrieval agent in the current product.

## Augmentation

Purpose: Assemble evidence, candidate meaning and decision policy into the model request.

### Augmentation

Section eight. Augmentation. The purpose is to assemble a decision-ready request from the evidence and retrieved possibilities. Retrieval supplies options. Augmentation explains those options and the rules for selecting them.

### The repository supplies evidence, not the answer key

For Orion, the payload includes repository identity, public or synthetic source status, revision, evidence hash, selected evidence, phrase strings, and candidate records. Evidence one preserves the patient-intake sentence. Candidate records contain canonical ID, kind, name, and description. Aliases helped retrieval but are not serialized into those candidate objects. Expected evaluation labels are never supplied.

### Policy makes the semantic task explicit

The system instructions require supported approved IDs, primary-purpose Topics, and primary implementation Tags. Shared frameworks do not prove initiative membership. Negation matters; multiple Projects are allowed. Unsupported input can produce no match or a request for more context. User decisions remain application constraints rather than an invitation for the model to overrule them.

### Count the assembled contract, not just the prose

A strict response schema describes assignments, evidence references, reasons, status, and summary. LangChain binds that schema to the hosted request. The harness inspects the assembled messages and schema before counting input tokens. This is retrieval-augmented structured classification, with durable application memory. It is not a conversational document-question-answering agent, and adaptive budgets do not turn it into Adaptive RAG.

## Generation and validation

Purpose: Return supported IDs, then check whether a proposal is safe and useful.

### Generation and validation

Section nine. Generation and validation. The purpose is to turn the assembled context into a bounded proposal, then check it before it affects organization. Valid JSON is only the beginning of that check.

### The saved model answer chose four supported IDs

In the preserved Orion call, the model selected Orion Clinical Platform, Web APIs, FastAPI, and Python. All four assignments cited evidence one. Forge and Package Management were omitted. The request counted seven hundred sixty input tokens and returned one hundred ninety-five output tokens. This visible result does not expose the model's private reasoning process.

### Application checks go beyond a response schema

Validation checks active IDs, kinds, workspace ownership, allowed candidates, duplicates, field limits, status, and evidence references. Dispatch and commit also check access, profile hashes, revisions, and user decisions. Suggestions remain proposals until accepted. A real evidence ID may still cite irrelevant prose, and the model's confidence is not a calibrated accuracy probability.

### Model roles and audit gaps need honest labels

Luna is the task default supported by the limited classification tests; Sol supplied the taxonomy draft. A comprehensive model-winner study was not completed. The audit also found evidence-ID validation broader than the transmitted compact set, and a taxonomy prompt limit of twenty versus a validator limit of fifty. Those are improvement tasks, not shipped guarantees.

## Counterexamples and failure cases

Purpose: Use awkward inputs to distinguish matching words from supported meaning.

### Counterexamples and failure cases

Section ten. Counterexamples and failure cases. Their purpose is to show where an apparently sensible pipeline can mislead us. We keep the confusing evidence visible rather than explaining only the clean success case.

### Negation and multiple memberships change the answer

One fixture explicitly says it is not part of Helios or Orion. Lexical names still retrieve both Projects, but the saved classifier selects HTTP Clients and Python with neither Project. Another audit fixture genuinely supports two initiatives. The task must allow both. A forced single winner would change the meaning of organization.

### FastAPI exposed a packing and policy weakness

The full FastAPI profile contains its purpose statement, but an uppercase title marker let documentation links occupy compact slots. Retrieval could see evidence the generator did not receive. Metadata still supported the saved answer, Web APIs and Python. An earlier answer added unwanted secondary labels. Primary-only policy clarified the task, but reused cases cannot establish an independent causal improvement.

### Sparse or adversarial input needs an honest exit

Empty, fork-only, and metadata-only cases need no-match or uncertainty paths. Installation noise can introduce unrelated names. English extraction can miss other languages. Narrow cleaning can miss malicious instructions or secret-like text. These fixtures explore boundaries; they are not a comprehensive security benchmark. Next, we preserve the decisions and uncertainty that follow from these cases.

## Memory and user authority

Purpose: Preserve completed work and corrections independently of current labels.

### Memory and user authority

Section eleven. Memory and user authority. The purpose is to preserve useful state across changes. Here, memory means application records, not a model remembering a conversation or a LangChain conversation-memory component.

### Keep four dimensions separate

Relationships, completed analysis, freshness, and review status answer different questions. A successful no-match is completed analysis. Removing Orion's Project can leave its Topic and Tags useful, while the receipt remains. Provider replay cache and optional run history are different records. Deleting one display or membership does not silently make the repository eligible for another paid decision.

### Corrections must survive later organization

Accepting a proposal creates a user decision. Rejecting or removing a relationship leaves a protected tombstone. Approved rules can supply deterministic mappings, subject to those rejections. Ordinary organization cannot recreate a rejected edge behind the user's back. These protections preserve authority; they do not prove every accepted relationship was independently verified truth.

### Reconcile known information without fresh inference

Local reconciliation applies approved rules, compatible stored assignments, or contiguous name and alias matches for review. This match is stricter than retrieval's unordered alias tokens. Local suggestions have visible provenance and zero model confidence. They do not manufacture AI completion. Fresh analysis remains available with an explicit reason and reviewed budget when the user wants a new judgment.

## Loop engineering

Purpose: Control when work runs, skips, reconciles, retries or becomes stale.

### Loop engineering

Section twelve. Loop engineering. Its purpose is to control transitions around inference. We need to know when to run, when to skip, and when a result has become unsafe to apply. This is application control, not an autonomous model thought-and-action loop.

### Admit one attempt and preserve uncertain outcomes

Preview and worker check admission before constructing the provider or making a count request. Transactions claim running attempts so concurrent starts do not independently process the same operation. Previously attempted or uncertain work requires deliberate review, not a silent retry. Explicit re-analysis can bypass memoization while retaining privacy, schema, and spending checks. Classification cohorts use new-analysis, Project, and recency ordering, not a learned ranker.

### Thresholds schedule work, not permission

Automatic organization accumulates eligible changes. Defaults combine weight six and three distinct entities, or two new Projects, followed by a ninety-second quiet period and a thirty-minute cooldown. Types and thresholds are configurable. Consumed event sequences prevent endless rescheduling. Existing analysis still reconciles locally. A change upstream cannot be noticed before its content is fetched.

### Fences protect a newer decision from an older result

Revision, generation, policy, and epoch fences bind a response to current state. If the user edits or resets during generation, unsafe associations are discarded while historical cost and processing evidence remain. Reset uses a scoped, expiring, one-use preview and exact confirmation. It preserves cost history and readiness reports. These are tested local safeguards, not distributed exactly-once execution or forensic erasure.

## Harness engineering

Purpose: Make every admitted request measurable, authorized and finite.

### Harness engineering

Section thirteen. Harness engineering. Its purpose is to make a model request measurable and bounded before it leaves the application. A successful connection alone tells us nothing about decision quality, safe state changes, or total cost.

### Inspect, count, reserve, then generate

The provider inspects the serialized LangChain request, including destination, model, instructions, schema, output limits, and disabled tool or conversation fields. The HTTP hook checks current session and workspace authorization. Counting consumes an HTTP attempt. Only a successful bounded count permits a monetary reservation and generation. SDK retries are disabled to prevent hidden request multiplication.

### An absent response does not mean an absent charge

Known valid usage settles the estimate. Refusal or incomplete output is not a successful replay entry, but can still cost tokens. Missing usage, timeout, and uncertain failures keep the maximum reservation. A bound violation stops later paid admission. Selected provider rejections have a specific local accounting policy; none of these estimates is independent invoice reconciliation.

### Fixed windows and adaptive grants share a ceiling

Fixed mode has audited request and generation limits. Selective renewal or override preserves past attempts and spending. Adaptive mode admits a finite reviewed dollar grant under the same cumulative cap. Per-call reservations transfer from a run hold without double counting. Recovery links holds to jobs, releases unused terminal money, and preserves unknown-call holds. Separate local databases still require reconciliation.

## Tokenomics and optimization

Purpose: Measure the total useful outcome, not merely a smaller prompt.

### Tokenomics and optimization

Section fourteen. Tokenomics and optimization. The purpose is to understand what each decision consumes and which costs can be avoided. We separate historical estimates, conservative admission bounds, and the broader cost of a useful accepted relationship.

### A reservation is a bound, not typical usage

The harness pins a rate snapshot and counts assembled input. It reserves possible output, a conservative cache-write allowance, and headroom without assuming a cache discount. Known usage later settles in integer microdollars. Reasoning tokens already belong to output and must not be added twice. A maximum-output reservation is not a prediction of the answer's usual length.

### Historical counts need the right denominator

The twenty-case API round made twenty generation requests and twenty input-count requests: forty provider HTTP operations. It recorded sixteen thousand forty-one input tokens and three thousand four hundred fourteen output tokens. The rounded inference estimate was about three-tenths of a cent. This excludes media, infrastructure, indexing, and human review; it is not a production cost guarantee.

### Avoiding work is different from provider caching

Compact evidence, candidate caps, and bounded collection sampling reduce individual requests, but can omit useful context. Receipts and local reconciliation can avoid another request entirely. Provider prompt caching still invokes a model, and no discount benefit appeared in that round. Count latency, evidence refresh, storage, and reviewer corrections also matter. Optimize cost per correct, accepted, current association.

## Evaluation and evidence

Purpose: Evaluate retrieval, decisions and workflow separately, with honest limits.

### Evaluation and evidence

Section fifteen. Evaluation and evidence. The purpose is to learn which stage succeeds, which stage fails, and how far the measurements generalize. A single attractive score cannot answer all three questions.

### Know what the small benchmark actually contains

The frozen corpus has thirty repositories. Ten were development cases; twenty formed the evaluation partition, with eight public libraries and twelve synthetic cases. The registry has forty-two concepts, including four non-searchable Domains. Public labels were proposed and user-approved. Related initiatives were grouped, but policy clarification reused evaluation cases. The final round is regression validation, not untouched generalization evidence. Project-positive evidence is synthetic; private enterprise performance remains unestablished.

### Retrieval recall and assignment quality are different

Candidate recall asks whether expected IDs reached the shortlist. Both lexical methods covered all expected evaluation labels under generous caps. Classification then produced fifty true positives, zero false positives, and two misses: micro F one of ninety-eight percent. Both missing labels had been retrieved, locating those errors after candidate inclusion, without proving whether packing or model selection caused them.

### Quality, support and calibration need more evidence

Taxonomy drafts passed structural checks and received qualitative acceptance, but no numeric human rubric was recorded. One repeated classification agreed; that is not long-run stability. Limited timing, contract, race, privacy, and recovery checks establish specific behaviors. They do not measure citation entailment or calibrated confidence. No complete RAGAS-style question-answering evaluation or independent production accuracy study was performed. Historical timings use nearest-rank percentiles from twenty observations, not a production guarantee. Subscription-based Codex checks were supplementary, not replacements for real API validation.

### Build the next evaluation before choosing another layer

A stronger study needs independent annotations, unseen initiatives, harder neighbors, no-match cases, and broader languages. Freeze policy and source snapshots before comparing methods. Group related repositories when splitting, and report per-kind errors, abstention, source support, correction effort, and total cost. Confidence intervals and model-winner claims should follow adequate data rather than being manufactured from this small reused set.

## Stronger retrieval and contextual retrieval

Purpose: Add a retrieval layer only when its errors and costs justify the change.

### Stronger retrieval and contextual retrieval

Section sixteen. Stronger retrieval and contextual retrieval. The purpose is to investigate specific weaknesses without mistaking architectural complexity for improvement. Everything in the research lane is a proposal or external reference, not a current product capability.

### Fix evidence selection before adding a new model

First preserve complete sentences, decisive passages, and contradiction. Align evidence validation with exactly what was transmitted. Compare candidate-conditioned passage selection with today's simple packing at the same token ceiling. Sparse experiments can vary term frequency, field weights, alias order, boosts, and smaller caps. These tests ask which error is fixed, rather than assuming the next layer must be better.

### Dense and hybrid search need versioned units and filters

A public-only bi-encoder trial could embed concept definitions and repository-purpose profiles separately. A small registry can use exact local similarity before an approximate-neighbor service. Cache by content and encoder version; preserve identity and access metadata. If dense search recovers real lexical misses, compare sparse and dense unions with reciprocal-rank fusion. A reranker adds cost and cannot recover a candidate absent from that union. Private embeddings are derived content and need separate permission.

### Contextual retrieval enriches indexed chunks

Now, contextual retrieval. Its purpose is to make an indexed chunk meaningful beyond its isolated words. Anthropic's approach adds document-conditioned context before indexing chunks with embeddings and BM25, with optional reranking. Our deterministic metadata and purpose excerpts are not that mechanism. A trial could compare cheap metadata prefixes with generated context, accounting for indexing, refresh, privacy, and downstream support. External published results do not become measured GitHub Manager improvements merely by showing the reference diagram.

### Bounded escalation is different from an autonomous agent

A future controller could allow one extra source-linked evidence pass after an insufficient-context result, under a reviewed budget, then abstain. Adaptive RAG, Self-RAG, and corrective RAG are research references, not adopted implementations. Agentic retrieval would additionally need tool permissions and trajectory evaluation. Domain relationships alone do not create GraphRAG. Application memory does not make the model remember conversations.

## Decision models: the Jev research question

Purpose: Test bounded semantic judgments without changing multi-label meaning or user authority.

### Decision models: the Jev research question

Section seventeen. Decision models, and the Jev research question. The purpose is to investigate whether a specialized decision interface could improve bounded judgments after the options are known. No Jev integration or live Jev test has been performed here.

### Ask support questions rather than forcing one winner

TypeSafe describes Choice, Score, and Noul primitives for typed judgments. For repository organization, a candidate could be supported, unsupported, or unclear. Ask separately for each candidate when several memberships are possible. Open-ended taxonomy discovery still needs generation to propose new names and definitions. A choice among existing options cannot replace that creative vocabulary step.

### Confidence and provider changes need their own evaluation

A probability-derived decision confidence is not the same as today's generated confidence number, and neither proves task calibration. A shadow study should retain the baseline, test negation and option order, and measure high-confidence errors, abstention, fallback, review effort, and total spending. Extra provider credentials, retention terms, retries, and failures require their own controls. Faster decisions do not guarantee better completed workflows.

### Semantic judgment cannot grant operational authority

Potential uses include candidate filtering, passage relevance, duplicate-review triage, or bounded assignment. Any filter can discard a correct candidate. Budget arithmetic, privacy policy, stable-ID validity, rejections, and stale-state protection stay deterministic. Adoption should require a measured quality-cost tradeoff on independent data, not a vendor headline. We finish by following the entire current workflow once more.

## The complete trace and next steps

Purpose: Reconnect each mechanism to the repository the user wanted to find.

### The complete trace and next steps

Section eighteen. The complete trace and next steps. The purpose is to reconnect the technical layers to the original need: find useful repositories, understand why they belong together, and keep control as the collection changes.

### Trace one decision from source to reviewed state

Orion's source sentence explains patient intake, the clinical initiative, FastAPI, and Python. Local extraction retains evidence one. Retrieval finds six possibilities. Augmentation supplies evidence, definitions, policy, and schema. Generation returns four supported IDs. Validation and review establish usable relationships. A receipt preserves completed work even if the user later removes a Project.

### Preserve evidence while improving the system

Readiness phases, frozen corpora, source hashes, lockfiles, reports, and historical ledgers preserve what was actually tested. Reconstructing a request offline is not recovering an original wire log. This animation does not rerun application or model benchmarks. The original academic, illustrated, and publication editions remain available with exact inputs, formulas, qualifications, and references.

### Improve the useful outcome, not just the architecture

The next steps are better evidence packing, tighter validation parity, independent evaluation, and only then conditional retrieval or decision-model experiments. Cloud migration needs separate concurrency and recovery validation. The practical habit is simple: put the source, shortlist, request, answer, and resulting state beside one another. Change one user decision, follow the next run, and measure what improved.
