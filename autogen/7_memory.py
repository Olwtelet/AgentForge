import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from autogen_ext.models.openai import OpenAIChatCompletionClient

from settings import settings

"""
------------------------------------------------------------------------
In this example, we explore Autogen agents with the following features:
- Memory stores
- User preferences
- Persistent context

This example shows a primitive example of a Memory store that maintains
user preferences across interactions. You can build on the Memory protocol
to implement more complex memory stores using vector databases, ML models,
or other advanced storage mechanisms.

For more advanced and custom memory stores, check:
https://microsoft.github.io/autogen/stable//user-guide/agentchat-user-guide/memory.html#custom-memory-stores-vector-dbs-etc
------------------------------------------------------------------------
"""

# --- 1. Define a tool function ---
async def get_weather(city: str, units: str = "imperial") -> str:
    """Get weather information for a city."""
    if units == "imperial":
        return f"The weather in {city} is 73 °F and Sunny."
    elif units == "metric":
        return f"The weather in {city} is 23 °C and Sunny."
    else:
        return f"Sorry, I don't know the weather in {city}."

async def main() -> None:
    # --- 2. Define the model client ---
    model_client = OpenAIChatCompletionClient(
        model=settings.OPENAI_MODEL_NAME,
        api_key=settings.OPENAI_API_KEY.get_secret_value()
    )

    # --- 3. Initialize user memory and add preferences ---
    user_memory = ListMemory()
    
    # Add user preferences to memory
    await user_memory.add(
        MemoryContent(
            content="The weather should be in metric units", 
            mime_type=MemoryMimeType.TEXT
        )
    )

    await user_memory.add(
        MemoryContent(
            content="Meal recipes must be vegan", 
            mime_type=MemoryMimeType.TEXT
        )
    )

    # --- 4. Define the agent with memory ---
    assistant_agent = AssistantAgent(
        name="assistant_agent",
        model_client=model_client,
        tools=[get_weather],
        memory=[user_memory], # Add memory to the agent here
        system_message="You are a helpful assistant that remembers user preferences."
    )

    # --- 5. Run the agent ---
    await Console(
        assistant_agent.run_stream(
            task=("What's the weather like in New York?")
        )
    )
    
    await Console(
        assistant_agent.run_stream(
            task=("Write brief meal recipe with broth?")
        )
    )
    # Get the assistant's messages and model context
    print(
        "-" * 50,
        f"\nAssistant's Internal messages:\n\t"
        f"{await assistant_agent._model_context.get_messages()}"
    )

if __name__ == "__main__":
    asyncio.run(main())
