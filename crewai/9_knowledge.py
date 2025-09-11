import os

from crewai import Agent, Task, Crew
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai.knowledge.source.crew_docling_source import CrewDoclingSource
from crewai.knowledge.knowledge_config import KnowledgeConfig

from settings import settings
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore CrewAI's agents with the following features:
- Knowledge sources for external information
- Knowledge configuration options
- Agent-specific and crew-wide knowledge
- Different embedding providers per agent's knowledge sources

Knowledge sources allow agents to access and utilize
external information to enhance their decision-making
and provide more accurate, contextual responses.

For more details, visit:
https://docs.crewai.com/en/concepts/knowledge
-------------------------------------------------------
"""

# --- 1. Create a Agent Basic Knowledge Examples ---
# 1.1 Basic String Knowledge
user_info = StringKnowledgeSource(
    content="Users name is John. He is 30 years old and lives in San Francisco."
)

# 1.2 Simple CrewDoclingSource Example
llm_info_source = CrewDoclingSource(
    file_paths=[
        "https://lilianweng.github.io/posts/2024-11-28-reward-hacking",
        "https://lilianweng.github.io/posts/2024-07-07-hallucination",
    ],
)

# Text sources: Raw strings, text files (.txt), PDF documents
# Structured data: CSV files, Excel spreadsheets, JSON documents

# --- 2. Define a Knowledge configuration (optional) ---
knowledge_config = KnowledgeConfig(results_limit=10, score_threshold=0.5)

# --- 3. Create agents with agent-specific knowledge ---
user_specialist = Agent(
    role="User Specialist",
    goal="Provide user-specific expertise",
    backstory="User expert",
    llm=settings.OPENAI_MODEL_NAME,
    verbose=True,
    knowledge_sources=[user_info],  # Agent1-specific knowledge
    knowledge_config=knowledge_config,
    # embedder=... # Agent can have its own embedder, see below
)

llm_info_specialist = Agent(
    role="Search Specialist",
    goal="Provide search expertise",
    backstory="Search expert",
    llm=settings.OPENAI_MODEL_NAME,
    verbose=True,
    knowledge_sources=[llm_info_source],  # Agent2-specific knowledge
    embedder={  # Agent can have its own embedder
        "provider": "openai",
        "config": {"model": "text-embedding-3-small"}
    }
)

generalist = Agent(
    role="General Assistant", 
    goal="Provide general assistance",
    backstory="General helper",
    llm=settings.OPENAI_MODEL_NAME,
    verbose=True,
    # No agent-specific knowledge
)

# --- 4. Create tasks for each agent ---
task_user = Task(
    description=(
        "Respond to the question about the user: "
        "What city does John live in and how old is he?"
    ),
    expected_output="The answer to the question",
    agent=user_specialist,
)

task_llm = Task(
    description=(
        "Answer the question about LLMs: "
        "What is the reward hacking paper about? Be sure to provide sources."
    ),
    expected_output="A summary of the relevant information with sources.",
    agent=llm_info_specialist,
)

task_general = Task(
    description=(
        "Answer the general question: "
        "What is the capital of Lisbon?"
    ),
    expected_output="A helpful answer to the question.",
    agent=generalist,
)


# --- 5. Add Crew-wide knowledge (shared by all agents) ---
crew_knowledge = StringKnowledgeSource(
    content="Every agent should start its answers with 'Hello there! 😄'"
)

# --- 6. Create the crew with agents, tasks, and crew-wide knowledge ---
crew = Crew(
    agents=[user_specialist, llm_info_specialist, generalist],
    tasks=[task_user, task_llm, task_general],
    knowledge_sources=[crew_knowledge]  # Crew-wide knowledge
)
# -> user_specialist/llm_info_specialist get: crew_knowledge + specific knowledge
# -> generalist gets: crew_knowledge only
# Each agent gets only their specific knowledge
# Each can use different embedding providers

# --- 7. Run the crew with the various tasks ---
result = crew.kickoff()
