"""Agent-SDK framework integrations. Importing this package registers every framework's stages.
Add new frameworks here as they're implemented (google_adk, msagent, strands)."""
from . import openai_agents  # noqa: F401  (registers openai-agents:search)
