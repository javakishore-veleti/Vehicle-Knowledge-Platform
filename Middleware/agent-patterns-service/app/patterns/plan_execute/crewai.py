"""Plan-and-Execute on **CrewAI** — a planner agent emits sub-queries; Python retrieves; a synthesizer answers."""
import json
import re

from ... import registry, corpus, crew


def run(ctx: dict) -> dict:
    from crewai import Agent, Task, Crew, Process
    q = ctx["input"]

    planner = Agent(role="Planner", goal="Decompose a question into focused sub-queries.",
                    backstory="Breaks complex questions into searchable parts.", llm=crew.crew_llm(), verbose=False)
    pt = Task(description=f"Decompose into 2-4 sub-queries. Return ONLY a JSON array of strings.\n\n{q}",
              expected_output="A JSON array of strings.", agent=planner)
    raw = str(Crew(agents=[planner], tasks=[pt], process=Process.sequential, verbose=False).kickoff())
    m = re.search(r"\[.*\]", raw, re.S)
    try:
        subs = json.loads(m.group(0)) if m else [q]
    except Exception:
        subs = [q]
    subs = [str(s) for s in subs][:4] or [q]

    seen = {}
    for sq in subs:
        for d in corpus.retrieve(sq, 2):
            seen.setdefault(d["source"], d)
    notes = "\n".join(f"- {d['text']} ({d['source']})" for d in seen.values())

    synth = Agent(role="Synthesizer", goal="Answer from the gathered notes.",
                  backstory="Writes the final, grounded answer.", llm=crew.crew_llm(), verbose=False)
    st = Task(description=f"Using these notes, answer: {q}\n\nNOTES:\n{notes}", expected_output="Final answer.", agent=synth)
    ans = str(Crew(agents=[synth], tasks=[st], process=Process.sequential, verbose=False).kickoff())
    return {"answer": ans, "steps": subs}


registry.register("plan-execute", "crewai", run)
