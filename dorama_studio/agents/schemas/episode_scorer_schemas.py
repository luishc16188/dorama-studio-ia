from typing import Any

from pydantic import BaseModel


class EpisodeScorerInput(BaseModel):
    episode_num: int
    episode_package: dict[str, Any]
    score_breakdown: dict[str, Any] | None = None


class EpisodeScorerOutput(BaseModel):
    episode_score: float
    verdict: str
    breakdown: dict[str, Any]
    feedback: list[str]
