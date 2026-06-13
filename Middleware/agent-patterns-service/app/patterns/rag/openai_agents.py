"""RAG on the **OpenAI Agents SDK** — an Agent whose @function_tool retrieves from the corpus."""
from ... import registry, corpus, oa


def run(ctx: dict) -> dict:
    from agents import Agent, Runner, function_tool

    @function_tool
    def search_docs(query: str) -> list:
        """Retrieve the most relevant vehicle documents for a query."""
        return [d["text"] for d in corpus.retrieve(query, k=3)]

    oa._ensure_key()
    agent = Agent(name="vkp-rag", model="gpt-4o-mini",
                  instructions="Call search_docs, then answer ONLY from the returned documents. Cite figures exactly.",
                  tools=[search_docs])
    return {"answer": Runner.run_sync(agent, ctx["input"]).final_output}


registry.register("rag", "openai_agents", run)
