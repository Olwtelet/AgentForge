# AG2

- Repo: https://github.com/ag2ai/ag2
- Documentation: https://docs.ag2.ai/latest/

AG2 (formerly AutoGen 0.2) builds agent systems around *conversable agents*: a
`UserProxyAgent` drives the interaction and an `AssistantAgent` responds, with
tool calls and human input threaded through the conversation.

## Setup

```bash
uv sync
```

```bash
cp .env.example .env
```

Fill in `OPENAI_API_KEY`, then run any example:

```bash
uv run python 0_sample_agent.py
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
| [`0_sample_agent.py`](0_sample_agent.py) | Hello World — assistant driven by a user proxy |
| [`1_agent_with_tools.py`](1_agent_with_tools.py) | Tools — registering Python functions |
| [`2_structured_outputs.py`](2_structured_outputs.py) | Structured output with Pydantic models |
| [`3_human_in_the_loop.py`](3_human_in_the_loop.py) | Human-in-the-loop via the user proxy |
| [`4_multi_agent.py`](4_multi_agent.py) | Multi-agent group conversation |

## Capabilities

What this directory demonstrates — not the limit of what AG2 can do.

| Capability | Example |
| --- | --- |
| Hello World | [`0_sample_agent.py`](0_sample_agent.py) |
| Tools | [`1_agent_with_tools.py`](1_agent_with_tools.py) |
| Structured Output | [`2_structured_outputs.py`](2_structured_outputs.py) |
| Human-in-the-Loop | [`3_human_in_the_loop.py`](3_human_in_the_loop.py) |
| Multi-Agent | [`4_multi_agent.py`](4_multi_agent.py) |
| Streaming | Not implemented |
| Memory | Not implemented |
| RAG | Not implemented |
| MCP | Not implemented |
| Tracing | Not implemented |
| Evaluation | Not implemented |
