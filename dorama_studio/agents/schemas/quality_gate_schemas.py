from typing import Any

from pydantic import BaseModel


class QualityGateInput(BaseModel):
    episode_num: int
    episode_score: float
    breakdown: dict[str, Any] | None = None
    feedback: list[str] | None = None
    threshold: float = 85.0


class QualityGateOutput(BaseModel):
    verdict: str
    passed: bool
    score: float
    threshold: float
    notes: list[str] = []
    status: str
