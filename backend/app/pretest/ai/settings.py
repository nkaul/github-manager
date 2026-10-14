import os
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config import BACKEND_ROOT, REPO_ROOT

MODELS = frozenset({"gpt-6.1-sol", "gpt-6-luna", "gpt-6-astra"})
PRIVATE_ROOT = REPO_ROOT / "docs/validation/private"


class AISettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_ROOT / ".env", extra="ignore")

    app_env: Literal["local"] = "local"
    openai_api_key: SecretStr = Field(default=SecretStr(""), repr=False)
    openai_taxonomy_model: str = "gpt-6.1-sol"
    openai_classification_model: str = "gpt-6-luna"
    openai_taxonomy_comparison_model: str = "gpt-6-astra"
    openai_classification_comparison_model: str = "gpt-6.1-sol"
    openai_taxonomy_reasoning_effort: Literal["low", "medium", "high"] = "low"
    openai_classification_reasoning_effort: Literal["low", "medium", "high"] = "low"
    ai_pretest_live_enabled: bool = False
    ai_pretest_allowed_data: Literal["public_and_synthetic"] = "public_and_synthetic"
    ai_pretest_budget_usd: float = Field(default=5, gt=0, le=5)
    ai_pretest_persistence: Literal["sqlite"] = "sqlite"
    ai_pretest_state_directory: Path = PRIVATE_ROOT / "ai-pretest"
    ai_pretest_classification_max_input_tokens: int = Field(default=2000, gt=0, le=2000)
    ai_pretest_classification_max_output_tokens: int = Field(default=2048, gt=0, le=2048)
    ai_pretest_taxonomy_max_input_tokens: int = Field(default=12000, gt=0, le=12000)
    ai_pretest_taxonomy_max_output_tokens: int = Field(default=4096, gt=0, le=4096)
    ai_pretest_request_timeout_seconds: int = Field(default=60, ge=1, le=60)
    ai_pretest_max_retries: int = Field(default=1, ge=0, le=1)
    # The user authorized a further <=20 requests after the initial 14 attempts.
    ai_pretest_max_generation_calls: int = Field(default=14, ge=1, le=34)

    @model_validator(mode="after")
    def validate_scope(self):
        for model in self.models:
            if model not in MODELS:
                raise ValueError("Model outside the approved comparison allowlist")
        directory = self.ai_pretest_state_directory
        if not directory.is_absolute():
            directory = BACKEND_ROOT / directory
        directory = directory.resolve()
        if not directory.is_relative_to(PRIVATE_ROOT.resolve()):
            raise ValueError("AI experiment state must stay in the ignored private directory")
        self.ai_pretest_state_directory = directory
        return self

    @property
    def models(self):
        return list(
            dict.fromkeys(
                [
                    self.openai_taxonomy_model,
                    self.openai_classification_model,
                    self.openai_taxonomy_comparison_model,
                    self.openai_classification_comparison_model,
                ]
            )
        )

    def require_live(self, explicit_flag: bool):
        if not explicit_flag or not self.ai_pretest_live_enabled:
            raise ValueError("Live calls require --live and AI_PRETEST_LIVE_ENABLED=true")
        if not self.openai_api_key.get_secret_value().strip():
            raise ValueError("Missing local OpenAI API key")
        for key in ("OPENAI_BASE_URL", "OPENAI_API_BASE", "LANGSMITH_ENDPOINT"):
            if os.getenv(key):
                raise ValueError("Inherited provider/tracing destination is not authorized")
        for key in ("LANGSMITH_TRACING", "LANGCHAIN_TRACING_V2"):
            if os.getenv(key, "false").lower() not in {"false", "0", ""}:
                raise ValueError("Remote tracing is outside the approved data scope")
