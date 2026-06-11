"""ReAct on **CrewAI** — an agent equipped with the vehicle_spec tool reasons + calls it (CrewAI's agent loop)."""
from ... import registry, tools, crew


def run(ctx: dict) -> dict:
    from crewai import Agent, Task, Crew, Process
    from crewai.tools import tool

    @tool("vehicle_spec")
    def vehicle_spec(model: str, field: str = "") -> str:
        """Look up specs (type, range, mpg, towing, price, seats) for a known vehicle model."""
        return str(tools.vehicle_spec(model, field))

    agent = Agent(role="Vehicle Analyst", goal="Answer using the vehicle_spec tool for any factual lookup.",
                  backstory="A precise automotive expert.", tools=[vehicle_spec], llm=crew.crew_llm(), verbose=False)
    task = Task(description=ctx["input"], expected_output="A factual answer grounded in the tool results.", agent=agent)
    out = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False).kickoff()
    return {"answer": str(out)}


registry.register("react", "crewai", run)
