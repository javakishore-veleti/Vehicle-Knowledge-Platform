"""Shared prompts + deterministic helpers for the Chaining / Parallelization pattern.

The 5 VKP use cases have different topologies, but their LLM prompts and their DETERMINISTIC steps
(clean, hash, section-split, sentence-chunk, majority vote) are framework-agnostic and must stay
identical across cells — so they live here. Each framework cell wires its own graph/crew around them.
"""
import hashlib
import re
from collections import Counter

# multi-provider fan-out: three "providers" with distinct system prompts.
PROVIDERS = [("concise", "Answer concisely."),
             ("detailed", "Answer with supporting detail."),
             ("cautious", "Answer cautiously and flag any uncertainty.")]
VOTER_SYS = "Answer the spec question with ONLY a short factual value."

CONSENSUS_PROMPT = "Compare these provider answers and give the consensus:\n\n{body}"
TITLE_PROMPT = "Give a short one-line title for this content:\n{c}"
SUMMARIZE_PROMPT = "Summarize in one sentence:\n{t}"
TRANSLATE_PROMPT = "Translate to English (return as-is if already English):\n{q}"

USE_CASES = ["multi-provider-fanout", "ingestion-chain", "sectioning", "voting", "translate-then-index"]
DEFAULT_UC = "multi-provider-fanout"


def clean_text(raw: str) -> str:
    return " ".join(raw.split())


def sha16(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def split_sections(q: str) -> list:
    secs = [s.strip() for s in re.split(r"\n+", q) if s.strip()]
    if len(secs) < 2:
        secs = [s.strip() for s in re.split(r"(?<=\.)\s+", q) if s.strip()]
    return secs[:4] or [q]


def split_sentences(text: str) -> list:
    return [c.strip() for c in re.split(r"(?<=\.)\s+", text) if c.strip()] or [text]


def majority(votes: list) -> str:
    norm = [v.strip().lower()[:60] for v in votes]
    return Counter(norm).most_common(1)[0][0]
