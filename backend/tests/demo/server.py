"""Disposable browser test app. Real auth/session/CSRF, explicitly fake external providers."""

import tempfile
from pathlib import Path

from fastapi import HTTPException, Request
from starlette.responses import JSONResponse

from app.demo import domain
from app.demo.allowance import ApplicationLedger
from app.local import LocalSettings, create_local_app
from tests.demo.fixtures import Adapter, Provider

_directory = tempfile.TemporaryDirectory(prefix="ghm-phase09-browser-")
app = create_local_app(
    LocalSettings(
        app_origin="http://127.0.0.1:3016",
        github_client_id="test-fixture",
        github_client_secret="test-fixture",
        demo_live_ai=True,
        demo_budget_operator_ids="9009,9101,9102,9103,9106,9107",
    ),
    adapter=Adapter(),
    provider_factory=Provider,
    db_path=Path(_directory.name) / "app.sqlite3",
    allowance_ledger=ApplicationLedger(Path(_directory.name) / "ai", initialize=True),
)


@app.middleware("http")
async def reject_reserved_app_ports(request: Request, call_next):
    # A fixture entrypoint must never impersonate the app on the user's normal ports.
    if request.scope.get("server", (None, None))[1] in {3000, 8000}:
        return JSONResponse(
            {"detail": "Fixture server requires isolated test ports"}, status_code=503
        )
    return await call_next(request)


@app.post("/api/v1/test/login")
def isolated_ui_identity(value: dict):
    # Test-only route in this disposable server; never imported by app.local.
    actor = value.get("id")
    if actor not in {
        9101,
        9102,
        9103,
        9104,
        9105,
        9106,
        9107,
        9108,
        9161,
        9162,
        9163,
        9164,
        9171,
        9172,
        9173,
    }:
        raise HTTPException(400, "Unknown UI test fixture")
    cookie = app.state.sessions.create(
        {"id": actor, "login": f"ui-fixture-{actor}", "name": "UI Test Fixture"},
        "fixture-only",
        ["repo"],
        3600,
    )
    response = JSONResponse({"fixture": True})
    response.set_cookie("gm_session", cookie, httponly=True, samesite="lax")
    return response


@app.post("/api/v1/test/review-fixture")
def review_fixture(request: Request):
    session = app.state.sessions.get(request.cookies.get("gm_session"))
    if not session or session.user["id"] != 9104:
        raise HTTPException(403, "Review fixture session required")
    workspace = "9104:samples"
    app.state.service.load_samples(workspace)

    def seed(state):
        existing = domain.create_concept(
            state,
            {
                "kind": "DOMAIN",
                "name": "Artificial Intelligence",
                "aliases": ["AI"],
                "description": "Existing fixture domain",
                "domain": None,
            },
        )
        archived = domain.create_concept(
            state,
            {
                "kind": "TAG",
                "name": "Legacy Machine Learning",
                "aliases": ["ML"],
                "description": "Archived fixture tag",
                "domain": None,
            },
        )
        domain.remove_concept(state, archived["id"])
        proposals = [
            {
                "kind": "DOMAIN",
                "name": "AI - Atrificial Intelligence",
                "aliases": ["AI"],
                "description": "New proposal awaiting conflict review",
                "supporting_repo_ids": ["synthetic/orion-api"],
                "domain": None,
            },
            {
                "kind": "PROJECT",
                "name": "AI Workbench",
                "aliases": [],
                "description": "Synthetic project",
                "domain": "AI - Atrificial Intelligence",
            },
            {
                "kind": "TAG",
                "name": "Learning",
                "aliases": ["ML"],
                "description": "Example tag with archived alias conflict",
                "domain": None,
            },
            {
                "kind": "TOPIC",
                "name": "Search",
                "aliases": ["search"],
                "description": "Example duplicate inside one proposal",
                "domain": None,
            },
        ]
        state["organization"]["drafts"]["review-fixture"] = {
            "id": "review-fixture",
            "status": "DRAFT",
            "proposals": proposals,
            "fence": domain.fence(state),
            "notes": "UI FIXTURE — no model call",
            "evidence": "FIXTURE",
            "model": "Deterministic fixture",
            "revision": 3,
        }
        return {"fixture": True, "existing_id": existing["id"], "archived_id": archived["id"]}

    return app.state.database.mutate(workspace, seed)
