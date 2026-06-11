"""Plan-and-Execute on **LangGraph** — a compiled StateGraph: plan -> execute -> synthesize.

This is the most natural fit: each phase is a graph node, state flows between them, and you can later
add a `replan` conditional edge. Reference implementation — needs `langgraph` + an LLM.

    from langgraph_pe import run
    answer, steps, results = run(query, llm_complete, retrieve, synthesize)
"""
from typing import Callable, TypedDict

from _common import PLAN_PROMPT, merge, parse_steps


def build(llm_complete: Callable[[str], str], retrieve: Callable[[str], list], synthesize: Callable[[str, list], str]):
    from langgraph.graph import StateGraph, START, END

    class State(TypedDict, total=False):
        query: str
        steps: list
        results: list
        answer: str

    def plan(state: State) -> dict:
        steps = parse_steps(llm_complete(PLAN_PROMPT.format(q=state["query"])), state["query"])
        return {"steps": steps}

    def execute(state: State) -> dict:
        per_step = [retrieve(sq) for sq in state["steps"]]
        return {"results": merge(per_step, cap=12)}

    def synth(state: State) -> dict:
        return {"answer": synthesize(state["query"], state["results"])}

    g = StateGraph(State)
    g.add_node("plan", plan)
    g.add_node("execute", execute)
    g.add_node("synthesize", synth)
    g.add_edge(START, "plan")
    g.add_edge("plan", "execute")
    g.add_edge("execute", "synthesize")
    g.add_edge("synthesize", END)
    return g.compile()


def run(query: str, llm_complete, retrieve, synthesize):
    out = build(llm_complete, retrieve, synthesize).invoke({"query": query})
    return out.get("answer", ""), out.get("steps", []), out.get("results", [])
