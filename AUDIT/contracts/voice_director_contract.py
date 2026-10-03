from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class VoiceDirectorInput(BaseModel):
    """Input schema for VoiceDirectorAgent."""
    state: dict[str, Any] = Field(..., description="Current pipeline state")
    episode_spec: dict[str, Any] = Field(..., description="Episode specification")
    character_state_refs: Dict[str, str] = Field(..., description="Character state references from CharacterDirector")
    dialogue_lines: List[dict[str, Any]] = Field(..., description="Dialogue lines to direct")
    scene_context: dict[str, Any] = Field(..., description="Scene context for voice direction")
    emotional_target: str = Field(..., description="Emotional target for voice performance")

class VoiceDirectorOutput(BaseModel):
    """Output schema for VoiceDirectorAgent."""
    state: dict[str, Any] = Field(..., description="Updated pipeline state")
    voice_directions: List[dict[str, Any]] = Field(..., description="Voice direction instructions")
    voice_id: str = Field(..., description="Selected voice ID")
    lip_sync_timestamps: Dict[str, Any] = Field(default_factory=dict, description="Lip sync timing")
    emotional_notes: Dict[str, Any] = Field(default_factory=dict, description="Emotional performance notes")
    confidence: float = Field(0.0, description="Confidence score 0.0-1.0")
    estimated_tokens: int = Field(2500, description="Estimated token usage")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")

class VoiceDirectorError(BaseModel):
    """Error schema for VoiceDirectorAgent."""
    error_code: str = Field(VoiceDirectorErrorCodes.VOICE_DIRECTION_FAILED, description="Error code identifier")
    error_message: str = Field(..., description="Human-readable error message")
    context: Optional[dict[str, Any]] = Field(None, description="Context where error occurred")
    recoverable: bool = Field(True, description="Whether error is recoverable")
    suggested_approach: Optional[str] = Field(None, description="Suggested alternative approach")

# Error codes
class VoiceDirectorErrorCodes:
    CHARACTER_NOT_FOUND = "VD001"
    INSUFFICIENT_DIALOGUE = "VD002"
    EMOTIONAL_CONTEXT_MISSING = "VD003"
    VOICE_NOT_AVAILABLE = "VD004"
    LIP_SYNC_FAILED = "VD005"