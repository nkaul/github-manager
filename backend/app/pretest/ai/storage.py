import hashlib
import json
import math
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

PRICES = {
    "gpt-6.1-sol": {"input": 2.0, "cached": 0.10, "write": 2.5, "output": 10.0},
    "gpt-6-luna": {"input": 0.10, "cached": 0.01, "write": 0.125, "output": 0.50},
    "gpt-6-astra": {"input": 10.0, "cached": 1.0, "write": 12.5, "output": 50.0},
}
PRICE_DATE = "2026-10-11"


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


def private_json(path, value, *, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    flags = os.O_WRONLY | os.O_CREAT | (os.O_EXCL if exclusive else os.O_TRUNC)
    descriptor = os.open(path, flags, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


class BudgetError(ValueError):
    pass


class Ledger:
    def __init__(self, directory, cap=5.0, *, initialize=False, anchor=None):
        self.directory = Path(directory)
        self.path = self.directory / "runs.sqlite3"
        self.anchor = Path(anchor) if anchor else self.directory.parent / "ai-budget.local.json"
        self.cap = int(round(cap * 1_000_000))
        if initialize:
            if self.path.exists() or self.anchor.exists():
                raise BudgetError("Experiment already initialized; reuse its ledger")
            self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
            experiment = uuid.uuid4().hex
            private_json(
                self.anchor,
                {"experiment": experiment, "cap": self.cap, "path": str(self.path.resolve())},
                exclusive=True,
            )
            with self.connect() as db:
                db.executescript("""
                    CREATE TABLE experiment(id TEXT PRIMARY KEY, cap INTEGER NOT NULL);
                    CREATE TABLE calls(id TEXT PRIMARY KEY, task TEXT, model TEXT,
                        reserved INTEGER NOT NULL, charged INTEGER, state TEXT, detail TEXT,
                        created TEXT NOT NULL);
                    CREATE TABLE cache(key TEXT PRIMARY KEY, value TEXT NOT NULL);
                """)
                db.execute("INSERT INTO experiment VALUES (?, ?)", (experiment, self.cap))
                db.commit()
        if not self.path.exists() or not self.anchor.exists():
            raise BudgetError(
                "Missing durable budget state; explicit first initialization required"
            )
        approved = json.loads(self.anchor.read_text())
        with self.connect() as db:
            row = db.execute("SELECT id, cap FROM experiment").fetchone()
            if not row or row != (approved["experiment"], approved["cap"]):
                raise BudgetError("Corrupt/mismatched experiment state")
            if row[1] != self.cap or approved["path"] != str(self.path.resolve()):
                raise BudgetError("Experiment cap/path cannot change")
        os.chmod(self.path, 0o600)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        try:
            # Rollback journal avoids leaving unprotected WAL sidecars.
            db.execute("PRAGMA journal_mode=DELETE")
            yield db
        finally:
            db.close()

    def summary(self):
        with self.connect() as db:
            rows = db.execute("SELECT reserved, charged, state FROM calls").fetchall()
        charged = sum(c or 0 for _, c, _ in rows)
        outstanding = sum(r for r, c, _ in rows if c is None)
        return {
            "cap_usd": self.cap / 1e6,
            "estimated_usd": charged / 1e6,
            "reserved_usd": outstanding / 1e6,
            "calls": len(rows),
            "remaining_usd": (self.cap - charged - outstanding) / 1e6,
        }

    def reserve(self, task, model, input_tokens, max_output, *, max_calls=None):
        if model not in PRICES or min(input_tokens, max_output) < 0:
            raise BudgetError("Unknown price or invalid token bound")
        price = PRICES[model]
        # Reserve input AND worst-case cache write, plus rounding/headroom.
        amount = math.ceil(
            1.05 * (input_tokens * (price["input"] + price["write"]) + max_output * price["output"])
        )
        ident = uuid.uuid4().hex
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if max_calls is not None:
                calls = db.execute("SELECT COUNT(*) FROM calls").fetchone()[0]
                if calls >= max_calls:
                    raise BudgetError("Generation request limit reached; no new call authorized")
            if db.execute("SELECT 1 FROM calls WHERE state='BOUND_VIOLATION'").fetchone():
                raise BudgetError(
                    "Earlier usage exceeded its reservation; paid continuation stopped"
                )
            used = db.execute("SELECT COALESCE(SUM(COALESCE(charged,reserved)),0) FROM calls")
            if used.fetchone()[0] + amount > self.cap:
                raise BudgetError("Experiment-wide $5 admission ceiling reached")
            db.execute(
                "INSERT INTO calls VALUES (?,?,?,?,NULL,?,?,?)",
                (
                    ident,
                    task,
                    model,
                    amount,
                    "RESERVED",
                    "{}",
                    datetime.now(UTC).isoformat(),
                ),
            )
            db.commit()
        return ident

    def settle(self, ident, usage, *, no_charge=False):
        with self.connect() as db:
            row = db.execute(
                "SELECT model,reserved,charged FROM calls WHERE id=?", (ident,)
            ).fetchone()
            if not row or row[2] is not None:
                raise BudgetError("Unknown/already settled reservation")
            price = PRICES[row[0]]
            if no_charge:
                charged, state = 0, "REJECTED_BEFORE_GENERATION"
            else:
                inp, out = usage.get("input_tokens"), usage.get("output_tokens")
                if not isinstance(inp, int) or not isinstance(out, int) or min(inp, out) < 0:
                    return  # Unknown charge remains fully reserved.
                details = usage.get("input_tokens_details") or {}
                cached = details.get("cached_tokens", 0)
                writes = details.get("cache_write_tokens", 0)
                if not 0 <= cached <= inp or not 0 <= writes <= inp:
                    return
                charged = math.ceil(
                    (inp - cached) * price["input"]
                    + cached * price["cached"]
                    + writes * price["write"]
                    + out * price["output"]
                )
                state = "SETTLED" if charged <= row[1] else "BOUND_VIOLATION"
            db.execute(
                "UPDATE calls SET charged=?,state=?,detail=? WHERE id=?",
                (charged, state, json.dumps(usage), ident),
            )
            db.commit()

    def cache_get(self, key):
        with self.connect() as db:
            row = db.execute("SELECT value FROM cache WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else None

    def cache_put(self, key, value):
        with self.connect() as db:
            db.execute("INSERT OR REPLACE INTO cache VALUES (?,?)", (key, json.dumps(value)))
            db.commit()

    def calls(self):
        with self.connect() as db:
            db.row_factory = sqlite3.Row
            return [dict(row) for row in db.execute("SELECT * FROM calls ORDER BY created")]
