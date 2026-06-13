"""RAG on **Google ADK** — an LlmAgent whose native FunctionTool retrieves from the corpus."""
from ... import registry, corpus, adk


def run(ctx: dict) -> dict:
    from google.adk.tools import FunctionTool

    def search_docs(query: str) -> list:
        """Retrieve the most relevant vehicle documents for a query."""
        return [d["text"] for d in corpus.retrieve(query, k=3)]

    ans = adk.run_agent("Call search_docs, then answer ONLY from the returned documents with exact figures.",
                        ctx["input"], tools=[FunctionTool(func=search_docs)])
    return {"answer": ans}


registry.register("rag", "google_adk", run)
