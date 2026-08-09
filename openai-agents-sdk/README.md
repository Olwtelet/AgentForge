# OpenAI Agents SDK

- Repo: https://github.com/openai/openai-agents-python
- Documentation: https://openai.github.io/openai-agents-python/

OpenAI's lightweight agent framework, built around three primitives: agents,
handoffs between agents, and guardrails. Tracing is built in — every run shows
up in the OpenAI dashboard without extra setup.

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
| [`1_tools_and_metrics.py`](1_tools_and_metrics.py) | Function tools and usage metrics |
| [`2_structured_outputs.py`](2_structured_outputs.py) | Structured output with Pydantic models |
| [`3_parallelization_in_workflow.py`](3_parallelization_in_workflow.py) | Running agents in parallel |
| [`4_handoffs_and_streaming.py`](4_handoffs_and_streaming.py) | Handoffs between agents + streaming |
| [`5_agents_as_tools.py`](5_agents_as_tools.py) | Exposing an agent as a tool |
| [`6_output_guardrails.py`](6_output_guardrails.py) | Output guardrails |
| [`7_llm_as_a_judge.py`](7_llm_as_a_judge.py) | LLM-as-a-judge evaluation loop |
| [`8_tracing.py`](8_tracing.py) | Custom traces and spans |

Screenshots of the resulting traces are in [`traces/`](traces/).

## Capabilities

What this directory demonstrates — not the limit of what the SDK can do.

| Capability | Example |
| --- | --- |
| Hello World | [`0_hello_world.py`](0_hello_world.py) |
| Tools | [`1_tools_and_metrics.py`](1_tools_and_metrics.py) |
| Structured Output | [`2_structured_outputs.py`](2_structured_outputs.py) |
| Streaming | [`4_handoffs_and_streaming.py`](4_handoffs_and_streaming.py) |
| Multi-Agent | [`4_handoffs_and_streaming.py`](4_handoffs_and_streaming.py), [`5_agents_as_tools.py`](5_agents_as_tools.py) |
| Tracing | [`8_tracing.py`](8_tracing.py) |
| Evaluation | [`7_llm_as_a_judge.py`](7_llm_as_a_judge.py) |
| Memory | Not implemented |
| Human-in-the-Loop | Not implemented |
| RAG | Not implemented |
| MCP | Not implemented |
