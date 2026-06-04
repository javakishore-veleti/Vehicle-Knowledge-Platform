# vehicle-explore-service

FastAPI AI-search service for VKP. Semantic search over the pgVector embeddings produced by
the indexing subsystem. **Search is framework-routed** so the same request can run against
different agent implementations:

```
POST /api/vehicle-explore/{frameworkName}/search
GET  /api/vehicle-explore/frameworks
GET  /api/vehicle-explore/providers     # provider checkboxes for the UI (creds present + free/default flags)
GET  /health
```

`{frameworkName}` ∈ `langgraph` (implemented) · `crewai` · `llamaindex` · `haystack`
(registered, return 501). Request body:

```json
{ "query": "electric and hybrid vehicles", "companyId": "<optional uuid>", "topK": 8,
  "store": "pgvector", "useLlm": true, "providers": ["groq-70b", "groq-8b"] }
```

`store` ∈ `pgvector | mongodb`; `providers` selects which LLMs answer (omit = server default).
Response: `{ framework, store, query, answer, answerSource, answers, results, count }` where
`answerSource` ∈ `llm | extractive | none` and `answers` is the **per-provider** comparison list
`[{ provider, label, model, answer, ok, error, promptTokens, completionTokens, totalTokens,
finishReason, costUsd, latencyMs }]` — every selected LLM answers the same query so quality,
tokens, cost and latency are compared side by side.

## How it works
1. The query is embedded locally with **fastembed** (`sentence-transformers/all-MiniLM-L6-v2`,
   384d) — the same model whose vectors fill `vec_all_minilm_l6_v2`.
2. Retrieval: **pgvector** cosine (`<=>`), or **MongoDB** Atlas `$vectorSearch` (when `store=mongodb`;
   index via `scripts/create_mongo_index.py`). Optionally scoped to a company.
3. The `langgraph` framework runs a real **LangGraph** graph (`retrieve → generate | empty`). The
   `generate` node fans out to the **selected LLM providers** (in parallel, over the same top-K sources)
   and returns each one's RAG answer (cites sources `[n]`) with tokens/cost/latency, so quality is
   compared side by side; the top-level `answer` is the first successful one (extractive fallback if all
   fail). Providers are mostly **OpenAI-compatible** (one SDK, different base_url/key/model) plus an
   **AWS Bedrock** boto3 path — see `providers.py` REGISTRY (`openai, groq-70b, groq-8b, hf, google,
   anthropic, bedrock`). Default selection = the **free** providers (Groq), so there's no cost or error
   noise unless other providers are opted in via the UI checkboxes / the request `providers[]`.

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

---

## Production KPIs & metrics

What professional teams instrument when deploying an LLM/RAG search system — across five layers.
Items marked ✅ are already exposed by VKP; ⬜ are what a production rollout adds.

### 1. Retrieval quality (the vector-search half)
Measured against a labeled "golden set" of query → relevant-doc pairs:
- **Recall@k / Hit-rate@k** — is the right passage in the top-k? *(the single most important RAG
  metric — bad retrieval caps everything downstream)* ⬜
- **Precision@k, MRR, nDCG** — are the top results the relevant ones, ranked well? ⬜
- **Context precision / context recall** (RAGAS) — how much retrieved context is relevant, and did we
  retrieve all the needed context? ⬜
- **Zero-result / low-confidence rate** — % of queries with nothing above the similarity threshold. ⬜
- The per-source **cosine similarity score** is returned today. ✅

