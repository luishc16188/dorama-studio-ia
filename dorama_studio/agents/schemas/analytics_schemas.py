from typing import Any

from pydantic import BaseModel


class AnalyticsInput(BaseModel):
    episode_num: int
    distribution_packages: list[dict[str, Any]]
    released_episodes: list[dict[str, Any]]


class AnalyticsOutput(BaseModel):
    analytics_insights: dict[str, Any]
    status: str
