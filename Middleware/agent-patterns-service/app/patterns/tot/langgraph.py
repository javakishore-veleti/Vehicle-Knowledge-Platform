"""Tree of Thoughts on **LangGraph** — branch (propose N) -> evaluate (score) -> select best."""
import re
from typing import TypedDict

from ... import registry, llm


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]

    class S(TypedDict, total=False):
        thoughts: list
        scores: list
        answer: str

    def branch(_s):
        raw = llm.complete(f"Propose 3 DISTINCT candidate answers/approaches to: {q}\nSeparate each with a line '---'.")
        parts = [p.strip() for p in raw.split("---") if p.strip()][:3] or [raw]
        return {"thoughts": parts}

    def evaluate(s):
        scores = []
        for t in s["thoughts"]:
            r = llm.complete(f"Rate 1-10 how well this answers '{q}'. Reply only the number.\n\n{t}")
            m = re.search(r"\d+", r); scores.append(int(m.group(0)) if m else 5)
        return {"scores": scores}

    def select(s):
        best = max(range(len(s["thoughts"])), key=lambda i: s["scores"][i])
        return {"answer": s["thoughts"][best]}

    g = StateGraph(S)
    g.add_node("branch", branch); g.add_node("evaluate", evaluate); g.add_node("select", select)
    g.add_edge(START, "branch"); g.add_edge("branch", "evaluate"); g.add_edge("evaluate", "select"); g.add_edge("select", END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "steps": [f"thought{i+1}: score {sc}" for i, sc in enumerate(out["scores"])]}


registry.register("tot", "langgraph", run)
