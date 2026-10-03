from typing import Any

from pydantic import BaseModel


class VideoAnimatorInput(BaseModel):
    episode_num: int
    master_script: dict[str, Any]
    visual_direction: dict[str, Any]
    animation_style: str = "cinematic"


class VideoAnimatorOutput(BaseModel):
    video_prompts: list[dict[str, Any]]
    status: str
    total_prompts: int
