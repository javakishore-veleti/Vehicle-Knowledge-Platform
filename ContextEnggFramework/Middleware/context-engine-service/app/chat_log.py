"""Per-request telemetry ledger for the CEF chat — `cef_chat_request_log` (Postgres, jsonb-heavy).

Mirrors the explore-service's veh_search_request_log: one richly-detailed row per orchestrate call
capturing *what happened* across the CEF pipeline (permission -> retrieval -> memory -> assembly ->
reasoning -> evolution): input params, request origin, knowledge-base scope, the 5 assembly
strategies, tech stack, DB tables + indexes, LLM/agent reasoning engine + 3rd-party vendors, the
ordered flow steps (drive the UI diagram), and the cited sources. Recording is best-effort.

List/detail APIs back the cef-portal "Chat Logs" pages (server-side ?page&size + latest-N ?limit).
"""
from typing import Optional

import psycopg2
from psycopg2.extras import Json, RealDictCursor

from . import config

_ready = False

# Seeded automakers (the chat's "knowledge base" dropdown) -> friendly name.
_COMPANIES = {
    "10000000-0000-4000-8000-000000000001": "General Motors",
    "10000000-0000-4000-8000-000000000002": "Ford",
    "10000000-0000-4000-8000-000000000003": "Honda",
    "10000000-0000-4000-8000-000000000004": "Toyota",
    "10000000-0000-4000-8000-000000000005": "BMW",
}


def _pg():
    return psycopg2.connect(host=config.PG_HOST, port=config.PG_PORT, dbname=config.PG_DB,
                            user=config.PG_USER, password=config.PG_PASSWORD, options=config.PG_OPTIONS)


def ensure_schema() -> None:
    global _ready
    if _ready:
        return
    with _pg() as conn, conn.cursor() as cur:
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {config.PG_SCHEMA}")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS cef_chat_request_log (
                id             TEXT PRIMARY KEY,
                created_dt     TIMESTAMPTZ NOT NULL DEFAULT now(),
                title          TEXT,
                description    TEXT,
                query          TEXT,
                company_id     TEXT,
                knowledge_base TEXT,
                role           TEXT,
                framework      TEXT,
                model          TEXT,
                origin_source  TEXT,
                status         TEXT,
                latency_ms     INTEGER,
                retrieved      INTEGER,
                used           INTEGER,
                memory_turns   INTEGER,
                session_id     TEXT,
                request_params JSONB,
                request_origin JSONB,
                scope          JSONB,
                strategies     JSONB,
                tech_stack     JSONB,
                db_tables      JSONB,
                indexes        JSONB,
                llms           JSONB,
                vendors        JSONB,
                steps          JSONB,
                result_summary JSONB,
                answer         JSONB
            )
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS cef_log_created_idx   ON cef_chat_request_log (created_dt DESC)")
        cur.execute("CREATE INDEX IF NOT EXISTS cef_log_company_idx   ON cef_chat_request_log (company_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS cef_log_status_idx    ON cef_chat_request_log (status)")
    _ready = True


def _vendor_for(model: str) -> str:
    m = (model or "").lower()
    if m.startswith("agentic:"):
        return "agentic-service (roster)"
    if "gpt" in m or "openai" in m:
        return "OpenAI"
    if "llama" in m or "groq" in m:
        return "Groq"
    if "claude" in m:
        return "Anthropic"
    if "gemini" in m:
        return "Google"
    return model or "unknown"


