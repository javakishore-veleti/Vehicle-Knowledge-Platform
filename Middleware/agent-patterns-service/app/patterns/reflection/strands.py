"""Reflection on **AWS Strands** — an Agent drives draft -> critique -> revise (synchronous).

Implements the 5 VKP Reflection use cases via ctx['useCase']; the use-case instructions come from
`_base.USE_CASES` (shared with every framework cell). Each step is a Strands Agent run via sa.complete."""
from ... import registry, sa
from . import _base


def run(ctx: dict) -> dict:
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"))
    draft = sa.complete(spec["generate"].format(q=q))
    critique = sa.complete(f"{spec['critique']}\n\nDRAFT:\n{draft}")
    answer = sa.complete(f"{spec['revise']}\n\nDRAFT:\n{draft}\n\nCRITIQUE:\n{critique}")
    return {**_base.result(draft, critique, answer), "useCase": uc}


registry.register("reflection", "strands", run)
