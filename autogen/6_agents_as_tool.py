import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.tools import AgentTool, TeamTool
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import SourceMatchTermination
from autogen_agentchat.ui import Console

from utils import print_new_section
from settings import settings

"""
-------------------------------------------------------
In this example, we explore Autogen agents with the following features:
- Agents as Tools
- Teams as Tools
- Tool integration

This example shows how to use both individual agents and teams of agents 
as tools that can be invoked by other agents.
-------------------------------------------------------
"""

async def main() -> None:
    model_client = OpenAIChatCompletionClient(
        model=settings.OPENAI_MODEL_NAME,
        api_key=settings.OPENAI_API_KEY.get_secret_value()
    )
    
    writer = AssistantAgent(
        name="writer",
        description="A writer agent for generating text.",
        model_client=model_client,
        system_message="Write well.",
    )
    summarizer = AssistantAgent(
        name="summarizer",
        model_client=model_client,
        system_message="You summarize the text.",
    )

    # Create model client with parallel tool calls disabled for the main agent
    main_model_client = OpenAIChatCompletionClient(
        model=settings.OPENAI_MODEL_NAME,
        api_key=settings.OPENAI_API_KEY.get_secret_value(),
        parallel_tool_calls=False  # Disable parallel tool calls for the main agent
    )
    # > IMPORTANT!
    # When using AgentTool or TeamTool, you must disable parallel tool calls to avoid 
    # concurrency issues. These tools cannot run concurrently as agents and teams 
    # maintain internal state that would conflict with parallel execution.

    # --------------------------------------
    #             Agent as Tool
    # --------------------------------------
    
    # Agent as Tool
    agent_tool = AgentTool(agent=writer)
    
    assistant = AssistantAgent(
        name="assistant",
        model_client=main_model_client,
        tools=[agent_tool], # Use the agent_tool
        system_message="You are a helpful assistant.",
    )
    
    # --- 4. Run the team
    print_new_section("1. Agent as Tool")
    await Console(assistant.run_stream(task="Write a poem about the sea."))
    

    # --------------------------------------
    #        Team of Agents as Tool
    # --------------------------------------
    
    # Team of Agents as Tool
    # Create a TeamTool that uses the team to run tasks, returning the last message as the result.
    team = RoundRobinGroupChat(
        [writer, summarizer], 
        termination_condition=SourceMatchTermination(sources=["summarizer"])
    )
    
    team_tool = TeamTool(
        team=team,
        name="writing_team",
        description="A tool for writing tasks.",
        return_value_as_last_message=True,
    )
    
    assistant = AssistantAgent(
        name="assistant",
        model_client=main_model_client,
        tools=[team_tool],  # Use the team_tool
        system_message="You are a helpful assistant.",
    )

    # --- 4. Run the team
    print_new_section("2. Team of Agents as Tool")
    await Console(assistant.run_stream(task="Write a poem about the sea."))

if __name__ == "__main__":
    asyncio.run(main())
