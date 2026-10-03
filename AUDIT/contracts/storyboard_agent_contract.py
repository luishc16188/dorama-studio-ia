from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class StoryboardAgentInput(BaseModel):
    """Input schema for StoryboardAgent."""
    state: dict[str, Any] = Field(..., description="Current pipeline state")
    episode_blueprint: dict[str, Any] = Field(..., description="Episode blueprint from MasterWriter")
    episode_number: int = Field(..., description="Episode number in season")
    season_id: str = Field(..., description="Season identifier")
    character_state_refs: Optional[Dict[str, str]] = Field(None, description="Character state references")
    continuity_rules: Optional[Dict[str, Any]] = Field(None, description="Continuity rules to enforce")

class StoryboardAgentOutput(BaseModel):
    """Output schema for StoryboardAgent."""
    state: dict[str, Any] = Field(..., description="Updated pipeline state")
    storyboard: dict[str, Any] = Field(..., description="Generated storyboard structure")
    storyboard_id: str = Field(..., description="Unique storyboard identifier")
    shot_count: int = Field(0, description="Number of shots in storyboard")
    visual_consistency_score: float = Field(0.0, description="Visual consistency score 0.0-1.0")
    confidence: float = Field(0.0, description="Confidence score 0.0-1.0")
    estimated_tokens: int = Field(3500, description="Estimated token usage")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")

class StoryboardAgentError(BaseModel):
    """Error schema for StoryboardAgent."""
    error_code: str = Field(StoryboardAgentErrorCodes.STORYBOARD_GENERATION_FAILED, description="Error code identifier")
    error_message: str = Field(..., description="Human-readable error message")
    context: Optional[dict[str, Any]] = Field(None, description="Context where error occurred")
    recoverable: bool = Field(True, description="Whether error is recoverable")
    suggested_approach: Optional[str] = Field(None, description="Suggested alternative approach")

# Error codes
class StoryboardAgentErrorCodes:
    BLUEPRINT_NOT_FOUND = "SB001"
    INSUFFICIENT_CONTEXT = "SB002"
    CONSISTENCY_VIOLATION = "SB003"
    GENERATION_FAILED = "SB004"