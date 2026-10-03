from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class KeyframeAgentInput(BaseModel):
    """Input schema for KeyframeAgent."""
    state: dict[str, Any] = Field(..., description="Current pipeline state")
    shots: List[dict[str, Any]] = Field(..., description="Episode shots structure")
    episode_number: int = Field(..., description="Episode number in season")
    season_id: str = Field(..., description="Season identifier")
    character_references: Optional[Dict[str, Any]] = Field(None, description="Character references for consistency")
    creative_genome_context: Optional[dict[str, Any]] = Field(None, description="Creative genome context")

class KeyframeAgentOutput(BaseModel):
    """Output schema for KeyframeAgent."""
    state: dict[str, Any] = Field(..., description="Updated pipeline state")
    keyframes: List[dict[str, Any]] = Field(..., description="Generated keyframes")
    keyframe_id: str = Field(..., description="Unique keyframe identifier")
    consistency_notes: Dict[str, Any] = Field(default_factory=dict, description="Consistency maintenance notes")
    generation_ready: bool = Field(True, description="Ready for video keyframe generation")
    confidence: float = Field(0.0, description="Confidence score 0.0-1.0")
    estimated_tokens: int = Field(2500, description="Estimated token usage")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")

class KeyframeAgentError(BaseModel):
    """Error schema for KeyframeAgent."""
    error_code: str = Field(KeyframeAgentErrorCodes.KEYFRAME_GENERATION_FAILED, description="Error code identifier")
    error_message: str = Field(..., description="Human-readable error message")
    context: Optional[dict[str, Any]] = Field(None, description="Context where error occurred")
    recoverable: bool = Field(True, description="Whether error is recoverable")
    suggested_approach: Optional[str] = Field(None, description="Suggested alternative approach")

# Error codes
class KeyframeAgentErrorCodes:
    SHOTS_NOT_FOUND = "KA001"
    INSUFFICIENT_CONTEXT = "KA002"
    CONSISTENCY_VIOLATION = "KA003"
    GENERATION_FAILED = "KA004"