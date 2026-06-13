"""Plan-and-Execute on **LlamaIndex** — the native SubQuestionQueryEngine (plan → sub-query → combine)."""
from ... import registry, li


def run(ctx: dict) -> dict:
    from llama_index.core.query_engine import SubQuestionQueryEngine
    from llama_index.core.tools import QueryEngineTool, ToolMetadata
    idx = li.index()
    tool = QueryEngineTool(query_engine=idx.as_query_engine(llm=li.llm()),
                           metadata=ToolMetadata(name="vehicles", description="Indexed vehicle content (specs, models, pricing)."))
    eng = SubQuestionQueryEngine.from_defaults(query_engine_tools=[tool], llm=li.llm(), verbose=False)
    return {"answer": str(eng.query(ctx["input"]))}


registry.register("plan-execute", "llamaindex", run)
