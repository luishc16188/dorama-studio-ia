from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class MasterWriterInput(BaseModel):
    """Input schema for MasterWriterAgent."""
    state: dict[str, Any] = Field(..., description="Current pipeline state")
    blueprint_id: str = Field(..., description="Episode blueprint identifier")
    hook_ref: str = Field(..., description="Hook pack reference")
    episode_number: int = Field(..., description="Episode number in season")
    season_id: str = Field(..., description="Season identifier")
    creative_genome_context: Optional[dict[str, Any]] = Field(None, description="Creative genome context for pattern awareness")
    retention_actions: Optional[List[str]] = Field(None, description="Retention actions from previous review")
    cliffhanger_hints: Optional[List[str]] = Field(None, description="Cliffhanger hint patterns")

class MasterWriterOutput(BaseModel):
    """Output schema for MasterWriterAgent."""
    state: dict[str, Any] = Field(..., description="Updated pipeline state")
    scripts: List[dict[str, Any]] = Field(..., description="Generated episode scripts")
    episode_blueprints: List[dict[str, Any]] = Field(..., description="Episode blueprints generated")
    beats: List[dict[str, Any]] = Field(..., description="Story beats structure")
    script_id: str = Field(..., description="Unique script identifier")
    blueprint_id: str = Field(..., description="Blueprint identifier")
    confidence: float = Field(0.0, description="Confidence score 0.0-1.0")
    estimated_tokens: int = Field(4000, description="Estimated token usage")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")

class MasterWriterError(BaseModel):
    """Error schema for MasterWriterAgent."""
    error_code: str = Field(MasterWriterErrorCodes.MASTER_WRITE_FAILED, description="Error code identifier")
    error_message: str = Field(..., description="Human-readable error message")
    context: Optional[dict[str, Any]] = Field(None, description="Context where error occurred")
    recoverable: bool = Field(True, description="Whether error is recoverable")
    suggested_fallback: Optional[str] = Field(None, description="Suggested fallback approach")

# Error codes
class MasterWriterErrorCodes:
    BLUEPRINT_NOT_FOUND = "MW001"
    HOOK_MISMATCH = "MW002"
    EPISODE_OUT_OF_RANGE = "MW003"
    CREATIVE_EXHAUSTION = "MW004"
    STRUCTURE_INVALID = "MW005"