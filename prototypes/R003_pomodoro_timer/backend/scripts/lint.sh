#!/usr/bin/env bash
# =============================================================================
# R003 Pomodoro Timer - Lint Script
# =============================================================================
# Run ruff linter and formatter
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔍 Linting Pomodoro Timer Backend...${NC}"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo -e "${GREEN}📦 Activating virtual environment${NC}"
    source .venv/bin/activate
fi

# Run ruff check
echo -e "${GREEN}Running ruff check...${NC}"
if command -v ruff &> /dev/null; then
    ruff check .
    echo -e "${GREEN}✅ No lint errors found!${NC}"
else
    echo -e "${YELLOW}⚠️  Ruff not installed. Install with: pip install ruff${NC}"
fi

# Run ruff format check
echo -e "${GREEN}Checking code formatting...${NC}"
if command -v ruff &> /dev/null; then
    ruff format --check .
    echo -e "${GREEN}✅ Code formatting is correct!${NC}"
else
    echo -e "${YELLOW}⚠️  Ruff not installed. Install with: pip install ruff${NC}"
fi
