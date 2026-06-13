"""Tree of Thoughts on **LangGraph** — branch (propose 3) → evaluate (score) → select best.

Implements the 5 VKP use cases via ctx['useCase'] (default = best-car-for-me). Each defines the branch
prompt (what thoughts to propose) and the evaluation criterion to score them against."""
import re
from typing import TypedDict

from ... import llm, registry


def _best_car(q):
    return (f"Propose 3 DISTINCT car recommendations for this need, each under a DIFFERENT priority "
            f"(budget-first, space-first, efficiency-first). Separate each with a line '---'.\n\nNEED: {q}",
            f"how well it fits the need: {q}")


def _ambiguous(q):
    return (f"List 3 DISTINCT interpretations of this ambiguous vehicle query, each naming the vehicle(s) it "
            f"would mean. Separate each with '---'.\n\nQUERY: {q}",
            f"how likely this interpretation matches the user's intent for: {q}")


def _trim(q):
    return (f"Propose 3 DISTINCT trim / option configurations addressing this goal. Separate with '---'.\n\nGOAL: {q}",
            f"how well it meets the budget / feature goal: {q}")


def _multi_constraint(q):
    return (f"Propose 3 DISTINCT candidate vehicles that could satisfy these constraints. Separate with '---'.\n\nCONSTRAINTS: {q}",
            f"how fully it satisfies the constraints: {q}")


def _spec_conflict(q):
    return (f"Propose 3 DISTINCT hypotheses that could explain this spec conflict (e.g. year / trim / market "
            f"differences). Separate with '---'.\n\nCONFLICT: {q}",
            f"how plausibly it resolves the conflict: {q}")


_USE_CASES = {"best-car-for-me": _best_car, "ambiguous-query": _ambiguous, "trim-optimizer": _trim,
              "multi-constraint-filter": _multi_constraint, "spec-conflict-resolver": _spec_conflict}


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]
    uc = ctx.get("useCase") or "best-car-for-me"
    branch_p, eval_crit = _USE_CASES.get(uc, _best_car)(q)

    class S(TypedDict, total=False):
        thoughts: list
        scores: list
        answer: str

    def branch(_s):
        raw = llm.complete(branch_p)
        parts = [p.strip() for p in raw.split("---") if p.strip()][:3] or [raw]
        return {"thoughts": parts}

    def evaluate(s):
        scores = []
        for t in s["thoughts"]:
            r = llm.complete(f"Rate 1-10 {eval_crit}. Reply with only the number.\n\nCANDIDATE:\n{t}")
            m = re.search(r"\d+", r)
            scores.append(int(m.group(0)) if m else 5)
        return {"scores": scores}

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