### 2. Answer quality (the generation half) — the "RAG triad"
- **Faithfulness / groundedness** — is every claim supported by retrieved sources? → **hallucination
  rate** (usually the #1 governance KPI). ⬜
- **Answer relevancy** — does it actually answer the question? ⬜
- **Citation / attribution accuracy** — do the `[n]` citations point to the right source? *(VKP emits
  `[n]` citations, which makes this checkable)* ✅(checkable) / ⬜(measured)
- **Correctness / completeness** vs ground-truth. ⬜
- Tooling: **RAGAS, TruLens, DeepEval, LangSmith, Arize Phoenix** (LLM-as-judge + periodic human review).

### 3. Operational / SRE
- **Latency P50 / P95 / P99** and **time-to-first-token** — tails are what users feel. ✅(per-call latency) / ⬜(percentile dashboards)
- **Throughput (QPS), concurrency, availability/uptime, error rate** — per provider. ✅(per-provider ok/error)
- **Token usage** (in/out) and **cost per query** / per provider/model. ✅
- **Cache hit rate** (embedding cache, *semantic* query cache). ⬜

### 4. Product / business engagement (the north-star layer)
- **Answer rate / success rate** — % of queries returning a usable answer. ⬜
- **Query reformulation & abandonment rate** — repeated rephrasing / leaving = retrieval failing
  (a strong implicit-quality signal). ⬜
- **Citation click-through**, queries/session, retention. ⬜
- **Explicit feedback** — 👍/👎, CSAT, feedback rate *(the `search_feedback` collection anticipates this)*. ⬜
- **Deflection / conversion** — for VKP: search → "Build & Price" / test-drive / lead. Usually the
  **north-star metric**. ⬜

### 5. Safety, governance & data health
- **Hallucination, toxicity, PII leakage, prompt-injection** detection; **refusal / over-refusal rate**;
  bias/fairness. ⬜
- **Index freshness / staleness**, **coverage** (docs/companies indexed), **crawl success rate & robots
  compliance**, chunk quality. ⬜(partly visible via snapshots)
- **Provenance** — every answer traceable to a source + timestamp (source URLs ✅; add crawl dates ⬜).

### How they're produced
- **Offline eval harness** in CI: golden dataset + RAGAS/LLM-judge on every prompt/model/index change
  (catches regressions).
- **Online**: A/B tests / interleaving + live guardrail monitoring + a feedback loop.
- **Cost/quality frontier**: VKP's side-by-side provider comparison (quality vs tokens vs latency vs $)
  is exactly the analysis used to pick a default model / route by query difficulty.

---

## Guardrails (input & output)

Guardrails are where a demo becomes deployable. They sit in three places: **input** (the query),
**output** (the answer), and a RAG-specific one in the **retrieved context**. Build them **layered &
cheap-first** (rules → small classifier → LLM-judge only when needed). For VKP they can run on the
**free Groq** key (or **Llama Guard** via Groq); make them toggleable (`VKP_GUARDRAILS=on`).

### Input guardrails (on the query, before retrieval/generation)
| Guardrail | Why | Typical implementation |
|---|---|---|
| **Scope / topic filter** | Keep it about vehicles; reject off-domain & competitor probing | small classifier / LLM-judge |
| **Prompt-injection / jailbreak** | "ignore previous instructions", system-prompt exfiltration | Llama Guard / Prompt Guard, Rebuff, Lakera, heuristics |
| **PII detection / redaction** | Don't log/forward user PII | Presidio, regex (email/phone/SSN/card) |
| **Toxicity / abuse** | Block harassment | OpenAI Moderation, Azure Content Safety, Llama Guard |
| **Length / rate / cost limits** | Stop abuse & runaway spend | max tokens, per-user rate limit, budget cap |
| **Language / sanitization** | Route non-supported langs; prevent query injection | langdetect; parameterized vector/SQL queries |

### Output guardrails (on the answer, before returning)
| Guardrail | Why | Implementation |
|---|---|---|
| **Groundedness / faithfulness** ⭐ | Block claims not supported by retrieved sources (hallucination) | NLI entailment or LLM-judge per claim; abstain if unsupported |
| **Citation validation** | `[n]` must map to real retrieved sources, not fabricated | programmatic check vs the result set |
| **Abstention / confidence floor** | If top score < threshold → "I don't have that" not a guess | similarity-threshold gate |
| **PII / secret leakage** | No PII from context or system-prompt in the answer | output scanner |
| **Brand / policy safety** | No competitor disparagement, no legal/financial advice, pricing disclaimers | policy rules + judge |
| **Factual-risk gating** ⭐ | VKP: wrong **price/spec = liability** — flag numeric claims not present verbatim in sources | numeric-claim verification |

### RAG-specific: indirect prompt injection
The *retrieved documents* can carry malicious instructions (a crawled page that says "ignore your
rules…"). Mitigate by treating retrieved content as **data, not instructions** (delimit/escape it),
**sanitizing crawled content at ingest**, tracking **provenance**, and never letting retrieved text
trigger tools/actions.

### Where they'd live in VKP (LangGraph)
```
input_guard → retrieve → [sanitize context] → generate → output_guard → answer
     ↘ (blocked) → refuse                          ↘ (ungrounded) → "not in my sources"
```
Each guard is a conditional edge to a `refuse`/`abstain` terminal — the same pattern as the existing
`retrieve → generate | empty` graph.

### Guardrail KPIs (measure the guardrails too)
- **Block rate** & **false-positive (over-blocking) rate** — over-refusal kills UX.
- **Injection catch rate** (against a red-team set), **hallucination-caught rate**.
- **Added latency / cost** per guardrail; **escalation / refusal rate**.

> Highest-value for VKP: (1) a **groundedness / abstention** output check (never invent a price/spec;
> say "not in my sources"), and (2) **input scope + injection** filtering — both cheap on free Groq.
>
> Frameworks: NVIDIA **NeMo Guardrails**, **Guardrails AI**, Meta **Llama Guard / Prompt Guard**,
> **AWS Bedrock Guardrails**, **Azure AI Content Safety**, OpenAI Moderation, Lakera / Rebuff.
