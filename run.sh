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

# Load environment variables from .env.local
echo "🔑 Loading environment variables..."
export $(grep -v '^#' .env.local | xargs)

# Verify key API keys are loaded
echo "🔍 Checking API keys..."
if [ -n "$OPENAI_API_KEY" ]; then
    echo "   ✅ OpenAI API key loaded"
else
    echo "   ❌ OpenAI API key missing"
fi

if [ -n "$GOOGLE_API_KEY" ]; then
    echo "   ✅ Google API key loaded"
else
    echo "   ❌ Google API key missing"
fi

if [ -n "$MISTRAL_API_KEY" ]; then
    echo "   ✅ Mistral API key loaded"
else
    echo "   ❌ Mistral API key missing"
fi

if [ -n "$PORTIA_API_KEY" ]; then
    echo "   ✅ Portia API key loaded"
else
    echo "   ❌ Portia API key missing"
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "⚠️  No virtual environment found, using system Python"
fi

# Navigate to backend
cd backend

# Start the server
echo "🌟 Starting server with loaded environment..."
python main.py
