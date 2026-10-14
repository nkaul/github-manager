"""Four-generation real-provider proof with a clearly synthetic app session; no GitHub calls."""

import argparse
import asyncio
import json
import time
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.auth.sessions import SessionStore
from app.config import REPO_ROOT
from app.demo.ai import budget_summary
from app.local import LocalSettings, create_local_app
from app.pretest.ai.storage import private_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", required=True)
    parser.parse_args()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    directory = REPO_ROOT / "docs/validation/private/demo" / ("live-" + stamp)
    sessions = SessionStore()
    owner = {
        "id": 9090009,
        "login": "phase09-public-validation",
        "name": "Synthetic Validation Session",
    }
    cookie = sessions.create(owner, "not-a-github-token", [], 3600)
    app = create_local_app(
        LocalSettings(demo_live_ai=True), sessions=sessions, db_path=directory / "app.sqlite3"
    )
    client = TestClient(app, base_url="http://127.0.0.1:8000")
    client.cookies.set("gm_session", cookie)
    client.headers.update(
        {"Origin": "http://127.0.0.1:3000", "X-CSRF-Token": sessions.get(cookie).csrf_token}
    )
    workspace = str(owner["id"]) + ":samples"
    before = budget_summary()
    if before.get("unavailable") or before["http"]["remaining"] < 8:
        raise SystemExit("Need eight authorized HTTP slots; no calls made")
    results = []
    started = time.monotonic()

    def post(path, body=None):
        response = client.post("/api/v1" + path, params={"collection": "samples"}, json=body)
        if response.status_code >= 400:
            raise ValueError("Local API validation failed: " + str(response.status_code))
        return response.json()

    def run(mode):
        post("/organizer/reorganize", {"mode": mode, "ai_mode": "LIVE"})
        job = app.state.database.claim({workspace})
        asyncio.run(app.state.service.perform(job))
        result = app.state.database.read(workspace)["organization"]["runs"][job["id"]]
        results.append(result)
        print(
            json.dumps(
                {
                    "kind": mode,
                    "status": result["status"],
                    "processed": result["processed"],
                    "failed": result["failed"],
                    "message": result.get("message"),
                }
            ),
            flush=True,
        )
        return result

    post("/samples/load")
    first = run("DISCOVER")
    if first["status"] == "COMPLETED":
        state = app.state.database.read(workspace)
        draft = next(iter(state["organization"]["drafts"].values()))
        proposals = [
            {k: p[k] for k in ("kind", "name", "description", "aliases")}
            | {"domain": p["parent_domain"]}
            for p in draft["proposals"]
        ]
        post(
            "/taxonomy/drafts/publish",
            {
                "draft_id": draft["id"],
                "proposals": proposals,
                "expected_revision": state["organization"]["control"]["revision"],
            },
        )
        run("FULL_CLASSIFICATION")
    after = budget_summary()
    state = app.state.database.read(workspace)
    seconds = round(time.monotonic() - started, 3)
    private_json(
        directory / "integration.local.json",
        {
            "session": "SYNTHETIC_VALIDATION_SESSION",
            "sources": "PUBLIC_AND_SYNTHETIC",
            "before": before,
            "after": after,
            "runs": results,
            "seconds": seconds,
            "organization": state["organization"],
        },
    )
    report = REPO_ROOT / "docs/validation" / ("phase-0-9-live-ai-" + stamp + ".md")
    lines = [
        "# Phase 0.9 real AI integration check",
        "",
        f"UTC: {stamp}. Duration: {seconds}s.",
        "",
        "Session: synthetic authenticated app fixture, not a live GitHub OAuth observation.",
        "Inputs: public FastAPI sample + two synthetic Orion examples; no private data.",
        "Real OpenAI HTTP via LangChain, product schemas and shared durable budget.",
        "",
        "| Run | Status | Processed | Failed | Model / evidence |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['kind']} | {r['status']} | {r['processed']}/{r['total']} | "
            f"{r['failed']} | {r.get('model', 'per-repo')} / {r.get('evidence', 'per-repo')} |"
        )
        for key, o in r["outcomes"].items():
            u = o.get("usage") or {}
            lines.append(
                f"| {key} | {o['status']} | — | — | {o.get('model')} / {o['evidence']}; "
                f"{u.get('input_tokens')} in, {u.get('output_tokens')} out; {o.get('seconds')}s |"
            )
    lines += [
        "",
        f"New HTTP slots: {after['http']['used'] - before['http']['used']}; "
        f"phase total {after['http']['used']}/20.",
        f"New generation reservations: {after['calls'] - before['calls']}; "
        f"cumulative {after['calls']}/44.",
        f"Estimated cumulative cost: ${after['estimated_usd']:.6f}; "
        f"outstanding ${after['reserved_usd']:.6f}; original ceiling $5.",
        "",
        "Isolated publication proof; normal UI publication requires human review.",
        "Suggestions only; integration evidence, not a quality benchmark.",
        f"Private diagnostics: `{directory.relative_to(REPO_ROOT)}`.",
    ]
    report.write_text("\n".join(lines) + "\n")
    print(
        json.dumps(
            {"report": str(report.relative_to(REPO_ROOT)), "seconds": seconds, "budget": after}
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
