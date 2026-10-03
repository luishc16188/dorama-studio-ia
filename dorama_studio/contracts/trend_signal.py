"""
Data contract for Trend Hunter → Viral Analyst transition
Based on AUTODIAGNOSTICO_SISTEMA.md Transition 1
"""

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class SaturationLevel(str, Enum):
    EMERGING = "emerging"
    GROWING = "growing"
    MATURE = "mature"
    DECLINING = "declining"


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class TrendSignal(BaseModel):
    """Output from Trend Hunter (Agent 1) - Input to Viral Analyst (Agent 2)"""

    trend_id: str = Field(pattern=r"^TR-\d{4}-\d{6}$")
    trend: str = Field(min_length=10, max_length=200)
    growth_rate_pct: float = Field(ge=0, le=1000)
    sentiment: Sentiment
    competitor_insight: str = Field(min_length=20, max_length=500)
    saturation_level: SaturationLevel
    source_platforms: list[
        Literal["tiktok", "youtube", "instagram", "reddit", "twitter"]
    ]
    keywords: list[str] = Field(min_length=1, max_length=10)
    demographic_hint: str | None = Field(default=None, max_length=100)
    detected_at: datetime = Field(default_factory=datetime.now)

    @model_validator(mode="after")
    def validate_growth_consistency(self):
        """Growth rate should match saturation level"""
        if (
            self.saturation_level == SaturationLevel.DECLINING
            and self.growth_rate_pct > 10
        ):
            raise ValueError("Declining trend cannot have high growth rate")
        if (
            self.saturation_level == SaturationLevel.EMERGING
            and self.growth_rate_pct < 5
        ):
            raise ValueError("Emerging trend should have at least 5% growth")
        return self

    def to_viral_analyst_prompt(self) -> str:
        """Format for Viral Analyst input"""
        return (
            f"TREND: {self.trend}\n"
            f"ID: {self.trend_id}\n"
            f"GROWTH: {self.growth_rate_pct:.1f}%\n"
            f"SENTIMENT: {self.sentiment.value}\n"
            f"SATURATION: {self.saturation_level.value}\n"
            f"COMPETITOR INSIGHT: {self.competitor_insight}\n"
            f"PLATFORMS: {', '.join(self.source_platforms)}\n"
            f"KEYWORDS: {', '.join(self.keywords)}"
        )


class ViralPotential(BaseModel):
    """Output from Viral Analyst (Agent 2)"""

    trend_id: str
    viral_score: int = Field(ge=0, le=100)
    hook_categories: list[
        Literal[
            "revelation",
            "threat",
            "betrayal",
            "humiliation",
            "power",
            "identity",
            "prohibition",
            "mystery",
            "impossible_romance",
            "revenge",
            "visual_shock",
            "question",
        ]
    ] = Field(min_length=1, max_length=3)
    target_demographic: str = Field(min_length=5)
    estimated_reach: int = Field(ge=0)
    confidence: float = Field(ge=0, le=1)
    key_angles: list[str] = Field(min_length=2, max_length=5)
    risk_factors: list[str] = Field(max_length=3)
    recommended_format: Literal[
        "vertical_15s", "vertical_30s", "vertical_60s", "vertical_90s"
    ]
