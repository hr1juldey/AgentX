#!/bin/bash
# Install dependencies

cd "$(dirname "$0")/.."
echo "📦 Installing dependencies..."
pip install -e .
