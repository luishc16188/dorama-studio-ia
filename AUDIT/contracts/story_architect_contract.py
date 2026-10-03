from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class StoryArchitectInput(BaseModel):
    """Input schema for StoryArchitectAgent."""
    state: dict[str, Any] = Field(..., description="Current pipeline state")
    concept: str = Field(..., description="Story concept or brief")
    genre: str = Field(..., description="Genre classification")
    total_episodes: int = Field(30, description="Total episodes in season")
    season_number: int = Field(1, description="Season number")
    previous_season_bible: Optional[str] = Field(None, description="Previous season bible reference")
    creative_genome_context: Optional[dict[str, Any]] = Field(None, description="Creative genome context for pattern awareness")

class StoryArchitectOutput(BaseModel):
    """Output schema for StoryArchitectAgent."""
    state: dict[str, Any] = Field(..., description="Updated pipeline state")
    story_architecture: dict[str, Any] = Field(..., description="Complete story architecture")
    story_architecture_summary: str = Field(..., description="Summary of story architecture")
    blueprint_id: str = Field(..., description="Unique blueprint identifier")
    season_arc: str = Field(..., description="Season-level arc summary")
    recommended_genre_adjustments: Optional[List[str]] = Field(None, description="Genre adjustment recommendations")
    confidence: float = Field(0.0, description="Confidence score 0.0-1.0")
    estimated_tokens: int = Field(4000, description="Estimated token usage")

class StoryArchitectError(BaseModel):
    """Error schema for StoryArchitectAgent."""
    error_code: str = Field(..., description="Error code identifier")
    error_message: str = Field(..., description="Human-readable error message")
    context: Optional[dict[str, Any]] = Field(None, description="Context where error occurred")
    recoverable: bool = Field(True, description="Whether error is recoverable")