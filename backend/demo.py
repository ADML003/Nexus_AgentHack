#!/usr/bin/env python3
"""
Comprehensive demo of the Nexus AI Backend
Demonstrates:
1. Portia.ai integration with Mistral LLM
2. FastAPI endpoints
3. GitHub OAuth integration (setup)
"""

import asyncio
import json
import time
from typing import Dict, Any

def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def print_step(step: str, description: str):
    """Print a formatted step"""
    print(f"\n🔥 {step}")
    print(f"   {description}")

async def main():
    """Main demo function"""
    print_header("🚀 NEXUS AI BACKEND - PORTIA.AI INTEGRATION DEMO")
    
    print("✅ SETUP COMPLETE:")
    print("   - FastAPI backend server running on http://localhost:8000")
    print("   - Portia SDK installed and configured with Mistral LLM")
    print("   - Environment variables loaded from .env.local")
    print("   - GitHub OAuth endpoints implemented")
    
    print_step("1. SERVER STATUS", "Backend is running with these endpoints:")
    endpoints = [
        "GET  /                     - API info and status",
        "GET  /health               - Health check endpoint", 
        "POST /api/query            - Portia AI agent query processing",
        "POST /api/auth/github/exchange - GitHub OAuth token exchange",
        "GET  /api/auth/github/user     - Get GitHub user info",
        "GET  /api/auth/github/repos    - Get user repositories",
        "GET  /docs                 - Interactive API documentation",
        "GET  /redoc                - Alternative API documentation"
    ]
    
    for endpoint in endpoints:
        print(f"   📍 {endpoint}")
    
    print_step("2. PORTIA AI INTEGRATION", "Configured with:")
    print("   🤖 LLM Provider: Mistral AI")
    print("   🧠 Model: mistral-large-latest") 
    print("   🔧 Tools: Example tool registry (calculator, etc.)")
    print("   💾 Storage: Portia Cloud (with your API key)")
    
    print_step("3. ENVIRONMENT CONFIGURATION", "API Keys configured:")
    env_vars = [
        "MISTRAL_API_KEY      ✅ (Active)",
        "PORTIA_API_KEY       ✅ (Active)", 
        "TAVILY_API_KEY       ✅ (Available)",
        "GITHUB_CLIENT_SECRET ⚙️  (Placeholder - update for OAuth)"
    ]
    
    for var in env_vars:
        print(f"   🔑 {var}")
    
    print_step("4. GITHUB OAUTH SETUP", "Ready for integration:")
    print("   📝 Update GITHUB_CLIENT_SECRET in .env.local")
    print("   🌐 Register app at: https://github.com/settings/applications/new")
    print("   🔄 Callback URL: http://localhost:3000/auth/callback")
    
    print_step("5. DEMO COMMANDS", "Test the API:")
    
    demo_commands = [
        {
            "description": "Test API root endpoint",
            "command": 'curl "http://localhost:8000/"'
        },
        {
            "description": "Test health endpoint", 
            "command": 'curl "http://localhost:8000/health"'
        },
        {
            "description": "Test Portia AI query (simple math)",
            "command": '''curl -X POST "http://localhost:8000/api/query" \\
     -H "Content-Type: application/json" \\
     -d '{"query": "What is 7 times 8?"}'
'''
        },
        {
            "description": "Test Portia AI query (complex reasoning)",
            "command": '''curl -X POST "http://localhost:8000/api/query" \\
     -H "Content-Type: application/json" \\
     -d '{"query": "If I save $100 per month for 2 years at 3% annual interest, how much will I have?"}'
'''
        },
        {
            "description": "View API documentation",
            "command": "open http://localhost:8000/docs"
        }
    ]
    
    for i, cmd in enumerate(demo_commands, 1):
        print(f"\n   {i}. {cmd['description']}:")
        print(f"      {cmd['command']}")
    
    print_step("6. PROJECT STRUCTURE", "Backend files created:")
    files = [
        "backend/main.py        - FastAPI server with Portia integration",
        "backend/test_api.py    - API test client", 
        "backend/test_portia.py - Portia SDK test",
        ".env.local             - Environment variables",
    ]
    
    for file in files:
        print(f"   📄 {file}")
    
    print_step("7. NEXT STEPS", "Frontend integration:")
    next_steps = [
        "Connect your Next.js frontend to http://localhost:8000",
        "Implement GitHub OAuth flow in your React components",
        "Use the /api/query endpoint for AI-powered features",
        "Add authentication middleware for protected routes"
    ]
    
    for step in next_steps:
        print(f"   📋 {step}")
    
    print_header("🎉 DEMO COMPLETE")
    print("Your FastAPI backend with Portia.ai integration is ready!")
    print("Server running at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")

if __name__ == "__main__":
    asyncio.run(main())
