# GitHub Manager — animated article companion plan

Date: October 15, 2026. Status: **Proposed; awaiting approval.**

This plan incorporates the request for a short animated introduction, the subsequent request to animate all substantive concepts in the articles and earlier detailed diagrams, and the clarification that prose needs its own explanatory motion. Only planning and read-only inspection have been performed. Production starts after approval.

## Purpose and recommended package

Help a viewer understand why GitHub Manager exists, follow the information through its AI workflow, and retain the context when the explanation becomes technical. The opening problem is practical: a repository list shows names and technologies, but does not reliably explain which repositories belong to an initiative or why an association should be trusted.

Produce a linked package from one shared set of scenes:

| Output | Proposed scope | Intended audience |
|---|---|---|
| Short introduction | Approximately two minutes: purpose, workspace, four organization dimensions, evidence → AI suggestion → user review, and continuity | A first-time viewer deciding what the app does |
| Complete animated companion | Provisionally 25–30 minutes, with individually accessible chapters; final duration follows the coverage map and measured speech | Readers who want the reasoning, algorithms, data, tradeoffs and results explained visually |
| Chapter clips | The companion's chapters exported separately, with short orientation slates | A viewer following a particular article section |
| Animated diagram references | Eight approximately 20–60-second silent sequences corresponding to the eight detailed illustrated figures; exact duration follows each mechanism | Readers revisiting a diagram alongside the detailed article |
| Explanation and evidence package | Transcript, captions, source/scene map, animation sources, media accounting and Markdown validation report | Accessibility, review, reproducibility and later revisions |

The introduction will reuse scenes and narration from the master. It will have its own opening and closing, so it works independently. The longer companion preserves the concepts that do not fit in two minutes. Duration is an estimate, not a reason to remove substantive insights. Bibliography entries and exact payloads remain in the linked reference material; mechanisms, caveats and consequences receive visual explanation.

The existing article editions and diagrams remain available. A new local companion index will connect article sections, videos, transcripts and original figures without rewriting previous editions. External publication is a later action.

## Source and style audit

The [core README](../../../../README.md) supplies the product premise and intended experience. It explicitly describes intended architecture; some diagrams include deferred infrastructure. The [v2 article](article.md), [worked examples](workflow-examples.md), [claim checks](claim-checks.md), [academic edition](../../github-manager-ai-system-design.md) and [illustrated edition](../../illustrated/github-manager-ai-system-design-illustrated.md) supply implementation status, actual examples, measurements and qualifications.

These sources have different roles. A proposed component in the README must not become a current feature merely because an older illustration shows it. The current runtime is local Next.js/FastAPI/SQLite. The public demo site hosts explanatory media; it is not a hosted deployment of that interactive runtime.

| Existing asset | Planned use |
|---|---|
| [System overview](../../../../docs/diagrams/github_manager_system_overview.png) | Product orientation and principal visual reference: people, repository documents, robot and workspace |
| [Evidence to decisions](../figures/01-evidence-to-decisions.png) | Opening journey from repository discovery to user-owned organization |
| [Two AI phases](figures/01-two-ai-phases.png) | Vocabulary discovery, review and canonical publication; separate per-repository classification |
| [Data through classification](figures/02-data-through-classification.png) | Orion evidence, six candidates, assembled request and four returned labels |
| [Remember the analysis](../figures/02-remember-the-analysis.png) | Durable receipts, local reconciliation, NO_MATCH and explicit refresh |
| [Accountable calls](../figures/03-accountable-model-calls.png) | Count, reserve, generate and record |
| [Eight detailed illustrations](../../illustrated/figures/README.md) | Full technical coverage and eight animated reference sequences |
| [Academic diagram sources](../../figures/README.md) | Exact-label cross-checks and mechanism structure; illustration style comes from the hand-drawn editions |
| [Existing selected voice preview](../../../../demo/voice-preview-v2/README.md) | Cedar Option D delivery reference |
| [Earlier production plan](../../../../docs/planning/demo-video-v2.md) | Lessons about narration pacing, synchronization and preservation |

