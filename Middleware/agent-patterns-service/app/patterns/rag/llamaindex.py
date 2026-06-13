"""RAG on **LlamaIndex** — native VectorStoreIndex + MetadataFilters for use-case-scoped retrieval.

Implements the 5 VKP RAG use cases via ctx['useCase']; the prompts come from `_base` (shared with every
framework cell). The use-case SCOPING is done the native LlamaIndex way — MetadataFilters on the index
(brand / is_brochure) + similarity_top_k — rather than the keyword corpus, so this keeps the native vector
showcase while honoring each use case (company-only, brochure-only, snapshot, wider)."""
from ... import registry, config, corpus, li
from . import _base


def _scoped_index():
    from llama_index.core import VectorStoreIndex, Document, Settings
    from llama_index.embeddings.openai import OpenAIEmbedding
    Settings.llm = li.llm()
    if config.OPENAI_API_KEY:
        Settings.embed_model = OpenAIEmbedding(api_key=config.OPENAI_API_KEY)
    docs = [Document(text=d["text"], metadata={"source": d["source"], "brand": d["source"].split("/")[0],
                                               "doc_type": "brochure" if "brochure" in d["source"] else "page"})
            for d in corpus._DOCS]
    return VectorStoreIndex.from_documents(docs)


def run(ctx: dict) -> dict:
    from llama_index.core.vector_stores import MetadataFilters, MetadataFilter, FilterOperator
    q = ctx["input"]
    uc, instr = _base.spec_for(ctx.get("useCase"))

    filters, k = None, 3
    if uc in ("company-scoped-faq", "snapshot-grounded"):
        brand = _base.company(q)
        if brand:
            filters = MetadataFilters(filters=[MetadataFilter(key="brand", value=brand, operator=FilterOperator.EQ)])
        k = 5 if uc == "snapshot-grounded" else 3
    elif uc == "brochure-pdf-lookup":
        filters = MetadataFilters(filters=[MetadataFilter(key="doc_type", value="brochure", operator=FilterOperator.EQ)])
    elif uc == "explain-feature":
        k = 4

    qe = _scoped_index().as_query_engine(llm=li.llm(), similarity_top_k=k, filters=filters)
    resp = qe.query(f"{instr}\n\nQuestion: {q}")
    sources = [n.node.metadata.get("source") for n in getattr(resp, "source_nodes", [])]
    return {"answer": str(resp), "steps": sources, "useCase": uc}


registry.register("rag", "llamaindex", run)
