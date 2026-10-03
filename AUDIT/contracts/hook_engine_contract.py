from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class HookEngineInput(BaseModel):
    """Input schema for HookEngineAgent."""
    state: dict[str, Any] = Field(..., description="Current pipeline state")
    blueprint_id: str = Field(..., description="Episode blueprint identifier")
    episode_number: int = Field(..., description="Episode number in season")
    season_id: str = Field(..., description="Season identifier")
    creative_genome_context: Optional[dict[str, Any]] = Field(None, description="Creative genome context")
    retention_context: Optional[dict[str, Any]] = Field(None, description="Retention context from previous episodes")

class HookEngineOutput(BaseModel):
    """Output schema for HookEngineAgent."""
    state: dict[str, Any] = Field(..., description="Updated pipeline state")
    hook_id: str = Field(..., description="Unique hook identifier")
    top_5_hooks: List[dict[str, Any]] = Field(..., description="Top 5 generated hooks")
    all_candidates_count: int = Field(0, description="Total candidates evaluated")
    mechanism_coverage: Dict[str, int] = Field(default_factory=dict, description="Mechanism coverage counts")
    selected_hook: Optional[dict[str, Any]] = Field(None, description="Selected hook for this episode")
    confidence: float = Field(0.0, description="Confidence score 0.0-1.0")
    estimated_tokens: int = Field(2000, description="Estimated token usage")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")

class HookEngineError(BaseModel):
    """Error schema for HookEngineAgent."""
    error_code: str = Field(HookEngineErrorCodes.HOOK_GENERATION_FAILED, description="Error code identifier")
    error_message: str = Field(..., description="Human-readable error message")
    context: Optional[dict[str, Any]] = Field(None, description="Context where error occurred")
    recoverable: bool = Field(True, description="Whether error is recoverable")
    suggested_approach: Optional[str] = Field(None, description="Suggested alternative approach")

# Error codes
class HookEngineErrorCodes:
    BLUEPRINT_NOT_FOUND = "HE001"
    INSUFFICIENT_CONTEXT = "HE002"
    CREATIVE_EXHAUSTION = "HE003"
    SIMILAR_HOOK_DETECTED = "HE004"