from typing import Any

from pydantic import BaseModel


class OriginalityEngineInput(BaseModel):
    viral_potential: dict[str, Any]
    creative_genome: dict[str, Any] | None = None
    mutation_budget: dict[str, float] | None = None


class OriginalityEngineOutput(BaseModel):
    is_original: bool
    cliche_score: float
    novelty_score: float
    detected_cliches: list[str]
    mutation_suggestions: list[str]
    mechanism_extracted: str
    mutation_budget_allocation: dict[str, float]
    status: str
