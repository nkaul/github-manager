import hashlib
import secrets
import time
from dataclasses import dataclass, field
from threading import Lock
from typing import Any


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


@dataclass
class OAuthState:
    browser_hash: str
    verifier: str
    expires_at: float


@dataclass
class Session:
    user: dict[str, Any]
    token: str = field(repr=False)
    scopes: list[str]
    expires_at: float
    csrf_token: str = field(default_factory=lambda: secrets.token_urlsafe(32), repr=False)
    snapshot: dict[str, Any] | None = None
    snapshot_at: float = 0
    report: dict[str, Any] | None = None


class SessionStore:
    """Local single-process, bounded memory. No GitHub tokens are written to disk."""

    def __init__(self, clock=time.monotonic, capacity: int = 100):
        self.clock = clock
        self.capacity = capacity
        self.states: dict[str, OAuthState] = {}
        self.sessions: dict[str, Session] = {}
        self.lock = Lock()

    def _prune(self):
        now = self.clock()
        for mapping in (self.states, self.sessions):
            for key in list(mapping):
                if mapping[key].expires_at <= now:
                    del mapping[key]

    def begin(self, browser_nonce: str, ttl: int) -> tuple[str, str]:
        with self.lock:
            self._prune()
            if len(self.states) >= self.capacity:
                raise ValueError("Too many pending sign-ins; try again shortly")
            state, verifier = secrets.token_urlsafe(32), secrets.token_urlsafe(64)
            self.states[digest(state)] = OAuthState(
                digest(browser_nonce), verifier, self.clock() + ttl
            )
            return state, verifier

    def consume(self, state: str, browser_nonce: str) -> OAuthState | None:
        with self.lock:
            self._prune()
            saved = self.states.get(digest(state))
            if not saved or not secrets.compare_digest(saved.browser_hash, digest(browser_nonce)):
                return None
            return self.states.pop(digest(state))

    def create(self, user: dict, token: str, scopes: list[str], ttl: int) -> str:
        with self.lock:
            self._prune()
            if len(self.sessions) >= self.capacity:
                raise ValueError("Too many local sessions")
            key = secrets.token_urlsafe(48)
            self.sessions[digest(key)] = Session(user, token, scopes, self.clock() + ttl)
            return key

    def get(self, key: str | None) -> Session | None:
        with self.lock:
            self._prune()
            return self.sessions.get(digest(key)) if key else None

    def discard(self, key: str | None):
        with self.lock:
            if key:
                self.sessions.pop(digest(key), None)
