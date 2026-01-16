#!/usr/bin/env bash
# =============================================================================
# R002 Todo List - Backend Test Script
# =============================================================================
# Run pytest tests with coverage
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

echo "Running tests with coverage..."
pytest --cov=. --cov-report=term-missing --cov-report=html tests/

echo "✅ Tests completed!"