The established visual language is white paper, dark pen outlines, handwritten headings, rounded documents/cards, recognizable human and robot characters, circled steps, flowing arrows, and light indigo/blue/purple marker washes. Motion should preserve this language.

Existing PNGs are flattened artwork, not editable character rigs. They can be shown intact, framed through browser viewports, highlighted and revealed. Independently moving documents, words, chips, arrows and state indicators need separate layers. These layers will be drawn as SVG/HTML in the same ink-and-marker treatment, with deterministic text. If a new illustrated pose is necessary, use the existing images as references for a small addition; do not imply a flat PNG can automatically provide convincing articulated character animation.

## How prose becomes animation

Each substantive passage gets an explanation record:

```text
Source section → viewer's question → starting data/state
→ visible operation → resulting data/state → practical consequence
→ qualification → narration cue → source artifact
```

The animation is an illustrated sequence of events. A paragraph about a policy becomes a visible choice; a paragraph about a failure becomes a state transition; an algorithm becomes a transformation of understandable data. Reusing a complete diagram is useful for orientation, but the mechanism is then demonstrated with individual objects and readable labels.

| Idea conveyed in prose | Proposed motion | What a viewer should understand |
|---|---|---|
| Shared Python/FastAPI does not establish shared initiative membership | Bring a public FastAPI library card and synthetic Orion application card together; align their technology chips; connect only the application to the Orion Project | Technology similarity and Project identity answer different questions |
| Four organization dimensions | Move one repository into a Project relationship, reveal its parent Domain, and retain independent Topic/Tag chips; add a second Project to demonstrate many-to-many membership | Domains derive through Projects; Topics and Tags still help when no Project applies |
| Context has authority boundaries | Separate source facts, untrusted README text, approved concepts and execution identity into labeled lanes; show only the appropriate compact data entering the request | Not all stored context is sent to the model or granted equal authority |
| Chunking and evidence selection | Reveal README blocks, select purpose text, attach E0/E1 identifiers, and animate character/byte bounds separately from the eventual token count | Selected excerpts retain provenance; they are not an LLM summary |
| RAKE versus prose | Split selected text into phrases, show co-occurrence/frequency contributions, then place the complete purpose sentence beside the keyword chips | Keywords aid matching but do not replace relationships or negation in prose |
| Taxonomy discovery differs from classification | Several repository profiles feed a proposed concept draft; a person edits and approves it; a separate lane starts from one repository and approved candidate IDs | Proposing vocabulary and assigning relationships are different jobs |
| Retrieval returns possibilities | Highlight matching words, reveal cosine/alias score components and fill the six Orion candidate slots | A positive search score does not establish membership |
| Augmentation has concrete contents | Evidence/phrases, candidate IDs/definitions, and policy/schema cards assemble into a request envelope; display a brief actual JSON excerpt | The viewer can see what the LLM receives and why |
| Generation returns a bounded proposal | Use the saved Orion response to reveal four selected IDs and E1 references while Forge and Package Management remain unselected | The answer selects approved IDs; it is not an invented label list or hidden reasoning trace |
| Negation changes the decision | Keep “not part of Helios or Orion” visible while both names retrieve candidates; leave both Project candidates unselected in the saved result | Search matches and semantic support can disagree |
| Compaction can lose decisive evidence | Animate FastAPI's purpose passage staying in the full profile while links occupy the compact slots; mark the documented packing weakness | A correct answer does not prove every preprocessing step was ideal |
| Hidden canonical conflicts | Search an active-name shelf, then reveal a matching alias or archived reservation; demonstrate opt-in reuse, rename or removal | A reserved term need not be another visible active display name |
| Validation and user authority | Pass a returned ID through workspace/kind/candidate/evidence checks, pause at review, and reject a stale return after a user edit | A well-formed response still needs application validation and human authority |
| Remembered processing is separate from labels | Remove a Project chip while the receipt remains; route the next run to local reconciliation; show NO_MATCH retaining completed status | Removing an assignment does not erase completed analysis or authorize a new paid call |
| Scheduling is a controlled loop | Accumulate change events, cross a configurable threshold, wait through quiet/cooldown windows, then check analysis admission | Automatic organization does not silently override no-repeat protection |
| Budget, concurrency and uncertainty | Reserve from a finite balance before generation; show competing requests contending for it; settle known usage and retain an uncertain reservation | Cost controls include failures and concurrent work, not just a progress counter |
| Evaluation has separate layers | Show expected labels entering retrieval, then predictions entering TP/FP/FN trays; distinguish a retrieved miss from a decision miss | Candidate recall, assignment quality and workflow correctness measure different things |
| More tokens or layers need evidence | Compare prompt representations and historical token counts; show proposed retrieval layers with incremental latency/cost labels | Adding phrases, embeddings or a reranker is an experiment, not an automatic improvement |
| Jev is a future bounded-decision option | Branch into a clearly marked research lane with per-candidate support questions, uncertainty and fallback; keep open-ended vocabulary generation separate | A decision model may help a narrow judgment, but is not currently integrated or validated here |

