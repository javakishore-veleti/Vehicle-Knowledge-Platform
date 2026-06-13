"""Shared plan / execute / synthesize specs for the Plan-and-Execute pattern (every framework cell).

Each use case returns {plan, exec, instr}:
  - plan: ("llm", n) → decompose into n sub-queries via an LLM/agent, or ("fixed", [steps])
  - exec: (q, steps) → an evidence string, gathered DETERMINISTICALLY (corpus retrieval / vehicle_spec
          tool / simulated pipeline) — no LLM in the execute step
  - instr: the synthesis instruction for the final answer
Framework-agnostic, so every cell shares it and differs only in how it runs plan/execute/synthesize."""
import json
import re

from ... import llm, corpus, tools

_MODELS = ["rav4 prime", "camry", "f-150", "tacoma", "model 3", "civic"]
_DIMS = [("type", "type"), ("range_mi", "electric_range_mi"), ("mpg", "mpg"),
         ("towing_lb", "towing_lb"), ("price_usd", "base_price_usd"), ("seats", "seats")]


def models_in(q: str) -> list:
    ql = (q or "").lower().replace("-", " ")
    found = [m for m in _MODELS if m.replace("-", " ") in ql]
    return found or ["rav4 prime", "model 3"]


def parse_steps(raw: str, q: str, n: int = 4) -> list:
    m = re.search(r"\[.*\]", raw, re.S)
    try:
        s = json.loads(m.group(0)) if m else [q]
    except Exception:
        s = [q]
    return [str(x) for x in s][:n] or [q]


def llm_steps(q: str, n: int = 4) -> list:
    return parse_steps(llm.complete(f"Break this into {n} focused sub-queries. Return ONLY a JSON array of strings.\n\n{q}"), q, n)


def _exec_retrieve(q, steps):
    return "\n".join(f"- {sq}: " + "; ".join(d["text"] for d in corpus.retrieve(sq, 2)) for sq in steps)


def _exec_buyers(q, steps):
    return "\n".join(f"- {s}: " + "; ".join(d["text"] for d in corpus.retrieve(q + " " + s, 2)) for s in steps)


def _exec_onboarding(q, steps):
    return ("\n".join(f"- {s}: simulated OK" for s in steps)
            + "\n- re-plan: JS-heavy site → switch discover to a Playwright crawl")


def _exec_spec_sheet(q, steps):
    return "\n".join(f"- {m}: " + ", ".join(f"{lbl}={tools.vehicle_spec(m, f).get(f, '-')}" for lbl, f in _DIMS)
                     for m in models_in(q))


def _exec_tco(q, steps):
    return "\n".join(f"- {m}: base price ${tools.vehicle_spec(m, 'base_price_usd').get('base_price_usd', '?')}; "
                     f"estimate 5-year fuel / maintenance / insurance / resale" for m in models_in(q))


USE_CASES = {
    "multi-brand-comparison": {"plan": ("llm", 4), "exec": _exec_retrieve,
                               "instr": "Compare and synthesize a clear answer with a verdict."},
    "buyers-guide-builder": {"plan": ("fixed", ["Identify 2-3 candidate models", "Key specs", "Price", "Safety", "Rank them"]),
                             "exec": _exec_buyers, "instr": "Produce a short ranked buyer's guide (1-3) with a one-line reason each."},
    "adaptive-onboarding": {"plan": ("fixed", ["discover links (sitemap + page crawl)", "ingest content (fetch + clean text + hash)",
                                               "index vectors (chunk + embed → vkp_vectors)"]),
                            "exec": _exec_onboarding, "instr": "Summarize the company-onboarding pipeline plan and the re-planning decision."},
    "spec-sheet-assembly": {"plan": ("fixed", [f"{lbl} per model" for lbl, _ in _DIMS]),
                            "exec": _exec_spec_sheet, "instr": "Assemble a clean side-by-side spec sheet/table from the evidence."},
    "tco-report": {"plan": ("fixed", ["purchase price", "fuel/energy", "maintenance (5yr)", "insurance (5yr)", "resale value"]),
                   "exec": _exec_tco, "instr": "Give an approximate 5-year total-cost-of-ownership comparison (rough estimates are fine)."},
}

DEFAULT_UC = "multi-brand-comparison"


def spec_for(use_case: str | None, q: str) -> tuple:
    uc = use_case if use_case in USE_CASES else DEFAULT_UC
    return uc, USE_CASES[uc]


def steps_for(spec: dict, q: str) -> list:
    """Deterministic/LLM plan (used by non-agentic cells like LangGraph)."""
    kind = spec["plan"][0]
    return llm_steps(q, spec["plan"][1]) if kind == "llm" else list(spec["plan"][1])


def synth_prompt(instr: str, q: str, evidence: str) -> str:
    return f"{instr}\n\nTASK: {q}\n\nEVIDENCE:\n{evidence}"
