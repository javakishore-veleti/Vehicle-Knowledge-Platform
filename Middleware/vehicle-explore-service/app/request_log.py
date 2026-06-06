"""Per-request telemetry ledger for vehicle search — `veh_search_request_log` (Postgres, jsonb-heavy).

Every search writes one richly-detailed row capturing *what happened*: the input params, where the
request originated (which "Try" chip / search button / URL deep-link), the full tech stack, the DB
tables + indexes touched, the LLMs + 3rd-party vendors invoked, the ordered flow steps (which drive
the UI flow diagram), guardrail verdicts, and a result summary. Scalar columns are indexed for
server-side pagination/filtering; everything else lives in jsonb columns.

The list/detail APIs back the portal's "Search Logs" pages: server-side pagination (?page&size) and
a latest-N client-side mode (?limit). Recording is best-effort — it never breaks a search.
"""
from typing import Optional

import psycopg2
from psycopg2.extras import Json, RealDictCursor

from . import config

_ready = False


def _pg():
    return psycopg2.connect(host=config.PG_HOST, port=config.PG_PORT, dbname=config.PG_DB,
                            user=config.PG_USER, password=config.PG_PASSWORD)


def ensure_schema() -> None:
    """Idempotently create the table + indexes (jsonb columns for the rich 'what happened' detail)."""
    global _ready
    if _ready:
        return
    with _pg() as conn, conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS veh_search_request_log (
                id            TEXT PRIMARY KEY,
                created_dt    TIMESTAMPTZ NOT NULL DEFAULT now(),
                title         TEXT,
                description   TEXT,
                query         TEXT,
                store         TEXT,
                mode          TEXT,
                framework     TEXT,
                origin_source TEXT,
                llm_enabled   BOOLEAN,
                status        TEXT,
                latency_ms    INTEGER,
                result_count  INTEGER,
                session_id    TEXT,
                user_type     TEXT,
                -- jsonb: as much structured "what happened" as possible --
                request_params  JSONB,
                request_origin  JSONB,
                tech_stack      JSONB,
                db_tables       JSONB,
                indexes         JSONB,
                llms            JSONB,
                vendors         JSONB,
                guardrails      JSONB,
                steps           JSONB,
                result_summary  JSONB,
                answer          JSONB
            )
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS veh_log_created_idx   ON veh_search_request_log (created_dt DESC)")
        cur.execute("CREATE INDEX IF NOT EXISTS veh_log_store_idx     ON veh_search_request_log (store)")
        cur.execute("CREATE INDEX IF NOT EXISTS veh_log_framework_idx ON veh_search_request_log (framework)")
        cur.execute("CREATE INDEX IF NOT EXISTS veh_log_status_idx    ON veh_search_request_log (status)")
    _ready = True


# --- vendor map: provider id -> 3rd-party vendor name (for the vendors jsonb) ---
_VENDOR = {
    "openai": "OpenAI", "groq-70b": "Groq", "groq-8b": "Groq", "hf": "Hugging Face",
    "google": "Google", "anthropic": "Anthropic", "bedrock": "AWS Bedrock",
}


