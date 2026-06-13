# Agent Patterns Service — Development Tracker

A single, living tracker for implementing **every agentic-AI pattern in every tech stack**, as
production-grade, immediately-deployable code in this repo.

---

## Requirement
Implement **each agentic pattern** in **all the major tech stacks / frameworks / SDKs** —
LangGraph, CrewAI, LlamaIndex, Haystack, OpenAI Agents SDK, Google ADK (Agent Development Kit),
Microsoft Agent Framework, and AWS Strands — as a **new API service** in this codebase, invoked over a
clean API (REST now; Airflow for any batch variants later).

## Objective
See exactly **how each stack's code looks** for the same pattern, side by side, so the concepts are
mastered through real implementations — not toy snippets.

## Purpose
**Professional, production-ready code I can deploy immediately** — proper structure, config, error
handling, lazy per-SDK imports, graceful degradation, and a uniform invocation contract. Doubles as a
reusable reference library and a stack-comparison harness.

## Approach / Architecture
- **New service:** `Middleware/agent-patterns-service/` — FastAPI, port **:8094**, own venv.
- **Matrix layout:** `app/patterns/<pattern>/<framework>.py` — one cell per (pattern × framework),
  each registering a `run(ctx)` into a central **registry**.
- **Uniform contract:** `POST /agent-patterns/{pattern}/{framework}/run` with a typed pydantic
  request/response; `GET /agent-patterns/patterns` returns the coverage matrix; `GET /health`.
- **Lazy SDK imports:** the service boots without any heavy SDK installed; a cell only imports its SDK
  inside `run()`, so missing SDK/key → a clean error for that cell only. Install per deployment.
