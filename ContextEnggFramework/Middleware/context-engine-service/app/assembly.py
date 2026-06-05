"""Context Assembly Layer — aggregate, deduplicate, rank, order, compress, and format the retrieval +
memory signals into the final context block. Implements the 5 context-engineering strategies.
"""
from . import config


def _dedupe_rank(chunks: list[dict]) -> list[dict]:
    seen, out = set(), []
    for c in sorted(chunks, key=lambda c: c.get("score", 0.0), reverse=True):
        key = (c.get("sourceUrl"), (c.get("snippet") or "")[:80])
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
    return out


def _compress(turns: list[dict], keep: int = 4) -> list[dict]:
    """Strategy 2 (compression): keep recent turns verbatim, summarise older ones into one line."""
    if len(turns) <= keep:
        return turns
    older = turns[:-keep]
    summary = "Earlier: " + " | ".join((t.get("text") or "")[:80] for t in older)
    return [{"role": "summary", "text": summary}] + turns[-keep:]


def assemble(query: str, chunks: list[dict], turns: list[dict], scope_info: dict, rules: str) -> tuple[str, list[dict]]:
    # Strategy 1 (selection): rank + dedupe, then fit to the char budget — write less, include more.
    ranked = _dedupe_rank(chunks)
    picked, used = [], 0
    for c in ranked:
        snippet = (c.get("snippet") or "")[:600]
        if used + len(snippet) > config.CONTEXT_CHAR_BUDGET:
            break
        picked.append({**c, "snippet": snippet})
        used += len(snippet)

    turns = _compress(turns)  # Strategy 2

    # Strategy 5 (format optimisation): structured markdown blocks (structure is signal).
    sources = "\n".join(f"[{i + 1}] {c['sourceUrl']}\n{c['snippet']}" for i, c in enumerate(picked))
    history = "\n".join(f"{t['role']}: {t['text']}" for t in turns)

    # Strategy 3 (ordering): rules + scope FIRST, the immediate task LAST (models attend least to the
    # middle). Strategy 4 (isolation) is handled by the orchestrator's specialised steps.
    block = (
        f"## RULES\n{rules}\n\n"
        f"## SCOPE\n{scope_info['policy']}\n\n"
        f"## SOURCES\n{sources or '(none)'}\n\n"
        f"## CONVERSATION\n{history or '(none)'}\n\n"
        f"## TASK\n{query}\n"
    )
    return block, picked
