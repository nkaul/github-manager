"""Local conflict checks and opt-in repairs; publication remains an explicit transaction."""

import json
from copy import deepcopy
from hashlib import sha256

from app.demo import domain


def editable(state, draft_id, revision):
    domain.writable(state)
    org = state["organization"]
    draft = org["drafts"].get(draft_id)
    if not draft or draft["status"] != "DRAFT" or org["control"]["revision"] != revision:
        raise ValueError("Draft unavailable or taxonomy changed; review current revision")
    if draft.get("fence"):
        domain.check_fence(state, draft["fence"])
    return draft


def canonical(state, value):
    return next(
        (
            c
            for c in state["organization"]["concepts"].values()
            if c["active"]
            and c["kind"] == value["kind"]
            and domain.normalize(c["name"]) == domain.normalize(value["name"])
        ),
        None,
    )


def check(state, values):
    conflicts, reused, seen = [], [], {}
    parents = {
        domain.normalize(term)
        for c in state["organization"]["concepts"].values()
        if c["active"] and c["kind"] == "DOMAIN"
        for term in [c["id"], c["name"], *c["aliases"]]
    } | {
        domain.normalize(term)
        for v in values
        if v["kind"] == "DOMAIN"
        for term in [v["name"], *v["aliases"]]
    }
    for i, value in enumerate(values):
        existing = canonical(state, value)
        if existing:
            reused.append(
                {
                    "proposal_index": i,
                    "id": existing["id"],
                    "name": existing["name"],
                    "kind": existing["kind"],
                    "message": f"Proposal {i + 1} reuses existing {existing['kind'].lower()} "
                    f"“{existing['name']}” and its stable ID. "
                    "Existing metadata and aliases stay unchanged.",
                }
            )
        local = domain.term_conflicts(state, value, excluding=existing["id"] if existing else None)
        # Exact canonical reuse retains existing metadata: proposed aliases are not installed.
        if existing:
            local = [c for c in local if c["type"] != "RESERVED_TERM"]
        for c in local:
            conflicts.append({**c, "proposal_index": i})
        for field, index, term in [
            ("name", None, value["name"]),
            *(("alias", j, text) for j, text in enumerate(value["aliases"])),
        ]:
            key = (value["kind"], domain.normalize(term))
            if key in seen and seen[key][0] != i:
                peer, peer_term = seen[key]
                conflicts.append(
                    {
                        "type": "DUPLICATE_PROPOSAL",
                        "proposal_index": i,
                        "field": field,
                        "alias_index": index,
                        "term": term,
                        "normalized": key[1],
                        "incoming_name": value["name"],
                        "kind": value["kind"],
                        "peer_index": peer,
                        "message": f"{'Canonical name' if field == 'name' else 'Alias'} “{term}” "
                        f"in proposal {i + 1} conflicts with “{peer_term}” in proposal {peer + 1} "
                        f"({values[peer]['name']}) of the same type after normalization.",
                    }
                )
            else:
                seen[key] = (i, term)
        if value["kind"] == "PROJECT" and not existing:
            if domain.normalize(value.get("domain") or "") not in parents:
                conflicts.append(
                    {
                        "type": "INVALID_PARENT",
                        "proposal_index": i,
                        "field": "domain",
                        "term": value.get("domain") or "",
                        "kind": "PROJECT",
                        "incoming_name": value["name"],
                        "message": f"Project “{value['name']}” refers to domain "
                        f"“{value.get('domain') or '(empty)'}”, which is neither an active domain "
                        "nor an included domain proposal. "
                        "Edit its domain name or exclude the project.",
                    }
                )
        elif value["kind"] != "PROJECT" and value.get("domain"):
            conflicts.append(
                {
                    "type": "INVALID_PARENT",
                    "proposal_index": i,
                    "field": "domain",
                    "term": value["domain"],
                    "kind": value["kind"],
                    "incoming_name": value["name"],
                    "message": "Only projects can have a parent domain; "
                    f"clear it on “{value['name']}”.",
                }
            )
    for c in conflicts:
        row = values[c["proposal_index"]]
        if c["field"] == "name":
            c["suggested_name"] = domain.distinct_name(
                state,
                row,
                [
                    term
                    for v in values
                    if v["kind"] == row["kind"]
                    for term in [v["name"], *v["aliases"]]
                ],
            )
        actions = [{"kind": "EXCLUDE", "label": "Exclude this proposal"}]
        if c["field"] == "alias":
            actions.insert(0, {"kind": "REMOVE_ALIAS", "label": f"Remove alias “{c['term']}”"})
        if c.get("suggested_name"):
            actions.insert(0, {"kind": "RENAME", "label": f"Use name “{c['suggested_name']}”"})
        if c.get("existing", {}).get("active"):
            actions.append({"kind": "REUSE", "label": f"Reuse existing “{c['existing']['name']}”"})
        c["actions"] = actions
        c["id"] = sha256(json.dumps(c, sort_keys=True).encode()).hexdigest()[:24]
    return {"valid": not conflicts, "conflicts": conflicts, "reused": reused}


