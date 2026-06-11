"""Multi-agent on **LangGraph** — a supervisor fans work to spec/pricing/safety workers, then composes."""
import operator
from typing import Annotated, TypedDict

from ... import registry, llm


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]

    class S(TypedDict, total=False):
        notes: Annotated[list, operator.add]
        answer: str

    def worker(role, sysp):
        def _n(_s): return {"notes": [(role, llm.complete(q, system=sysp))]}
        return _n

    def supervisor(s):
        body = "\n\n".join(f"{r}: {t}" for r, t in s["notes"])
        return {"answer": llm.complete(f"You are the lead advisor. Compose a final answer to '{q}' from your specialists:\n\n{body}")}

    g = StateGraph(S)
    g.add_node("spec", worker("spec", "You are a vehicle SPECS specialist. Give only spec facts relevant to the question."))
    g.add_node("pricing", worker("pricing", "You are a vehicle PRICING specialist. Give pricing/value facts."))
    g.add_node("safety", worker("safety", "You are a vehicle SAFETY specialist. Give safety/reliability facts."))
    g.add_node("supervisor", supervisor)
    g.add_edge(START, "spec"); g.add_edge(START, "pricing"); g.add_edge(START, "safety")
    g.add_edge("spec", "supervisor"); g.add_edge("pricing", "supervisor"); g.add_edge("safety", "supervisor")
    g.add_edge("supervisor", END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "steps": [r for r, _ in out["notes"]]}


registry.register("multi-agent", "langgraph", run)
