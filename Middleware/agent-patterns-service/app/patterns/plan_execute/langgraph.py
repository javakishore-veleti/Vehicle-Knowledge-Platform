"""Plan-and-Execute on **LangGraph** — plan → execute → synthesize StateGraph.

Implements the 5 VKP use cases via ctx['useCase'] (default = multi-brand-comparison). Each provides a
plan_fn (the steps) and an exec_fn (gather evidence per step) — corpus retrieval or the vehicle_spec tool."""
import json
import re
from typing import TypedDict

from ... import llm, registry, corpus, tools

_MODELS = ["rav4 prime", "camry", "f-150", "tacoma", "model 3", "civic"]


def _models_in(q: str) -> list:
    ql = (q or "").lower().replace("-", " ")
    found = [m for m in _MODELS if m.replace("-", " ") in ql]
    return found or ["rav4 prime", "model 3"]


def _llm_steps(q: str, n: int = 4) -> list:
    raw = llm.complete(f"Break this into {n} focused sub-queries. Return ONLY a JSON array of strings.\n\n{q}")
    m = re.search(r"\[.*\]", raw, re.S)
    try:
        s = json.loads(m.group(0)) if m else [q]
    except Exception:
        s = [q]
    return [str(x) for x in s][:n] or [q]


def _multi_brand(q):
    return (lambda: _llm_steps(q),
            lambda st: "\n".join(f"- {sq}: " + "; ".join(d["text"] for d in corpus.retrieve(sq, 2)) for sq in st),
            "Compare and synthesize a clear answer with a verdict.")


def _buyers_guide(q):
    steps = ["Identify 2-3 candidate models", "Key specs", "Price", "Safety", "Rank them"]
    return (lambda: steps,
            lambda st: "\n".join(f"- {s}: " + "; ".join(d["text"] for d in corpus.retrieve(q + " " + s, 2)) for s in st),
            "Produce a short ranked buyer's guide (1-3) with a one-line reason each.")


def _onboarding(q):
    steps = ["discover links (sitemap + page crawl)", "ingest content (fetch + clean text + hash)", "index vectors (chunk + embed → vkp_vectors)"]
    return (lambda: steps,
            lambda st: "\n".join(f"- {s}: simulated OK" for s in st) + "\n- re-plan: JS-heavy site → switch discover to a Playwright crawl",
            "Summarize the company-onboarding pipeline plan and the re-planning decision.")


def _spec_sheet(q):
    dims = [("type", "type"), ("range_mi", "electric_range_mi"), ("mpg", "mpg"),
            ("towing_lb", "towing_lb"), ("price_usd", "base_price_usd"), ("seats", "seats")]
    models = _models_in(q)
    return (lambda: [f"{lbl} per model" for lbl, _ in dims],
            lambda st: "\n".join(f"- {m}: " + ", ".join(f"{lbl}={tools.vehicle_spec(m, f).get(f, '-')}" for lbl, f in dims) for m in models),
            "Assemble a clean side-by-side spec sheet/table from the evidence.")


def _tco(q):
    models = _models_in(q)
    return (lambda: ["purchase price", "fuel/energy", "maintenance (5yr)", "insurance (5yr)", "resale value"],
            lambda st: "\n".join(f"- {m}: base price ${tools.vehicle_spec(m, 'base_price_usd').get('base_price_usd', '?')}; "
                                 f"estimate 5-year fuel / maintenance / insurance / resale" for m in models),
            "Give an approximate 5-year total-cost-of-ownership comparison (rough estimates are fine).")


_USE_CASES = {"multi-brand-comparison": _multi_brand, "buyers-guide-builder": _buyers_guide,
              "adaptive-onboarding": _onboarding, "spec-sheet-assembly": _spec_sheet, "tco-report": _tco}


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]
    uc = ctx.get("useCase") or "multi-brand-comparison"
    plan_fn, exec_fn, instr = _USE_CASES.get(uc, _multi_brand)(q)

    class S(TypedDict, total=False):
        steps: list
        evidence: str
        answer: str

    def plan(_s): return {"steps": plan_fn()}
    def execute(s): return {"evidence": exec_fn(s["steps"])}
    def synth(s): return {"answer": llm.complete(f"{instr}\n\nTASK: {q}\n\nEVIDENCE:\n{s['evidence']}")}

    g = StateGraph(S)
    g.add_node("plan", plan); g.add_node("execute", execute); g.add_node("synthesize", synth)
    g.add_edge(START, "plan"); g.add_edge("plan", "execute"); g.add_edge("execute", "synthesize"); g.add_edge("synthesize", END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "steps": out["steps"], "useCase": uc}


registry.register("plan-execute", "langgraph", run)
