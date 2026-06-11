"""Central registry of (pattern, framework) -> run(ctx) cells. Each cell registers itself on import."""
from typing import Callable

_REG: dict[tuple[str, str], Callable[[dict], dict]] = {}


def register(pattern: str, framework: str, fn: Callable[[dict], dict]) -> None:
    _REG[(pattern, framework)] = fn


def implemented(pattern: str, framework: str) -> bool:
    return (pattern, framework) in _REG


def dispatch(pattern: str, framework: str, ctx: dict) -> dict:
    fn = _REG.get((pattern, framework))
    if fn is None:
        raise KeyError(f"{pattern}/{framework} not implemented")
    return fn(ctx)


def matrix() -> dict:
    """Coverage view: which frameworks are implemented for each pattern."""
    by_pattern: dict[str, list[str]] = {}
    frameworks: set[str] = set()
    for (p, f) in _REG:
        by_pattern.setdefault(p, []).append(f)
        frameworks.add(f)
    return {
        "patterns": {p: sorted(fs) for p, fs in sorted(by_pattern.items())},
        "frameworks": sorted(frameworks),
        "count": len(_REG),
    }
