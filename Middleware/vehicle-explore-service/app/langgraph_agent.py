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
    provider_ids: Optional[list]
    results: list
    answer: str
    answer_source: str
    answers: list


def _retrieve_node(state: AgentState) -> dict:
    results = frameworks._retrieve(state["query"], state.get("company_id"), state["top_k"], state["store"])
    return {"results": results}


def _generate_node(state: AgentState) -> dict:
    answer, source, answers = frameworks.synthesize(
        state["query"], state["results"], state.get("use_llm", True), state.get("provider_ids"))
    return {"answer": answer, "answer_source": source, "answers": answers}


def _empty_node(state: AgentState) -> dict:
    return {"answer": "No relevant vehicle content was found for this query.", "answer_source": "none", "answers": []}


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
        use_llm: bool = True, provider_ids: Optional[list[str]] = None) -> tuple[str, str, list[dict], list[dict]]:
    out = _graph().invoke({
        "query": query, "company_id": company_id, "top_k": top_k, "store": store,
        "use_llm": use_llm, "provider_ids": provider_ids,
    })
    return out.get("answer", ""), out.get("answer_source", "none"), out.get("results", []), out.get("answers", [])


# ===== collect + index stages (classic-roster, registered with agentic_stages) =====
import os  # noqa: E402

from . import agentic_stages, tools as _tools  # noqa: E402
from .agentic_stages import COLLECT_INSTRUCTIONS, INDEX_INSTRUCTIONS  # noqa: E402

LG_MODEL = os.getenv("VKP_LANGGRAPH_MODEL", "llama-3.3-70b-versatile")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def _llm():
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model=LG_MODEL, api_key=os.getenv("GROQ_API_KEY", ""),
                      base_url=GROQ_BASE_URL, temperature=0.2)


def _collect(seed: str) -> str:
    from langchain_core.tools import tool as lc_tool
    from langgraph.prebuilt import create_react_agent

    @lc_tool
    def fetch_page(url: str) -> dict:
        """Fetch a web page; returns {url, title, links:[{url,type}], images:[...]}."""
        return _tools.fetch_page(url)

    agent = create_react_agent(_llm(), [fetch_page])
    out = agent.invoke({"messages": [
        ("system", COLLECT_INSTRUCTIONS),
        ("user", f"Seed URL: {seed}\nDiscover and return the relevant vehicle resource links as JSON.")]})
    return out["messages"][-1].content


def _chunk(content: str) -> str:
    msg = _llm().invoke([
        ("system", INDEX_INSTRUCTIONS),
        ("user", f"CONTENT:\n{content}\n\nReturn the chunks as a JSON array of strings.")])
    return msg.content


def collect(ctx: dict) -> dict:
    return agentic_stages.collect_flow("langgraph", "LangGraph", LG_MODEL, _collect, ctx)


def index(ctx: dict) -> dict:
    return agentic_stages.index_flow("langgraph", "LangGraph", LG_MODEL, _chunk, ctx)


agentic_stages.register_collect("langgraph", collect)
agentic_stages.register_index("langgraph", index)
