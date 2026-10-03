from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class RetentionEngineInput(BaseModel):
    """Input schema for RetentionEngineAgent."""
    state: dict[str, Any] = Field(..., description="Current pipeline state")
    microbeats: List[dict[str, Any]] = Field(..., description="Microbeats structure from episode")
    episode_number: int = Field(..., description="Episode number in season")
    season_id: str = Field(..., description="Season identifier")
    previous_episodes_retention: Optional[List[dict[str, Any]]] = Field(None, description="Retention data from previous episodes")
    creative_genome_context: Optional[dict[str, Any]] = Field(None, description="Creative genome context for pattern awareness")

class RetentionEngineOutput(BaseModel):
    """Output schema for RetentionEngineAgent."""
    state: dict[str, Any] = Field(..., description="Updated pipeline state")
    retention_actions: List[dict[str, Any]] = Field(..., description="Retention actions to apply")
    retention_score: float = Field(0.0, description="Retention score 0.0-1.0")
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors for drop-off")
    recommended_fixes: List[dict[str, Any]] = Field(default_factory=list, description="Recommended fixes for retention issues")
    confidence: float = Field(0.0, description="Confidence score 0.0-1.0")
    estimated_tokens: int = Field(2000, description="Estimated token usage")
    analyzed_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")

class RetentionEngineError(BaseModel):
    """Error schema for RetentionEngineAgent."""
    error_code: str = Field(RetentionEngineErrorCodes.RETENTION_ANALYSIS_FAILED, description="Error code identifier")
    error_message: str = Field(..., description="Human-readable error message")
    context: Optional[dict[str, Any]] = Field(None, description="Context where error occurred")
    recoverable: bool = Field(True, description="Whether error is recoverable")
    suggested_alternative: Optional[str] = Field(None, description="Suggested alternative analysis approach")

# Error codes
class RetentionEngineErrorCodes:
    EPISODE_SPEC_INVALID = "RE001"
    INSUFFICIENT_MICROBEATS = "RE002"
    ANALYSIS_ENGINE_ERROR = "RE003"
    PATTERN_DETECTION_ERROR = "RE004"