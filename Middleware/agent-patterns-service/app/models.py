"""Pydantic request/response contracts — uniform across every (pattern × framework) cell."""
from typing import Optional

from pydantic import BaseModel


class RunReq(BaseModel):
    input: str                         # the question / task for the pattern
    useCase: Optional[str] = None      # selects a concrete VKP use case (e.g. 'chunk-quality-review')
    maxIterations: int = 1             # for looping patterns (reflection, evaluator-optimizer)


class RunResp(BaseModel):
    pattern: str
    framework: str
    input: str
    useCase: Optional[str] = None
    answer: Optional[str] = None
    draft: Optional[str] = None
    critique: Optional[str] = None
    steps: Optional[list] = None
    iterations: int = 1
    model: Optional[str] = None
    ok: bool = True
    error: Optional[str] = None
    latencyMs: Optional[int] = None
