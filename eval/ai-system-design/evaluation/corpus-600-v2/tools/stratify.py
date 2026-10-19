"""Deterministic domain-aware allocation of immutable leakage groups, without labels."""
from collections import Counter
import hashlib
import json


def allocate(members, targets):
    def stable(rows):
        return hashlib.sha256(json.dumps(sorted(r['numeric_id'] for r in rows)).encode()).hexdigest()
    groups = sorted(members, key=lambda rows: (-len(rows), stable(rows)))
    domains = Counter(r['sampling_domain'] for rows in groups for r in rows)
    total = sum(domains.values())
    per_domain = {split: {domain: n * target / total for domain, n in domains.items()} for split, target in targets.items()}
    counts = Counter()
    coverage = {split: Counter() for split in targets}
    slots = []
    vectors = [Counter(r['sampling_domain'] for r in rows) for rows in groups]
    def delta(split, vector, size):
        global_target = targets[split]
        change = .3 * (((counts[split] + size - global_target)**2 - (counts[split] - global_target)**2) / global_target)
        for domain, n in vector.items():
            target = per_domain[split][domain]
            change += ((coverage[split][domain] + n - target)**2 - (coverage[split][domain] - target)**2) / target
        return change
    for rows, vector in zip(groups, vectors):
        fitting = [split for split in targets if counts[split] + len(rows) <= targets[split]]
        split = min(fitting or list(targets), key=lambda split: (delta(split, vector, len(rows)), split))
        counts[split] += len(rows)
        coverage[split].update(vector)
        slots.append(split)
    # Equal-size swaps improve domain coverage without changing overall split sizes.
    swaps = 0
    for _ in range(100):
        best = None
        for i, left in enumerate(groups):
            for j in range(i + 1, len(groups)):
                if slots[i] == slots[j] or len(left) != len(groups[j]):
                    continue
                a, b = slots[i], slots[j]
                difference = Counter(vectors[j]);difference.subtract(vectors[i])
                change = delta(a, difference, 0) + delta(b, {key: -n for key,n in difference.items()}, 0)
                if change < -1e-8 and (best is None or change < best[0]):
                    best = (change, i, j, difference)
        if best is None:
            break
        _, i, j, difference = best
        a, b = slots[i], slots[j]
        coverage[a].update(difference)
        coverage[b].subtract(difference)
        slots[i], slots[j] = b, a
        swaps += 1
    assigned, output = {}, []
    for rows, split in zip(groups, slots):
        ids = sorted(r['numeric_id'] for r in rows)
        gid = 'group:' + stable(rows)[:16]
        output.append({'id': gid, 'split': split, 'repository_ids': ids})
        for rid in ids:
            assigned[rid] = {'group': gid, 'split': split}
    return assigned, output, dict(counts), {'method': 'Domain-aware greedy group allocation + equal-size local swaps',
        'per_domain_targets': per_domain, 'per_domain_actual': {s: dict(c) for s,c in coverage.items()},
        'equal_size_swaps': swaps, 'all_groups_preserved': True,
        'limitation': 'Domain stratification uses sampling buckets only; families/owners/near-duplicate groups never split. Exact per-domain proportions may be impossible.'}
