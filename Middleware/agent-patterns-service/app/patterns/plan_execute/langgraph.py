"""Plan-and-Execute on **LangGraph** — plan -> execute (retrieve per sub-query) -> synthesize."""
import json
import re
from typing import TypedDict

from ... import registry, llm, corpus


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]

    class S(TypedDict, total=False):
        steps: list
        docs: list
        answer: str

    def plan(_s):
        raw = llm.complete(f"Break this into 2-4 focused sub-queries. Return ONLY a JSON array of strings.\n\n{q}")
        m = re.search(r"\[.*\]", raw, re.S)
        try:
            steps = json.loads(m.group(0)) if m else [q]
        except Exception:
            steps = [q]
        return {"steps": [str(s) for s in steps][:4] or [q]}

    def execute(s):
        seen = {}
        for sq in s["steps"]:
            for d in corpus.retrieve(sq, 2):
                seen.setdefault(d["source"], d)
        return {"docs": list(seen.values())}

    def synthesize(s):
        notes = "\n".join(f"- {d['text']} ({d['source']})" for d in s["docs"])
        return {"answer": llm.complete(f"Using these notes, answer: {q}\n\nNOTES:\n{notes}")}

    g = StateGraph(S)
    g.add_node("plan", plan); g.add_node("execute", execute); g.add_node("synthesize", synthesize)
    g.add_edge(START, "plan"); g.add_edge("plan", "execute"); g.add_edge("execute", "synthesize"); g.add_edge("synthesize", END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "steps": out["steps"]}


registry.register("plan-execute", "langgraph", run)
