#!/bin/bash
# =============================================================================
# R004 Habit Tracker - Run Script
# =============================================================================
# Starts the FastAPI server with hot reload
# =============================================================================

cd "$(dirname "$0")/.."

echo "🚀 Starting Habit Tracker API server..."
echo "📍 API will be available at: http://0.0.0.0:8004"
echo "📖 Docs at: http://0.0.0.0:8004/docs"
echo ""

python -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload
