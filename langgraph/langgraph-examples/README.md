# LangGraph Examples

- Repo: https://github.com/langchain-ai/langgraph
- Documentation: https://langchain-ai.github.io/langgraph/

LangGraph models agents as explicit state graphs: nodes are steps, edges are
transitions, and a checkpointer persists state so runs can be interrupted,
resumed and inspected.

## Setup

```bash
uv sync
```

```bash
cp .env.example .env
```

Fill in your OpenAI endpoint and key.

<details>
<summary>Without <code>uv</code></summary>

A `requirements.txt` is also provided for this module:

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

</details>

### Jupyter

Make sure you select the environment created above as the notebook kernel. All
required packages are installed there.

## Examples

| File | Concept |
| --- | --- |
| [`customer-support.ipynb`](customer-support.ipynb) | A customer-support bot built up in four parts: tools, state, interrupts (human-in-the-loop) and specialised sub-graphs |

Diagrams for each part are in [`img/`](img/).

## Related LangGraph code in this repository

| What | Where |
| --- | --- |
| Hello World / tools / memory agent | [`../../study-agents-differences/langgraph_agent.py`](../../study-agents-differences/langgraph_agent.py) |
| RAG + API tools agent | [`../../study-agents-differences/langgraph_rag_api_agent.py`](../../study-agents-differences/langgraph_rag_api_agent.py) |
| Full RAG application | [`../langgraph-project/`](../langgraph-project/) |
