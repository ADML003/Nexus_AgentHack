#!/usr/bin/env python3
"""
Robust API Testing Script
Tests the Nexus AI Backend with comprehensive error handling and retries
"""

import asyncio
import httpx
import json
import time
import sys
from typing import Dict, Any, Optional

class RobustAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.timeout = 30.0
        
    async def test_health(self) -> Dict[str, Any]:
        """Test health endpoint with retries"""
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(f"{self.base_url}/health")
                    if response.status_code == 200:
                        return {"success": True, "data": response.json()}
                    else:
                        return {"success": False, "error": f"Status {response.status_code}: {response.text}"}
            except httpx.ConnectError:
                if attempt < 2:
                    print(f"   Connection failed, retrying in {2 ** attempt} seconds...")
                    await asyncio.sleep(2 ** attempt)
                    continue
                return {"success": False, "error": "Server not responding after retries"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Max retries exceeded"}
    
    async def test_query(self, query: str) -> Dict[str, Any]:
        """Test query endpoint with proper error handling"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {"query": query}
                response = await client.post(
                    f"{self.base_url}/api/query",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {"success": True, "data": data}
                else:
                    return {"success": False, "error": f"Status {response.status_code}: {response.text}"}
                    
        except httpx.TimeoutException:
            return {"success": False, "error": "Request timed out - this might indicate API rate limiting"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_status(self) -> Dict[str, Any]:
        """Test status endpoint"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/status")
                if response.status_code == 200:
                    return {"success": True, "data": response.json()}
                else:
                    return {"success": False, "error": f"Status {response.status_code}: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

async def main():
    print("🧪 Robust Nexus AI Backend API Testing")
    print("=" * 50)
    
    tester = RobustAPITester()
    
    # Test 1: Health Check
    print("\n1. Testing Health Endpoint...")
    health_result = await tester.test_health()
    if health_result["success"]:
        data = health_result["data"]
        print("   ✅ Health check passed!")
        print(f"   📊 Status: {data.get('status')}")
        print(f"   🤖 Portia: {'✅' if data.get('portia_configured') else '❌'}")
        print(f"   🧠 Mistral: {'✅' if data.get('mistral_configured') else '❌'}")
    else:
        print(f"   ❌ Health check failed: {health_result['error']}")
        print("\n💡 Make sure the server is running:")
        print("   cd /Users/ADML/Desktop/Nexus/backend")
        print("   /Users/ADML/Desktop/Nexus/.venv/bin/python main.py")
        return
    
    # Test 2: Status Endpoint
    print("\n2. Testing Status Endpoint...")
    status_result = await tester.test_status()
    if status_result["success"]:
        print("   ✅ Status endpoint working!")
        data = status_result["data"]
        portia_info = data.get("portia", {})
        print(f"   🔧 Model: {portia_info.get('model', 'unknown')}")
        print(f"   🔑 API Keys: {len([k for k, v in data.get('environment', {}).items() if v])} configured")
    else:
        print(f"   ❌ Status check failed: {status_result['error']}")
    
    # Test 3: Simple Query
    print("\n3. Testing AI Query (Simple Math)...")
    query_result = await tester.test_query("What is 10 + 5?")
    if query_result["success"]:
        data = query_result["data"]
        if data.get("success"):
            print("   ✅ Query successful!")
            result = data.get("result", {})
            print(f"   🎯 Plan Run ID: {result.get('plan_run_id', 'N/A')}")
            print(f"   ⏱️  Execution Time: {data.get('execution_time_seconds', 0):.2f}s")
            final_output = result.get("final_output", {})
            print(f"   🧮 Result: {final_output.get('value', 'No result')}")
        else:
            print(f"   ❌ Query failed: {data.get('error')}")
            if "429" in str(data.get('error', '')):
                print("   💡 This is likely a rate limit issue. Try again in a few minutes.")
    else:
        print(f"   ❌ Query request failed: {query_result['error']}")
    
    # Test 4: Complex Query
    print("\n4. Testing AI Query (Complex)...")
    complex_query = "Explain the difference between machine learning and artificial intelligence in simple terms"
    complex_result = await tester.test_query(complex_query)
    if complex_result["success"]:
        data = complex_result["data"]
        if data.get("success"):
            print("   ✅ Complex query successful!")
            print(f"   ⏱️  Execution Time: {data.get('execution_time_seconds', 0):.2f}s")
            result = data.get("result", {})
            final_output = result.get("final_output", {})
            answer = final_output.get("value", "")
            if len(answer) > 100:
                print(f"   📝 Answer: {answer[:100]}...")
            else:
                print(f"   📝 Answer: {answer}")
        else:
            print(f"   ❌ Complex query failed: {data.get('error')}")
    else:
        print(f"   ❌ Complex query request failed: {complex_result['error']}")
    
    print("\n🏁 Testing Complete!")
    print("\n📊 Summary:")
    print(f"   • Health: {'✅' if health_result['success'] else '❌'}")
    print(f"   • Status: {'✅' if status_result['success'] else '❌'}")
    print(f"   • Simple Query: {'✅' if query_result['success'] and query_result['data'].get('success') else '❌'}")
    print(f"   • Complex Query: {'✅' if complex_result['success'] and complex_result['data'].get('success') else '❌'}")

if __name__ == "__main__":
    asyncio.run(main())
