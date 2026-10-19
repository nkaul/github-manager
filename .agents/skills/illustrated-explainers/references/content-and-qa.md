# Content contract and review

Before generating, make a compact figure contract:

```text
Viewer question and purpose
Source artifacts and date/version
Required facts, exact strings, numbers and units
Relationships and authority boundaries
Current / historical / illustrative / proposed status
Input → operation → output → consequence
Material caveat and source/provenance note
Placement, aspect ratio and reading size
```

Mark which wording must be verbatim and which may be shortened without changing meaning. Avoid a model inventing a representative JSON schema or example ID when the actual one is available. An honest empty request placeholder is preferable to plausible-looking false fields.

## Lessons from actual corrections

- **Excerpt versus summary:** deterministic source selection was incorrectly described as summarization. A model-summary label would imply an additional inference stage. Call the operation what it is.
- **Source coordinates:** character offsets in cleaned evidence were incorrectly drawn as original README line numbers. Label coordinates in the unit and source frame actually recorded.
- **Metadata:** example cards must use fields the application supplies; a familiar Stars/Updated pair is not a substitute for actual Topics/Language inputs.
- **Freshness versus permission:** a change can schedule local reconciliation without authorizing another paid inference. A loop arrow must show that distinction.
- **Valid citation versus supported claim:** an existing evidence ID does not prove entailment. Preserve that caveat beside validation.
- **Ranking versus reranking:** a ranked shortlist is not evidence of a neural reranker, dense index or autonomous retrieval loop.
- **Historical quality:** a small reused regression score is not production accuracy or an independent model-winner study.

These examples are reusable checks for representation errors, not instructions to insert GitHub-specific labels into other subjects.

## Review in useful passes

1. **Meaning and coverage:** compare every content-contract item with the actual figure. Check who owns facts and decisions, which boundary data crosses, and whether arrows imply unsupported relationships.
2. **Exactness:** inspect names, labels, IDs, quantities, inequality signs, denominators and units. Check current versus proposed status and qualifiers near claims. OCR may assist, but it is not sufficient evidence of correctness.
3. **Reading experience:** inspect the actual export at publication size. Look for clipped text, tiny labels, weak contrast, overloaded panels, confusing flow and repeated information. Split dense material when needed.
4. **Targeted correction:** name the wrong region and exact replacement while preserving unrelated illustrations, colors, numbers and facts. Reinspect the corrected export; edits can introduce new mistakes.

For a set of figures, keep a coverage matrix so no mechanism disappears when the design becomes simpler. Preserve original images and exact technical companions when requested. Save generation/edit prompts, source hashes, actual dimensions and a short review record when reproducibility or publication warrants them.

Alt text should describe the mechanism and consequence, not only colors and icons. Captions should define the figure's status and what its measurements do and do not establish. Do not claim user comprehension, engagement or scientific validity merely because visual checks passed.
