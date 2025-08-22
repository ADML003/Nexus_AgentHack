#!/usr/bin/env python3
"""
Nexus AI Backend - FastAPI Server
Primary: Google Gemini 1.5 Pro | Secondary: Mistral AI
"""

import os
import asyncio
import time
import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import httpx
from mistralai import Mistral

from portia import (
    Portia,
    Config,
    LLMProvider,
    StorageClass,
    LogLevel,
    example_tool_registry,
    open_source_tool_registry,
    PortiaToolRegistry,
    McpToolRegistry,
)

# Import Gemini integration
from gemini_model import GeminiModel, create_gemini_config

# Load environment variables
load_dotenv("../.env.local")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
PORTIA_API_KEY = os.getenv("PORTIA_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not PORTIA_API_KEY:
    raise ValueError("PORTIA_API_KEY not found in environment variables")

# Global clients
portia_gemini: Optional[Portia] = None
portia_mistral: Optional[Portia] = None
mistral_client: Optional[Mistral] = None

class QueryRequest(BaseModel):
    """Request model for AI queries"""
    query: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    model_preference: Optional[str] = "gemini"  # "gemini", "mistral", "auto"

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
    portia_gemini_configured: bool
    portia_mistral_configured: bool
    mistral_configured: bool
    google_configured: bool
    environment: str

def create_enhanced_tool_registry():
    """Create a comprehensive tool registry with all available Portia tools"""
    logger.info("🔧 Creating enhanced tool registry with all available tools...")
    
    # Start with open source tools (10 tools available)
    all_tools = list(open_source_tool_registry.get_tools())
    logger.info(f"✅ Starting with {len(all_tools)} open source tools")
    
    # Try to add Portia Cloud tools if API key is available
    if PORTIA_API_KEY:
        try:
            logger.info("🌐 Setting up Portia Cloud tools...")
            
            # Create a temporary config for cloud tools registry
            temp_config = Config.from_default(
                llm_provider=LLMProvider.MISTRALAI,
                default_model='mistralai/mistral-small-latest',
                mistralai_api_key=MISTRAL_API_KEY,
                portia_api_key=PORTIA_API_KEY,
                storage_class='MEMORY'
            )
            
            # Initialize cloud registry with config
            cloud_registry = PortiaToolRegistry(config=temp_config)
            
            # Get available cloud tools
            cloud_tools = cloud_registry.get_tools()
            logger.info(f"✅ Found {len(cloud_tools)} Portia Cloud tools")
            
            # Add cloud tools to our list
            for tool in cloud_tools:
                # Check if tool already exists (by name)
                if not any(t.name == tool.name for t in all_tools):
                    all_tools.append(tool)
                    logger.info(f"  + Added cloud tool: {tool.name[:50]}...")
                else:
                    logger.info(f"  - Skipped duplicate tool: {tool.name}")
                
        except Exception as e:
            logger.warning(f"⚠️  Failed to load Portia Cloud tools: {str(e)}")
            logger.info("   Continuing with open source tools only")
    
    # Try to add MCP tools
    try:
        logger.info("🔗 Setting up MCP tools...")
        mcp_registry = McpToolRegistry()
        mcp_tools = mcp_registry.get_tools()
        
        if mcp_tools:
            logger.info(f"✅ Found {len(mcp_tools)} MCP tools")
            for tool in mcp_tools:
                if not any(t.name == tool.name for t in all_tools):
                    all_tools.append(tool)
                    logger.info(f"  + Added MCP tool: {tool.name}")
        else:
            logger.info("ℹ️  No MCP tools currently configured")
            
    except Exception as e:
        logger.warning(f"⚠️  Failed to load MCP tools: {str(e)}")
    
    # Create final registry with all tools
    try:
        final_registry = open_source_tool_registry
        for tool in all_tools[len(open_source_tool_registry.get_tools()):]:  # Skip already included open source tools
            final_registry = final_registry.with_tool(tool)
            
        final_tools = final_registry.get_tools()
        logger.info(f"🎯 Enhanced tool registry created with {len(final_tools)} total tools:")
        
        for i, tool in enumerate(final_tools):
            tool_type = "🌐 Cloud" if "portia:" in tool.name else "🔧 Open Source"
            logger.info(f"  {i+1:2d}. {tool_type} - {tool.name}")
        
        return final_registry
        
    except Exception as e:
        logger.error(f"❌ Failed to create final registry: {e}")
        logger.info("   Falling back to open source tools only")
        return open_source_tool_registry

def setup_gemini_portia() -> Optional[Portia]:
    """Setup Portia with Google Gemini as primary model"""
    try:
        if not GOOGLE_API_KEY:
            logger.warning("Google API key not found")
            return None
        
        logger.info("🤖 Setting up Portia with Google Gemini 1.5 Pro...")
        
        # Create Gemini configuration
        config = create_gemini_config(
            api_key=GOOGLE_API_KEY,
            model_name="gemini-1.5-pro",
            temperature=0.7,
            max_tokens=2048,
            storage_class=StorageClass.CLOUD if PORTIA_API_KEY else StorageClass.DISK,
            storage_dir='nexus_runs_gemini' if not PORTIA_API_KEY else None,
            default_log_level=LogLevel.INFO,
        )
        
        # Create enhanced tool registry
        enhanced_tools = create_enhanced_tool_registry()
        
        portia = Portia(config=config, tools=enhanced_tools)
        logger.info("✅ Gemini Portia configured successfully")
        return portia
        
    except Exception as e:
        logger.error(f"❌ Failed to setup Gemini Portia: {str(e)}")
        return None

def setup_mistral_portia() -> Optional[Portia]:
    """Setup Portia with Mistral AI as secondary model"""
    try:
        if not MISTRAL_API_KEY:
            logger.warning("Mistral API key not found")
            return None
        
        logger.info("📝 Setting up Portia with Mistral AI (secondary)...")
        
        config = Config.from_default(
            llm_provider=LLMProvider.MISTRALAI,
            default_model="mistralai/mistral-small-latest",
            planning_model="mistralai/mistral-small-latest",
            execution_model="mistralai/mistral-small-latest",
            mistralai_api_key=MISTRAL_API_KEY,
            portia_api_key=PORTIA_API_KEY,
            storage_class=StorageClass.CLOUD if PORTIA_API_KEY else StorageClass.DISK,
            storage_dir='nexus_runs_mistral' if not PORTIA_API_KEY else None,
            default_log_level=LogLevel.INFO,
        )
        
        # Create enhanced tool registry
        enhanced_tools = create_enhanced_tool_registry()
        
        portia = Portia(config=config, tools=enhanced_tools)
        logger.info("✅ Mistral Portia configured successfully")
        return portia
        
    except Exception as e:
        logger.error(f"❌ Failed to setup Mistral Portia: {str(e)}")
        return None

def setup_mistral_client() -> Optional[Mistral]:
    """Setup direct Mistral client for final fallback"""
    try:
        if not MISTRAL_API_KEY:
            return None
        
        client = Mistral(api_key=MISTRAL_API_KEY)
        logger.info("✅ Direct Mistral client configured")
        return client
        
    except Exception as e:
        logger.error(f"❌ Failed to setup Mistral client: {str(e)}")
        return None

async def initialize_services():
    """Initialize all AI services"""
    global portia_gemini, portia_mistral, mistral_client
    
    logger.info("🚀 Initializing AI services...")
    
    # Initialize Gemini (primary)
    portia_gemini = setup_gemini_portia()
    
    # Initialize Mistral (secondary)
    portia_mistral = setup_mistral_portia()
    mistral_client = setup_mistral_client()
    
    # Log status
    services_status = {
        "Gemini Portia": bool(portia_gemini),
        "Mistral Portia": bool(portia_mistral),
        "Mistral Direct": bool(mistral_client)
    }
    
    for service, status in services_status.items():
        status_icon = "✅" if status else "❌"
        logger.info(f"{status_icon} {service}: {'Available' if status else 'Not Available'}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await initialize_services()
    yield
    # Shutdown
    logger.info("🛑 Shutting down AI services")

# Initialize FastAPI app
app = FastAPI(
    title="Nexus AI Backend",
    description="AI backend with Google Gemini (primary) and Mistral (secondary) integration",
    version="3.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def execute_with_retry(
    portia_instance: Portia,
    query: str,
    model_name: str,
    max_retries: int = 3,
    base_delay: float = 1.0
) -> Dict[str, Any]:
    """Execute query with exponential backoff retry logic"""
    
    for attempt in range(max_retries):
        try:
            logger.info(f"🔄 Attempt {attempt + 1}/{max_retries} for {model_name} query execution")
            
            start_time = time.time()
            plan_run = portia_instance.run(query)
            execution_time = time.time() - start_time
            
            logger.info(f"⏱️ {model_name} query executed in {execution_time:.2f} seconds")
            logger.info(f"📋 Plan Run ID: {plan_run.id}")
            logger.info(f"📊 Final State: {plan_run.state}")
            
            # Extract result based on available attributes
            result_data = {"plan_run_id": plan_run.id, "state": plan_run.state}
            
            if hasattr(plan_run, 'outputs') and plan_run.outputs:
                if hasattr(plan_run.outputs, 'final_output') and plan_run.outputs.final_output:
                    result_data["final_output"] = plan_run.outputs.final_output.value
                    result_data["output_type"] = plan_run.outputs.final_output.type
                if hasattr(plan_run.outputs, 'execution_outputs') and plan_run.outputs.execution_outputs:
                    result_data["execution_outputs"] = [
                        {
                            "value": output.value,
                            "type": output.type
                        }
                        for output in plan_run.outputs.execution_outputs
                    ]
            
            return {
                "success": True,
                "result": result_data,
                "execution_time": execution_time
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"❌ {model_name} attempt {attempt + 1} failed: {error_msg}")
            
            if attempt == max_retries - 1:
                return {
                    "success": False,
                    "error": f"{model_name} failed after {max_retries} attempts. Last error: {error_msg}",
                    "execution_time": None
                }
            
            # Exponential backoff
            delay = base_delay * (2 ** attempt)
            logger.info(f"⏳ Waiting {delay:.1f}s before retry...")
            await asyncio.sleep(delay)

async def execute_mistral_fallback(query: str) -> Dict[str, Any]:
    """Execute query using direct Mistral API as final fallback"""
    try:
        if not mistral_client:
            return {
                "success": False,
                "error": "Mistral client not available",
                "execution_time": None
            }
        
        logger.info("🔄 Using Mistral direct API as final fallback...")
        start_time = time.time()
        
        response = mistral_client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": query}],
            temperature=0.7,
            max_tokens=1024
        )
        
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            "result": {
                "final_output": response.choices[0].message.content,
                "output_type": "text",
                "model": "mistral-small-latest",
                "usage": response.usage.__dict__ if hasattr(response, 'usage') else None
            },
            "execution_time": execution_time
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Mistral fallback failed: {str(e)}",
            "execution_time": None
        }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        portia_gemini_configured=bool(portia_gemini),
        portia_mistral_configured=bool(portia_mistral),
        mistral_configured=bool(mistral_client),
        google_configured=bool(GOOGLE_API_KEY),
        environment=os.getenv("ENVIRONMENT", "development")
    )

