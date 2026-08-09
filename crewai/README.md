# CrewAI

- Repo: https://github.com/crewAIInc/crewAI
- Documentation: https://docs.crewai.com/

CrewAI models agent systems as a *crew*: role-playing agents assigned to tasks,
executed sequentially or hierarchically. Flows add explicit, event-driven
control over how those crews run.

## Setup

```bash
uv sync
```

```bash
cp .env.example .env
```

Fill in `OPENAI_API_KEY`, then run any example:

```bash
uv run python 0_hello_world.py
```

<details>
<summary>Without <code>uv</code></summary>

A `requirements.txt` is also provided for this module:

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

</details>

## Examples

| File | Concept |
| --- | --- |
| [`0_hello_world.py`](0_hello_world.py) | Hello World — one agent, one task |
| [`1_tools.py`](1_tools.py) | Custom tools |
| [`2_built_in_tools.py`](2_built_in_tools.py) | CrewAI's built-in tool library |
| [`3_streaming.py`](3_streaming.py) | Streaming responses |
| [`4_structured_outputs.py`](4_structured_outputs.py) | Structured output with Pydantic models |
| [`5_tasks.py`](5_tasks.py) | Task configuration, context and output files |
| [`6_callbacks.py`](6_callbacks.py) | Step and task callbacks |
| [`7_memory.py`](7_memory.py) | Short-term, long-term and entity memory |
| [`8_reasoning.py`](8_reasoning.py) | Agent reasoning and planning |
| [`9_knowledge.py`](9_knowledge.py) | Knowledge sources (RAG) |
| [`10_multi_agent_collaboration.py`](10_multi_agent_collaboration.py) | Multi-agent collaboration |
| [`11_flows.py`](11_flows.py) | Flows — event-driven orchestration |
| [`12_flows_with_agents.py`](12_flows_with_agents.py) | Flows combined with crews |
| [`13_crew_simplification.py`](13_crew_simplification.py) | YAML-driven crew configuration |

Rendered flow plots produced by the examples live in [`plots/`](plots/).

### Full projects

| Project | What it shows |
| --- | --- |
| [`crewai-project/`](crewai-project/) | PDM-managed crew with custom tools and a knowledge base |
| [`chatbot-example/`](chatbot-example/) | Chatbot crew with a knowledge base |
| [`crewai-simple-examples/`](crewai-simple-examples/) | Standalone scripts, including a human-input tool wired to a Chainlit UI |

## Capabilities

What this directory demonstrates — not the limit of what CrewAI can do.

| Capability | Example |
| --- | --- |
| Hello World | [`0_hello_world.py`](0_hello_world.py) |
| Tools | [`1_tools.py`](1_tools.py), [`2_built_in_tools.py`](2_built_in_tools.py) |
| Structured Output | [`4_structured_outputs.py`](4_structured_outputs.py) |
| Streaming | [`3_streaming.py`](3_streaming.py) |
| Memory | [`7_memory.py`](7_memory.py) |
| Multi-Agent | [`10_multi_agent_collaboration.py`](10_multi_agent_collaboration.py) |
| RAG | [`9_knowledge.py`](9_knowledge.py) |
| Human-in-the-Loop | Chainlit-bound tool in [`crewai-simple-examples/agents.py`](crewai-simple-examples/agents.py); no standalone script |
| MCP | Not implemented |
| Tracing | Not implemented — [`6_callbacks.py`](6_callbacks.py) shows lifecycle callbacks, which is not the same thing |
| Evaluation | Not implemented |

## More complex examples

For larger reference applications, see the official
[crewAI-examples](https://github.com/crewAIInc/crewAI-examples) repository.
