# agent-patterns-service (:8094)

Every **agentic pattern** implemented in **every framework**, side by side — production reference + a
stack-comparison harness. See `Development_Tracker.md` for the full status matrix.

## Run
```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt            # core; add the framework SDKs you want to run
export OPENAI_API_KEY=...                   # or GROQ_API_KEY=... (free, OpenAI-compatible)
uvicorn app.main:app --port 8094
```

## API
- `GET  /agent-patterns/patterns` — coverage matrix (which frameworks per pattern)
- `POST /agent-patterns/{pattern}/{framework}/run` — body `{"input": "..."}`
- `GET  /health`

```bash
curl -X POST localhost:8094/agent-patterns/reflection/langgraph/run \
  -H 'content-type: application/json' -d '{"input":"Is the Toyota RAV4 Prime a plug-in hybrid?"}'
```

## Layout
```
app/
  main.py        FastAPI app + uniform run endpoint
  registry.py    (pattern, framework) -> run(ctx) registry + coverage matrix
  config.py      OpenAI / Groq config
  llm.py         shared complete()  (cells that need a model OBJECT build it from config)
  models.py      RunReq / RunResp (pydantic)
  patterns/<pattern>/<framework>.py   one cell each; lazy SDK import inside run()
```

Adding a cell: write `run(ctx)->dict`, `registry.register("<pattern>","<framework>", run)`, import it
from the pattern's `__init__.py`, and flip its row in `Development_Tracker.md` to ✅.