- **Domain:** vehicle/automotive (reuses VKP's domain) so every cell is realistic, not academic.

## Status legend
| Symbol | Meaning |
|---|---|
| ✅ | Code complete (committed; runs once its SDK + an LLM key are present) |
| 🟡 | In progress (this cycle) |
| ⬜ | Planned |
| ⛔ | Blocked (SDK dep conflict / API gap — see Notes) |

## Progress summary
- **Patterns:** 10 · **Frameworks:** 8 · **Cells:** 80
- **Done:** 80 / 80 — ✅ **MATRIX COMPLETE.** Reflection × 8 + **LangGraph × 10** + **CrewAI × 10** + **LlamaIndex × 9** + **Haystack × 9** + **OpenAI Agents × 9** + **Google ADK × 9** + **Microsoft Agent Framework × 9** + **AWS Strands × 9** — every pattern × framework cell verified live · **Planned:** 0
- **Scaffold (service skeleton + registry + API + venv):** ✅ done & verified (`/health` → 80 cells, `/agent-patterns/patterns`)
- **Installs:** all via `requirements.txt` — `uv pip install -r requirements.txt` (or pip). **venv = Python 3.12** (CrewAI/most agent SDKs lack 3.14 wheels).
- **Use-case axis** (the 5 concrete VKP use cases per pattern, selectable via `useCase`): **LangGraph 50/50 ✅ COMPLETE.** Now propagating to the other 7 frameworks, one pattern per cycle. Each pattern's use-case instructions live in the pattern's `_base.py` (`USE_CASES` catalog) so every framework cell pulls the SAME catalog and differs only in mechanics. **CrewAI:** ✅ **50/50 COMPLETE** — all 10 patterns × 5 VKP use cases verified live. Every pattern's use-case behavior lives in a shared `_base` catalog consumed by BOTH LangGraph and CrewAI, so the two columns differ only in framework mechanics: reflection/evaluator/chaining/router/tot/rewoo/multi-agent/plan-execute (structure + deterministic helpers match exactly), RAG (use-case-scoped search tool, sources match byte-for-byte), react (per-use-case toolset from crawl/vehicle_spec/NHTSA/dealer/find_moved). **LlamaIndex:** ✅ **50/50 COMPLETE** — all 10 patterns × 5 use cases verified live over the shared `_base` catalogs via `li.complete`, with NATIVE LlamaIndex constructs where they fit: ReAct → workflow `ReActAgent` (per-use-case FunctionTool subset), RAG → `VectorStoreIndex` + `MetadataFilters` (brand/doc_type scoping), plan-execute → `SubQuestionQueryEngine` for multi-brand-comparison (+ `_base` plan/exec for the fixed-plan/tool use cases).
**Haystack:** ✅ **50/50 COMPLETE** — all 10 patterns × 5 use cases verified live over the shared `_base` catalogs via `hay.complete`, with NATIVE Haystack constructs where they fit: RAG → BM25 `Pipeline` + retriever `filters` (meta.brand / meta.doc_type scoping), ReAct → native `Agent` + per-use-case `Tool` subset.
**OpenAI Agents:** 40/50 — Reflection ✅ + Tree-of-Thoughts ✅ + Multi-agent ✅ + Chaining ✅ + Router ✅ + Evaluator-optimizer ✅ + ReWOO ✅ + Plan-execute ✅ (all verified live via `oa.complete` over the shared `_base` catalogs; rewoo plan sizes 2/9/6/3/8 + plan-execute steps 4/5/3/6/5 match the other cells, query-rewriter scores via REAL retrieval). **Left (OpenAI Agents):** rag, react (native Agent + @function_tool).
**Dep note (openai pin):** a later SDK install silently downgraded `openai` to 2.24.0, which broke `openai-agents` (needs `ResponseToolSearchCall`). Bumped back to **openai 2.41.1** and re-smoke-tested all 5 openai-using frameworks (langgraph/crewai/llamaindex/haystack/openai_agents) — no regressions. The venv shares one `openai` across 6 SDKs, so re-verify cross-framework after any version change.
**Next frameworks for the use-case axis:** Google ADK, Microsoft, Strands (0/50 each). `GET /agent-patterns/{pattern}/usecases` lists them.
- **Dep note (2026-06):** the 6-SDK install churn bumped `langchain-core`/`langgraph-prebuilt` to 1.x; **`langgraph` core pinned to `>=1.0`** to match (prebuilt 1.x needs `langgraph.stream`). Also fixed a LangGraph reflection node/state-key collision (`critique`) that newer LangGraph rejects — nodes are now `do_*`-prefixed.

---

## Tasks — per pattern × tech stack

File path = `app/patterns/<pattern>/<file>`. Frameworks (fixed order):
LangGraph · CrewAI · LlamaIndex · Haystack · OpenAI Agents SDK · Google ADK · Microsoft Agent Framework · AWS Strands.

### 1. Reflection / Reflexion  — *generate → self-critique → revise*   `✅ cycle 1 done`
| Framework | File | Development Status | Notes |
|---|---|---|---|
| LangGraph | `reflection/langgraph.py` | ✅ | StateGraph: draft → critique → revise — **verified live** |
| CrewAI | `reflection/crewai.py` | ✅ | writer + critic agents, sequential crew |
| LlamaIndex | `reflection/llamaindex.py` | ✅ | LLM abstraction drives the 3 steps |
| Haystack | `reflection/haystack.py` | ✅ | OpenAIGenerator per step |
| OpenAI Agents SDK | `reflection/openai_agents.py` | ✅ | writer + critic Agents, `Runner.run_sync` |
| Google ADK | `reflection/google_adk.py` | ✅ | LlmAgent via async InMemoryRunner |
| Microsoft Agent Framework | `reflection/msagent.py` | ✅ | OpenAIChatClient agents |
| AWS Strands | `reflection/strands.py` | ✅ | Strands Agent per step |

### 2. ReAct  — *reason ↔ act loop (tool-calling)*
| Framework | File | Development Status | Notes |
|---|---|---|---|
| LangGraph | `react/langgraph.py` | ✅ | `create_react_agent` + tool |
| CrewAI | `react/crewai.py` | ✅ | agent with tools |
| LlamaIndex | `react/llamaindex.py` | ✅ | native 0.14 **workflow `ReActAgent`** + `FunctionTool` (async `.run`) |
| Haystack | `react/haystack.py` | ✅ | native **`agents.Agent`** + **`tools.Tool`** (chat-generator loop) |
| OpenAI Agents SDK | `react/openai_agents.py` | ✅ | native **Agent** + **`@function_tool`** + `Runner.run_sync` |
| Google ADK | `react/google_adk.py` | ✅ | native **LlmAgent** + **FunctionTool** (ADK tool loop) |
| Microsoft Agent Framework | `react/msagent.py` | ✅ | native **Agent** + **`@tool`** (AF tool loop) |
| AWS Strands | `react/strands.py` | ✅ | native **Agent** + **`@tool`** (Strands agent loop) |

### 3. RAG pipeline  — *retrieve → generate*
| Framework | File | Development Status | Notes |
|---|---|---|---|
| LangGraph | `rag/langgraph.py` | ✅ | retrieve → generate StateGraph |
| CrewAI | `rag/crewai.py` | ✅ | retriever tool + answer agent |
| LlamaIndex | `rag/llamaindex.py` | ✅ | native **`VectorStoreIndex.as_query_engine`** over the corpus |
| Haystack | `rag/haystack.py` | ✅ | native **Pipeline**: BM25 retriever → PromptBuilder → generator |
| OpenAI Agents SDK | `rag/openai_agents.py` | ✅ | Agent whose `@function_tool` retrieves from the corpus |
| Google ADK | `rag/google_adk.py` | ✅ | LlmAgent whose FunctionTool retrieves from the corpus |
| Microsoft Agent Framework | `rag/msagent.py` | ✅ | Agent whose `@tool` retrieves from the corpus |
| AWS Strands | `rag/strands.py` | ✅ | Agent whose `@tool` retrieves from the corpus |

### 4. Plan-and-Execute  — *plan up front → execute each (+ re-plan)*
| Framework | File | Development Status | Notes |
|---|---|---|---|
| LangGraph | `plan_execute/langgraph.py` | ✅ | plan → execute → synthesize graph |
| CrewAI | `plan_execute/crewai.py` | ✅ | planner + executor crew |
| LlamaIndex | `plan_execute/llamaindex.py` | ✅ | native **`SubQuestionQueryEngine`** (plan → sub-query → combine) |
| Haystack | `plan_execute/haystack.py` | ✅ | plan sub-questions → answer each → synthesize |
| OpenAI Agents SDK | `plan_execute/openai_agents.py` | ✅ | planner Agent → execute sub-steps → synthesizer Agent |
| Google ADK | `plan_execute/google_adk.py` | ✅ | planner LlmAgent → execute sub-steps → synthesizer LlmAgent |
| Microsoft Agent Framework | `plan_execute/msagent.py` | ✅ | planner Agent → execute sub-steps → synthesizer Agent |
| AWS Strands | `plan_execute/strands.py` | ✅ | planner Agent → execute sub-steps → synthesizer Agent |

### 5. Router / dispatcher  — *classify → route*
| Framework | File | Development Status | Notes |
|---|---|---|---|
| LangGraph | `router/langgraph.py` | ✅ | conditional edges |
| CrewAI | `router/crewai.py` | ✅ | router agent → delegated crew |
| LlamaIndex | `router/llamaindex.py` | ✅ | LLM classify → tailored handler (`li.complete`) |
| Haystack | `router/haystack.py` | ✅ | generator classifies → tailored prompt |
| OpenAI Agents SDK | `router/openai_agents.py` | ✅ | classifier Agent → tailored specialist Agent |
| Google ADK | `router/google_adk.py` | ✅ | classifier LlmAgent → tailored specialist LlmAgent |
| Microsoft Agent Framework | `router/msagent.py` | ✅ | classifier Agent → tailored specialist Agent |
| AWS Strands | `router/strands.py` | ✅ | classifier Agent → tailored specialist Agent |

### 6. Prompt chaining / parallelization  — *deterministic chain · fan-out → merge*
| Framework | File | Development Status | Notes |
|---|---|---|---|
| LangGraph | `chaining/langgraph.py` | ✅ | sequential / fan-out graph |
| CrewAI | `chaining/crewai.py` | ✅ | sequential tasks |
| LlamaIndex | `chaining/llamaindex.py` | ✅ | 2-step LLM chain rewrite → answer (`li.complete`) |
| Haystack | `chaining/haystack.py` | ✅ | native **Pipeline**: rewrite → OutputAdapter → answer |
| OpenAI Agents SDK | `chaining/openai_agents.py` | ✅ | 2-Agent chain: rewrite → answer (Runner) |
| Google ADK | `chaining/google_adk.py` | ✅ | 2-LlmAgent chain: rewrite → answer (InMemoryRunner) |
| Microsoft Agent Framework | `chaining/msagent.py` | ✅ | 2-Agent chain: rewrite → answer (one event loop) |
| AWS Strands | `chaining/strands.py` | ✅ | 2-Agent chain: rewrite → answer (sync) |

### 7. Multi-agent (supervisor / workers)  — *delegate → specialists → merge*
| Framework | File | Development Status | Notes |
|---|---|---|---|
| LangGraph | `multi_agent/langgraph.py` | ✅ | supervisor graph |
| CrewAI | `multi_agent/crewai.py` | ✅ | hierarchical crew |
| LlamaIndex | `multi_agent/llamaindex.py` | ✅ | spec/pricing/safety specialists → lead composes |
| Haystack | `multi_agent/haystack.py` | ✅ | spec/pricing/safety specialists → lead composes |
| OpenAI Agents SDK | `multi_agent/openai_agents.py` | ✅ | spec/pricing/safety Agents → lead Agent composes |
| Google ADK | `multi_agent/google_adk.py` | ✅ | spec/pricing/safety LlmAgents → lead LlmAgent composes |
| Microsoft Agent Framework | `multi_agent/msagent.py` | ✅ | spec/pricing/safety Agents → lead Agent composes |
| AWS Strands | `multi_agent/strands.py` | ✅ | spec/pricing/safety Agents → lead Agent composes |

### 8. Evaluator-optimizer  — *generate ↔ judge loop*
| Framework | File | Development Status | Notes |
|---|---|---|---|
| LangGraph | `evaluator/langgraph.py` | ✅ | generate ↔ evaluate cycle (conditional) |
| CrewAI | `evaluator/crewai.py` | ✅ | maker + judge crew, looped |
| LlamaIndex | `evaluator/llamaindex.py` | ✅ | generate → judge → revise (one round) |
| Haystack | `evaluator/haystack.py` | ✅ | generate → judge → revise (one round) |
| OpenAI Agents SDK | `evaluator/openai_agents.py` | ✅ | generator Agent → judge Agent → revise (one round) |
| Google ADK | `evaluator/google_adk.py` | ✅ | generator LlmAgent → judge LlmAgent → revise |
| Microsoft Agent Framework | `evaluator/msagent.py` | ✅ | generator Agent → judge Agent → revise |
| AWS Strands | `evaluator/strands.py` | ✅ | generator Agent → judge Agent → revise |

### 9. ReWOO  — *plan all tool calls blind, run WithOut Observation*
| Framework | File | Development Status | Notes |
|---|---|---|---|
| LangGraph | `rewoo/langgraph.py` | ✅ | planner → worker (no obs) → solver graph |
| CrewAI | `rewoo/crewai.py` | ✅ | planner + parallel workers + solver |
| LlamaIndex | `rewoo/llamaindex.py` | ✅ | planner emits blind tool calls → execute (no LLM) → solve |
| Haystack | `rewoo/haystack.py` | ✅ | planner blind tool calls → execute (no LLM) → solve |
| OpenAI Agents SDK | `rewoo/openai_agents.py` | ✅ | planner Agent (blind) → execute (no LLM) → solver Agent |
| Google ADK | `rewoo/google_adk.py` | ✅ | planner LlmAgent (blind) → execute (no LLM) → solver LlmAgent |
| Microsoft Agent Framework | `rewoo/msagent.py` | ✅ | planner Agent (blind) → execute (no LLM) → solver Agent |
| AWS Strands | `rewoo/strands.py` | ✅ | planner Agent (blind) → execute (no LLM) → solver Agent |

### 10. Tree of Thoughts (ToT)  — *branch → evaluate → backtrack*
| Framework | File | Development Status | Notes |
|---|---|---|---|
| LangGraph | `tot/langgraph.py` | ✅ | branch/evaluate/select graph |
| CrewAI | `tot/crewai.py` | ✅ | proposer + scorer crew |
| LlamaIndex | `tot/llamaindex.py` | ✅ | branch (propose 3) → evaluate (score) → select |
| Haystack | `tot/haystack.py` | ✅ | branch (propose 3) → evaluate (score) → select |
| OpenAI Agents SDK | `tot/openai_agents.py` | ✅ | proposer Agent (3) → judge Agent scores → select |
| Google ADK | `tot/google_adk.py` | ✅ | proposer LlmAgent (3) → judge LlmAgent scores → select |
| Microsoft Agent Framework | `tot/msagent.py` | ✅ | proposer Agent (3) → judge Agent scores → select |
| AWS Strands | `tot/strands.py` | ✅ | proposer Agent (3) → judge Agent scores → select |

---

## Invocation
- **Run a cell:** `POST /agent-patterns/{pattern}/{framework}/run` with `{"input": "..."}`
- **Coverage matrix:** `GET /agent-patterns/patterns`
- **Health:** `GET /health`
- Batch variants (bulk runs / scheduled) can be wrapped as Airflow DAGs later via `airflow-adapter-service`.

## How to add a cell
1. Create `app/patterns/<pattern>/<framework>.py` with a `run(ctx: dict) -> dict` and call
   `registry.register("<pattern>", "<framework>", run)` at the bottom.
2. Import it from `app/patterns/<pattern>/__init__.py` (lazy SDK imports inside `run`).
3. Add the SDK to `requirements.txt` (optional extra) and flip this tracker's status to ✅.
