"""Router on **CrewAI** — a classifier agent picks a category; Python routes to the matching specialist agent."""
from ... import registry, crew


def run(ctx: dict) -> dict:
    from crewai import Agent, Task, Crew, Process
    q = ctx["input"]

    clf = Agent(role="Router", goal="Classify the question.", backstory="Routes questions to specialists.",
                llm=crew.crew_llm(), verbose=False)
    ct = Task(description=f"Classify as exactly one word: spec, compare, recommend, other.\n\n{q}",
              expected_output="One word.", agent=clf)
    raw = str(Crew(agents=[clf], tasks=[ct], process=Process.sequential, verbose=False).kickoff()).strip().lower()
    route = (raw.split() or ["other"])[0]
    route = route if route in ("spec", "compare", "recommend") else "other"

    roles = {"spec": "a vehicle SPEC expert", "compare": "a vehicle COMPARISON expert",
             "recommend": "a vehicle BUYING ADVISOR", "other": "a helpful vehicle assistant"}
    specialist = Agent(role=roles[route], goal="Answer the question well.", backstory=roles[route],
                       llm=crew.crew_llm(), verbose=False)
    at = Task(description=q, expected_output="A strong answer.", agent=specialist)
    ans = str(Crew(agents=[specialist], tasks=[at], process=Process.sequential, verbose=False).kickoff())
    return {"answer": ans, "steps": [f"routed -> {route}"]}


registry.register("router", "crewai", run)
