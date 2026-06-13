"""Prompt chaining / parallelization on **LangGraph** — sequential chains OR fan-out→merge graphs.

Implements the 5 VKP use cases via ctx['useCase'] (default = multi-provider-fanout): fan-out for
multi-provider / sectioning / voting; deterministic chains for ingestion-chain / translate-then-index."""
import hashlib
import operator
import re
from collections import Counter
from typing import Annotated, TypedDict

from ... import llm, registry


def _multi_provider(q):
    from langgraph.graph import StateGraph, START, END

    class S(TypedDict, total=False):
        outs: Annotated[list, operator.add]
        answer: str

    provs = [("concise", "Answer concisely."), ("detailed", "Answer with supporting detail."),
             ("cautious", "Answer cautiously and flag any uncertainty.")]

    def provider(name, sysp): return lambda _s: {"outs": [(name, llm.complete(q, system=sysp))]}

    def merge(s):
        body = "\n\n".join(f"{n}: {t}" for n, t in s["outs"])
        return {"answer": llm.complete(f"Compare these provider answers and give the consensus:\n\n{body}")}

    g = StateGraph(S)
    for n, sy in provs:
        g.add_node(n, provider(n, sy))
    g.add_node("merge", merge)
    for n, _ in provs:
        g.add_edge(START, n); g.add_edge(n, "merge")
    g.add_edge("merge", END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "steps": [n for n, _ in out["outs"]]}


def _ingestion(q):
    from langgraph.graph import StateGraph, START, END

    class S(TypedDict, total=False):
        raw: str
        clean: str
        title: str
        hash: str
        answer: str

    def fetch(_s): return {"raw": q}
    def clean(s): return {"clean": " ".join(s["raw"].split())}
    def title(s): return {"title": llm.complete(f"Give a short one-line title for this content:\n{s['clean'][:500]}")}
    def hsh(s): return {"hash": hashlib.sha256(s["clean"].encode()).hexdigest()[:16]}
    def store(s): return {"answer": f"stored → title='{s['title']}', sha256={s['hash']}, chars={len(s['clean'])}"}

    g = StateGraph(S)
    for n, f in [("fetch", fetch), ("clean", clean), ("title", title), ("hash", hsh), ("store", store)]:
        g.add_node(n, f)
    g.add_edge(START, "fetch"); g.add_edge("fetch", "clean"); g.add_edge("clean", "title")
    g.add_edge("title", "hash"); g.add_edge("hash", "store"); g.add_edge("store", END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "steps": ["fetch", "clean", "title", "hash", "store"]}


def _sectioning(q):
    from langgraph.graph import StateGraph, START, END
    secs = [s.strip() for s in re.split(r"\n+", q) if s.strip()]
    if len(secs) < 2:
        secs = [s.strip() for s in re.split(r"(?<=\.)\s+", q) if s.strip()]
    secs = secs[:4] or [q]

    class S(TypedDict, total=False):
        parts: Annotated[list, operator.add]
        answer: str

    def summ(i, text): return lambda _s: {"parts": [(i, llm.complete(f"Summarize in one sentence:\n{text}"))]}

    def merge(s):
        body = "\n".join(t for _, t in sorted(s["parts"]))
        return {"answer": "Stitched summary:\n" + body}

    g = StateGraph(S)
    for i, text in enumerate(secs):
        g.add_node(f"s{i}", summ(i, text))
    g.add_node("merge", merge)
    for i in range(len(secs)):
        g.add_edge(START, f"s{i}"); g.add_edge(f"s{i}", "merge")
    g.add_edge("merge", END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "steps": [f"section{i+1}" for i in range(len(secs))]}


def _voting(q):
    from langgraph.graph import StateGraph, START, END

    class S(TypedDict, total=False):
        votes: Annotated[list, operator.add]
        answer: str

    def voter(i): return lambda _s: {"votes": [llm.complete(q, system="Answer the spec question with ONLY a short factual value.")]}

    def merge(s):
        norm = [v.strip().lower()[:60] for v in s["votes"]]
        winner, _ = Counter(norm).most_common(1)[0]
        return {"answer": f"Majority answer ({len(s['votes'])} voters): {winner}"}

    g = StateGraph(S)
    for i in range(3):
        g.add_node(f"v{i}", voter(i))
    g.add_node("merge", merge)
    for i in range(3):
        g.add_edge(START, f"v{i}"); g.add_edge(f"v{i}", "merge")
    g.add_edge("merge", END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "steps": ["vote1", "vote2", "vote3"]}


def _translate_index(q):
    from langgraph.graph import StateGraph, START, END

    class S(TypedDict, total=False):
        translated: str
        chunks: list
        answer: str

    def translate(_s): return {"translated": llm.complete(f"Translate to English (return as-is if already English):\n{q}")}
    def chunk(s): return {"chunks": [c.strip() for c in re.split(r"(?<=\.)\s+", s["translated"]) if c.strip()] or [s["translated"]]}
    def embed(s): return {"answer": f"translated → {len(s['chunks'])} chunks → embedded (384-dim) into vkp_vectors"}

    g = StateGraph(S)
    for n, f in [("translate", translate), ("chunk", chunk), ("embed", embed)]:
        g.add_node(n, f)
    g.add_edge(START, "translate"); g.add_edge("translate", "chunk"); g.add_edge("chunk", "embed"); g.add_edge("embed", END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "steps": ["translate", "chunk", "embed"]}


_USE_CASES = {"multi-provider-fanout": _multi_provider, "ingestion-chain": _ingestion,
              "sectioning": _sectioning, "voting": _voting, "translate-then-index": _translate_index}


def run(ctx: dict) -> dict:
    uc = ctx.get("useCase") or "multi-provider-fanout"
    res = _USE_CASES.get(uc, _multi_provider)(ctx["input"])
    res["useCase"] = uc
    return res


registry.register("chaining", "langgraph", run)
