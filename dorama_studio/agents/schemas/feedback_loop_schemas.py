from typing import Any

from pydantic import BaseModel


class FeedbackLoopInput(BaseModel):
    episode_num: int
    feedback_data: dict[str, Any]
    learning_context: dict[str, Any] | None = None


class FeedbackLoopOutput(BaseModel):
    feedback_insights: dict[str, Any]
    status: str
    improvements: list[str] = []
