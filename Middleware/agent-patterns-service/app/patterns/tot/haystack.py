"""Tree of Thoughts on **Haystack** — branch (propose 3) → evaluate (score) → select."""
import re

from ... import registry, hay


def run(ctx: dict) -> dict:
    q = ctx["input"]
    raw = hay.complete(f"Propose 3 DISTINCT candidate answers to: {q}. Separate each with '---'.")
    thoughts = [p.strip() for p in raw.split("---") if p.strip()][:3] or [raw]
    scores = []
    for t in thoughts:
        r = hay.complete(f"Rate 1-10 how well this answers '{q}'. Reply only the number.\n\n{t}")
        mm = re.search(r"\d+", r)
        scores.append(int(mm.group(0)) if mm else 5)
    best = max(range(len(thoughts)), key=lambda i: scores[i])
    return {"answer": thoughts[best], "steps": [f"thought{i+1}: score {s}" for i, s in enumerate(scores)]}


registry.register("tot", "haystack", run)
