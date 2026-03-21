#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")"
echo "Starting bot-citas on :8000..."
uv run uvicorn main:app --host 0.0.0.0 --port 8000
