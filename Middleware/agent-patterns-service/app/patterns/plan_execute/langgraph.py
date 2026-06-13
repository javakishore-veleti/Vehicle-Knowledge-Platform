"""Plan-and-Execute on **LangGraph** — plan → execute → synthesize StateGraph.

Implements the 5 VKP use cases via ctx['useCase'] (default = multi-brand-comparison). The plan/execute/
synthesize specs live in `_base.USE_CASES` (shared with every framework cell); execute gathers evidence
via corpus retrieval or the vehicle_spec tool. This cell shows ONLY the LangGraph plan→execute→synth graph."""
from typing import TypedDict

from ... import llm, registry
from . import _base


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"), q)

    class S(TypedDict, total=False):
        steps: list
        evidence: str
        answer: str

    def plan(_s): return {"steps": _base.steps_for(spec, q)}
    def execute(s): return {"evidence": spec["exec"](q, s["steps"])}
    def synth(s): return {"answer": llm.complete(_base.synth_prompt(spec["instr"], q, s["evidence"]))}

    g = StateGraph(S)
    g.add_node("plan", plan); g.add_node("execute", execute); g.add_node("synthesize", synth)
    g.add_edge(START, "plan"); g.add_edge("plan", "execute"); g.add_edge("execute", "synthesize"); g.add_edge("synthesize", END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "steps": out["steps"], "useCase": uc}


registry.register("plan-execute", "langgraph", run)
