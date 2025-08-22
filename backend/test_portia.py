from dotenv import load_dotenv
from portia import (
    Portia,
    Config,
    example_tool_registry,
)

# Load environment variables from the parent directory's .env.local
load_dotenv('../.env.local')

# Set up Mistral configuration using Config.from_default
config = Config.from_default(
    llm_provider="mistralai",
    default_model="mistralai/mistral-small-latest"
)

# Instantiate Portia with Mistral config and example tools
portia = Portia(config=config, tools=example_tool_registry)

# Run the test query and print the output!
plan_run = portia.run('add 1 + 2')
print(plan_run.model_dump_json(indent=2))
