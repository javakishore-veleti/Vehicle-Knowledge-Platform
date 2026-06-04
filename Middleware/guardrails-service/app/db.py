"""Postgres query ledger: two tables — guest users and authenticated users.

Every query is keyed by query_id; the input check inserts the row, the output check updates it.
"""
import json
import logging

import psycopg2

from . import config

log = logging.getLogger("guardrails")

DDL_GUEST = """
CREATE TABLE IF NOT EXISTS user_queries_guest (
  query_id       TEXT PRIMARY KEY,
  session_id     TEXT NOT NULL,
  query_text     TEXT,
  framework      TEXT,
  store          TEXT,
  input_action   TEXT,
  input_reasons  JSONB,
  output_action  TEXT,
  output_reasons JSONB,
  created_dt     TIMESTAMPTZ DEFAULT now(),
  updated_dt     TIMESTAMPTZ DEFAULT now()
)"""

DDL_AUTH = """
CREATE TABLE IF NOT EXISTS user_queries_auth_user (
  query_id       TEXT PRIMARY KEY,
  session_id     TEXT NOT NULL,
  user_id        TEXT NOT NULL,
  query_text     TEXT,
  framework      TEXT,
  store          TEXT,
  input_action   TEXT,
  input_reasons  JSONB,
  output_action  TEXT,
  output_reasons JSONB,
  created_dt     TIMESTAMPTZ DEFAULT now(),
  updated_dt     TIMESTAMPTZ DEFAULT now()
)"""


def _conn():
    return psycopg2.connect(host=config.PG_HOST, port=config.PG_PORT, dbname=config.PG_DB,
                            user=config.PG_USER, password=config.PG_PASSWORD)


def init_db() -> None:
    with _conn() as c, c.cursor() as cur:
        cur.execute(DDL_GUEST)
        cur.execute(DDL_AUTH)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_uqg_session ON user_queries_guest(session_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_uqa_session ON user_queries_auth_user(session_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_uqa_user ON user_queries_auth_user(user_id)")


def _table(user_type: str) -> str:
    return "user_queries_auth_user" if (user_type or "").upper() == "AUTH" else "user_queries_guest"


def log_input(user_type, query_id, session_id, user_id, query_text, framework, store, action, reasons) -> None:
    t = _table(user_type)
    with _conn() as c, c.cursor() as cur:
        if t.endswith("auth_user"):
            cur.execute(
                f"INSERT INTO {t} (query_id, session_id, user_id, query_text, framework, store, input_action, input_reasons) "
                f"VALUES (%s,%s,%s,%s,%s,%s,%s,%s) "
                f"ON CONFLICT (query_id) DO UPDATE SET input_action=EXCLUDED.input_action, "
                f"input_reasons=EXCLUDED.input_reasons, updated_dt=now()",
                (query_id, session_id, user_id or "", query_text, framework, store, action, json.dumps(reasons)))
        else:
            cur.execute(
                f"INSERT INTO {t} (query_id, session_id, query_text, framework, store, input_action, input_reasons) "
                f"VALUES (%s,%s,%s,%s,%s,%s,%s) "
                f"ON CONFLICT (query_id) DO UPDATE SET input_action=EXCLUDED.input_action, "
                f"input_reasons=EXCLUDED.input_reasons, updated_dt=now()",
                (query_id, session_id, query_text, framework, store, action, json.dumps(reasons)))


def log_output(user_type, query_id, action, reasons) -> None:
    t = _table(user_type)
    with _conn() as c, c.cursor() as cur:
        cur.execute(f"UPDATE {t} SET output_action=%s, output_reasons=%s, updated_dt=now() WHERE query_id=%s",
                    (action, json.dumps(reasons), query_id))


def list_queries(user_type, session_id, limit=50) -> list[dict]:
    t = _table(user_type)
    with _conn() as c, c.cursor() as cur:
        cur.execute(f"SELECT query_id, query_text, input_action, output_action, created_dt FROM {t} "
                    f"WHERE session_id=%s ORDER BY created_dt DESC LIMIT %s", (session_id, limit))
        rows = cur.fetchall()
    return [{"queryId": r[0], "queryText": r[1], "inputAction": r[2], "outputAction": r[3],
             "createdDt": str(r[4])} for r in rows]
