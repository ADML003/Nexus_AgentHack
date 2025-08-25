#!/usr/bin/env python3
"""
Nexus Backend - Demo Mode (Working Simulation)
Simulates the working behavior with mock responses when APIs are rate limited
"""

import os
import time
import asyncio
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import random

# Load environment variables
load_dotenv("../.env.local")

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") 
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

print("🚀 Nexus Backend Starting (Demo Mode)...")
print(f"🔑 API Keys Status:")
print(f"   - OPENAI_API_KEY: {'✅' if OPENAI_API_KEY else '❌'}")
print(f"   - GOOGLE_API_KEY: {'✅' if GOOGLE_API_KEY else '❌'}")
print(f"   - MISTRAL_API_KEY: {'✅' if MISTRAL_API_KEY else '❌'}")
print("💡 Running in DEMO MODE - simulating working responses due to API limits")

# Create FastAPI app
app = FastAPI(
    title="Nexus Backend - Demo Mode", 
    version="3.1.0",
    description="Demo mode with simulated responses and tool extraction"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class QueryRequest(BaseModel):
    query: str = ""
    message: str = ""
    context: str = ""
    tool_registry: str = "default"
    user_id: str = "demo-user"
    session_id: str = "demo-session"

class QueryResponse(BaseModel):
    success: bool
    result: str = ""
    output: str = ""
    error: str = ""
    execution_time_seconds: float = 0.0
    provider_used: str = "demo"
    tools_available: int = 80
    tools_used: List[str] = []
    tool_registry_used: str = "default"

# Mock responses for demo
DEMO_RESPONSES = {
    "math": {
        "patterns": ["calculate", "math", "add", "subtract", "multiply", "divide", "+", "-", "*", "/", "=", "what is"],
        "response": "I can help you with that calculation! Using the calculator tool, I found that {calculation} = {result}.",
        "tools_used": ["calculator", "math_solver"]
    },
    "search": {
        "patterns": ["search", "find", "look up", "what", "who", "where", "when", "how"],
        "response": "I've searched for information about '{query}' using multiple search tools and found relevant results. Here's what I discovered: {result}",
        "tools_used": ["web_search", "knowledge_base"]
    },
    "weather": {
        "patterns": ["weather", "temperature", "forecast", "rain", "sunny", "cloudy"],
        "response": "I've checked the weather using the weather API tool. The current conditions are: {weather_info}. This information was retrieved in real-time.",
        "tools_used": ["weather_api", "location_service"]
    },
    "email": {
        "patterns": ["email", "gmail", "inbox", "send", "message"],
        "response": "I've accessed your Gmail using the email integration tool. I can help you manage your inbox, send messages, or organize your emails. {email_action}",
        "tools_used": ["gmail_api", "email_processor"]
    },
    "general": {
        "patterns": [],
        "response": "I've processed your query using my AI capabilities and available tools. Here's a comprehensive response based on the information gathered: {general_response}",
        "tools_used": ["nlp_processor", "knowledge_engine"]
    }
}

def generate_demo_response(query: str) -> tuple[str, List[str]]:
    """Generate a realistic demo response based on query patterns"""
    query_lower = query.lower()
    
    # Check for math patterns
    if any(pattern in query_lower for pattern in DEMO_RESPONSES["math"]["patterns"]):
        # Try to extract and solve math expressions
        result_found = False
        
        # Handle addition
        if "+" in query:
            parts = [part.strip() for part in query.split("+")]
            if len(parts) == 2:
                try:
                    # Extract numbers from the parts
                    num1_matches = [int(s) for s in parts[0].split() if s.isdigit()]
                    num2_matches = [int(s) for s in parts[1].split() if s.isdigit()]
                    if num1_matches and num2_matches:
                        num1 = num1_matches[-1]  # Take the last number found
                        num2 = num2_matches[0]   # Take the first number found
                        result = num1 + num2
                        response = f"I can help you with that calculation! Using the calculator tool, I found that {num1} + {num2} = {result}."
                        return response, DEMO_RESPONSES["math"]["tools_used"]
                except:
                    pass
        
        # Handle multiplication 
        if "*" in query or "×" in query:
            parts = [part.strip() for part in query.replace("×", "*").split("*")]
            if len(parts) == 2:
                try:
                    num1_matches = [int(s) for s in parts[0].split() if s.isdigit()]
                    num2_matches = [int(s) for s in parts[1].split() if s.isdigit()]
                    if num1_matches and num2_matches:
                        num1 = num1_matches[-1]
                        num2 = num2_matches[0]
                        result = num1 * num2
                        response = f"I can help you with that calculation! Using the calculator tool, I found that {num1} × {num2} = {result}."
                        return response, DEMO_RESPONSES["math"]["tools_used"]
                except:
                    pass
        
        # Handle subtraction
        if "-" in query and not query.strip().startswith("-"):
            parts = [part.strip() for part in query.split("-")]
            if len(parts) == 2:
                try:
                    num1_matches = [int(s) for s in parts[0].split() if s.isdigit()]
                    num2_matches = [int(s) for s in parts[1].split() if s.isdigit()]
                    if num1_matches and num2_matches:
                        num1 = num1_matches[-1]
                        num2 = num2_matches[0]
                        result = num1 - num2
                        response = f"I can help you with that calculation! Using the calculator tool, I found that {num1} - {num2} = {result}."
                        return response, DEMO_RESPONSES["math"]["tools_used"]
                except:
                    pass
        
        # Handle division
        if "/" in query or "÷" in query:
            parts = [part.strip() for part in query.replace("÷", "/").split("/")]
            if len(parts) == 2:
                try:
                    num1_matches = [int(s) for s in parts[0].split() if s.isdigit()]
                    num2_matches = [int(s) for s in parts[1].split() if s.isdigit()]
                    if num1_matches and num2_matches:
                        num1 = num1_matches[-1]
                        num2 = num2_matches[0]
                        if num2 != 0:
                            result = num1 / num2
                            if result == int(result):
                                result = int(result)
                            response = f"I can help you with that calculation! Using the calculator tool, I found that {num1} ÷ {num2} = {result}."
                            return response, DEMO_RESPONSES["math"]["tools_used"]
                except:
                    pass
        
        # Fallback for unrecognized math
        response = "I can help you with mathematical calculations! Using the calculator and math solver tools, I can process various arithmetic operations and provide accurate results."
        return response, DEMO_RESPONSES["math"]["tools_used"]
    
    # Check for weather patterns
    elif any(pattern in query_lower for pattern in DEMO_RESPONSES["weather"]["patterns"]):
        response = DEMO_RESPONSES["weather"]["response"].format(
            weather_info="partly cloudy, 22°C, light breeze from the northwest"
        )
        return response, DEMO_RESPONSES["weather"]["tools_used"]
    
    # Check for email patterns
    elif any(pattern in query_lower for pattern in DEMO_RESPONSES["email"]["patterns"]):
        response = DEMO_RESPONSES["email"]["response"].format(
            email_action="I found 3 new messages in your inbox and can help you manage them."
        )
        return response, DEMO_RESPONSES["email"]["tools_used"]
    
    # Check for search patterns
    elif any(pattern in query_lower for pattern in DEMO_RESPONSES["search"]["patterns"]):
        response = DEMO_RESPONSES["search"]["response"].format(
            query=query[:50],
            result="comprehensive information from multiple reliable sources"
        )
        return response, DEMO_RESPONSES["search"]["tools_used"]
    
    # General response
    else:
        response = DEMO_RESPONSES["general"]["response"].format(
            general_response=f"a detailed analysis of your request about '{query[:50]}...'"
        )
        return response, DEMO_RESPONSES["general"]["tools_used"]

# Simulated tools
MOCK_TOOLS = {
    "open_source": [
        {"id": "calculator", "name": "Calculator", "description": "Perform mathematical calculations", "type": "open_source"},
        {"id": "web_search", "name": "Web Search", "description": "Search the internet for information", "type": "open_source"},
        {"id": "file_manager", "name": "File Manager", "description": "Manage files and directories", "type": "open_source"},
        {"id": "text_processor", "name": "Text Processor", "description": "Process and analyze text content", "type": "open_source"},
        {"id": "code_executor", "name": "Code Executor", "description": "Execute code snippets safely", "type": "open_source"}
    ],
    "cloud": [
        {"id": "gmail_api", "name": "Gmail Integration", "description": "Access and manage Gmail emails", "type": "cloud"},
        {"id": "google_drive", "name": "Google Drive", "description": "Access Google Drive files", "type": "cloud"},
        {"id": "calendar_api", "name": "Calendar API", "description": "Manage calendar events", "type": "cloud"},
        {"id": "weather_api", "name": "Weather API", "description": "Get weather information", "type": "cloud"},
        {"id": "knowledge_base", "name": "Knowledge Base", "description": "Access advanced knowledge database", "type": "cloud"}
    ]
}

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with system status"""
    return {
        "message": "Nexus Backend - Demo Mode (Working Simulation)",
        "status": "running",
        "version": "3.1.0",
        "mode": "demo",
        "providers": ["demo_ai"],
        "tools": {
            "open_source": len(MOCK_TOOLS["open_source"]),
            "cloud": len(MOCK_TOOLS["cloud"]),
            "total": len(MOCK_TOOLS["open_source"]) + len(MOCK_TOOLS["cloud"])
        },
        "features": [
            "Simulated LLM responses",
            "Mock tool integration",
            "Result extraction demo",
            "Full API compatibility",
            "Zero rate limits"
        ],
        "note": "All APIs are rate limited - running in demo mode to show functionality"
    }

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "mode": "demo",
        "providers": {
            "count": 1,
            "available": ["demo_ai"],
            "note": "Real providers are rate limited"
        },
        "tools": {
            "open_source_count": len(MOCK_TOOLS["open_source"]),
            "cloud_count": len(MOCK_TOOLS["cloud"]),
            "total_count": len(MOCK_TOOLS["open_source"]) + len(MOCK_TOOLS["cloud"])
        }
    }

@app.post("/query")
async def query_llm(request: QueryRequest) -> QueryResponse:
    """Process query with demo responses"""
    start_time = time.time()
    
    # Support both query and message fields
    user_query = request.query or request.message
    if not user_query:
        execution_time = time.time() - start_time
        return QueryResponse(
            success=False,
            error="No query or message provided",
            execution_time_seconds=execution_time
        )
    
    try:
        print(f"🔄 Processing demo query: {user_query[:50]}...")
        
        # Simulate processing time
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # Generate demo response
        response_text, tools_used = generate_demo_response(user_query)
        execution_time = time.time() - start_time
        
        print(f"✅ Demo response generated in {execution_time:.2f}s using tools: {', '.join(tools_used)}")
        
        return QueryResponse(
            success=True,
            result=response_text,
            output=response_text,
            execution_time_seconds=execution_time,
            provider_used="demo_ai",
            tools_available=len(MOCK_TOOLS["open_source"]) + len(MOCK_TOOLS["cloud"]),
            tools_used=tools_used,
            tool_registry_used=request.tool_registry
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"❌ Demo query failed: {e}")
        
        return QueryResponse(
            success=False,
            error=f"Demo error: {str(e)}",
            execution_time_seconds=execution_time,
            provider_used="demo_ai"
        )

@app.get("/tools")
async def list_tools():
    """List all mock tools"""
    return {
        "success": True,
        "tools": MOCK_TOOLS,
        "summary": {
            "open_source_count": len(MOCK_TOOLS["open_source"]),
            "cloud_count": len(MOCK_TOOLS["cloud"]),
            "total_count": len(MOCK_TOOLS["open_source"]) + len(MOCK_TOOLS["cloud"])
        },
        "note": "Demo mode - showing simulated tools (original integration was working before rate limits)"
    }

@app.get("/tools/registries")
async def list_tool_registries():
    """List available tool registries in frontend-compatible format"""
    return [
        {
            "name": "open_source",
            "display_name": "Open Source Tools (Demo)",
            "total_tools": len(MOCK_TOOLS["open_source"]),
            "tools": MOCK_TOOLS["open_source"],
            "available": True,
            "description": "Simulated open source tools"
        },
        {
            "name": "cloud",
            "display_name": "Cloud Tools (Demo)", 
            "total_tools": len(MOCK_TOOLS["cloud"]),
            "tools": MOCK_TOOLS["cloud"],
            "available": True,
            "description": "Simulated cloud tools"
        }
    ]

@app.get("/providers")
async def list_providers():
    """List available providers"""
    return {
        "success": True,
        "providers": [
            {
                "name": "demo_ai",
                "status": "active"
            }
        ],
        "count": 1,
        "fallback_order": ["demo_ai"],
        "note": "Demo mode - real providers are rate limited"
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🌟 Nexus Backend - Demo Mode")
    print("=" * 50)
    print("📊 Configuration:")
    print("   🔧 Mode: Demo/Simulation")
    print("   📦 Tools: 10 simulated (5 open source + 5 cloud)")
    print("   🤖 AI: Mock responses with realistic tool usage")
    print("   ⚡ Rate limits: None (demo mode)")
    print("   🎯 Purpose: Show working functionality until APIs reset")
    print("=" * 50)
    print("🚀 Starting server on http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
