#!/bin/bash
# Nexus AI Backend Startup Script

# Change to backend directory
cd "$(dirname "$0")"

echo "🚀 Starting Nexus AI Backend Server"
echo "======================================"
echo "Working directory: $(pwd)"
echo ""

# Check if virtual environment exists
if [ -d "../.venv" ]; then
    echo "✅ Virtual environment found"
    PYTHON_CMD="../.venv/bin/python"
else
    echo "❌ Virtual environment not found at ../.venv"
    echo "Please run: python -m venv ../.venv && source ../.venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found in current directory"
    exit 1
fi

echo "✅ Starting FastAPI server with Portia.ai and Mistral AI integration..."
echo "   Documentation: http://localhost:8000/docs"
echo "   Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
exec $PYTHON_CMD main.py