Animation will reveal observable inputs, operations and outputs. The robot is an explanatory character, not a claim that internal model reasoning was recorded. Illustrative user edits and synthetic repository fixtures stay labeled.

## Keep context visible throughout

Use one primary example, `synthetic/orion-api`, through extraction, retrieval, augmentation, generation and later state changes. Its anchor sentence is:

> Patient intake API for the Orion Clinical Platform. Uses FastAPI and Python.

The saved six-candidate shortlist contains Orion, Forge, Web APIs, Package Management, FastAPI and Python. The saved real-provider result selects Orion, Web APIs, FastAPI and Python, citing E1. These are historical observations from an authored synthetic fixture, not a new live classification or a real private repository.

A persistent, compact path shows **Discover → Evidence → Vocabulary → Retrieve → Request → Review → Remember**. The active position changes as the film progresses. Vocabulary is a collection-level branch feeding classification; the path is an orientation aid, not a false claim that every repository creates a new vocabulary.

Keep the repository's name, current evidence and accepted/proposed state visible when relevant. Introduce an unfamiliar term after its example, explain it in everyday language, then show the technical label. Each chapter briefly recalls the state it starts from and states what its result enables next. Counterexamples temporarily branch from Orion, then return to the main path.

Use shape, icon and text labels alongside color. Keep **Current**, **Historical test**, **Illustrative replay**, **Compared offline**, **External research** and **Proposed** visibly distinct. Future branches use a separate labeled area; color alone will not carry these distinctions.

## Full companion chapter and coverage plan

The table defines coverage rather than final cuts. The narration/shot map will expand these into individual beats after approval. The first chapter also supplies most of the short introduction.

