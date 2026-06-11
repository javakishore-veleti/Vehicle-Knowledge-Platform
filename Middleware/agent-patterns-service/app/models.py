"""Pydantic request/response contracts — uniform across every (pattern × framework) cell."""
from typing import Optional

from pydantic import BaseModel


class RunReq(BaseModel):
    input: str                         # the question / task for the pattern
    maxIterations: int = 1             # for looping patterns (reflection, evaluator-optimizer)


class RunResp(BaseModel):
    pattern: str
    framework: str
    input: str
    answer: Optional[str] = None       # the final result of the pattern
    draft: Optional[str] = None        # intermediate (reflection/evaluator: the first attempt)
    critique: Optional[str] = None     # intermediate (reflection/evaluator: the critique)
    steps: Optional[list] = None       # intermediate (plan/react/tot: the plan or trace)
    iterations: int = 1
    model: Optional[str] = None
    ok: bool = True
    error: Optional[str] = None
    latencyMs: Optional[int] = None
