#!/bin/bash
# =============================================================================
# R004 Habit Tracker - Test Script
# =============================================================================
# Runs pytest with coverage reporting
# =============================================================================

cd "$(dirname "$0")/.."

echo "🧪 Running Habit Tracker API tests..."
echo ""

python -m pytest tests/ -v --cov=. --cov-report=term-missing