| Chapter | Story and animated explanation | Coverage in the detailed article |
|---|---|---|
| C01 — Why GitHub Manager exists | Scattered owned/shared/starred repositories become an inspectable workspace. Show discovery, browsing, search, AI suggestions and manual control through illustrated scenes. End with the problem of two repos sharing technologies but serving different purposes | README premise; academic §1; v2 opening |
| C02 — What organization means | Domains, Projects, Topics and Tags; derived Domain membership; multi-Project repository; Topic/Tag-only repository; local Topics versus native GitHub topics | Academic §1.1; v2 vocabulary |
| C03 — What the system knows and trusts | GitHub facts versus user organization versus README evidence; local Next.js/FastAPI/SQLite and server credential boundary; privacy before counting; public/synthetic hosted input; development context hierarchy and Phase 0/0.5/0.9 provenance | Academic §2–4; detailed figure 01 |
| C04 — From README to source-linked evidence | CommonMark/heading policy, selection and cleaning, metadata fallback, block/document bounds, source hashes, cleaned offsets, complete versus compact profile, format/negation truncation risks | Academic §5; detailed figure 03; v2 evidence |
| C05 — What keywords can and cannot do | RAKE phrase splitting/scoring and provenance; YAKE comparison; distinct-document frequency; corpus support versus semantic clustering; one-case token ablation | Academic §6 and §14.3; v2 keywords |
| C06 — Discover and review a vocabulary | Owner/language cohort selection, compact collection/byte packing and exact counting, actual 30-profile taxonomy example, draft schema/support IDs, review/publication, normalized alias/archive conflicts and opt-in repairs | Academic §10; v2 taxonomy; two-phase figure |
| C07 — Retrieve candidates, not conclusions | Concepts are the retrieved documents; binary-IDF cosine versus count TF-IDF; alias token-set boost, per-kind caps/ties, actual Orion scores; BM25 saturation/length normalization and alias-only comparison; sparse choice and limitations | Academic §7; detailed figure 02; v2 retrieval |
| C08 — What enters and leaves the LLM | Compact evidence + phrases + candidate definitions + instructions + schema; aliases' retrieval-only role; LangChain binding; actual request excerpt and saved four-ID answer; generation settings and model roles; broad/simple RAG with application memory | Academic §3, §8 and §14.1; v2 augmentation |
| C09 — The awkward examples | Negated API, FastAPI packing/secondary-label issue, multiple Projects, empty/no-match and metadata-only cases, installation noise, multilingual/injection limitations. Reuse concrete fixtures where supported and label illustrative operations | Academic §8.4 and §16; v2 counterexamples |
| C10 — Turn a proposal into durable user decisions | Schema/ID/workspace/kind/candidate/evidence validation; review; manual precedence/rejections/rules; stale versions and reset fences; documented validation parity gaps rather than invented guarantees | Academic §8.2–8.3, §10.2 and §12.4; v2 validation |
| C11 — Memory and controlled loops | Separate relationships, receipts, freshness and review; replay cache versus durable processing history; local rule/stored/alias reconciliation; explicit reasoned re-analysis; weighted/distinct events, quiet/cooldown and no automatic paid resend | Academic §11–12; detailed figure 04; v2 memory |
| C12 — The execution harness | Authorization, exact assembled-request token count, atomic reservations, finite HTTP/generation grants, retries disabled, in-flight/unknown recovery, fixed versus adaptive limits, reset does not refill cost history | Academic §13; detailed figure 05; v2 harness |
| C13 — Tokenomics and useful optimization | Input/schema/output/reasoning accounting, historical rate snapshots, reservation versus settlement, cache discounts versus no-call savings, historical totals, representation tradeoffs, cohort/candidate caps, count latency, media/infra/review costs kept separate | Academic §14; v2 economics |
| C14 — What the evaluations establish | Corpus/split/registry and user-approved references; candidate recall versus per-kind/micro P/R/F1; 50 TP/0 FP/2 FN, small reused-set qualification; taxonomy qualitative review, limited stability/timing/model comparison, contract/race tests; RAG evaluation gaps and source-entailment needs | Academic §15 and §19; detailed figure 06; v2 evaluation |
| C15 — Stronger retrieval: what to test next | Better sentence/passage packing; sparse ablations; versioned bi-encoder units and hash cache; dense exact scoring before ANN; hard access filters; sparse/dense union and RRF; conditional cross-encoder reranking; contextual prefixes/Anthropic comparison; bounded escalation versus Adaptive/Agentic/GraphRAG/Self-RAG/CRAG; independent/grouped evaluations and quality–cost tradeoffs | Academic §9 and §17–19; detailed figures 07–08; v2 research |
| C16 — Decision models and the complete trace | Jev Choice/Score/Noul as research; per-candidate judgments preserve multi-label output; confidence/calibration, shadow tests and finite fallback; deterministic authority stays in code. Close by retracing source → candidates → request → answer → review → remembered state | v2 Jev section/research note and conclusion; academic §18.7–20 |

Every substantive v2 section, every academic mechanism-inventory row, every detailed-figure requirement, and each material documented limitation will be assigned to an animated narration beat or animated reference sequence in the coverage map. A link alone does not satisfy concept coverage. Exact formulas and full JSON can have longer pauseable reference views and links after their underlying mechanism has been animated. A missing mapping blocks the completeness claim; an estimated runtime does not justify dropping it.

The discovery draft and classification benchmark used separate registries. The animation can explain how the phases relate architecturally, but must not present these saved examples as one historical publish-and-classify run.

## Animation and rendering approach

