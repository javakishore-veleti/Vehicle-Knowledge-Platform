"""Reflection on **Google ADK** — LlmAgents (via InMemoryRunner) drive draft -> critique -> revise.

Implements the 5 VKP Reflection use cases via ctx['useCase']; the use-case instructions come from
`_base.USE_CASES` (shared with every framework cell). Each step is an LlmAgent run via adk.complete."""
from ... import registry, adk
from . import _base


def run(ctx: dict) -> dict:
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"))
    draft = adk.complete(spec["generate"].format(q=q))
    critique = adk.complete(f"{spec['critique']}\n\nDRAFT:\n{draft}")
    answer = adk.complete(f"{spec['revise']}\n\nDRAFT:\n{draft}\n\nCRITIQUE:\n{critique}")
    return {**_base.result(draft, critique, answer), "useCase": uc}


registry.register("reflection", "google_adk", run)
