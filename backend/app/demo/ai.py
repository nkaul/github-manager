"""Reuse proven inference checks; add a separate durable Phase 0.9 HTTP allowance."""

import json
import time
from urllib.parse import urlsplit

from pydantic import Field

from app.demo.allowance import ApplicationLedger, RequestAllowance  # re-export for existing callers
from app.pretest.ai.provider import BudgetedProvider, ProviderBlocked
from app.pretest.ai.settings import AISettings
from app.pretest.ai.storage import Ledger, private_json


class DemoAISettings(AISettings):
    # The frozen Phase 0.5 settings remain unchanged. ApplicationLedger enforces
    # the current audited generation allowance at reservation time.
    ai_pretest_max_generation_calls: int = Field(default=44, ge=1, le=44)


class DemoProvider(BudgetedProvider):
    def __init__(self, settings, ledger, *, mode, authorized=lambda: True, transport=None):
        super().__init__(settings, ledger, transport=transport)
        self.allowance = RequestAllowance(ledger)
        self.mode = mode
        self.authorized = authorized
        self.counter.event_hooks["request"] = [self.guard]
        self.counter.event_hooks["response"] = [self.record_http]
        # Guard generation before the old hook performs its count request.
        self.client.event_hooks["request"] = [self.guard, self.before]
        self.client.event_hooks["response"] = [self.record_http, self.after]

    def bind_budget(self, plan_id):
        self.ledger.plan_id = plan_id

    def guard(self, request):
        if self.mode != "LIVE":
            raise ProviderBlocked("No valid cached result; select Live AI for a new request")
        if not self.authorized():
            raise ProviderBlocked("Connection or workspace changed; request cancelled")
        url = urlsplit(str(request.url))
        if url.scheme != "https" or url.netloc != "api.openai.com" or request.method != "POST":
            raise ProviderBlocked("Unapproved provider destination")
        request.extensions["phase09_http"] = self.allowance.take(url.path)

    def record_http(self, response):
        key = response.request.extensions.get("phase09_http")
        if key:
            self.allowance.record(key, response.status_code)

    def invoke(self, *args, **kwargs):
        result = super().invoke(*args, **kwargs)
        if result["status"] != "PASS" and not result.get("count_http_status"):
            result["evidence"] = "POLICY"
        private_json(
            self.settings.ai_pretest_state_directory
            / "phase09-calls"
            / (str(time.time_ns()) + ".local.json"),
            result,
        )
        return result


def open_provider(mode, authorized):
    settings = DemoAISettings(ai_pretest_live_enabled=True, ai_pretest_max_generation_calls=44)
    ledger = ApplicationLedger(settings.ai_pretest_state_directory, settings.ai_pretest_budget_usd)
    return DemoProvider(settings, ledger, mode=mode, authorized=authorized)


def budget_summary(ledger=None):
    try:
        settings = AISettings()
        ledger = ledger or Ledger(
            settings.ai_pretest_state_directory, settings.ai_pretest_budget_usd
        )
        allowance = RequestAllowance(ledger)
        from app.demo.run_budget import RunBudgets

        runs = RunBudgets(ledger).summary()
        return {
            **ledger.summary(),
            **allowance.policy(),
            "run_budget": runs,
            "remaining_usd": runs["available_usd"],
        }
    except (ValueError, OSError, json.JSONDecodeError):
        return {
            "unavailable": True,
            "message": "Existing AI ledger/key setup required; no automatic initialization",
        }
