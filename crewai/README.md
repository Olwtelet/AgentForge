# CrewAI

- Repo: https://github.com/crewAIInc/crewAI
- Documentation: https://docs.crewai.com/

## CrewAI Examples

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

#### Run the examples

To run the examples, you should go to `crewai` directory and run:

```bash
python3 <file_name>.py
```

#### More complex examples

For more complex examples, please refer to the `crewAI-examples` repository: https://github.com/crewAIInc/crewAI-examples