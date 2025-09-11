import os

from crewai import Agent, Task, Crew

from settings import settings
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore a simple Hello World agent
-------------------------------------------------------
"""

# --- 1. Create an agent ---
agent = Agent(
    role="Greeter",
    goal="Say hello to the world",
    backstory="A friendly AI assistant",
    llm=settings.OPENAI_MODEL_NAME,
    verbose=True
)

# --- 2. Create a task ---
task = Task(
    description="Say hello to the world",
    expected_output="A greeting message",
    agent=agent
)

# --- 3. Create crew ---
crew = Crew(
    agents=[agent],
    tasks=[task]
)

# --- 4. Run the crew ---
result = crew.kickoff()
# no need to print, as verbose=True will show the output in the terminal

# --- 4. Alternatively, you can run the agent on the task ---
# (If you want to see the result, uncomment the line below)
# result = agent.execute_task(task)