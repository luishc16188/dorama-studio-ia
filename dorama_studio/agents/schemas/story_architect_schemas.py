from typing import Any

from pydantic import BaseModel


class StoryArchitectInput(BaseModel):
    viral_potential: dict[str, Any]
    originality_report: dict[str, Any]


class StoryArchitectOutput(BaseModel):
    beat_hook: str
    beat_promise: str
    beat_question: str
    beat_escalation: str
    beat_reward: str
    beat_question2: str
    beat_cliffhanger: str
    narrative_mechanism: str
    emotional_arc: str
    beat_ratings: dict[str, float]
    total_narrative_score: float
    status: str
