# AutoGen

- Repo: https://github.com/microsoft/autogen
- Documentation: https://microsoft.github.io/autogen/stable/index.html

## About AutoGen 0.4

AutoGen `v0.4` was rebuilt from the ground up on an asynchronous, event-driven
architecture to address observability, flexibility, interactive control and
scale.

The API is layered: the `Core` API is a scalable, event-driven actor framework
for agentic workflows; the `AgentChat` API sits on top of it, offering a
task-driven, high-level framework for interactive agentic applications. It
replaces AutoGen `v0.2` (now maintained separately as [AG2](../ag2/)).

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

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

</details>

## Examples

| File | Concept |
| --- | --- |
| [`0_hello_world.py`](0_hello_world.py) | Hello World |
| [`1_tools.py`](1_tools.py) | Function tools and their schemas |
| [`2_streaming_and_metrics.py`](2_streaming_and_metrics.py) | Streaming responses and usage metrics |
| [`3_structured_outputs.py`](3_structured_outputs.py) | Structured output with Pydantic models |
| [`4_human_in_the_loop.py`](4_human_in_the_loop.py) | Human-in-the-loop interaction |
| [`5_multi_agent_teams.py`](5_multi_agent_teams.py) | Agent teams and termination conditions |
| [`6_agents_as_tool.py`](6_agents_as_tool.py) | Delegating to an agent exposed as a tool |
| [`7_memory.py`](7_memory.py) | Memory across turns |

### Full project

[`autogen-project/`](autogen-project/) is a larger PDM-managed application with a
knowledge base, custom agents and a RAG pipeline. See its
[README](autogen-project/README.md).

## Capabilities

What this directory demonstrates — not the limit of what AutoGen can do.

| Capability | Example |
| --- | --- |
| Hello World | [`0_hello_world.py`](0_hello_world.py) |
| Tools | [`1_tools.py`](1_tools.py) |
| Structured Output | [`3_structured_outputs.py`](3_structured_outputs.py) |
| Streaming | [`2_streaming_and_metrics.py`](2_streaming_and_metrics.py) |
| Memory | [`7_memory.py`](7_memory.py) |
| Human-in-the-Loop | [`4_human_in_the_loop.py`](4_human_in_the_loop.py) |
| Multi-Agent | [`5_multi_agent_teams.py`](5_multi_agent_teams.py), [`6_agents_as_tool.py`](6_agents_as_tool.py) |
| RAG | [`autogen-project/`](autogen-project/) |
| MCP | Not implemented |
| Tracing | Not implemented |
| Evaluation | Not implemented |
