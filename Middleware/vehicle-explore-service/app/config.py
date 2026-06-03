"""Runtime config (env-overridable). Defaults match the localhost pgVector + minilm setup."""
import os

# --- pgVector (default store) ---
PG_HOST = os.getenv("VKP_PG_HOST", "localhost")
PG_PORT = int(os.getenv("VKP_PG_PORT", "5432"))
PG_DB = os.getenv("VKP_PG_DB", "vkp")
PG_USER = os.getenv("VKP_PG_USER", "vkp")
PG_PASSWORD = os.getenv("VKP_PG_PASSWORD", "vkp")

# --- MongoDB Atlas Vector Search (alternative store) ---
MONGO_URI = os.getenv("VKP_MONGO_URI", "mongodb://localhost:27017/vkp?directConnection=true")
MONGO_DB = os.getenv("VKP_MONGO_DB", "vkp")
MONGO_VECTOR_INDEX = os.getenv("VKP_MONGO_VECTOR_INDEX", "vkp_vector_index")

# The query must be embedded with the SAME provider+model whose vectors fill the table/collection.
#   sentence-transformers -> fastembed local (default; vec_all_minilm_l6_v2, 384d)
#   openai                -> OpenAI embeddings (text-embedding-3-small -> vec_text_embedding_3_small, 1536d)
EMBED_PROVIDER = os.getenv("VKP_EMBED_PROVIDER", "sentence-transformers")
EMBED_MODEL = os.getenv("VKP_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
VECTOR_TABLE = os.getenv("VKP_VECTOR_TABLE", "vec_all_minilm_l6_v2")

# Default store when the request doesn't specify one: pgvector | mongodb.
DEFAULT_STORE = os.getenv("VKP_VECTOR_STORE", "pgvector")

# --- LLM answer (optional; falls back to extractive on any error / missing key) ---
# Provider is pluggable via the OpenAI-compatible API: default is OpenAI, but pointing
# VKP_LLM_BASE_URL + VKP_LLM_API_KEY at Groq/Azure/etc. works unchanged.
LLM_ENABLED = os.getenv("VKP_LLM_ENABLED", "true").lower() in ("1", "true", "yes")
LLM_MODEL = os.getenv("VKP_LLM_MODEL", "gpt-4o-mini")
LLM_BASE_URL = os.getenv("VKP_LLM_BASE_URL", "")          # empty -> OpenAI default endpoint
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_API_KEY = os.getenv("VKP_LLM_API_KEY", "") or OPENAI_API_KEY
