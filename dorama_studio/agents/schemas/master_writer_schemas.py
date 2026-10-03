from typing import Any

from pydantic import BaseModel


class MasterWriterInput(BaseModel):
    episode_num: int
    narrative_intent: str
    hook_category: str
    characters: list[str] = []


class MasterWriterOutput(BaseModel):
    master_script: dict[str, Any]
    status: str
    generated_at: str = ""
