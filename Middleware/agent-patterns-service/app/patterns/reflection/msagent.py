"""Reflection on the **Microsoft Agent Framework** — an Agent drives draft -> critique -> revise.

Implements the 5 VKP Reflection use cases via ctx['useCase']; the use-case instructions come from
`_base.USE_CASES` (shared with every framework cell). All calls run in ONE event loop (AF telemetry
ContextVar breaks across repeated asyncio.run)."""
from ... import registry, msa
from . import _base


def run(ctx: dict) -> dict:
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"))

    async def _go():
        draft = await msa.acomplete(spec["generate"].format(q=q))
        critique = await msa.acomplete(f"{spec['critique']}\n\nDRAFT:\n{draft}")
        answer = await msa.acomplete(f"{spec['revise']}\n\nDRAFT:\n{draft}\n\nCRITIQUE:\n{critique}")
        return draft, critique, answer

    draft, critique, answer = msa.run_sync(_go())
    return {**_base.result(draft, critique, answer), "useCase": uc}


registry.register("reflection", "msagent", run)
