#!/usr/bin/env python3
"""
Nexus Portia Backend - Proper Implementation
Following Portia documentation exactly:
1. Google as primary, Mistral as secondary, OpenAI as tertiary (reordered due to OpenAI quota limits)
2. Full tool integration (open source + cloud)
3. Proper result extraction from nested run.result structure
4. Complete error handling and multi-provider fallback
"""

import os
import time
import concurrent.futures
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, SecretStr
from dotenv import load_dotenv

from portia import (
    Portia,
    Config,
    LLMProvider,
    PortiaToolRegistry,
    open_source_tool_registry,
    default_config
)
from pydantic import SecretStr

# Load environment variables
load_dotenv(".env.local")

# Configuration - Check all API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
PORTIA_API_KEY = os.getenv("PORTIA_API_KEY")

print("🚀 Starting Nexus Portia Backend - Proper Implementation")
print("🔑 API Key Status:")
print(f"   OpenAI: {'✅' if OPENAI_API_KEY else '❌'}")
print(f"   Google: {'✅' if GOOGLE_API_KEY else '❌'}")
print(f"   Mistral: {'✅' if MISTRAL_API_KEY else '❌'}")
print(f"   Portia: {'✅' if PORTIA_API_KEY else '❌'}")

# Create FastAPI app
app = FastAPI(
    title="Nexus Portia Backend", 
    version="2.0.0",
    description="Proper implementation with Google->Mistral->OpenAI fallback and full tool integration"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Timeout handling for PortiaToolRegistry initialization
def load_portia_registry_with_timeout(config, timeout=15):
    """
    Load PortiaToolRegistry with timeout handling to prevent hanging
    Best practice: Add retry logic and fallback states for cloud registry
    """
    print(f"   📡 Loading cloud tool registry (timeout: {timeout}s)...")
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(PortiaToolRegistry, config=config)
        try:
            start_time = time.time()
            registry = future.result(timeout=timeout)
            load_time = time.time() - start_time
            print(f"   ✅ Cloud registry loaded in {load_time:.2f}s")
            return registry
        except concurrent.futures.TimeoutError:
            print(f"   ⏰ Timeout: PortiaToolRegistry initialization took longer than {timeout}s")
            print("   🔄 Falling back to open source tools only")
            return None
        except Exception as e:
            print(f"   ❌ Cloud registry failed: {e}")
            print("   🔄 Falling back to open source tools only")
            return None

def create_portia_instance_with_timeout(config, timeout=15):
    """
    Create Portia instance with timeout-protected registry loading
    """
    try:
        # Load registry with timeout protection
        tools_registry = load_portia_registry_with_timeout(config, timeout)
        
        if tools_registry is None:
            # Fallback to open source tools only
            print("   📦 Using open source tools as fallback")
            return Portia(config=config, tools=open_source_tool_registry)
        
        # Use cloud registry
        return Portia(config=config, tools=tools_registry)
        
    except Exception as e:
        print(f"   ❌ Portia instance creation failed: {e}")
        # Final fallback to open source only
        print("   📦 Final fallback to open source tools")
        return Portia(config=config, tools=open_source_tool_registry)

# Initialize tool registries
def initialize_tool_registries():
    """Initialize both open source and cloud tool registries with timeout protection"""
    print("📦 Loading tool registries...")
    
    # Open source tools
    os_tools = open_source_tool_registry.get_tools()
    print(f"✅ Open Source Tools: {len(os_tools)} loaded")
    
    # Cloud tools using timeout-protected loading
    cloud_tools = []
    cloud_registry = None
    if PORTIA_API_KEY:
        try:
            print("☁️ Loading cloud tool registry...")
            # Use timeout-protected loading with proper config
            config = default_config()
            if PORTIA_API_KEY:
                config.portia_api_key = SecretStr(PORTIA_API_KEY)
            cloud_registry = load_portia_registry_with_timeout(config)
            if cloud_registry:
                cloud_tools = cloud_registry.get_tools()
                print(f"✅ Cloud Tools: {len(cloud_tools)} loaded")
            else:
                print("⚠️ Cloud tools registry timeout - using open source only")
        except Exception as e:
            print(f"⚠️ Cloud tools not available: {e}")
    else:
        print("⚠️ No PORTIA_API_KEY - cloud tools disabled")
    
    return os_tools, cloud_tools, cloud_registry

# Initialize tools (for health check and tool listing endpoints)
os_tools, cloud_tools, cloud_registry = initialize_tool_registries()
total_tools = len(os_tools) + len(cloud_tools)

# Note: Using official PortiaToolRegistry pattern in provider initialization
# Each Portia instance automatically gets the latest cloud tools from dashboard
print(f"📊 Tool Summary: {len(os_tools)} open source, {len(cloud_tools)} cloud tools available")
print("☁️  Cloud tools are managed via Portia dashboard and automatically reflected")

# Initialize LLM providers in order: Google -> Mistral -> OpenAI (reordered due to OpenAI quota)
portia_instances = []

def initialize_providers():
    """Initialize LLM providers using timeout-protected cloud registry (reused)"""
    global portia_instances
    
    print("🔧 Initializing LLM providers (Google -> Mistral -> OpenAI) with timeout protection...")
    
    # Create shared cloud registry once to avoid multiple API calls
    shared_cloud_registry = None
    if PORTIA_API_KEY and cloud_registry:
        print("🔄 Reusing existing cloud registry for providers...")
        shared_cloud_registry = cloud_registry
    elif PORTIA_API_KEY:
        print("📡 Loading shared cloud registry for all providers...")
        shared_cloud_registry = load_portia_registry_with_timeout(default_config())
    
    # Provider 1: Google (primary - working)
    if GOOGLE_API_KEY:
        try:
            print("🔍 Initializing Google with shared cloud registry...")
            # Create config
            config = default_config()
            config.llm_provider = LLMProvider.GOOGLE
            config.google_api_key = SecretStr(GOOGLE_API_KEY)
            config.portia_api_key = SecretStr(PORTIA_API_KEY)
            
            # Use shared registry or fallback to open source
            tools_to_use = shared_cloud_registry if shared_cloud_registry else open_source_tool_registry
            google_portia = Portia(config=config, tools=tools_to_use)
            
            portia_instances.append(("google", google_portia))
            registry_type = "cloud" if shared_cloud_registry else "open-source"
            print(f"✅ Google AI provider initialized with {registry_type} tool registry")
        except Exception as e:
            print(f"⚠️ Google provider failed: {e}")
    
    # Provider 2: Mistral (secondary - working)  
    if MISTRAL_API_KEY:
        try:
            print("🔍 Initializing Mistral with shared cloud registry...")
            # Create config
            config = default_config()
            config.llm_provider = LLMProvider.MISTRALAI
            config.mistralai_api_key = SecretStr(MISTRAL_API_KEY)
            config.portia_api_key = SecretStr(PORTIA_API_KEY)
            
            # Use shared registry or fallback to open source
            tools_to_use = shared_cloud_registry if shared_cloud_registry else open_source_tool_registry
            mistral_portia = Portia(config=config, tools=tools_to_use)
            
            portia_instances.append(("mistral", mistral_portia))
            registry_type = "cloud" if shared_cloud_registry else "open-source"
            print(f"✅ Mistral AI provider initialized with {registry_type} tool registry")
        except Exception as e:
            print(f"⚠️ Mistral provider failed: {e}")

    # Provider 3: OpenAI (tertiary - has quota issues)
    if OPENAI_API_KEY:
        try:
            print("🔍 Initializing OpenAI with shared cloud registry...")
            # Create config
            config = default_config()
            config.llm_provider = LLMProvider.OPENAI
            config.openai_api_key = SecretStr(OPENAI_API_KEY)
            config.portia_api_key = SecretStr(PORTIA_API_KEY)
            
            # Use shared registry or fallback to open source
            tools_to_use = shared_cloud_registry if shared_cloud_registry else open_source_tool_registry
            openai_portia = Portia(config=config, tools=tools_to_use)
            
            portia_instances.append(("openai", openai_portia))
            registry_type = "cloud" if shared_cloud_registry else "open-source"
            print(f"✅ OpenAI provider initialized with {registry_type} tool registry")
        except Exception as e:
            print(f"⚠️ OpenAI provider failed (quota issues): {e}")
            
            portia_instances.append(("google", google_portia))
            registry_type = "cloud" if shared_cloud_registry else "open-source"
            print(f"✅ Google AI provider initialized with {registry_type} tool registry")
        except Exception as e:
            print(f"⚠️ Google provider failed: {e}")
    
    # Provider 3: Mistral (tertiary)
    if MISTRAL_API_KEY:
        try:
            print("🔍 Initializing Mistral with shared cloud registry...")
            # Create config
            config = default_config()
            config.llm_provider = LLMProvider.MISTRALAI
            config.mistralai_api_key = SecretStr(MISTRAL_API_KEY)
            config.portia_api_key = SecretStr(PORTIA_API_KEY)
            
            # Use shared registry or fallback to open source
            tools_to_use = shared_cloud_registry if shared_cloud_registry else open_source_tool_registry
            mistral_portia = Portia(config=config, tools=tools_to_use)
            
            portia_instances.append(("mistral", mistral_portia))
            registry_type = "cloud" if shared_cloud_registry else "open-source"
            print(f"✅ Mistral AI provider initialized with {registry_type} tool registry")
        except Exception as e:
            print(f"⚠️ Mistral provider failed: {e}")

# Initialize providers
initialize_providers()

# Request/Response models
class QueryRequest(BaseModel):
    message: str
    use_tools: bool = True
    tool_registry: str = "combined"
    user_id: Optional[str] = None

class QueryResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    tools_used: Optional[List[str]] = None
    error: Optional[str] = None
    execution_time_seconds: Optional[float] = None
    tool_registry_used: Optional[str] = None

# API Endpoints
@app.get("/health")
async def health_check():
    """Enhanced health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "providers": {
            "count": len(portia_instances),
            "available": [name for name, _ in portia_instances],
            "openai_available": any(name == "openai" for name, _ in portia_instances),
            "google_available": any(name == "google" for name, _ in portia_instances),
            "mistral_available": any(name == "mistral" for name, _ in portia_instances),
        },
        "tools": {
            "open_source_count": len(os_tools),
            "cloud_count": len(cloud_tools), 
            "total_count": total_tools
        },
        "cloud_registry": {
            "available": cloud_registry is not None,
            "authenticated": PORTIA_API_KEY is not None
        }
    }

@app.get("/tools/open-source")
async def list_open_source_tools():
    """List available open source tools"""
    return {
        "success": True,
        "tools": [
            {
                "id": tool.id,
                "name": tool.name, 
                "description": tool.description,
                "category": getattr(tool, 'category', 'general')
            }
            for tool in os_tools
        ],
        "count": len(os_tools)
    }

@app.get("/tools/cloud") 
async def list_cloud_tools():
    """List available cloud tools"""
    return {
        "success": True,
        "tools": [
            {
                "id": tool.id,
                "name": tool.name,
                "description": tool.description, 
                "category": getattr(tool, 'category', 'cloud')
            }
            for tool in cloud_tools
        ],
        "count": len(cloud_tools),
        "available": len(cloud_tools) > 0
    }

@app.get("/tools/registries")
async def list_tool_registries():
    """List available tool registries and their status"""
    return {
        "success": True,
        "registries": {
            "open_source": {
                "name": "Open Source Tool Registry",
                "available": True,
                "tool_count": len(os_tools),
                "status": "active"
            },
            "cloud": {
                "name": "Portia Cloud Tool Registry", 
                "available": cloud_registry is not None,
                "tool_count": len(cloud_tools),
                "status": "active" if cloud_registry is not None else "disabled",
                "authenticated": PORTIA_API_KEY is not None
            }
        },
        "total_tools": total_tools,
        "summary": {
            "registries_active": 1 + (1 if cloud_registry is not None else 0),
            "total_registries": 2
        }
    }

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process query with proper multi-provider fallback and result extraction
    Following Portia documentation for nested result structure
    """
    start_time = time.time()
    
    try:
        print(f"📝 Processing query: '{request.message}'")
        print(f"🔧 Using {len(portia_instances)} providers: {[name for name, _ in portia_instances]}")
        
        if not request.message or not request.message.strip():
            raise ValueError("Empty message provided")
        
        last_error = None
        
        # Try each provider in priority order
        for provider_name, portia_instance in portia_instances:
            try:
                print(f"🔍 Trying {provider_name.upper()}...")
                
                # Run the query
                run = portia_instance.run(request.message)
                print(f"✅ Run initiated: {run.id}")
                
                # Wait for completion with proper state checking
                max_wait = 60  # 60 seconds timeout
                waited = 0
                
                while waited < max_wait:
                    current_state = run.state.value
                    print(f"⏳ State: {current_state} ({waited}s)")
                    
                    if current_state in ['COMPLETE', 'FAILED', 'CANCELLED']:
                        break
                    
                    time.sleep(2)
                    waited += 2
                
                final_state = run.state.value
                print(f"✅ Final state: {final_state}")
                
                if final_state == 'COMPLETE':
                    # Extract result using proper Portia documentation approach
                    result_text = extract_result_from_run(run)
                    
                    if result_text:
                        execution_time = time.time() - start_time
                        tools_used = extract_tools_used(run)
                        
                        return QueryResponse(
                            success=True,
                            result=result_text,
                            tools_used=tools_used,
                            execution_time_seconds=execution_time,
                            tool_registry_used=f"{request.tool_registry}_{provider_name}"
                        )
                    else:
                        print(f"⚠️ No result extracted from {provider_name.upper()}")
                        last_error = f"{provider_name}: No result extracted"
                        continue
                
                elif final_state == 'FAILED':
                    error_msg = extract_error_from_run(run)
                    print(f"❌ {provider_name.upper()} failed: {error_msg}")
                    last_error = f"{provider_name}: {error_msg}"
                    
                    # Check for rate limits and try next provider
                    if any(term in error_msg.lower() for term in ['rate limit', 'quota', 'capacity', '429']):
                        print("🔄 Rate limit detected, trying next provider...")
                        continue
                    
                elif final_state == 'CANCELLED':
                    print(f"⚠️ {provider_name.upper()} cancelled")
                    last_error = f"{provider_name}: Run cancelled"
                    continue
                
                else:
                    # Timeout case
                    print(f"⏰ {provider_name.upper()} timeout after {max_wait}s")
                    last_error = f"{provider_name}: Timeout after {max_wait}s"
                    continue
                    
            except Exception as e:
                error_msg = str(e)
                print(f"❌ {provider_name.upper()} exception: {error_msg}")
                last_error = f"{provider_name}: {error_msg}"
                continue
        
        # All providers failed
        execution_time = time.time() - start_time
        return QueryResponse(
            success=False,
            error=f"All providers failed. Last error: {last_error}",
            execution_time_seconds=execution_time,
            tool_registry_used="all_failed"
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"❌ Query processing error: {e}")
        return QueryResponse(
            success=False,
            error=str(e),
            execution_time_seconds=execution_time,
            tool_registry_used="error"
        )

def extract_result_from_run(run) -> Optional[str]:
    """
    Extract result from PlanRun following Portia documentation
    The result structure is nested: run.result contains the actual response
    """
    try:
        # Method 1: Direct result attribute (most common according to docs)
        if hasattr(run, 'result') and run.result is not None:
            result_value = run.result
            print(f"✅ Found result via run.result: {type(result_value)}")
            return str(result_value)
        
        # Method 2: Check outputs structure 
        if hasattr(run, 'outputs') and run.outputs:
            # Check final_output
            if hasattr(run.outputs, 'final_output') and run.outputs.final_output:
                final_out = run.outputs.final_output
                
                if hasattr(final_out, 'summary') and final_out.summary:
                    print("✅ Found result via outputs.final_output.summary")
                    return str(final_out.summary)
                
                if hasattr(final_out, 'value') and final_out.value:
                    print("✅ Found result via outputs.final_output.value")
                    return str(final_out.value)
            
            # Check step_outputs for $result
            if hasattr(run.outputs, 'step_outputs') and run.outputs.step_outputs:
                if '$result' in run.outputs.step_outputs:
                    step_result = run.outputs.step_outputs['$result']
                    if hasattr(step_result, 'summary') and step_result.summary:
                        print("✅ Found result via step_outputs.$result.summary")
                        return str(step_result.summary)
                    if hasattr(step_result, 'value') and step_result.value:
                        print("✅ Found result via step_outputs.$result.value")
                        return str(step_result.value)
        
        print("⚠️ No result found in run object")
        return None
        
    except Exception as e:
        print(f"❌ Error extracting result: {e}")
        return None

def extract_tools_used(run) -> Optional[List[str]]:
    """Extract list of tools used during execution"""
    try:
        tools_used = []
        
        if hasattr(run, 'outputs') and run.outputs:
            if hasattr(run.outputs, 'step_outputs') and run.outputs.step_outputs:
                for step_name, step_output in run.outputs.step_outputs.items():
                    if step_name != '$result':  # Don't include the result step
                        tools_used.append(step_name)
        
        return tools_used if tools_used else None
    except Exception as e:
        print(f"⚠️ Error extracting tools used: {e}")
        return None

def extract_error_from_run(run) -> str:
    """Extract error message from failed run"""
    try:
        if hasattr(run, 'outputs') and run.outputs:
            if hasattr(run.outputs, 'final_output') and run.outputs.final_output:
                if hasattr(run.outputs.final_output, 'value'):
                    return str(run.outputs.final_output.value)
        return "Unknown error occurred"
    except Exception as e:
        return f"Error extracting error message: {e}"

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🌟 Nexus Portia Backend - Ready!")
    print("="*60)
    print("📊 Summary:")
    print(f"   🔧 LLM Providers: {len(portia_instances)} ({[name for name, _ in portia_instances]})")
    print(f"   📦 Open Source Tools: {len(os_tools)}")
    print(f"   ☁️  Cloud Tools: {len(cloud_tools)}")
    print(f"   🔢 Total Tools: {total_tools}")
    print(f"   🔑 Cloud Registry: {'✅ Active' if cloud_registry else '❌ Inactive'}")
    print("="*60)
    print("🚀 Starting server on http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("="*60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
