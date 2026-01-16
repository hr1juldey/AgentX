#!/usr/bin/env bash
# =============================================================================
# R003 Pomodoro Timer - Run Script
# =============================================================================
# Start the development server
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🍅 Starting Pomodoro Timer Backend...${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found, copying from .env.example${NC}"
    cp .env.example .env
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo -e "${GREEN}📦 Activating virtual environment${NC}"
    source .venv/bin/activate
fi

# Run the server
echo -e "${GREEN}🚀 Starting server on http://0.0.0.0:8003${NC}"
python main.py