def build(*, req: dict, result: dict, origin: Optional[dict], latency_ms: int) -> dict:
    query = req.get("query")
    session_id = req.get("sessionId")
    company_id = req.get("companyId")
    role = (req.get("role") or "USER").upper()
    framework = req.get("framework")
    kb = _COMPANIES.get(company_id or "", company_id or "all (admin)")

    ctx = result.get("context") or {}
    scope = result.get("scope") or {}
    model = result.get("model")
    sources = result.get("sources") or []
    strategies = ctx.get("strategies") or ["selection", "compression", "ordering", "isolation", "format"]
    retrieved = ctx.get("retrieved", 0)
    used = ctx.get("used", 0)
    memory_turns = ctx.get("memoryTurns", 0)
    embed_vendor = "OpenAI" if config.EMBED_PROVIDER == "openai" else "local (sentence-transformers via fastembed)"
    reason_vendor = _vendor_for(model)

    tech_stack = [
        {"layer": "frontend", "tech": "Angular 19 (cef-portal)"},
        {"layer": "api", "tech": "FastAPI (context-engine-service :8093)"},
        {"layer": "orchestrator", "tech": "CEF Context Orchestrator"},
        {"layer": "permission", "tech": f"ABAC scope · role={role}"},
        {"layer": "retrieval", "tech": f"pgVector · {config.VECTOR_TABLE}"},
        {"layer": "embeddings", "tech": f"{config.EMBED_PROVIDER} · {config.EMBED_MODEL}"},
        {"layer": "memory", "tech": "MongoDB cef_memory (Context Evolution loop)"},
        {"layer": "assembly", "tech": "5 strategies: " + ", ".join(strategies)},
        {"layer": "reasoning", "tech": (f"agentic-service roster ({model})" if (model or '').startswith('agentic:')
                                        else f"LLM · {model}")},
        {"layer": "telemetry", "tech": "Prometheus + OpenTelemetry (Jaeger)"},
    ]
    db_tables = [
        {"name": config.VECTOR_TABLE, "db": "postgres", "role": "vector embeddings (retrieval)", "op": "SELECT"},
        {"name": "cef_memory", "db": "mongodb", "role": "conversation memory (evolution loop)", "op": "find/insert"},
        {"name": "cef_chat_request_log", "db": "postgres", "role": "this telemetry row", "op": "INSERT"},
    ]
    indexes = [
        {"name": f"{config.VECTOR_TABLE} (ivfflat/hnsw on embedding)", "table": config.VECTOR_TABLE,
         "type": "vector (cosine <=>)", "used": True},
        {"name": "cef_memory.sessionId", "table": "cef_memory", "type": "Mongo index", "used": memory_turns > 0},
    ]
    llms = [{"role": "reasoning", "model": model, "vendor": reason_vendor, "framework": framework, "ok": True}]
    _reason_desc = (f"agentic-service roster ({model}) — the reasoning is delegated to a pluggable agent SDK "
                    "instead of a direct LLM call." if (model or '').startswith('agentic:')
                    else f"{reason_vendor} chat API generates the final answer from the assembled context block ({model}).")
    vendors = [
        {"name": reason_vendor, "kind": "reasoning", "role": f"answer generation ({model})", "ok": True,
         "description": _reason_desc},
        {"name": embed_vendor, "kind": "embeddings", "role": f"query embedding ({config.EMBED_MODEL})", "ok": True,
         "description": ("Embeds the query IN-PROCESS via fastembed (ONNX) into a 384-dim vector with "
                         f"{config.EMBED_MODEL} — no external call, no cost — to drive pgVector retrieval.")},
        {"name": "MongoDB", "kind": "memory store", "role": "cef_memory conversation turns", "ok": True,
         "description": ("Stores the conversation turns in the cef_memory collection. This is the Context "
                         "Evolution loop: prior turns are recalled to give the next answer continuity.")},
    ]

    vector_sql = (f"SELECT source_url, chunk_text, 1 - (embedding <=> :q::vector) AS score\n"
                  f"  FROM {config.VECTOR_TABLE}\n  WHERE company_id = :company  -- scoped by Permission layer\n"
                  f"  ORDER BY embedding <=> :q::vector\n  LIMIT {req.get('topK', 8)}\n"
                  f"-- :q = 384-dim query embedding ({config.EMBED_MODEL})")

    steps = []
    n = [0]
    def step(key, label, typ, status="ok", desc="", detail=None):
        n[0] += 1
        steps.append({"n": n[0], "key": key, "label": label, "type": typ, "status": status,
                      "ms": None, "desc": desc, "detail": detail or {}})

    osrc = (origin or {}).get("source") or "chat"
    step("request", "Message received", "request", "ok",
         "The chat message arrives at the CEF Context Orchestrator. We record where it came from "
         "(a suggestion chip or the composer) and the input params.",
         {"origin": osrc, "label": (origin or {}).get("label"), "query": query})
    step("permission", "Permission scope", "permission", "ok",
         "The Permission layer (ABAC) decides what the caller may see: an ADMIN can query any company, "
         f"a USER is confined to their company boundary. Here the knowledge base is scoped to {kb}.",
         {"role": role, "companyBoundary": scope.get("companyBoundary"), "knowledgeBase": kb})
    step("retrieve", "Retrieval (pgVector)", "retrieve", "ok",
         f"Embeds the query and runs a vector search over {config.VECTOR_TABLE}, scoped to the company, "
         f"returning the top {req.get('topK', 8)} chunks. Retrieved {retrieved}.",
         {"table": config.VECTOR_TABLE, "topK": req.get("topK", 8), "retrieved": retrieved,
          "vectorQuery": vector_sql})
    step("memory", "Memory recall", "memory", "ok",
         "Recalls the recent conversation turns for this session from MongoDB cef_memory, so the answer "
         "has continuity (the Context Evolution loop's read side).",
         {"store": "MongoDB cef_memory", "turns": memory_turns})
    step("assemble", "Context assembly", "assemble", "ok",
         "The Context Assembly layer applies the 5 strategies — selection, compression, ordering, "
         "isolation, format — to fit the most relevant retrieved chunks + memory into the char budget.",
         {"strategies": strategies, "used": used, "charBudget": ctx.get("charBudget")})
    step("reason", "LLM reasoning", "reason", "ok",
         _reason_desc,
         {"model": model, "vendor": reason_vendor, "framework": framework})
    step("evolve", "Context evolution", "evolve", "ok",
         "Persists this exchange (user + assistant turns) back to cef_memory so future turns in the "
         "session build on it — the write side of the Context Evolution loop.",
         {"appended": 2, "store": "cef_memory"})
    step("answer", "Answer returned", "answer", "ok",
         f"The cited answer plus its {len(sources)} source(s) are returned to the chat UI.",
         {"sources": len(sources)})
    step("persist", "Telemetry persisted", "store", "ok",
         "This row — every field on this page — is written to cef_chat_request_log for the Chat Logs view.",
         {"table": "cef_chat_request_log"})

    title = f"CEF chat “{(query or '')[:48]}” · {kb} · {model}"
    description = (
        f"Orchestrated a {role}-scoped chat over {kb}: retrieved {retrieved} chunk(s), used {used} "
        f"after 5-strategy assembly, with {memory_turns} memory turn(s); reasoned via {model}"
        + (f" ({framework})" if framework else "") + f". Origin: {osrc}."
    )

    return {
        "id": result.get("logId") or req.get("_logId"), "title": title, "description": description,
        "query": query, "company_id": company_id, "knowledge_base": kb, "role": role,
        "framework": framework, "model": model, "origin_source": osrc, "status": "ok",
        "latency_ms": latency_ms, "retrieved": retrieved, "used": used, "memory_turns": memory_turns,
        "session_id": session_id,
        "request_params": {"query": query, "companyId": company_id, "role": role,
                           "framework": framework, "topK": req.get("topK", 8)},
        "request_origin": origin or {"source": "chat"},
        "scope": scope, "strategies": [{"name": s, "enabled": True} for s in strategies],
        "tech_stack": tech_stack, "db_tables": db_tables, "indexes": indexes, "llms": llms,
        "vendors": vendors, "steps": steps,
        "result_summary": {"retrieved": retrieved, "used": used, "memoryTurns": memory_turns,
                           "sources": sources},
        "answer": {"model": model, "text": result.get("answer"), "sources": len(sources)},
    }


