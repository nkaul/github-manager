"""Domain invariants shared by routes and durable workers."""

import re
import time
import unicodedata
from datetime import UTC, datetime

from app.demo.store import identifier


def now():
    return datetime.now(UTC).isoformat()


def normalize(value):
    return re.sub(r"[^\w+#]+", " ", unicodedata.normalize("NFKC", value).casefold()).strip()


def fence(state):
    c = state["organization"]["control"]
    return {
        k: c[k]
        for k in (
            "generation",
            "taxonomy_epoch",
            "ai_epoch",
            "cache_epoch",
            "revision",
            "policy_version",
        )
    }


def check_fence(state, expected):
    if state["organization"]["control"]["resetting"] or fence(state) != expected:
        raise ValueError("Stale workspace generation, taxonomy or policy; result discarded")


def writable(state):
    if state["organization"]["control"]["resetting"]:
        raise ValueError("Reset cleanup is in progress")


def active(state, key):
    c = state["organization"]["concepts"].get(key)
    if not c or not c["active"]:
        raise ValueError("Active concept not found")
    return c


def changed(state, concept, change_type, weight=1):
    org = state["organization"]
    org["control"]["revision"] += 1
    change_event(state, concept, change_type, weight)


def change_event(state, concept, change_type, weight=1):
    org = state["organization"]
    sequence = max(org["control"].get("change_sequence", 0), len(org["changes"])) + 1
    org["control"]["change_sequence"] = sequence
    org["changes"].append(
        {
            "sequence": sequence,
            "entity": concept,
            "type": change_type,
            "weight": weight,
            "revision": org["control"]["revision"],
            "at": time.time(),
        }
    )
    org["changes"] = org["changes"][-500:]


class TaxonomyConflict(ValueError):
    def __init__(self, conflicts):
        self.conflicts = conflicts
        super().__init__(conflicts[0]["message"])


def distinct_name(state, item, extra=()):
    reserved = {
        normalize(term)
        for c in state["organization"]["concepts"].values()
        if c["kind"] == item["kind"] and not c.get("merged_into")
        for term in [c["name"], *c["aliases"]]
    } | {normalize(t) for t in extra}
    base = item["name"].strip() or item["kind"].title()
    for i in range(2, 10000):
        suffix = f" ({i})"
        candidate = base[: 100 - len(suffix)].rstrip() + suffix
        if normalize(candidate) not in reserved:
            return candidate
    raise ValueError("Choose a distinct name manually")


def term_conflicts(state, item, excluding=None):
    conflicts, seen = [], {}
    terms = [
        ("name", None, item["name"]),
        *(("alias", i, text) for i, text in enumerate(item["aliases"])),
    ]
    for field, index, term in terms:
        word = normalize(term)
        base = {
            "field": field,
            "alias_index": index,
            "term": term,
            "normalized": word,
            "incoming_name": item["name"],
            "kind": item["kind"],
        }
        label = "Canonical name" if field == "name" else "Alias"
        if not word or len(word) > 100:
            conflicts.append(
                {
                    **base,
                    "type": "INVALID_TERM",
                    "message": f"{label} “{term}” on {item['kind'].lower()} “{item['name']}” "
                    "must contain letters/numbers and be at most 100 normalized characters.",
                }
            )
        elif word in seen:
            conflicts.append(
                {
                    **base,
                    "type": "DUPLICATE_TERM",
                    "message": f"{label} “{term}” repeats {seen[word]} in "
                    f"{item['kind'].lower()} “{item['name']}” after normalization.",
                }
            )
        seen[word] = f"“{term}”"
    for other in state["organization"]["concepts"].values():
        # Archived concepts retain reservations to prevent unwanted recreation.
        if other["id"] == excluding or other["kind"] != item["kind"] or other.get("merged_into"):
            continue
        for field, index, term in terms:
            for matched_field, matched in [
                ("name", other["name"]),
                *(("alias", text) for text in other["aliases"]),
            ]:
                if normalize(term) and normalize(term) == normalize(matched):
                    conflicts.append(
                        {
                            "type": "RESERVED_TERM",
                            "field": field,
                            "alias_index": index,
                            "term": term,
                            "normalized": normalize(term),
                            "incoming_name": item["name"],
                            "kind": item["kind"],
                            "existing": {
                                k: other.get(k)
                                for k in (
                                    "id",
                                    "kind",
                                    "name",
                                    "aliases",
                                    "description",
                                    "domain",
                                    "active",
                                )
                            },
                            "matched_field": matched_field,
                            "matched_term": matched,
                            "message": f"{'Canonical name' if field == 'name' else 'Alias'} "
                            f"“{term}” on {item['kind'].lower()} “{item['name']}” is reserved "
                            f"as {'the canonical name' if matched_field == 'name' else 'an alias'} "
                            f"of {'active' if other['active'] else 'archived'} "
                            f"{other['kind'].lower()} “{other['name']}” (matched “{matched}”).",
                        }
                    )
    for conflict in conflicts:
        if conflict["field"] == "name":
            conflict["suggested_name"] = distinct_name(state, item, item["aliases"])
    return conflicts


