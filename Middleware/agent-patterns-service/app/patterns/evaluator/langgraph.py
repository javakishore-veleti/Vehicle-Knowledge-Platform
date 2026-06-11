"""Evaluator-optimizer on **LangGraph** — generate -> evaluate(score) -> (loop if below threshold) -> done."""
import re
from typing import TypedDict

from ... import registry, llm


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]
    max_iter = int(ctx.get("maxIterations") or 2)

    class S(TypedDict, total=False):
        answer: str
        score: int
        feedback: str
        n: int

    def generate(s):
        if s.get("feedback"):
            a = llm.complete(f"Improve the answer to '{q}' using this feedback: {s['feedback']}\n\nPrevious: {s.get('answer','')}")
        else:
            a = llm.complete(q, system="You are a vehicle expert. Answer accurately.")
        return {"answer": a, "n": s.get("n", 0) + 1}

    def evaluate(s):
        r = llm.complete(f"Rate the answer 1-10 for accuracy+completeness and give one-line feedback. "
                         f"Format exactly: SCORE: <n> | FEEDBACK: <text>\n\nQ: {q}\nA: {s['answer']}")
        m = re.search(r"SCORE:\s*(\d+)", r); fb = re.search(r"FEEDBACK:\s*(.*)", r)
        return {"score": int(m.group(1)) if m else 7, "feedback": fb.group(1).strip() if fb else ""}

    def route(s): return "done" if s["score"] >= 8 or s["n"] >= max_iter else "generate"

    g = StateGraph(S)
    g.add_node("generate", generate); g.add_node("evaluate", evaluate)
    g.add_edge(START, "generate"); g.add_edge("generate", "evaluate")
    g.add_conditional_edges("evaluate", route, {"generate": "generate", "done": END})
    out = g.compile().invoke({})
    return {"answer": out["answer"], "critique": out.get("feedback"),
            "steps": [f"iterations={out.get('n')}", f"final_score={out.get('score')}"]}


registry.register("evaluator-optimizer", "langgraph", run)
