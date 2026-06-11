"""Shared CrewAI LLM config — OpenAI (key) or free Groq via litellm's 'groq/' prefix."""
from . import config


def crew_llm():
    from crewai import LLM
    if config.OPENAI_API_KEY:
        return LLM(model=config.OPENAI_MODEL, api_key=config.OPENAI_API_KEY)
    return LLM(model=f"groq/{config.GROQ_MODEL}", api_key=config.GROQ_API_KEY)