def validate_terms(state, item, excluding=None):
    conflicts = term_conflicts(state, item, excluding)
    if conflicts:
        raise TaxonomyConflict(conflicts)
    if item["kind"] == "PROJECT":
        parent = active(state, item.get("domain"))
        if parent["kind"] != "DOMAIN":
            raise ValueError("Projects require an active domain")
    elif item.get("domain"):
        raise ValueError("Only projects have a parent domain")


def create_concept(state, value, *, origin="USER"):
    writable(state)
    if len(state["organization"]["concepts"]) >= 500:
        raise ValueError("Local demo limit: 500 concepts")
    item = {**value, "id": identifier(), "active": True, "origin": origin, "created_at": now()}
    validate_terms(state, item)
    state["organization"]["concepts"][item["id"]] = item
    changed(
        state,
        item["id"],
        "CREATE_PROJECT" if item["kind"] == "PROJECT" else "CREATE",
        3 if item["kind"] == "PROJECT" else 1,
    )
    return item


def edit_concept(state, key, value):
    writable(state)
    item = active(state, key)
    updated = {**item, **value}
    validate_terms(state, updated, excluding=key)
    state["organization"]["concepts"][key] = updated
    if updated != item:
        cosmetic = normalize(updated["name"]) == normalize(item["name"]) and all(
            updated.get(k) == item.get(k) for k in ("description", "aliases", "domain")
        )
        changed(
            state,
            key,
            "COSMETIC" if cosmetic else "EDIT",
            0 if cosmetic else 2 if item["kind"] == "PROJECT" else 1,
        )
    return updated


def unassigned(state):
    for c in state["organization"]["concepts"].values():
        if c.get("protected"):
            return c["id"]
    c = create_concept(
        state,
        {
            "kind": "DOMAIN",
            "name": "Unassigned",
            "description": "Projects without an assigned domain",
            "aliases": [],
            "domain": None,
        },
    )
    c["protected"] = True
    return c["id"]


def remove_concept(state, key):
    writable(state)
    item = active(state, key)
    if item.get("protected"):
        raise ValueError("The Unassigned domain is protected")
    org = state["organization"]
    if item["kind"] == "DOMAIN":
        projects = [c for c in org["concepts"].values() if c["active"] and c.get("domain") == key]
        if projects:
            parent = unassigned(state)
            for c in projects:
                c["domain"] = parent
    item["active"] = False
    for edges in org["edges"].values():
        edges.pop(key, None)
    for suggestion in org["suggestions"].values():
        if suggestion["concept_id"] == key and suggestion["status"] == "PROPOSED":
            suggestion["status"] = "INVALIDATED"
    changed(state, key, "ARCHIVE")
    return item