def build(*, query: str, store: str, mode: str, framework: str, query_id: str, session_id: str,
          user_type: str, llm_enabled: bool, top_k: int, providers_requested, company_id,
          origin: Optional[dict], results: list, answers: list, answer: str, answer_source: str,
          guardrails: dict, latency_ms: int) -> dict:
    """Assemble the full telemetry record (all the jsonb fields + the flow steps for the diagram)."""
    embed_vendor = "OpenAI" if config.EMBED_PROVIDER == "openai" else "local (sentence-transformers via fastembed)"
    gin = (guardrails or {}).get("input") or {}
    gout = (guardrails or {}).get("output") or {}

    # --- LLMs invoked (per provider, with tokens/cost/latency) ---
    llms = [{
        "provider": a.get("provider"), "label": a.get("label"), "model": a.get("model"),
        "ok": bool(a.get("ok")), "promptTokens": a.get("promptTokens"),
        "completionTokens": a.get("completionTokens"), "totalTokens": a.get("totalTokens"),
        "costUsd": a.get("costUsd"), "latencyMs": a.get("latencyMs"), "error": a.get("error"),
    } for a in (answers or [])]

    # --- 3rd-party vendors invoked ---
    vendors = []
    seen = set()
    for a in (answers or []):
        v = _VENDOR.get(a.get("provider"))
        if v and v not in seen:
            seen.add(v)
            vendors.append({"name": v, "kind": "LLM API", "via": a.get("provider"),
                            "role": "answer generation", "ok": bool(a.get("ok"))})
    vendors.append({"name": embed_vendor, "kind": "embeddings",
                    "role": f"query embedding ({config.EMBED_MODEL})", "ok": mode != "fts"})
    vendors.append({"name": "guardrails-service", "kind": "safety",
                    "role": "input/output content checks", "ok": True})

    # --- tech stack ---
    tech_stack = [
        {"layer": "frontend", "tech": "Angular 19 (vehicle-search-portal)"},
        {"layer": "api", "tech": "FastAPI (vehicle-explore-service :8090)"},
        {"layer": "agent-framework", "tech": framework},
        {"layer": "embeddings", "tech": f"{config.EMBED_PROVIDER} · {config.EMBED_MODEL}"},
        {"layer": "vector-store", "tech": "pgVector (Postgres)" if store == "pgvector" else "MongoDB Atlas Vector Search"},
        {"layer": "retrieval-mode", "tech": mode},
        {"layer": "llm", "tech": ", ".join(sorted({a.get("model") for a in (answers or []) if a.get("model")})) or "extractive (no LLM)"},
        {"layer": "guardrails", "tech": "guardrails-service (LLM Guard / Groq safeguard)"},
        {"layer": "telemetry", "tech": "Prometheus + OpenTelemetry (Jaeger)"},
    ]

    # --- DB tables touched ---
    if store == "pgvector":
        db_tables = [{"name": config.VECTOR_TABLE, "db": "postgres", "role": "vector embeddings", "op": "SELECT"}]
    else:
        db_tables = [{"name": "vkp_chunks", "db": "mongodb", "role": "vector embeddings", "op": "find/$vectorSearch"}]
    db_tables += [
        {"name": "user_queries", "db": "postgres (guardrails-service)", "role": "guest/auth query ledger", "op": "INSERT"},
        {"name": "veh_search_request_log", "db": "postgres", "role": "this telemetry row", "op": "INSERT"},
    ]

    # --- indexes used ---
    if store == "pgvector":
        indexes = [
            {"name": f"{config.VECTOR_TABLE} (ivfflat/hnsw on embedding)", "table": config.VECTOR_TABLE,
             "type": "vector (cosine <=>)", "used": mode in ("vector", "hybrid")},
            {"name": f"{config.VECTOR_TABLE}_tsv_gin", "table": config.VECTOR_TABLE,
             "type": "GIN (full-text tsvector)", "used": mode in ("fts", "hybrid")},
        ]
    else:
        indexes = [{"name": "vkp_vector_index", "table": "vkp_chunks", "type": "Atlas vectorSearch", "used": True}]

    # --- ordered flow steps (drive the UI flow diagram) ---
    steps = []
    n = [0]
    def step(key, label, typ, status="ok", ms=None, detail=None):
        n[0] += 1
        steps.append({"n": n[0], "key": key, "label": label, "type": typ,
                      "status": status, "ms": ms, "detail": detail or {}})

    osrc = (origin or {}).get("source") or "url"
    step("request", "Request received", "request", "ok", None,
         {"origin": osrc, "label": (origin or {}).get("label"), "query": query})
    step("guardrail_in", "Input guardrail", "guardrail",
         "ok" if gin.get("allowed", True) else "blocked", None,
         {"allowed": gin.get("allowed", True), "queryId": query_id})
    if mode != "fts":
        step("embed", "Embed query", "embed", "ok", None,
             {"provider": config.EMBED_PROVIDER, "model": config.EMBED_MODEL, "vendor": embed_vendor})
    step("retrieve", f"{mode} retrieval", "retrieve", "ok", None,
         {"store": store, "mode": mode,
          "table": config.VECTOR_TABLE if store == "pgvector" else "vkp_chunks",
          "topK": top_k, "found": len(results or [])})
    if llm_enabled and answers:
        for a in answers:
            step(f"llm_{a.get('provider')}", f"LLM · {a.get('label') or a.get('provider')}", "llm",
                 "ok" if a.get("ok") else "error", a.get("latencyMs"),
                 {"model": a.get("model"), "vendor": _VENDOR.get(a.get("provider")),
                  "totalTokens": a.get("totalTokens"), "costUsd": a.get("costUsd"), "error": a.get("error")})
    else:
        step("extractive", "Extractive answer (no LLM)", "answer", "ok", None, {})
    step("guardrail_out", "Output guardrail", "guardrail", "ok", None,
         {"checked": (gout or {}).get("checked"), "blocked": (gout or {}).get("blocked")})
    step("answer", "Answer returned", "answer",
         "blocked" if answer_source == "blocked" else "ok", None,
         {"answerSource": answer_source, "sources": len(results or [])})
    step("persist", "Telemetry persisted", "store", "ok", None, {"table": "veh_search_request_log"})

    # --- result summary ---
    scored = sorted(results or [], key=lambda r: r.get("score") or 0, reverse=True)
    hosts = []
    for r in scored:
        u = r.get("sourceUrl") or ""
        h = u.split("/")[2] if "://" in u else u
        if h and h not in hosts:
            hosts.append(h)
    result_summary = {
        "count": len(results or []),
        "topScore": round(scored[0]["score"], 4) if scored and scored[0].get("score") is not None else None,
        "hosts": hosts[:8],
        "sources": [{"url": r.get("sourceUrl"), "score": r.get("score")} for r in scored[:8]],
    }

    models = sorted({a.get("model") for a in (answers or []) if a.get("ok") and a.get("model")})
    llm_part = f" · LLM: {', '.join(models)}" if models else " · extractive"
    title = f"{mode} search “{(query or '')[:48]}” on {store} via {framework}{llm_part}"
    description = (
        f"{framework} ran a {mode} search over {store} "
        f"({config.VECTOR_TABLE if store == 'pgvector' else 'vkp_chunks'}), "
        f"retrieved {len(results or [])} source(s)"
        + (f", answered by {len(models)} LLM provider(s) [{', '.join(models)}]" if models else ", extractive answer")
        + f". Origin: {osrc}. Result: {answer_source}."
    )

    return {
        "id": query_id, "title": title, "description": description, "query": query, "store": store,
        "mode": mode, "framework": framework, "origin_source": osrc, "llm_enabled": llm_enabled,
        "status": answer_source, "latency_ms": latency_ms, "result_count": len(results or []),
        "session_id": session_id, "user_type": user_type,
        "request_params": {"query": query, "store": store, "mode": mode, "topK": top_k,
                           "useLlm": llm_enabled, "providers": providers_requested, "companyId": company_id,
                           "framework": framework},
        "request_origin": origin or {"source": "url"},
        "tech_stack": tech_stack, "db_tables": db_tables, "indexes": indexes, "llms": llms,
        "vendors": vendors, "guardrails": guardrails or {}, "steps": steps,
        "result_summary": result_summary,
        "answer": {"source": answer_source, "text": answer,
                   "providers": [{"provider": a.get("provider"), "label": a.get("label"),
                                  "ok": bool(a.get("ok"))} for a in (answers or [])]},
    }


