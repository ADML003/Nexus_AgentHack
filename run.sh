#!/bin/bash

# Nexus AI Backend Startup Script
echo "🚀 Starting Nexus AI Backend..."

# Navigate to project root
cd "$(dirname "$0")"

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "❌ Error: .env.local file not found!"
    echo "Please make sure .env.local exists with your API keys"
    exit 1
fi

echo "✅ Found .env.local file"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "⚠️  No virtual environment found, using system Python"
fi

# Navigate to backend
cd backend

# Start the server (API keys will be loaded from .env.local by python-dotenv)
echo "🌟 Starting server..."
python main.py