@app.get("/tools")
async def list_available_tools():
    """List all available tools in the enhanced registry"""
    try:
        enhanced_registry = create_enhanced_tool_registry()
        tools = enhanced_registry.get_tools()
        
        tools_info = []
        for i, tool in enumerate(tools):
            tool_info = {
                "id": i + 1,
                "name": tool.name,
                "class": tool.__class__.__name__,
                "type": "Cloud" if hasattr(tool, '_is_cloud_tool') else "Open Source",
                "description": getattr(tool, 'description', 'No description available')
            }
            tools_info.append(tool_info)
        
        return {
            "success": True,
            "total_tools": len(tools_info),
            "open_source_count": len([t for t in tools_info if t["type"] == "Open Source"]),
            "cloud_count": len([t for t in tools_info if t["type"] == "Cloud"]),
            "portia_api_key_configured": bool(PORTIA_API_KEY),
            "tools": tools_info
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to retrieve tools: {str(e)}",
            "tools": []
        }

@app.post("/query", response_model=QueryResponse)
async def query_ai(request: QueryRequest, background_tasks: BackgroundTasks):
    """
    Process AI query with intelligent model selection and fallback
    Priority: Google Gemini -> Mistral Portia -> Mistral Direct
    """
    start_time = time.time()
    
    try:
        logger.info(f"🔍 Processing query: {request.query[:100]}...")
        logger.info(f"👤 User: {request.user_id}, Session: {request.session_id}")
        logger.info(f"🎯 Model preference: {request.model_preference}")
        
        # Determine execution strategy based on preference and availability
        if request.model_preference == "gemini" and portia_gemini:
            logger.info("🤖 Using Google Gemini (Primary)")
            result = await execute_with_retry(portia_gemini, request.query, "Gemini")
            model_used = "gemini-1.5-pro"
            
        elif request.model_preference == "mistral" and portia_mistral:
            logger.info("📝 Using Mistral Portia (Requested)")
            result = await execute_with_retry(portia_mistral, request.query, "Mistral")
            model_used = "mistral-portia"
            
        else:
            # Auto fallback logic: Gemini -> Mistral Portia -> Mistral Direct
            logger.info("🎯 Auto model selection...")
            
            # Try Gemini first
            if portia_gemini:
                logger.info("🤖 Trying Google Gemini...")
                result = await execute_with_retry(portia_gemini, request.query, "Gemini", max_retries=2)
                model_used = "gemini-1.5-pro"
                
                if not result["success"]:
                    logger.info("📝 Gemini failed, trying Mistral Portia...")
                    if portia_mistral:
                        result = await execute_with_retry(portia_mistral, request.query, "Mistral", max_retries=2)
                        model_used = "mistral-portia"
                        
                        if not result["success"]:
                            logger.info("🚨 Portia failed, using Mistral direct...")
                            result = await execute_mistral_fallback(request.query)
                            model_used = "mistral-direct"
                    else:
                        logger.info("🚨 Using Mistral direct fallback...")
                        result = await execute_mistral_fallback(request.query)
                        model_used = "mistral-direct"
                        
            elif portia_mistral:
                logger.info("📝 Using Mistral Portia...")
                result = await execute_with_retry(portia_mistral, request.query, "Mistral")
                model_used = "mistral-portia"
                
                if not result["success"]:
                    logger.info("🚨 Fallback to Mistral direct...")
                    result = await execute_mistral_fallback(request.query)
                    model_used = "mistral-direct"
                    
            else:
                logger.info("🚨 Using Mistral direct (only option)...")
                result = await execute_mistral_fallback(request.query)
                model_used = "mistral-direct"
        
        total_time = time.time() - start_time
        
        if result["success"]:
            logger.info(f"✅ Query completed successfully with {model_used}")
            logger.info(f"⏱️ Total execution time: {total_time:.2f}s")
            
            return QueryResponse(
                success=True,
                plan_run_id=result["result"].get("plan_run_id") if result.get("result") else None,
                result=result["result"],
                execution_time_seconds=total_time,
                model_used=model_used
            )
        else:
            logger.error(f"❌ All models failed: {result['error']}")
            raise HTTPException(
                status_code=500,
                detail=f"AI processing failed: {result['error']}"
            )
            
    except Exception as e:
        total_time = time.time() - start_time
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"💥 {error_msg}")
        
        return QueryResponse(
            success=False,
            error=error_msg,
            execution_time_seconds=total_time,
            model_used="none"
        )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Nexus AI Backend with Google Gemini Integration",
        "version": "3.0.0",
        "status": "running",
        "primary_model": "Google Gemini 1.5 Pro",
        "models_available": {
            "gemini_1_5_pro": bool(portia_gemini),
            "mistral_portia": bool(portia_mistral),
            "mistral_direct": bool(mistral_client)
        },
        "fallback_chain": [
            "Google Gemini 1.5 Pro (Primary)",
            "Mistral Portia (Secondary)",
            "Mistral Direct API (Final)"
        ]
    }

if __name__ == "__main__":
    logger.info("🚀 Starting Nexus AI Backend with Google Gemini...")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
