"""Reflection on **LlamaIndex** — its LLM drives draft -> critique -> revise.

Implements the 5 VKP Reflection use cases via ctx['useCase']; the use-case instructions come from
`_base.USE_CASES` (shared with every framework cell). This cell uses LlamaIndex's LLM for each step."""
from ... import registry, li
from . import _base


def run(ctx: dict) -> dict:
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"))
    draft = li.complete(spec["generate"].format(q=q))
    critique = li.complete(f"{spec['critique']}\n\nDRAFT:\n{draft}")
    answer = li.complete(f"{spec['revise']}\n\nDRAFT:\n{draft}\n\nCRITIQUE:\n{critique}")
    return {**_base.result(draft, critique, answer), "useCase": uc}


registry.register("reflection", "llamaindex", run)
