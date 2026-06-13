"""RAG on **AWS Strands** — a Strands Agent whose use-case-scoped @tool retrieves the corpus.

Implements the 5 VKP RAG use cases via ctx['useCase']; the retrieval-scoping + prompts come from `_base`
(shared with every framework cell). The search_docs tool applies the use case's scope (company, brochure,
snapshot, …) so the agentic RAG honors each use case. This cell uses the native Strands Agent + @tool."""
from ... import registry, sa
from . import _base


def run(ctx: dict) -> dict:
    from strands import tool
    q = ctx["input"]
    uc, instr = _base.spec_for(ctx.get("useCase"))

    @tool
    def search_docs(query: str) -> str:
        """Search the vehicle knowledge base (scoped to this use case); returns top snippets with sources."""
        return _base.format_sources(_base.retrieve_for(uc, query, scope_q=q))

    ans = sa.run_agent(f"Call search_docs, then answer ONLY from the returned documents. {instr}",
                       q, tools=[search_docs])
    steps = [d["source"] for d in _base.retrieve_for(uc, q)]
    return {"answer": ans, "steps": steps, "useCase": uc}


registry.register("rag", "strands", run)
