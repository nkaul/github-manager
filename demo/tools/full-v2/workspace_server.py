"""Recording-only copy of the real account. No fixture repositories or AI outputs."""

import json
import os
import sys
from pathlib import Path

import httpx
from fastapi import HTTPException, Request
from starlette.responses import JSONResponse

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "backend"))
from app.demo.ai import DemoAISettings, DemoProvider
from app.demo.allowance import ApplicationLedger
from app.local import LocalSettings, create_local_app
from app.pretest.ai.provider import ProviderBlocked

PRIVATE = ROOT / "docs/validation/private/demo/full-v2"
USER = json.loads((PRIVATE / "inspection.json").read_text())["user"]
LEDGER = ApplicationLedger(PRIVATE / "ai")
HTTP_CAP = 4
AUDIT = PRIVATE / "live-http.json"
PUBLIC_NAMES = {"allegro/ralph", "acassen/keepalived"}
PUBLIC_PROOFS = {}


class PublicOnlyProvider(DemoProvider):
    def invoke(self, model, task, schema, system, evidence, validator, **kwargs):
        rows = evidence.get("collection", [evidence])
        state = app.state.database.read(str(USER["id"]) + ":github")
        for row in rows:
            key = row.get("repo_id")
            repo = state["core"]["repos"].get(key, {})
            if (
                repo.get("name") not in PUBLIC_NAMES
                or repo.get("private") is not False
                or repo.get("source") != "PUBLIC_GITHUB"
                or not PUBLIC_PROOFS.get(key)
            ):
                raise ProviderBlocked(
                    "Demo export denied: evidence is not freshly verified public allowlisted input"
                )
        if evidence.get("private") is not False:
            raise ProviderBlocked("Private model input denied")
        return super().invoke(
            model, task, schema, system, evidence, validator, **kwargs
        )


class PublicAdapter:
    """Revalidate only genuinely public repositories against api.github.com."""

    async def request(self, token, path, **kw):
        state = app.state.database.read(str(USER["id"]) + ":github")
        public = [
            r for r in state["core"]["repos"].values() if r.get("private") is False
        ]
        allowed = {"/repositories/" + str(r["id"]) for r in public} | {
            "/repos/" + r["name"] + "/readme" for r in public
        }
        if path not in allowed or kw.get("data"):
            raise ValueError(
                "Recording copy permits only public metadata and README reads"
            )
        async with httpx.AsyncClient(
            timeout=20, trust_env=False, follow_redirects=False
        ) as client:
            r = await client.get(
                "https://api.github.com" + path,
                headers={
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
        r.raise_for_status()
        result = r.json()
        if path.startswith("/repositories/"):
            if (
                result.get("private") is not False
                or result.get("full_name") not in PUBLIC_NAMES
            ):
                raise ValueError(
                    "Only named public repositories may be extracted for live demo inference"
                )
            PUBLIC_PROOFS["github.com#" + str(result["id"])] = True
        return result, r


def recording_provider(mode, authorized):
    provider = PublicOnlyProvider(
        DemoAISettings(
            ai_pretest_live_enabled=True,
            ai_pretest_max_retries=0,
            ai_pretest_state_directory=PRIVATE / "ai",
        ),
        LEDGER,
        mode=mode,
        authorized=authorized,
    )

    def bound(request):
        calls = json.loads(AUDIT.read_text()) if AUDIT.exists() else []
        if len(calls) >= HTTP_CAP:
            raise ProviderBlocked(
                "Full demo four-request live intelligence limit reached"
            )
        if not os.getenv("FULL_DEMO_ALLOW_LIVE") == "1":
            raise ProviderBlocked("Recording rehearsal: live requests disabled")
        calls.append({"path": request.url.path, "state": "DISPATCHED"})
        AUDIT.write_text(json.dumps(calls, indent=2) + "\n")

    for client in [provider.counter, provider.client]:
        client.event_hooks["request"].insert(0, bound)
    return provider


app = create_local_app(
    LocalSettings(
        _env_file=None,
        github_client_id="recording-copy",
        github_client_secret="unused",
        app_origin="http://127.0.0.1:3000",
        demo_live_ai=True,
        demo_budget_operator_ids=str(USER["id"]),
    ),
    adapter=PublicAdapter(),
    db_path=PRIVATE / "app.sqlite3",
    provider_factory=recording_provider,
    allowance_ledger=LEDGER,
)


@app.post("/api/v1/recording/resume")
def resume(request: Request):
    if request.headers.get("x-recording-key") != os.environ["FULL_DEMO_SESSION_KEY"]:
        raise HTTPException(403, "Recording coordinator required")
    cookie = app.state.sessions.create(
        USER, "public-read-only-no-github-token", ["repo"], 7200
    )
    r = JSONResponse({"source": "REAL_ACCOUNT_COPY"})
    r.set_cookie("gm_session", cookie, httponly=True, samesite="lax")
    return r


@app.post("/api/v1/recording/reopen")
def reopen(request: Request):
    from copy import deepcopy

    from app.demo import domain
    from app.demo.store import identifier

    if not app.state.sessions.get(request.cookies.get("gm_session")):
        raise HTTPException(401, "Recording session required")
    import sqlite3

    with sqlite3.connect(PRIVATE / "source.sqlite3") as db:
        source = json.loads(
            db.execute(
                "SELECT state FROM workspace WHERE id=?", (str(USER["id"]) + ":github",)
            ).fetchone()[0]
        )
    prior = next(iter(source["organization"]["drafts"].values()))

    def action(state):
        d = deepcopy(prior)
        d.update(
            id=identifier(),
            status="DRAFT",
            evidence="REPLAY",
            fence=domain.fence(state),
            revision=state["organization"]["control"]["revision"],
            notes="Reopened saved real-model result for review demonstration; no new model call.",
        )
        d.pop("edited_proposals", None)
        state["organization"]["drafts"][d["id"]] = d
        return {"id": d["id"], "source": "SAVED_REAL_MODEL_RESULT"}

    return app.state.database.mutate(str(USER["id"]) + ":github", action)


@app.post("/api/v1/recording/restore")
def restore(request: Request):
    if request.headers.get("x-recording-key") != os.environ["FULL_DEMO_SESSION_KEY"]:
        raise HTTPException(403, "Recording coordinator required")
    import sqlite3

    with sqlite3.connect(PRIVATE / "source.sqlite3") as db:
        source = json.loads(
            db.execute(
                "SELECT state FROM workspace WHERE id=?", (str(USER["id"]) + ":github",)
            ).fetchone()[0]
        )

    def action(state):
        state.clear()
        state.update(source)
        state["organization"]["control"]["auto_enabled"] = False

    app.state.database.mutate(str(USER["id"]) + ":github", action)
    return {"source": "RESTORED_REAL_ACCOUNT_COPY"}
