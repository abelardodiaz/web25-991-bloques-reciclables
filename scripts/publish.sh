#!/usr/bin/env bash
# Publish ulfblk packages to PyPI in topological order.
# Usage: UV_PUBLISH_TOKEN=pypi-xxx bash scripts/publish.sh
#
# Requires: uv (https://docs.astral.sh/uv/)

set -euo pipefail

BASE="$(cd "$(dirname "$0")/.." && pwd)"
PACKAGES_DIR="$BASE/packages/python"

# Load token from .env if not set
if [ -z "${UV_PUBLISH_TOKEN:-}" ] && [ -f "$BASE/.env" ]; then
  UV_PUBLISH_TOKEN=$(grep UV_PUBLISH_TOKEN "$BASE/.env" 2>/dev/null | cut -d= -f2 || true)
  export UV_PUBLISH_TOKEN
fi

if [ -z "${UV_PUBLISH_TOKEN:-}" ]; then
  echo "ERROR: UV_PUBLISH_TOKEN not set (check .env or environment)"
  exit 1
fi

# Topological order: core first, then deps, then everything else
PACKAGES=(
  "ulfblk-core"
  "ulfblk-db"
  "ulfblk-auth"
  "ulfblk-multitenant"
  "ulfblk-testing"
  "ulfblk-redis"
  "ulfblk-gateway"
  "ulfblk-channels"
  "ulfblk-billing"
  "ulfblk-notifications"
  "ulfblk-automation"
  "ulfblk-ai-rag"
  "ulfblk-ci-github"
  "ulfblk-ci-gitlab"
  "ulfblk-docker-dev"
  "ulfblk-docker-prod"
)

echo "Publishing ${#PACKAGES[@]} packages to PyPI..."
echo ""

for pkg in "${PACKAGES[@]}"; do
  pkg_dir="$PACKAGES_DIR/$pkg"
  if [ ! -d "$pkg_dir" ]; then
    echo "SKIP: $pkg (directory not found)"
    continue
  fi

  echo "--- $pkg ---"

  # Clean previous builds
  rm -rf "$pkg_dir/dist"

  # Build
  echo "  Building..."
  (cd "$pkg_dir" && uv build --quiet)

  # Publish
  echo "  Publishing..."
  (cd "$pkg_dir" && uv publish dist/* --token "$UV_PUBLISH_TOKEN")

  echo "  Done: $pkg"
  echo ""
done

echo "All packages published."
