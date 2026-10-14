import os
import re
from datetime import UTC, datetime
from pathlib import Path


def cell(value) -> str:
    return str(value).replace("|", "/").replace("\n", " ").replace("\r", " ")


def write_report(directory: Path, prefix: str, title: str, rows: list[dict], notes=()) -> Path:
    if not re.fullmatch(r"[a-z0-9-]+", prefix):
        raise ValueError("Invalid report prefix")
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    target = directory / f"{prefix}-{stamp}.md"
    lines = [
        f"# {title}",
        "",
        f"Run: {stamp}",
        "",
        *notes,
        "",
        "| Check | Evidence | Status | Detail |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(cell(row.get(k, "")) for k in ("check", "evidence", "status", "detail"))
            + " |"
        )
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        stream.write("\n".join(lines) + "\n")
    return target


def github_report(directory: Path, snapshot: dict, scopes: list[str], fixture_rows=()) -> dict:
    rows = [
        {
            "check": "GitHub identity",
            "evidence": "LIVE",
            "status": "PASS",
            "detail": "Authenticated numeric identity matched to this browser session",
        }
    ]
    rows += [
        {
            "check": item["source"],
            "evidence": "LIVE",
            "status": "PASS" if item["status"] == "OBSERVED" else "BLOCKED",
            "detail": f"{item['status']}; observed count={item['count']}; {item['note']}",
        }
        for item in snapshot["coverage"]
    ]
    rows += [
        {"check": name, "evidence": "POLICY", "status": "NOT_TESTED", "detail": detail}
        for name, detail in [
            (
                "Fixture breadth",
                "Named fixtures cover supplied cases only; record missing relationships/orgs",
            ),
            (
                "Production token lifecycle",
                "Local expiry and logout only; durable encryption and refresh remain Phase 1/2",
            ),
        ]
    ]
    rows.extend(fixture_rows)
    path = write_report(
        directory,
        "github",
        "Phase 0 GitHub OAuth access report",
        rows,
        [
            "Connector: OAuth App (user selected). Read-only application calls.",
            f"Signed-in identity: @{cell(snapshot['identity']['login'])}; "
            f"GitHub numeric ID: {snapshot['identity']['id']}.",
            f"Granted scopes: {', '.join(scopes) or '(none returned)'}. Verify actual grants.",
            "Private local report: identity retained for verification; repo names/content omitted.",
            f"Unique accessible inventory: {len(snapshot['repos'])}; "
            f"private: {sum(bool(repo.get('private')) for repo in snapshot['repos'])}; "
            f"eligible My Repos: {sum(bool(repo.get('eligible')) for repo in snapshot['repos'])}; "
            f"Favorites: {sum(bool(repo.get('favorite')) for repo in snapshot['repos'])}.",
            "Disposition: review these GitHub fixture outcomes and the separate AWS evidence.",
        ],
    )
    return {"filename": path.name, "rows": rows}
