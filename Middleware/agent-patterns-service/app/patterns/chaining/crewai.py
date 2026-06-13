"""Prompt chaining / parallelization on **CrewAI** — agents + tasks wired per use case.

Implements the 5 VKP use cases via ctx['useCase']: multi-provider/sectioning fan out across SEPARATE
agents (CrewAI can't reuse one executor concurrently); ingestion/translate are deterministic chains
with a single LLM step; voting tallies a deterministic majority. Prompts + deterministic steps come
from `_base` (shared with every framework cell)."""
from ... import registry, crew
from . import _base


def _multi_provider(q):
    provs = [_mk(role=f"{n} provider", goal=sysp) for n, sysp in _base.PROVIDERS]
    ptasks = [_task(f"{sysp}\n\nQuestion: {q}", "An answer.", provs[i], async_execution=True)
              for i, (n, sysp) in enumerate(_base.PROVIDERS)]
    lead = _mk("Lead Advisor", "Give the consensus across provider answers.")
    merge = _task("Compare the provider answers (your context) and give the consensus.", "The consensus answer.", lead, context=ptasks)
    out = _crew(provs + [lead], ptasks + [merge])
    return {"answer": str(out), "steps": [n for n, _ in _base.PROVIDERS]}


def _ingestion(q):
    clean = _base.clean_text(q)
    titler = _mk("Content Titler", "Write a short one-line title.")
    t = _task(_base.TITLE_PROMPT.format(c=clean[:500]), "A one-line title.", titler)
    _crew([titler], [t])
    title = str(t.output).strip()
    return {"answer": f"stored → title='{title}', sha256={_base.sha16(clean)}, chars={len(clean)}",
            "steps": ["fetch", "clean", "title", "hash", "store"]}


def _sectioning(q):
    secs = _base.split_sections(q)
    summers = [_mk(f"Summarizer {i+1}", "Summarize a section in one sentence.") for i in range(len(secs))]
    tasks = [_task(_base.SUMMARIZE_PROMPT.format(t=secs[i]), "One sentence.", summers[i], async_execution=True)
             for i in range(len(secs))]
    editor = _mk("Stitch Editor", "Stitch section summaries into one.")
    stitch = _task("Combine the section summaries (your context) into one stitched summary.", "Stitched summary.", editor, context=tasks)
    out = _crew(summers + [editor], tasks + [stitch])
    return {"answer": str(out), "steps": [f"section{i+1}" for i in range(len(secs))]}


def _voting(q):
    voters = [_mk(f"Voter {i+1}", "Answer with ONLY a short factual value.") for i in range(3)]
    tasks = [_task(f"{_base.VOTER_SYS}\n\nQuestion: {q}", "A short factual value.", voters[i]) for i in range(3)]
    _crew(voters, tasks)
    votes = [str(t.output) for t in tasks]
    return {"answer": f"Majority answer ({len(votes)} voters): {_base.majority(votes)}", "steps": ["vote1", "vote2", "vote3"]}


def _translate_index(q):
    translator = _mk("Translator", "Translate vehicle content to English.")
    t = _task(_base.TRANSLATE_PROMPT.format(q=q), "English text.", translator)
    _crew([translator], [t])
    chunks = _base.split_sentences(str(t.output))
    return {"answer": f"translated → {len(chunks)} chunks → embedded (384-dim) into vkp_vectors",
            "steps": ["translate", "chunk", "embed"]}


_USE_CASES = {"multi-provider-fanout": _multi_provider, "ingestion-chain": _ingestion,
              "sectioning": _sectioning, "voting": _voting, "translate-then-index": _translate_index}


# --- thin CrewAI constructors (imports kept lazy inside run) ---
def _mk(role, goal):
    from crewai import Agent
    return Agent(role=role, goal=goal, backstory="A precise automotive assistant.", llm=crew.crew_llm(), verbose=False)


def _task(description, expected, agent, context=None, async_execution=False):
    from crewai import Task
    kw = {"description": description, "expected_output": expected, "agent": agent, "async_execution": async_execution}
    if context:
        kw["context"] = context
    return Task(**kw)


def _crew(agents, tasks):
    from crewai import Crew, Process
    return Crew(agents=agents, tasks=tasks, process=Process.sequential, verbose=False).kickoff()


def run(ctx: dict) -> dict:
    uc = ctx.get("useCase") or _base.DEFAULT_UC
    res = _USE_CASES.get(uc, _multi_provider)(ctx["input"])
    res["useCase"] = uc
    return res


registry.register("chaining", "crewai", run)
