from pathlib import Path
from urllib.parse import urlsplit

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_env: str = "local"
    app_origin: str = "http://127.0.0.1:3000"
    github_client_id: str = ""
    github_client_secret: str = Field(default="", repr=False)
    github_scopes: str = "read:user repo read:org notifications"
    github_api_version: str = "2026-03-10"
    session_ttl_seconds: int = Field(default=3600, ge=60, le=28800)
    session_warning_seconds: int = Field(default=120, ge=10, le=300)
    github_sync_timeout_seconds: int = Field(default=300, ge=30, le=1800)
    oauth_state_ttl_seconds: int = Field(default=600, ge=30, le=600)
    reports_directory: Path = REPO_ROOT / "docs/validation/private"
    github_fixtures_file: Path | None = None

    @model_validator(mode="after")
    def local_only(self):
        origin = urlsplit(self.app_origin)
        if (
            self.app_env != "local"
            or origin.scheme != "http"
            or origin.hostname not in {"127.0.0.1", "localhost", "::1"}
            or origin.username
            or origin.password
            or origin.path not in {"", "/"}
            or origin.query
            or origin.fragment
        ):
            raise ValueError("Phase 0 runs only on an explicit loopback HTTP origin")
        self.app_origin = self.app_origin.rstrip("/")
        if not self.reports_directory.is_absolute():
            self.reports_directory = (BACKEND_ROOT / self.reports_directory).resolve()
        if self.github_fixtures_file and not self.github_fixtures_file.is_absolute():
            self.github_fixtures_file = (BACKEND_ROOT / self.github_fixtures_file).resolve()
        return self

    @property
    def callback_url(self) -> str:
        return f"{self.app_origin}/api/v1/auth/github/callback"

    @property
    def oauth_configured(self) -> bool:
        return bool(self.github_client_id.strip() and self.github_client_secret.strip())
