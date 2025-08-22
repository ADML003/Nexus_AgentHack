#!/usr/bin/env python3
"""
Enhanced Nexus AI Backend - FastAPI Server with Robust Error Handling
Improved version with better error handling and fallback strategies
"""

import os
import asyncio
import time
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

from portia import (
    Portia,
    Config,
    LLMProvider,
    StorageClass,
    LogLevel,
    example_tool_registry,
)

# Load environment variables
load_dotenv('../.env.local')

# Global Portia instances for fallback
portia_mistral: Optional[Portia] = None
portia_openai: Optional[Portia] = None

class QueryRequest(BaseModel):
    """Request model for AI queries"""
    query: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    model_preference: Optional[str] = "mistral"  # "mistral", "openai", "auto"

class QueryResponse(BaseModel):
    """Response model for AI queries"""
    success: bool
    plan_run_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_seconds: Optional[float] = None
    model_used: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    portia_mistral_configured: bool
    portia_openai_configured: bool
    mistral_configured: bool
    openai_configured: bool
    environment: str

def setup_mistral_portia() -> Optional[Portia]:
    """Setup Portia with Mistral AI"""
    try:
        mistral_api_key = os.getenv('MISTRAL_API_KEY')
        portia_api_key = os.getenv('PORTIA_API_KEY')
        
        if not mistral_api_key:
            print("⚠️  Mistral API key not found")
            return None
        
        print("🚀 Setting up Portia with Mistral AI...")
        
        config = Config.from_default(
            llm_provider=LLMProvider.MISTRALAI,
            default_model="mistralai/mistral-small-latest",  # Use smaller model to avoid limits
            planning_model="mistralai/mistral-small-latest",
            execution_model="mistralai/mistral-small-latest",
            mistralai_api_key=mistral_api_key,
            portia_api_key=portia_api_key,
            storage_class=StorageClass.CLOUD if portia_api_key else StorageClass.DISK,
            storage_dir='nexus_runs_mistral' if not portia_api_key else None,
            default_log_level=LogLevel.INFO,
        )
        
        portia = Portia(config=config, tools=example_tool_registry)
        print("✅ Mistral Portia initialized successfully")
        return portia
        
    except Exception as e:
        print(f"❌ Failed to initialize Mistral Portia: {str(e)}")
        return None

def setup_openai_portia() -> Optional[Portia]:
    """Setup Portia with OpenAI as fallback"""
    try:
        openai_api_key = os.getenv('OPENAI_API_KEY')
        portia_api_key = os.getenv('PORTIA_API_KEY')
        
        if not openai_api_key:
            print("⚠️  OpenAI API key not found, skipping OpenAI fallback")
            return None
        
        print("🔄 Setting up Portia with OpenAI fallback...")
        
        config = Config.from_default(
            llm_provider=LLMProvider.OPENAI,
            default_model="openai/gpt-4o-mini",  # Use smaller, cheaper model
            openai_api_key=openai_api_key,
            portia_api_key=portia_api_key,
            storage_class=StorageClass.CLOUD if portia_api_key else StorageClass.DISK,
            storage_dir='nexus_runs_openai' if not portia_api_key else None,
            default_log_level=LogLevel.INFO,
        )
        
        portia = Portia(config=config, tools=example_tool_registry)
        print("✅ OpenAI Portia fallback initialized successfully")
        return portia
        
    except Exception as e:
        print(f"⚠️  OpenAI fallback setup failed: {str(e)}")
        return None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    global portia_mistral, portia_openai
    
    print("🌟 Starting Nexus AI Backend with robust error handling...")
    
    # Try to setup Mistral first
    portia_mistral = setup_mistral_portia()
    
    # Setup OpenAI as fallback
    portia_openai = setup_openai_portia()
    
    if not portia_mistral and not portia_openai:
        print("❌ No AI providers available! Check your API keys.")
    else:
        providers = []
        if portia_mistral:
            providers.append("Mistral AI")
        if portia_openai:
            providers.append("OpenAI")
        print(f"✅ Available providers: {', '.join(providers)}")
    
    yield
    
    # Shutdown
    print("🛑 Nexus AI Backend shutting down")

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced Nexus AI Backend",
    description="Robust AI agent backend with Portia.ai, Mistral AI, and OpenAI fallback",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://nexus-agent-hack.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Enhanced health check"""
    mistral_configured = bool(os.getenv('MISTRAL_API_KEY'))
    openai_configured = bool(os.getenv('OPENAI_API_KEY'))
    portia_mistral_ok = portia_mistral is not None
    portia_openai_ok = portia_openai is not None
    
    status = "healthy"
    if not portia_mistral_ok and not portia_openai_ok:
        status = "degraded"
    elif not portia_mistral_ok:
        status = "fallback_mode"
    
    return HealthResponse(
        status=status,
        portia_mistral_configured=portia_mistral_ok,
        portia_openai_configured=portia_openai_ok,
        mistral_configured=mistral_configured,
        openai_configured=openai_configured,
        environment=os.getenv('ENVIRONMENT', 'development')
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Enhanced Nexus AI Backend with Robust Error Handling",
        "version": "2.0.0",
        "status": "operational",
        "docs": "/docs",
        "available_providers": [
            "mistral" if portia_mistral else None,
            "openai" if portia_openai else None
        ]
    }

