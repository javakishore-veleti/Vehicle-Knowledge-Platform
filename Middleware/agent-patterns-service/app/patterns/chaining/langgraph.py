"""Prompt chaining / parallelization on **LangGraph** — sequential chains OR fan-out→merge graphs.

Implements the 5 VKP use cases via ctx['useCase'] (default = multi-provider-fanout): fan-out for
multi-provider / sectioning / voting; deterministic chains for ingestion-chain / translate-then-index.
Prompts + deterministic steps come from `_base` (shared with every framework cell); this cell shows
ONLY the LangGraph graph topologies."""
import operator
from typing import Annotated, TypedDict

from ... import llm, registry
from . import _base


def _multi_provider(q):
    from langgraph.graph import StateGraph, START, END

    class S(TypedDict, total=False):
        outs: Annotated[list, operator.add]
        answer: str

    def provider(name, sysp): return lambda _s: {"outs": [(name, llm.complete(q, system=sysp))]}

    def merge(s):
        body = "\n\n".join(f"{n}: {t}" for n, t in s["outs"])
        return {"answer": llm.complete(_base.CONSENSUS_PROMPT.format(body=body))}

    g = StateGraph(S)
    for n, sy in _base.PROVIDERS:
        g.add_node(n, provider(n, sy))
    g.add_node("merge", merge)
    for n, _ in _base.PROVIDERS:
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
    def clean(s): return {"clean": _base.clean_text(s["raw"])}
    def title(s): return {"title": llm.complete(_base.TITLE_PROMPT.format(c=s["clean"][:500]))}
    def hsh(s): return {"hash": _base.sha16(s["clean"])}
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
    secs = _base.split_sections(q)

    class S(TypedDict, total=False):
        parts: Annotated[list, operator.add]
        answer: str

    def summ(i, text): return lambda _s: {"parts": [(i, llm.complete(_base.SUMMARIZE_PROMPT.format(t=text)))]}

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

    def voter(i): return lambda _s: {"votes": [llm.complete(q, system=_base.VOTER_SYS)]}

    def merge(s):
        return {"answer": f"Majority answer ({len(s['votes'])} voters): {_base.majority(s['votes'])}"}

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

    def translate(_s): return {"translated": llm.complete(_base.TRANSLATE_PROMPT.format(q=q))}
    def chunk(s): return {"chunks": _base.split_sentences(s["translated"])}
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
    uc = ctx.get("useCase") or _base.DEFAULT_UC
    res = _USE_CASES.get(uc, _multi_provider)(ctx["input"])
    res["useCase"] = uc
    return res


registry.register("chaining", "langgraph", run)
