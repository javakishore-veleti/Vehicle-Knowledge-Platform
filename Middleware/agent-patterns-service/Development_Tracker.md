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
- **Done:** 26 / 80 — Reflection × 8 + **LangGraph × 10** + **CrewAI × 10** — all verified live · **Planned:** 54
- **Scaffold (service skeleton + registry + API + venv):** ✅ done & verified (`/health` → 26 cells, `/agent-patterns/patterns`)
- **Installs:** all via `requirements.txt` — `uv pip install -r requirements.txt` (or pip). **venv = Python 3.12** (CrewAI/most agent SDKs lack 3.14 wheels).
- **Use-case axis** (the 5 concrete VKP use cases per pattern, 50 total): selectable via `useCase` in the request. **Done: 5/50** — Reflection × 5 (LangGraph), all verified live. The rest are the next track. `GET /agent-patterns/{pattern}/usecases` lists them.

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
| LlamaIndex | `react/llamaindex.py` | ⬜ | `ReActAgent` |
| Haystack | `react/haystack.py` | ⬜ | ToolInvoker loop |
| OpenAI Agents SDK | `react/openai_agents.py` | ⬜ | `function_tool` + Agent |
| Google ADK | `react/google_adk.py` | ⬜ | LlmAgent + FunctionTool |
| Microsoft Agent Framework | `react/msagent.py` | ⬜ | agent + tools |
| AWS Strands | `react/strands.py` | ⬜ | `@tool` + Agent |

### 3. RAG pipeline  — *retrieve → generate*
| Framework | File | Development Status | Notes |
|---|---|---|---|
| LangGraph | `rag/langgraph.py` | ✅ | retrieve → generate StateGraph |
| CrewAI | `rag/crewai.py` | ✅ | retriever tool + answer agent |
| LlamaIndex | `rag/llamaindex.py` | ⬜ | `RetrieverQueryEngine` (native) |
| Haystack | `rag/haystack.py` | ⬜ | Retriever → PromptBuilder → Generator pipeline |
| OpenAI Agents SDK | `rag/openai_agents.py` | ⬜ | retrieval tool + Agent |
| Google ADK | `rag/google_adk.py` | ⬜ | retrieval tool + LlmAgent |
| Microsoft Agent Framework | `rag/msagent.py` | ⬜ | retrieval tool + agent |
| AWS Strands | `rag/strands.py` | ⬜ | retrieval tool + Agent |

### 4. Plan-and-Execute  — *plan up front → execute each (+ re-plan)*
| Framework | File | Development Status | Notes |
|---|---|---|---|
| LangGraph | `plan_execute/langgraph.py` | ✅ | plan → execute → synthesize graph |
| CrewAI | `plan_execute/crewai.py` | ✅ | planner + executor crew |
| LlamaIndex | `plan_execute/llamaindex.py` | ⬜ | `SubQuestionQueryEngine` |
| Haystack | `plan_execute/haystack.py` | ⬜ | planner pipeline + fan-out |
| OpenAI Agents SDK | `plan_execute/openai_agents.py` | ⬜ | planner Agent + executors |
| Google ADK | `plan_execute/google_adk.py` | ⬜ | `SequentialAgent` |
| Microsoft Agent Framework | `plan_execute/msagent.py` | ⬜ | planner + worker agents |
| AWS Strands | `plan_execute/strands.py` | ⬜ | planner + worker Agents |

### 5. Router / dispatcher  — *classify → route*
| Framework | File | Development Status | Notes |
|---|---|---|---|
| LangGraph | `router/langgraph.py` | ✅ | conditional edges |
| CrewAI | `router/crewai.py` | ✅ | router agent → delegated crew |
| LlamaIndex | `router/llamaindex.py` | ⬜ | `RouterQueryEngine` |
| Haystack | `router/haystack.py` | ⬜ | conditional router component |
| OpenAI Agents SDK | `router/openai_agents.py` | ⬜ | agent handoffs |
| Google ADK | `router/google_adk.py` | ⬜ | LlmAgent routing / transfer |
| Microsoft Agent Framework | `router/msagent.py` | ⬜ | routing agent |
| AWS Strands | `router/strands.py` | ⬜ | router Agent |

