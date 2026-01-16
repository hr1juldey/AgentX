#!/bin/bash
# Run tests

cd "$(dirname "$0")/.."
echo "🧪 Running tests..."
pytest tests/ -v --tb=short
