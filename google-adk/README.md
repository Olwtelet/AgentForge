# Google ADK

- Repo: https://github.com/google/adk-python
- Documentation: https://google.github.io/adk-docs/

Google Agent Development Kit (ADK) is Google's open-source framework for building, evaluating, and deploying AI agents. It provides a rich set of primitives for tool use, multi-agent orchestration, session management, memory, callbacks, and structured outputs — all tightly integrated with the Gemini model family while also supporting third-party models via LiteLLM.

## Setup

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment variables

Copy the example file and fill in your keys:

```bash
cp .env.example .env
```

Edit `.env` — the variables are listed in [`.env.example`](.env.example):

```
GOOGLE_API_KEY=your-google-api-key
GOOGLE_MODEL_NAME=gemini-2.5-flash

# Required only for 09_litellm.py
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL_NAME=openai/gpt-4o-mini
```

To get a Google API key:
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create or select a project.
3. Navigate to **APIs & Services > Credentials**.
4. Click **Create credentials > API key**.
5. Enable the [Generative Language API](https://console.developers.google.com/apis/api/generativelanguage.googleapis.com/overview).

### 3. Run an example

```bash
uv run python 00_hello_world.py
```

## Examples

| File | Feature | Description |
|------|---------|-------------|
| `00_hello_world.py` | Hello World | Simplest possible agent — one question, one answer |
| `01_tools.py` | Custom Tools | Define and call Python functions as agent tools |
| `02_built_in_tools.py` | Built-in Tools | Use ADK's built-in Google Search and code execution tools |
| `03_agents_as_tools.py` | Agents as Tools | Compose agents by calling sub-agents as tools |
| `04_multi_agent_systems.py` | Multi-Agent Systems | Orchestrate multiple specialised agents |
| `05_workflow_agents.py` | Workflow Agents | SequentialAgent, ParallelAgent, and LoopAgent |
| `06_callbacks.py` | Callbacks | Intercept and modify LLM calls, tool calls, and agent lifecycle |
| `07_memory.py` | Memory | Persist and recall facts across separate sessions |
| `08_structured_outputs.py` | Structured Outputs | Enforce typed JSON output using Pydantic schemas |
| `09_litellm.py` | LiteLLM | Use OpenAI and other non-Google models inside ADK agents |
| `10_artifacts.py` | Artifacts | Save, load, and list binary/text artifacts across sessions |
| `11_mcp_tools.py` | MCP Tools | Connect agents to MCP servers for filesystem and external tools |
| `12_grounding.py` | Grounding | Ground responses in Google Search results with source citations |
| `13_safety.py` | Safety Guardrails | Block unsafe inputs and redact PII from outputs via callbacks |
| `14_evaluation.py` | Evaluation | Score agent behavior against expected tool trajectories and responses |

## Capabilities

What this directory demonstrates — not the limit of what ADK can do.

| Capability | Example |
| --- | --- |
| Hello World | [`00_hello_world.py`](00_hello_world.py) |
| Tools | [`01_tools.py`](01_tools.py), [`02_built_in_tools.py`](02_built_in_tools.py) |
| Structured Output | [`08_structured_outputs.py`](08_structured_outputs.py) |
| Memory | [`07_memory.py`](07_memory.py) |
| Multi-Agent | [`03_agents_as_tools.py`](03_agents_as_tools.py), [`04_multi_agent_systems.py`](04_multi_agent_systems.py), [`05_workflow_agents.py`](05_workflow_agents.py) |
| MCP | [`11_mcp_tools.py`](11_mcp_tools.py) |
| Evaluation | [`14_evaluation.py`](14_evaluation.py) |
| RAG | Grounding via Google Search in [`12_grounding.py`](12_grounding.py); no local vector-store example |
| Streaming | Not implemented |
| Human-in-the-Loop | Not implemented |
| Tracing | Not implemented — [`06_callbacks.py`](06_callbacks.py) intercepts the lifecycle, which is not the same thing |

## Key dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `google-adk` | 1.26.0 | Core framework |
| `google-adk[eval]` | 1.26.0 | Evaluation extras (rouge-score, scikit-learn, pandas) |
| `pydantic` | ≥2.0 | Structured output schemas and settings |
| `pydantic-settings` | ≥2.0 | `.env` file loading via `BaseSettings` |
| `litellm` | latest | Third-party model routing (required for `09_litellm.py`) |
| `mcp` | latest | MCP protocol client (required for `11_mcp_tools.py`) |
