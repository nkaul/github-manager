"""Complete loopback-only app; app.main retains the historical Phase 0 entrypoint."""

import asyncio
import base64
import hashlib
import hmac
import json
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import Depends, HTTPException, Query, Request
from pydantic import model_validator
from starlette.responses import JSONResponse

from app.auth.sessions import SessionStore
from app.config import REPO_ROOT, Settings
from app.demo import analysis, domain, explorer, taxonomy_review
from app.demo.ai import budget_summary
from app.demo.allowance import AllowanceUpdate, RequestAllowance
from app.demo.corpus import Corpus, CorpusConflict, CorpusDraft, CorpusReview
from app.demo.corpus_registry import RegistryConceptInput, RegistryConflict
from app.demo.models import (
    ConceptInput,
    ConceptPatch,
    DraftPatch,
    ExecutePlan,
    MappingInput,
    MergeInput,
    PublishInput,
    RemediateInput,
    ResetExecute,
    ResetScope,
    RuleInput,
    RunInput,
    RunPreferences,
    RunPreview,
    SelectionSummary,
    SettingsInput,
    SuggestionBatch,
)
from app.demo.service import Service
from app.demo.store import Store, identifier
from app.github.client import OAuthAppAdapter
from app.main import SESSION_COOKIE, create_app
from app.pretest.ai.settings import AISettings
from app.pretest.ai.storage import Ledger


class LocalSettings(Settings):
    demo_database: str = str(REPO_ROOT / "docs/validation/private/demo/app.sqlite3")
    demo_live_ai: bool = False
    demo_budget_operator_ids: str = ""

    @model_validator(mode="after")
    def database_scope(self):
        from pathlib import Path

        path = Path(self.demo_database)
        if not path.is_absolute():
            path = REPO_ROOT / "backend" / path
        path = path.resolve()
        if not path.is_relative_to((REPO_ROOT / "docs/validation/private").resolve()):
            raise ValueError("Demo database must remain under ignored private local storage")
        self.demo_database = str(path)
        if any(
            not value.strip().isdigit()
            for value in self.demo_budget_operator_ids.split(",")
            if value.strip()
        ):
            raise ValueError("Budget operator IDs must be comma-separated numeric GitHub IDs")
        return self


