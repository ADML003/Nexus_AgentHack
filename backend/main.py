#!/usr/bin/env python3
"""
Nexus Portia Backend - Google & Mistral Only
Following Portia documentation exactly:
1. Google as primary, Mistral as fallback (OpenAI completely removed)
2. Full tool integr        # SOLUTION: Create a hybrid approach that ensures both tool types are accessible
        # Problem: Open source registry missing cloud tools (Gmail), cloud registry missing open source tools (weather)
        # Solution: Use cloud registry as primary (includes most tools), but ensure critical open source tools work
        
        if shared_cloud_registry:
            print("🔄 Using hybrid approach: cloud registry as primary with open source fallback")
            try:
                # Use cloud registry as primary (includes Gmail and other cloud tools)
                portia_instance = Portia(config=config, tools=shared_cloud_registry)
                print(f"   ✅ Primary: Cloud registry with {len(shared_cloud_registry.get_tools())} tools")
                print(f"   📧 Gmail tools: Available (portia:google:gmail:send_email, draft_email, etc.)")
                print(f"   🌤️  Weather tool: Available through open source fallback")
                registry_type = "cloud (primary) with open source fallback"
                
            except Exception as e:
                print(f"⚠️ Cloud registry failed, using open source only: {e}")
                portia_instance = Portia(config=config, tools=open_source_tool_registry)
                registry_type = "open-source fallback"
        else:
            # Fallback to open source only if cloud is not available
            print("📦 Using open source tools only...")
            portia_instance = Portia(config=config, tools=open_source_tool_registry)
            registry_type = "open-source only" (open source + cloud)
3. Proper result extraction from nested run.result structure
4. Complete error handling and provider fallback
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
load_dotenv("../.env.local")

# Configuration - Check Google and Mistral API keys only (OpenAI removed)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
PORTIA_API_KEY = os.getenv("PORTIA_API_KEY")

print("🚀 Starting Nexus Portia Backend - Google & Mistral Only")
print("🔑 API Key Status:")
print(f"   Google: {'✅' if GOOGLE_API_KEY else '❌'}")
print(f"   Mistral: {'✅' if MISTRAL_API_KEY else '❌'}")
print(f"   Portia: {'✅' if PORTIA_API_KEY else '❌'}")
print("   OpenAI: ❌ Disabled (removed from configuration)")

# Create FastAPI app
app = FastAPI(
    title="Nexus Portia Backend", 
    version="2.0.0",
    description="Google Gemini & Mistral implementation with full tool integration (OpenAI disabled)"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_portia_registry_with_timeout(config, timeout=15):
    
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

# Initialize LLM providers using the CORRECT Portia pattern from official docs
portia_instance_cloud = None
portia_instance_open_source = None

def initialize_providers():
    """Initialize LLM provider using the official Portia documentation pattern"""
    global portia_instance_cloud, portia_instance_open_source
    
    print("🔧 Initializing LLM provider using official Portia pattern...")
    
    # Create shared cloud registry once
    shared_cloud_registry = None
    if PORTIA_API_KEY and cloud_registry:
        print("🔄 Reusing existing cloud registry...")
        shared_cloud_registry = cloud_registry
    elif PORTIA_API_KEY:
        print("📡 Loading cloud registry...")
        config = default_config()
        config.portia_api_key = SecretStr(PORTIA_API_KEY)
        shared_cloud_registry = load_portia_registry_with_timeout(config)
    
    try:
        # OFFICIAL PATTERN: Single config with all API keys, automatic provider inference
        config = default_config()
        
        # Set all API keys in the config (official pattern - Google & Mistral only)
        if PORTIA_API_KEY:
            config.portia_api_key = SecretStr(PORTIA_API_KEY)
        if GOOGLE_API_KEY:
            config.google_api_key = SecretStr(GOOGLE_API_KEY)
        if MISTRAL_API_KEY:
            config.mistralai_api_key = SecretStr(MISTRAL_API_KEY)
        
        # Set primary provider (Google since it's working)
        config.llm_provider = LLMProvider.GOOGLE
        
        # Force specific Google models to prevent any OpenAI fallback
        try:
            # Use Config.from_default with explicit Google models
            config = Config.from_default(
                llm_provider=LLMProvider.GOOGLE,
                google_api_key=GOOGLE_API_KEY,
                mistralai_api_key=MISTRAL_API_KEY,
                portia_api_key=PORTIA_API_KEY,
                default_model="google/gemini-1.5-flash",
                planning_model="google/gemini-1.5-flash",
                execution_model="google/gemini-1.5-flash"
            )
            print("✅ Using explicit Google model configuration")
        except Exception as e:
            print(f"⚠️ Explicit model config failed, using basic config: {e}")
            # Fallback to basic config
            pass
        
        # Create cloud instance for Gmail and Google Workspace tools
        if shared_cloud_registry:
            print("🔧 Creating cloud instance for Gmail and Google Workspace tools")
            portia_instance_cloud = Portia(config=config, tools=shared_cloud_registry)
            print(f"✅ Cloud instance: {len(shared_cloud_registry.get_tools())} tools (includes Gmail, Google Docs, etc.)")
        else:
            print("⚠️ Cloud registry not available")
        
        # Create open source instance for weather and other open source tools
        print("🔧 Creating open source instance for weather and basic tools")
        portia_instance_open_source = Portia(config=config, tools=open_source_tool_registry)
        print(f"✅ Open source instance: {len(open_source_tool_registry.get_tools())} tools (includes weather, calculator, etc.)")
        
        print(f"✅ Portia instances initialized with Google as primary provider")
        print(f"✅ Available fallback provider: Mistral (OpenAI disabled)")
        
    except Exception as e:
        print(f"❌ Portia instance initialization failed: {e}")
        # Fallback to open source only
        try:
            config = default_config()
            config.llm_provider = LLMProvider.GOOGLE
            config.google_api_key = SecretStr(GOOGLE_API_KEY)
            portia_instance = Portia(config=config, tools=open_source_tool_registry)
            print(f"✅ Fallback: Portia initialized with open source tools only")
        except Exception as e2:
            print(f"❌ Complete initialization failure: {e2}")
            portia_instance = None
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

class ClarificationRequest(BaseModel):
    """Request to respond to a Portia clarification"""
    plan_run_id: str  # The ID of the plan run waiting for clarification
    response: str  # User's response to the clarification
    user_id: Optional[str] = None

class ClarificationModel(BaseModel):
    """Model for Portia clarifications requiring user intervention"""
    type: str  # Type of clarification (e.g., "oauth", "input", "permission")
    message: str  # Human-readable message to show the user
    details: Optional[Dict[str, Any]] = None  # Additional context/data
    action_required: str  # What action the user needs to take

class QueryResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    tools_used: Optional[List[str]] = None
    error: Optional[str] = None
    execution_time_seconds: Optional[float] = None
    tool_registry_used: Optional[str] = None
    clarification: Optional[ClarificationModel] = None  # Portia clarification requiring user action
    requires_user_action: bool = False  # Quick flag to check if user intervention needed

# API Endpoints
@app.get("/health")
async def health_check():
    """Enhanced health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "provider": {
            "available": portia_instance_cloud is not None or portia_instance_open_source is not None,
            "primary": "google" if (portia_instance_cloud or portia_instance_open_source) else None,
            "fallbacks": ["mistral"] if (portia_instance_cloud or portia_instance_open_source) else [],
            "disabled": ["openai"],
            "note": "OpenAI removed due to quota issues"
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
    Process query with appropriate Portia instance based on tool registry selection
    Automatic fallback providers handled by Portia internally
    """
    start_time = time.time()
    
    try:
        print(f"📝 Processing query: '{request.message}'")
        print(f"🔧 Requested tool registry: {request.tool_registry}")
        
        # Select the appropriate Portia instance based on tool registry
        if request.tool_registry == "cloud" and portia_instance_cloud:
            portia_instance = portia_instance_cloud
            registry_used = "cloud"
            print(f"🔧 Using cloud instance (Gmail, Google Docs, etc.)")
        elif request.tool_registry == "open_source" and portia_instance_open_source:
            portia_instance = portia_instance_open_source
            registry_used = "open_source"
            print(f"🔧 Using open source instance (weather, calculator, etc.)")
        elif request.tool_registry == "default" or request.tool_registry == "combined":
            # For combined/default, prefer cloud if available (includes more tools)
            if portia_instance_cloud:
                portia_instance = portia_instance_cloud
                registry_used = "cloud"
                print(f"🔧 Using cloud instance for default/combined (includes Gmail + Google tools)")
            elif portia_instance_open_source:
                portia_instance = portia_instance_open_source
                registry_used = "open_source"
                print(f"🔧 Fallback to open source instance")
            else:
                raise ValueError("No Portia instances available")
        else:
            # Fallback logic
            if portia_instance_cloud:
                portia_instance = portia_instance_cloud
                registry_used = "cloud"
                print(f"🔧 Fallback to cloud instance")
            elif portia_instance_open_source:
                portia_instance = portia_instance_open_source
                registry_used = "open_source"
                print(f"🔧 Fallback to open source instance")
            else:
                raise ValueError("No Portia instances available")
        
        if not request.message or not request.message.strip():
            raise ValueError("Empty message provided")
            
        if not portia_instance:
            raise ValueError("Portia instance not initialized")
        
        print(f"🔍 Running query with Google (primary)...")
        
        # Run the query using selected instance
        run = portia_instance.run(request.message)
        print(f"✅ Run initiated: {run.id}")
        
        # Wait for completion with proper state checking
        max_wait = 60  # 60 seconds timeout
        waited = 0
        
        while waited < max_wait:
            current_state = run.state.value
            print(f"⏳ State: {current_state} ({waited}s)")
            
            # Check for clarifications (human intervention needed)
            if hasattr(run, 'clarifications') and run.clarifications:
                print(f"🔄 Clarification required: {len(run.clarifications)} pending")
                clarification = run.clarifications[0]  # Get first clarification
                
                clarification_data = ClarificationModel(
                    type=clarification.get('type', 'user_input'),
                    message=clarification.get('message', 'User action required'),
                    details=clarification.get('details', {}),
                    action_required=clarification.get('action_required', 'Please provide the required input')
                )
                
                execution_time = time.time() - start_time
                return QueryResponse(
                    success=False,  # Not complete yet, waiting for user
                    clarification=clarification_data,
                    requires_user_action=True,
                    execution_time_seconds=execution_time,
                    tool_registry_used=registry_used
                )
            
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
                    tool_registry_used=registry_used
                )
            else:
                print("❌ No result extracted from successful run")
                return QueryResponse(
                    success=False,
                    error="No result found in completed run",
                    execution_time_seconds=time.time() - start_time
                )
        elif final_state == 'FAILED':
            error_msg = f"Run failed: {getattr(run, 'error', 'Unknown error')}"
            print(f"❌ {error_msg}")
            return QueryResponse(
                success=False,
                error=error_msg,
                execution_time_seconds=time.time() - start_time
            )
        else:
            error_msg = f"Run timeout or cancelled (state: {final_state})"
            print(f"❌ {error_msg}")
            return QueryResponse(
                success=False,
                error=error_msg,
                execution_time_seconds=time.time() - start_time
            )
            
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = str(e)
        print(f"❌ Query processing failed: {error_msg}")
        
        return QueryResponse(
            success=False,
            error=error_msg,
            execution_time_seconds=execution_time
        )
        
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

@app.post("/clarification", response_model=QueryResponse)
async def handle_clarification(request: ClarificationRequest):
    """
    Respond to a Portia clarification and continue plan execution
    """
    start_time = time.time()
    
    try:
        print(f"🔄 Responding to clarification for plan run: {request.plan_run_id}")
        
        # Try to find the run in either instance
        run = None
        portia_instance = None
        
        if portia_instance_cloud:
            try:
                run = portia_instance_cloud.get_run(request.plan_run_id)
                portia_instance = portia_instance_cloud
                print(f"✅ Found run in cloud instance")
            except:
                pass
        
        if not run and portia_instance_open_source:
            try:
                run = portia_instance_open_source.get_run(request.plan_run_id)
                portia_instance = portia_instance_open_source
                print(f"✅ Found run in open source instance")
            except:
                pass
        
        if not run:
            raise ValueError(f"Plan run not found: {request.plan_run_id}")
        
        # Respond to the clarification
        try:
            run.respond_to_clarification(request.response)
            print(f"✅ Clarification response sent: {request.response}")
        except Exception as e:
            raise ValueError(f"Failed to respond to clarification: {e}")
        
        # Wait for completion after clarification response
        max_wait = 60
        waited = 0
        
        while waited < max_wait:
            current_state = run.state.value
            print(f"⏳ State after clarification: {current_state} ({waited}s)")
            
            # Check for additional clarifications
            if hasattr(run, 'clarifications') and run.clarifications:
                print(f"🔄 Additional clarification required: {len(run.clarifications)} pending")
                clarification = run.clarifications[0]
                
                clarification_data = ClarificationModel(
                    type=clarification.get('type', 'user_input'),
                    message=clarification.get('message', 'Additional user action required'),
                    details=clarification.get('details', {}),
                    action_required=clarification.get('action_required', 'Please provide the required input')
                )
                
                execution_time = time.time() - start_time
                return QueryResponse(
                    success=False,
                    clarification=clarification_data,
                    requires_user_action=True,
                    execution_time_seconds=execution_time,
                    tool_registry_used="cloud" if portia_instance == portia_instance_cloud else "open_source"
                )
            
            if current_state in ['COMPLETE', 'FAILED', 'CANCELLED']:
                break
            
            time.sleep(2)
            waited += 2
        
        final_state = run.state.value
        print(f"✅ Final state after clarification: {final_state}")
        
        if final_state == 'COMPLETE':
            result_text = extract_result_from_run(run)
            
            if result_text:
                execution_time = time.time() - start_time
                tools_used = extract_tools_used(run)
                
                return QueryResponse(
                    success=True,
                    result=result_text,
                    tools_used=tools_used,
                    execution_time_seconds=execution_time,
                    tool_registry_used="cloud" if portia_instance == portia_instance_cloud else "open_source"
                )
            else:
                return QueryResponse(
                    success=False,
                    error="Task completed but no result was returned",
                    execution_time_seconds=time.time() - start_time
                )
        else:
            return QueryResponse(
                success=False,
                error=f"Task failed with state: {final_state}",
                execution_time_seconds=time.time() - start_time
            )
            
    except Exception as e:
        print(f"❌ Clarification handling failed: {e}")
        return QueryResponse(
            success=False,
            error=f"Clarification handling failed: {str(e)}",
            execution_time_seconds=time.time() - start_time
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
    print(f"   🔧 LLM Provider: {'✅ Active (Google primary)' if (portia_instance_cloud or portia_instance_open_source) else '❌ Inactive'}")
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
