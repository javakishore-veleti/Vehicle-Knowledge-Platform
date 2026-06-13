"""Evaluator-optimizer on **LangGraph** — generate ↔ evaluate loop with a score-gated conditional edge.

Implements the 5 VKP use cases via ctx['useCase'] (default = answer-refiner). The use-case prompts +
eval strategies live in `_base.USE_CASES` (shared by every framework cell); query-rewriter uses REAL
corpus retrieval as the evaluation signal. This cell shows ONLY the LangGraph loop mechanics."""
from typing import TypedDict

from ... import registry
from . import _base


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"))
    max_iter = int(ctx.get("maxIterations") or 3)

    class S(TypedDict, total=False):
        output: str
        score: int
        feedback: str
        n: int

    def generate(s): return {"output": _base.generate(spec, q, s.get("output"), s.get("feedback")), "n": s.get("n", 0) + 1}

    def evaluate(s):
        score, fb = _base.evaluate(spec, q, s["output"])
        return {"score": score, "feedback": fb}

    def route(s): return "done" if s["score"] >= 8 or s["n"] >= max_iter else "generate"

    g = StateGraph(S)
    g.add_node("generate", generate)
    g.add_node("evaluate", evaluate)
    g.add_edge(START, "generate")
    g.add_edge("generate", "evaluate")
    g.add_conditional_edges("evaluate", route, {"generate": "generate", "done": END})
    out = g.compile().invoke({})
    return {"answer": out["output"], "critique": out.get("feedback"), "useCase": uc,
            "steps": [f"iterations={out.get('n')}", f"final_score={out.get('score')}"]}


registry.register("evaluator-optimizer", "langgraph", run)
