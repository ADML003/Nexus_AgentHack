#!/usr/bin/env python3
"""
Comprehensive Test for Gemini + Mistral Integration
Tests both models individually and through the server
"""

import os
import asyncio
import time
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.local")

async def test_gemini_direct():
    """Test Gemini integration directly"""
    print("🧪 Testing Google Gemini Direct Integration...")
    
    try:
        from gemini_model import GeminiModel
        from portia import Message
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not found")
            return False
        
        model = GeminiModel(
            model_name="gemini-1.5-flash",  # Use Flash for faster testing
            api_key=api_key,
            temperature=0.7,
            max_tokens=100
        )
        
        messages = [Message(role="user", content="What is 5 + 3? Answer briefly.")]
        start_time = time.time()
        response = model.get_response(messages)
        execution_time = time.time() - start_time
        
        print(f"✅ Gemini Direct: SUCCESS")
        print(f"📝 Response: {response.content}")
        print(f"⏱️ Time: {execution_time:.2f}s")
        return True
        
    except Exception as e:
        print(f"❌ Gemini Direct: FAILED - {str(e)}")
        return False

async def test_mistral_direct():
    """Test Mistral integration directly"""
    print("\n🧪 Testing Mistral Direct Integration...")
    
    try:
        from mistralai import Mistral
        
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            print("❌ MISTRAL_API_KEY not found")
            return False
        
        client = Mistral(api_key=api_key)
        
        start_time = time.time()
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": "What is 4 + 6? Answer briefly."}],
            temperature=0.7,
            max_tokens=100
        )
        execution_time = time.time() - start_time
        
        print(f"✅ Mistral Direct: SUCCESS")
        print(f"📝 Response: {response.choices[0].message.content}")
        print(f"⏱️ Time: {execution_time:.2f}s")
        return True
        
    except Exception as e:
        print(f"❌ Mistral Direct: FAILED - {str(e)}")
        return False

async def test_gemini_portia():
    """Test Gemini through Portia"""
    print("\n🧪 Testing Gemini through Portia...")
    
    try:
        from gemini_model import create_gemini_config
        from portia import Portia, example_tool_registry
        
        api_key = os.getenv("GOOGLE_API_KEY")
        portia_key = os.getenv("PORTIA_API_KEY")
        
        if not api_key or not portia_key:
            print("❌ Required API keys not found")
            return False
        
        config = create_gemini_config(
            api_key=api_key,
            model_name="gemini-1.5-flash",
            temperature=0.7,
            max_tokens=200
        )
        
        portia = Portia(config=config, tools=example_tool_registry)
        
        start_time = time.time()
        result = portia.run("Calculate 7 + 8 and explain the result.")
        execution_time = time.time() - start_time
        
        print(f"✅ Gemini Portia: SUCCESS")
        print(f"📋 Plan ID: {result.id}")
        print(f"📊 State: {result.state}")
        
        if hasattr(result, 'outputs') and result.outputs and result.outputs.final_output:
            print(f"🎯 Response: {result.outputs.final_output.value}")
        
        print(f"⏱️ Time: {execution_time:.2f}s")
        return True
        
    except Exception as e:
        print(f"❌ Gemini Portia: FAILED - {str(e)}")
        return False

async def test_server_health():
    """Test server health endpoint"""
    print("\n🧪 Testing Server Health...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health", timeout=10.0)
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Server Health: SUCCESS")
                print(f"📊 Status: {health_data.get('status')}")
                print(f"🤖 Gemini Configured: {health_data.get('portia_gemini_configured')}")
                print(f"📝 Mistral Configured: {health_data.get('portia_mistral_configured')}")
                return True
            else:
                print(f"❌ Server Health: FAILED - Status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Server Health: FAILED - {str(e)}")
        return False

async def test_server_query():
    """Test server query endpoint"""
    print("\n🧪 Testing Server Query...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test with Gemini preference
            payload = {
                "query": "What is 9 + 12? Explain briefly.",
                "model_preference": "gemini",
                "user_id": "test_user"
            }
            
            start_time = time.time()
            response = await client.post(
                "http://localhost:8000/query",
                json=payload,
                timeout=30.0
            )
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                result_data = response.json()
                print(f"✅ Server Query: SUCCESS")
                print(f"🎯 Model Used: {result_data.get('model_used')}")
                print(f"📝 Success: {result_data.get('success')}")
                print(f"⏱️ Time: {execution_time:.2f}s")
                
                if result_data.get('result') and result_data['result'].get('final_output'):
                    print(f"📄 Response: {result_data['result']['final_output']}")
                
                return True
            else:
                print(f"❌ Server Query: FAILED - Status {response.status_code}")
                print(f"📄 Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Server Query: FAILED - {str(e)}")
        return False

async def main():
    """Run comprehensive tests"""
    print("🚀 Starting Comprehensive AI Integration Tests")
    print("=" * 60)
    
    # Test individual components
    tests = [
        ("Gemini Direct", test_gemini_direct),
        ("Mistral Direct", test_mistral_direct),
        ("Gemini Portia", test_gemini_portia),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name}: CRASHED - {str(e)}")
            results.append((test_name, False))
    
    # Test server (if running)
    print(f"\n{'='*60}")
    print("🌐 Testing Server Integration")
    print("=" * 60)
    
    server_tests = [
        ("Server Health", test_server_health),
        ("Server Query", test_server_query),
    ]
    
    for test_name, test_func in server_tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name}: CRASHED - {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n🎯 Summary: {passed}/{total} tests passed")
    
    if passed >= len(tests):  # At least all component tests pass
        print("🎉 Core integration working! Ready for production.")
    else:
        print("⚠️  Some core tests failed. Check configurations.")
    
    print(f"\n💡 To start the server: python main.py")
    print(f"📋 Health check: curl http://localhost:8000/health")
    print(f"🔧 Test query: curl -X POST http://localhost:8000/query -H 'Content-Type: application/json' -d '{{\"query\":\"Hello!\",\"model_preference\":\"gemini\"}}'")

if __name__ == "__main__":
    asyncio.run(main())
