#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -x .tools/node/bin/node ]]; then
  export PATH="$PWD/.tools/node/bin:$PATH"
fi
if [[ -d .tools/playwright ]]; then
  export PLAYWRIGHT_BROWSERS_PATH="$PWD/.tools/playwright"
fi
export NEXT_TELEMETRY_DISABLED=1
backend/.venv/bin/ruff check backend
backend/.venv/bin/ruff format --check backend
backend/.venv/bin/pytest backend/tests/pretest -q
npm --prefix frontend run lint
npm --prefix frontend run build
npm --prefix frontend run typecheck
npm --prefix frontend run test:pretest
