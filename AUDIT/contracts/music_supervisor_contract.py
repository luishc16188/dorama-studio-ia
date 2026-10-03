from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class MusicSupervisorInput(BaseModel):
    """Input schema for MusicSupervisorAgent."""
    state: dict[str, Any] = Field(..., description="Current pipeline state")
    episode_spec: dict[str, Any] = Field(..., description="Episode specification")
    scene_contexts: List[dict[str, Any]] = Field(..., description="Scene contexts for music")
    genre_references: Optional[List[str]] = Field(None, description="Genre references for music style")
    mood_requirements: Optional[dict[str, Any]] = Field(None, description="Mood requirements per scene")
    creative_genome_context: Optional[dict[str, Any]] = Field(None, description="Creative genome context")

class MusicSupervisorOutput(BaseModel):
    """Output schema for MusicSupervisorAgent."""
    state: dict[str, Any] = Field(..., description="Updated pipeline state")
    music_timeline: List[dict[str, Any]] = Field(..., description="Music timeline entries")
    music_id: str = Field(..., description="Unique music identifier")
    genre_classification: str = Field(..., description="Music genre classification")
    mood_analysis: Dict[str, Any] = Field(default_factory=dict, description="Mood analysis results")
    confidence: float = Field(0.0, description="Confidence score 0.0-1.0")
    estimated_tokens: int = Field(3000, description="Estimated token usage")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")

class MusicSupervisorError(BaseModel):
    """Error schema for MusicSupervisorAgent."""
    error_code: str = Field(MusicSupervisorErrorCodes.MUSIC_GENERATION_FAILED, description="Error code identifier")
    error_message: str = Field(..., description="Human-readable error message")
    context: Optional[dict[str, Any]] = Field(None, description="Context where error occurred")
    recoverable: bool = Field(True, description="Whether error is recoverable")
    suggested_approach: Optional[str] = Field(None, description="Suggested alternative approach")

# Error codes
class MusicSupervisorErrorCodes:
    GENRE_NOT_FOUND = "MS001"
    INSUFFICIENT_CONTEXT = "MS002"
    MOOD_CONFLICT = "MS003"
    GENERATION_FAILED = "MS004"