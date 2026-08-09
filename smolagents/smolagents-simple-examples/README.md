# smolagents

- Repo: https://github.com/huggingface/smolagents
- Documentation: https://huggingface.co/docs/smolagents/en/index

Hugging Face's minimal agent library. Its distinguishing idea is the
`CodeAgent`: instead of emitting JSON tool calls, the model writes Python code
that calls tools directly.

## Setup

```bash
uv sync
```

```bash
cp .env.example .env
```

Fill in `HF_TOKEN` and `OPENAI_API_KEY`, then run any example:

```bash
uv run python simple-agent.py
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
| [`simple-agent.py`](simple-agent.py) | Hello World — a single agent with tools |
| [`multi-agent-simple.py`](multi-agent-simple.py) | Minimal manager/worker agent setup |
| [`multi-agent.py`](multi-agent.py) | Multi-agent system with web search and page inspection |

Generated output from the examples is written to [`outputs/`](outputs/).

## Capabilities

What this directory demonstrates — not the limit of what smolagents can do.

| Capability | Example |
| --- | --- |
| Hello World | [`simple-agent.py`](simple-agent.py) |
| Tools | [`simple-agent.py`](simple-agent.py) |
| Multi-Agent | [`multi-agent.py`](multi-agent.py), [`multi-agent-simple.py`](multi-agent-simple.py) |
| Structured Output | Not implemented |
| Streaming | Not implemented |
| Memory | Not implemented |
| Human-in-the-Loop | Not implemented |
| RAG | Not implemented |
| MCP | Not implemented |
| Tracing | Not implemented |
| Evaluation | Not implemented |

> ⚠️ `CodeAgent` executes model-generated Python. Run untrusted prompts in a
> sandbox only — see [SECURITY.md](../../SECURITY.md).
