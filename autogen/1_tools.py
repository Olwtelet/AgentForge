import asyncio

from autogen_core.tools import FunctionTool
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from settings import settings

"""
------------------------------------------------------------------------
In this example, we explore Autogen agents with the following features:
- Tool usage
- Tool Schemas

This example shows how to define and use tools using Autogen.
------------------------------------------------------------------------
"""

# --- 1. Define a tool that searches the web for information. ---
# For simplicity, we will use a mock function here that returns a static string.
async def web_search_func(query: str) -> str:
    """Find information on the web"""
    return "AutoGen is a programming framework for building multi-agent applications."

# NOTE: This step is automatically performed inside the AssistantAgent if the tool is a Python function.
web_search_function_tool = FunctionTool(
    web_search_func, description="Find information on the web"
)


# --- 2. Define the model client ---
model_client = OpenAIChatCompletionClient(
    model=settings.OPENAI_MODEL_NAME,
    api_key=settings.OPENAI_API_KEY.get_secret_value()
)

# --- 3. Define the agent ---
agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    tools=[web_search_func],
    system_message="Use tools to solve tasks.",
    max_tool_iterations=1,
)

async def main()  -> None:
    # --- 4. Run the agent and print the result ---
    result = await agent.run(task="Find information on AutoGen")
    print(result)
    print("-" * 50)
    
    # Get the last message
    print("Final Answer: ", result.messages[-1].content)
    print("-" * 50)
    
    # Get tool schema
    # The schema is provided to the model during AssistantAgent's on_messages call.
    web_search_function_tool.schema
    print("Tool Schema: ", web_search_function_tool.schema)

if __name__ == "__main__":
    asyncio.run(main())