def rewrite_parents(values, old_terms, name):
    old = {domain.normalize(term) for term in old_terms}
    for v in values:
        if v["kind"] == "PROJECT" and domain.normalize(v.get("domain") or "") in old:
            v["domain"] = name


def remediate(state, values, action, conflict_id):
    analysis = check(state, values)
    updated = deepcopy(values)
    if action == "CLEAN_ALIASES":
        remove = {}
        for c in analysis["conflicts"]:
            if c["field"] == "alias":
                remove.setdefault(c["proposal_index"], set()).add(c["alias_index"])
        for i, indices in remove.items():
            updated[i]["aliases"] = [
                t for j, t in enumerate(updated[i]["aliases"]) if j not in indices
            ]
        message = "Removed conflicting aliases from the submitted draft values."
    else:
        c = next((c for c in analysis["conflicts"] if c["id"] == conflict_id), None)
        if not c or action not in {a["kind"] for a in c["actions"]}:
            raise ValueError(
                "Conflict changed or repair is unavailable; check the current draft again"
            )
        i = c["proposal_index"]
        row = updated[i]
        if action == "REMOVE_ALIAS":
            row["aliases"].pop(c["alias_index"])
        elif action == "RENAME":
            old = row["name"]
            row["name"] = c["suggested_name"]
            if row["kind"] == "DOMAIN":
                rewrite_parents(updated, [old], row["name"])
        elif action == "REUSE":
            existing = c["existing"]
            if row["kind"] == "DOMAIN":
                rewrite_parents(updated, [row["name"], *row["aliases"]], existing["name"])
            row.update(
                {k: existing[k] for k in ("kind", "name", "description", "aliases", "domain")}
            )
        elif action == "EXCLUDE":
            updated.pop(i)
        message = next(a["label"] for a in c["actions"] if a["kind"] == action) + "."
    return {
        "proposals": updated,
        "check": check(state, updated),
        "message": message
        + " Review the changes before saving or publishing. Live taxonomy is unchanged.",
    }


def publish(state, draft_id, revision, values):
    draft = editable(state, draft_id, revision)
    analysis = check(state, values)
    if analysis["conflicts"]:
        raise domain.TaxonomyConflict(analysis["conflicts"])
    org, parents, result = state["organization"], {}, []
    for c in org["concepts"].values():
        if c["active"] and c["kind"] == "DOMAIN":
            for term in [c["id"], c["name"], *c["aliases"]]:
                parents[domain.normalize(term)] = c["id"]
    for kind in ("DOMAIN", "PROJECT", "TOPIC", "TAG"):
        for value in values:
            if value["kind"] != kind:
                continue
            value = deepcopy(value)
            existing = canonical(state, value)
            if value["kind"] == "PROJECT":
                value["domain"] = parents.get(domain.normalize(value.get("domain") or ""))
            item = existing or domain.create_concept(state, value, origin="AI_ACCEPTED")
            result.append(item)
            if kind == "DOMAIN":
                for term in [
                    item["id"],
                    item["name"],
                    *item["aliases"],
                    value["name"],
                    *value["aliases"],
                ]:
                    parents[domain.normalize(term)] = item["id"]
    org["control"]["revision"] = revision + 1
    for event in org["changes"]:
        if event["revision"] > revision:
            event["revision"] = revision + 1
    draft["status"] = "PUBLISHED"
    return {"concepts": result, "revision": revision + 1, "reused": analysis["reused"]}
