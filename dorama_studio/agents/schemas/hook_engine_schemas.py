from typing import Any

from pydantic import BaseModel


class HookEngineInput(BaseModel):
    episode_num: int
    hook_category: str
    hook_strength: float = 0.5
    context_data: dict[str, Any] | None = None


class HookEngineOutput(BaseModel):
    hook_text: str
    hook_category: str
    hook_strength: float
    generated_at: str = ""
