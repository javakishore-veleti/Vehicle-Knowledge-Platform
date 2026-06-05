"""Runtime config (env-overridable). Mirrors the explore service's datastore defaults so the
agentic frameworks query the SAME indexed pgvector tables."""
import os

# --- pgVector (the indexed chunks produced by the indexing subsystem) ---
PG_HOST = os.getenv("VKP_PG_HOST", "localhost")
PG_PORT = int(os.getenv("VKP_PG_PORT", "5432"))
PG_DB = os.getenv("VKP_PG_DB", "vkp")
PG_USER = os.getenv("VKP_PG_USER", "vkp")
PG_PASSWORD = os.getenv("VKP_PG_PASSWORD", "vkp")

# Query embedding must match the indexed table's model (default: local minilm 384d).
EMBED_PROVIDER = os.getenv("VKP_EMBED_PROVIDER", "sentence-transformers")
EMBED_MODEL = os.getenv("VKP_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
VECTOR_TABLE = os.getenv("VKP_VECTOR_TABLE", "vec_all_minilm_l6_v2")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Which model the agent SDKs talk to. Prefer OpenAI if a key is present, else free Groq (most SDKs
# accept an OpenAI-compatible base_url). Groq's OpenAI-compatible endpoint:
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = os.getenv("VKP_AGENT_GROQ_MODEL", "llama-3.3-70b-versatile")
OPENAI_MODEL = os.getenv("VKP_AGENT_OPENAI_MODEL", "gpt-4o-mini")