_JSONB = ("request_params", "request_origin", "scope", "strategies", "tech_stack", "db_tables",
          "indexes", "llms", "vendors", "steps", "result_summary", "answer")
_SCALAR = ("id", "title", "description", "query", "company_id", "knowledge_base", "role", "framework",
           "model", "origin_source", "status", "latency_ms", "retrieved", "used", "memory_turns",
           "session_id")


def record(rec: dict) -> None:
    try:
        if not rec.get("id"):
            return
        ensure_schema()
        cols = list(_SCALAR) + list(_JSONB)
        vals = [rec.get(c) for c in _SCALAR] + [Json(rec.get(c)) for c in _JSONB]
        placeholders = ", ".join(["%s"] * len(cols))
        with _pg() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO cef_chat_request_log ({', '.join(cols)}) VALUES ({placeholders}) "
                f"ON CONFLICT (id) DO NOTHING",
                vals,
            )
    except Exception:  # noqa: BLE001
        pass


_LIST_COLS = ("id", "created_dt", "title", "query", "knowledge_base", "role", "model",
              "framework", "origin_source", "status", "latency_ms", "retrieved", "used",
              "memory_turns", "vendors")


def list_logs(page: int = 0, size: int = 20, limit: Optional[int] = None,
              company_id: Optional[str] = None, status: Optional[str] = None) -> dict:
    ensure_schema()
    where, args = [], []
    if company_id: where.append("company_id = %s"); args.append(company_id)
    if status:     where.append("status = %s");     args.append(status)
    clause = (" WHERE " + " AND ".join(where)) if where else ""
    cols = ", ".join(_LIST_COLS)
    with _pg() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        if limit:
            cur.execute(f"SELECT {cols} FROM cef_chat_request_log{clause} ORDER BY created_dt DESC LIMIT %s",
                        args + [min(int(limit), 5000)])
            items = cur.fetchall()
            return {"mode": "client", "limit": int(limit), "count": len(items), "items": items}
        size = max(1, min(int(size), 100)); page = max(0, int(page))
        cur.execute(f"SELECT COUNT(*) AS c FROM cef_chat_request_log{clause}", args)
        total = cur.fetchone()["c"]
        cur.execute(f"SELECT {cols} FROM cef_chat_request_log{clause} ORDER BY created_dt DESC "
                    f"LIMIT %s OFFSET %s", args + [size, page * size])
        items = cur.fetchall()
    return {"mode": "server", "page": page, "size": size, "total": total,
            "totalPages": (total + size - 1) // size, "count": len(items), "items": items}


def get_log(log_id: str) -> Optional[dict]:
    ensure_schema()
    with _pg() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM cef_chat_request_log WHERE id = %s", [log_id])
        return cur.fetchone()
