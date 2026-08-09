# Legacy run logs

Raw assistant transcripts captured with the original `--mode metrics-loop --file`
flow, before the JSONL benchmark harness existed. They are kept for reference
only: they contain responses, not structured metrics, and the model, library
versions and prompts used to produce them are not recorded.

New runs should use the structured harness instead:

```bash
uv run python -m benchmarks.runner --scenario rag --iterations 10
```
