"""Shared access-scoped explorer projections for lists, summaries and run cohorts."""

import time
from datetime import datetime

from app.demo import analysis


def repositories(state, workspace, actor, scope=None):
    scope = scope or {}
    view = scope.get("view", "all")
    org = state["organization"]
    active = {key: c for key, c in org["concepts"].items() if c["active"]}
    result = []
    for key, repo in state["core"]["repos"].items():
        if repo.get("unavailable"):
            continue
        edges = (
            {}
            if org["control"]["resetting"]
            else {cid: edge for cid, edge in org["edges"].get(key, {}).items() if cid in active}
        )
        projects = [cid for cid in edges if active[cid]["kind"] == "PROJECT"]
        dates = [x["at"] for x in repo.get("activities", []) if x["actor_id"] == actor]
        recent = max(dates, default=None)
        age = (time.time() - datetime.fromisoformat(recent).timestamp()) / 86400 if recent else None
        view = scope.get("view", "all")
        if view == "my" and not (
            repo.get("eligible") or repo.get("included") and workspace.endswith(":github")
        ):
            continue
        if view == "favorites" and not repo.get("favorite"):
            continue
        if view == "latest" and (age is None or not 0 <= age <= scope.get("days", 14)):
            continue
        if view == "uncategorized" and projects:
            continue
        concept = scope.get("concept", "")
        if (
            concept
            and concept not in edges
            and not any(active[p].get("domain") == concept for p in projects)
        ):
            continue
        language = scope.get("language", "")
        if language == "__UNKNOWN__" and repo.get("language"):
            continue
        if (
            language
            and language != "__UNKNOWN__"
            and (repo.get("language") or "").casefold() != language.casefold()
        ):
            continue
        visibility = scope.get("visibility", "all")
        if visibility != "all" and repo["private"] != (visibility == "private"):
            continue
        text = " ".join(
            [
                repo["name"],
                repo.get("description") or "",
                repo.get("owner", ""),
                repo.get("language") or "",
                *[active[c]["name"] + " " + " ".join(active[c]["aliases"]) for c in edges],
            ]
        )
        if scope.get("q", "").casefold() not in text.casefold():
            continue
        reviews = (
            0
            if org["control"]["resetting"]
            else sum(
                s["repo_key"] == key and s["status"] == "PROPOSED"
                for s in org["suggestions"].values()
            )
        )
        status = analysis.projection(state, key)
        if view == "no_labels" and edges or view == "needs_review" and not reviews:
            continue
        if view == "no_match" and (status.get("last_success") or {}).get("status") != "NO_MATCH":
            continue
        if view == "failed" and status["state"] not in {"FAILED", "UNCERTAIN"}:
            continue
        if view == "stale" and not status["stale"]:
            continue
        counts = {
            kind: sum(active[cid]["kind"] == kind for cid in edges)
            for kind in ("PROJECT", "TOPIC", "TAG")
        }
        result.append(
            {
                **repo,
                "organization": edges,
                "last_user_activity": recent,
                "review_count": reviews,
                "project_count": len(projects),
                "label_count": len(edges),
                "label_counts": counts,
                "domain_ids": sorted({active[p]["domain"] for p in projects}),
                "analysis": status,
            }
        )
    result.sort(
        key=lambda r: (
            (r.get("last_user_activity") or "", r["name"].casefold(), r["key"])
            if view == "latest"
            else (r["name"].casefold(), r["key"])
        ),
        reverse=view == "latest",
    )
    return result


def summary(items):
    return {
        "repos": len(items),
        "organized": sum(bool(r["project_count"]) for r in items),
        "uncategorized": sum(not r["project_count"] for r in items),
        "review": sum(bool(r["review_count"]) for r in items),
        "suggestions": sum(r["review_count"] for r in items),
        "labeled": sum(bool(r["label_count"]) for r in items),
        "no_labels": sum(not r["label_count"] for r in items),
        "projects": sum(bool(r["label_counts"]["PROJECT"]) for r in items),
        "topics": sum(bool(r["label_counts"]["TOPIC"]) for r in items),
        "tags": sum(bool(r["label_counts"]["TAG"]) for r in items),
        "ai_analyzed": sum(r["analysis"]["ai_analyzed"] for r in items),
        "stale": sum(r["analysis"]["stale"] for r in items),
    }


def concepts(state, items):
    """Distinct accepted and separate pending counts, across the entire filtered scope."""
    keys = {r["key"] for r in items}
    return {
        cid: {
            "accepted": sum(cid in r["organization"] or cid in r["domain_ids"] for r in items),
            "pending": len(
                {
                    s["repo_key"]
                    for s in state["organization"]["suggestions"].values()
                    if s["status"] == "PROPOSED"
                    and s["concept_id"] == cid
                    and s["repo_key"] in keys
                }
            ),
        }
        for cid, c in state["organization"]["concepts"].items()
        if c["active"]
    }


def languages(items):
    counts = {}
    for repo in items:
        label = repo.get("language") or "Unknown"
        counts[label] = counts.get(label, 0) + 1
    return [
        {"value": "__UNKNOWN__" if name == "Unknown" else name, "label": name, "count": count}
        for name, count in sorted(counts.items())
    ]