### 6. Prompt chaining / parallelization  — *deterministic chain · fan-out → merge*
| Framework | File | Development Status | Notes |
|---|---|---|---|
| LangGraph | `chaining/langgraph.py` | ✅ | sequential / fan-out graph |
| CrewAI | `chaining/crewai.py` | ✅ | sequential tasks |
| LlamaIndex | `chaining/llamaindex.py` | ⬜ | `QueryPipeline` |
| Haystack | `chaining/haystack.py` | ⬜ | multi-component pipeline |
| OpenAI Agents SDK | `chaining/openai_agents.py` | ⬜ | chained Runner calls |
| Google ADK | `chaining/google_adk.py` | ⬜ | SequentialAgent / ParallelAgent |
| Microsoft Agent Framework | `chaining/msagent.py` | ⬜ | workflow chain |
| AWS Strands | `chaining/strands.py` | ⬜ | chained Agents |

### 7. Multi-agent (supervisor / workers)  — *delegate → specialists → merge*
| Framework | File | Development Status | Notes |
|---|---|---|---|
| LangGraph | `multi_agent/langgraph.py` | ✅ | supervisor graph |
| CrewAI | `multi_agent/crewai.py` | ✅ | hierarchical crew |
| LlamaIndex | `multi_agent/llamaindex.py` | ⬜ | `AgentRunner` + sub-agents |
| Haystack | `multi_agent/haystack.py` | ⬜ | multi-agent pipeline |
| OpenAI Agents SDK | `multi_agent/openai_agents.py` | ⬜ | supervisor + handoffs |
| Google ADK | `multi_agent/google_adk.py` | ⬜ | parent LlmAgent + sub-agents |
| Microsoft Agent Framework | `multi_agent/msagent.py` | ⬜ | group chat / orchestrator |
| AWS Strands | `multi_agent/strands.py` | ⬜ | agents-as-tools |

### 8. Evaluator-optimizer  — *generate ↔ judge loop*
| Framework | File | Development Status | Notes |
|---|---|---|---|
| LangGraph | `evaluator/langgraph.py` | ✅ | generate ↔ evaluate cycle (conditional) |
| CrewAI | `evaluator/crewai.py` | ✅ | maker + judge crew, looped |
| LlamaIndex | `evaluator/llamaindex.py` | ⬜ | `Evaluator` + retry |
| Haystack | `evaluator/haystack.py` | ⬜ | loop with eval component |
| OpenAI Agents SDK | `evaluator/openai_agents.py` | ⬜ | producer + judge Agents |
| Google ADK | `evaluator/google_adk.py` | ⬜ | LoopAgent |
| Microsoft Agent Framework | `evaluator/msagent.py` | ⬜ | producer + judge agents |
| AWS Strands | `evaluator/strands.py` | ⬜ | producer + judge Agents |

### 9. ReWOO  — *plan all tool calls blind, run WithOut Observation*
| Framework | File | Development Status | Notes |
|---|---|---|---|
| LangGraph | `rewoo/langgraph.py` | ✅ | planner → worker (no obs) → solver graph |
| CrewAI | `rewoo/crewai.py` | ✅ | planner + parallel workers + solver |
| LlamaIndex | `rewoo/llamaindex.py` | ⬜ | plan tools upfront, batch run |
| Haystack | `rewoo/haystack.py` | ⬜ | planner → parallel branches → solver |
| OpenAI Agents SDK | `rewoo/openai_agents.py` | ⬜ | planner emits calls, batch execute |
| Google ADK | `rewoo/google_adk.py` | ⬜ | plan + ParallelAgent workers |
| Microsoft Agent Framework | `rewoo/msagent.py` | ⬜ | plan + parallel workers |
| AWS Strands | `rewoo/strands.py` | ⬜ | plan + batch tool exec |

### 10. Tree of Thoughts (ToT)  — *branch → evaluate → backtrack*
| Framework | File | Development Status | Notes |
|---|---|---|---|
| LangGraph | `tot/langgraph.py` | ✅ | branch/evaluate/select graph |
| CrewAI | `tot/crewai.py` | ✅ | proposer + scorer crew |
| LlamaIndex | `tot/llamaindex.py` | ⬜ | multi-branch + evaluator |
| Haystack | `tot/haystack.py` | ⬜ | branch pipeline + scorer |
| OpenAI Agents SDK | `tot/openai_agents.py` | ⬜ | proposer + evaluator Agents |
| Google ADK | `tot/google_adk.py` | ⬜ | branches + evaluator agent |
| Microsoft Agent Framework | `tot/msagent.py` | ⬜ | proposer + evaluator agents |
| AWS Strands | `tot/strands.py` | ⬜ | proposer + evaluator Agents |

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
