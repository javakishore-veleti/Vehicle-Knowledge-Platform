"""Reflection on **Haystack** — an OpenAIGenerator drives draft -> critique -> revise.

Implements the 5 VKP Reflection use cases via ctx['useCase']; the use-case instructions come from
`_base.USE_CASES` (shared with every framework cell). This cell uses Haystack's generator for each step."""
from ... import registry, hay
from . import _base


def run(ctx: dict) -> dict:
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"))
    draft = hay.complete(spec["generate"].format(q=q))
    critique = hay.complete(f"{spec['critique']}\n\nDRAFT:\n{draft}")
    answer = hay.complete(f"{spec['revise']}\n\nDRAFT:\n{draft}\n\nCRITIQUE:\n{critique}")
    return {**_base.result(draft, critique, answer), "useCase": uc}


registry.register("reflection", "haystack", run)
