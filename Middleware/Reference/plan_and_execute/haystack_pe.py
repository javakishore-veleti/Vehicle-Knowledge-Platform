"""Plan-and-Execute on **Haystack 2.x** — a planner built from a PromptBuilder + Generator emits the
sub-queries; the fan-out retrieval + synthesis follow. Reference implementation — needs `haystack-ai` + an LLM.

Haystack Pipelines are static graphs, so the dynamic fan-out (N sub-queries -> N retrievals) is done in
Python around a planning pipeline rather than inside one pipeline. The planner is a real 2-component
Haystack pipeline (PromptBuilder -> OpenAIGenerator).
"""
from typing import Callable

from _common import PLAN_PROMPT, merge, parse_steps


def _planner_pipeline():
    from haystack import Pipeline
    from haystack.components.builders import PromptBuilder
    from haystack.components.generators import OpenAIGenerator

    pipe = Pipeline()
    pipe.add_component("prompt", PromptBuilder(template="{{ q }}"))
    pipe.add_component("llm", OpenAIGenerator())
    pipe.connect("prompt.prompt", "llm.prompt")
    return pipe


def run(query: str, retrieve: Callable[[str], list], synthesize: Callable[[str, list], str]):
    # ---- PLAN: run the planning pipeline ----
    pipe = _planner_pipeline()
    out = pipe.run({"prompt": {"q": PLAN_PROMPT.format(q=query)}})
    raw = (out.get("llm", {}).get("replies") or [""])[0]
    steps = parse_steps(raw, query)

    # ---- EXECUTE + SYNTHESIZE ----
    results = merge([retrieve(sq) for sq in steps], cap=12)
    return synthesize(query, results), steps, results
