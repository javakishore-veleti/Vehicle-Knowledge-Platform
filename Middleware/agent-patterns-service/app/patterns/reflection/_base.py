"""Shared prompts + helpers for the Reflection pattern, reused by every framework cell so the cells
differ ONLY in framework mechanics (the point of the comparison)."""

DRAFT_SYS = ("You are a precise automotive expert. Answer the user's vehicle question concisely and "
             "factually. Avoid hallucinated specs or prices.")

CRITIC_SYS = ("You are a meticulous fact critic for automotive answers. Find inaccuracies, missing "
              "context, and unsupported claims.")

CRITIQUE = ("Critique the ANSWER to the QUESTION for factual accuracy, completeness, and any unsupported "
            "claims. Reply with a short bullet list of concrete fixes, or 'No changes needed.'\n\n"
            "QUESTION: {q}\nANSWER: {a}")

REVISE = ("Revise the ANSWER using the CRITIQUE. Return ONLY the improved answer — no preamble.\n\n"
          "QUESTION: {q}\nANSWER: {a}\nCRITIQUE: {c}")


def result(draft: str, critique: str, answer: str) -> dict:
    """Uniform return shape for every reflection cell."""
    return {"draft": draft, "critique": critique, "answer": answer}
