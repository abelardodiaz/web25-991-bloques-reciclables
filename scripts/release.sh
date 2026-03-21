#!/usr/bin/env bash
# Release pipeline for ulfblk monorepo.
# Detects changes, bumps versions, generates changelogs, publishes to PyPI.
#
# Usage:
#   bash scripts/release.sh              # Dry run (detect only)
#   bash scripts/release.sh --publish    # Full release: bump + commit + tag + publish
#
# Requires: UV_PUBLISH_TOKEN in environment or .env file

set -euo pipefail

BASE="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BASE"

# Load token from .env if not set
if [ -z "${UV_PUBLISH_TOKEN:-}" ] && [ -f .env ]; then
    UV_PUBLISH_TOKEN=$(grep UV_PUBLISH_TOKEN .env 2>/dev/null | cut -d= -f2 || true)
    export UV_PUBLISH_TOKEN
fi

PUBLISH=false
if [ "${1:-}" = "--publish" ]; then
    PUBLISH=true
fi

echo "=== ulfblk Release Pipeline ==="
echo ""

# Step 1: Detect changes
echo "Step 1: Detecting changes..."
python scripts/version.py --detect
echo ""

if [ "$PUBLISH" = false ]; then
    echo "Dry run complete. Run with --publish to execute the full release."
    exit 0
fi

# Step 2: Apply version bumps
echo "Step 2: Applying version bumps..."
python scripts/version.py --apply
echo ""

# Step 3: Commit
echo "Step 3: Committing version bumps..."
git add packages/python/*/pyproject.toml packages/python/*/CHANGELOG.md
git commit -m "chore(release): bump package versions

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
echo ""

# Step 4: Tag
echo "Step 4: Creating tags..."
python scripts/version.py --tag
echo ""

# Step 5: Publish to PyPI
if [ -z "${UV_PUBLISH_TOKEN:-}" ]; then
    echo "WARNING: UV_PUBLISH_TOKEN not set. Skipping PyPI publish."
    echo "Set it in .env or environment, then run: bash scripts/publish.sh"
else
    echo "Step 5: Publishing to PyPI..."
    bash scripts/publish.sh
fi

echo ""
echo "=== Release complete ==="
echo "Push commits and tags: git push && git push --tags"
