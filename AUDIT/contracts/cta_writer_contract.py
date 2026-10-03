from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class CTAWriterInput(BaseModel):
    """Input schema for CTAWriterAgent."""
    state: dict[str, Any] = Field(..., description="Current pipeline state")
    beats: List[dict[str, Any]] = Field(..., description="Story beats structure")
    episode_number: int = Field(..., description="Episode number in season")
    season_id: str = Field(..., description="Season identifier")
    episode_type: str = Field(..., description="Episode type (romance, action, mystery, etc.)")
    creative_genome_context: Optional[dict[str, Any]] = Field(None, description="Creative genome context")

class CTAWriterOutput(BaseModel):
    """Output schema for CTAWriterAgent."""
    state: dict[str, Any] = Field(..., description="Updated pipeline state")
    cta_options: List[dict[str, Any]] = Field(..., description="CTA options generated")
    selected_cta: dict[str, Any] = Field(..., description="Selected call-to-action")
    cta_id: str = Field(..., description="Unique CTA identifier")
    cta_type: str = Field(..., description="CTA type classification")
    confidence: float = Field(0.0, description="Confidence score 0.0-1.0")
    estimated_tokens: int = Field(1000, description="Estimated token usage")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")

class CTAWriterError(BaseModel):
    """Error schema for CTAWriterAgent."""
    error_code: str = Field(CTAWriterErrorCodes.CTA_GENERATION_FAILED, description="Error code identifier")
    error_message: str = Field(..., description="Human-readable error message")
    context: Optional[dict[str, Any]] = Field(None, description="Context where error occurred")
    recoverable: bool = Field(True, description="Whether error is recoverable")
    suggested_alternative: Optional[str] = Field(None, description="Suggested alternative CTA")

# Error codes
class CTAWriterErrorCodes:
    INSUFFICIENT_CONTEXT = "CW001"
    CREATIVE_EXHAUSTION = "CW002"
    TYPE_MISMATCH = "CW003"
    PATTERN_NOT_APPLICABLE = "CW004"