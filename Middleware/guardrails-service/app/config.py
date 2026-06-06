"""Guardrails service config (env-overridable)."""
import os

# Postgres (the query ledger lives here).
PG_HOST = os.getenv("VKP_PG_HOST", "localhost")
PG_PORT = int(os.getenv("VKP_PG_PORT", "5432"))
PG_DB = os.getenv("VKP_PG_DB", "postgres")          # single `postgres` database; tables live in a schema
PG_USER = os.getenv("VKP_PG_USER", "vkp")
PG_PASSWORD = os.getenv("VKP_PG_PASSWORD", "vkp")
PG_SCHEMA = os.getenv("VKP_PG_SCHEMA", "vkp_guardrails")
PG_OPTIONS = f"-c search_path={PG_SCHEMA},public"

# Guardrail engine: rules (built-in, always works) | llmguard (protectai/llm-guard) | groq (Llama Guard).
# "auto" = use llmguard if importable, else rules.
ENGINE = os.getenv("VKP_GUARDRAILS_ENGINE", "auto")

# Limits / thresholds.
MAX_QUERY_CHARS = int(os.getenv("VKP_GUARDRAILS_MAX_CHARS", "2000"))

# Groq (for the optional Llama-Guard engine).
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_GUARD_MODEL = os.getenv("VKP_GROQ_GUARD_MODEL", "openai/gpt-oss-safeguard-20b")
