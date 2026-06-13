"""RAG on **AWS Strands** — a Strands Agent whose native @tool retrieves from the corpus."""
from ... import registry, corpus, sa


def run(ctx: dict) -> dict:
    from strands import tool

    @tool
    def search_docs(query: str) -> list:
        """Retrieve the most relevant vehicle documents for a query."""
        return [d["text"] for d in corpus.retrieve(query, k=3)]

    ans = sa.run_agent("Call search_docs, then answer ONLY from the returned documents with exact figures.", ctx["input"], tools=[search_docs])
    return {"answer": ans}


registry.register("rag", "strands", run)
