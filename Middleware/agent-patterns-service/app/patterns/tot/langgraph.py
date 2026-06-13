"""Tree of Thoughts on **LangGraph** — branch (propose 3) → evaluate (score) → select best.

Implements the 5 VKP use cases via ctx['useCase'] (default = best-car-for-me). The branch prompts +
eval criteria live in `_base.USE_CASES` (shared with every framework cell); this cell shows ONLY the
LangGraph branch/evaluate/select graph."""
from typing import TypedDict

from ... import llm, registry
from . import _base


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]
    uc, branch_p, eval_crit = _base.spec_for(ctx.get("useCase"), q)

    class S(TypedDict, total=False):
        thoughts: list
        scores: list
        answer: str

    def branch(_s):
        return {"thoughts": _base.parse_thoughts(llm.complete(branch_p))}

    def evaluate(s):
        return {"scores": [_base.score_of(llm.complete(_base.eval_prompt(eval_crit, t))) for t in s["thoughts"]]}

    def select(s):
        best = max(range(len(s["thoughts"])), key=lambda i: s["scores"][i])
        return {"answer": s["thoughts"][best]}

    g = StateGraph(S)
    g.add_node("branch", branch); g.add_node("evaluate", evaluate); g.add_node("select", select)
    g.add_edge(START, "branch"); g.add_edge("branch", "evaluate"); g.add_edge("evaluate", "select"); g.add_edge("select", END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "useCase": uc,
            "steps": [f"thought{i+1}: score {sc}" for i, sc in enumerate(out["scores"])]}


registry.register("tot", "langgraph", run)
