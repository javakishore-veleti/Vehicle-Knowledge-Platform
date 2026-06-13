"""Shared branch prompts + eval criteria + parse helpers for the Tree-of-Thoughts pattern.

Each use case = (branch_prompt, eval_criterion): what 3 distinct thoughts to propose, and the
criterion to score them against. Framework-agnostic, so every cell shares it and differs only in
how it runs the branch/evaluate/select steps."""
import re

USE_CASES = {
    "best-car-for-me": lambda q: (
        f"Propose 3 DISTINCT car recommendations for this need, each under a DIFFERENT priority "
        f"(budget-first, space-first, efficiency-first). Separate each with a line '---'.\n\nNEED: {q}",
        f"how well it fits the need: {q}"),
    "ambiguous-query": lambda q: (
        f"List 3 DISTINCT interpretations of this ambiguous vehicle query, each naming the vehicle(s) it "
        f"would mean. Separate each with '---'.\n\nQUERY: {q}",
        f"how likely this interpretation matches the user's intent for: {q}"),
    "trim-optimizer": lambda q: (
        f"Propose 3 DISTINCT trim / option configurations addressing this goal. Separate with '---'.\n\nGOAL: {q}",
        f"how well it meets the budget / feature goal: {q}"),
    "multi-constraint-filter": lambda q: (
        f"Propose 3 DISTINCT candidate vehicles that could satisfy these constraints. Separate with '---'.\n\nCONSTRAINTS: {q}",
        f"how fully it satisfies the constraints: {q}"),
    "spec-conflict-resolver": lambda q: (
        f"Propose 3 DISTINCT hypotheses that could explain this spec conflict (e.g. year / trim / market "
        f"differences). Separate with '---'.\n\nCONFLICT: {q}",
        f"how plausibly it resolves the conflict: {q}"),
}

DEFAULT_UC = "best-car-for-me"


def spec_for(use_case: str | None, q: str) -> tuple:
    uc = use_case if use_case in USE_CASES else DEFAULT_UC
    branch_p, eval_crit = USE_CASES[uc](q)
    return uc, branch_p, eval_crit


def parse_thoughts(raw: str) -> list:
    return [p.strip() for p in (raw or "").split("---") if p.strip()][:3] or [raw]


def eval_prompt(eval_crit: str, thought: str) -> str:
    return f"Rate 1-10 {eval_crit}. Reply with only the number.\n\nCANDIDATE:\n{thought}"


def score_of(r: str) -> int:
    m = re.search(r"\d+", r or "")
    return int(m.group(0)) if m else 5
