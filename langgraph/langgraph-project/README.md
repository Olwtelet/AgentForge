# langgraph-project

A full LangGraph application: a router graph that classifies an incoming
question, asks for more information when the request is ambiguous, and otherwise
answers it from a local vector store built from the documents in
[`knowledge-base/`](knowledge-base/).

## Setup

This project is managed with [PDM](https://pdm-project.org/):

```bash
pdm install
```

```bash
cp .env.example .env
```

Fill in your OpenAI endpoint and key, then run:

```bash
pdm run python -m langgraph_project.main
```

## Structure

```text
src/langgraph_project/
├── agents/
│   ├── agents.py          # the graph: routing, more-info and RAG nodes
│   ├── configuration.py   # runtime configuration
│   └── prompts.py         # prompt loading
├── tools/
│   └── retriever_tool.py  # retrieval over the vector store
├── vector_store/
│   ├── index.py           # index construction
│   └── loader.py          # document loading
├── state.py               # graph state definition
└── main.py                # entry point
```

Prompts live in [`prompts/`](prompts/) as plain text files, so they can be edited
without touching code. The rendered graph is in [`img/graph.png`](img/graph.png).

## Capabilities

| Capability | Where |
| --- | --- |
| Multi-Agent / routing graph | [`src/langgraph_project/agents/agents.py`](src/langgraph_project/agents/agents.py) |
| RAG | [`src/langgraph_project/vector_store/`](src/langgraph_project/vector_store/), [`tools/retriever_tool.py`](src/langgraph_project/tools/retriever_tool.py) |
| State management | [`src/langgraph_project/state.py`](src/langgraph_project/state.py) |
