#!/usr/bin/env python3
"""
Working Portia backend - Open Source + Cloud Tools
"""

import os
import time
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from portia import (
    Portia,
    Config,
    LLMProvider,
    PortiaToolRegistry,
    open_source_tool_registry
)

# Load environment variables
load_dotenv("../.env.local")

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PORTIA_API_KEY = os.getenv("PORTIA_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY required")

print("🚀 Starting Nexus Portia Backend...")

# Create FastAPI app
app = FastAPI(title="Nexus Portia Backend", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Portia instances
config = Config.from_default(
    llm_provider=LLMProvider.GOOGLE,
    google_api_key=GOOGLE_API_KEY
)

# Open source tools
print("📦 Loading open source tools...")
open_source_portia = Portia(config=config, tools=open_source_tool_registry)
os_tools = open_source_tool_registry.get_tools()
print(f"✅ Open Source Tools: {len(os_tools)}")

# Cloud tools
cloud_portia = None
cloud_tools = []
if PORTIA_API_KEY:
    try:
        print("📦 Loading cloud tools...")
        cloud_config = Config.from_default(
            llm_provider=LLMProvider.GOOGLE,
            google_api_key=GOOGLE_API_KEY,
            portia_api_key=PORTIA_API_KEY
        )
        cloud_registry = PortiaToolRegistry(config=cloud_config)
        cloud_portia = Portia(config=cloud_config, tools=cloud_registry)
        cloud_tools = cloud_registry.get_tools()
        print(f"✅ Cloud Tools: {len(cloud_tools)}")
    except Exception as e:
        print(f"⚠️ Cloud tools failed: {e}")

# Models
class QueryRequest(BaseModel):
    query: str
    tool_registry: str = "open_source"  # Default to open_source since it's more reliable
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    tools_used: Optional[List[str]] = None
    error: Optional[str] = None
    execution_time_seconds: Optional[float] = None
    tool_registry_used: Optional[str] = None

class ToolInfo(BaseModel):
    id: str
    name: str
    description: str
    category: str

class ToolRegistryResponse(BaseModel):
    registry_name: str
    total_tools: int
    tools: List[ToolInfo]

def get_tool_info(tool) -> ToolInfo:
    """Convert tool to ToolInfo"""
    tool_name = getattr(tool, 'name', 'Unknown Tool').lower()
    
    # Categorize tools
    if 'search' in tool_name or 'web' in tool_name or 'crawl' in tool_name:
        category = "Search & Web"
    elif 'calendar' in tool_name or 'gmail' in tool_name or 'slack' in tool_name or 'docs' in tool_name:
        category = "Productivity" 
    elif 'weather' in tool_name or 'map' in tool_name:
        category = "Information"
    elif 'file' in tool_name or 'document' in tool_name or 'pdf' in tool_name:
        category = "File Management"
    elif 'calculator' in tool_name or 'math' in tool_name:
        category = "Calculation"
    elif 'image' in tool_name or 'vision' in tool_name:
        category = "Image & Vision"
    else:
        category = "Utility"
    
    return ToolInfo(
        id=getattr(tool, 'id', 'unknown'),
        name=getattr(tool, 'name', 'Unknown Tool'),
        description=getattr(tool, 'description', 'No description available')[:200] + "...",  # Truncate long descriptions
        category=category
    )

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "open_source_tools": len(os_tools),
        "cloud_tools": len(cloud_tools),
        "google_api_configured": bool(GOOGLE_API_KEY),
        "portia_api_configured": bool(PORTIA_API_KEY),
        "cloud_tools_available": cloud_portia is not None
    }

@app.get("/tools/registries", response_model=List[ToolRegistryResponse])
async def get_tool_registries():
    """Get all tool registries"""
    registries = []
    
    # Open source
    registries.append(ToolRegistryResponse(
        registry_name="open_source",
        total_tools=len(os_tools),
        tools=[get_tool_info(tool) for tool in os_tools]
    ))
    
    # Cloud
    if cloud_portia:
        registries.append(ToolRegistryResponse(
            registry_name="cloud",
            total_tools=len(cloud_tools),
            tools=[get_tool_info(tool) for tool in cloud_tools[:50]]  # Limit for size
        ))
    
    return registries

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process query with selected registry"""
    start_time = time.time()
    
    try:
        # Select Portia instance
        if request.tool_registry == "cloud" and cloud_portia:
            portia_instance = cloud_portia
            registry_used = "cloud"
        else:
            portia_instance = open_source_portia
            registry_used = "open_source"
        
        print(f"🔍 Processing: {request.query[:50]}... with {registry_used}")
        
        # Execute query
        result = portia_instance.run(request.query)
        
        execution_time = time.time() - start_time
        print(f"✅ Completed in {execution_time:.2f}s")
        
        return QueryResponse(
            success=True,
            result=str(result.result),
            execution_time_seconds=execution_time,
            tool_registry_used=registry_used,
            tools_used=[]  # Could extract from logs if needed
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"❌ Error: {e}")
        
        return QueryResponse(
            success=False,
            error=str(e),
            execution_time_seconds=execution_time,
            tool_registry_used=request.tool_registry
        )

if __name__ == "__main__":
    import uvicorn
    print("🌟 Server ready!")
    uvicorn.run(app, host="0.0.0.0", port=8000)
