"""Transactional, owner-scoped local aggregate adapter; never stores OAuth secrets."""

import json
import os
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Protocol


def identifier():
    return uuid.uuid4().hex


def initial_state():
    return {
        "core": {"repos": {}, "coverage": [], "synced_at": None, "activity_coverage": []},
        "intelligence": {"profiles": {}, "version": "demo-rake-v2"},
        "organization": {
            "concepts": {},
            "edges": {},
            "rejections": {},
            "suggestions": {},
            "drafts": {},
            "rules": {},
            "runs": {},
            "audit": [],
            "changes": [],
            "control": {
                "generation": 1,
                "taxonomy_epoch": 1,
                "ai_epoch": 1,
                "cache_epoch": 1,
                "revision": 0,
                "processed_revision": 0,
                "version": 0,
                "active_run": None,
                "resetting": False,
                "auto_enabled": False,
                "quiet_seconds": 90,
                "cooldown_seconds": 1800,
                "last_auto": 0,
                "policy_version": 1,
            },
        },
    }


class WorkspaceRepository(Protocol):
    def read(self, workspace: str) -> dict: ...
    def mutate(self, workspace: str, action): ...


class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS workspace(id TEXT PRIMARY KEY, state TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, workspace TEXT NOT NULL,
                    kind TEXT NOT NULL, payload TEXT NOT NULL, status TEXT NOT NULL,
                    lease REAL NOT NULL DEFAULT 0, created REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS previews(id TEXT PRIMARY KEY, workspace TEXT NOT NULL,
                    plan TEXT NOT NULL, expires REAL NOT NULL, consumed INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS run_previews(
                    id TEXT PRIMARY KEY, workspace TEXT NOT NULL,
                    plan TEXT NOT NULL, expires REAL NOT NULL, consumed INTEGER NOT NULL DEFAULT 0);
            """)
        os.chmod(self.path, 0o600)
        # Persist the one-time, offline migration before detailed history can be reset.
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            from app.demo.analysis import upgrade

            for row in db.execute("SELECT id,state FROM workspace").fetchall():
                state = json.loads(row["state"])
                if state["organization"].get("analysis_schema") != 1:
                    upgrade(state)
                    self.save(db, row["id"], state)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        try:
            db.execute("PRAGMA journal_mode=DELETE")
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def load(db, workspace):
        from app.demo.analysis import upgrade

        row = db.execute("SELECT state FROM workspace WHERE id=?", (workspace,)).fetchone()
        return upgrade(json.loads(row[0]) if row else initial_state())

    @staticmethod
    def save(db, workspace, state):
        state["organization"]["control"]["version"] += 1
        db.execute("INSERT OR REPLACE INTO workspace VALUES (?,?)", (workspace, json.dumps(state)))

    def read(self, workspace):
        with self.connect() as db:
            return self.load(db, workspace)

    def mutate(self, workspace, action):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            state = self.load(db, workspace)
            result = action(state)
            self.save(db, workspace, state)
            return result

    def enqueue(self, workspace, kind, payload, run, plan_id=None):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            state = self.load(db, workspace)
            org = state["organization"]
            if plan_id:
                row = db.execute(
                    "SELECT * FROM run_previews WHERE id=? AND workspace=?", (plan_id, workspace)
                ).fetchone()
                if not row:
                    raise ValueError("Run preview is unavailable")
                if row["consumed"] and plan_id in org["runs"]:
                    return org["runs"][plan_id]
                if (
                    row["consumed"]
                    or row["expires"] < time.time()
                    or json.loads(row["plan"])["version"] != org["control"]["version"]
                ):
                    raise ValueError("Run preview is expired or stale; preview again")
            if org["control"]["resetting"] or org["control"]["active_run"]:
                raise ValueError("A workspace job is already active")
            org["runs"][run["id"]] = run
            org["control"]["active_run"] = run["id"]
            self.save(db, workspace, state)
            db.execute(
                "INSERT INTO jobs VALUES (?,?,?,?,?,0,?)",
                (run["id"], workspace, kind, json.dumps(payload), "QUEUED", time.time()),
            )
            if plan_id:
                db.execute("UPDATE run_previews SET consumed=1 WHERE id=?", (plan_id,))
        return run

    def preview_run(self, workspace, plan):
        plan_id = identifier()
        with self.connect() as db:
            db.execute(
                "INSERT INTO run_previews VALUES (?,?,?,?,0)",
                (plan_id, workspace, json.dumps(plan), time.time() + 300),
            )
        return plan_id

    def run_plan(self, workspace, plan_id):
        with self.connect() as db:
            row = db.execute(
                "SELECT * FROM run_previews WHERE id=? AND workspace=?", (plan_id, workspace)
            ).fetchone()
            if not row or (not row["consumed"] and row["expires"] < time.time()):
                raise ValueError("Run preview expired or unavailable; preview again")
            return {**json.loads(row["plan"]), "consumed": bool(row["consumed"])}

    def claim(self, authorized_workspaces):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            rows = db.execute(
                "SELECT * FROM jobs WHERE status IN ('QUEUED','WAITING_FOR_REAUTH') "
                "ORDER BY created"
            ).fetchall()
            for row in rows:
                state = self.load(db, row["workspace"])
                org = state["organization"]
                if org["control"]["active_run"] != row["id"] or org["runs"].get(row["id"], {}).get(
                    "status"
                ) in {"CANCELLED_STALE", "COMPLETED", "FAILED", "INTERRUPTED", "PARTIAL_FAILED"}:
                    db.execute("UPDATE jobs SET status='CANCELLED_STALE' WHERE id=?", (row["id"],))
                    continue
                if row["workspace"] not in authorized_workspaces:
                    db.execute(
                        "UPDATE jobs SET status='WAITING_FOR_REAUTH' WHERE id=?", (row["id"],)
                    )
                    continue
                db.execute(
                    "UPDATE jobs SET status='RUNNING',lease=? WHERE id=?",
                    (time.time() + 180, row["id"]),
                )
                return {**dict(row), "payload": json.loads(row["payload"])}
        return None

    def recover(self):
        # Never blindly repeat inference whose remote outcome is uncertain after process death.
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            for row in db.execute("SELECT * FROM jobs WHERE status='RUNNING'").fetchall():
                state = self.load(db, row["workspace"])
                org = state["organization"]
                from app.demo.analysis import interrupt

                interrupt(state, row["id"])
                run = org["runs"].get(row["id"])
                if run:
                    run.update(
                        status="INTERRUPTED",
                        message="Backend restarted; review results before retry",
                    )
                if org["control"]["active_run"] == row["id"]:
                    org["control"]["active_run"] = None
                if row["kind"] == "RESET":
                    # Cleanup is local/idempotent; unlike inference it can safely resume.
                    org["control"]["active_run"] = row["id"]
                    if run:
                        run.update(status="QUEUED", message="Resuming local reset cleanup")
                    db.execute("UPDATE jobs SET status='QUEUED' WHERE id=?", (row["id"],))
                else:
                    db.execute("UPDATE jobs SET status='INTERRUPTED' WHERE id=?", (row["id"],))
                self.save(db, row["workspace"], state)

    def finish(self, job, status):
        with self.connect() as db:
            db.execute("UPDATE jobs SET status=?,lease=0 WHERE id=?", (status, job["id"]))

    def preview(self, workspace, plan):
        key = identifier()
        with self.connect() as db:
            db.execute(
                "INSERT INTO previews VALUES (?,?,?,?,0)",
                (key, workspace, json.dumps(plan), time.time() + 300),
            )
        return key

    def execute_preview(self, workspace, key, confirmation, action):
        if confirmation != "DELETE":
            raise ValueError("Type exactly DELETE")
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT * FROM previews WHERE id=? AND workspace=?", (key, workspace)
            ).fetchone()
            if not row or row["consumed"] or row["expires"] < time.time():
                raise ValueError("Reset preview expired, reused or unavailable")
            plan = json.loads(row["plan"])
            state = self.load(db, workspace)
            if state["organization"]["control"]["version"] != plan["version"]:
                raise ValueError("Workspace changed; request a new preview")
            result = action(state, plan)
            self.save(db, workspace, state)
            db.execute("UPDATE previews SET consumed=1 WHERE id=?", (key,))
            if result.get("kind") == "RESET":
                db.execute(
                    "INSERT INTO jobs VALUES (?,?,?,?,?,0,?)",
                    (result["id"], workspace, "RESET", json.dumps(plan), "QUEUED", time.time()),
                )
            return result
