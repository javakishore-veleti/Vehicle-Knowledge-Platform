"""Reflection on the **OpenAI Agents SDK** — its Agent + Runner drive draft -> critique -> revise.

Implements the 5 VKP Reflection use cases via ctx['useCase']; the use-case instructions come from
`_base.USE_CASES` (shared with every framework cell). Each step is an Agent run via oa.complete."""
from ... import registry, oa
from . import _base


def run(ctx: dict) -> dict:
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"))
    draft = oa.complete(spec["generate"].format(q=q))
    critique = oa.complete(f"{spec['critique']}\n\nDRAFT:\n{draft}")
    answer = oa.complete(f"{spec['revise']}\n\nDRAFT:\n{draft}\n\nCRITIQUE:\n{critique}")
    return {**_base.result(draft, critique, answer), "useCase": uc}


registry.register("reflection", "openai_agents", run)
