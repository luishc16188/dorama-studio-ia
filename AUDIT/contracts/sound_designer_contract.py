from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class SoundDesignerInput(BaseModel):
    """Input schema for SoundDesignerAgent."""
    state: dict[str, Any] = Field(..., description="Current pipeline state")
    episode_spec: dict[str, Any] = Field(..., description="Episode specification")
    sfx_requirements: List[dict[str, Any]] = Field(..., description="SFX requirements per shot")
    music_cues: Optional[List[str]] = Field(None, description="Music cues needed")
    ambient_requirements: Optional[dict[str, Any]] = Field(None, description="Ambient sound requirements")

class SoundDesignerOutput(BaseModel):
    """Output schema for SoundDesignerAgent."""
    state: dict[str, Any] = Field(..., description="Updated pipeline state")
    sfx_layers: List[dict[str, Any]] = Field(..., description="SFX layers generated")
    sfx_id: str = Field(..., description="Unique SFX identifier")
    ambient_sound: Optional[dict[str, Any]] = Field(None, description="Ambient sound configuration")
    confidence: float = Field(0.0, description="Confidence score 0.0-1.0")
    estimated_tokens: int = Field(2000, description="Estimated token usage")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")

class SoundDesignerError(BaseModel):
    """Error schema for SoundDesignerAgent."""
    error_code: str = Field(SoundDesignerErrorCodes.SFX_GENERATION_FAILED, description="Error code identifier")
    error_message: str = Field(..., description="Human-readable error message")
    context: Optional[dict[str, Any]] = Field(None, description="Context where error occurred")
    recoverable: bool = Field(True, description="Whether error is recoverable")
    suggested_approach: Optional[str] = Field(None, description="Suggested alternative approach")

# Error codes
class SoundDesignerErrorCodes:
    SFX_NOT_FOUND = "SD001"
    INSUFFICIENT_REQUIREMENTS = "SD002"
    CONSISTENCY_VIOLATION = "SD003"
    GENERATION_FAILED = "SD004"