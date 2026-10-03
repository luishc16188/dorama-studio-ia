from typing import Any

from pydantic import BaseModel


class SFXDesignerInput(BaseModel):
    episode_num: int
    master_script: dict[str, Any]
    audio_direction: dict[str, Any]


class SFXDesignerOutput(BaseModel):
    sfx_cues: list[dict[str, Any]]
    status: str
    total_sfx: int
