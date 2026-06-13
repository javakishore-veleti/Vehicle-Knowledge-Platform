"""RAG on the **Microsoft Agent Framework** — an Agent whose native @tool retrieves from the corpus."""
from ... import registry, corpus, msa


def run(ctx: dict) -> dict:
    from agent_framework import tool

    @tool
    def search_docs(query: str) -> list:
        """Retrieve the most relevant vehicle documents for a query."""
        return [d["text"] for d in corpus.retrieve(query, k=3)]

    async def _go():
        return await msa.acomplete(ctx["input"], "Call search_docs, then answer ONLY from the returned documents with exact figures.", tools=[search_docs])

    return {"answer": msa.run_sync(_go())}


registry.register("rag", "msagent", run)
