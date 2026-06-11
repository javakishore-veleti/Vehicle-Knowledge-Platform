# Plan-and-Execute — reference implementations across 7 frameworks

The **live** Plan-and-Execute search framework in VKP (`vehicle-explore-service/app/plan_execute_agent.py`)
is deliberately **framework-free** — plain Python (plan → loop-retrieve → synthesize), so it has no agent-SDK
dependency. These modules are **reference implementations** that show how the *same* pattern is expressed
idiomatically on each major framework, for comparison and learning.

> They are reference/educational code: each needs its own SDK installed **and** an LLM key to actually run.
> They are **not** wired into the running services (that would pull every heavy SDK into one process).

## The pattern, three phases

```
PLAN      an LLM decomposes the question into 2–6 focused sub-queries
EXECUTE   retrieve for each sub-query, merge + dedup the sources
SYNTHESIZE generate one cited answer over the union
```

To keep each file focused on the *framework*, retrieval and synthesis are injected as callables
(`retrieve(subquery)->list[dict]`, `synthesize(query, results)->str`) — see `_common.py`. The framework
part is the **planner + orchestration**.

## The modules

| File | Framework | How it expresses Plan-and-Execute |
|---|---|---|
| `langgraph_pe.py` | **LangGraph** | a compiled `StateGraph`: `plan → execute → synthesize` nodes (add a `replan` edge later) |
| `crewai_pe.py` | **CrewAI** | a planner Agent + Task emits sub-queries; synthesizer follows |
| `llamaindex_pe.py` | **LlamaIndex** | the built-in `SubQuestionQueryEngine` (native plan-and-execute) + a manual variant |
| `haystack_pe.py` | **Haystack 2.x** | a `PromptBuilder → Generator` planner pipeline, then fan-out |
| `openai_pe.py` | **OpenAI Agents SDK** (`agents`) | a planner `Agent` via `Runner.run_sync` |
| `google_pe.py` | **Google ADK** (`google.adk`) | a planner `LlmAgent` driven by the async `InMemoryRunner` |
| `msagent_pe.py` | **Microsoft Agent Framework** (`agent_framework`) | an `OpenAIChatClient` planner agent |

## Usage (sketch)

```python
from langgraph_pe import run     # or crewai_pe / openai_pe / ...

def retrieve(subquery):  # plug in your vector search -> [{sourceUrl, snippet, score}, ...]
    ...
def synthesize(query, results):  # plug in your LLM answer-over-sources
    ...
def llm_complete(prompt):        # a raw single-shot completion (used by the planners that need one)
    ...

answer, plan_steps, results = run(query, llm_complete, retrieve, synthesize)
```

(Signatures vary slightly per framework — the agent-SDK ones build the planner internally, so they take
`(query, retrieve, synthesize, model=...)`; the graph/pipeline ones take an injected `llm_complete`.)

The shipping version that actually runs in the service is the framework-free
`plan_execute_agent.py` + the `auto` router — these references are the "how would I do it on X?" companions.
