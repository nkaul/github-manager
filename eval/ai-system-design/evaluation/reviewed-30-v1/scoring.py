"""Partial-label scoring: unknown is never silently converted to false positive."""

from collections import Counter


def score(records, registry):
    result = {}
    for kind in ("PROJECT", "TOPIC", "TAG", "ALL"):
        counts = Counter()
        for row in records:
            positive = {
                cid
                for cid in row["positive_ids"]
                if kind == "ALL" or registry[cid]["kind"] == kind
            }
            predicted = {
                cid
                for cid in row.get("predicted_ids", [])
                if cid in registry and (kind == "ALL" or registry[cid]["kind"] == kind)
            }
            negative = set(row.get("explicit_negative_ids", []))
            counts.update(
                {
                    "repositories": 1,
                    "reviewed_positives": len(positive),
                    "retrieved_positives": len(
                        positive & set(row.get("candidate_ids", []))
                    ),
                    "selected_positives": len(positive & predicted),
                    "predicted_pairs": len(predicted),
                    "explicitly_unsupported_predictions": len(predicted & negative),
                    "unjudged_predictions": len(predicted - positive - negative),
                    "completed_predictions": int(row.get("status") == "PASS"),
                    "exact_positive_set_matches": int(
                        row.get("status") == "PASS" and positive == predicted
                    ),
                }
            )
        p, tp, fp = (
            counts["reviewed_positives"],
            counts["selected_positives"],
            counts["explicitly_unsupported_predictions"],
        )
        result[kind] = dict(counts) | {
            "candidate_recall_of_reviewed_positives": counts["retrieved_positives"] / p
            if p
            else None,
            "prediction_recall_of_reviewed_positives": tp / p if p else None,
            "candidate_conditional_positive_recall": tp / counts["retrieved_positives"]
            if counts["retrieved_positives"]
            else None,
            "judged_precision": tp / (tp + fp) if tp + fp else None,
            "predicted_judgement_coverage": (tp + fp) / counts["predicted_pairs"]
            if counts["predicted_pairs"]
            else None,
            "exhaustive_precision": None,
            "exhaustive_f1": None,
        }
    return result
