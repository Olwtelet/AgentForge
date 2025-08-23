import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from settings import settings

"""
-------------------------------------------------------
In this example, we explore a simple Hello World agent
-------------------------------------------------------
"""

# --- 1. Define the model client ---
model_client = OpenAIChatCompletionClient(
    model=settings.OPENAI_MODEL_NAME,
    api_key=settings.OPENAI_API_KEY.get_secret_value()
)

# --- 2. Define the agent ---
agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
)

# --- 3. Run the agent with a user message ---
print(
    asyncio.run(
        agent.run(task="Say 'Hello World!'")
    )
)
