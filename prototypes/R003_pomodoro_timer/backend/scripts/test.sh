#!/usr/bin/env bash
# =============================================================================
# R003 Pomodoro Timer - Test Script
# =============================================================================
# Run tests with coverage
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧪 Running Pomodoro Timer Backend Tests...${NC}"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo -e "${GREEN}📦 Activating virtual environment${NC}"
    source .venv/bin/activate
fi

# Run tests with coverage
echo -e "${GREEN}Running pytest with coverage...${NC}"
pytest --cov=. --cov-report=term-missing --cov-report=html -v

echo -e "${GREEN}✅ Tests complete!${NC}"
echo -e "${YELLOW}📊 Coverage report generated in htmlcov/index.html${NC}"
