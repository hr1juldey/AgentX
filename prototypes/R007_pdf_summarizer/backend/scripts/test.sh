#!/bin/bash
# Script to run tests for the PDF Summarizer API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Running tests for PDF Summarizer API...${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -e ".[test]"

# Run tests with pytest
echo -e "${GREEN}Running tests...${NC}"
pytest tests/ -v --tb=short

echo -e "${GREEN}Tests completed!${NC}"
