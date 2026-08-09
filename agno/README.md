# Agno

- Repo: https://github.com/agno-agi/agno
- Documentation: https://docs.agno.com/introduction

Agno is a lightweight, performance-oriented agent framework with built-in
toolkits (search, finance, knowledge bases), first-class async and streaming,
and a workflow layer for multi-step pipelines.

## Setup

```bash
uv sync
```

```bash
cp .env.example .env
```

Fill in `OPENAI_API_KEY`, then run any example:

```bash
uv run python 1_simple_agent.py
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
| [`1_simple_agent.py`](1_simple_agent.py) | Hello World |
| [`2_async.py`](2_async.py) | Async execution |
| [`3_streaming.py`](3_streaming.py) | Streaming responses |
| [`4_parallel_tool_calling.py`](4_parallel_tool_calling.py) | Calling multiple tools in parallel |
| [`5_human_in_the_loop.py`](5_human_in_the_loop.py) | Human confirmation before tool execution |
| [`6_workflow_example.py`](6_workflow_example.py) | Workflows with state, caching and Pydantic models |

## Capabilities

What this repository demonstrates — not the limit of what Agno can do.

| Capability | Example |
| --- | --- |
| Hello World | [`1_simple_agent.py`](1_simple_agent.py) |
| Tools | [`4_parallel_tool_calling.py`](4_parallel_tool_calling.py) |
| Streaming | [`3_streaming.py`](3_streaming.py) |
| Human-in-the-Loop | [`5_human_in_the_loop.py`](5_human_in_the_loop.py) |
| Structured Output | Shown inside [`6_workflow_example.py`](6_workflow_example.py), not standalone |
| Multi-Agent | Shown as a workflow in [`6_workflow_example.py`](6_workflow_example.py); no agent-to-agent delegation example |
| Memory | [`../study-agents-differences/agno_agent.py`](../study-agents-differences/agno_agent.py) |
| RAG | [`../study-agents-differences/agno_rag_api_agent.py`](../study-agents-differences/agno_rag_api_agent.py) |
| MCP | Not implemented |
| Tracing | Not implemented |
| Evaluation | Not implemented |
