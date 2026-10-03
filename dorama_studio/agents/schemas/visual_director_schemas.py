from typing import Any

from pydantic import BaseModel


class VisualDirectorInput(BaseModel):
    universe: dict[str, Any]
    visual_requirements: dict[str, Any]
    episode_num: int


class VisualDirectorOutput(BaseModel):
    visual_direction: dict[str, Any]
    status: str
