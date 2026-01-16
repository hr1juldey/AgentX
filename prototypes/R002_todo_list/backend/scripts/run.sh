#!/usr/bin/env bash
# =============================================================================
# R002 Todo List - Backend Run Script
# =============================================================================
# Start the FastAPI development server
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Install dependencies if needed
if [ ! -d ".venv" ]; then
    echo "Installing dependencies..."
    uv pip install -e .
fi

# Create data directory if it doesn't exist
mkdir -p data

# Run the server
echo "Starting FastAPI server on port 8002..."
python main.py
