import asyncio
import json
import time
from datetime import date

from openai import AsyncAzureOpenAI, AsyncOpenAI
from pydantic_ai import Agent as PydanticAgent

# Pydantic AI imports
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.tools import Tool
from tavily import TavilyClient

from agent_contract import AgentResult, TokenUsage

# Prompt components
from prompts import goal, instructions, knowledge, role

# Load environment variables
from settings import settings
from utils import execute_agent, get_tools_descriptions, parse_args

# Initialize Tavily client
tavily_client = TavilyClient(api_key=settings.tavily_api_key.get_secret_value())


class Agent:
    def __init__(
        self,
        provider: str = "openai",
        memory: bool = True,
        verbose: bool = False,
        tokens: bool = False
        ):
        """
        Initialize the Pydantic AI agent.
        """
        self.name = "PydanticAI Agent"

        # Initialize the language model.
        # Pydantic AI expects one of its own model classes; for both OpenAI and
        # Azure OpenAI we wrap the corresponding async client in OpenAIModel.
        if provider == "azure" and settings.azure_api_key:
            client = AsyncAzureOpenAI(
                azure_endpoint=settings.azure_endpoint,
                azure_deployment=settings.azure_deployment_name,
                api_version=settings.azure_api_version,
                api_key=settings.azure_api_key.get_secret_value(),
            )
            self.model = OpenAIModel(settings.azure_deployment_name, openai_client=client)
        elif provider == "openai" and settings.openai_api_key:
            client = AsyncOpenAI(api_key=settings.openai_api_key.get_secret_value())
            self.model = OpenAIModel(settings.openai_model_name, openai_client=client)
        else:
            raise ValueError(
                f"No credentials available for provider '{provider}'. "
                "Set the corresponding API key in your .env file."
            )

        # Create tools
        #   - We dont use dependency injection because we cannot define tool metadata
        self.tools = self._create_tools()
        
        # Create the agent with a comprehensive system prompt
        self.agent = PydanticAgent(
            model=self.model,
            tools=self.tools, # this could be ignored if we used dependency injection
            system_prompt="\n".join([
                role,
                goal,
                instructions,
                "You have access to two primary tools: date and web_search.",
                knowledge
            ]),
            deps_type=str,
            result_type=str,
            model_settings={"temperature": settings.temperature},
        )

        self.memory = memory
        self.tokens = tokens

        # Conversation history
        self.messages = []

        # Extras:
        self.tools_descriptions = get_tools_descriptions(
            [(tool.name, tool.description) for tool in self.tools]
        )


    def _create_tools(self):
        """
        Create and register tools for the agent.
        """
        # @self.agent.tool_plain
        async def date_tool() -> str:
            """Get the current date"""
            today = date.today()
            return today.strftime("%B %d, %Y")

        # @self.agent.tool_plain
        async def web_search_tool(query: str) -> str:
            """Search the web for information"""
            # Call Tavily's search and dump the results as a JSON string
            search_response = tavily_client.search(query)
            results = json.dumps(search_response.get('results', []))
            # print(f"Web Search Results for '{query}':")
            # print(results)
            return results
        
        return [
            Tool(date_tool, name="date_tool", description="Gets the current date"),
            Tool(web_search_tool, name="web_search_tool", description="Searches the web for information")
        ]

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
            # Create new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # Run the async function in the loop
                result = loop.run_until_complete(
                    self.agent.run(message, deps=message, message_history=self.messages)
                )
            finally:
                loop.close()

            exec_time = time.perf_counter() - start

            # Maintain conversation history
            if self.memory:
                self.messages.extend(result.new_messages())

            usage = None
            if self.tokens:
                run_usage = result.usage()
                usage = TokenUsage(
                    input_tokens=getattr(run_usage, "request_tokens", None),
                    output_tokens=getattr(run_usage, "response_tokens", None),
                    total_tokens=getattr(run_usage, "total_tokens", None),
                    embedding_tokens=0,
                )

            return AgentResult(
                content=result.data, elapsed_seconds=exec_time, usage=usage
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
            self.messages = []
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
    