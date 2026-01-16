#!/usr/bin/env bash
# =============================================================================
# R002 Todo List - Backend Lint Script
# =============================================================================
# Run ruff linter and formatter
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

echo "Running ruff linter..."
ruff check .

echo "Running ruff formatter check..."
ruff format --check .

echo "✅ Linting completed!"
