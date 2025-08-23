# Autogen

- Repo: https://github.com/microsoft/autogen
- Documentation: https://microsoft.github.io/autogen/stable/index.html

## About AutoGen 0.4

AutoGen `v0.4` was built from-the-ground-up adopting an asynchronous, event-driven architecture to address issues such as observability, flexibility, interactive control, and scale.

The `v0.4` API is layered: the `Core` API is the foundation layer offering a scalable, event-driven actor framework for creating agentic workflows; the `AgentChat` API is built on `Core`, offering a task-driven, high-level framework for building interactive agentic applications. It is a replacement for AutoGen `v0.2`

## Autogen Examples

### How to setup

#### Virtual environment

Create a simple virtual environment with:

```bash
python3 -m venv .venv
```

Then activate it with:
```bash
# On Linux/macOS
source .venv/bin/activate
# On Windows
.venv\Scripts\activate
```

And install the requirements with:
```bash
pip install -r requirements.txt
```

#### .env

See .env.example and create a .env (on the root of the repository).
You need to get an open AI endpoint and key and fill them in.
