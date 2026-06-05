"""Stage x framework registry. Each framework module registers the stages it implements
(search | collect | index); the API dispatches `/agentic/{stage}/{framework}/run` here.

A framework is a pluggable agent-SDK integration (openai-agents, google-adk, msagent, strands, ...).
The same framework can implement multiple stages — they register independently.
"""
from typing import Callable

STAGES = ("search", "collect", "index")

# framework id -> { stage -> callable(ctx: dict) -> dict }
_REGISTRY: dict[str, dict[str, Callable]] = {}


def register(framework: str, stage: str, fn: Callable) -> None:
    if stage not in STAGES:
        raise ValueError(f"unknown stage: {stage}")
    _REGISTRY.setdefault(framework, {})[stage] = fn


def frameworks() -> list[str]:
    return sorted(_REGISTRY)


def implemented(stage: str) -> list[str]:
    return sorted(f for f, stages in _REGISTRY.items() if stage in stages)


def matrix() -> dict[str, list[str]]:
    """stage -> [frameworks implementing it] — the coverage matrix for the UI/diagnostics."""
    return {stage: implemented(stage) for stage in STAGES}


def run(stage: str, framework: str, ctx: dict) -> dict:
    fn = _REGISTRY.get(framework, {}).get(stage)
    if fn is None:
        raise KeyError(f"{framework!r} does not implement stage {stage!r}")
    return fn(ctx)
