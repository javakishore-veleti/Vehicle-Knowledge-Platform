"""Parallelization on **LangGraph** — fan out 3 perspectives concurrently (reducer merges), then synthesize."""
import operator
from typing import Annotated, TypedDict

from ... import registry, llm


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]

    class S(TypedDict, total=False):
        parts: Annotated[list, operator.add]
        answer: str

    def pros(_s): return {"parts": [("Pros", llm.complete(f"List the PROS relevant to: {q}"))]}
    def cons(_s): return {"parts": [("Cons", llm.complete(f"List the CONS relevant to: {q}"))]}
    def alts(_s): return {"parts": [("Alternatives", llm.complete(f"Suggest ALTERNATIVES relevant to: {q}"))]}

    def merge(s):
        body = "\n\n".join(f"{k}:\n{v}" for k, v in s["parts"])
        return {"answer": llm.complete(f"Synthesize a balanced answer to '{q}' from these notes:\n\n{body}")}

    g = StateGraph(S)
    for n, f in [("pros", pros), ("cons", cons), ("alts", alts), ("merge", merge)]:
        g.add_node(n, f)
    g.add_edge(START, "pros"); g.add_edge(START, "cons"); g.add_edge(START, "alts")   # fan-out
    g.add_edge("pros", "merge"); g.add_edge("cons", "merge"); g.add_edge("alts", "merge")  # join
    g.add_edge("merge", END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "steps": [k for k, _ in out["parts"]]}


registry.register("chaining", "langgraph", run)
