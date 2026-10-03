from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class VisualAgentInput(BaseModel):
    """Input schema for VisualAgent."""
    state: dict[str, Any] = Field(..., description="Current pipeline state")
    shots: List[dict[str, Any]] = Field(..., description="Episode shots structure")
    episode_number: int = Field(..., description="Episode number in season")
    season_id: str = Field(..., description="Season identifier")
    character_state_refs: Optional[Dict[str, str]] = Field(None, description="Character state references")
    creative_genome_context: Optional[dict[str, Any]] = Field(None, description="Creative genome context")

class VisualAgentOutput(BaseModel):
    """Output schema for VisualAgent."""
    state: dict[str, Any] = Field(..., description="Updated pipeline state")
    visual_prompts: List[dict[str, Any]] = Field(..., description="Visual prompts for each shot")
    character_consistency_notes: Dict[str, Any] = Field(default_factory=dict, description="Character consistency notes")
    generation_ready: bool = Field(True, description="Whether ready for video generation")
    confidence: float = Field(0.0, description="Confidence score 0.0-1.0")
    estimated_tokens: int = Field(3000, description="Estimated token usage")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")

class VisualAgentError(BaseModel):
    """Error schema for VisualAgent."""
    error_code: str = Field(VisualAgentErrorCodes.VISUAL_GENERATION_FAILED, description="Error code identifier")
    error_message: str = Field(..., description="Human-readable error message")
    context: Optional[dict[str, Any]] = Field(None, description="Context where error occurred")
    recoverable: bool = Field(True, description="Whether error is recoverable")
    suggested_approach: Optional[str] = Field(None, description="Suggested alternative approach")

# Error codes
class VisualAgentErrorCodes:
    SHOTS_NOT_FOUND = "VA001"
    INSUFFICIENT_CONTEXT = "VA002"
    CONSISTENCY_VIOLATION = "VA003"
    GENERATION_FAILED = "VA004"