#!/bin/bash
# Development script for PDF Summarizer Frontend

cd "$(dirname "$0")/.."

echo "Starting PDF Summarizer Frontend development server..."
echo "API URL: ${NEXT_PUBLIC_API_URL:-http://localhost:8007}"
echo ""

npm run dev