_JSONB = ("request_params", "request_origin", "tech_stack", "db_tables", "indexes", "llms",
          "vendors", "guardrails", "steps", "result_summary", "answer")
_SCALAR = ("id", "title", "description", "query", "store", "mode", "framework", "origin_source",
           "llm_enabled", "status", "latency_ms", "result_count", "session_id", "user_type")


def record(rec: dict) -> None:
    """Insert one telemetry row (best-effort; swallows errors so a search never fails on logging)."""
    try:
        ensure_schema()
        cols = list(_SCALAR) + list(_JSONB)
        vals = [rec.get(c) for c in _SCALAR] + [Json(rec.get(c)) for c in _JSONB]
        placeholders = ", ".join(["%s"] * len(cols))
        with _pg() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO veh_search_request_log ({', '.join(cols)}) VALUES ({placeholders}) "
                f"ON CONFLICT (id) DO NOTHING",
                vals,
            )
    except Exception:  # noqa: BLE001 — telemetry must never break search
        pass


# Compact projection for the list view (no heavy jsonb except small chips).
_LIST_COLS = ("id", "created_dt", "title", "query", "store", "mode", "framework", "origin_source",
              "llm_enabled", "status", "latency_ms", "result_count", "vendors")


def list_logs(page: int = 0, size: int = 20, limit: Optional[int] = None,
              store: Optional[str] = None, framework: Optional[str] = None,
              status: Optional[str] = None) -> dict:
    """Server-side page (?page&size) OR latest-N for client-side paging (?limit)."""
    ensure_schema()
    where, args = [], []
    if store:     where.append("store = %s");     args.append(store)
    if framework: where.append("framework = %s"); args.append(framework)
    if status:    where.append("status = %s");    args.append(status)
    clause = (" WHERE " + " AND ".join(where)) if where else ""
    cols = ", ".join(_LIST_COLS)
    with _pg() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        if limit:  # client-side mode: latest N, no offset paging
            cur.execute(f"SELECT {cols} FROM veh_search_request_log{clause} ORDER BY created_dt DESC LIMIT %s",
                        args + [min(int(limit), 5000)])
            items = cur.fetchall()
            return {"mode": "client", "limit": int(limit), "count": len(items), "items": items}
        size = max(1, min(int(size), 100))
        page = max(0, int(page))
        cur.execute(f"SELECT COUNT(*) AS c FROM veh_search_request_log{clause}", args)
        total = cur.fetchone()["c"]
        cur.execute(f"SELECT {cols} FROM veh_search_request_log{clause} ORDER BY created_dt DESC "
                    f"LIMIT %s OFFSET %s", args + [size, page * size])
        items = cur.fetchall()
    return {"mode": "server", "page": page, "size": size, "total": total,
            "totalPages": (total + size - 1) // size, "count": len(items), "items": items}


def get_log(log_id: str) -> Optional[dict]:
    """Full row (all jsonb) for the detail + dynamic flow-diagram page."""
    ensure_schema()
    with _pg() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM veh_search_request_log WHERE id = %s", [log_id])
        return cur.fetchone()
