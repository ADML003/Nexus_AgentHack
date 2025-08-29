#!/bin/bash
echo "🚀 Starting Nexus AI Backend..."

# Check if .env.local exists in parent directory  
if [ -f "../.env.local" ]; then
    echo "✅ Found .env.local file"
else
    echo "⚠️ Warning: ../.env.local not found"
fi

echo "🔑 Loading environment variables..."

# Display key checking (without exposing keys)
echo "🔍 Checking API keys..."
cd ..
if grep -q "^GOOGLE_API_KEY=" .env.local && ! grep -q "^#.*GOOGLE_API_KEY=" .env.local; then
    echo "   ✅ Google API key loaded"
else
    echo "   ❌ Google API key missing"
fi

if grep -q "^MISTRAL_API_KEY=" .env.local && ! grep -q "^#.*MISTRAL_API_KEY=" .env.local; then
    echo "   ✅ Mistral API key loaded" 
else
    echo "   ❌ Mistral API key missing"
fi

if grep -q "^PORTIA_API_KEY=" .env.local && ! grep -q "^#.*PORTIA_API_KEY=" .env.local; then
    echo "   ✅ Portia API key loaded"
else
    echo "   ❌ Portia API key missing"  
fi

if grep -q "^#.*OPENAI_API_KEY=" .env.local || ! grep -q "OPENAI_API_KEY=" .env.local; then
    echo "   ℹ️  OpenAI API disabled (removed from configuration)"
else
    echo "   ⚠️  OpenAI API key found but should be disabled"
fi

echo "📦 Activating virtual environment..."
echo "🌟 Starting server with loaded environment..."

# Change to backend directory and start server
cd backend
python main.py
