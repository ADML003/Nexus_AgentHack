#!/usr/bin/env python3
"""
Test client for the Nexus AI Backend API
This script demonstrates the Portia.ai integration and GitHub OAuth functionality
"""

import httpx
import asyncio
import json
from typing import Dict, Any

class NexusAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = httpx.AsyncClient()
    
    async def test_health(self) -> Dict[str, Any]:
        """Test the health endpoint"""
        response = await self.session.get(f"{self.base_url}/health")
        return response.json()
    
    async def test_query(self, query: str) -> Dict[str, Any]:
        """Test the Portia query endpoint"""
        response = await self.session.post(
            f"{self.base_url}/api/query",
            json={"query": query}
        )
        return response.json()
    
    async def close(self):
        """Close the HTTP session"""
        await self.session.aclose()

async def run_demo():
    """Run a demonstration of the API"""
    client = NexusAPIClient()
    
    try:
        print("🚀 Nexus AI Backend Demo with Portia.ai Integration")
        print("=" * 60)
        
        # Test health endpoint
        print("\n1. Testing Health Endpoint...")
        health = await client.test_health()
        print(f"   Status: {health}")
        
        # Test basic math query
        print("\n2. Testing Portia AI Agent - Basic Math...")
        math_query = "What is 15 * 24?"
        print(f"   Query: {math_query}")
        
        result = await client.test_query(math_query)
        print(f"   Plan Run ID: {result['plan_run_id']}")
        print(f"   State: {result['state']}")
        print(f"   Final Output: {result['final_output']}")
        
        # Test more complex query
        print("\n3. Testing Portia AI Agent - Complex Query...")
        complex_query = "Calculate the compound interest for $1000 at 5% annual rate for 3 years"
        print(f"   Query: {complex_query}")
        
        result2 = await client.test_query(complex_query)
        print(f"   Plan Run ID: {result2['plan_run_id']}")
        print(f"   State: {result2['state']}")
        print(f"   Final Output: {result2['final_output']}")
        
        # Test reasoning query
        print("\n4. Testing Portia AI Agent - Reasoning Query...")
        reasoning_query = "If I have 3 apples and give away 2, then buy 5 more, how many apples do I have?"
        print(f"   Query: {reasoning_query}")
        
        result3 = await client.test_query(reasoning_query)
        print(f"   Plan Run ID: {result3['plan_run_id']}")
        print(f"   State: {result3['state']}")
        print(f"   Final Output: {result3['final_output']}")
        
        print("\n✅ Demo completed successfully!")
        print("\n📝 GitHub OAuth Endpoints Available:")
        print("   POST /api/auth/github/exchange - Exchange GitHub code for token")
        print("   GET  /api/auth/github/user    - Get authenticated user info")
        print("   GET  /api/auth/github/repos   - Get user's repositories")
        
        print("\n🌐 API Documentation:")
        print("   http://localhost:8000/docs - Interactive API documentation")
        print("   http://localhost:8000/redoc - Alternative API documentation")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(run_demo())
