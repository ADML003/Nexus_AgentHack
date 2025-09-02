#!/usr/bin/env python3

import requests
import json

def test_clarification_flow():
    """Test the clarification system with a Gmail query that should require OAuth"""
    
    base_url = "http://localhost:8000"
    
    # Test query that should trigger Gmail OAuth clarification
    query_data = {
        "message": "Send an email to test@example.com with subject 'Test Email' and body 'Hello from Portia!'",
        "tool_registry": "cloud",
        "user_id": "test-user",
        "session_id": "test-session"
    }
    
    print("🔵 Testing clarification flow with Gmail query...")
    print(f"Query: {query_data['message']}")
    
    # Send initial query
    response = requests.post(f"{base_url}/query", json=query_data)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Query response received")
        print(f"Success: {data.get('success')}")
        print(f"Requires user action: {data.get('requires_user_action')}")
        
        if data.get('clarification'):
            clarification = data['clarification']
            print(f"\n🔶 Clarification needed:")
            print(f"Type: {clarification.get('type')}")
            print(f"Message: {clarification.get('message')}")
            print(f"Action required: {clarification.get('action_required')}")
            
            if clarification.get('details'):
                print(f"Details: {json.dumps(clarification['details'], indent=2)}")
                
            # Simulate user providing authorization
            clarification_response = {
                "clarification_id": "test-clarification-id",
                "user_response": "authorized",
                "user_id": "test-user",
                "session_id": "test-session"
            }
            
            print(f"\n🔵 Sending clarification response...")
            clarify_response = requests.post(f"{base_url}/clarification", json=clarification_response)
            
            if clarify_response.status_code == 200:
                clarify_data = clarify_response.json()
                print(f"✅ Clarification response received")
                print(f"Success: {clarify_data.get('success')}")
                print(f"Result: {clarify_data.get('result', 'No result')}")
                
                if clarify_data.get('requires_user_action'):
                    print("🔶 Additional clarification needed")
                else:
                    print("✅ Task completed successfully")
            else:
                print(f"❌ Clarification request failed: {clarify_response.status_code}")
                print(clarify_response.text)
        else:
            print("ℹ️ No clarification was needed")
            print(f"Result: {data.get('result', 'No result')}")
    else:
        print(f"❌ Query failed: {response.status_code}")
        print(response.text)

def test_basic_query():
    """Test a basic query that shouldn't require clarification"""
    
    base_url = "http://localhost:8000"
    
    query_data = {
        "message": "What's 2 + 2?",
        "tool_registry": "open_source",
        "user_id": "test-user",
        "session_id": "test-session"
    }
    
    print("\n🔵 Testing basic query (no clarification expected)...")
    print(f"Query: {query_data['message']}")
    
    response = requests.post(f"{base_url}/query", json=query_data)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Query response received")
        print(f"Success: {data.get('success')}")
        print(f"Requires user action: {data.get('requires_user_action')}")
        print(f"Result: {data.get('result', 'No result')}")
        
        if data.get('tools_used'):
            print(f"Tools used: {data['tools_used']}")
    else:
        print(f"❌ Query failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    print("🚀 Testing Portia Clarification System")
    print("=" * 50)
    
    try:
        test_basic_query()
        test_clarification_flow()
        
        print("\n" + "=" * 50)
        print("✅ Tests completed! Check the frontend at http://localhost:3001/agent")
        print("Try asking: 'Send an email to test@example.com' to see clarifications in action")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed: {e}")
