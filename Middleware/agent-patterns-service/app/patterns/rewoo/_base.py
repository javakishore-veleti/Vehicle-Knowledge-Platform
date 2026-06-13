"""Shared plan/worker/solver specs for the ReWOO pattern (reused by every framework cell).

The ReWOO point: the PLAN is produced blind (here: deterministically from the models in the query),
the WORKER executes all tool calls with NO LLM in the loop, and only the SOLVER may use an LLM.
Each use case returns {plan, worker, solver} where solver is ("llm", prompt_builder) or
("raw", text_builder) — so a framework can run the solver via an agent or skip it entirely
(nightly-price-refresh is fully LLM-free)."""
import re

from ... import llm, tools

_TRACKED = ["rav4 prime", "camry", "f-150", "tacoma", "model 3", "civic"]


def models_in(q: str) -> list:
    ql = (q or "").lower().replace("-", " ")
    return [m for m in _TRACKED if m.replace("-", " ") in ql] or _TRACKED


def spec_worker(plan: list) -> str:
    """Execute the planned vehicle_spec calls — NO LLM (the 'WithOut Observation' worker)."""
    return "\n".join(f"{c} -> {tools.vehicle_spec(c.get('model', ''), c.get('field', ''))}" for c in plan)


def _bulk_worker(plan: list) -> str:
    items = "\n".join(f"- {c['image']}" for c in plan)
    return llm.complete(f"Write a concise alt-text caption for EACH image (one per line):\n{items}")


def _batch_spec(q):
    return {"plan": [{"model": m} for m in models_in(q)], "worker": spec_worker,
            "solver": ("llm", lambda q, ev: f"Summarize this enriched spec data per model:\n\n{ev}")}


def _multi_brand_facts(q):
    facts = ["base_price_usd", "mpg", "electric_range_mi"]
    return {"plan": [{"model": m, "field": f} for m in models_in(q) for f in facts], "worker": spec_worker,
            "solver": ("llm", lambda q, ev: f"Combine these facts into a clear grid by model:\n\n{ev}")}


def _nightly_price(q):
    return {"plan": [{"model": m, "field": "base_price_usd"} for m in _TRACKED], "worker": spec_worker,
            "solver": ("raw", lambda q, ev: "Nightly price refresh (LLM-free):\n" + ev)}


def _bulk_alt(q):
    imgs = [s.strip() for s in re.split(r"[,\n]", q) if s.strip() and len(s.strip()) > 3] \
        or ["front 3/4 of a red SUV", "interior dashboard", "rear cargo area"]
    return {"plan": [{"image": i} for i in imgs], "worker": _bulk_worker,
            "solver": ("raw", lambda q, ev: "Alt-text (batch):\n" + ev)}


def _fixed_dim(q):
    dims = ["towing_lb", "mpg", "base_price_usd", "seats"]
    return {"plan": [{"model": m, "field": d} for m in models_in(q) for d in dims], "worker": spec_worker,
            "solver": ("llm", lambda q, ev: f"Synthesize a fixed-dimension comparison from this evidence:\n\n{ev}")}


USE_CASES = {"batch-spec-enrichment": _batch_spec, "parallel-multi-brand-facts": _multi_brand_facts,
             "nightly-price-refresh": _nightly_price, "bulk-image-alt-text": _bulk_alt,
             "fixed-dimension-comparison": _fixed_dim}

DEFAULT_UC = "fixed-dimension-comparison"


def spec_for(use_case: str | None, q: str) -> tuple:
    uc = use_case if use_case in USE_CASES else DEFAULT_UC
    return uc, USE_CASES[uc](q)
