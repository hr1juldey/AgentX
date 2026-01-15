#!/usr/bin/env bash
# =============================================================================
# AGENTX Prototype - Backend Lint Script
# =============================================================================
# Run ruff for linting and formatting
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "Running ruff linter..."
ruff check .

echo ""
echo "Running ruff formatter check..."
ruff format --check .

echo ""
echo "To auto-fix issues, run:"
echo "  ruff check . --fix"
echo "  ruff format ."
