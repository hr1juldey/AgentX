#!/usr/bin/env bash
# =============================================================================
# AGENTX Prototype - Frontend Lint Script
# =============================================================================
# Run ESLint and TypeScript checks
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "Running ESLint..."
npm run lint

echo ""
echo "Linting complete!"
