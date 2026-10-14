"""Isolated recording app: test identity/inventory, actual product services and optional real AI."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.local import LocalSettings, create_local_app  # noqa: E402
from app.demo.ai import open_provider  # noqa: E402
from tests.demo.fixtures import Adapter, Provider  # noqa: E402

DATABASE = Path(os.environ["RECORDING_DATABASE"])


def recording_provider(mode, authorized):
    # Fixture automation is explicitly labeled in the video and all returned outcomes.
    # It exercises the real 90-second scheduler without exceeding the existing cap.
    if os.getenv("RECORDING_FIXTURE_AI") == "1" or DATABASE.with_suffix(".fixture-ai").exists():
        return Provider(mode, authorized)
    return open_provider(mode, authorized)


app = create_local_app(
    LocalSettings(
        _env_file=None,
        github_client_id="recording-fixture",
        github_client_secret="recording-fixture",
        app_origin="http://127.0.0.1:3000",
        demo_live_ai=True,
    ),
    adapter=Adapter(),
    db_path=DATABASE,
    provider_factory=recording_provider,
)
