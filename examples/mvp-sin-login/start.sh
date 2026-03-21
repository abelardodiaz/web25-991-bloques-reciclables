#!/usr/bin/env bash
# Start MVP sin Login - backend + frontend
# Usage: bash examples/mvp-sin-login/start.sh

set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"

BASE="$(cd "$(dirname "$0")" && pwd)"

echo "Starting backend on :8000..."
cd "$BASE/backend"
uv run uvicorn main:app --host 0.0.0.0 --port 8000 &
BACK_PID=$!

echo "Starting frontend on :3000..."
cd "$BASE/frontend"
npx next dev --port 3000 &
FRONT_PID=$!

echo ""
echo "Backend:  http://localhost:8000/docs"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop both"

trap "kill $BACK_PID $FRONT_PID 2>/dev/null" EXIT
wait
