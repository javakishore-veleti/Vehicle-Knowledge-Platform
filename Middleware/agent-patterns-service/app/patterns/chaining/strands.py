"""Prompt chaining / parallelization on **AWS Strands** — chains + fan-outs of Agent runs.

Implements the 5 VKP use cases via ctx['useCase']: multi-provider/sectioning/voting fan out across Agent
runs; ingestion/translate are deterministic chains with one LLM step. Prompts + the deterministic steps
(clean/hash/section-split/sentence-chunk/majority) come from `_base` (shared with every framework cell),
so sha256/chunk-count/majority match the other cells exactly."""
from ... import registry, sa
from . import _base


def _multi_provider(q):
    outs = [(n, sa.complete(q, sysp)) for n, sysp in _base.PROVIDERS]
    body = "\n\n".join(f"{n}: {t}" for n, t in outs)
    return {"answer": sa.complete(_base.CONSENSUS_PROMPT.format(body=body)), "steps": [n for n, _ in _base.PROVIDERS]}


def _ingestion(q):
    clean = _base.clean_text(q)
    title = sa.complete(_base.TITLE_PROMPT.format(c=clean[:500])).strip()
    return {"answer": f"stored → title='{title}', sha256={_base.sha16(clean)}, chars={len(clean)}",
            "steps": ["fetch", "clean", "title", "hash", "store"]}


def _sectioning(q):
    secs = _base.split_sections(q)
    parts = [sa.complete(_base.SUMMARIZE_PROMPT.format(t=s)) for s in secs]
    return {"answer": "Stitched summary:\n" + "\n".join(parts), "steps": [f"section{i+1}" for i in range(len(secs))]}


def _voting(q):
    votes = [sa.complete(q, _base.VOTER_SYS) for _ in range(3)]
    return {"answer": f"Majority answer ({len(votes)} voters): {_base.majority(votes)}", "steps": ["vote1", "vote2", "vote3"]}


def _translate_index(q):
    translated = sa.complete(_base.TRANSLATE_PROMPT.format(q=q))
    chunks = _base.split_sentences(translated)
    return {"answer": f"translated → {len(chunks)} chunks → embedded (384-dim) into vkp_vectors",
            "steps": ["translate", "chunk", "embed"]}


_USE_CASES = {"multi-provider-fanout": _multi_provider, "ingestion-chain": _ingestion,
              "sectioning": _sectioning, "voting": _voting, "translate-then-index": _translate_index}


def run(ctx: dict) -> dict:
    uc = ctx.get("useCase") if ctx.get("useCase") in _USE_CASES else _base.DEFAULT_UC
    res = _USE_CASES[uc](ctx["input"])
    res["useCase"] = uc
    return res


registry.register("chaining", "strands", run)
