from typing import Any

from pydantic import BaseModel


class AudioEngineerInput(BaseModel):
    episode_num: int
    beats: list[dict[str, Any]]
    master_script: dict[str, Any] = {}
    breakdown: dict[str, Any] = {}


class AudioPromptOutput(BaseModel):
    beat_name: str
    beat_index: int
    ambience: str
    sfx_layers: list[dict[str, Any]]
    music: dict[str, Any]
    silence_drop: bool
    sub_bass_stinger: bool
    voice_processing: str
    notes: str


class AudioEngineerOutput(BaseModel):
    audio_prompts: list[AudioPromptOutput]
    status: str
