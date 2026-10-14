#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../backend"
if [[ ! -x .venv/bin/uvicorn ]]; then
  echo "Run uv sync --project backend --frozen from the repository root first."
  exit 1
fi
exec .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
