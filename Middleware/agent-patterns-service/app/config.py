"""Configuration for agent-patterns-service. LLM access mirrors the other VKP Python services:
OpenAI when OPENAI_API_KEY is set, else free Groq (OpenAI-compatible) when GROQ_API_KEY is set."""
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

PORT = int(os.getenv("PORT", "8094"))


def has_llm() -> bool:
    return bool(OPENAI_API_KEY or GROQ_API_KEY)


def model_name() -> str:
    """Human-readable name of the active chat model (for responses/telemetry)."""
    return OPENAI_MODEL if OPENAI_API_KEY else GROQ_MODEL
