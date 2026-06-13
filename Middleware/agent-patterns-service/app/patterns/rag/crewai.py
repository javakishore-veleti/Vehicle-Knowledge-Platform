"""RAG on **CrewAI** — an agent with a use-case-scoped search_docs tool retrieves, then answers with
citations.

Implements the 5 VKP RAG use cases via ctx['useCase']. The retrieval-scoping + prompts come from
`_base` (shared with every framework cell): the search_docs tool applies the use case's scope (company,
brochure, snapshot, …), so the agentic RAG honors each use case. This cell shows ONLY the CrewAI mechanics."""
from ... import registry, crew
from . import _base


def run(ctx: dict) -> dict:
    from crewai import Agent, Task, Crew, Process
    from crewai.tools import tool
    q = ctx["input"]
    uc, instr = _base.spec_for(ctx.get("useCase"))

    @tool("search_docs")
    def search_docs(query: str) -> str:
        """Search the vehicle knowledge base (scoped to this use case); returns top snippets with sources."""
        return _base.format_sources(_base.retrieve_for(uc, query, scope_q=q))

    agent = Agent(role="Vehicle Researcher", goal=instr, backstory="A careful RAG analyst.",
                  tools=[search_docs], llm=crew.crew_llm(), verbose=False)
    task = Task(description=f"Use search_docs to retrieve, then answer with citations: {q}\n\n{instr}",
                expected_output="A cited answer.", agent=agent)
    ans = str(Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False).kickoff())
    steps = [d["source"] for d in _base.retrieve_for(uc, q)]
    return {"answer": ans, "steps": steps, "useCase": uc}


registry.register("rag", "crewai", run)
