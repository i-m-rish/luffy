#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

cd "$ROOT_DIR"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python 3 was not found. Install it with Homebrew: brew install python"
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Creating local virtual environment..."
  "$PYTHON_BIN" -m venv .venv
fi

source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

echo "Starting Luffy local apps on macOS..."
echo "IGA UI:       http://127.0.0.1:8001/ui"
echo "IGA API docs: http://127.0.0.1:8001/docs"
echo "IdP UI:       http://127.0.0.1:8002/ui"
echo "IdP API docs: http://127.0.0.1:8002/docs"
echo "Press Ctrl+C to stop both apps."

cleanup() {
  echo "Stopping local apps..."
  kill "${IGA_PID:-0}" "${IDP_PID:-0}" 2>/dev/null || true
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

wait
