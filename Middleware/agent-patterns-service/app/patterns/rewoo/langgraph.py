"""ReWOO on **LangGraph** — planner (blind) → worker (execute all, no LLM in the loop) → solver.

Implements the 5 VKP use cases via ctx['useCase'] (default = fixed-dimension-comparison). The plan,
worker, and solver spec live in `_base.USE_CASES` (shared with every framework cell); the worker runs
the planned vehicle_spec calls with NO LLM (the 'WithOut Observation' part). This cell shows ONLY the
LangGraph planner→worker→solver graph."""
from typing import TypedDict

from ... import llm, registry
from . import _base


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"), q)
    worker_fn = spec["worker"]
    solver_kind, solver_builder = spec["solver"]

    class S(TypedDict, total=False):
        plan: list
        evidence: str
        answer: str

    def planner(_s): return {"plan": spec["plan"]}
    def worker(s): return {"evidence": worker_fn(s["plan"])}   # NO LLM for the tool calls
    def solver(s):
        ev = s["evidence"]
        return {"answer": llm.complete(solver_builder(q, ev)) if solver_kind == "llm" else solver_builder(q, ev)}

    g = StateGraph(S)
    g.add_node("planner", planner); g.add_node("worker", worker); g.add_node("solver", solver)
    g.add_edge(START, "planner"); g.add_edge("planner", "worker"); g.add_edge("worker", "solver"); g.add_edge("solver", END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "steps": [str(c) for c in out["plan"]], "useCase": uc}


registry.register("rewoo", "langgraph", run)
