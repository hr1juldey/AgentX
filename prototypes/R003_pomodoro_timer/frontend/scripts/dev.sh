#!/usr/bin/env bash
# =============================================================================
# AGENTX Prototype - Frontend Dev Script
# =============================================================================
# Start the Next.js development server
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo "Starting Next.js development server..."
npm run dev
