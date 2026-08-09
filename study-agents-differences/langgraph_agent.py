import json
import time
from datetime import date

# LangGraph and LangChain imports
from typing import Annotated, TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool
from langchain_huggingface import ChatHuggingFace
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from tavily import TavilyClient

from agent_contract import AgentResult, TokenUsage

# Prompt components
from prompts import goal, instructions, knowledge, role

# Load environment variables
from settings import settings
from utils import execute_agent, get_tools_descriptions, parse_args

# Initialize Tavily client
tavily_client = TavilyClient(api_key=settings.tavily_api_key.get_secret_value())


# LangGraph specific - Define the state for the graph
class State(TypedDict):
    messages: Annotated[list, add_messages]


class Agent:
    def __init__(
        self, 
        provider: str = "openai", 
        memory: bool = True,
        verbose: bool = False, 
        tokens: bool = False
    ):
        """
        Initialize the LangGraph agent using create_react_agent.
        """
        self.name = "LangGraph Agent"

        # Create tools
        self.tools = self._create_tools()

        # Create memory
        if memory:
            self.memory = MemorySaver()
        else:
            self.memory = None
        # Memory will be checkpointed per thread. We will start with thread id 1.
        self.thread_id = 1

        self.tokens = tokens

        # Create the prompt
        self.prompt = self._create_prompt()

        # Initialize the language model
        self.model = (
            AzureChatOpenAI(
                base_url=f"{settings.azure_endpoint}/deployments/{settings.azure_deployment_name}",
                api_version=settings.azure_api_version,
                api_key=settings.azure_api_key.get_secret_value(),
                temperature=settings.temperature,
            )
            if provider == "azure" and settings.azure_api_key
            else ChatOpenAI(
                api_key=settings.openai_api_key.get_secret_value(),
                model=settings.openai_model_name,
                temperature=settings.temperature,
            )
            if provider == "openai" and settings.openai_api_key
            else ChatHuggingFace(
                model=settings.open_source_model_name
            )
        )

        # Create the agent graph
        self.graph = create_react_agent(
            model=self.model,
            tools=self.tools,
            prompt=self.prompt,
            checkpointer=self.memory,
            debug=True if verbose else False
        )

        # Extras:
        self.tools_descriptions = get_tools_descriptions(
            [(tool.name, tool.description) for tool in self.tools]
        )


    @staticmethod
    def date_tool(tool_input: dict | None = None):
        """
        Function to get the current date.

        ``tool_input`` is accepted (and ignored) because LangChain's ``Tool``
        always passes an argument, even for zero-argument tools.
        """
        today = date.today()
        return today.strftime("%B %d, %Y")

    @staticmethod
    def web_search_tool(query: str):
        """
        This function searches the web for the given query and returns the results.
        """
        # Call Tavily's search and dump the results as a JSON string
        search_response = tavily_client.search(query)
        results = json.dumps(search_response.get('results', []))
        # print("Web Search Tool was called!")
        # print(f"Web Search Results for '{query}':")
        # print(results)
        return results

    def _create_tools(self):
        """
        Create tools for the agent.

        Returns:
            List of tools
        """
        return [
            Tool(
                name="date_tool",
                func=self.date_tool,
                description="Useful for getting the current date"
            ),
            Tool(
                name="web_search_tool",
                func=self.web_search_tool,
                description="Useful for searching the web for information"
            )
        ]

    def _create_prompt(self):
        """
        Create a comprehensive prompt for the agent.

        Returns:
            ChatPromptTemplate
        """
        return ChatPromptTemplate.from_messages([
            ("system", "\n".join([role, goal, instructions, knowledge])),
            ("placeholder", "{messages}"),
        ])

    def _inc_thread_id(self):
        """
        Simply increments the thread id and returns the new id.

        """
        new_thread_id = self.thread_id + 1
        self.thread_id = new_thread_id
        return new_thread_id

    def chat(self, message: str) -> AgentResult:
        """
        Send a message and get a response.

        Args:
            message (str): User's input message

        Returns:
            AgentResult: The assistant's response, latency and token usage.
        """
        start = time.perf_counter()
        try:
            # Prepare input
            inputs = {"messages": [("user", message)]}
            config = {"configurable": {"thread_id": str(self.thread_id)}}

            # Stream the graph updates and collect the final response
            full_response = ""
            event = None
            for event in self.graph.stream(inputs, config=config, stream_mode="values"):
                if event and "messages" in event:
                    last_message = event["messages"][-1]
                    if hasattr(last_message, "content"):
                        full_response = last_message.content
            exec_time = time.perf_counter() - start

            usage = None
            tool_calls = None
            if event:
                tool_calls = sum(
                    len(getattr(msg, "tool_calls", None) or [])
                    for msg in event["messages"]
                )
            if self.tokens and event:
                prompt_tokens = completion_tokens = total_tokens = 0
                for msg in event["messages"]:  # last event contains all messages
                    if msg.response_metadata:
                        token_usage = msg.response_metadata["token_usage"]
                        prompt_tokens += token_usage["prompt_tokens"]
                        completion_tokens += token_usage["completion_tokens"]
                        total_tokens += token_usage["total_tokens"]
                usage = TokenUsage(
                    input_tokens=prompt_tokens,
                    output_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    embedding_tokens=0,
                )

            return AgentResult(
                content=full_response,
                elapsed_seconds=exec_time,
                usage=usage,
                tool_calls=tool_calls,
            )

        except Exception as e:
            return AgentResult.from_error(e, time.perf_counter() - start)

    def clear_chat(self):
        """
        Reset the conversation context.

        Returns:
            bool: True if reset was successful
        """
        try:
            self._inc_thread_id() # Incrementing the thread ID basically resets the memory
            return True
        except Exception as e:
            print(f"Error clearing chat: {e}")
            return False


def main():
    """
    Example usage demonstrating the agent interface.
    """
    
    args = parse_args()

    agent = Agent(
        provider=args.provider,
        memory=False if args.no_memory else True,
        verbose=args.verbose,
        tokens=args.mode in ["metrics", "metrics-loop"]
    )

    execute_agent(agent, args)


if __name__ == "__main__":
    main()
    