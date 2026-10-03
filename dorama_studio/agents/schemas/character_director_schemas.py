from typing import Any

from pydantic import BaseModel


class CharacterDirectorInput(BaseModel):
    character_bible: dict[str, Any]
    story_arc: dict[str, Any]
    episode_num: int | None = None


class CharacterDirectorOutput(BaseModel):
    character_direction: dict[str, Any]
    status: str
