#!/usr/bin/env bash
# Start EduSync backend + frontend
# Backend: http://localhost:8000/docs
# Frontend: http://localhost:3000
# Admin: http://localhost:3000/admin

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Starting EduSync backend..."
cd "$SCRIPT_DIR"
uv run uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Starting EduSync frontend..."
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "EduSync running:"
echo "  Backend:  http://localhost:8000/docs"
echo "  Frontend: http://localhost:3000"
echo "  Admin:    http://localhost:3000/admin"
echo ""
echo "Press Ctrl+C to stop"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
