"""Tree of Thoughts on **CrewAI** — a proposer agent yields 3 thoughts, an evaluator agent scores each,
Python selects the best.

Implements the 5 VKP use cases via ctx['useCase']. The branch prompts + eval criteria come from
`_base.USE_CASES` (shared with every framework cell); this cell shows ONLY the CrewAI mechanics."""
from ... import registry, crew
from . import _base


def run(ctx: dict) -> dict:
    from crewai import Agent, Task, Crew, Process
    q = ctx["input"]
    uc, branch_p, eval_crit = _base.spec_for(ctx.get("useCase"), q)

    proposer = Agent(role="Proposer", goal="Propose distinct candidate answers.", backstory="A creative automotive analyst.",
                     llm=crew.crew_llm(), verbose=False)
    pt = Task(description=branch_p, expected_output="3 candidates separated by '---'.", agent=proposer)
    raw = str(Crew(agents=[proposer], tasks=[pt], process=Process.sequential, verbose=False).kickoff())
    thoughts = _base.parse_thoughts(raw)

    evaluator = Agent(role="Evaluator", goal="Score each candidate against the criterion.", backstory="A strict scorer.",
                      llm=crew.crew_llm(), verbose=False)
    scores = []
    for t in thoughts:
        et = Task(description=_base.eval_prompt(eval_crit, t), expected_output="A number.", agent=evaluator)
        scores.append(_base.score_of(str(Crew(agents=[evaluator], tasks=[et], process=Process.sequential, verbose=False).kickoff())))

    best = max(range(len(thoughts)), key=lambda i: scores[i])
    return {"answer": thoughts[best], "useCase": uc,
            "steps": [f"thought{i+1}: score {s}" for i, s in enumerate(scores)]}


registry.register("tot", "crewai", run)
