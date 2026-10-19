"""Disposable UI server: real corpus files, fake identity, isolated SQLite and no AI."""

import tempfile
from pathlib import Path

from fastapi import Query, Request
from starlette.responses import JSONResponse

from app.demo.allowance import ApplicationLedger
from app.local import LocalSettings, create_local_app
from tests.demo.fixtures import Adapter, Provider

_directory = tempfile.TemporaryDirectory(prefix="ghm-corpus-browser-")
app = create_local_app(
    LocalSettings(
        github_client_id="test-fixture",
        github_client_secret="test-fixture",
        app_origin="http://127.0.0.1:3015",
    ),
    adapter=Adapter(),
    provider_factory=Provider,
    db_path=Path(_directory.name) / "app.sqlite3",
    allowance_ledger=ApplicationLedger(Path(_directory.name) / "ai", initialize=True),
)


@app.middleware("http")
async def reject_reserved_app_ports(request: Request, call_next):
    if request.scope.get("server", (None, None))[1] in {3000, 8000}:
        return JSONResponse(
            {"detail": "Fixture server requires isolated test ports"}, status_code=503
        )
    return await call_next(request)


@app.post("/api/v1/test/login")
def login(user_id: int = Query(9120, alias="id", ge=9000, le=99999)):
    cookie = app.state.sessions.create(
        {"id": user_id, "login": "corpus-ui-test", "name": "Disposable corpus test"},
        "fixture-only",
        ["repo"],
        3600,
    )
    response = JSONResponse({"fixture": True})
    response.set_cookie("gm_session", cookie, httponly=True, samesite="lax")
    return response
