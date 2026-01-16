#!/bin/bash

# Habit Tracker Frontend - Development Script

echo "Starting Habit Tracker Frontend..."
echo "API URL: ${NEXT_PUBLIC_API_URL:-http://localhost:8004}"
echo ""

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start development server
npm run dev
