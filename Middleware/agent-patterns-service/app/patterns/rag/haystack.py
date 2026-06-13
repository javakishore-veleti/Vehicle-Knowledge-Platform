"""RAG on **Haystack** — native Pipeline (BM25 retriever → PromptBuilder → generator) + meta filters.

Implements the 5 VKP RAG use cases via ctx['useCase']; the prompts come from `_base` (shared with every
framework cell). The use-case SCOPING is done the native Haystack way — `filters` on the BM25 retriever
over `meta.brand` / `meta.doc_type` + top_k — keeping the native pipeline showcase while honoring each
use case (company-only, brochure-only, snapshot, wider)."""
from ... import registry, corpus, hay
from . import _base

_TPL = ("{{ instr }}\n{% for doc in documents %}- {{ doc.content }} (source: {{ doc.meta.source }})\n{% endfor %}\n"
        "Question: {{ question }}\nAnswer:")


def _scoped_store():
    from haystack import Document
    from haystack.document_stores.in_memory import InMemoryDocumentStore
    store = InMemoryDocumentStore()
    store.write_documents([Document(content=d["text"], meta={"source": d["source"], "brand": d["source"].split("/")[0],
                                                             "doc_type": "brochure" if "brochure" in d["source"] else "page"})
                           for d in corpus._DOCS])
    return store


def run(ctx: dict) -> dict:
    from haystack import Pipeline
    from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
    from haystack.components.builders import PromptBuilder
    q = ctx["input"]
    uc, instr = _base.spec_for(ctx.get("useCase"))

    filters, k = None, 3
    if uc in ("company-scoped-faq", "snapshot-grounded"):
        brand = _base.company(q)
        if brand:
            filters = {"field": "meta.brand", "operator": "==", "value": brand}
        k = 5 if uc == "snapshot-grounded" else 3
    elif uc == "brochure-pdf-lookup":
        filters = {"field": "meta.doc_type", "operator": "==", "value": "brochure"}
    elif uc == "explain-feature":
        k = 4

    pipe = Pipeline()
    pipe.add_component("retriever", InMemoryBM25Retriever(document_store=_scoped_store(), top_k=k))
    pipe.add_component("prompt", PromptBuilder(template=_TPL, required_variables=["question", "instr"]))
    pipe.add_component("llm", hay.generator())
    pipe.connect("retriever.documents", "prompt.documents")
    pipe.connect("prompt.prompt", "llm.prompt")

    retr_in = {"query": q}
    if filters:
        retr_in["filters"] = filters
    res = pipe.run({"retriever": retr_in, "prompt": {"question": q, "instr": instr}}, include_outputs_from={"retriever"})
    sources = [d.meta.get("source") for d in res["retriever"]["documents"]]
    return {"answer": res["llm"]["replies"][0], "steps": sources, "useCase": uc}


registry.register("rag", "haystack", run)
