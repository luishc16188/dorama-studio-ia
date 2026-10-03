from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class EpisodeVerdict(str, Enum):
    PASS = "pass"
    REWRITE = "rewrite"
    HUMAN_REVIEW = "human_review"

class ScoreBreakdown(BaseModel):
    """Breakdown of episode scoring by dimension."""
    hook: float = Field(0.0, description="Hook quality score 0.0-1.0")
    dialogue_quality: float = Field(0.0, description="Dialogue quality score")
    story_structure: float = Field(0.0, description="Story structure score")
    emotional_damage: float = Field(0.0, description="Emotional damage score")
    retention_cadence: float = Field(0.0, description="Retention cadence score")
    character_voice: float = Field(0.0, description="Character voice score")
    visual_potential: float = Field(0.0, description="Visual potential score")
    audio_design: float = Field(0.0, description="Audio design score")
    cliffhanger: float = Field(0.0, description="Cliffhanger score")
    cta_tribal: float = Field(0.0, description="CTA tribal score")

class EpisodeScorerInput(BaseModel):
    """Input schema for EpisodeScorerAgent."""
    state: dict[str, Any] = Field(..., description="Current pipeline state")
    episode_spec: dict[str, Any] = Field(..., description="Episode specification")
    quality_threshold: float = Field(85.0, description="Minimum quality threshold for PASS")
    rewrite_threshold: float = Field(75.0, description="Threshold for REWRITE recommendation")
    human_review_threshold: float = Field(70.0, description="Threshold for HUMAN_REVIEW")
    include_creative_genome: bool = Field(True, description="Whether to include genome analysis")
    detailed_analysis: bool = Field(True, description="Whether to provide detailed breakdown")

class EpisodeScorerOutput(BaseModel):
    """Output schema for EpisodeScorerAgent."""
    state: dict[str, Any] = Field(..., description="Updated pipeline state")
    episode_score: float = Field(0.0, description="Overall episode score 0.0-100.0")
    verdict: EpisodeVerdict = Field(EpisodeVerdict.PASS, description="Quality verdict")
    breakdown: ScoreBreakdown = Field(..., description="Score breakdown by dimension")
    feedback: List[dict[str, Any]] = Field(..., description="List of feedback items")
    critical_failures: List[str] = Field(default_factory=list, description="Critical failures detected")
    recovery_suggestions: List[str] = Field(default_factory=list, description="Suggestions for improvement")
    confidence: float = Field(0.0, description="Confidence score 0.0-1.0")
    estimated_tokens: int = Field(2048, description="Estimated token usage")
    scored_at: datetime = Field(default_factory=datetime.utcnow, description="Scoring timestamp")

class EpisodeScorerError(BaseModel):
    """Error schema for EpisodeScorerAgent."""
    error_code: str = Field(EpisodeScorerErrorCodes.SCORING_FAILED, description="Error code identifier")
    error_message: str = Field(..., description="Human-readable error message")
    context: Optional[dict[str, Any]] = Field(None, description="Context where error occurred")
    recoverable: bool = Field(True, description="Whether error is recoverable")
    suggested_action: Optional[str] = Field(None, description="Suggested recovery action")

# Error codes
class EpisodeScorerErrorCodes:
    EPISODE_SPEC_INVALID = "ES001"
    INSUFFICIENT_DATA = "ES002"
    SCORING_ENGINE_ERROR = "ES003"
    THRESHOLD_CALCULATION_ERROR = "ES004"
    CREATIVE_GENOME_ERROR = "ES005"