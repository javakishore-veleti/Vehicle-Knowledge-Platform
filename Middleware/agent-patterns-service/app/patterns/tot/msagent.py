"""Tree of Thoughts on the **Microsoft Agent Framework** — branch (propose 3) → evaluate (score) → select."""
import re

from ... import registry, msa


def run(ctx: dict) -> dict:
    q = ctx["input"]

    async def _go():
        raw = await msa.acomplete(f"Propose 3 DISTINCT candidate answers to: {q}. Separate each with '---'.")
        thoughts = [p.strip() for p in raw.split("---") if p.strip()][:3] or [raw]
        scores = []
        for t in thoughts:
            r = await msa.acomplete(f"Rate 1-10 how well this answers '{q}'. Reply only the number.\n\n{t}", "You are a strict judge.")
            mm = re.search(r"\d+", r)
            scores.append(int(mm.group(0)) if mm else 5)
        best = max(range(len(thoughts)), key=lambda i: scores[i])
        return thoughts[best], [f"thought{i+1}: score {s}" for i, s in enumerate(scores)]

    ans, steps = msa.run_sync(_go())
    return {"answer": ans, "steps": steps}


registry.register("tot", "msagent", run)