def execute_with_retry(portia_client: Portia, query: str, max_retries: int = 2) -> Dict[str, Any]:
    """Execute query with retry logic for rate limits"""
    for attempt in range(max_retries + 1):
        try:
            start_time = time.time()
            plan_run = portia_client.run(query)
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "plan_run": plan_run,
                "execution_time": execution_time
            }
            
        except Exception as e:
            error_str = str(e)
            
            # Check if it's a rate limit error
            if "429" in error_str or "capacity exceeded" in error_str.lower():
                if attempt < max_retries:
                    wait_time = (2 ** attempt) * 5  # Exponential backoff
                    print(f"   Rate limit hit, waiting {wait_time}s before retry {attempt + 1}")
                    time.sleep(wait_time)
                    continue
            
            # If not rate limit or max retries exceeded, return error
            return {
                "success": False,
                "error": error_str,
                "execution_time": time.time() - start_time if 'start_time' in locals() else None
            }
    
    return {"success": False, "error": "Max retries exceeded"}

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process AI queries with fallback and retry logic"""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    print(f"🤖 Processing query: {request.query[:100]}...")
    
    # Determine which provider to use
    model_used = None
    result = None
    
    # Try Mistral first (unless specifically requesting OpenAI)
    if request.model_preference != "openai" and portia_mistral:
        print("   Attempting with Mistral AI...")
        result = execute_with_retry(portia_mistral, request.query)
        model_used = "mistral"
        
        if result["success"]:
            print(f"✅ Mistral successful in {result['execution_time']:.2f}s")
        else:
            print(f"❌ Mistral failed: {result['error'][:100]}...")
    
    # Fallback to OpenAI if Mistral failed or was specifically requested
    if (not result or not result["success"]) and portia_openai and request.model_preference != "mistral":
        print("   Falling back to OpenAI...")
        result = execute_with_retry(portia_openai, request.query)
        model_used = "openai" if not model_used else f"{model_used}->openai"
        
        if result["success"]:
            print(f"✅ OpenAI fallback successful in {result['execution_time']:.2f}s")
        else:
            print(f"❌ OpenAI fallback also failed: {result['error'][:100]}...")
    
    if not result or not result["success"]:
        error_msg = result.get("error", "No AI providers available") if result else "No AI providers available"
        
        return QueryResponse(
            success=False,
            error=error_msg,
            model_used=model_used,
            execution_time_seconds=result.get("execution_time") if result else None
        )
    
    # Success - extract results
    plan_run = result["plan_run"]
    response_data = {
        "plan_run_id": plan_run.id,
        "plan_id": plan_run.plan_id,
        "state": plan_run.state,
        "current_step_index": plan_run.current_step_index,
        "final_output": {
            "value": plan_run.outputs.final_output.value,
            "summary": plan_run.outputs.final_output.summary
        },
        "step_outputs": {
            key: {
                "value": value.value,
                "summary": value.summary
            } for key, value in plan_run.outputs.step_outputs.items()
        },
        "clarifications": plan_run.outputs.clarifications
    }
    
    return QueryResponse(
        success=True,
        plan_run_id=plan_run.id,
        result=response_data,
        execution_time_seconds=result["execution_time"],
        model_used=model_used
    )

@app.get("/api/status")
async def get_status():
    """Get detailed status information"""
    return {
        "providers": {
            "mistral": {
                "available": portia_mistral is not None,
                "model": "mistral-small-latest",
                "api_key_set": bool(os.getenv('MISTRAL_API_KEY'))
            },
            "openai": {
                "available": portia_openai is not None,
                "model": "gpt-4o-mini",
                "api_key_set": bool(os.getenv('OPENAI_API_KEY'))
            }
        },
        "environment": {
            "portia_api_key": bool(os.getenv('PORTIA_API_KEY')),
            "tavily_api_key": bool(os.getenv('TAVILY_API_KEY')),
        },
        "server": {
            "environment": os.getenv('ENVIRONMENT', 'development'),
            "port": 8000,
            "version": "2.0.0"
        }
    }

if __name__ == "__main__":
    # Configuration
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '8000'))
    debug = os.getenv('ENVIRONMENT', 'development') == 'development'
    
    print(f"🚀 Starting Enhanced Nexus AI Backend on {host}:{port}")
    print(f"   Debug Mode: {debug}")
    print(f"   Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"   API Documentation: http://{host}:{port}/docs")
    
    # Run the server
    uvicorn.run(
        "main_robust:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug",
        access_log=True
    )