def merge_concepts(state, source, target):
    writable(state)
    a, b = active(state, source), active(state, target)
    if source == target or a["kind"] != b["kind"] or a.get("protected") or b.get("protected"):
        raise ValueError("Merge requires two distinct non-protected concepts of the same kind")
    aliases = list(dict.fromkeys([*b["aliases"], a["name"], *a["aliases"]]))
    if len(aliases) > 6:
        raise ValueError("Merged aliases exceed six; edit aliases first")
    a["merged_into"] = target
    b["aliases"] = aliases
    validate_terms(state, b, excluding=target)
    a["active"] = False
    org = state["organization"]
    for edges in org["edges"].values():
        edge = edges.pop(source, None)
        if edge and (target not in edges or edge["source"] == "USER"):
            edges[target] = {**edge, "concept_id": target}
    for rejects in org["rejections"].values():
        if source in rejects:
            rejects[target] = rejects.pop(source)
    # Rejection wins over automatic membership. An explicit accepted USER edge wins
    # over an older equivalent tombstone when two concepts are intentionally merged.
    for key, rejects in org["rejections"].items():
        edge = org["edges"].get(key, {}).get(target)
        if target in rejects and edge:
            if edge["source"] == "USER":
                rejects.pop(target)
            else:
                org["edges"][key].pop(target)
    for s in org["suggestions"].values():
        if s["concept_id"] == source:
            s["status"] = "INVALIDATED"
    for rule in org["rules"].values():
        if rule["concept_id"] == source:
            rule["concept_id"] = target
    if a["kind"] == "DOMAIN":
        for c in org["concepts"].values():
            if c.get("domain") == source:
                c["domain"] = target
    changed(state, target, "MERGE", 2)
    return b


def mapping(state, repo_keys, concept_ids, operation, source="USER"):
    writable(state)
    org = state["organization"]
    for key in repo_keys:
        modified = False
        repo = state["core"]["repos"].get(key)
        if not repo or repo.get("unavailable"):
            raise ValueError("Accessible repository not found")
        for cid in concept_ids:
            if active(state, cid)["kind"] == "DOMAIN":
                raise ValueError("Domains derive from project membership")
            edges = org["edges"].setdefault(key, {})
            rejects = org["rejections"].setdefault(key, {})
            if operation == "ADD":
                if source != "USER" and cid in rejects:
                    continue
                if cid not in edges or (source == "USER" and edges[cid]["source"] != "USER"):
                    edges[cid] = {"concept_id": cid, "source": source, "at": now()}
                    modified = True
                if source == "USER":
                    modified = bool(rejects.pop(cid, None)) or modified
            else:
                modified = bool(edges.pop(cid, None)) or modified
                if cid not in rejects:
                    rejects[cid] = {"at": now(), "protected": True}
                    modified = True
            for suggestion in org["suggestions"].values():
                if suggestion["repo_key"] == key and suggestion["concept_id"] == cid:
                    suggestion["status"] = "ACCEPTED" if operation == "ADD" else "REJECTED"
        if source == "USER" and modified:
            repo["decision_version"] = repo.get("decision_version", 0) + 1


def rule_matches(rule, repo):
    fields = {
        "name": repo["name"],
        "owner": repo.get("owner", ""),
        "language": repo.get("language") or "",
        "topic": " ".join(repo.get("topics", [])),
    }
    value = fields[rule["field"]].casefold()
    test = rule["value"].casefold()
    if rule["field"] == "topic" and rule["operator"] == "equals":
        return test in [t.casefold() for t in repo.get("topics", [])]
    return value == test if rule["operator"] == "equals" else test in value


def coverage(state):
    org = state["organization"]
    repos = [r for r in state["core"]["repos"].values() if not r.get("unavailable")]
    organized = sum(
        any(
            org["concepts"].get(cid, {}).get("active") and org["concepts"][cid]["kind"] == "PROJECT"
            for cid in org["edges"].get(r["key"], {})
        )
        for r in repos
    )
    return {
        "repos": len(repos),
        "organized": organized,
        "uncategorized": len(repos) - organized,
        "review": sum(s["status"] == "PROPOSED" for s in org["suggestions"].values()),
    }
