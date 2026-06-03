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

Request body also accepts `store` (`pgvector` | `mongodb`) and `useLlm` (bool).
Response: `{ framework, store, query, answer, answerSource, results: [{ sourceUrl, snippet, score }], count }`
where `answerSource` ∈ `llm | extractive | none`.

## How it works
1. The query is embedded locally with **fastembed** (`sentence-transformers/all-MiniLM-L6-v2`,
   384d) — the same model whose vectors fill `vec_all_minilm_l6_v2`.
2. Retrieval: **pgvector** cosine (`<=>`), or **MongoDB** Atlas `$vectorSearch` (when `store=mongodb`;
   index via `scripts/create_mongo_index.py`). Optionally scoped to a company.
3. The `langgraph` framework runs a real **LangGraph** graph (`retrieve → generate | empty`). The
   `generate` node produces an **LLM-backed** RAG answer (cites sources `[n]`) and falls back to an
   extractive summary on any error/missing key. The LLM provider is **OpenAI-compatible and pluggable**:
   default OpenAI, or point `VKP_LLM_BASE_URL`/`VKP_LLM_API_KEY`/`VKP_LLM_MODEL` at Groq, Azure, etc.
   (e.g. Groq: `VKP_LLM_BASE_URL=https://api.groq.com/openai/v1 VKP_LLM_MODEL=llama-3.3-70b-versatile`).

## Run (localhost)
```bash
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
cp .env.example .env        # pick provider profiles (Groq LLM, OpenAI embeddings, ...)
./scripts/run.sh            # loads .env, serves on :8090
```
`scripts/run.sh` sources `.env` (gitignored) for provider config, then runs uvicorn.

### Provider profiles (.env)
- **LLM answer** (OpenAI-compatible, default OpenAI). Groq (free) — verified:
  `VKP_LLM_BASE_URL=https://api.groq.com/openai/v1 VKP_LLM_API_KEY=${GROQ_API_KEY} VKP_LLM_MODEL=llama-3.3-70b-versatile`
- **Store**: `VKP_VECTOR_STORE=pgvector|mongodb`.
- **Query embedding** (must match the indexed table): default `sentence-transformers` (local, 384d,
  `vec_all_minilm_l6_v2`); or OpenAI — `VKP_EMBED_PROVIDER=openai VKP_EMBED_MODEL=text-embedding-3-small
  VKP_VECTOR_TABLE=vec_text_embedding_3_small` (1536d; needs OpenAI credit).

Other env (defaults): `VKP_PG_HOST=localhost VKP_PG_PORT=5432 VKP_PG_DB=vkp VKP_PG_USER=vkp
VKP_PG_PASSWORD=vkp VKP_MONGO_URI=mongodb://localhost:27017/vkp?directConnection=true`.

Consumed by the **vehicle-search-portal** (end-user search UI).
