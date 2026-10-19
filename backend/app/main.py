import base64
import hashlib
import hmac
import json
import secrets
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.auth.sessions import Session, SessionStore
from app.config import Settings
from app.github.client import GitHubError, OAuthAppAdapter
from app.pretest.github_probe import fixture_checks
from app.pretest.report import github_report

SESSION_COOKIE, NONCE_COOKIE = "gm_session", "gm_oauth_browser"


def create_app(settings=None, adapter=None, store=None):
    settings = settings or Settings()
    adapter = adapter or OAuthAppAdapter(settings)
    store = store or SessionStore()

    @asynccontextmanager
    async def lifespan(app):
        yield
        store.sessions.clear()
        store.states.clear()

    app = FastAPI(
        title="GitHub Manager Local Preflight",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "[::1]"])

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request, error):
        value = {"detail": error.detail}
        if error.status_code == 401:
            value.update(code="SESSION_EXPIRED", reauthentication_required=True)
        return JSONResponse(value, status_code=error.status_code, headers=error.headers)

    @app.middleware("http")
    async def private_response(request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    def authenticated(request: Request):
        session = store.get(request.cookies.get(SESSION_COOKIE))
        if session is None:
            raise HTTPException(401, "Sign in to GitHub")
        return session

    def mutation(request: Request, session: Session = Depends(authenticated)):
        if request.headers.get("origin") != settings.app_origin or not secrets.compare_digest(
            request.headers.get("x-csrf-token", ""), session.csrf_token
        ):
            raise HTTPException(403, "Invalid Origin or CSRF token")
        return session

    async def snapshot(session):
        if session.snapshot is None or store.clock() - session.snapshot_at > 300:
            try:
                value = await adapter.inventory(session.token)
                if value["identity"]["id"] != session.user["id"]:
                    raise GitHubError("identity_changed; sign in again", 401)
            except GitHubError as exc:
                if exc.status == 401:
                    session.expires_at = 0
                raise HTTPException(401 if exc.status == 401 else 502, exc.category) from None
            session.snapshot = value
            session.snapshot_at = store.clock()
        return session.snapshot

    @app.get("/health")
    def health():
        return {"status": "ok", "phase": 0}

    @app.get("/api/v1/pretest/config")
    def config():
        return {
            "oauth_configured": settings.oauth_configured,
            "callback_url": settings.callback_url,
            "connector": "OAuth App",
            "requested_scopes": settings.github_scopes.split(),
            "local_only": True,
        }

    @app.get("/api/v1/auth/github/start")
    def start(request: Request):
        if not settings.oauth_configured:
            raise HTTPException(
                503,
                "Configure GitHub client ID/secret in backend/.env, then restart the backend",
            )
        browser = secrets.token_urlsafe(32)
        try:
            state, verifier = store.begin(browser, settings.oauth_state_ttl_seconds)
        except ValueError:
            raise HTTPException(429, "Too many pending sign-ins") from None
        response = RedirectResponse(adapter.authorization_url(state, verifier), status_code=302)
        response.set_cookie(
            NONCE_COOKIE,
            browser,
            httponly=True,
            samesite="lax",
            max_age=settings.oauth_state_ttl_seconds,
            path="/api/v1/auth/github",
        )
        return response

    @app.get("/api/v1/auth/github/callback")
    async def callback(request: Request, state: str = "", code: str = "", error: str = ""):
        saved = store.consume(state, request.cookies.get(NONCE_COOKIE, ""))
        if not saved:
            raise HTTPException(400, "Invalid, expired, reused or browser-mismatched OAuth state")
        if error or not code:
            response = RedirectResponse(settings.app_origin + "/?auth=cancelled", status_code=303)
            response.delete_cookie(NONCE_COOKIE, path="/api/v1/auth/github")
            return response
        try:
            value = await adapter.exchange(code, saved.verifier)
            issued_at = store.clock()
            user = await adapter.identity(value["access_token"])
            token_ttl = (
                int(int(value["expires_in"]) - (store.clock() - issued_at))
                if "expires_in" in value
                else None
            )
            if token_ttl is not None and token_ttl <= 0:
                raise ValueError("GitHub grant already expired")
            ttl = min(settings.session_ttl_seconds, token_ttl or settings.session_ttl_seconds)
            key = store.create(
                user,
                value["access_token"],
                [s.strip() for s in value.get("scope", "").split(",") if s.strip()],
                ttl,
                token_ttl=token_ttl,
            )
        except (GitHubError, ValueError, KeyError):
            raise HTTPException(502, "GitHub authorization failed; start sign-in again") from None
        store.discard(request.cookies.get(SESSION_COOKIE))
        response = RedirectResponse(settings.app_origin, status_code=303)
        response.set_cookie(
            SESSION_COOKIE, key, httponly=True, samesite="lax", max_age=ttl, path="/"
        )
        response.delete_cookie(NONCE_COOKIE, path="/api/v1/auth/github")
        return response

    def identity_response(session):
        return {
            "user": session.user,
            "scopes": session.scopes,
            "connector": "OAuth App",
            "csrf_token": session.csrf_token,
            "session": store.metadata(
                session, settings.session_ttl_seconds, settings.session_warning_seconds
            ),
        }

    @app.get("/api/v1/me")
    def me(session: Session = Depends(authenticated)):
        return identity_response(session)

    @app.post("/api/v1/auth/session/extend")
    def extend(request: Request, session: Session = Depends(mutation)):
        key = request.cookies.get(SESSION_COOKIE)
        renewed = store.extend(key, settings.session_ttl_seconds)
        if renewed is None:
            raise HTTPException(401, "Your local session ended. Sign in to GitHub again")
        value = identity_response(renewed)
        response = JSONResponse(value)
        response.set_cookie(
            SESSION_COOKIE,
            key,
            httponly=True,
            samesite="lax",
            max_age=value["session"]["expires_in_seconds"],
            path="/",
        )
        return response

    @app.get("/api/v1/repos")
    async def repos(
        view: Literal["my", "favorites", "all"] = "my",
        limit: int = Query(20, ge=1, le=100),
        cursor: str = Query("", max_length=2048),
        q: str = Query("", max_length=100),
        session: Session = Depends(authenticated),
    ):
        data = await snapshot(session)
        signature = f"{view}:{q}:{session.snapshot_at}"
        offset = 0
        if cursor:
            try:
                decoded, supplied_mac = cursor.split(".")
                expected = hmac.new(
                    session.csrf_token.encode(), decoded.encode(), hashlib.sha256
                ).hexdigest()
                payload = json.loads(base64.urlsafe_b64decode(decoded + "=" * (-len(decoded) % 4)))
                if not hmac.compare_digest(supplied_mac, expected) or payload["scope"] != signature:
                    raise ValueError
                offset = payload["offset"]
                if type(offset) is not int or offset < 0:
                    raise ValueError
            except (ValueError, KeyError, TypeError):
                raise HTTPException(400, "Invalid or stale page cursor; refresh the list") from None
        selected = [
            r
            for r in data["repos"]
            if (
                view == "all"
                or (view == "my" and r["eligible"])
                or (view == "favorites" and r["favorite"])
            )
            and q.lower() in r["full_name"].lower()
        ]
        next_cursor = None
        if offset + limit < len(selected):
            encoded = (
                base64.urlsafe_b64encode(
                    json.dumps({"scope": signature, "offset": offset + limit}).encode()
                )
                .decode()
                .rstrip("=")
            )
            mac = hmac.new(
                session.csrf_token.encode(), encoded.encode(), hashlib.sha256
            ).hexdigest()
            next_cursor = encoded + "." + mac
        return {
            "items": selected[offset : offset + limit],
            "total": len(selected),
            "next_cursor": next_cursor,
            "coverage": data["coverage"],
        }

    @app.post("/api/v1/auth/logout")
    def logout(request: Request, session: Session = Depends(mutation)):
        store.discard(request.cookies.get(SESSION_COOKIE))
        response = PlainTextResponse("Signed out")
        response.delete_cookie(SESSION_COOKIE, path="/")
        return response

    @app.post("/api/v1/pretest/github/run")
    async def run(session: Session = Depends(mutation)):
        session.snapshot = None
        data = await snapshot(session)
        fixture_rows = await fixture_checks(
            settings.github_fixtures_file, data, adapter, session.token
        )
        session.report = github_report(
            settings.reports_directory, data, session.scopes, fixture_rows
        )
        return session.report

    @app.get("/api/v1/pretest/github/report")
    def report(session: Session = Depends(authenticated)):
        if not session.report:
            raise HTTPException(404, "Run access verification first")
        path = settings.reports_directory / session.report["filename"]
        return PlainTextResponse(
            path.read_text(),
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{path.name}"'},
        )

    return app


app = create_app()
