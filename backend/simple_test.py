#!/usr/bin/env python3
"""
Simple API test using curl
"""
import subprocess
import time
import json

def test_health():
    """Test the health endpoint"""
    try:
        result = subprocess.run(['curl', '-s', 'http://localhost:8000/health'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            response = json.loads(result.stdout)
            print("✅ Health Check:")
            print(f"   Status: {response.get('status')}")
            print(f"   Portia Configured: {response.get('portia_configured')}")
            print(f"   Mistral Configured: {response.get('mistral_configured')}")
            return True
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_query():
    """Test the query endpoint"""
    try:
        query_data = {
            "query": "What is 5 + 7?"
        }
        
        result = subprocess.run([
            'curl', '-s', 
            '-X', 'POST',
            '-H', 'Content-Type: application/json',
            '-d', json.dumps(query_data),
            'http://localhost:8000/api/query'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            print("✅ Query Test:")
            print(f"   Success: {response.get('success')}")
            if response.get('success'):
                print(f"   Plan Run ID: {response.get('plan_run_id')}")
                print(f"   Execution Time: {response.get('execution_time_seconds'):.2f}s")
                final_output = response.get('result', {}).get('final_output', {})
                print(f"   Result: {final_output.get('value', 'No result')}")
            else:
                print(f"   Error: {response.get('error')}")
            return True
        else:
            print("❌ Query test failed")
            return False
    except Exception as e:
        print(f"❌ Query test error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Nexus AI Backend API")
    print("=" * 40)
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    # Test health endpoint
    if test_health():
        print()
        # Test query endpoint
        test_query()
    
    print("\n🏁 Test completed")
