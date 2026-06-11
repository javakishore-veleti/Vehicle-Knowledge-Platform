"""Tree of Thoughts on **CrewAI** — a proposer agent yields 3 thoughts, an evaluator scores, Python selects best."""
import re

from ... import registry, crew


def run(ctx: dict) -> dict:
    from crewai import Agent, Task, Crew, Process
    q = ctx["input"]
    proposer = Agent(role="Proposer", goal="Propose distinct candidate answers.", backstory="Creative analyst.",
                     llm=crew.crew_llm(), verbose=False)
    pt = Task(description=f"Propose 3 DISTINCT candidate answers to: {q}. Separate each with a line '---'.",
              expected_output="3 candidates.", agent=proposer)
    raw = str(Crew(agents=[proposer], tasks=[pt], process=Process.sequential, verbose=False).kickoff())
    thoughts = [p.strip() for p in raw.split("---") if p.strip()][:3] or [raw]

    evaluator = Agent(role="Evaluator", goal="Score each candidate.", backstory="A strict scorer.",
                      llm=crew.crew_llm(), verbose=False)
    scores = []
    for t in thoughts:
        et = Task(description=f"Rate 1-10 how well this answers '{q}'. Reply only the number.\n\n{t}",
                  expected_output="A number.", agent=evaluator)
        r = str(Crew(agents=[evaluator], tasks=[et], process=Process.sequential, verbose=False).kickoff())
        mm = re.search(r"\d+", r)
        scores.append(int(mm.group(0)) if mm else 5)
    best = max(range(len(thoughts)), key=lambda i: scores[i])
    return {"answer": thoughts[best], "steps": [f"thought{i+1}: score {s}" for i, s in enumerate(scores)]}


registry.register("tot", "crewai", run)
