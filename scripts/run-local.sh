#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

python -m pip install -r requirements-dev.txt

echo "Starting Luffy local apps..."
echo "IGA UI: http://127.0.0.1:8001/ui"
echo "IGA API docs: http://127.0.0.1:8001/docs"
echo "IdP UI: http://127.0.0.1:8002/ui"
echo "IdP API docs: http://127.0.0.1:8002/docs"
echo "Press Ctrl+C to stop both apps."

cleanup() {
  echo "Stopping local apps..."
  kill "${IGA_PID:-0}" "${IDP_PID:-0}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

(
  cd "$ROOT_DIR/apps/iga-service/src"
  uvicorn fastapi_app:app --reload --port 8001
) &
IGA_PID=$!

(
  cd "$ROOT_DIR/apps/idp-service/src"
  uvicorn fastapi_app:app --reload --port 8002
) &
IDP_PID=$!

wait
