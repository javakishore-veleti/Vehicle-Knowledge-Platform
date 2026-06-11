"""ReWOO on **LangGraph** — planner emits ALL tool calls blind -> worker runs them (no LLM) -> solver combines."""
import json
import re
from typing import TypedDict

from ... import registry, llm, tools


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]

    class S(TypedDict, total=False):
        plan: list
        evidence: list
        answer: str

    def planner(_s):
        raw = llm.complete(
            'Plan the vehicle_spec(model, field) tool calls needed to answer the question — WITHOUT any '
            'results yet. Return ONLY a JSON array of {"model":..,"field":..} objects.\n\n' + q)
        m = re.search(r"\[.*\]", raw, re.S)
        try:
            plan = json.loads(m.group(0)) if m else []
        except Exception:
            plan = []
        return {"plan": plan[:6]}

    def worker(s):   # execute ALL planned calls with NO LLM in the loop (WithOut Observation)
        ev = [{"call": c, "result": tools.vehicle_spec(c.get("model", ""), c.get("field", ""))} for c in s["plan"]]
        return {"evidence": ev}

    def solver(s):
        body = "\n".join(f"{e['call']} -> {e['result']}" for e in s["evidence"])
        return {"answer": llm.complete(f"Using ONLY this evidence, answer: {q}\n\nEVIDENCE:\n{body}")}

    g = StateGraph(S)
    g.add_node("planner", planner); g.add_node("worker", worker); g.add_node("solver", solver)
    g.add_edge(START, "planner"); g.add_edge("planner", "worker"); g.add_edge("worker", "solver"); g.add_edge("solver", END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "steps": [str(c) for c in out["plan"]]}


registry.register("rewoo", "langgraph", run)