Build a small deterministic scene renderer using the existing local Node, Playwright/Chrome and FFmpeg tooling. The bundled FFmpeg 7.1 executable was checked successfully. Node, Playwright and Chrome are present. The scene renderer itself is new work proposed here; the earlier pipeline captured UI actions and cannot simply be relabeled as an illustration-animation engine.

Use HTML/SVG scene layers with an explicit `seek(time)` timeline. Objects have stable IDs, positions and start/end states. Draw arrows progressively, move evidence cards between stages, reveal phrase/score contributions, emphasize decisive words, change assignment/receipt status and pause on consequences. Limited motion on people/robots can add warmth while the information-carrying motion remains clear. Focus one causal change at a time.

Existing raster illustrations remain source artwork. Browser viewports and overlays can focus on a region without rewriting source pixels. Additional code-native cards, icons and paths supply independent motion and large readable labels. New raster illustration generation/editing, if necessary, uses the image generation workflow with inspected style references and preserves originals. Proposed allowance: at most two image-generation requests, separate from the application inference ledger. No external generative-video service or new subscription is required by this approach.

Render in restartable scene chunks and encode **1920×1080, 30 fps, H.264 MP4 with AAC audio**. Keep intermediate frames/chunks cached so adjusting one scene does not repeat the whole render or regenerate narration. Export chapter clips and reference sequences from the shared timeline. Use video loops for quality/size; an additional GIF can be derived later if a publishing platform needs one.

Text is laid out separately from moving artwork where it needs to remain legible. Target 44–60 px for essential labels and readable two-line captions, with approximately 90 px edge margins and a dedicated subtitle area. Tiny labels from a complete source diagram will be enlarged or restated in a focused view. All exact strings, IDs and numbers are deterministic text; motion does not morph their spelling.

## Narration and synchronization

Retain **Cedar, Option D: warm and deliberate delivery**, matching the prior selected voice. Aim for roughly 130–145 spoken words per minute with intentional viewing pauses; measure the result rather than treating a speed parameter as proof. Use coherent multi-scene takes with identical directions, pronunciation guidance and room for transitions.

