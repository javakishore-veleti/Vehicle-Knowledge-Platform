"""AI framework router. The framework name is part of the URL
(/api/vehicle-explore/{framework}/search) so requests can route to different agent
implementations. 'langgraph' is the implemented retrieve->synthesize pipeline; the others are
registered but not yet implemented.
"""
from typing import Optional

from .search import search_chunks

IMPLEMENTED = {"langgraph"}
KNOWN = {"langgraph", "crewai", "llamaindex", "haystack"}


def synthesize_answer(query: str, results: list[dict]) -> str:
    """Extractive answer over the retrieved snippets.

    The vectors + snippets are framework-agnostic; an LLM-backed answer (OpenAI/Azure) can slot
    in here behind the same contract once a key/quota is available — kept extractive for now.
    """
    if not results:
        return "No relevant vehicle content was found for this query."
    top = " ".join(results[0]["snippet"].split())
    return f"Based on {len(results)} matching source(s): {top[:300]}"


def run(framework: str, query: str, company_id: Optional[str], top_k: int) -> tuple[str, list[dict]]:
    results = search_chunks(query, company_id, top_k)
    answer = synthesize_answer(query, results)
    return answer, results
