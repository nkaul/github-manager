"""Application source policy and versioned extraction, preserving the frozen benchmark."""

import re

from app.pretest.ai.evidence import profile
from app.pretest.ai.storage import digest


def model_allowed(repo):
    return (
        repo.get("private") is False
        and not repo.get("unavailable")
        and repo.get("source") in {"PUBLIC_GITHUB", "SYNTHETIC"}
        and repo.get("policy_verified") is True
    )


def build_profile(repo, readme=""):
    if not model_allowed(repo):
        raise ValueError("Private/unverified repositories cannot enter model evidence")
    # RST directives/badges were observed as noise; correct only app v2, never benchmark v1.
    readme = re.sub(
        r"^\s*\.\.\s+(?:image|badge|raw|include|toctree)::.*(?:\n[ \t]+.*)*", "", readme, flags=re.M
    )
    record = {
        "id": repo["key"],
        "name": repo["name"],
        "description": repo.get("description") or "",
        "topics": repo.get("topics", []),
        "language": repo.get("language"),
        "sha": repo.get("readme_sha"),
        "private": False,
        "source": repo["source"],
        "readme": readme,
    }
    result = profile(record)
    result["extractor"] = "demo-rake-tfidf-v2"
    result["hash"] = digest({"base": result["hash"], "version": result["extractor"]})
    return result


def sample_records():
    from app.pretest.ai.corpus import load_corpus
    from app.pretest.ai.settings import PRIVATE_ROOT

    records = load_corpus(PRIVATE_ROOT / "ai-pretest", fetch=False)
    chosen = {"synthetic/orion-api", "synthetic/orion-ui", "fastapi/fastapi"}
    repos = {}
    profiles = {}
    for r in records:
        if r["id"] not in chosen and r.get("name") != "fastapi/fastapi":
            continue
        key = r["id"]
        synthetic = r["source"] == "SYNTHETIC"
        repo = {
            "key": key,
            "id": r.get("numeric_id"),
            "name": r["name"] if synthetic else r.get("canonical_name", key),
            "description": r["description"],
            "language": r["language"],
            "topics": r["topics"],
            "private": False,
            "source": r["source"],
            "policy_verified": True,
            "html_url": None
            if synthetic
            else r.get("html_url", "https://github.com/fastapi/fastapi"),
            "owner": "synthetic" if synthetic else "fastapi",
            "default_branch": None,
            "branch_count": None,
            "eligible": False,
            "favorite": False,
            "included": True,
            "sources": ["SYNTHETIC" if synthetic else "PUBLIC_SAMPLE"],
            "readme_sha": r["sha"],
            "decision_version": 0,
            "activities": [],
            "synthetic": synthetic,
            "starred": False,
            "watched": False,
            "fetched_at": r.get("fetched_at"),
        }
        repos[key] = repo
        profiles[key] = build_profile(repo, r.get("readme", ""))
    if len(repos) != 3:
        raise ValueError("Approved three-repository sample corpus missing; run Phase 0.5 setup")
    return repos, profiles
