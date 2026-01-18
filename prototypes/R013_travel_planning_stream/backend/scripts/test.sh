#!/usr/bin/env bash
# =============================================================================
# AGENTX Prototype - Backend Test Script
# =============================================================================
# Run pytest tests with coverage
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "Running tests with coverage..."
pytest tests/ --cov=. --cov-report=term-missing --cov-report=html

echo ""
echo "Coverage report generated in htmlcov/index.html"
