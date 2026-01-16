#!/bin/bash
# Script to set up development environment

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up PDF Summarizer development environment...${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies with dev tools
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -e ".[dev]"

# Create necessary directories
echo -e "${YELLOW}Creating data directories...${NC}"
mkdir -p data/uploads

# Copy .env.example to .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
fi

echo -e "${GREEN}Development environment setup complete!${NC}"
echo -e "${YELLOW}To activate the environment, run: source venv/bin/activate${NC}"
echo -e "${YELLOW}To run the server: ./scripts/run.sh${NC}"
echo -e "${YELLOW}To run tests: ./scripts/test.sh${NC}"
