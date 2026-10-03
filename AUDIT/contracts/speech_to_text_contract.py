from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class SpeechToTextInput(BaseModel):
    """Input schema for SpeechToTextAgent."""
    state: dict[str, Any] = Field(..., description="Current pipeline state")
    mode: str = Field("tts", description="Mode: 'tts' for text-to-speech")
    dialogues: List[dict[str, Any]] = Field(..., description="Dialogue lines to synthesize")
    episode_number: int = Field(..., description="Episode number in season")
    season_id: str = Field(..., description="Season identifier")
    voice_preset: Optional[str] = Field(None, description="Voice preset identifier")
    quality_preset: Optional[str] = Field(None, description="Quality preset for output")

class SpeechToTextOutput(BaseModel):
    """Output schema for SpeechToTextAgent."""
    state: dict[str, Any] = Field(..., description="Updated pipeline state")
    artifact_id: str = Field(..., description="Unique artifact identifier for audio")
    voice_artifacts: dict[str, Any] = Field(..., description="Generated voice artifacts")
    confidence: float = Field(0.0, description="Confidence score 0.0-1.0")
    estimated_tokens: int = Field(180, description="Estimated token usage")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    duration_seconds: float = Field(0.0, description="Generated audio duration")

class SpeechToTextError(BaseModel):
    """Error schema for SpeechToTextAgent."""
    error_code: str = Field(SpeechToTextErrorCodes.TTS_FAILED, description="Error code identifier")
    error_message: str = Field(..., description="Human-readable error message")
    context: Optional[dict[str, Any]] = Field(None, description="Context where error occurred")
    recoverable: bool = Field(True, description="Whether error is recoverable")
    suggested_approach: Optional[str] = Field(None, description="Suggested alternative approach")

# Error codes
class SpeechToTextErrorCodes:
    TTS_FAILED = "STT001"
    VOICE_NOT_AVAILABLE = "STT002"
    QUALITY_ISSUE = "STT003"
    DURATION_EXCEEDED = "STT004"