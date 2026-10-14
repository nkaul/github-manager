#!/usr/bin/env bash
set -euo pipefail
TASK_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$TASK_REPO_ROOT"
backend/.venv/bin/ruff check backend
backend/.venv/bin/python -m pytest backend/tests/pretest -q
