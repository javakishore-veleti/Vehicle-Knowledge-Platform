"""Router on **Google ADK** — a classifier LlmAgent routes to the matching handler.

Implements the 5 VKP router use cases via ctx['useCase']; the classify prompts + route tables come from
`_base.USE_CASES` (shared with every framework cell). LLM routes run a specialist LlmAgent with the
route's system prompt; static routes return the routing string (topic-guardrail blocks unsafe)."""
from ... import registry, adk
from . import _base


def run(ctx: dict) -> dict:
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"))
    route = _base.pick_route(spec, adk.complete(_base.classify_prompt(spec, q), "Reply with one word."))
    h = spec["routes"][route]
    ans = (h[2] + adk.complete(q, h[1])) if h[0] == "llm" else _base.render_static(h, q)
    return {"answer": ans, "steps": [f"routed -> {route}"], "useCase": uc}


registry.register("router", "google_adk", run)
