# Alias boost: proposed plain-language clarification

**Supporting explanation · October 20, 2026 · The user authorized a brief explanation; the main walkthrough now includes the FastAPI example and the once-per-label/token-matching qualifications below. This fuller note is retained for reference.**

An **alias** is another name stored for an approved taxonomy item. For example, the Topic **Web APIs** has the alias `FastAPI` in the authored example registry.

Think of the local search as doing two checks:

1. **Word-overlap score:** compare the repository evidence with each label’s name, description and aliases. Shared words contribute to an IDF-weighted cosine score; words that are rarer among label documents count more.
2. **Name/alias bonus:** if the evidence contains all the significant words of a label’s name **or any one alias**, add **3** to that label’s score. This is an extra application rule, not part of the basic TF-IDF formula.

For **Orion Clinical Platform**, the local overlap score is **0.7382**. Its name’s significant words appear in the evidence, so the application adds **3**:

```text
0.7382 word-overlap score + 3 name/alias bonus = 3.7382 ranking score
```

For **Web APIs**, its alias `FastAPI` is present in “Uses FastAPI and Python,” so it receives the same **+3** bonus. The rule recognizes the stored technology alias even though the displayed canonical name is different.

The bonus is added **once per label**, even if the name and several aliases match. After lowercasing, tokenization and stopword removal, the significant words can appear in any order or in separate passages; this code does **not** require an adjacent, exact phrase match. A one-word alias can therefore be a powerful but sometimes broad signal.

The bonus means **“put this existing label near the front of the choices to inspect.”** It does not prove the label is appropriate and does not assign it. A final score of 3.7382 is **not a probability or confidence percentage**. Scores stay local; the LLM receives shortlisted IDs, kinds, names and descriptions, together with compact evidence and phrase clues, and must select supported labels.

## Source and status

- Verified against `Retriever.candidates()` in [`backend/app/pretest/ai/evidence.py`](../../../backend/app/pretest/ai/evidence.py).
- Worked values come from the preserved [`retrieval.json`](retrieval.json) and [`registry.json`](registry.json) documentation examples.
- No application algorithm, prompt, payload, evaluation result or live model call changed.
