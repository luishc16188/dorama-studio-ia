from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class EditorInput(BaseModel):
    """Input schema for EditorAgent."""
    state: dict[str, Any] = Field(..., description="Current pipeline state")
    shots: List[dict[str, Any]] = Field(..., description="Episode shots structure")
    video_artifacts: dict[str, Any] = Field(..., description="Video artifacts from VisualEngine")
    master_audio: dict[str, Any] = Field(..., description="Master audio from AudioMixer")
    subtitle_file: dict[str, Any] = Field(..., description="Subtitle file from SubtitleAgent")
    edit_parameters: Optional[dict[str, Any]] = Field(None, description="Edit parameters (trim, transitions, etc.)")

class EditorOutput(BaseModel):
    """Output schema for EditorAgent."""
    state: dict[str, Any] = Field(..., description="Updated pipeline state")
    edit_timeline_id: str = Field(..., description="Unique edit timeline identifier")
    timeline: dict[str, Any] = Field(..., description="Edit timeline structure")
    edit_id: str = Field(..., description="Unique edit identifier")
    confidence: float = Field(0.0, description="Confidence score 0.0-1.0")
    estimated_tokens: int = Field(2500, description="Estimated token usage")
    edited_at: datetime = Field(default_factory=datetime.utcnow, description="Edit timestamp")

class EditorError(BaseModel):
    """Error schema for EditorAgent."""
    error_code: str = Field(EditorErrorCodes.EDITING_FAILED, description="Error code identifier")
    error_message: str = Field(..., description="Human-readable error message")
    context: Optional[dict[str, Any]] = Field(None, description="Context where error occurred")
    recoverable: bool = Field(True, description="Whether error is recoverable")
    suggested_approach: Optional[str] = Field(None, description="Suggested alternative approach")

# Error codes
class EditorErrorCodes:
    MISSING_ARTIFACTS = "ED001"
    INCOMPATIBLE_FORMATS = "ED002"
    EDITING_ENGINE_ERROR = "ED003"
    TIMELINE_CONFLICT = "ED004"