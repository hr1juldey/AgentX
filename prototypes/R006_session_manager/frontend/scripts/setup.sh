#!/bin/bash

# Session Manager Frontend Setup Script
# This script sets up the Next.js frontend for R006 Session Manager

set -e

echo "🚀 Setting up Session Manager Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

echo "✅ Node.js version: $(node --version)"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
    echo "📝 Creating .env.local from example..."
    cp .env.local.example .env.local
fi

echo "✅ Setup complete!"
echo ""
echo "📋 Available commands:"
echo "  npm run dev      - Start development server"
echo "  npm run build    - Build for production"
echo "  npm run start    - Start production server"
echo "  npm run lint     - Run ESLint"
echo ""
echo "🎯 Development server will run on http://localhost:3006"
echo "📡 API configured at: $NEXT_PUBLIC_API_URL"
