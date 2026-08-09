import json
import time
from datetime import date

import tiktoken
from llama_index.core.agent import FunctionCallingAgentWorker
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from llama_index.core.tools import FunctionTool
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI

# Llama-Index imports
from llama_index.llms.openai import OpenAI
from tavily import TavilyClient

from agent_contract import AgentResult, TokenUsage, count_tool_calls

# Prompt components
from prompts import goal, instructions, knowledge, role

# Load environment variables
from settings import settings
from utils import execute_agent, get_tools_descriptions, parse_args

# Initialize Tavily client
tavily_client = TavilyClient(api_key=settings.tavily_api_key.get_secret_value())

token_counter = TokenCountingHandler(
    tokenizer=tiktoken.encoding_for_model("gpt-4").encode
)

class Agent:
    def __init__(
        self, 
        provider: str = "openai", 
        memory: bool = True,
        verbose: bool = False,
        tokens: bool = False
    ):
        """
        Initialize the Llama-Index agent.
        """
        self.name = "Llama-Index Function Calling Agent"
        
        # Initialize the language model
        self.model = (
            AzureOpenAI(
                engine=settings.azure_deployment_name,
                api_base=f"{settings.azure_endpoint}/deployments/{settings.azure_deployment_name}",
                api_version=settings.azure_api_version,
                api_key=settings.azure_api_key.get_secret_value(),
                callback_manager=CallbackManager([token_counter]) if tokens else None,
                temperature=settings.temperature,
            )
            if provider == "azure" and settings.azure_api_key
            else OpenAI(
                api_key=settings.openai_api_key.get_secret_value(),
                model=settings.openai_model_name,
                temperature=settings.temperature,
            )
            if provider == "openai" and settings.openai_api_key
            else HuggingFaceInferenceAPI(
                model=settings.open_source_model_name
            )
        )

        self.tokens = tokens

        # Create tools
        self.tools = self._create_tools()

        # Create the agent
        self.agent = FunctionCallingAgentWorker.from_tools(
            llm=self.model,
            tools=self.tools,
            max_function_calls=2,
            system_prompt="\n".join([
                role,
                goal,
                instructions,
                "You have access to two primary tools: date_tool and web_search_tool.",
                knowledge,
                # llama_index_react_prompt
            ]),
            verbose=True if verbose else False
        ).as_agent()

        # Extras:
        self.tools_descriptions = get_tools_descriptions(
            [(tool.metadata.name, tool.metadata.description) for tool in self.tools]
        )



    @staticmethod
    def date_tool():
        """
        Function to get the current date.
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
            FunctionTool.from_defaults(
                fn=self.date_tool,
                name="date_tool",
                description="Useful for getting the current date"
            ),
            FunctionTool.from_defaults(
                fn=self.web_search_tool,
                name="web_search_tool",
                description="Useful for searching the web for information"
            )
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
            # Send message to the agent
            response = self.agent.chat(message)
            exec_time = time.perf_counter() - start

            usage = None
            if self.tokens:
                usage = TokenUsage(
                    input_tokens=token_counter.prompt_llm_token_count,
                    output_tokens=token_counter.completion_llm_token_count,
                    total_tokens=token_counter.total_llm_token_count,
                    embedding_tokens=token_counter.total_embedding_token_count,
                )
                token_counter.reset_counts()

            return AgentResult(
                content=str(response),
                elapsed_seconds=exec_time,
                usage=usage,
                tool_calls=count_tool_calls(getattr(response, "sources", None)),
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
            # Reset the agent's chat history
            self.agent.reset()
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
    