#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -x .tools/node/bin/node ]]; then
  export PATH="$PWD/.tools/node/bin:$PATH"
fi
export NEXT_TELEMETRY_DISABLED=1
export GHM_UI=preflight
exec npm --prefix frontend run dev
