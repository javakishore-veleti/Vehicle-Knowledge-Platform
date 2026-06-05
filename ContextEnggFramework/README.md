# Context Engineering Framework (CEF)

An independent capability within the Vehicle Knowledge Platform that implements the
**Context Engineering Framework** (`Docs/Research/ContextEngineeringFramework.jpeg`) — "how you
upgrade RAG to the next level". It orchestrates the *right knowledge, right scope, right role, right
time* into an LLM reasoning step, then evolves its memory from the outcome.

It is **its own sub-project** (own `Middleware/` + `Portals/`) but **reuses VKP** heavily rather than
rebuilding: the same Postgres/pgvector + MongoDB, the same RBAC/session libraries, and the same agent
frameworks as the reasoning engine. Domain stays **vehicle knowledge**.

## The pipeline (from the diagram)

```
User Query
   │
   ▼
Context Orchestrator      understand intent, plan steps, decide what context is needed
   │      ├── Retrieval Layer    hybrid search (dense+sparse), structured + unstructured, external APIs
   │      ├── Memory Layer       conversation history, workflow state, user prefs, long-term memory
   │      └── Permission Layer   RBAC/ABAC, attribute access, data boundaries, policy enforcement
   ▼
Context Assembly Layer    aggregate, deduplicate, rank, structure and scope the context
   ▼
LLM (Reasoning Engine)    generate, reason, plan, take actions  (← the VKP agent roster)
   ▼
Response
   ▼
Context Evolution Loop    critique, feedback, memory update, new knowledge  (loops back)
```

### The 5 context-engineering strategies (implemented in the Assembly Layer)
1. **Selection** — write less, include more: rank + pick the most relevant context, don't dump everything.
2. **Compression** — keep history, lose weight: summarise older turns, incremental updates.
3. **Ordering** — position matters: critical rules first, the immediate task last (models attend least to the middle).
4. **Isolation** — divide & conquer: split work across specialised agents (planner/retriever/reasoner).
5. **Format optimisation** — structure is signal: token-efficient YAML/Markdown blocks.

## What CEF REUSES vs builds new

| Layer | Reuses (VKP) | New (CEF) |
|---|---|---|
| Retrieval | pgvector/Mongo + vector/fts/hybrid (explore/agentic) | — |
| Permission | `vkp-jwt-rbac`, `vkp-session-security` | attribute/data-boundary scoping |
| Memory | session ledger | MongoDB conversation + long-term memory store |
| Reasoning | the 8-framework agent roster (agentic-service / explore) | framework selection per query |
| Evolution | `search_feedback` pattern | critique + memory-update loop |
| Orchestrator + Assembly | — | the whole thing (the heart of CEF) |

## Layout

```
ContextEnggFramework/
  Middleware/
    context-engine-service/    # Python FastAPI :8093 — the orchestrator pipeline
    context-admin-service/     # Spring Boot :8094 — strategy config + eval harness
  Portals/
    cef-search-portal/         # static SPA :5173 — customer context-aware vehicle chat
    cef-admin-portal/          # static SPA :5174 — strategy config + eval
```

## Phases — ALL DONE
1. ✅ **context-engine-service** orchestrator (retrieval → assembly[5 strategies] → reasoning → evolution), reusing VKP retrieval + agent roster.
2. ✅ MongoDB-backed **memory** + the **Context Evolution loop** — verified multi-turn continuity.
3. ✅ **context-admin-service** (Spring Boot) — context-strategy CRUD + an eval harness scorecarding groundedness.
4. ✅ **Portals** — cef-admin-portal (strategy/eval) + cef-search-portal (context-aware chat). `bash Portals/serve.sh`.
