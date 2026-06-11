"""Plan-and-Execute on **LlamaIndex** — the idiomatic fit is the built-in `SubQuestionQueryEngine`,
which IS plan-and-execute: an LLM generates sub-questions, each runs against a query-engine tool, then
the answers are combined. Reference implementation — needs `llama-index` + an LLM.

Two flavours are shown:
  - native(): wrap the project's retriever as a QueryEngineTool and let SubQuestionQueryEngine do the
    plan -> sub-query -> combine automatically (the "batteries-included" way).
  - run(): a manual plan -> fan-out -> synthesize using the injected callables (so it matches the other
    reference modules' signature exactly).
"""
from typing import Callable

from _common import PLAN_PROMPT, merge, parse_steps


def native(query: str, index, llm=None):
    """Let LlamaIndex's SubQuestionQueryEngine do plan-and-execute over a vector index."""
    from llama_index.core.query_engine import SubQuestionQueryEngine
    from llama_index.core.tools import QueryEngineTool, ToolMetadata

    tool = QueryEngineTool(
        query_engine=index.as_query_engine(llm=llm),
        metadata=ToolMetadata(name="vehicle_content",
                              description="Indexed vehicle content (specs, models, pricing, features)."),
    )
    engine = SubQuestionQueryEngine.from_defaults(query_engine_tools=[tool], llm=llm, verbose=True)
    resp = engine.query(query)
    return str(resp)


def run(query: str, llm_complete: Callable[[str], str], retrieve: Callable[[str], list],
        synthesize: Callable[[str, list], str]):
    """Manual variant matching the shared (llm_complete, retrieve, synthesize) signature."""
    steps = parse_steps(llm_complete(PLAN_PROMPT.format(q=query)), query)
    results = merge([retrieve(sq) for sq in steps], cap=12)
    return synthesize(query, results), steps, results
