"""Real LangGraph agent for the 'langgraph' framework.

A compiled StateGraph: retrieve -> (conditional) -> generate | empty -> END.
- retrieve: vector search (pgvector or mongodb) over the indexed chunks.
- conditional edge: skip generation entirely when nothing was retrieved.
- generate: LLM (OpenAI) RAG answer, with graceful fallback to an extractive summary.

This replaces the inline retrieve->synthesize pipeline with an actual LangGraph graph, so the
framework name in the URL routes to a genuine agent implementation that's easy to extend
(add grading / query-rewrite / multi-hop nodes).
"""
from functools import lru_cache
from typing import Optional, TypedDict

from . import frameworks


class AgentState(TypedDict, total=False):
    query: str
    company_id: Optional[str]
    top_k: int
    store: str
    use_llm: bool
    results: list
    answer: str
    answer_source: str


def _retrieve_node(state: AgentState) -> dict:
    results = frameworks._retrieve(state["query"], state.get("company_id"), state["top_k"], state["store"])
    return {"results": results}


def _generate_node(state: AgentState) -> dict:
    answer, source = frameworks.synthesize_answer(state["query"], state["results"], state.get("use_llm", True))
    return {"answer": answer, "answer_source": source}


def _empty_node(state: AgentState) -> dict:
    return {"answer": "No relevant vehicle content was found for this query.", "answer_source": "none"}


def _route_after_retrieve(state: AgentState) -> str:
    return "generate" if state.get("results") else "empty"


@lru_cache(maxsize=1)
def _graph():
    from langgraph.graph import StateGraph, START, END
    g = StateGraph(AgentState)
    g.add_node("retrieve", _retrieve_node)
    g.add_node("generate", _generate_node)
    g.add_node("empty", _empty_node)
    g.add_edge(START, "retrieve")
    g.add_conditional_edges("retrieve", _route_after_retrieve, {"generate": "generate", "empty": "empty"})
    g.add_edge("generate", END)
    g.add_edge("empty", END)
    return g.compile()


def run(query: str, company_id: Optional[str], top_k: int, store: str,
        use_llm: bool = True) -> tuple[str, str, list[dict]]:
    out = _graph().invoke({
        "query": query, "company_id": company_id, "top_k": top_k, "store": store, "use_llm": use_llm,
    })
    return out.get("answer", ""), out.get("answer_source", "none"), out.get("results", [])
