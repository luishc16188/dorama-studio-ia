from typing import Any

from pydantic import BaseModel


class ViralAnalystInput(BaseModel):
    trend_signal: dict[str, Any]
    historical_data: list[dict[str, Any]] | None = None


class ViralAnalystOutput(BaseModel):
    trend_id: str
    viral_score: int
    hook_categories: list[str]
    target_demographic: str
    estimated_reach: int
    confidence: float
    key_angles: list[str]
    risk_factors: list[str]
    recommended_format: str
    status: str
