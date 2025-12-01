#!/usr/bin/env bash
set -euo pipefail

# Replace literal "$PORT" arguments with the actual environment value so Railway's
# non-shell start command stops failing with "$PORT is not a valid integer".
RESOLVED_PORT="${PORT:-8000}"
ARGS=()
for arg in "$@"; do
  if [[ "$arg" == "\$PORT" || "$arg" == "\${PORT}" ]]; then
    ARGS+=("${RESOLVED_PORT}")
  else
    ARGS+=("$arg")
  fi
done

exec python -m uvicorn "${ARGS[@]}"
