"""Plan-and-Execute on **LlamaIndex** — native SubQuestionQueryEngine for the LLM-planned use case,
shared `_base` plan/execute for the tool/fixed-plan ones.

Implements the 5 VKP use cases via ctx['useCase']. multi-brand-comparison uses the NATIVE
SubQuestionQueryEngine (decompose → sub-query over the VectorStoreIndex → combine) — LlamaIndex's own
plan-execute construct. The others (buyers-guide / onboarding / spec-sheet / tco) run the use case's
deterministic execute from `_base` (corpus retrieval / vehicle_spec tool) + an li.complete synthesis."""
from ... import registry, li
from . import _base


def _native_subquestion(q: str, instr: str) -> str:
    from llama_index.core.query_engine import SubQuestionQueryEngine
    from llama_index.core.tools import QueryEngineTool, ToolMetadata
    tool = QueryEngineTool(query_engine=li.index().as_query_engine(llm=li.llm()),
                           metadata=ToolMetadata(name="vehicles", description="Indexed vehicle content (specs, models, pricing)."))
    eng = SubQuestionQueryEngine.from_defaults(query_engine_tools=[tool], llm=li.llm(), verbose=False)
    return str(eng.query(f"{instr}\n\n{q}"))


def run(ctx: dict) -> dict:
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"), q)

    if spec["plan"][0] == "llm":      # multi-brand-comparison → native SubQuestionQueryEngine
        return {"answer": _native_subquestion(q, spec["instr"]),
                "steps": ["native SubQuestionQueryEngine decomposition"], "useCase": uc}

    steps = list(spec["plan"][1])      # fixed-plan use cases → shared _base execute + li synth
    evidence = spec["exec"](q, steps)
    return {"answer": li.complete(_base.synth_prompt(spec["instr"], q, evidence)), "steps": steps, "useCase": uc}


registry.register("plan-execute", "llamaindex", run)
