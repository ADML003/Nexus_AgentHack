#!/usr/bin/env python3
"""
Quick API Fix Verification
Tests the corrected PlanRun attribute access
"""

from dotenv import load_dotenv
from portia import Config, LLMProvider, Portia, example_tool_registry
import os

load_dotenv('../.env.local')

def test_fixed_api():
    """Test the corrected API structure"""
    try:
        print("🧪 Testing Fixed Portia API Structure")
        print("=" * 40)
        
        config = Config.from_default(
            llm_provider=LLMProvider.MISTRALAI,
            default_model='mistralai/mistral-small-latest',
            mistralai_api_key=os.getenv('MISTRAL_API_KEY'),
            storage_class='MEMORY'
        )
        
        portia = Portia(config=config, tools=example_tool_registry)
        
        print("🤖 Running test query: 'What is 8 + 7?'")
        plan_run = portia.run('What is 8 + 7?')
        
        print("✅ Query completed successfully!")
        print(f"📋 Plan Run ID: {plan_run.id}")
        print(f"📊 State: {plan_run.state}")
        
        # Test the corrected attribute access
        final_output = plan_run.outputs.final_output
        print(f"🎯 Final Answer: {final_output.value}")
        print(f"📝 Summary: {final_output.summary}")
        
        # Test step outputs
        print("🔧 Step Outputs:")
        for key, value in plan_run.outputs.step_outputs.items():
            print(f"   {key}: {value.value} ({value.summary})")
        
        # Create the response structure like in the API
        api_response = {
            "success": True,
            "plan_run_id": plan_run.id,
            "result": {
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
            },
            "model_used": "mistral"
        }
        
        print("\n🎉 SUCCESS! API structure works correctly!")
        print(f"🔍 Final answer extracted: {api_response['result']['final_output']['value']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fixed_api()
    
    if success:
        print("\n✅ CONCLUSION: The API issue was NOT rate limits!")
        print("   It was incorrect attribute access in the code.")
        print("   The fixed code should now work properly.")
        print("\n📋 To start the working server:")
        print("   cd /Users/ADML/Desktop/Nexus/backend")
        print("   /Users/ADML/Desktop/Nexus/.venv/bin/python main_robust.py")
    else:
        print("\n❌ CONCLUSION: There are still issues to resolve.")
