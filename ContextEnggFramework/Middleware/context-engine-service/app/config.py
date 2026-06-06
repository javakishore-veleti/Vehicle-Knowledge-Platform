"""CEF runtime config (env-overridable). Reuses VKP's datastore + LLM defaults."""
import os

# --- pgVector (the same indexed chunks VKP retrieval reads). One `postgres` DB; tables in schemas. ---
PG_HOST = os.getenv("VKP_PG_HOST", "localhost")
PG_PORT = int(os.getenv("VKP_PG_PORT", "5432"))
PG_DB = os.getenv("VKP_PG_DB", "postgres")
PG_USER = os.getenv("VKP_PG_USER", "vkp")
PG_PASSWORD = os.getenv("VKP_PG_PASSWORD", "vkp")
PG_SCHEMA = os.getenv("VKP_PG_SCHEMA", "vkp_cef")              # cef_chat_request_log lives here
VECTOR_SCHEMA = os.getenv("VKP_VECTOR_SCHEMA", "vkp_vectors")  # shared vec_* table read for retrieval
PG_OPTIONS = f"-c search_path={PG_SCHEMA},{VECTOR_SCHEMA},public"
EMBED_PROVIDER = os.getenv("VKP_EMBED_PROVIDER", "sentence-transformers")
EMBED_MODEL = os.getenv("VKP_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
VECTOR_TABLE = os.getenv("VKP_VECTOR_TABLE", "vec_all_minilm_l6_v2")

# --- MongoDB (memory layer; optional — falls back to in-process memory) ---
MONGO_URI = os.getenv("VKP_MONGO_URI", "mongodb://localhost:27017/vkp?directConnection=true")
MONGO_DB = os.getenv("VKP_MONGO_DB", "vkp")
MEMORY_ENABLED = os.getenv("CEF_MEMORY_ENABLED", "true").lower() in ("1", "true", "yes")

# --- Reasoning (OpenAI preferred, else free Groq) ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
OPENAI_MODEL = os.getenv("CEF_OPENAI_MODEL", "gpt-4o-mini")
GROQ_MODEL = os.getenv("CEF_GROQ_MODEL", "llama-3.3-70b-versatile")

# --- Reasoning via the VKP agent roster (optional): when set, the reasoning layer routes to the
#     agentic-service instead of a direct LLM call, so any framework can be the reasoning engine. ---
AGENTIC_URL = os.getenv("CEF_AGENTIC_URL", "")            # e.g. http://localhost:8092
DEFAULT_FRAMEWORK = os.getenv("CEF_DEFAULT_FRAMEWORK", "openai-agents")

# --- Assembly budget (token-ish; we approximate by characters) ---
CONTEXT_CHAR_BUDGET = int(os.getenv("CEF_CONTEXT_CHAR_BUDGET", "6000"))
