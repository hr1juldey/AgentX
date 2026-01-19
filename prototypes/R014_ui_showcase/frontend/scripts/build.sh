#!/usr/bin/env bash
# =============================================================================
# AGENTX Prototype - Frontend Build Script
# =============================================================================
# Build the Next.js application for production
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "Building Next.js application..."
npm run build

echo ""
echo "Build complete! Output in .next/"
echo "To start production server: npm run start"
