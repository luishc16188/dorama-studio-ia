from datetime import datetime
from typing import Any

from pydantic import BaseModel


class TrendHunterInput(BaseModel):
    regions: list[str] = ["global"]
    languages: list[str] = ["es", "en"]
    time_window_hours: int = 24


class TrendHunterOutput(BaseModel):
    trend_signal: dict[str, Any]
    status: str
    generated_at: datetime