The official [speech guide](https://developers.openai.com/api/docs/guides/text-to-speech) documents Cedar and delivery instructions. The [deprecation schedule](https://developers.openai.com/api/docs/deprecations) lists the previous TTS snapshots for removal on January 6, 2027. For this near-term production, recheck access to the existing narration model before paid generation; do not silently change the selected voice or replace its delivery with another provider. The [model page](https://developers.openai.com/api/docs/models/gpt-4o-mini-tts) lists token-based pricing, so estimated media reservations must not be described as a reconciled invoice.

Generate narration once per approved take, retain it, obtain spoken timing, and lock visual cues to the measured audio. A highlight or decision should appear when its corresponding phrase is spoken, with the result held long enough to read. Caption text follows the script and verified timing; recognized omissions must be repaired locally or explicitly reviewed. Avoid using speech stretching to force a target runtime.

The soundtrack is speech-led. Keep AI-generated voice disclosure in the player/credits. Package VTT/SRT captions and a full transcript. Technical audio checks establish levels and clipping, not human naturalness: representative listening and the user's early sample feedback remain part of review.

Proposed API scope after approval: **at most 16 additional OpenAI HTTP requests and a $2 incremental media-accounting allowance**, covering availability checks, narration, alignment and targeted retakes. Plan approximately eight to ten initial speech takes, up to three alignment requests, and preserve room for a check/retakes within the shared 16-request limit. Client retries are disabled; failed and uncertain requests count. Cache successful takes and retain conservative cost holds when billing usage is unavailable. The existing cumulative $5 ceiling and historical reservations remain in force; execution must check remaining headroom before dispatch and admit no request that exceeds either bound. This plan does not reset an earlier ledger or authorize fresh repository classification, taxonomy benchmarks or Jev tests.

Only the sanitized narration script and generated narration audio are needed by speech/alignment services. No app login or private account content is needed for this animated explanation. The prior permission for unmasked real-account walkthrough footage does not turn a synthetic article example into real account data.

## Phased production after approval

| Stage | Work and reviewable result | Exit condition |
|---|---|---|
| A — Coverage and script | Freeze source hashes; produce paragraph/mechanism → scene mapping, narration, visual states, captions and factual-status labels; inventory all eight detailed figures | Every substantive concept mapped; current/historical/proposed distinctions correct; no unsupported improvement claims |
| B — Representative motion sample | Render a 45–60-second narrated sample spanning evidence → candidate shortlist → request → supported result, using the actual Orion example and selected style | User can review motion, legibility, voice and timing before long-form production |
| C — Full scene system | Complete all chapter scenes and eight reference sequences using reusable assets/timeline components; produce the remaining narration only after sample feedback | Full source coverage, readable inputs/outputs and visible causal transitions |
| D — Assembly and verification | Export master, short intro, chapters, loops, captions, transcript, player and report; inspect motion/audio and preserve prior artifacts | Decode/playback/synchronization/content/preservation checks pass, with limitations recorded |

Approval now authorizes the complete package within the stated scope and limits. Share the representative sample early for feedback while preparing the remaining coverage and scenes; incorporate that feedback before final assembly. A routine render or edit does not require another permission request. A change to the voice, paid limits or publication scope would need a separate decision.

## Deliverables and preservation

Proposed new output locations:

```text
eval/ai-system-design/animation/
  README.md                 Local article/chapter/reference index
  storyboard.md             Narration, visible actions and source mapping
  coverage.json             Sections/mechanisms/figure requirements → beats
  assets-manifest.json       Source hashes, status and new-asset provenance
  transcript.md
  validation.md              Factual, visual, audio, accounting and preservation QA

demo/tools/article-animation/
  ...                       Renderer, timeline, audio/admission and verification tools

demo/article-animation/
  overview-1080p.mp4
  complete-1080p.mp4
  captions.vtt / captions.srt
  chapters/                 Individually playable chapter clips
  diagram-loops/            Eight animated detailed-diagram references
  poster.png
  index.html                Local chapter/caption/loop player
  timing.json
  media-qa.json
  speech-requests.json       Sanitized accounting/provenance, never credentials
```

Use new folders and read existing assets as sources. Preserve academic, illustrated, v1 and v2 article bytes, original diagrams, previous videos/voices, benchmark fixtures, reports and ledgers. The new companion index links them rather than changing historical results. Application source, real workspace state, cloud resources and model defaults are outside this production task.

## Acceptance checks

1. **Coverage:** all substantive v2 sections, detailed-figure requirements and academic algorithm/mechanism rows map to a visible animated explanation in the companion or a reference clip. No chapter relies solely on a pan across dense prose, and a prose link does not replace an animation.
2. **Factual fidelity:** verify actual example text, six candidates/four outputs, phase separation, protected user decisions, no-repeat policy and current runtime. Historical measures retain dates, denominators and caveats. Proposed methods remain labeled proposed.
3. **Motion and legibility:** inspect every scene transition and representative intermediate states; no overlapping labels, clipped cards, unwanted raster distortion or subtitle collisions. Important data remains readable at 1080p and in a smaller player. Provide static posters/transcript for readers who do not want motion.
4. **Synchronization:** inspect phrase-to-action cues, caption boundaries and result holds; a stable visual must precede the next explanation. Do not equate matching total durations with synchronization.
5. **Audio:** check decoded sound, pronunciation consistency, audible edits, clipping, silence and loudness. Target approximately −16 LUFS with true peaks below −1 dBTP; record measured values and listening limitations.
6. **Media/player:** verify resolution/frame rate/codec, full decode, seek, captions, chapter boundaries and local links. Loop resets should be intentional and non-distracting.
7. **Accounting/preservation:** report attempts, retakes, retained holds and known usage separately; respect both approved caps; compare protected hashes and historical ledger/report records without rewriting them.

This is an explanation and media-validation project. It does not establish new application reliability, model quality, retrieval superiority or audience engagement results. Existing readiness records retain their original meaning.

## Approval requested

Approve the **two-minute introduction + complete chaptered companion + animated references**, the existing hand-drawn visual language, Cedar's calmer delivery, and the bounded media scope above. Share the representative motion sample early and incorporate feedback before final assembly. Publishing/uploading to the public demo repository remains a separate action.
