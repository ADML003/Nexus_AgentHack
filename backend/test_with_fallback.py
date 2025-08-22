import os
from dotenv import load_dotenv
from portia import (
    Config,
    LLMProvider,
    Portia,
    example_tool_registry,
)

load_dotenv('../.env.local')  # Load from parent directory
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')

def test_with_mistral():
    """Test with Mistral AI - small model to avoid capacity limits"""
    try:
        print("🤖 Testing with Mistral AI (mistral-small-latest)...")
        
        mistral_config = Config.from_default(
            llm_provider=LLMProvider.MISTRALAI,
            default_model="mistralai/mistral-small-latest",  # Using smaller model
            mistralai_api_key=MISTRAL_API_KEY
        )
        
        portia = Portia(config=mistral_config, tools=example_tool_registry)
        plan_run = portia.run('add 1 + 2')
        
        print("✅ Mistral AI Success!")
        print(plan_run.model_dump_json(indent=2))
        return True
        
    except Exception as e:
        print(f"❌ Mistral AI failed: {str(e)}")
        if "429" in str(e) or "capacity exceeded" in str(e).lower():
            print("   Reason: Rate limit/capacity exceeded")
        return False

def test_with_openai_fallback():
    """Fallback to OpenAI if available"""
    try:
        print("\n🔄 Falling back to OpenAI...")
        
        openai_config = Config.from_default(
            llm_provider=LLMProvider.OPENAI,
            default_model="openai/gpt-4o-mini"  # Using smaller, cheaper model
        )
        
        portia = Portia(config=openai_config, tools=example_tool_registry)
        plan_run = portia.run('add 1 + 2')
        
        print("✅ OpenAI Fallback Success!")
        print(plan_run.model_dump_json(indent=2))
        return True
        
    except Exception as e:
        print(f"❌ OpenAI fallback also failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Portia Integration with Fallback Strategy")
    print("=" * 60)
    
    # Try Mistral first
    if not test_with_mistral():
        # If Mistral fails, try OpenAI
        if not test_with_openai_fallback():
            print("\n💡 Suggestions:")
            print("1. Wait a few minutes and try again (rate limit may reset)")
            print("2. Upgrade your Mistral AI plan for higher capacity")
            print("3. Set up OpenAI API key as backup: OPENAI_API_KEY in .env.local")
            print("4. Use a different model like 'mistralai/mistral-tiny' if available")
        
    print("\n🏁 Test completed")
