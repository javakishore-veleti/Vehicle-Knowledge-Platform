"""Reflection / Reflexion — generate -> self-critique -> revise — across all frameworks.
Each import registers one (reflection, <framework>) cell. SDK imports are lazy (inside run())."""
from . import langgraph, crewai, llamaindex, haystack, openai_agents, google_adk, msagent, strands  # noqa: F401
