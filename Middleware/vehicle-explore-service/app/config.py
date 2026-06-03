"""Runtime config (env-overridable). Defaults match the localhost pgVector + minilm setup."""
import os

PG_HOST = os.getenv("VKP_PG_HOST", "localhost")
PG_PORT = int(os.getenv("VKP_PG_PORT", "5432"))
PG_DB = os.getenv("VKP_PG_DB", "vkp")
PG_USER = os.getenv("VKP_PG_USER", "vkp")
PG_PASSWORD = os.getenv("VKP_PG_PASSWORD", "vkp")

# The query is embedded with the SAME model whose vectors fill the table below.
# Default: sentence-transformers/all-MiniLM-L6-v2 (384d) -> vec_all_minilm_l6_v2.
EMBED_MODEL = os.getenv("VKP_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
VECTOR_TABLE = os.getenv("VKP_VECTOR_TABLE", "vec_all_minilm_l6_v2")
