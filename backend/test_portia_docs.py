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

# Create a default Portia config with LLM provider set to Mistral AI and the latest Mistral Large model
mistral_config = Config.from_default(
    llm_provider=LLMProvider.MISTRALAI,
    default_model="mistralai/mistral-large-latest",
    mistralai_api_key=MISTRAL_API_KEY
)
# Instantiate a Portia instance. Load it with the config and with the example tools.
portia = Portia(config=mistral_config, tools=example_tool_registry)
# Run the test query and print the output!
plan_run = portia.run('add 1 + 2')
print(plan_run.model_dump_json(indent=2))
