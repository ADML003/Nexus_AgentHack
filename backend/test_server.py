#!/usr/bin/env python3
"""
Simple Portia backend - Open Source Tools Only (for testing)
"""

import os
import time
from typing import Optional, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from portia import (
    Portia,
    Config,
    LLMProvider,
    open_source_tool_registry
)

# Load environment variables
load_dotenv("/Users/ADML/Desktop/Nexus/.env.local")

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY required")

print("🚀 Starting Simple Nexus Backend (Open Source Tools Only)...")

# Create FastAPI app
app = FastAPI(title="Nexus Simple Backend", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize open source tools only
print("📦 Loading open source tools...")
config = Config.from_default(
    llm_provider=LLMProvider.GOOGLE,
    google_api_key=GOOGLE_API_KEY
)

os_portia = Portia(config=config)
os_portia.add_tool_registry(open_source_tool_registry)
os_tools = list(os_portia.tool_registry.list_tools())
print(f"✅ Open Source Tools: {len(os_tools)}")

# Models
class QueryRequest(BaseModel):
    query: str
    tool_registry: str = "open_source"
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
    """Extract tool information"""
    return ToolInfo(
        id=getattr(tool, 'id', 'unknown'),
        name=getattr(tool, 'name', 'Unknown Tool'),
        description=getattr(tool, 'description', 'No description available'),
        category=getattr(tool, 'category', 'Unknown')
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "open_source_tools": len(os_tools),
        "google_api_configured": bool(GOOGLE_API_KEY),
    }

@app.get("/tools/registries", response_model=List[ToolRegistryResponse])
async def get_tool_registries():
    """Get all tool registries"""
    registries = [
        ToolRegistryResponse(
            registry_name="open_source",
            total_tools=len(os_tools),
            tools=[get_tool_info(tool) for tool in os_tools]
        )
    ]
    return registries

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process query with open source tools"""
    start_time = time.time()
    
    try:
        print(f"🔍 Processing: {request.query[:50]}... with open_source")
        
        # Execute query
        result = os_portia.run(request.query)
        
        execution_time = time.time() - start_time
        print(f"✅ Completed in {execution_time:.2f}s")
        
        # Extract result - improved method
        result_text = "Task completed successfully."
        
        try:
            # Wait a bit for final_output to be populated
            import time as time_mod
            max_wait = 10  # seconds
            wait_interval = 1
            waited = 0
            
            while waited < max_wait:
                if hasattr(result, 'final_output') and result.final_output:
                    final_output = str(result.final_output).strip()
                    if final_output and final_output != 'None':
                        result_text = final_output
                        print(f"✅ Got final_output after {waited}s: {result_text[:100]}...")
                        break
                
                time_mod.sleep(wait_interval)
                waited += wait_interval
            
            # If still no result, try other approaches
            if result_text == "Task completed successfully.":
                if isinstance(result, str):
                    result_text = result
                else:
                    result_text = f"Task completed. View full results in Portia dashboard."
        
        except Exception as e:
            print(f"⚠️ Error extracting result: {e}")
            result_text = f"Task completed. Execution time: {execution_time:.2f}s"
        
        return QueryResponse(
            success=True,
            result=result_text,
            execution_time_seconds=execution_time,
            tool_registry_used="open_source",
            tools_used=[]
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"❌ Error: {e}")
        
        return QueryResponse(
            success=False,
            error=str(e),
            execution_time_seconds=execution_time,
            tool_registry_used="open_source"
        )

if __name__ == "__main__":
    import uvicorn
    print("🌟 Simple server ready!")
    uvicorn.run(app, host="0.0.0.0", port=8000)
