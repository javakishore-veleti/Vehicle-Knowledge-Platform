from typing import Optional

from pydantic import BaseModel


class InputCheckReq(BaseModel):
    text: str
    sessionId: str
    queryId: Optional[str] = None
    userType: str = "GUEST"      # GUEST | AUTH
    userId: Optional[str] = None
    framework: Optional[str] = None
    store: Optional[str] = None


class OutputCheckReq(BaseModel):
    answer: str
    sessionId: str
    queryId: str
    userType: str = "GUEST"
    userId: Optional[str] = None
    numSources: int = 0


class FeedbackReq(BaseModel):
    rating: str                 # "up" | "down"
    queryId: Optional[str] = None
    sessionId: Optional[str] = None
    userType: str = "GUEST"
    userId: Optional[str] = None
    provider: Optional[str] = None
    comment: Optional[str] = None
