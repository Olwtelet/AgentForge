import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console

from settings import settings

"""
------------------------------------------------------------------------
In this example, we explore Autogen agents with the following features:
- Custom tool definition
- Streaming responses
- Stats/Usage Metrics

This example shows the different ways to stream responses and collect 
metrics using Autogen.
------------------------------------------------------------------------
"""

# ---  1. Define a tool that calculates the sum of a list of integers. ---
def sum(values: list[int]) -> int:
    """Calculate the sum of a list of integers."""
    return sum(values)


# --- 2. Define the model client ---
model_client = OpenAIChatCompletionClient(
    model=settings.OPENAI_MODEL_NAME,
    api_key=settings.OPENAI_API_KEY.get_secret_value()
)

# --- 3. Define the agent ---
agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    tools=[sum],
    system_message="Use tools to solve tasks.",
)

# --- 4. Define the streaming function ---
async def assistant_run_stream() -> None:
    # Option 1: read each message from the stream (as shown in the previous example).
    # async for message in agent.run_stream(task="What the result of 2 + 4?"):
    #     print(message)

    # Option 2: use Console to print all messages as they appear.
    await Console(
        agent.run_stream(task="What the result of 2 + 4?"),
        output_stats=True,  # Enable stats/metrics printing
    )

if __name__ == "__main__":
    asyncio.run(assistant_run_stream())
