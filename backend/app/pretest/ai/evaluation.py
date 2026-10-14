import math
from collections import Counter


def metrics(records, registry):
    result = {}
    for kind in ("PROJECT", "TOPIC", "TAG", "ALL"):
        tp = fp = fn = positives = 0
        for record in records:
            gold = {i for i in record["gold"] if kind == "ALL" or registry[i]["kind"] == kind}
            predicted = {
                i for i in record["predicted"] if kind == "ALL" or registry[i]["kind"] == kind
            }
            tp += len(gold & predicted)
            fp += len(predicted - gold)
            fn += len(gold - predicted)
            positives += bool(gold)
        precision = tp / (tp + fp) if tp + fp else None
        recall = tp / (tp + fn) if tp + fn else None
        f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None
        result[kind] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "positive_repos": positives,
            "label_support": tp + fn,
            "repos": len(records),
        }
    return result


def candidate_recall(cases, candidate_sets, registry):
    result = {}
    for kind in ("PROJECT", "TOPIC", "TAG"):
        total = found = 0
        for repo in cases:
            gold = {i for i in repo["labels"] if registry[i]["kind"] == kind}
            total += len(gold)
            found += len(gold & set(candidate_sets[repo["id"]]))
        result[kind] = {"found": found, "gold": total, "recall": found / total if total else None}
    return result


def percentiles(values):
    if not values:
        return {"n": 0, "p50": None, "p95": None}
    ordered = sorted(values)
    return {
        "n": len(values),
        "p50": ordered[math.ceil(len(values) * 0.50) - 1],
        "p95": ordered[math.ceil(len(values) * 0.95) - 1],
    }


def organization_simulation(results, registry):
    user_edges, rejections = {"p-audit"}, {"p-helios"}
    proposed = set(results) - rejections - user_edges
    snapshot = {
        "USER": sorted(user_edges),
        "PROPOSED": sorted(proposed),
        "REJECTED": sorted(rejections),
    }
    domains = {
        registry[i]["domain"]
        for i in user_edges | proposed
        if i in registry and registry[i]["kind"] == "PROJECT"
    }
    return {
        "state": "COMPLETED",
        "associations": snapshot,
        "domains": sorted(domains),
        "canonical_published": False,
        "github_mutations": 0,
    }


def corpus_groups(cases):
    """Group by explicit initiative name, with unrelated samples kept as outliers."""
    groups = Counter()
    assignments = {}
    for case in cases:
        name = case["name"]
        group = name.split("-", 1)[0] if case["source"] == "SYNTHETIC" else "public-outliers"
        assignments[case["id"]] = group
        groups[group] += 1
    return {
        group: [c["id"] for c in cases if assignments[c["id"]] == group]
        for group, count in groups.items()
        if count >= 2
    }
