"""RAG on **Haystack** — its native Pipeline: BM25 retriever → PromptBuilder → generator."""
from ... import registry, hay

_TPL = ("Answer the question using only these documents.\n"
        "{% for doc in documents %}- {{ doc.content }}\n{% endfor %}\n"
        "Question: {{ question }}\nAnswer:")


def run(ctx: dict) -> dict:
    from haystack import Pipeline
    from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
    from haystack.components.builders import PromptBuilder
    q = ctx["input"]
    pipe = Pipeline()
    pipe.add_component("retriever", InMemoryBM25Retriever(document_store=hay.doc_store(), top_k=3))
    pipe.add_component("prompt", PromptBuilder(template=_TPL, required_variables=["question"]))
    pipe.add_component("llm", hay.generator())
    pipe.connect("retriever.documents", "prompt.documents")
    pipe.connect("prompt.prompt", "llm.prompt")
    res = pipe.run({"retriever": {"query": q}, "prompt": {"question": q}})
    return {"answer": res["llm"]["replies"][0]}


registry.register("rag", "haystack", run)
