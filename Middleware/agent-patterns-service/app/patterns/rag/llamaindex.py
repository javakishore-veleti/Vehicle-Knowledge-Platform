"""RAG on **LlamaIndex** — a VectorStoreIndex query engine (its native RAG)."""
from ... import registry, li


def run(ctx: dict) -> dict:
    qe = li.index().as_query_engine(llm=li.llm())
    resp = qe.query(ctx["input"])
    sources = [n.node.metadata.get("source") for n in getattr(resp, "source_nodes", [])]
    return {"answer": str(resp), "steps": sources}


registry.register("rag", "llamaindex", run)
