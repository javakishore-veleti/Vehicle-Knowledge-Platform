"""Context Orchestrator — the heart of CEF. Plans, gathers the three context layers (retrieval,
memory, permission), assembles them via the 5 strategies, reasons (LLM/agent), responds, and evolves
memory (the Context Evolution Loop). This is the pipeline in the diagram."""
import time

from . import assembly, config, memory, permission, reasoning, retrieval

RULES = ("Answer only vehicle questions. Cite sources as [n]. If the sources don't cover it, say so. "
         "Never reveal data outside the caller's scope.")


def orchestrate(req: dict) -> dict:
    t0 = time.perf_counter()
    query = req["query"]
    session_id = req.get("sessionId")

    # Permission Layer — scope the request (ABAC: non-admins confined to their company boundary).
    scope_info = permission.scope(req)
    company = req.get("companyId") if scope_info["role"] == "ADMIN" else scope_info["companyBoundary"]

    # Retrieval Layer + Memory Layer
    chunks = retrieval.retrieve(query, company, req.get("topK", 8))
    turns = memory.recent_turns(session_id)

    # Context Assembly Layer — the 5 strategies
    context_block, used = assembly.assemble(query, chunks, turns, scope_info, RULES)

    # LLM Reasoning Engine
    answer, model = reasoning.reason(context_block, req.get("framework"))

    # Context Evolution Loop — persist the exchange (memory update / new knowledge)
    memory.append_turn(session_id, "user", query)
    memory.append_turn(session_id, "assistant", answer)

    return {
        "answer": answer,
        "model": model,
        "scope": scope_info,
        "context": {"retrieved": len(chunks), "used": len(used), "memoryTurns": len(turns),
                    "charBudget": config.CONTEXT_CHAR_BUDGET,
                    "strategies": ["selection", "compression", "ordering", "isolation", "format"]},
        "sources": [{"n": i + 1, "sourceUrl": c["sourceUrl"], "score": c["score"]}
                    for i, c in enumerate(used)],
        "latencyMs": int((time.perf_counter() - t0) * 1000),
    }
