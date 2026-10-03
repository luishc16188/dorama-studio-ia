from typing import Any

from pydantic import BaseModel


class CTAWriterInput(BaseModel):
    episode_num: int
    cliffhanger_data: dict[str, Any]
    cta_type: str = "moral_dilemma"
    platform: str = "social_media"


class CTAWriterOutput(BaseModel):
    cta_text: str
    cta_type: str
    platform: str
    status: str
    generated_at: str = ""
