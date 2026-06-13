"""Multi-agent on **LangGraph** — supervisor → parallel specialist workers (reducer-merged) → compose.

Implements the 5 VKP use cases via ctx['useCase'] (default = spec-price-safety). The worker rosters +
merge instructions live in `_base.USE_CASES` (shared with every framework cell); per-brand-workers spins
one worker per brand in the query. This cell shows ONLY the LangGraph fan-out→reducer→merge graph."""
import operator
import re
from typing import Annotated, TypedDict

from ... import llm, registry
from . import _base


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]
    uc, workers, merge_instr = _base.spec_for(ctx.get("useCase"), q)

    class S(TypedDict, total=False):
        notes: Annotated[list, operator.add]
        answer: str

    def mk(label, prompt):
        return lambda _s: {"notes": [(label, llm.complete(prompt))]}

    def merge(s):
        body = "\n\n".join(f"{l}: {t}" for l, t in s["notes"])
        return {"answer": llm.complete(_base.merge_prompt(merge_instr, q, body))}

    g = StateGraph(S)
    names = []
    for label, prompt in workers:
        nm = "w_" + re.sub(r"\W+", "_", label.lower())
        g.add_node(nm, mk(label, prompt)); names.append(nm)
    g.add_node("merge", merge)
    for nm in names:
        g.add_edge(START, nm); g.add_edge(nm, "merge")
    g.add_edge("merge", END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "steps": [l for l, _ in out["notes"]], "useCase": uc}


registry.register("multi-agent", "langgraph", run)
