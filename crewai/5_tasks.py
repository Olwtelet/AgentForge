import os
from httpx import codes
from pydantic import BaseModel

from crewai import Agent, Task, Crew
from crewai_tools import CodeInterpreterTool

from settings import settings
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore CrewAI's agents with the following features:
- Using Pydantic models for structured responses
- LLM with structured output
- Agent with structured output

This demonstrates how to ensure LLMs and agents return data in specific,
structured formats that can be easily processed by other systems.

For more details, visit:
https://docs.crewai.com/en/concepts/llms#structured-llm-calls
-------------------------------------------------------
"""

# --- 1. Define a Pydantic model for structured output ---
class CodeSnippet(BaseModel):
    code: str

# --- 2. Define the agent ---
agent = Agent(
    role="Multi Purpose Specialist",
    goal="You are an expert in multiple domains.",
    backstory=(
        "You are a master at understanding various topics and can provide "
        "detailed information and code snippets as needed."
    ),
    llm=settings.OPENAI_MODEL_NAME,
    verbose=True,
)

# --- 3. Define the tasks ---
generate_code_snippet_task = Task(
    description="Generated simple code for this: {topic}",
    expected_output="A simple code snippet for {topic}",
    async_execution=True,  # This task will run asynchronously
    output_pydantic=CodeSnippet,  # Expecting structured output using Pydantic model
    agent=agent,
)

simplify_code_snippet_task = Task(
    description="Interpret and simplify code snippet using the tools",
    expected_output="A natural language description of the code snippet",
    agent=agent,
    context=[generate_code_snippet_task],  # Other tasks whose outputs will be used as context for this task
    markdown=True,  # Enable automatic markdown formatting
    tools=[CodeInterpreterTool()] # Limit the agent to only use this tool for this task
    # (this tool will be added to the agent's tools automatically)
)

# --- 5. Create the crew with the event listener ---
crew = Crew(
    agents=[agent],
    tasks=[generate_code_snippet_task, simplify_code_snippet_task],
)

# -- 6. Run the crew (will print streaming events in real-time) ---
result = crew.kickoff(
    inputs={"topic": "fibonacci sequence in python"},
)

# Show the results of the tasks
print("Task 1 Result (raw):\n", result.tasks_output[0].raw[:200], "...\n" + "-" * 50)
print("Task 1 Result (pydantic):", type(result.tasks_output[0].pydantic), "\n"+ "-" * 50)
print("Task 2 Result (raw):\n", result.tasks_output[1].raw[:200])
