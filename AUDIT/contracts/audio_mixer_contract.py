from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class AudioMixerInput(BaseModel):
    """Input schema for AudioMixerAgent."""
    state: dict[str, Any] = Field(..., description="Current pipeline state")
    voice_tracks: dict[str, Any] = Field(..., description="Voice tracks from VoiceDirector")
    sfx_layers: dict[str, Any] = Field(..., description="SFX layers from SoundDesigner")
    music_timeline: dict[str, Any] = Field(..., description="Music timeline from MusicSupervisor")
    mix_parameters: Optional[dict[str, Any]] = Field(None, description="Mix parameters (volume, balance, etc.)")

class AudioMixerOutput(BaseModel):
    """Output schema for AudioMixerAgent."""
    state: dict[str, Any] = Field(..., description="Updated pipeline state")
    master_audio: dict[str, Any] = Field(..., description="Master audio mix")
    mix_id: str = Field(..., description="Unique mix identifier")
    mix_duration: float = Field(0.0, description="Mix duration in seconds")
    confidence: float = Field(0.0, description="Confidence score 0.0-1.0")
    estimated_tokens: int = Field(1500, description="Estimated token usage")
    mixed_at: datetime = Field(default_factory=datetime.utcnow, description="Mix timestamp")

class AudioMixerError(BaseModel):
    """Error schema for AudioMixerAgent."""
    error_code: str = Field(AudioMixerErrorCodes.MIXING_FAILED, description="Error code identifier")
    error_message: str = Field(..., description="Human-readable error message")
    context: Optional[dict[str, Any]] = Field(None, description="Context where error occurred")
    recoverable: bool = Field(True, description="Whether error is recoverable")
    suggested_approach: Optional[str] = Field(None, description="Suggested alternative approach")

# Error codes
class AudioMixerErrorCodes:
    MISSING_TRACKS = "AM001"
    INCOMPATIBLE_FORMATS = "AM002"
    MIXING_ENGINE_ERROR = "AM003"
    LEVEL_OVERLOAD = "AM004"