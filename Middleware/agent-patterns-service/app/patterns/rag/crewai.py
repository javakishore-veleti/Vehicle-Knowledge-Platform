"""RAG on **CrewAI** — an agent with a search_docs tool retrieves, then answers with citations."""
from ... import registry, corpus, crew


def run(ctx: dict) -> dict:
    from crewai import Agent, Task, Crew, Process
    from crewai.tools import tool

    @tool("search_docs")
    def search_docs(query: str) -> str:
        """Search the vehicle knowledge base; returns the top snippets with their sources."""
        return "\n".join(f"[{i+1}] {d['text']} (source: {d['source']})" for i, d in enumerate(corpus.retrieve(query, 3)))

    agent = Agent(role="Vehicle Researcher", goal="Answer ONLY from retrieved sources and cite [n].",
                  backstory="A careful RAG analyst.", tools=[search_docs], llm=crew.crew_llm(), verbose=False)
    task = Task(description=f"Search the knowledge base and answer with citations: {ctx['input']}",
                expected_output="A cited answer.", agent=agent)
    return {"answer": str(Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False).kickoff())}


registry.register("rag", "crewai", run)
