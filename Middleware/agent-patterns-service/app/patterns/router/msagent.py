"""Router on the **Microsoft Agent Framework** — a classifier Agent routes to the matching handler.

Implements the 5 VKP router use cases via ctx['useCase']; the classify prompts + route tables come from
`_base.USE_CASES` (shared with every framework cell). LLM routes run a specialist Agent with the route's
system prompt; static routes return the routing string. Each cell runs in ONE event loop (AF telemetry)."""
from ... import registry, msa
from . import _base


def run(ctx: dict) -> dict:
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"))

    async def _go():
        route = _base.pick_route(spec, await msa.acomplete(_base.classify_prompt(spec, q), "Reply with one word."))
        h = spec["routes"][route]
        ans = (h[2] + await msa.acomplete(q, h[1])) if h[0] == "llm" else _base.render_static(h, q)
        return route, ans

    route, ans = msa.run_sync(_go())
    return {"answer": ans, "steps": [f"routed -> {route}"], "useCase": uc}


registry.register("router", "msagent", run)
