from typing import Any

from pydantic import BaseModel


class DistributionInput(BaseModel):
    episode_num: int
    video_prompts: list[dict[str, Any]]
    audio_prompts: list[dict[str, Any]]
    sfx_cues: list[dict[str, Any]]
    platform: str


class DistributionOutput(BaseModel):
    distribution_packages: dict[str, Any]
    status: str
    platforms_covered: list[str]
