# Contributing to AgentForge

Thanks for helping make AgentForge a better reference. This guide covers the
four things people usually want to do: add an example, add a framework, add a
dependency, and update the benchmarks.

## Ground rules

- **Examples teach one concept.** A reader should be able to open a file, run
  it, and understand a single idea. Resist bundling.
- **Never commit credentials.** Configuration lives in `.env` (git-ignored);
  document new variables in the module's `.env.example` with an empty or
  clearly-fake placeholder.
- **Don't reformat what you didn't change.** The framework examples are pinned
  to specific library versions; whitespace churn buries real changes.
- **Don't invent capabilities.** The [capability matrix](README.md#-capability-matrix)
  is verified against code in this repository. If there's no example, it's ❌.

---

## Setting up

Each framework directory is an independent project. There is no repository-wide
environment — see [Why separate environments](README.md#why-separate-environments).

```bash
cd <framework-directory>
uv sync
cp .env.example .env
```

Lint and tests are run from the repository root and from
`study-agents-differences/` respectively:

```bash
uvx ruff@0.16.1 check .
```

```bash
cd study-agents-differences && uv run pytest
```

---

## Adding an example to an existing framework

1. **Name it by concept, numbered in learning order.** Follow the convention
   already used in that directory — some use `0_`, others `00_`:

   ```text
   crewai/7_memory.py
   llama-index/03_memory.py
   ```

   Prefer these concept names so examples stay comparable across frameworks:

   | Concept | Typical filename |
   | --- | --- |
   | Hello World | `00_hello_world.py` |
   | Tools | `01_tools.py` |
   | Structured Output | `02_structured_outputs.py` |
   | Streaming | `03_streaming.py` |
   | Memory | `04_memory.py` |
   | Human-in-the-Loop | `05_human_in_the_loop.py` |
   | Multi-agent | `06_multi_agent.py` |
   | RAG | `07_rag.py` |
   | MCP | `08_mcp.py` |
   | Tracing | `09_tracing.py` |
   | Evaluation | `10_evaluation.py` |

   **Do not rename existing files** to match this table — the READMEs and the
   root capability matrix link to them by name.

2. **Read config from `settings.py`,** never from hardcoded values or bare
   `os.environ` reads scattered through the file.

3. **Add a docstring or header comment** explaining what the example shows and
   linking to the relevant framework documentation.

4. **Update the tables.** Add a row to that framework's `README.md`, and update
   the [capability matrix](README.md#-capability-matrix) and
   [example table](README.md#-find-an-example) in the root README.

5. **Verify it compiles:**

   ```bash
   python -m compileall -q <your-file>.py
   ```

---

## Adding a new framework

1. **Create a top-level directory** named after the framework (kebab-case:
   `my-framework/`).

2. **Add a `pyproject.toml`** with **direct dependencies only**. Transitive
   dependencies belong in `uv.lock`:

   ```toml
   [project]
   name = "my-framework-examples"
   version = "0.1.0"
   description = "MyFramework examples"
   requires-python = ">=3.12"
   dependencies = [
       "my-framework>=1.0",
       "pydantic-settings>=2.0",
       "python-dotenv>=1.0",
   ]
   ```

   Then generate the lockfile:

   ```bash
   uv lock
   ```

3. **Add `.env.example`** listing every variable the examples read, with
   placeholder values only.

4. **Add `settings.py`** using `pydantic-settings`, matching the pattern in the
   existing directories.

5. **Write at least a Hello World and a Tools example.**

6. **Add a `README.md`** with: links to the framework's docs and repo, setup
   steps (`uv sync` → `cp .env.example .env` → `uv run python …`), and a table
   of the examples.

7. **Update the root README** — the frameworks table, the capability matrix and
   the example table.

8. **Add the lint exemption** for the new directory in [`ruff.toml`](ruff.toml)
   under `[lint.per-file-ignores]`, matching the other example directories.

---

## Adding a framework to the benchmark

The benchmark lives in
[`study-agents-differences/benchmarks/`](study-agents-differences/benchmarks/).
Three steps, no changes to the runner or report needed:

1. **Implement the agent module** as `study-agents-differences/<name>_agent.py`.
   It must expose an `Agent` class whose `chat()` returns an `AgentResult`
   **on success and on failure alike**:

   ```python
   from agent_contract import AgentResult, TokenUsage

   class Agent:
       def __init__(self, provider="openai", memory=True, verbose=False, tokens=False):
           ...

       def chat(self, message: str) -> AgentResult:
           start = time.perf_counter()
           try:
               response = self.agent.run(message)
               return AgentResult(
                   content=response.content,
                   elapsed_seconds=time.perf_counter() - start,
                   usage=TokenUsage(input_tokens=..., output_tokens=..., total_tokens=...),
               )
           except Exception as e:
               return AgentResult.from_error(e, time.perf_counter() - start)

       def clear_chat(self) -> bool:
           ...
   ```

   Returning a bare string, a tuple, or letting an exception escape will fail
   the contract tests in `tests/unit/test_repo_hygiene.py`.

2. **Use the shared tools and prompts.** Import tool code from
   [`shared_functions/`](study-agents-differences/shared_functions/) and the
   system prompt from `prompts.py`. Giving your framework a better tool than the
   others invalidates the comparison.

3. **Register it** in
   [`benchmarks/adapters.py`](study-agents-differences/benchmarks/adapters.py)
   and add its id to the relevant scenario in
   [`benchmarks/scenarios.py`](study-agents-differences/benchmarks/scenarios.py).

---

## Updating benchmark results

Never hand-edit numbers into a README. Run the harness and generate the report:

```bash
cd study-agents-differences
uv run python -m benchmarks.runner --scenario web_search --iterations 10
```

```bash
uv run python -m benchmarks.report benchmarks/results/run-*.jsonl -o benchmarks/results/REPORT.md
```

When sharing results, always state the model, provider, date and library
versions — a number without that context is not reproducible. JSONL result files
are git-ignored by default; commit them only if you deliberately want a snapshot
in version control, and say what produced them.

To add a new scenario, drop a dataset in
[`benchmarks/datasets/`](study-agents-differences/benchmarks/datasets/) and
declare it in `scenarios.py`. Every framework in a scenario must receive
**identical prompts**.

---

## Adding a dependency

Add it to the relevant `pyproject.toml` under `dependencies`, then run `uv lock`
in that directory.

- **Direct dependencies only.** If nothing in the directory imports it, it
  doesn't belong in the manifest.
- **Pin frameworks under comparison** (`agno==1.1.8`) so benchmark runs stay
  reproducible; use lower bounds (`httpx>=0.28.1`) for infrastructure.
- **Never paste `pip freeze` output** into a manifest. Transitive dependencies
  are the lockfile's job.

---

## Running the checks

```bash
uvx ruff@0.16.1 check .
```

```bash
python -m compileall -q .
```

```bash
cd study-agents-differences && uv run pytest
```

Integration tests hit real APIs and spend tokens, so they are excluded by
default. Run them explicitly when you need to:

```bash
uv run pytest -m integration
```

`ruff format` is **not** enforced repository-wide — see the note in
[`ruff.toml`](ruff.toml). Match the surrounding style of the file you're editing.

---

## Pull requests

- One logical change per PR.
- State how you verified it (which commands you ran, what output you saw).
- If you touched the capability matrix, say which file you checked to justify
  each mark.
- If a check fails and you believe it's wrong, explain why rather than
  disabling it.
