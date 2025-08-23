import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import (
    RoundRobinGroupChat, 
    SelectorGroupChat, 
    MagenticOneGroupChat,
    Swarm,
)
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

from utils import print_new_section
from settings import settings

"""
------------------------------------------------------------------------
In this example, we explore Autogen agents with the following features:
- Multi-agent
- Teams
- Collaboration
- Orchestration

This example shows the 4 different team presets of AgentChat API:
1. RoundRobinGroupChat - A team that runs a group chat with participants 
   taking turns in a round-robin fashion.
2. SelectorGroupChat - A team that selects the next speaker using a 
   ChatCompletion model after each message.
3. MagenticOneGroupChat - A generalist multi-agent system for solving 
   open-ended web and file-based tasks across a variety of domains.
4. Swarm - A team that uses HandoffMessage to signal transitions between agents.
------------------------------------------------------------------------
"""

# Setup:
# --- 1. Define the model client ---
model_client = OpenAIChatCompletionClient(
    model=settings.OPENAI_MODEL_NAME,
    api_key=settings.OPENAI_API_KEY.get_secret_value()
)

# ------------------------------------------------------------
#                    1. RoundRobinGroupChat
# ------------------------------------------------------------
# A team that runs a group chat with participants taking turns 
# in a round-robin fashion to publish a message to all.

# --- 1. Define the team agents ---
# 1.1 Create the primary agent
primary_agent = AssistantAgent(
    "primary",
    model_client=model_client,
    system_message="You are a helpful AI assistant.",
)

# 1.2 Create the critic agent.
critic_agent = AssistantAgent(
    "critic",
    model_client=model_client,
    system_message=(
        "Provide constructive feedback. Respond with 'APPROVE' "
        "to when your feedbacks are addressed."
    ),
)

# --- 2. Define a termination condition that stops the task if the critic approves.
text_termination = TextMentionTermination("APPROVE")

# --- 3. Create a team the agents.
team = RoundRobinGroupChat(
    participants=[primary_agent, critic_agent], 
    termination_condition=text_termination
)

# --- 4. Run the team
print_new_section("1. RoundRobinGroupChat")
asyncio.run(
    Console(
        team.run_stream(task="Write a short poem about the fall season.")
    )
)

# ------------------------------------------------------------
#                    2. SelectorGroupChat
# ------------------------------------------------------------
# A group chat team that have participants takes turn to publish a message to all, 
# using a ChatCompletion model to select the next speaker after each message.

# --- 1. Define the tools to be used by the agents ---
async def lookup_hotel(location: str) -> str:
    return f"Here are some hotels in {location}: hotel1, hotel2, hotel3."

async def lookup_flight(origin: str, destination: str) -> str:
    return f"Here are some flights from {origin} to {destination}: flight1, flight2, flight3."

async def book_trip(hotel: str, flight: str) -> str:
    return "Your trip is booked!"

# --- 2. Define the agents ---
# 2.1. Travel Advisor Agent
travel_advisor = AssistantAgent(
    "travel_advisor",
    model_client,
    tools=[book_trip],
    description="Helps with travel planning.",
)
# 2.2. Hotel Agent
hotel_agent = AssistantAgent(
    "hotel_agent",
    model_client,
    tools=[lookup_hotel],
    description="Helps with hotel booking.",
)
# 2.3. Flight Agent
flight_agent = AssistantAgent(
    "flight_agent",
    model_client,
    tools=[lookup_flight],
    description="Helps with flight booking.",
)

# --- 3. Create the termination condition ---
termination = TextMentionTermination("TERMINATE")

# --- 4. Create the team ---
team = SelectorGroupChat(
    [travel_advisor, hotel_agent, flight_agent],
    model_client=model_client,
    termination_condition=termination,
    allow_repeated_speaker=False,
    max_selector_attempts=3,
    # ...
)

# --- 5. Run the conversation and stream to the console ---
print_new_section("2. SelectorGroupChat")
asyncio.run(
    Console(
        team.run_stream(task="Book a 3-day trip from Lisbon to NY with flight and hotel.")
    )
)


# ------------------------------------------------------------
#                   3. MagenticOneGroupChat
# ------------------------------------------------------------
# A team that runs a group chat with participants managed by the MagenticOneOrchestrator.

# --- 1. Define the agent ---
assistant = AssistantAgent(
    "assistant",
    model_client=model_client,
)

# --- 2. Create the team ---
# The MagenticOneOrchestrator is automatically set when the team is created.
team = MagenticOneGroupChat(
    [assistant], 
    model_client=model_client,
    max_turns=2,
    max_stalls=1,
    # ...
)

# --- 3. Run the team ---
print_new_section("3. MagenticOneGroupChat")
asyncio.run(
    Console(
        team.run_stream(task="Write a short story about a brave knight.")
    )
)


# -------------------------------------------------
#                    4. Swarm
# -------------------------------------------------
# A group chat team that selects the next speaker based on handoff message only.
# The first participant in the list of participants is the initial speaker. 
# The next speaker is selected based on the HandoffMessage message sent by the current speaker. 
# If no handoff message is sent, the current speaker continues to be the speaker.

# --- 1. Define the agents ---
agent1 = AssistantAgent(
    "Alice",
    model_client=model_client,
    handoffs=["Bob"],
    system_message=(
        "You are Alice and you only answer questions about yourself. "
        "If the question is about Bob, please hand off to Bob."
    )
)
agent2 = AssistantAgent(
    "Bob", 
    model_client=model_client, 
    system_message="You are Bob and your birthday is on 1st January.",
)

# --- 2. Create the termination condition ---
termination = MaxMessageTermination(3)

# --- 3. Create the team ---
team = Swarm([agent1, agent2], termination_condition=termination)

# --- 4. Run the team ---
print_new_section("4. Swarm")
asyncio.run(
    Console(team.run_stream(task="What is bob's birthday?"))
)
