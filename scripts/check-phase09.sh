#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$PWD/.tools/node/bin:$PATH"
export NEXT_TELEMETRY_DISABLED=1
export PLAYWRIGHT_BROWSERS_PATH="$PWD/.tools/playwright"
(cd backend && .venv/bin/ruff check app tests)
(cd backend && .venv/bin/pytest -q)
npm --prefix frontend run lint
npm --prefix frontend run typecheck
GHM_UI=demo npm --prefix frontend run build
npm --prefix frontend run test:regression
npm --prefix frontend run test:demo
