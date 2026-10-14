#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$PWD/.tools/node/bin:$PATH"
export NEXT_TELEMETRY_DISABLED=1
export GHM_UI=demo
mode="${1:---production}"
if [[ "$mode" == "--live-ai" ]]; then
  export DEMO_LIVE_AI=true
  mode=--production
fi
if [[ "$mode" != "--production" && "$mode" != "--dev" ]]; then
  echo "Usage: scripts/dev-demo.sh [--production|--dev|--live-ai]"
  exit 2
fi
if [[ ! -x backend/.venv/bin/uvicorn || ! -d frontend/node_modules ]]; then
  echo "Install the locked backend dev/ai-pretest groups and frontend dependencies first."
  exit 1
fi
if [[ "$mode" == "--production" && ! -f frontend/.next/BUILD_ID ]]; then
  npm --prefix frontend run build
fi
backend/.venv/bin/uvicorn --app-dir backend app.local:app --host 127.0.0.1 --port 8000 --no-access-log &
backend_pid=$!
trap 'kill "$backend_pid" 2>/dev/null || true' EXIT INT TERM
if [[ "$mode" == "--dev" ]]; then
  npm --prefix frontend run dev
else
  npm --prefix frontend run start
fi
