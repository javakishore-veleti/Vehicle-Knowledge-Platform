"""ReWOO on **LangGraph** — planner (blind) → worker (execute all, no LLM in the loop) → solver.

Implements the 5 VKP use cases via ctx['useCase'] (default = fixed-dimension-comparison). The worker runs
the planned vehicle_spec calls with NO LLM (the 'WithOut Observation' part); only the solver uses an LLM
(nightly-price-refresh is fully LLM-free)."""
import re
from typing import TypedDict

from ... import llm, registry, tools

_TRACKED = ["rav4 prime", "camry", "f-150", "tacoma", "model 3", "civic"]


def _models_in(q: str) -> list:
    ql = (q or "").lower().replace("-", " ")
    return [m for m in _TRACKED if m.replace("-", " ") in ql] or _TRACKED


def _spec_worker(plan: list) -> str:
    return "\n".join(f"{c} -> {tools.vehicle_spec(c.get('model', ''), c.get('field', ''))}" for c in plan)


def _batch_spec(q):
    plan = [{"model": m} for m in _models_in(q)]
    return (lambda: plan, _spec_worker,
            lambda q, ev: llm.complete(f"Summarize this enriched spec data per model:\n\n{ev}"))


def _multi_brand_facts(q):
    facts = ["base_price_usd", "mpg", "electric_range_mi"]
    plan = [{"model": m, "field": f} for m in _models_in(q) for f in facts]
    return (lambda: plan, _spec_worker,
            lambda q, ev: llm.complete(f"Combine these facts into a clear grid by model:\n\n{ev}"))


def _nightly_price(q):
    plan = [{"model": m, "field": "base_price_usd"} for m in _TRACKED]
    return (lambda: plan, _spec_worker,
            lambda q, ev: "Nightly price refresh (LLM-free):\n" + ev)


def _bulk_alt(q):
    imgs = [s.strip() for s in re.split(r"[,\n]", q) if s.strip() and len(s.strip()) > 3] \
        or ["front 3/4 of a red SUV", "interior dashboard", "rear cargo area"]
    plan = [{"image": i} for i in imgs]

    def worker(plan):
        items = "\n".join(f"- {c['image']}" for c in plan)
        return llm.complete(f"Write a concise alt-text caption for EACH image (one per line):\n{items}")

    return (lambda: plan, worker, lambda q, ev: "Alt-text (batch):\n" + ev)


def _fixed_dim(q):
    dims = ["towing_lb", "mpg", "base_price_usd", "seats"]
    plan = [{"model": m, "field": d} for m in _models_in(q) for d in dims]
    return (lambda: plan, _spec_worker,
            lambda q, ev: llm.complete(f"Synthesize a fixed-dimension comparison from this evidence:\n\n{ev}"))


_USE_CASES = {"batch-spec-enrichment": _batch_spec, "parallel-multi-brand-facts": _multi_brand_facts,
              "nightly-price-refresh": _nightly_price, "bulk-image-alt-text": _bulk_alt,
              "fixed-dimension-comparison": _fixed_dim}


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]
    uc = ctx.get("useCase") or "fixed-dimension-comparison"
    plan_fn, worker_fn, solver_fn = _USE_CASES.get(uc, _fixed_dim)(q)

    class S(TypedDict, total=False):
        plan: list
        evidence: str
        answer: str

    def planner(_s): return {"plan": plan_fn()}
    def worker(s): return {"evidence": worker_fn(s["plan"])}   # NO LLM for spec calls
    def solver(s): return {"answer": solver_fn(q, s["evidence"])}

    g = StateGraph(S)
    g.add_node("planner", planner); g.add_node("worker", worker); g.add_node("solver", solver)
    g.add_edge(START, "planner"); g.add_edge("planner", "worker"); g.add_edge("worker", "solver"); g.add_edge("solver", END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "steps": [str(c) for c in out["plan"]], "useCase": uc}


registry.register("rewoo", "langgraph", run)
