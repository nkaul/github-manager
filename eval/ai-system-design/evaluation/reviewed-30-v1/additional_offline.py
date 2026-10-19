"""Keyword and quote-visibility diagnostics; no models or reference edits."""

import json
from collections import Counter

from runner import OUT, corpus, read, save, verify  # isort: skip

from app.pretest.ai.evidence import yake_phrases


def norm(text):
    return " ".join(text.casefold().split())


def main():
    verify()
    c = corpus()
    cases, profiles, inputs = (
        read(OUT / name)
        for name in ("reference-snapshot.json", "profiles.json", "classification-inputs.json")
    )
    extraction, visibility = [], []
    counts = Counter()
    for rid, case in cases.items():
        prof = profiles[rid]
        text = "\n".join(e["text"] for e in prof["evidence"])
        keywords = yake_phrases(text)
        extraction.append(
            {
                "id": rid,
                "rake": prof["phrases"],
                "yake": keywords,
                "rake_top8_characters": sum(len(p["text"]) for p in prof["phrases"][:8]),
                "yake_top8_characters": sum(len(p["text"]) for p in keywords[:8]),
                "candidate_input_unchanged": True,
            }
        )
        by_id = {
            label["id"]: label
            for label in c.proposals[int(rid)]["labels"]
            if label.get("decision", "SUPPORTED") == "SUPPORTED"
        }
        profile_text = "\n".join(e["text"] for e in prof["evidence"])
        supplied_text = "\n".join(e["text"] for e in inputs[rid]["payload"]["evidence"])
        for cid in case["positive_ids"]:
            added = case["review"].get("additional_evidence", {}).get(cid)
            proofs = [added] if added else by_id.get(cid, {}).get("evidence", [])
            quotes = [p.get("quote", "") for p in proofs if p.get("quote", "").strip()]
            row = {
                "id": rid,
                "concept_id": cid,
                "quoted_reference": bool(quotes),
                "exact_profile_quote": any(q in profile_text for q in quotes),
                "exact_request_quote": any(q in supplied_text for q in quotes),
                "normalized_profile_quote": any(norm(q) in norm(profile_text) for q in quotes),
                "normalized_request_quote": any(norm(q) in norm(supplied_text) for q in quotes),
            }
            visibility.append(row)
            counts.update(
                {
                    key: int(row[key])
                    for key in (
                        "quoted_reference",
                        "exact_profile_quote",
                        "exact_request_quote",
                        "normalized_profile_quote",
                        "normalized_request_quote",
                    )
                }
            )
    save(
        "extraction-comparison.json",
        {
            "repositories": len(extraction),
            "records": extraction,
            "limits": "YAKE and RAKE are phrase comparisons over identical selected evidence. The current ranker queries evidence text, not phrase scores: candidate recall is identical by construction, not a YAKE quality win. No paid generation ablation performed.",
        },
    )
    save(
        "quote-visibility.json",
        {
            "positive_pairs": len(visibility),
            "counts": dict(counts),
            "records": visibility,
            "limits": "Recorded-quote lexical containment only, not semantic entailment or proof that no other supporting passage exists. Only actual repository evidence is searched; candidate definitions excluded.",
        },
    )
    print(
        json.dumps(
            {
                "phrase_comparison_repositories": len(extraction),
                "quote_visibility": dict(counts),
                "positive_pairs": len(visibility),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
