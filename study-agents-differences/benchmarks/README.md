# Benchmarks

Reproducible, cross-framework measurements for the agents in
[`study-agents-differences/`](../).

## What is held constant

The point of this harness is that the framework is the *only* variable. Every
run of a scenario shares:

| Held constant | Where it is defined |
| --- | --- |
| Model / deployment | [`settings.py`](../settings.py) (`azure_deployment_name` / `openai_model_name`) |
| Temperature | [`settings.py`](../settings.py) (`temperature`, default `0.0`) |
| System prompt | [`prompts.py`](../prompts.py) (`role`, `goal`, `instructions`, `knowledge`) |
| User prompts | [`datasets/`](datasets/) — one JSON file per scenario |
| API tool code | [`shared_functions/`](../shared_functions/) — the *same* Python functions are registered in every framework |
| Knowledge base | [`knowledge_base/cl_matches/`](../knowledge_base/cl_matches/) |
| Memory on/off | `--memory` flag, applied to every framework alike |
| Iterations, timeout, retries | `RunConfig` in [`runner.py`](runner.py) |
| Result shape | `AgentResult` in [`agent_contract.py`](../agent_contract.py) |

## What is *not* fully equalised

Be explicit about this when reading results:

- **Web search.** Agno uses its built-in `TavilyTools` toolkit; the other
  frameworks register a plain Tavily call. The toolkit may issue different
  requests. Compare with that in mind.
- **Retrieval.** Each framework uses its own vector store and chunking
  (`ChromaDb` for Agno, `Chroma` for LangGraph, `VectorStoreIndex` for
  LlamaIndex). The `rag` scenario measures whole pipelines, not just the LLM.
- **Agent loop.** ReAct, function-calling and graph agents take different
  numbers of model round-trips by design. That difference *is* the thing being
  measured.
- **Tool-call counts.** Only reported where the framework exposes them.
  `null` means "not reported", which is not the same as `0`.

## Running

```bash
uv run python -m benchmarks.runner --list
```

```bash
uv run python -m benchmarks.runner --scenario web_search --iterations 5 --provider azure
```

Useful flags:

| Flag | Effect |
| --- | --- |
| `--scenario NAME` | Repeatable. Defaults to every scenario. |
| `--framework ID` | Repeatable. Restrict to specific frameworks. |
| `--iterations N` | Runs per prompt (default `3`). |
| `--memory` | Keep conversation history between iterations. |
| `--reuse-agent` | Reuse one agent instead of rebuilding it each iteration. |
| `--retries N` | Retry failed runs (default `0`). |
| `--timeout S` | Runs slower than this are recorded as failures. |
| `--output PATH` | JSONL destination (default `results/run-<timestamp>.jsonl`). |

Results are written as JSONL, one object per run:

```json
{"framework": "langgraph", "scenario": "web_search", "prompt_id": "ucl_2024_explicit",
 "iteration": 1, "model": "gpt-4o-mini", "provider": "azure", "temperature": 0.0,
 "memory": false, "elapsed_seconds": 2.43, "success": true, "input_tokens": 100,
 "output_tokens": 80, "total_tokens": 180, "tool_calls": 2, "error": null}
```

Failed runs are recorded too, with `success: false` and the error message, so
failure rates stay visible.

## Reporting

```bash
uv run python -m benchmarks.report benchmarks/results/run-20250101T120000Z.jsonl
```

Write straight to a file with `-o`:

```bash
uv run python -m benchmarks.report benchmarks/results/*.jsonl -o benchmarks/results/REPORT.md
```

## Status

**Not executed — API credentials required.** This repository ships the harness
and the datasets, not recorded results. Numbers you see in a report come from
your own runs. Historical figures collected by the original author are kept, and
labelled as such, in [`../README.md`](../README.md).

## Adding a framework

1. Implement an agent module whose `Agent.chat()` returns an `AgentResult`
   (see [`agent_contract.py`](../agent_contract.py)).
2. Register it in [`adapters.py`](adapters.py).
3. Add its id to the relevant scenario in [`scenarios.py`](scenarios.py).

No changes to the runner or the report are needed.
