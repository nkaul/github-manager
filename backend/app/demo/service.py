import asyncio
import base64
import time

from app.demo import analysis, cohorts, domain, pricing
from app.demo.ai import open_provider
from app.demo.allowance import RequestAllowance
from app.demo.evidence import build_profile, model_allowed, sample_records
from app.demo.run_budget import RunBudgets
from app.demo.store import identifier
from app.pretest.ai.chains import CLASSIFY_SYSTEM, TAXONOMY_SYSTEM
from app.pretest.ai.evidence import Retriever, compact, tokens
from app.pretest.ai.schemas import (
    Classification,
    TaxonomyDraft,
    validate_classification,
    validate_taxonomy,
)
from app.pretest.ai.settings import AISettings
from app.pretest.ai.storage import Ledger, digest

TERMINAL = {"COMPLETED", "PARTIAL_FAILED", "FAILED", "CANCELLED_STALE", "INTERRUPTED"}


class Service:
    def __init__(
        self,
        store,
        adapter,
        sessions,
        *,
        provider_factory=open_provider,
        live_enabled=False,
        ledger_factory=None,
        budget_operators=(),
    ):
        self.store, self.adapter, self.sessions = store, adapter, sessions
        self.provider_factory = provider_factory
        self.live_enabled = live_enabled
        self.stopping = False
        self.ledger_factory = ledger_factory or self.default_ledger
        self.budget_operators = set(budget_operators)

    @staticmethod
    def default_ledger():
        settings = AISettings()
        return Ledger(settings.ai_pretest_state_directory, settings.ai_pretest_budget_usd)

    def preview(self, workspace, value):
        if value.ai_mode == "LIVE" and not self.live_enabled:
            raise ValueError("Live AI is disabled in backend configuration")
        try:
            ledger = self.ledger_factory()
        except ValueError:
            ledger = None
        return cohorts.preview(self.store, workspace, value, AISettings(), ledger)

    def start_plan(self, workspace, plan_id, *, actor, operator=False, reason="MANUAL"):
        plan = self.store.run_plan(workspace, plan_id)
        state = self.store.read(workspace)
        if plan["consumed"]:
            if plan_id in state["organization"]["runs"]:
                return state["organization"]["runs"][plan_id]
            raise ValueError("Run plan has already been used")
        if plan["pricing_version"] != pricing.VERSION:
            raise ValueError("Pricing snapshot changed; preview again")
        if not plan["can_start"]:
            raise ValueError(plan["blocked_reason"])
        if state["organization"]["control"]["version"] != plan["version"]:
            raise ValueError("Stale run preview; preview again")
        adaptive = plan["input"]["budget_mode"] == "ADAPTIVE" and plan["generations"] > 0
        ledger = self.ledger_factory() if plan["budget_revision"] is not None else None
        if ledger and RequestAllowance(ledger).policy()["revision"] != plan["budget_revision"]:
            raise ValueError("Budget policy changed; preview again")
        if adaptive and not operator:
            raise ValueError("An authorized budget operator must start adaptive live inference")
        budgets = RunBudgets(ledger) if adaptive else None
        if budgets:
            budgets.reserve(
                plan_id,
                workspace,
                plan["upper_micros"],
                plan["generations"],
                actor,
                plan["budget_revision"],
                RunBudgets.store_id(self.store),
            )
        try:
            result = self.queue(
                workspace,
                plan["input"]["mode"],
                plan["keys"],
                plan["input"]["ai_mode"],
                reason,
                plan_id=plan_id,
                adaptive=adaptive,
                preview=plan,
            )
        except Exception:
            # A duplicate concurrent start must not release the already queued job's hold.
            with self.store.connect() as db:
                queued = db.execute("SELECT 1 FROM jobs WHERE id=?", (plan_id,)).fetchone()
            if budgets and not queued:
                budgets.finish(plan_id)
            raise
        if budgets:
            budgets.queued(plan_id)
        return result

    def provider_for(self, job, authorized):
        provider = self.provider_factory(job["payload"]["ai_mode"], authorized)
        if job["payload"].get("adaptive") and hasattr(provider, "bind_budget"):
            provider.bind_budget(job["id"])
        return provider

    def session_for(self, workspace):
        owner = int(workspace.split(":")[0])
        with self.sessions.lock:
            self.sessions._prune()
            return next((s for s in self.sessions.sessions.values() if s.user["id"] == owner), None)

    def load_samples(self, workspace):
        if not workspace.endswith(":samples"):
            raise ValueError("Load samples only into the sample collection")
        repos, profiles = sample_records()

        def action(state):
            domain.writable(state)
            for key, repo in repos.items():
                old = state["core"]["repos"].get(key, {})
                if not old:
                    analysis.new_repository(state, key)
                state["core"]["repos"][key] = {
                    **repo,
                    "decision_version": old.get("decision_version", 0),
                }
            state["intelligence"]["profiles"].update(profiles)
            state["core"]["coverage"] = [
                {
                    "source": "PUBLIC_AND_SYNTHETIC",
                    "status": "SAMPLE",
                    "note": "Approved public + synthetic samples; not your GitHub relationships",
                }
            ]
            state["core"]["synced_at"] = domain.now()
            state["core"]["activity_coverage"] = [
                {
                    "source": "SYNTHETIC_FIXTURE",
                    "status": "FIXTURE",
                    "note": "Synthetic Orion activity; not observed GitHub contributions",
                }
            ]
            owner = int(workspace.split(":")[0])
            for key, repo in state["core"]["repos"].items():
                if repo.get("synthetic"):
                    repo["activities"] = [
                        {"at": domain.now(), "actor_id": owner, "kind": "SYNTHETIC_FIXTURE"}
                    ]

        self.store.mutate(workspace, action)

    def queue(
        self,
        workspace,
        mode,
        repo_keys=None,
        ai_mode="CACHE",
        reason="MANUAL",
        *,
        plan_id=None,
        adaptive=False,
        preview=None,
    ):
        if ai_mode == "LIVE" and not self.live_enabled:
            raise ValueError("Live AI is disabled in backend configuration")
        state = self.store.read(workspace)
        rules_only = ai_mode == "RULES" and mode in {"INCREMENTAL", "FULL_CLASSIFICATION"}
        keys = (
            []
            if mode in {"SYNC", "RESET"}
            else repo_keys
            or [
                k
                for k, r in state["core"]["repos"].items()
                if not r.get("unavailable") and (rules_only or model_allowed(r))
            ]
        )
        if mode not in {"SYNC", "RESET"} and not keys:
            raise ValueError("Select accessible public/synthetic repositories first")
        if len(keys) > 30:
            raise ValueError("Select at most 30 repositories per local run")
        if mode not in {"SYNC", "RESET"}:
            for key in keys:
                if (
                    key not in state["core"]["repos"]
                    or state["core"]["repos"][key].get("unavailable")
                    or (not rules_only and not model_allowed(state["core"]["repos"][key]))
                ):
                    raise ValueError("Private or unverified repository is not approved for AI")
        if mode in {"INCREMENTAL", "FULL_CLASSIFICATION"} and not any(
            c["active"] and c["kind"] != "DOMAIN"
            for c in state["organization"]["concepts"].values()
        ):
            raise ValueError("Publish or create taxonomy before classifying")
        rid = plan_id or identifier()
        payload = {
            "repo_keys": keys,
            "ai_mode": ai_mode,
            "fence": domain.fence(state),
            "reason": reason,
            "adaptive": adaptive,
            "planned": bool(plan_id),
            "reanalyze": bool(preview and preview["input"].get("reanalyze")),
            "reanalysis_reason": preview["input"].get("reanalysis_reason", "") if preview else "",
        }
        run = {
            "id": rid,
            "kind": mode,
            "status": "QUEUED",
            "created_at": domain.now(),
            "total": len(keys),
            "processed": 0,
            "failed": 0,
            "stale": 0,
            "outcomes": {},
            "reason": reason,
            "ai_mode": ai_mode,
            "reanalyze": payload["reanalyze"],
            "reanalysis_reason": payload["reanalysis_reason"],
            "revision": state["organization"]["control"]["revision"],
        }
        if preview:
            run["preview"] = {
                k: preview[k]
                for k in ("requested", "chosen", "upper_usd", "pricing_version", "http_requests")
            }
            run["budget_mode"] = preview["input"]["budget_mode"]
        return self.store.enqueue(workspace, mode, payload, run, plan_id=plan_id)

    def update_run(self, workspace, rid, **values):
        def action(state):
            org = state["organization"]
            run = org["runs"].get(rid)
            if run:
                run.update(values)
                if values.get("status") in TERMINAL and org["control"]["active_run"] == rid:
                    org["control"]["active_run"] = None

        self.store.mutate(workspace, action)

    async def loop(self):
        self.store.recover()
        try:
            RunBudgets(self.ledger_factory()).reconcile(self.store)
        except ValueError:
            pass
        last_reconcile = 0.0
        while not self.stopping:
            if time.monotonic() - last_reconcile > 10:
                try:
                    RunBudgets(self.ledger_factory()).reconcile(self.store)
                except ValueError:
                    pass
                last_reconcile = time.monotonic()
            with self.sessions.lock:
                self.sessions._prune()
                owners = {str(s.user["id"]) for s in self.sessions.sessions.values()}
            workspaces = {o + ":" + c for o in owners for c in ("github", "samples")}
            self.schedule(workspaces)
            job = self.store.claim(workspaces)
            if job:
                await self.perform(job)
            else:
                await asyncio.sleep(0.5)

    def schedule(self, workspaces):
        for workspace in workspaces:
            state = self.store.read(workspace)
            org = state["organization"]
            c = org["control"]
            trigger = analysis.automation(state)
            if not c["auto_enabled"] or c["active_run"] or c["resetting"] or not trigger["ready"]:
                continue
            if trigger["ready"]:
                try:
                    from app.demo.models import RepoScope, RunPreview

                    preferences = state.get(
                        "preferences",
                        {"classification_count": 10, "budget_mode": "FIXED", "budget_usd": 0.25},
                    )
                    value = RunPreview(
                        mode="INCREMENTAL",
                        ai_mode="LIVE" if self.live_enabled else "CACHE",
                        count=preferences["classification_count"],
                        budget_mode=preferences["budget_mode"],
                        budget_usd=preferences["budget_usd"],
                        scope=RepoScope(view="all" if workspace.endswith(":samples") else "my"),
                    )
                    plan = self.preview(workspace, value)
                    self.start_plan(
                        workspace,
                        plan["plan_id"],
                        actor="automatic:" + workspace.split(":")[0],
                        operator=workspace.split(":")[0] in self.budget_operators,
                        reason="AUTO",
                    )
                    self.store.mutate(
                        workspace,
                        lambda s: s["organization"]["control"].update(
                            last_auto=time.time(), auto_processed_sequence=trigger["sequence"]
                        ),
                    )
                except ValueError:
                    continue

    async def perform(self, job):
        workspace, rid = job["workspace"], job["id"]
        current = self.store.read(workspace)["organization"]
        if (
            current["control"]["active_run"] != rid
            or current["runs"].get(rid, {}).get("status") in TERMINAL
        ):
            self.store.finish(job, current["runs"].get(rid, {}).get("status", "CANCELLED_STALE"))
            if job["payload"].get("adaptive"):
                RunBudgets(self.ledger_factory()).finish(rid)
            return
        self.update_run(workspace, rid, status="RUNNING", message="Preparing inputs")
        try:
            if not self.session_for(workspace):
                raise ValueError("Reauthenticate before continuing")
            if job["kind"] == "SYNC":
                count = await self.sync(workspace)
                self.update_run(workspace, rid, total=count, processed=count)
            elif job["kind"] == "RESET":
                self.cleanup(workspace, rid, job["payload"])
            else:
                if job["payload"].get("adaptive"):
                    RunBudgets(self.ledger_factory()).activate(rid, workspace)
                await self.organize(job)
            state = self.store.read(workspace)
            run = state["organization"]["runs"].get(rid, {})
            if run.get("status") not in TERMINAL:
                self.update_run(
                    workspace,
                    rid,
                    status="PARTIAL_FAILED"
                    if run.get("failed") or run.get("stale")
                    else "COMPLETED",
                    finished_at=domain.now(),
                    message=(
                        f"{run.get('processed', 0)}/{run.get('total', 0)} repositories processed "
                        "in this cohort. Review proposed additions before accepting. "
                        "Remaining inventory was not included."
                    )
                    if job["kind"] in {"INCREMENTAL", "FULL_CLASSIFICATION"}
                    else run.get("message", "Finished"),
                )
            self.store.finish(
                job,
                self.store.read(workspace)["organization"]["runs"]
                .get(rid, {})
                .get("status", "COMPLETED"),
            )
        except Exception as exc:
            # Do not persist remote exception messages or request content.
            status = (
                "CANCELLED_STALE"
                if isinstance(exc, ValueError) and "Stale" in str(exc)
                else "FAILED"
            )
            message = (
                str(exc)[:200]
                if isinstance(exc, ValueError)
                else "Operation failed; check connection and retry explicitly"
            )
            self.update_run(
                workspace, rid, status=status, message=message, finished_at=domain.now()
            )
            self.store.finish(job, status)
        finally:
            self.store.mutate(workspace, lambda s: analysis.interrupt(s, rid))
            if job["payload"].get("adaptive"):
                budgets = RunBudgets(self.ledger_factory())
                budgets.finish(rid)
                if rid in self.store.read(workspace)["organization"]["runs"]:
                    self.update_run(workspace, rid, budget_outcome=budgets.outcome(rid))

    async def sync(self, workspace):
        session = self.session_for(workspace)
        if workspace.endswith(":samples"):
            self.load_samples(workspace)
            return len(self.store.read(workspace)["core"]["repos"])
        snapshot = await self.adapter.inventory(session.token)
        if snapshot["identity"]["id"] != session.user["id"]:
            raise ValueError("GitHub identity changed; sign in again")
        activity, activity_coverage = (
            {},
            [
                {
                    "source": "GITHUB_CONTRIBUTIONS",
                    "status": "UNAVAILABLE",
                    "note": "Activity unavailable; repository pushes are not a substitute",
                }
            ],
        )
        try:
            from app.demo.activity import fetch_activity

            activity, activity_coverage = await fetch_activity(
                self.adapter, session.token, session.user["id"]
            )
        except Exception:
            pass
        if not self.session_for(workspace):
            raise ValueError("Sign-in ended; sync cancelled")

        def commit(state):
            domain.writable(state)
            observed = {r["id"] for r in snapshot["repos"]}
            for key, old in state["core"]["repos"].items():
                if old.get("private") and old.get("id") not in observed:
                    old.update(unavailable=True, policy_verified=False)
                    state["intelligence"]["profiles"].pop(key, None)
            for r in snapshot["repos"]:
                key = "github.com#" + str(r["id"])
                old = state["core"]["repos"].get(key, {})
                if not old:
                    analysis.new_repository(state, key)
                elif old.get("language") != r.get("language"):
                    domain.change_event(state, key, "EVIDENCE", 2)
                state["core"]["repos"][key] = {
                    **old,
                    **r,
                    "key": key,
                    "name": r["full_name"],
                    "source": "PRIVATE_GITHUB" if r["private"] else "PUBLIC_GITHUB",
                    "policy_verified": not r["private"],
                    "owner": r["full_name"].split("/")[0],
                    "topics": old.get("topics", []),
                    "description": old.get("description", ""),
                    "starred": "STAR" in r["sources"],
                    "watched": "WATCH" in r["sources"],
                    "activities": activity.get(key, old.get("activities", [])),
                    "decision_version": old.get("decision_version", 0),
                    "unavailable": False,
                    "synced_at": domain.now(),
                }
                if r["private"]:
                    state["intelligence"]["profiles"].pop(key, None)
            state["core"].update(
                coverage=snapshot["coverage"],
                activity_coverage=activity_coverage,
                synced_at=domain.now(),
            )

        self.store.mutate(workspace, commit)
        return len(snapshot["repos"])

    async def ensure_profile(self, workspace, key, expected=None):
        state = self.store.read(workspace)
        expected = expected or domain.fence(state)
        domain.check_fence(state, expected)
        repo = state["core"]["repos"][key]
        if not model_allowed(repo):
            raise ValueError("Private or unverified model input blocked")
        prof = state["intelligence"]["profiles"].get(key)
        if workspace.endswith(":samples"):
            if not prof:
                _, profiles = sample_records()
                prof = profiles[key]
        else:
            session = self.session_for(workspace)
            try:
                meta, _ = await self.adapter.request(
                    session.token, "/repositories/" + str(repo["id"])
                )
                if meta.get("private") is not False or meta.get("id") != repo["id"]:
                    raise ValueError("Repository is no longer verified public")
            except Exception:

                def revoke(s):
                    s["core"]["repos"][key].update(unavailable=True, policy_verified=False)
                    s["intelligence"]["profiles"].pop(key, None)

                self.store.mutate(workspace, revoke)
                raise ValueError(
                    "Public access not verified; evidence hidden, sync to retry"
                ) from None
            repo = {
                **repo,
                "description": meta.get("description") or "",
                "topics": meta.get("topics", []),
                "language": meta.get("language"),
                "readme_sha": None,
            }
            try:
                doc, _ = await self.adapter.request(
                    session.token, "/repos/" + meta["full_name"] + "/readme"
                )
                if doc.get("encoding") != "base64" or doc.get("size", 999999) > 262144:
                    raise ValueError("README exceeds extraction ceiling")
                raw = base64.b64decode(doc["content"])
                if len(raw) > 262144:
                    raise ValueError("README exceeds extraction ceiling")
                repo["readme_sha"] = doc["sha"]
                prof = build_profile(repo, raw.decode("utf-8", errors="replace"))
            except Exception:
                # A verified public repo may legitimately have no README.
                prof = build_profile(repo)
        if not prof:
            prof = build_profile(repo)

        def commit(s):
            domain.check_fence(s, expected)
            if not model_allowed(s["core"]["repos"][key]):
                raise ValueError("Access policy changed")
            previous = s["intelligence"]["profiles"].get(key)
            if previous and previous["hash"] != prof["hash"]:
                domain.change_event(s, key, "EVIDENCE", 2)
            s["intelligence"]["profiles"][key] = prof
            current = s["core"]["repos"][key]
            for field in ("description", "topics", "language", "readme_sha"):
                if field in repo:
                    current[field] = repo[field]

        self.store.mutate(workspace, commit)
        return prof

    async def organize(self, job):
        workspace, rid = job["workspace"], job["id"]
        payload = job["payload"]
        expected = payload["fence"]
        state = self.store.read(workspace)
        domain.check_fence(state, expected)
        keys = payload["repo_keys"]
        profiles = {}
        rules_only = payload["ai_mode"] == "RULES" and job["kind"] in {
            "INCREMENTAL",
            "FULL_CLASSIFICATION",
        }
        op = analysis.operation(job["kind"])
        force = (
            payload.get("reanalyze", False)
            and payload.get("planned", False)
            and payload["ai_mode"] == "LIVE"
        )
        for key in keys:
            if (
                job["kind"] != "EXTRACT"
                and not analysis.admission(self.store.read(workspace), key, op, force)[0]
            ):
                profile = state["intelligence"]["profiles"].get(key)
                if profile:
                    profiles[key] = profile
                continue
            if not self.session_for(workspace):
                raise ValueError("Reauthenticate before continuing")
            if not rules_only:
                try:
                    profiles[key] = await self.ensure_profile(workspace, key, expected)
                except ValueError as error:
                    if "Stale" in str(error):
                        raise

                    def failed(s, key=key):
                        domain.check_fence(s, expected)
                        run = s["organization"]["runs"][rid]
                        run["outcomes"][key] = {"status": "INPUT_UNAVAILABLE", "evidence": "POLICY"}
                        run["failed"] += 1
                        run["processed"] += 1
                        receipt = (
                            s["organization"]["analysis"].setdefault(key, {}).setdefault(op, {})
                        )
                        receipt.update(
                            state="FAILED",
                            error="InputUnavailable",
                            last_attempt_run=rid,
                            last_attempt_at=time.time(),
                        )

                    self.store.mutate(workspace, failed)
        if job["kind"] == "EXTRACT":
            self.update_run(
                workspace,
                rid,
                processed=len(keys),
                message="Evidence extracted locally; no model calls",
            )
            return

        def authorized():
            try:
                return (
                    bool(self.session_for(workspace))
                    and domain.fence(self.store.read(workspace)) == expected
                    and not self.store.read(workspace)["organization"]["control"]["resetting"]
                )
            except Exception:
                return False

        if job["kind"] in {"DISCOVER", "REDISCOVER"}:
            if payload["ai_mode"] == "RULES":
                raise ValueError("Taxonomy discovery requires live AI or a validated cached result")
            if not profiles:
                raise ValueError("No approved input profiles available; sync and retry")
            claimed = self.store.mutate(
                workspace,
                lambda s: analysis.claim(
                    s,
                    list(profiles),
                    op,
                    rid,
                    force,
                    payload.get("reanalysis_reason") or payload["reason"],
                    expected,
                ),
            )
            if not claimed:
                self.update_run(
                    workspace,
                    rid,
                    processed=len(keys),
                    message=(
                        "Taxonomy inputs already analyzed or require explicit re-analysis; "
                        "no provider requests"
                    ),
                )
                return
            profiles = {k: profiles[k] for k in claimed}
            provider = self.provider_for(
                job,
                lambda: (
                    authorized()
                    and all(
                        analysis.receipt(self.store.read(workspace), k, op).get("last_attempt_run")
                        == rid
                        and analysis.receipt(self.store.read(workspace), k, op).get("state")
                        == "RUNNING"
                        and model_allowed(self.store.read(workspace)["core"]["repos"][k])
                        for k in claimed
                    )
                ),
            )
            try:
                evidence = {
                    "source": "PUBLIC_AND_SYNTHETIC",
                    "private": False,
                    "collection": cohorts.taxonomy_collection(
                        profiles, AISettings().ai_pretest_taxonomy_max_input_tokens
                    )
                    if payload.get("planned")
                    else [{"repo_id": k, **compact(p)} for k, p in profiles.items()],
                }
                model = provider.settings.openai_taxonomy_model
                result = await asyncio.to_thread(
                    provider.invoke,
                    model,
                    "taxonomy-demo",
                    TaxonomyDraft,
                    TAXONOMY_SYSTEM,
                    evidence,
                    lambda value: validate_taxonomy(value, set(claimed)),
                    **({"fresh": True} if force else {}),
                )
            finally:
                provider.close()
            self.store.mutate(
                workspace,
                lambda s: [
                    analysis.record(s, k, op, rid, result, profiles[k], expected, TAXONOMY_SYSTEM)
                    for k in claimed
                ],
            )
            if result["status"] != "PASS":
                raise ValueError(
                    "AI draft unavailable: "
                    + result.get("error_type", "provider failure")
                    + "; no taxonomy was published"
                )

            def commit(s):
                domain.check_fence(s, expected)
                draft = {
                    "id": identifier(),
                    "status": "DRAFT",
                    "proposals": result["result"]["proposals"],
                    "notes": result["result"]["notes"],
                    "evidence": result["evidence"],
                    "model": result.get("returned_model"),
                    "usage": result.get("usage"),
                    "revision": expected["revision"],
                    "repo_keys": claimed,
                    "run_id": rid,
                    "created_at": domain.now(),
                }
                draft["fence"] = expected
                s["organization"]["drafts"][draft["id"]] = draft

            self.store.mutate(workspace, commit)
            self.update_run(
                workspace,
                rid,
                processed=len(keys),
                evidence=result["evidence"],
                model=result.get("returned_model"),
            )
            return
        state = self.store.read(workspace)
        org = state["organization"]
        registry = {
            cid: {**c, "workspace": workspace} for cid, c in org["concepts"].items() if c["active"]
        }
        searchable = {
            cid: c
            for cid, c in registry.items()
            if c["kind"] != "DOMAIN"
            and tokens(" ".join([c["name"], c["description"], *c["aliases"]]))
        }
        retriever = Retriever(searchable, method="tfidf") if searchable and not rules_only else None
        for key in keys:
            state = self.store.read(workspace)
            domain.check_fence(state, expected)
            if key in state["organization"]["runs"][rid]["outcomes"]:
                continue
            if not self.session_for(workspace):
                raise ValueError("Reauthenticate before continuing")
            decision = state["core"]["repos"][key].get("decision_version", 0)
            profile = profiles.get(key)
            # Explicit user-approved rules are deterministic and cost no model calls.
            rule_ids = {
                r["concept_id"]
                for r in state["organization"]["rules"].values()
                if domain.rule_matches(r, state["core"]["repos"][key])
                and r["concept_id"] in registry
            }
            rejects = set(state["organization"]["rejections"].get(key, {}))
            manual = {
                cid
                for cid, e in state["organization"]["edges"].get(key, {}).items()
                if e["source"] == "USER"
            }
            candidates = (
                []
                if retriever is None or profile is None
                else [
                    cid
                    for cid in retriever.candidates(profile)
                    if cid
                    not in rejects
                    | manual
                    | rule_ids
                    | set(state["organization"]["edges"].get(key, {}))
                ]
            )
            result = {
                "status": "PASS",
                "evidence": "LOCAL_RULES",
                "result": {
                    "status": "NO_MATCH",
                    "assignments": [],
                    "summary": "No model request selected",
                },
            }
            allowed, skip_reason = analysis.admission(state, key, op, force)
            offline = not rules_only and not allowed
            if offline:
                # Only compatible stored decisions are replayed; new alias matches are proposals.
                success = analysis.receipt(state, key).get("last_success", {})
                compatible = (
                    success.get("revision") == expected["revision"]
                    and success.get("taxonomy_epoch") == expected["taxonomy_epoch"]
                    and success.get("fence") == expected
                    and profile
                    and success.get("profile_hash") == profile["hash"]
                )
                assignments = (
                    [
                        a
                        for a in (success.get("result") or {}).get("assignments", [])
                        if a["concept_id"] in candidates
                    ]
                    if compatible
                    else []
                )
                result["evidence"] = "STORED_ANALYSIS" if assignments else "LOCAL_MATCH"
                if not assignments and profile:
                    text = domain.normalize(
                        " ".join(
                            [
                                state["core"]["repos"][key].get("description") or "",
                                *[p["text"] for p in profile.get("phrases", [])],
                            ]
                        )
                    )
                    for cid in candidates:
                        concept = registry[cid]
                        if any(
                            " " + domain.normalize(t) + " " in " " + text + " "
                            for t in [concept["name"], *concept["aliases"]]
                        ):
                            assignments.append(
                                {
                                    "concept_id": cid,
                                    "kind": concept["kind"],
                                    "confidence": 0.0,
                                    "evidence_ids": [e["id"] for e in profile["evidence"][:2]],
                                    "reason": (
                                        "Local canonical/alias match; verify the primary purpose "
                                        "before accepting"
                                    ),
                                }
                            )
                result["result"]["assignments"] = assignments
                result["result"]["status"] = "OFFLINE_RECONCILED"
            if payload["ai_mode"] != "RULES" and candidates and allowed:
                context = {
                    "revision": expected["revision"],
                    "active_revision": expected["revision"],
                    "profile_hash": profile["hash"],
                    "active_profile_hash": profile["hash"],
                    "workspace": workspace,
                    "candidates": candidates,
                    "evidence_ids": [e["id"] for e in profile["evidence"]],
                    "rejections": list(rejects),
                }
                evidence = {
                    "source": state["core"]["repos"][key]["source"],
                    "private": False,
                    "repo_id": key,
                    "workspace": workspace,
                    "revision": expected["revision"],
                    "evidence_hash": profile["hash"],
                    "policy": profile["policy"],
                    **compact(profile),
                    "candidates": [
                        {k: registry[cid][k] for k in ("id", "kind", "name", "description")}
                        for cid in candidates
                    ],
                }
                claimed = self.store.mutate(
                    workspace,
                    lambda s: analysis.claim(
                        s,
                        [key],
                        op,
                        rid,
                        force,
                        payload.get("reanalysis_reason") or payload["reason"],
                        expected,
                    ),
                )
                if not claimed:
                    raise ValueError("Analysis admission changed; preview again")

                def classification_authorized():
                    current = self.store.read(workspace)
                    receipt = analysis.receipt(current, key)
                    repo = current["core"]["repos"].get(key, {})
                    return (
                        authorized()
                        and receipt.get("state") == "RUNNING"
                        and receipt.get("last_attempt_run") == rid
                        and model_allowed(repo)
                        and repo.get("decision_version", 0) == decision
                        and current["intelligence"]["profiles"].get(key, {}).get("hash")
                        == profile["hash"]
                    )

                provider = self.provider_for(job, classification_authorized)
                try:
                    result = await asyncio.to_thread(
                        provider.invoke,
                        provider.settings.openai_classification_model,
                        "classification-demo",
                        Classification,
                        CLASSIFY_SYSTEM,
                        evidence,
                        lambda value: validate_classification(value, context, registry),
                        **({"fresh": True} if force else {}),
                    )
                finally:
                    provider.close()
                # Receipt is historical fact even if the following association commit is stale.
                self.store.mutate(
                    workspace,
                    lambda s: analysis.record(
                        s, key, op, rid, result, profile, expected, CLASSIFY_SYSTEM
                    ),
                )

            def commit(s):
                domain.check_fence(s, expected)
                run = s["organization"]["runs"][rid]
                if key in run["outcomes"]:
                    return
                if s["core"]["repos"][key].get("decision_version", 0) != decision or (
                    profile
                    and s["intelligence"]["profiles"].get(key, {}).get("hash") != profile["hash"]
                ):
                    run["stale"] += 1
                    run["outcomes"][key] = {"status": "STALE", "evidence": result["evidence"]}
                    run["processed"] += 1
                    return
                if result["status"] != "PASS":
                    run["failed"] += 1
                else:
                    if rule_ids:
                        domain.mapping(s, [key], list(rule_ids), "ADD", "RULE")
                    for assignment in result["result"]["assignments"]:
                        domain.active(s, assignment["concept_id"])
                        if assignment["concept_id"] in s["organization"]["rejections"].get(key, {}):
                            continue
                        sid = digest([key, assignment["concept_id"]])
                        old = s["organization"]["suggestions"].get(sid)
                        if old and old["status"] in {"ACCEPTED", "REJECTED"}:
                            continue
                        s["organization"]["suggestions"][sid] = {
                            **assignment,
                            "id": sid,
                            "repo_key": key,
                            "status": "PROPOSED",
                            "evidence": result["evidence"],
                            "run_id": rid,
                            "model": result.get("returned_model"),
                            "profile_hash": profile["hash"],
                            "revision": expected["revision"],
                            "fence": expected,
                            "decision_version": decision,
                        }
                run["outcomes"][key] = {
                    "status": result["result"]["status"]
                    if result["status"] == "PASS"
                    else "FAILED",
                    "evidence": result["evidence"],
                    "error": result.get("error_type"),
                    "model": result.get("returned_model"),
                    "usage": result.get("usage"),
                    "seconds": result.get("seconds"),
                    "reason": skip_reason if offline else None,
                }
                rec = (
                    s["organization"]
                    .setdefault("analysis", {})
                    .setdefault(key, {})
                    .setdefault("classification", {})
                )
                if offline or rules_only:
                    rec["last_local_revision"] = expected["revision"]
                    rec["last_local_at"] = domain.now()
                run["processed"] += 1

            self.store.mutate(workspace, commit)

        def complete(s):
            domain.check_fence(s, expected)
            run = s["organization"]["runs"][rid]
            if (
                not run["failed"]
                and not run["stale"]
                and set(keys) == {k for k, r in s["core"]["repos"].items() if model_allowed(r)}
            ):
                s["organization"]["control"]["processed_revision"] = expected["revision"]

        self.store.mutate(workspace, complete)

    def cleanup(self, workspace, rid, plan):
        def action(state):
            org = state["organization"]
            scope = plan["scope"]
            selected = {
                cid
                for cid, c in org["concepts"].items()
                if c["kind"] in scope["kinds"] and not c.get("protected")
            }
            if "DOMAIN" in scope["kinds"] and "PROJECT" not in scope["kinds"]:
                # Temporarily allow creation of the protected parent during cleanup.
                org["control"]["resetting"] = False
                parent = domain.unassigned(state)
                org["control"]["resetting"] = True
                for c in org["concepts"].values():
                    if c.get("domain") in selected:
                        c["domain"] = parent
            for cid in selected:
                org["concepts"].pop(cid)
            for key, edges in org["edges"].items():
                for cid, edge in list(edges.items()):
                    if cid in selected or (scope["associations"] and edge["source"] != "USER"):
                        del edges[cid]
            for key, rejects in org["rejections"].items():
                for cid in selected:
                    rejects.pop(cid, None)
            for sid, s in list(org["suggestions"].items()):
                if s["concept_id"] in selected or (
                    scope["suggestions"] and s["status"] == "PROPOSED"
                ):
                    del org["suggestions"][sid]
            if scope["drafts"]:
                org["drafts"].clear()
            if scope["history"]:
                org["runs"] = {rid: org["runs"][rid]}
            if scope["rules"]:
                org["rules"].clear()
            else:
                org["rules"] = {
                    k: r for k, r in org["rules"].items() if r["concept_id"] not in selected
                }
            if scope["cache"]:
                state["intelligence"]["profiles"].clear()
            if selected or scope["cache"] or scope["associations"]:
                for operations in org.get("analysis", {}).values():
                    for receipt in operations.values():
                        success = receipt.get("last_success")
                        if success:
                            success["result"] = None
                            success["references_invalidated"] = True
                            if scope["cache"]:
                                success.pop("cache_key", None)
            if set(scope["kinds"]) == {"DOMAIN", "PROJECT", "TOPIC", "TAG"}:
                org["control"].update(revision=0, processed_revision=0)
                org["changes"].clear()
            elif selected:
                org["control"]["revision"] += 1
            org["control"]["resetting"] = False
            org["control"]["active_run"] = None
            org["audit"].append(
                {
                    "id": rid,
                    "at": domain.now(),
                    "scope": scope,
                    "counts": plan["counts"],
                    "status": "RESET_COMPLETED",
                    "verified": True,
                }
            )
            org["runs"][rid].update(
                status="COMPLETED",
                message="Cleanup verified; GitHub/Core and cost ledger preserved",
                processed=1,
                finished_at=domain.now(),
            )
            assert not selected & set(org["concepts"])
            assert not any(selected & set(edges) for edges in org["edges"].values())

        self.store.mutate(workspace, action)
        mode = plan["scope"]["restart"]
        if mode != "NONE":
            try:
                self.queue(
                    workspace,
                    "FULL_CLASSIFICATION" if mode == "RECLASSIFY_EXISTING" else "REDISCOVER",
                    ai_mode="CACHE",
                    reason="RESET_RESTART",
                )
            except ValueError as exc:
                self.update_run(
                    workspace, rid, message="Cleanup verified. Restart requires action: " + str(exc)
                )
