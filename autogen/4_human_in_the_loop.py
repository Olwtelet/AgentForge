import asyncio

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console

from settings import settings

"""
------------------------------------------------------------------------
In this example, we explore Autogen agents with the following features:
- Human-in-the-loop

This example shows how to integrate human feedback and approval 
into agent workflows.
------------------------------------------------------------------------
"""

# --- 1. Define the model client ---
model_client = OpenAIChatCompletionClient(
    model=settings.OPENAI_MODEL_NAME,
    api_key=settings.OPENAI_API_KEY.get_secret_value()
)

# --- 2. Create the Assistant Agent instance ---
assistant = AssistantAgent(
    name="assistant", 
    model_client=model_client
)

# --- 3. Create the UserProxy Agent ---
user_proxy = UserProxyAgent(
    name="user_proxy",
    input_func=input  # Use input() to get user input from console.
)

# --- 4. Create the termination condition ---
termination = TextMentionTermination("APPROVE")

# --- 5. Create the team ---
team = RoundRobinGroupChat([assistant, user_proxy], termination_condition=termination)

# --- 6. Run the conversation and stream to the console ---
asyncio.run(
    Console(
        team.run_stream(task="Write a 4-line poem about the ocean.")
    )
)
# > If you write APPROVE, it breaks
# > Else, it continues
