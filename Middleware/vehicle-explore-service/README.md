# vehicle-explore-service

FastAPI AI-search service for VKP. Semantic search over the pgVector embeddings produced by
the indexing subsystem. **Search is framework-routed** so the same request can run against
different agent implementations:

```
POST /api/vehicle-explore/{frameworkName}/search
GET  /api/vehicle-explore/frameworks
GET  /health
```

`{frameworkName}` ∈ `langgraph` (implemented) · `crewai` · `llamaindex` · `haystack`
(registered, return 501). Request body:

```json
{ "query": "electric and hybrid vehicles", "companyId": "<optional uuid>", "topK": 5 }
```

Response: `{ framework, query, answer, results: [{ sourceUrl, snippet, score }], count }`.

## How it works
1. The query is embedded locally with **fastembed** (`sentence-transformers/all-MiniLM-L6-v2`,
   384d) — the same model whose vectors fill `vec_all_minilm_l6_v2`.
2. **pgvector** cosine distance (`<=>`) ranks the nearest chunks (optionally scoped to a company).
3. `answer` is an extractive summary of the top snippets. The LLM-backed answer (OpenAI/Azure)
   slots into `frameworks.synthesize_answer()` behind the same contract once a key/quota exists.

## Run (localhost)
```bash
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
./.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8090
```
Config via env (defaults shown): `VKP_PG_HOST=localhost VKP_PG_PORT=5432 VKP_PG_DB=vkp
VKP_PG_USER=vkp VKP_PG_PASSWORD=vkp VKP_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
VKP_VECTOR_TABLE=vec_all_minilm_l6_v2`.

Consumed by the **vehicle-search-portal** (end-user search UI).
