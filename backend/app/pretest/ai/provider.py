import json
import re
import time

import httpx2
from langchain_openai import ChatOpenAI
from langsmith import tracing_context

from app.pretest.ai.storage import PRICE_DATE, BudgetError, digest

PROMPT_VERSION = "phase05-v1"
COUNT_KEYS = {"model", "input", "instructions", "text", "reasoning"}


class ProviderBlocked(ValueError):
    pass


class BudgetedProvider:
    """Guard the actual LangChain HTTP payload before any generation request."""

    def __init__(self, settings, ledger, *, transport=None):
        settings.require_live(True)
        self.settings, self.ledger = settings, ledger
        self.last = {}
        self.counter = httpx2.Client(
            timeout=settings.ai_pretest_request_timeout_seconds,
            trust_env=False,
            transport=transport,
        )
        self.client = httpx2.Client(
            timeout=settings.ai_pretest_request_timeout_seconds,
            trust_env=False,
            transport=transport,
            event_hooks={"request": [self.before], "response": [self.after]},
        )

    def close(self):
        self.client.close()
        self.counter.close()

    def before(self, request):
        if str(request.url) != "https://api.openai.com/v1/responses" or request.method != "POST":
            raise ProviderBlocked("Unexpected provider destination/operation")
        payload = json.loads(request.content)
        if (
            payload.get("model") not in self.settings.models
            or payload.get("store") is not False
            or payload.get("tools")
            or payload.get("stream")
            or payload.get("background")
            or payload.get("previous_response_id")
            or payload.get("conversation")
            or payload.get("service_tier") != "default"
        ):
            raise ProviderBlocked("Unapproved stateful/tool/tier request")
        maximum = payload.get("max_output_tokens")
        if not isinstance(maximum, int) or not 0 < maximum <= self.last["max_output"]:
            raise ProviderBlocked("Missing/excessive output ceiling")
        count_body = {k: v for k, v in payload.items() if k in COUNT_KEYS}
        response = self.counter.post(
            "https://api.openai.com/v1/responses/input_tokens",
            json=count_body,
            headers={
                "Authorization": request.headers["authorization"],
                "Content-Type": "application/json",
            },
        )
        self.last["count_http_status"] = response.status_code
        if response.status_code != 200:
            self.last["provider_error_code"] = self.error_code(response)
            raise ProviderBlocked(f"Token-count endpoint HTTP {response.status_code}")
        count = response.json().get("input_tokens")
        if not isinstance(count, int) or count < 0 or count > self.last["max_input"]:
            raise ProviderBlocked("Input/schema token ceiling exceeded or count unavailable")
        self.last["counted_input_tokens"] = count
        reservation = self.ledger.reserve(
            self.last["task"],
            payload["model"],
            count,
            maximum,
            max_calls=self.settings.ai_pretest_max_generation_calls,
        )
        self.last["reservation"] = reservation
        request.extensions["phase05_reservation"] = reservation

    @staticmethod
    def error_code(response):
        try:
            error = response.json().get("error", {})
            value = error.get("code") or error.get("type")
            if isinstance(value, str) and re.fullmatch(r"[a-z_]{1,64}", value):
                return value
            message = error.get("message", "").casefold()
            if any(word in message for word in ("quota", "billing", "credit")):
                return "QUOTA_OR_BILLING"
            if "rate limit" in message:
                return "RATE_LIMIT"
            return "UNCLASSIFIED_PROVIDER_ERROR"
        except (ValueError, AttributeError):
            return "NON_JSON_PROVIDER_ERROR"

    def after(self, response):
        response.read()
        reservation = response.request.extensions.get("phase05_reservation")
        self.last["http_status"] = response.status_code
        self.last["request_id"] = response.headers.get("x-request-id")
        if not reservation:
            raise ProviderBlocked("Generation has no spending reservation")
        if 200 <= response.status_code < 300:
            body = response.json()
            usage = body.get("usage") or {}
            self.last.update(
                {
                    "usage": usage,
                    "returned_model": body.get("model"),
                    "response_status": body.get("status"),
                    "response_id": body.get("id"),
                }
            )
            self.ledger.settle(reservation, usage)
        elif response.status_code in {400, 401, 403, 404, 422, 429}:
            self.last["provider_error_code"] = self.error_code(response)
            self.last["retry_after"] = response.headers.get("retry-after")
            self.ledger.settle(reservation, {}, no_charge=True)
        # Other statuses/timeouts retain their maximum reservation as uncertain.

    def invoke(
        self,
        model,
        task,
        schema,
        system,
        evidence,
        validator,
        *,
        fresh=False,
        max_input=None,
        max_output=None,
    ):
        if (
            evidence.get("source")
            not in {
                "SYNTHETIC",
                "PUBLIC_GITHUB",
                "PUBLIC_AND_SYNTHETIC",
            }
            or evidence.get("private") is not False
        ):
            return {
                "requested_model": model,
                "task": task,
                "status": "BLOCKED",
                "evidence": "POLICY",
                "error_type": "UnapprovedEvidence",
                "seconds": 0,
            }
        taxonomy = task.startswith("taxonomy")
        max_input = max_input or (
            self.settings.ai_pretest_taxonomy_max_input_tokens
            if taxonomy
            else self.settings.ai_pretest_classification_max_input_tokens
        )
        max_output = max_output or (
            self.settings.ai_pretest_taxonomy_max_output_tokens
            if taxonomy
            else self.settings.ai_pretest_classification_max_output_tokens
        )
        effort = (
            self.settings.openai_taxonomy_reasoning_effort
            if taxonomy
            else self.settings.openai_classification_reasoning_effort
        )
        key = digest(
            {
                "model": model,
                "task": task,
                "prompt_version": PROMPT_VERSION,
                "system": system,
                "evidence": evidence,
                "schema": schema.model_json_schema(),
                "effort": effort,
                "max_input": max_input,
                "max_output": max_output,
                "privacy": "public_and_synthetic-v1",
                "store": False,
                "tier": "default",
            }
        )
        cached = None if fresh else self.ledger.cache_get(key)
        if cached:
            parsed = validator(schema.model_validate(cached["result"]))
            return {**cached, "result": parsed.model_dump(), "evidence": "REPLAY", "cache_key": key}
        self.last = {
            "task": task,
            "requested_model": model,
            "max_input": max_input,
            "max_output": max_output,
            "price_date": PRICE_DATE,
        }
        started = time.monotonic()
        # Explicit method avoids a fallback to function calling/unconstrained JSON.
        model_instance = ChatOpenAI(
            model=model,
            api_key=self.settings.openai_api_key,
            base_url="https://api.openai.com/v1",
            use_responses_api=True,
            store=False,
            service_tier="default",
            reasoning_effort=effort,
            max_tokens=max_output,
            max_retries=0,
            timeout=self.settings.ai_pretest_request_timeout_seconds,
            http_client=self.client,
        )
        runnable = model_instance.with_structured_output(
            schema,
            method="json_schema",
            strict=True,
            include_raw=True,
        )
        try:
            with tracing_context(enabled=False):
                response = runnable.invoke(
                    [
                        ("system", system),
                        ("human", json.dumps(evidence, ensure_ascii=False)),
                    ]
                )
            if response.get("parsing_error") or response.get("parsed") is None:
                raise ValueError("Refused, incomplete or unparseable structured response")
            parsed = validator(response["parsed"])
            if self.last.get("response_status") != "completed":
                raise ValueError("Incomplete provider response")
            usage = self.last.get("usage") or {}
            if not all(isinstance(usage.get(k), int) for k in ("input_tokens", "output_tokens")):
                raise ProviderBlocked("Usage unavailable; reservation retained")
            if usage["input_tokens"] > max_input or usage["output_tokens"] > max_output:
                raise ProviderBlocked("Actual usage exceeded configured token ceilings")
            result = {
                **self.last,
                "status": "PASS",
                "evidence": "LIVE_PROVIDER",
                "result": parsed.model_dump(),
                "cache_key": key,
                "seconds": round(time.monotonic() - started, 3),
            }
            self.ledger.cache_put(key, result)
            return result
        except Exception as error:
            # Error messages may echo credentials or submitted content; never persist them.
            cause = error
            while cause.__cause__:
                cause = cause.__cause__
            result = {
                **self.last,
                "status": "BLOCKED"
                if isinstance(
                    cause,
                    (
                        ProviderBlocked,
                        BudgetError,
                    ),
                )
                or self.last.get("http_status") in {401, 403, 404, 429}
                else "FAIL",
                "error_type": type(cause).__name__,
                "evidence": "LIVE_PROVIDER",
                "seconds": round(time.monotonic() - started, 3),
                "cache_key": key,
            }
            return result
