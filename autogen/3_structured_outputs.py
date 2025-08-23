import asyncio
from typing import Literal
from pydantic import BaseModel

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import StructuredMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console

from settings import settings

"""
------------------------------------------------------------------------
In this example, we explore Autogen agents with the following features:
- Structured outputs
- Agent thoughts and responses

This example shows how to define structured outputs for the models.
Structured output allows models to return structured JSON text with 
pre-defined schema provided by the application. Different from JSON-mode, 
the schema can be provided as a Pydantic BaseModel class, which can also 
be used to validate the output.
------------------------------------------------------------------------
"""

# --- 1. Define the Agent response model ---
class AgentResponse(BaseModel):
    thoughts: str
    response: Literal["happy", "sad", "neutral"]


# --- 2. Define the model client ---
model_client = OpenAIChatCompletionClient(
    model=settings.OPENAI_MODEL_NAME,
    api_key=settings.OPENAI_API_KEY.get_secret_value()
)

# --- 3. Define the agent ---
agent = AssistantAgent(
    "assistant",
    model_client=model_client,
    system_message="Categorize the input as happy, sad, or neutral following the JSON format.",
    # Define the output content type of the agent.
    output_content_type=AgentResponse,
)

async def main() -> None:
    # --- 4. Run the agent and print the result ---
    result = await Console(agent.run_stream(task="I am happy."))

    # Check the last message in the result, validate its type, and print the thoughts and response.
    assert isinstance(result.messages[-1], StructuredMessage)
    assert isinstance(result.messages[-1].content, AgentResponse)
    print("Thought: ", result.messages[-1].content.thoughts)
    print("Response: ", result.messages[-1].content.response)
    await model_client.close()

if __name__ == "__main__":
    asyncio.run(main())