def create_local_app(
    settings=None,
    *,
    adapter=None,
    sessions=None,
    db_path=None,
    provider_factory=None,
    allowance_ledger=None,
    corpus_release=None,
):
    settings = settings or LocalSettings()
    adapter = adapter or OAuthAppAdapter(settings)
    sessions = sessions or SessionStore()
    database = Store(db_path or settings.demo_database)
    corpus = Corpus(
        REPO_ROOT,
        corpus_release or REPO_ROOT / "docs/validation/private/corpus-600-v2/release",
        database,
    )
    options = {"provider_factory": provider_factory} if provider_factory else {}
    service = Service(
        database,
        adapter,
        sessions,
        live_enabled=settings.demo_live_ai,
        ledger_factory=(lambda: allowance_ledger) if allowance_ledger else None,
        budget_operators={
            v.strip() for v in settings.demo_budget_operator_ids.split(",") if v.strip()
        },
        sync_timeout_seconds=settings.github_sync_timeout_seconds,
        **options,
    )
    app = create_app(settings, adapter, sessions)
    app.title = "GitHub Manager Local Workspace"
    app.state.database, app.state.service, app.state.sessions = database, service, sessions
    app.state.corpus = corpus
    old_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan(app):
        async with old_lifespan(app):
            task = asyncio.create_task(service.loop())
            yield
            service.stopping = True
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    app.router.lifespan_context = lifespan

    @app.exception_handler(ValueError)
    async def invalid(request, error):
        payload = {"detail": str(error)[:1000]}
        if isinstance(error, domain.TaxonomyConflict):
            payload.update(code="TAXONOMY_CONFLICT", conflicts=error.conflicts)
        if isinstance(error, CorpusConflict):
            payload.update(
                code=error.code,
                current_review=error.current_review,
                current_draft=error.current_draft,
            )
        if isinstance(error, RegistryConflict):
            payload.update(code=error.code, registry=error.registry, conflicts=error.conflicts)
        return JSONResponse(payload, status_code=409)

    def auth(request: Request):
        session = sessions.get(request.cookies.get(SESSION_COOKIE))
        if session is None:
            raise HTTPException(401, "Sign in to GitHub")
        return session

    def mutation(request: Request, session=Depends(auth)):
        if request.headers.get("origin") != settings.app_origin or not hmac.compare_digest(
            request.headers.get("x-csrf-token", ""), session.csrf_token
        ):
            raise HTTPException(403, "Invalid Origin or CSRF token")
        return session

    def can_manage_allowance(session):
        return str(session.user["id"]) in {
            value.strip() for value in settings.demo_budget_operator_ids.split(",") if value.strip()
        }

    def allowance_operator(session=Depends(mutation)):
        if not can_manage_allowance(session):
            raise HTTPException(403, "Only configured local budget operators can change allowances")
        return session

    def allowance():
        ai_settings = AISettings()
        ledger = allowance_ledger or Ledger(
            ai_settings.ai_pretest_state_directory, ai_settings.ai_pretest_budget_usd
        )
        return RequestAllowance(ledger)

    def ws(collection: Literal["github", "samples"] = "github", session=Depends(auth)):
        return str(session.user["id"]) + ":" + collection

    def mut_ws(collection: Literal["github", "samples"] = "github", session=Depends(mutation)):
        return str(session.user["id"]) + ":" + collection

    def corpus_ws(collection: Literal["ground-truth"] = "ground-truth", session=Depends(auth)):
        return str(session.user["id"]) + ":" + collection

    @app.get("/api/v1/corpus")
    def corpus_summary(workspace=Depends(corpus_ws)):
        return corpus.summary(workspace)

    @app.get("/api/v1/corpus/registry")
    def corpus_registry(workspace=Depends(corpus_ws)):
        return corpus.registry_view(workspace)

    @app.post("/api/v1/corpus/registry/concepts")
    def corpus_registry_create(
        value: RegistryConceptInput, workspace=Depends(corpus_ws), session=Depends(mutation)
    ):
        return corpus.create_registry_concept(workspace, value.model_dump(), session.user["id"])

    @app.post("/api/v1/corpus/open")
    def corpus_open(workspace=Depends(corpus_ws), session=Depends(mutation)):
        return corpus.open(workspace)

    @app.get("/api/v1/corpus/repos")
    def corpus_repos(
        q: str = Query("", max_length=500),
        domain: str = "",
        assigned_domain: str = "",
        concept: str = "",
        concept_ids: list[str] = Query(default=[], max_length=100),
        label_basis: Literal["proposals", "reviewed"] = "proposals",
        annotation_scope: Literal["all", "pilot", "initial_queue"] = "all",
        status: str = "",
        offset: int = Query(0, ge=0),
        limit: int = Query(25, ge=1, le=100),
        workspace=Depends(corpus_ws),
    ):
        return corpus.search(
            workspace,
            q,
            domain,
            concept,
            status,
            offset,
            limit,
            assigned_domain,
            concept_ids,
            label_basis,
            annotation_scope,
        )

    @app.get("/api/v1/corpus/repos/{repository_id}")
    def corpus_detail(repository_id: int, workspace=Depends(corpus_ws)):
        try:
            return corpus.detail(workspace, repository_id)
        except KeyError:
            raise HTTPException(404, "Repository not in this corpus")

    @app.get("/api/v1/corpus/repos/{repository_id}/source")
    def corpus_source(
        repository_id: int, path: str = Query(..., max_length=500), workspace=Depends(corpus_ws)
    ):
        try:
            return corpus.source(repository_id, path)
        except KeyError:
            raise HTTPException(404, "Source not in this corpus dossier")

    @app.get("/api/v1/corpus/repos/{repository_id}/neighbors")
    def corpus_neighbors(
        repository_id: int,
        q: str = Query("", max_length=500),
        domain: str = "",
        assigned_domain: str = "",
        concept: str = "",
        concept_ids: list[str] = Query(default=[], max_length=100),
        label_basis: Literal["proposals", "reviewed"] = "proposals",
        annotation_scope: Literal["all", "pilot", "initial_queue"] = "all",
        status: str = "",
        workspace=Depends(corpus_ws),
    ):
        try:
            return corpus.neighbors(
                workspace,
                repository_id,
                q=q,
                domain=domain,
                assigned_domain=assigned_domain,
                concept=concept,
                concept_ids=concept_ids,
                label_basis=label_basis,
                annotation_scope=annotation_scope,
                status=status,
            )
        except KeyError:
            raise HTTPException(404, "Repository not in this corpus")

    @app.put("/api/v1/corpus/repos/{repository_id}/review")
    def corpus_review(
        repository_id: int,
        value: CorpusReview,
        workspace=Depends(corpus_ws),
        session=Depends(mutation),
    ):
        try:
            return corpus.save_review(
                workspace, repository_id, value.model_dump(), session.user["id"]
            )
        except KeyError:
            raise HTTPException(404, "Repository not in this corpus")

    @app.get("/api/v1/corpus/repos/{repository_id}/draft")
    def corpus_draft(repository_id: int, workspace=Depends(corpus_ws)):
        try:
            return corpus.draft(workspace, repository_id)
        except KeyError:
            raise HTTPException(404, "Repository not in this corpus")

    @app.put("/api/v1/corpus/repos/{repository_id}/draft")
    def corpus_save_draft(
        repository_id: int,
        value: CorpusDraft,
        workspace=Depends(corpus_ws),
        session=Depends(mutation),
    ):
        try:
            return corpus.save_draft(
                workspace, repository_id, value.model_dump(), session.user["id"]
            )
        except KeyError:
            raise HTTPException(404, "Repository not in this corpus")

    @app.get("/api/v1/corpus/reviews/export")
    def corpus_export(workspace=Depends(corpus_ws)):
        records = corpus.records(workspace)
        return JSONResponse(
            {
                "release_id": corpus.manifest["release_id"],
                "manifest_sha256": corpus._manifest_hash,
                "reviews": list(records.values()),
                "reference_registry": corpus.export_registry(workspace),
                "unlisted_labels": "UNKNOWN_NOT_NEGATIVE",
            },
            headers={
                "Content-Disposition": 'attachment; filename="public-ground-truth-reviews.json"'
            },
        )

    # Keep Phase 0's route in app.main. This local entrypoint supplies the product explorer.
    app.router.routes = [
        r for r in app.router.routes if getattr(r, "path", None) not in {"/api/v1/repos", "/health"}
    ]

    @app.get("/health")
    def health():
        return {"status": "ok", "phase": "0.9", "storage": "local"}

    @app.get("/api/v1/workspace")
    def workspace(workspace=Depends(ws), session=Depends(auth)):
        state = database.read(workspace)
        org = state["organization"]
        if org["control"]["resetting"]:
            org = {**org, "concepts": {}, "edges": {}, "suggestions": {}, "drafts": {}, "rules": {}}
        return {
            "collection": workspace.split(":")[1],
            "repository_names": {
                k: r["name"] for k, r in state["core"]["repos"].items() if not r.get("unavailable")
            },
            "automation": analysis.automation(state),
            "concept_counts": explorer.concepts(
                state, explorer.repositories(state, workspace, session.user["id"])
            ),
            "organization": org,
            "coverage": domain.coverage({**state, "organization": org}),
            "summary": explorer.summary(
                explorer.repositories(state, workspace, session.user["id"])
            ),
            "source_coverage": state["core"]["coverage"],
            "activity_coverage": state["core"]["activity_coverage"],
            "synced_at": state["core"]["synced_at"],
            "live_ai_enabled": settings.demo_live_ai,
            "preferences": state.get(
                "preferences",
                {
                    "taxonomy_count": 10,
                    "classification_count": 10,
                    "budget_mode": "FIXED",
                    "budget_usd": 0.25,
                },
            ),
            "budget": budget_summary(allowance_ledger),
            "can_manage_allowance": can_manage_allowance(session),
        }

    @app.post("/api/v1/ai/allowance")
    def update_allowance(value: AllowanceUpdate, session=Depends(allowance_operator)):
        manager = allowance()
        manager.update(value, actor="github:" + str(session.user["id"]))
        return budget_summary(manager.ledger)

    @app.get("/api/v1/ai/allowance/history")
    def allowance_history(session=Depends(auth)):
        if not can_manage_allowance(session):
            raise HTTPException(
                403, "Only configured local budget operators can view allowance audit"
            )
        return allowance().history()

    @app.post("/api/v1/samples/load")
    def samples(workspace=Depends(mut_ws)):
        service.load_samples(workspace)
        return {"status": "LOADED"}

    @app.post("/api/v1/sync", status_code=202)
    def sync(workspace=Depends(mut_ws)):
        return service.queue(workspace, "SYNC")

    @app.get("/api/v1/repos")
    def repos(
        request: Request,
        view: Literal[
            "my",
            "favorites",
            "latest",
            "uncategorized",
            "all",
            "no_labels",
            "needs_review",
            "no_match",
            "failed",
            "stale",
        ] = "my",
        q: str = Query("", max_length=100),
        language: str = Query("", max_length=100),
        visibility: Literal["all", "public", "private"] = "all",
        concept: str = Query("", max_length=100),
        days: int = Query(14, ge=1, le=90),
        limit: int = Query(20, ge=1, le=100),
        cursor: str = Query("", max_length=2048),
        workspace=Depends(ws),
        session=Depends(auth),
    ):
        state = database.read(workspace)
        filters = dict(
            view=view, q=q, language=language, visibility=visibility, concept=concept, days=days
        )
        items = explorer.repositories(state, workspace, session.user["id"], filters)
        facets = explorer.languages(
            explorer.repositories(state, workspace, session.user["id"], {**filters, "language": ""})
        )
        scope = json.dumps(
            [
                workspace,
                view,
                q,
                language,
                visibility,
                concept,
                days,
                state["organization"]["control"]["version"],
            ]
        )
        offset = 0
        if cursor:
            try:
                raw, mac = cursor.split(".")
                expected = hmac.new(
                    session.csrf_token.encode(), raw.encode(), hashlib.sha256
                ).hexdigest()
                value = json.loads(base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4)))
                if (
                    not hmac.compare_digest(mac, expected)
                    or value["scope"] != scope
                    or type(value["offset"]) is not int
                    or value["offset"] < 0
                ):
                    raise ValueError
                offset = value["offset"]
            except Exception:
                raise HTTPException(400, "Invalid or stale page cursor; refresh list") from None
        next_cursor = None
        if offset + limit < len(items):
            raw = (
                base64.urlsafe_b64encode(
                    json.dumps({"scope": scope, "offset": offset + limit}).encode()
                )
                .decode()
                .rstrip("=")
            )
            next_cursor = (
                raw
                + "."
                + hmac.new(session.csrf_token.encode(), raw.encode(), hashlib.sha256).hexdigest()
            )
        return {
            "items": items[offset : offset + limit],
            "summary": explorer.summary(items),
            "languages": facets,
            "concept_counts": explorer.concepts(
                state,
                explorer.repositories(
                    state, workspace, session.user["id"], {**filters, "concept": ""}
                ),
            ),
            "total": len(items),
            "next_cursor": next_cursor,
            "coverage": state["core"]["coverage"],
        }

    @app.post("/api/v1/repos/summary")
    def selection_summary(
        value: SelectionSummary, workspace=Depends(mut_ws), session=Depends(auth)
    ):
        items = {
            r["key"]: r
            for r in explorer.repositories(database.read(workspace), workspace, session.user["id"])
        }
        if any(key not in items for key in value.repo_keys):
            raise ValueError(
                "Selection changed or contains inaccessible repositories; refresh the view"
            )
        return explorer.summary([items[key] for key in dict.fromkeys(value.repo_keys)])

    @app.get("/api/v1/repos/detail")
    def detail(key: str = Query(max_length=200), workspace=Depends(ws)):
        state = database.read(workspace)
        repo = state["core"]["repos"].get(key)
        if not repo or repo.get("unavailable"):
            raise HTTPException(404, "Accessible repository not found")
        resetting = state["organization"]["control"]["resetting"]
        return {
            "repo": {**repo, "analysis": analysis.projection(state, key)},
            "profile": None
            if repo["private"] or resetting
            else state["intelligence"]["profiles"].get(key),
            "edges": {} if resetting else state["organization"]["edges"].get(key, {}),
            "rejections": []
            if resetting
            else list(state["organization"]["rejections"].get(key, {})),
        }

    @app.post("/api/v1/repos/inclusion")
    def inclusion(
        key: str = Query(max_length=200), include: bool = True, workspace=Depends(mut_ws)
    ):
        def action(s):
            domain.writable(s)
            r = s["core"]["repos"].get(key)
            if not r or r.get("unavailable"):
                raise ValueError("Accessible candidate not found")
            r["included"] = include

        database.mutate(workspace, action)
        return {"included": include}

    @app.post("/api/v1/taxonomy/concepts")
    def create(value: ConceptInput, workspace=Depends(mut_ws)):
        return database.mutate(workspace, lambda s: domain.create_concept(s, value.model_dump()))

    @app.patch("/api/v1/taxonomy/concepts/{key}")
    def edit(key: str, value: ConceptPatch, workspace=Depends(mut_ws)):
        return database.mutate(
            workspace, lambda s: domain.edit_concept(s, key, value.model_dump(exclude_unset=True))
        )

    @app.delete("/api/v1/taxonomy/concepts/{key}")
    def archive(key: str, workspace=Depends(mut_ws)):
        return database.mutate(workspace, lambda s: domain.remove_concept(s, key))

    @app.post("/api/v1/taxonomy/concepts/merge")
    def merge(value: MergeInput, workspace=Depends(mut_ws)):
        return database.mutate(
            workspace, lambda s: domain.merge_concepts(s, value.source, value.target)
        )

    @app.post("/api/v1/repos/associations")
    def assign(value: MappingInput, workspace=Depends(mut_ws)):
        database.mutate(
            workspace,
            lambda s: domain.mapping(s, value.repo_keys, value.concept_ids, value.operation),
        )
        return {"status": "SAVED"}

    @app.post("/api/v1/organizer/reorganize", status_code=202)
    def run(value: RunInput, workspace=Depends(mut_ws)):
        return service.queue(workspace, value.mode, value.repo_keys, value.ai_mode)

    @app.post("/api/v1/organizer/preview")
    def preview_run(value: RunPreview, workspace=Depends(mut_ws)):
        return service.preview(workspace, value)

    @app.post("/api/v1/organizer/execute", status_code=202)
    def execute_run(value: ExecutePlan, workspace=Depends(mut_ws), session=Depends(auth)):
        plan = database.run_plan(workspace, value.plan_id)
        if (
            plan["input"]["budget_mode"] == "ADAPTIVE"
            and plan["generations"]
            and not can_manage_allowance(session)
        ):
            raise HTTPException(
                403, "Only configured budget operators can authorize adaptive live runs"
            )
        return service.start_plan(
            workspace,
            value.plan_id,
            actor="github:" + str(session.user["id"]),
            operator=can_manage_allowance(session),
        )

    @app.patch("/api/v1/organizer/preferences")
    def run_preferences(value: RunPreferences, workspace=Depends(mut_ws), session=Depends(auth)):
        if value.budget_mode == "ADAPTIVE" and not can_manage_allowance(session):
            raise HTTPException(403, "Only configured budget operators can enable adaptive policy")
        database.mutate(workspace, lambda s: s.update(preferences=value.model_dump()))
        return value.model_dump()

    @app.get("/api/v1/organizer/runs/{rid}")
    def run_detail(rid: str, workspace=Depends(ws)):
        result = database.read(workspace)["organization"]["runs"].get(rid)
        if not result:
            raise HTTPException(404, "Run not found")
        return result

    @app.patch("/api/v1/taxonomy/drafts/{key}")
    def edit_draft(key: str, value: DraftPatch, workspace=Depends(mut_ws)):
        def action(s):
            domain.writable(s)
            draft = s["organization"]["drafts"].get(key)
            if not draft or draft["status"] != "DRAFT":
                raise ValueError("Editable draft not found")
            draft["edited_proposals"] = [p.model_dump() for p in value.proposals]
            return draft

        return database.mutate(workspace, action)

    @app.delete("/api/v1/taxonomy/drafts/{key}")
    def reject_draft(key: str, workspace=Depends(mut_ws)):
        def action(s):
            domain.writable(s)
            if key not in s["organization"]["drafts"]:
                raise ValueError("Draft not found")
            s["organization"]["drafts"][key]["status"] = "REJECTED"

        database.mutate(workspace, action)
        return {"status": "REJECTED"}

    @app.post("/api/v1/taxonomy/drafts/check")
    def check_draft(value: PublishInput, workspace=Depends(mut_ws)):
        state = database.read(workspace)
        taxonomy_review.editable(state, value.draft_id, value.expected_revision)
        return taxonomy_review.check(state, [p.model_dump() for p in value.proposals])

    @app.post("/api/v1/taxonomy/drafts/remediate")
    def remediate_draft(value: RemediateInput, workspace=Depends(mut_ws)):
        state = database.read(workspace)
        taxonomy_review.editable(state, value.draft_id, value.expected_revision)
        return taxonomy_review.remediate(
            state, [p.model_dump() for p in value.proposals], value.action, value.conflict_id
        )

    @app.post("/api/v1/taxonomy/drafts/publish")
    def publish(value: PublishInput, workspace=Depends(mut_ws)):
        return database.mutate(
            workspace,
            lambda s: taxonomy_review.publish(
                s,
                value.draft_id,
                value.expected_revision,
                [p.model_dump() for p in value.proposals],
            ),
        )

    def validate_suggestion(s, sid):
        domain.writable(s)
        item = s["organization"]["suggestions"].get(sid)
        if not item or item["status"] != "PROPOSED":
            raise ValueError("Pending suggestion not found")
        domain.check_fence(s, item["fence"])
        repo = s["core"]["repos"].get(item["repo_key"])
        if not repo or repo.get("unavailable"):
            raise ValueError("Repository access changed")
        domain.active(s, item["concept_id"])
        if (
            s["intelligence"]["profiles"].get(item["repo_key"], {}).get("hash")
            != item["profile_hash"]
        ):
            raise ValueError("Evidence changed; reconcile or explicitly re-analyze")
        if repo.get("decision_version", 0) != item.get("decision_version", 0):
            raise ValueError("Manual decisions changed; reconcile before accepting")
        return item

    @app.post("/api/v1/organizer/suggestions/batch")
    def suggestions_batch(value: SuggestionBatch, workspace=Depends(mut_ws)):
        def action(s):
            domain.writable(s)
            valid, outcomes = [], []
            for sid in dict.fromkeys(value.ids):
                try:
                    valid.append(validate_suggestion(s, sid))
                except ValueError as exc:
                    outcomes.append({"id": sid, "status": "SKIPPED", "reason": str(exc)})
            # Validate against one snapshot so accepting the first item doesn't stale its siblings.
            for item in valid:
                domain.mapping(
                    s,
                    [item["repo_key"]],
                    [item["concept_id"]],
                    "ADD" if value.decision == "accept" else "REMOVE",
                )
                outcomes.append({"id": item["id"], "status": item["status"]})
            return {"outcomes": outcomes}

        return database.mutate(workspace, action)

    @app.post("/api/v1/organizer/suggestions/{sid}/{decision}")
    def suggestion(sid: str, decision: Literal["accept", "reject"], workspace=Depends(mut_ws)):
        def action(s):
            item = validate_suggestion(s, sid)
            domain.mapping(
                s,
                [item["repo_key"]],
                [item["concept_id"]],
                "ADD" if decision == "accept" else "REMOVE",
            )
            return item

        return database.mutate(workspace, action)

    @app.post("/api/v1/content/rules/preview")
    def preview_rule(value: RuleInput, workspace=Depends(mut_ws)):
        state = database.read(workspace)
        concept = domain.active(state, value.concept_id)
        if concept["kind"] == "DOMAIN":
            raise ValueError("Rules assign projects/topics/tags, not domains")
        return {
            "matches": [
                r["key"]
                for r in state["core"]["repos"].values()
                if not r.get("unavailable") and domain.rule_matches(value.model_dump(), r)
            ]
        }

    @app.post("/api/v1/content/rules")
    def save_rule(value: RuleInput, workspace=Depends(mut_ws)):
        def action(s):
            domain.writable(s)
            if domain.active(s, value.concept_id)["kind"] == "DOMAIN":
                raise ValueError("Rule target cannot be a domain")
            key = identifier()
            s["organization"]["rules"][key] = {"id": key, **value.model_dump()}
            domain.changed(s, key, "RULE", 2)
            return s["organization"]["rules"][key]

        return database.mutate(workspace, action)

    @app.delete("/api/v1/content/rules/{key}")
    def delete_rule(key: str, workspace=Depends(mut_ws)):
        def action(s):
            domain.writable(s)
            if key not in s["organization"]["rules"]:
                raise ValueError("Rule not found")
            s["organization"]["rules"].pop(key)
            domain.changed(s, key, "RULE", 2)

        database.mutate(workspace, action)
        return {"status": "REMOVED"}

    @app.patch("/api/v1/organizer/settings")
    def configure(value: SettingsInput, workspace=Depends(mut_ws)):
        def action(s):
            domain.writable(s)
            patch = value.model_dump(exclude_unset=True)
            if any(v is None for v in patch.values()):
                raise ValueError("Automatic settings cannot be null")
            control = s["organization"]["control"]
            if patch.get("quiet_seconds", control["quiet_seconds"]) >= patch.get(
                "auto_window_seconds", control.get("auto_window_seconds", 900)
            ):
                raise ValueError("Quiet period must be shorter than the change window")
            control.update(patch)

        database.mutate(workspace, action)
        return value

    @app.post("/api/v1/organizer/reset/preview")
    def reset_preview(value: ResetScope, workspace=Depends(mut_ws)):
        state = database.read(workspace)
        domain.writable(state)
        org = state["organization"]
        if value.restart == "RECLASSIFY_EXISTING" and {"PROJECT", "TOPIC", "TAG"} <= set(
            value.kinds
        ):
            raise ValueError("Reclassification needs retained taxonomy; choose rediscovery")
        selected = {
            cid
            for cid, c in org["concepts"].items()
            if c["kind"] in value.kinds and not c.get("protected")
        }
        counts = {
            "concepts": len(selected),
            "user_edges": 0,
            "automatic_edges": 0,
            "suggestions": sum(
                s["status"] == "PROPOSED" and (value.suggestions or s["concept_id"] in selected)
                for s in org["suggestions"].values()
            ),
            "drafts": len(org["drafts"]) if value.drafts else 0,
            "history": len(org["runs"]) if value.history else 0,
            "profiles": len(state["intelligence"]["profiles"]) if value.cache else 0,
            "rules": sum(value.rules or r["concept_id"] in selected for r in org["rules"].values()),
            "project_moves": sum(
                c["active"] and c.get("domain") in selected and c["id"] not in selected
                for c in org["concepts"].values()
            ),
            "preserved_repos": len(state["core"]["repos"]),
            "protected_rejections_preserved": sum(len(x) for x in org["rejections"].values()),
        }
        for edges in org["edges"].values():
            for cid, e in edges.items():
                if cid in selected or value.associations and e["source"] != "USER":
                    counts["user_edges" if e["source"] == "USER" else "automatic_edges"] += 1
        plan = {"scope": value.model_dump(), "version": org["control"]["version"], "counts": counts}
        key = database.preview(workspace, plan)
        return {**plan, "plan_id": key, "expires_in": 300, "confirmation_required": "DELETE"}

    @app.post("/api/v1/organizer/reset/execute", status_code=202)
    def execute(value: ResetExecute, workspace=Depends(mut_ws)):
        def action(s, plan):
            org = s["organization"]
            control = org["control"]
            old = control["active_run"]
            if old and old in org["runs"]:
                org["runs"][old].update(
                    status="CANCELLED_STALE", message="Fenced by confirmed reset"
                )
            control["generation"] += 1
            control["ai_epoch"] += int(plan["scope"]["associations"])
            control["cache_epoch"] += int(plan["scope"]["cache"])
            if set(plan["scope"]["kinds"]) == {"DOMAIN", "PROJECT", "TOPIC", "TAG"}:
                control["taxonomy_epoch"] += 1
            rid = identifier()
            run = {
                "id": rid,
                "kind": "RESET",
                "status": "QUEUED",
                "created_at": domain.now(),
                "total": 1,
                "processed": 0,
                "failed": 0,
                "scope": plan["scope"],
                "outcomes": {},
            }
            org["runs"][rid] = run
            control.update(resetting=True, active_run=rid)
            return run

        return database.execute_preview(workspace, value.plan_id, value.confirmation, action)

    return app


app = create_local_app()
