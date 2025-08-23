#!/bin/bash
echo "🚀 Starting Nexus Portia Backend..."

# Change to the backend directory
cd /Users/ADML/Desktop/Nexus/backend

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found!"
    exit 1
fi

# Check if .env.local exists
if [ ! -f "../.env.local" ]; then
    echo "⚠️ Warning: ../.env.local not found - API keys may not be loaded"
fi

# Start the server
echo "🔧 Starting Python server..."
python main.py
