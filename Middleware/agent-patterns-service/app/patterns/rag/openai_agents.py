"""RAG on the **OpenAI Agents SDK** — an Agent whose use-case-scoped @function_tool retrieves the corpus.

Implements the 5 VKP RAG use cases via ctx['useCase']; the retrieval-scoping + prompts come from `_base`
(shared with every framework cell). The search_docs tool applies the use case's scope (company, brochure,
snapshot, …) so the agentic RAG honors each use case. This cell uses the native Agent + Runner."""
from ... import registry, oa
from . import _base


def run(ctx: dict) -> dict:
    from agents import Agent, Runner, function_tool
    q = ctx["input"]
    uc, instr = _base.spec_for(ctx.get("useCase"))

    @function_tool
    def search_docs(query: str) -> str:
        """Search the vehicle knowledge base (scoped to this use case); returns top snippets with sources."""
        return _base.format_sources(_base.retrieve_for(uc, query, scope_q=q))

    oa._ensure_key()
    agent = Agent(name="vkp-rag", model="gpt-4o-mini",
                  instructions=f"Call search_docs, then answer ONLY from the returned documents. {instr}",
                  tools=[search_docs])
    ans = Runner.run_sync(agent, q).final_output
    steps = [d["source"] for d in _base.retrieve_for(uc, q)]
    return {"answer": ans, "steps": steps, "useCase": uc}


registry.register("rag", "openai_agents", run)
