#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

python -m pip install -r requirements-dev.txt

echo "Starting Luffy local apps..."
echo "IGA UI:       http://127.0.0.1:8001/ui"
echo "IGA API docs: http://127.0.0.1:8001/docs"
echo "IdP UI:       http://127.0.0.1:8002/ui"
echo "IdP API docs: http://127.0.0.1:8002/docs"
echo "ZSP App UI:   http://127.0.0.1:8003"
echo "ZSP API docs: http://127.0.0.1:8003/docs"
echo "Press Ctrl+C to stop all apps."

cleanup() {
  echo "Stopping local apps..."
  kill "${IGA_PID:-0}" "${IDP_PID:-0}" "${ZSP_PID:-0}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

(
  cd "$ROOT_DIR/apps/iga-service/src"
  python -m uvicorn fastapi_app:app --reload --host 127.0.0.1 --port 8001
) &
IGA_PID=$!

(
  cd "$ROOT_DIR/apps/idp-service/src"
  python -m uvicorn fastapi_app:app --reload --host 127.0.0.1 --port 8002
) &
IDP_PID=$!

(
  cd "$ROOT_DIR/apps/zsp-jit-app/src"
  python -m uvicorn fastapi_app:app --reload --host 127.0.0.1 --port 8003
) &
ZSP_PID=$!

wait
