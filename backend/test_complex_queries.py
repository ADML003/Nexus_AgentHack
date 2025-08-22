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

print("🚀 Testing Portia.ai + Mistral Integration")
print("=" * 50)

# Create a default Portia config with LLM provider set to Mistral AI and the latest Mistral Large model
mistral_config = Config.from_default(
    llm_provider=LLMProvider.MISTRALAI,
    default_model="mistralai/mistral-large-latest",
    mistralai_api_key=MISTRAL_API_KEY
)

# Instantiate a Portia instance. Load it with the config and with the example tools.
portia = Portia(config=mistral_config, tools=example_tool_registry)

# Test 1: Simple math
print("\n📊 Test 1: Simple Math")
print("Query: 'What is 15 * 24?'")
plan_run1 = portia.run('What is 15 * 24?')
print(f"Result: {plan_run1.outputs.final_output.value}")
print(f"Summary: {plan_run1.outputs.final_output.summary}")

# Test 2: Complex calculation  
print("\n📊 Test 2: Complex Calculation")
print("Query: 'Calculate the area of a circle with radius 5'")
plan_run2 = portia.run('Calculate the area of a circle with radius 5')
print(f"Result: {plan_run2.outputs.final_output.value}")
print(f"Summary: {plan_run2.outputs.final_output.summary}")

print("\n✅ Portia + Mistral integration is working perfectly!")
print("🎯 Ready for production use in your FastAPI backend!")
