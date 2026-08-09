# Pydantic AI

- Repo: https://github.com/pydantic/pydantic-ai
- Documentation: https://ai.pydantic.dev/agents/

Pydantic AI brings the Pydantic model-validation approach to agents: typed
dependencies, typed results, output validators, and a graph layer for stateful
multi-step flows.

## Setup

```bash
uv sync
```

```bash
cp .env.example .env
```

Fill in `OPENAI_API_KEY`, then run any example:

```bash
uv run python 00_hello_world.py
```

<details>
<summary>Without <code>uv</code></summary>

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

</details>

## Examples

| File | Concept |
| --- | --- |
| [`00_hello_world.py`](00_hello_world.py) | Hello World |
| [`01_tools_and_metrics.py`](01_tools_and_metrics.py) | Tools and usage metrics |
| [`02_built_in_tools.py`](02_built_in_tools.py) | Built-in tools |
| [`03_streaming.py`](03_streaming.py) | Streaming responses |
| [`04_structured_outputs.py`](04_structured_outputs.py) | Typed structured output |
| [`05_output_validators.py`](05_output_validators.py) | Output validators and retries |
| [`06_message_history.py`](06_message_history.py) | Message history (memory) |
| [`07_agent_delegation.py`](07_agent_delegation.py) | Delegating to another agent |
| [`08_programmatic_handoff.py`](08_programmatic_handoff.py) | Programmatic handoff between agents |
| [`09_stateful_graphs.py`](09_stateful_graphs.py) | Stateful graphs with `pydantic-graph` |
| [`10_human_in_the_loop.py`](10_human_in_the_loop.py) | Human-in-the-loop |

## Capabilities

What this directory demonstrates — not the limit of what Pydantic AI can do.

| Capability | Example |
| --- | --- |
| Hello World | [`00_hello_world.py`](00_hello_world.py) |
| Tools | [`01_tools_and_metrics.py`](01_tools_and_metrics.py), [`02_built_in_tools.py`](02_built_in_tools.py) |
| Structured Output | [`04_structured_outputs.py`](04_structured_outputs.py) |
| Streaming | [`03_streaming.py`](03_streaming.py) |
| Memory | [`06_message_history.py`](06_message_history.py) |
| Human-in-the-Loop | [`10_human_in_the_loop.py`](10_human_in_the_loop.py) |
| Multi-Agent | [`07_agent_delegation.py`](07_agent_delegation.py), [`08_programmatic_handoff.py`](08_programmatic_handoff.py) |
| RAG | Not implemented |
| MCP | Not implemented |
| Tracing | Not implemented — the framework integrates with Logfire, but no example here |
| Evaluation | Not implemented — [`05_output_validators.py`](05_output_validators.py) validates outputs, which is not evaluation |
