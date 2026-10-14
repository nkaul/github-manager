"""Finite adaptive grants and monetary holds in the original spending database."""

import hashlib
import json
import time
from pathlib import Path

from app.demo.pricing import VERSION, dollars
from app.pretest.ai.storage import BudgetError


class RunBudgets:
    def __init__(self, ledger):
        self.ledger = ledger
        with ledger.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS app_run_budgets(
                    id TEXT PRIMARY KEY, workspace TEXT NOT NULL, state TEXT NOT NULL,
                    ceiling INTEGER NOT NULL, remaining INTEGER NOT NULL,
                    http_limit INTEGER NOT NULL, http_used INTEGER NOT NULL DEFAULT 0,
                    generation_limit INTEGER NOT NULL, generation_used INTEGER NOT NULL DEFAULT 0,
                    pricing TEXT NOT NULL, created REAL NOT NULL, expires REAL NOT NULL,
                    actor TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS app_call_prices(
                    call_id TEXT PRIMARY KEY, plan_id TEXT,
                    version TEXT NOT NULL, rates TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS app_http_scope(
                    http_id INTEGER PRIMARY KEY, plan_id TEXT);
            """)
            if "store_id" not in {r[1] for r in db.execute("PRAGMA table_info(app_run_budgets)")}:
                db.execute(
                    "ALTER TABLE app_run_budgets ADD COLUMN store_id TEXT NOT NULL DEFAULT ''"
                )
            db.commit()

    @staticmethod
    def held(db):
        return db.execute(
            "SELECT COALESCE(SUM(remaining),0) FROM app_run_budgets "
            "WHERE state IN ('HELD','QUEUED','RUNNING')"
        ).fetchone()[0]

    def available(self):
        with self.ledger.connect() as db:
            db.execute("BEGIN")
            used = db.execute(
                "SELECT COALESCE(SUM(COALESCE(charged,reserved)),0) FROM calls"
            ).fetchone()[0]
            return max(0, self.ledger.cap - used - self.held(db))

    def reserve(
        self, plan_id, workspace, ceiling, generations, actor, expected_revision, store_id=""
    ):
        with self.ledger.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            old = db.execute(
                "SELECT workspace,state FROM app_run_budgets WHERE id=?", (plan_id,)
            ).fetchone()
            if old:
                if old[0] != workspace or old[1] not in {"HELD", "QUEUED", "RUNNING"}:
                    raise BudgetError(
                        "Adaptive plan has already finished or belongs to another workspace"
                    )
                return
            revision = db.execute(
                "SELECT revision FROM phase09_allowance_control WHERE id=1"
            ).fetchone()[0]
            if revision != expected_revision:
                raise BudgetError("Budget policy changed; preview again")
            if db.execute("SELECT 1 FROM calls WHERE state='BOUND_VIOLATION'").fetchone():
                raise BudgetError(
                    "Earlier usage exceeded its reservation; paid continuation stopped"
                )
            used = db.execute(
                "SELECT COALESCE(SUM(COALESCE(charged,reserved)),0) FROM calls"
            ).fetchone()[0]
            if ceiling < 0 or used + self.held(db) + ceiling > self.ledger.cap:
                raise BudgetError("Insufficient unreserved dollars; preview a smaller run")
            db.execute(
                "INSERT INTO app_run_budgets VALUES (?,?,'HELD',?,?,?,0,?,0,?,?,?,?,?)",
                (
                    plan_id,
                    workspace,
                    ceiling,
                    ceiling,
                    2 * generations,
                    generations,
                    VERSION,
                    time.time(),
                    time.time() + 300,
                    actor,
                    store_id,
                ),
            )
            db.commit()

    def activate(self, plan_id, workspace):
        with self.ledger.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT state,pricing FROM app_run_budgets WHERE id=? AND workspace=?",
                (plan_id, workspace),
            ).fetchone()
            if not row or row[0] not in {"HELD", "QUEUED", "RUNNING"} or row[1] != VERSION:
                raise BudgetError("Adaptive run grant is unavailable")
            db.execute("UPDATE app_run_budgets SET state='RUNNING' WHERE id=?", (plan_id,))
            db.commit()

    def queued(self, plan_id):
        with self.ledger.connect() as db:
            db.execute(
                "UPDATE app_run_budgets SET state='QUEUED' WHERE id=? AND state='HELD'", (plan_id,)
            )
            db.commit()

    def finish(self, plan_id):
        # Only the unused hold is released. Unknown calls keep their own reservations.
        with self.ledger.connect() as db:
            db.execute(
                "UPDATE app_run_budgets SET state='FINISHED',remaining=0 WHERE id=?", (plan_id,)
            )
            db.commit()

    def reconcile(self, store):
        with store.connect() as db:
            jobs = {r["id"]: r["status"] for r in db.execute("SELECT id,status FROM jobs")}
        with self.ledger.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            rows = db.execute(
                "SELECT id,state,expires FROM app_run_budgets WHERE state!='FINISHED' "
                "AND (store_id=? OR store_id='')",
                (self.store_id(store),),
            ).fetchall()
            for plan_id, state, expires in rows:
                status = jobs.get(plan_id)
                if status in {
                    "COMPLETED",
                    "FAILED",
                    "PARTIAL_FAILED",
                    "CANCELLED_STALE",
                    "INTERRUPTED",
                } or (status is None and state == "HELD" and expires < time.time()):
                    db.execute(
                        "UPDATE app_run_budgets SET state='FINISHED',remaining=0 WHERE id=?",
                        (plan_id,),
                    )
                elif status in {"QUEUED", "WAITING_FOR_REAUTH"} and state == "HELD":
                    db.execute("UPDATE app_run_budgets SET state='QUEUED' WHERE id=?", (plan_id,))
            db.commit()

    @staticmethod
    def store_id(store):
        return hashlib.sha256(str(Path(store.path).resolve()).encode()).hexdigest()

    def outcome(self, plan_id):
        with self.ledger.connect() as db:
            row = db.execute(
                "SELECT ceiling,http_used,generation_used,pricing,state "
                "FROM app_run_budgets WHERE id=?",
                (plan_id,),
            ).fetchone()
            costs = db.execute(
                "SELECT c.reserved,c.charged FROM calls c JOIN app_call_prices p "
                "ON p.call_id=c.id WHERE p.plan_id=?",
                (plan_id,),
            ).fetchall()
        if not row:
            return None
        return {
            "ceiling_usd": dollars(row[0]),
            "http_used": row[1],
            "generation_used": row[2],
            "pricing_version": row[3],
            "state": row[4],
            "estimated_usd": dollars(sum(c or 0 for _, c in costs)),
            "reserved_usd": dollars(sum(r for r, c in costs if c is None)),
        }

    def summary(self):
        with self.ledger.connect() as db:
            return {
                "held_usd": dollars(self.held(db)),
                "available_usd": dollars(self.available()),
                "pricing_version": VERSION,
            }


def adaptive_http(db, plan_id, endpoint):
    row = db.execute(
        "SELECT state,http_limit,http_used,generation_limit,generation_used "
        "FROM app_run_budgets WHERE id=?",
        (plan_id,),
    ).fetchone()
    if not row or row[0] != "RUNNING":
        raise BudgetError("Adaptive grant is not running")
    _, http_limit, http_used, gen_limit, gen_used = row
    if http_used >= http_limit or (endpoint == "/v1/responses" and gen_used >= gen_limit):
        raise BudgetError("Approved adaptive run request limit reached")
    db.execute("UPDATE app_run_budgets SET http_used=http_used+1 WHERE id=?", (plan_id,))


def call_price(db, call_id, plan_id, rates):
    db.execute(
        "INSERT INTO app_call_prices VALUES (?,?,?,?)",
        (call_id, plan_id, VERSION, json.dumps(rates)),
    )


def fixed_http_count(db):
    return db.execute(
        "SELECT COUNT(*) FROM phase09_http h LEFT JOIN app_http_scope s "
        "ON h.id=s.http_id WHERE s.plan_id IS NULL"
    ).fetchone()[0]


def fixed_generation_count(db):
    return db.execute(
        "SELECT COUNT(*) FROM calls c LEFT JOIN app_call_prices p "
        "ON c.id=p.call_id WHERE p.plan_id IS NULL"
    ).fetchone()[0]
