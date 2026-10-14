"""Audited local-app allowance windows; historical experiment records stay intact."""

import json
import time
import uuid
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.demo import pricing
from app.demo.run_budget import (
    RunBudgets,
    adaptive_http,
    call_price,
    fixed_generation_count,
    fixed_http_count,
)
from app.pretest.ai.provider import ProviderBlocked
from app.pretest.ai.storage import BudgetError, Ledger


class AllowanceUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    action: Literal["RENEW", "SET_LIMITS"]
    expected_revision: int = Field(ge=0, strict=True)
    requests: int | None = Field(default=None, ge=0, le=1000, strict=True)
    generations: int | None = Field(default=None, ge=0, le=1000, strict=True)
    reason: str = Field(min_length=3, max_length=200)

    @model_validator(mode="after")
    def selected_limits(self):
        if self.action == "RENEW" and (self.requests is None or self.requests < 2):
            raise ValueError("A new window needs at least two HTTP requests")
        if self.action == "SET_LIMITS" and self.requests is None and self.generations is None:
            raise ValueError("Select at least one limit to update")
        return self


class RequestAllowance:
    def __init__(self, ledger):
        self.ledger = ledger
        with ledger.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS phase09_authorization(id TEXT PRIMARY KEY, cap INTEGER);
                CREATE TABLE IF NOT EXISTS phase09_http(id INTEGER PRIMARY KEY AUTOINCREMENT,
                    endpoint TEXT NOT NULL, at REAL NOT NULL, status INTEGER);
                CREATE TABLE IF NOT EXISTS phase09_allowance_control(
                    id INTEGER PRIMARY KEY CHECK(id=1), revision INTEGER NOT NULL,
                    http_base INTEGER NOT NULL, http_limit INTEGER NOT NULL,
                    generation_base INTEGER NOT NULL, generation_limit INTEGER NOT NULL,
                    updated_at REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS phase09_allowance_audit(
                    revision INTEGER PRIMARY KEY, at REAL NOT NULL, actor TEXT NOT NULL,
                    action TEXT NOT NULL, reason TEXT NOT NULL,
                    before_json TEXT NOT NULL, after_json TEXT NOT NULL);
            """)
            db.execute(
                "INSERT OR IGNORE INTO phase09_authorization VALUES ('approved-2026-10-12',20)"
            )
            if db.execute("SELECT cap FROM phase09_authorization").fetchall() != [(20,)]:
                raise ProviderBlocked("Original Phase 0.9 request authorization mismatch")
            baseline = min(34, db.execute("SELECT COUNT(*) FROM calls").fetchone()[0])
            db.execute(
                "INSERT OR IGNORE INTO phase09_allowance_control VALUES (1,0,0,20,?,?,?)",
                (baseline, baseline + 10, time.time()),
            )
            db.commit()
        RunBudgets(ledger)

    @staticmethod
    def snapshot(db):
        revision, http_base, http_limit, gen_base, gen_limit, updated = db.execute(
            "SELECT revision,http_base,http_limit,generation_base,generation_limit,updated_at "
            "FROM phase09_allowance_control WHERE id=1"
        ).fetchone()
        rows = db.execute("SELECT endpoint,status FROM phase09_http").fetchall()
        generations = db.execute("SELECT COUNT(*) FROM calls").fetchone()[0]
        fixed_http = fixed_http_count(db)
        fixed_generations = fixed_generation_count(db)
        return {
            "revision": revision,
            "window_started_at": updated,
            "http": {
                "limit": http_limit - http_base,
                "used": max(0, fixed_http - http_base),
                "remaining": max(0, http_limit - fixed_http),
                "lifetime_used": len(rows),
                "fixed_lifetime_used": fixed_http,
                "lifetime_limit": http_limit,
                "generation_attempts": sum(p == "/v1/responses" for p, _ in rows),
                "count_attempts": sum(p.endswith("/input_tokens") for p, _ in rows),
            },
            "generations": {
                "limit": gen_limit - gen_base,
                "used": max(0, fixed_generations - gen_base),
                "remaining": max(0, gen_limit - fixed_generations),
                "lifetime_used": generations,
                "fixed_lifetime_used": fixed_generations,
                "lifetime_limit": gen_limit,
            },
        }

    def take(self, endpoint):
        if endpoint not in {"/v1/responses", "/v1/responses/input_tokens"}:
            raise ProviderBlocked("Unexpected OpenAI endpoint")
        with self.ledger.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            plan_id = getattr(self.ledger, "plan_id", None)
            if plan_id:
                adaptive_http(db, plan_id, endpoint)
            else:
                total = fixed_http_count(db)
                limit = db.execute(
                    "SELECT http_limit FROM phase09_allowance_control WHERE id=1"
                ).fetchone()[0]
                if total >= limit:
                    raise ProviderBlocked(
                        "HTTP allowance reached; use Manage API allowance to renew it"
                    )
                if endpoint == "/v1/responses":
                    generation_limit = db.execute(
                        "SELECT generation_limit FROM phase09_allowance_control WHERE id=1"
                    ).fetchone()[0]
                    if fixed_generation_count(db) >= generation_limit:
                        raise ProviderBlocked(
                            "Generation allowance reached; use Manage API allowance"
                        )
            cursor = db.execute(
                "INSERT INTO phase09_http(endpoint,at) VALUES (?,?)", (endpoint, time.time())
            )
            db.execute("INSERT INTO app_http_scope VALUES (?,?)", (cursor.lastrowid, plan_id))
            db.commit()
            return cursor.lastrowid

    def record(self, key, status):
        with self.ledger.connect() as db:
            db.execute("UPDATE phase09_http SET status=? WHERE id=?", (status, key))
            db.commit()

    def summary(self):
        return self.policy()["http"]

    def policy(self):
        with self.ledger.connect() as db:
            db.execute("BEGIN")
            return self.snapshot(db)

    def history(self):
        with self.ledger.connect() as db:
            rows = db.execute(
                "SELECT revision,at,actor,action,reason,before_json,after_json "
                "FROM phase09_allowance_audit ORDER BY revision DESC LIMIT 20"
            ).fetchall()
        return [
            dict(
                revision=r,
                at=at,
                actor=actor,
                action=action,
                reason=reason,
                before=json.loads(before),
                after=json.loads(after),
            )
            for r, at, actor, action, reason, before, after in rows
        ]

    def update(self, value: AllowanceUpdate, actor: str):
        with self.ledger.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            before = self.snapshot(db)
            if value.expected_revision != before["revision"]:
                raise ValueError("Allowance changed; close and reopen the controls before retrying")
            http = before["http"]
            gen = before["generations"]
            if value.action == "RENEW":
                http_base, gen_base = http["fixed_lifetime_used"], gen["fixed_lifetime_used"]
                requests = value.requests
                generations = value.generations if value.generations is not None else requests // 2
            else:
                http_base = http["lifetime_limit"] - http["limit"]
                gen_base = gen["lifetime_limit"] - gen["limit"]
                requests = value.requests if value.requests is not None else http["limit"]
                generations = value.generations if value.generations is not None else gen["limit"]
                if requests < http["used"] or generations < gen["used"]:
                    raise ValueError("A window limit cannot be lower than its recorded usage")
            db.execute(
                "UPDATE phase09_allowance_control SET revision=revision+1,http_base=?,"
                "http_limit=?,generation_base=?,generation_limit=?,updated_at=? WHERE id=1",
                (http_base, http_base + requests, gen_base, gen_base + generations, time.time()),
            )
            after = self.snapshot(db)
            db.execute(
                "INSERT INTO phase09_allowance_audit VALUES (?,?,?,?,?,?,?)",
                (
                    after["revision"],
                    time.time(),
                    actor,
                    value.action,
                    value.reason,
                    json.dumps(before),
                    json.dumps(after),
                ),
            )
            db.commit()
            return after


class ApplicationLedger(Ledger):
    """Apply dynamic generation admission in the same transaction as cost reservation.

    The frozen pre-test Ledger retains its original behavior. This local adapter
    uses the audited control row instead of the old fixed max_calls parameter.
    """

    def __init__(self, *args, **kwargs):
        self.plan_id = kwargs.pop("plan_id", None)
        super().__init__(*args, **kwargs)
        RequestAllowance(self)

    def reserve(self, task, model, input_tokens, max_output, *, max_calls=None):
        if model not in pricing.RATES or min(input_tokens, max_output) < 0:
            raise BudgetError("Unknown price or invalid token bound")
        amount = pricing.reserve_amount(model, input_tokens, max_output)
        ident = uuid.uuid4().hex
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if self.plan_id:
                plan = db.execute(
                    "SELECT state,remaining,generation_limit,generation_used "
                    "FROM app_run_budgets WHERE id=?",
                    (self.plan_id,),
                ).fetchone()
                if not plan or plan[0] != "RUNNING" or plan[1] < amount or plan[3] >= plan[2]:
                    raise BudgetError("Adaptive run reservation or generation bound reached")
            else:
                limit = db.execute(
                    "SELECT generation_limit FROM phase09_allowance_control WHERE id=1"
                ).fetchone()[0]
                if fixed_generation_count(db) >= limit:
                    raise BudgetError("Generation allowance reached; use Manage API allowance")
            if db.execute("SELECT 1 FROM calls WHERE state='BOUND_VIOLATION'").fetchone():
                raise BudgetError(
                    "Earlier usage exceeded its reservation; paid continuation stopped"
                )
            used = db.execute(
                "SELECT COALESCE(SUM(COALESCE(charged,reserved)),0) FROM calls"
            ).fetchone()[0]
            if used + RunBudgets.held(db) + (0 if self.plan_id else amount) > self.cap:
                raise BudgetError("Experiment-wide $5 admission ceiling reached")
            if self.plan_id:
                db.execute(
                    "UPDATE app_run_budgets SET remaining=remaining-?,"
                    "generation_used=generation_used+1 WHERE id=?",
                    (amount, self.plan_id),
                )
            db.execute(
                "INSERT INTO calls VALUES (?,?,?,?,NULL,?,?,?)",
                (ident, task, model, amount, "RESERVED", "{}", datetime.now(UTC).isoformat()),
            )
            call_price(db, ident, self.plan_id, pricing.RATES[model])
            db.commit()
        return ident

    def settle(self, ident, usage, *, no_charge=False):
        from decimal import ROUND_CEILING, Decimal

        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            saved = db.execute(
                "SELECT rates FROM app_call_prices WHERE call_id=?", (ident,)
            ).fetchone()
            if not saved:
                db.rollback()
                return super().settle(ident, usage, no_charge=no_charge)
            row = db.execute("SELECT reserved,charged FROM calls WHERE id=?", (ident,)).fetchone()
            if not row or row[1] is not None:
                raise BudgetError("Unknown/already settled reservation")
            if no_charge:
                charged, state = 0, "REJECTED_BEFORE_GENERATION"
            else:
                inp, out = usage.get("input_tokens"), usage.get("output_tokens")
                if type(inp) is not int or type(out) is not int or min(inp, out) < 0:
                    return
                detail = usage.get("input_tokens_details") or {}
                cached, writes = detail.get("cached_tokens", 0), detail.get("cache_write_tokens", 0)
                if (
                    type(cached) is not int
                    or type(writes) is not int
                    or not 0 <= cached <= inp
                    or not 0 <= writes <= inp
                ):
                    return
                rate = {k: Decimal(v) for k, v in json.loads(saved[0]).items()}
                charged = int(
                    (
                        (inp - cached) * rate["input"]
                        + cached * rate["cached"]
                        + writes * rate["write"]
                        + out * rate["output"]
                    ).to_integral_value(rounding=ROUND_CEILING)
                )
                state = "SETTLED" if charged <= row[0] else "BOUND_VIOLATION"
            db.execute(
                "UPDATE calls SET charged=?,state=?,detail=? WHERE id=?",
                (charged, state, json.dumps(usage), ident),
            )
            db.commit()
