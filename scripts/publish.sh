#!/usr/bin/env bash
# Publish ulfblk packages to PyPI in topological order.
# Usage: UV_PUBLISH_TOKEN=pypi-xxx bash scripts/publish.sh
#
# Requires: uv (https://docs.astral.sh/uv/)

set -euo pipefail

if [ -z "${UV_PUBLISH_TOKEN:-}" ]; then
  echo "ERROR: UV_PUBLISH_TOKEN not set"
  echo "Usage: UV_PUBLISH_TOKEN=pypi-xxx bash scripts/publish.sh"
  exit 1
fi

BASE="$(cd "$(dirname "$0")/.." && pwd)"
PACKAGES_DIR="$BASE/packages/python"

# Topological order: core first, then packages that depend on core
PACKAGES=(
  "ulfblk-core"
  "ulfblk-db"
  "ulfblk-auth"
  "ulfblk-multitenant"
  "ulfblk-testing"
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
