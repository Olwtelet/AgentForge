import argparse
import os
import statistics
from typing import Tuple

from agent_contract import AgentResult

AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))


# Function to get available agent modules and their display names.
# Display names are derived from the file name so that no agent (and no
# knowledge base / vector store) is instantiated just to list the options.
def get_available_agents() -> dict[str, str]:
    agents = {}
    for file in sorted(os.listdir(AGENTS_DIR)):
        if file.endswith('_agent.py'):
            module_name = file[:-3]  # Remove .py
            display_name = module_name.replace('_', ' ').title().replace('Api', 'API')
            agents[module_name] = display_name
    return agents


# Generate a list of the available tools
def get_tools_descriptions(tools_tuple: list[Tuple[str, str]]) -> str:
    """
    Generate a list of the available tools.

    Args:
        tools_tuple (list[Tuple[str, str], ...]): A list of (tool name, tool description) pairs.
    """
    return f"{'\n'.join([f'- {tool} ({desc})' for tool, desc in tools_tuple])}"


def parse_args():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--provider",
        type=str,
        choices=["azure", "openai", "other"],
        default="azure",
        help="The LLM provider to use in the agent."
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["metrics", "metrics-loop"],
        help="Mode. Should be either 'metrics' or 'metrics-loop'"
    )
    parser.add_argument(
        "--iter",
        type=int,
        help="Number of iterations. Required if mode is 'metrics-loop'."
    )
    parser.add_argument(
        "--no-memory",
        action="store_true",
        help="Maintain conversation history in the agent."
    )
    parser.add_argument(
        "--create",
        action="store_true",
        help="Create a new agent instance each time."
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print the Agent's logs and messages."
    )
    parser.add_argument(
        "--file",
        type=str,
        help="File to save the chat history."
    )

    args = parser.parse_args()

    if args.mode is None:
        args.verbose = True

    if args.mode == "metrics-loop" and args.iter is None:
        parser.error("--iter is required when --mode is 'metrics-loop'.")

    return args


def summarize_results(results: list[AgentResult]) -> dict:
    """
    Aggregate a list of AgentResult into summary statistics.

    Failed runs are excluded from latency/token means but counted as errors.
    """
    successes = [r for r in results if r.success]
    times = [r.elapsed_seconds for r in successes]

    def _avg_usage(field: str) -> float:
        if not successes:
            return 0.0
        values = [
            getattr(r.usage, field) or 0
            for r in successes
            if r.usage is not None
        ]
        return float(sum(values) / len(successes)) if values else 0.0

    return {
        "iterations": len(results),
        "errors": len(results) - len(successes),
        "mean_time": statistics.fmean(times) if times else 0.0,
        "std_time": statistics.pstdev(times) if len(times) > 1 else 0.0,
        "embedding_tokens": _avg_usage("embedding_tokens"),
        "input_tokens": _avg_usage("input_tokens"),
        "output_tokens": _avg_usage("output_tokens"),
        "total_tokens": _avg_usage("total_tokens"),
    }


def execute_agent(agent: object, args: argparse.Namespace):
    """
    Execute the agent with the given arguments.
    """
    while True:
        query = input("You: ")

        if query.lower() in ['exit', 'quit']:
            break

        iterations = args.iter if args.mode == "metrics-loop" else 1

        if args.mode in ["metrics", "metrics-loop"]:
            results: list[AgentResult] = []

            for _ in range(iterations):
                if args.create:
                    AgentClass = type(agent)
                    agent = AgentClass(
                        provider=args.provider,
                        memory=False if args.no_memory else True,
                        verbose=args.verbose,
                        tokens=True
                    )
                    if args.verbose:
                        print("New agent created.")

                result = agent.chat(query)
                results.append(result)

                if args.verbose:
                    output = result.content if result.success else f"[error] {result.error}"
                    if args.file:
                        with open(args.file, "a", encoding="utf-8") as f:
                            f.write(f"Assistant: {output}\n")
                    else:
                        print(f"Assistant: {output}\n")

            stats = summarize_results(results)
            print(
                f"{'-'*50}\n"
                f"Mode: {args.mode}\n"
                f"Iterations: {stats['iterations']} ({stats['errors']} errors)\n"
                f"\033[92mResponse Time: {stats['mean_time']:.2f} ± {stats['std_time']:.2f}s\033[0m\n"
                f"{'-'*50}\n"
                f"Embedding Tokens: {stats['embedding_tokens']:.1f}\n"
                f"LLM Prompt Tokens: {stats['input_tokens']:.1f}\n"
                f"LLM Completion Tokens: {stats['output_tokens']:.1f}\n"
                f"\033[36mTotal LLM Token Count: {stats['total_tokens']:.1f}\033[0m\n"
                f"{'-'*50}\n"
            )

        else:
            result = agent.chat(query)
            if args.verbose:
                if result.success:
                    print(f"Assistant: {result.content}")
                else:
                    print(f"Assistant error: {result.error}")
