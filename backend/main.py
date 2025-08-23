#!/usr/bin/env python3
"""
Nexus Portia Backend - Clean Implementation
Fixed all the core issues:
1. No incorrect await usage
2. Proper result extraction from PlanRun objects
3. Multi-provider fallback (Mistral -> Google)
4. Proper run completion waiting
"""

import os
import time
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
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
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
PORTIA_API_KEY = os.getenv("PORTIA_API_KEY")

print("🚀 Starting Nexus Portia Backend...")

# Create FastAPI app
app = FastAPI(title="Nexus Portia Backend", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize multiple Portia instances with different LLM providers for fallback
portia_instances = []

print("🔧 Initializing LLM providers...")

# Provider 1: Mistral (primary - best for math calculations)
if MISTRAL_API_KEY:
    try:
        mistral_config = Config.from_default(
            llm_provider=LLMProvider.MISTRALAI,
            mistralai_api_key=MISTRAL_API_KEY
        )
        mistral_portia = Portia(config=mistral_config, tools=open_source_tool_registry)
        portia_instances.append(("mistral", mistral_portia))
        print("✅ Mistral AI provider initialized")
    except Exception as e:
        print(f"⚠️ Mistral provider failed: {e}")

# Provider 2: Google (backup)
if GOOGLE_API_KEY:
    try:
        google_config = Config.from_default(
            llm_provider=LLMProvider.GOOGLE,
            google_api_key=GOOGLE_API_KEY
        )
        google_portia = Portia(config=google_config, tools=open_source_tool_registry)
        portia_instances.append(("google", google_portia))
        print("✅ Google AI provider initialized")
    except Exception as e:
        print(f"⚠️ Google provider failed: {e}")

# Check if we have at least one provider
if not portia_instances:
    print("❌ No LLM providers available!")
    print("💡 Make sure you have either MISTRAL_API_KEY or GOOGLE_API_KEY in your .env.local file")
    exit(1)

# Get tools info
os_tools = open_source_tool_registry.get_tools()
print(f"✅ Open Source Tools: {len(os_tools)} (using {len(portia_instances)} provider(s))")

# Models
class QueryRequest(BaseModel):
    message: str
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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "providers": len(portia_instances),
        "tools": len(os_tools),
        "mistral_available": any(name == "mistral" for name, _ in portia_instances),
        "google_available": any(name == "google" for name, _ in portia_instances)
    }

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process query with multi-provider fallback"""
    start_time = time.time()
    
    try:
        print(f"📝 Query: '{request.message}'")
        
        if not request.message or not request.message.strip():
            raise ValueError("Empty message provided")
        
        # Try each provider in order
        last_error = None
        
        for provider_name, portia_instance in portia_instances:
            try:
                print(f"🔍 Trying {provider_name.upper()}...")
                
                # Execute the query (no await needed!)
                run = portia_instance.run(request.message)
                print(f"✅ Run started: {run.id}")
                
                # Wait for completion
                max_wait = 60
                waited = 0
                while run.state.value not in ['COMPLETE', 'FAILED', 'CANCELLED'] and waited < max_wait:
                    time.sleep(2)
                    waited += 2
                    print(f"⏳ State: {run.state.value} ({waited}s)")
                
                print(f"✅ Final state: {run.state.value}")
                
                if run.state.value == 'COMPLETE':
                    # Extract result properly
                    result_text = None
                    
                    # Check outputs.final_output (the correct way)
                    if hasattr(run, 'outputs') and run.outputs:
                        if hasattr(run.outputs, 'final_output') and run.outputs.final_output:
                            final_out = run.outputs.final_output
                            
                            # Try summary first, then value
                            if hasattr(final_out, 'summary') and final_out.summary:
                                result_text = str(final_out.summary)
                                print(f"✅ Result from summary: {result_text}")
                            elif hasattr(final_out, 'value') and final_out.value:
                                result_text = str(final_out.value)
                                print(f"✅ Result from value: {result_text}")
                        
                        # Fallback: check step_outputs
                        if not result_text and hasattr(run.outputs, 'step_outputs') and run.outputs.step_outputs:
                            if '$result' in run.outputs.step_outputs:
                                step_result = run.outputs.step_outputs['$result']
                                if hasattr(step_result, 'summary') and step_result.summary:
                                    result_text = str(step_result.summary)
                                    print(f"✅ Result from step summary: {result_text}")
                                elif hasattr(step_result, 'value') and step_result.value:
                                    result_text = str(step_result.value)
                                    print(f"✅ Result from step value: {result_text}")
                    
                    if not result_text:
                        result_text = f"Query completed but no result extracted (Run ID: {run.id})"
                    
                    execution_time = time.time() - start_time
                    return QueryResponse(
                        success=True,
                        result=result_text,
                        execution_time_seconds=execution_time,
                        tool_registry_used=f"open_source_{provider_name}"
                    )
                
                elif run.state.value == 'FAILED':
                    # Extract error and try next provider
                    error_msg = "Unknown error"
                    if hasattr(run, 'outputs') and run.outputs and hasattr(run.outputs, 'final_output') and run.outputs.final_output:
                        if hasattr(run.outputs.final_output, 'value'):
                            error_msg = str(run.outputs.final_output.value)
                    
                    print(f"❌ {provider_name.upper()} failed: {error_msg}")
                    last_error = f"{provider_name}: {error_msg}"
                    
                    # If rate limit, definitely try next provider
                    if any(term in error_msg.lower() for term in ['rate limit', 'quota', 'capacity exceeded', '429']):
                        print("🔄 Rate limit - trying next provider...")
                        continue
                    
                    # For other errors, still try next provider
                    continue
                
            except Exception as e:
                print(f"❌ {provider_name.upper()} error: {e}")
                last_error = f"{provider_name}: {str(e)}"
                continue
        
        # All providers failed
        execution_time = time.time() - start_time
        return QueryResponse(
            success=False,
            error=f"All providers failed. Last: {last_error}",
            execution_time_seconds=execution_time,
            tool_registry_used="all_failed"
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"❌ Error: {e}")
        return QueryResponse(
            success=False,
            error=str(e),
            execution_time_seconds=execution_time,
            tool_registry_used="error"
        )

if __name__ == "__main__":
    import uvicorn
    print("🌟 Server starting on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
