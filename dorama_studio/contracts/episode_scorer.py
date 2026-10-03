"""
Data contracts for Episode Scorer - based on quality.yaml
"""

from pydantic import BaseModel, Field, model_validator


class HookScore(BaseModel):
    intrigue: int = Field(ge=0, le=100)
    emotion: int = Field(ge=0, le=100)
    retention: int = Field(ge=0, le=100)


class StoryScore(BaseModel):
    structure: int = Field(ge=0, le=100)
    pacing: int = Field(ge=0, le=100)
    coherence: int = Field(ge=0, le=100)


class EmotionScore(BaseModel):
    authenticity: int = Field(ge=0, le=100)
    intensity: int = Field(ge=0, le=100)
    variety: int = Field(ge=0, le=100)


class RetentionScore(BaseModel):
    hook_retention: int = Field(ge=0, le=100)
    mid_retention: int = Field(ge=0, le=100)
    completion_rate: int = Field(ge=0, le=100)


class CharacterScore(BaseModel):
    consistency: int = Field(ge=0, le=100)
    depth: int = Field(ge=0, le=100)
    chemistry: int = Field(ge=0, le=100)


class VisualScore(BaseModel):
    composition: int = Field(ge=0, le=100)
    lighting: int = Field(ge=0, le=100)
    consistency: int = Field(ge=0, le=100)


class AudioScore(BaseModel):
    dialogue_clarity: int = Field(ge=0, le=100)
    music_fit: int = Field(ge=0, le=100)
    sfx_quality: int = Field(ge=0, le=100)


class CliffhangerScore(BaseModel):
    urgency: int = Field(ge=0, le=100)
    curiosity: int = Field(ge=0, le=100)
    specificity: int = Field(ge=0, le=100)


class CTAScore(BaseModel):
    narrative_integration: int = Field(ge=0, le=100)
    clarity: int = Field(ge=0, le=100)
    urgency: int = Field(ge=0, le=100)


class EpisodeScore(BaseModel):
    """Complete episode scoring model based on quality.yaml"""

    # Main scores (0-100)
    hook: int = Field(ge=0, le=100)
    story: int = Field(ge=0, le=100)
    emotion: int = Field(ge=0, le=100)
    retention: int = Field(ge=0, le=100)
    characters: int = Field(ge=0, le=100)
    visual: int = Field(ge=0, le=100)
    audio: int = Field(ge=0, le=100)
    cliffhanger: int = Field(ge=0, le=100)
    cta: int = Field(ge=0, le=100)

    # Sub-scores for detailed analysis
    hook_details: HookScore
    story_details: StoryScore
    emotion_details: EmotionScore
    retention_details: RetentionScore
    character_details: CharacterScore
    visual_details: VisualScore
    audio_details: AudioScore
    cliffhanger_details: CliffhangerScore
    cta_details: CTAScore

    # Metadata
    episode_id: str
    timestamp: str
    version: str = "1.0.0"

    @model_validator(mode="after")
    def validate_consistency(self):
        """Ensure sub-scores align with main scores (within tolerance)"""
        # Hook: weighted average of intrigue(0.4), emotion(0.3), retention(0.3)
        expected_hook = round(
            self.hook_details.intrigue * 0.4
            + self.hook_details.emotion * 0.3
            + self.hook_details.retention * 0.3
        )
        if abs(self.hook - expected_hook) > 5:  # Allow 5pt tolerance
            raise ValueError(
                f"Hook score mismatch: expected ~{expected_hook}, got {self.hook}"
            )

        # Similar validations for other categories...
        return self

    def is_publishable(self) -> bool:
        """Check if episode meets minimum quality threshold"""
        # From quality.yaml: publish_minimum: 85
        return (
            min(
                self.hook,
                self.story,
                self.emotion,
                self.retention,
                self.characters,
                self.visual,
                self.audio,
                self.cliffhanger,
                self.cta,
            )
            >= 85
        )

    def needs_rewrite(self) -> bool:
        """Check if episode triggers rewrite"""
        # From quality.yaml: rewrite_trigger: 75
        return (
            min(
                self.hook,
                self.story,
                self.emotion,
                self.retention,
                self.characters,
                self.visual,
                self.audio,
                self.cliffhanger,
                self.cta,
            )
            < 75
        )

    def needs_human_review(self) -> bool:
        """Check if episode requires human review"""
        # From quality.yaml: human_review: 70
        return (
            min(
                self.hook,
                self.story,
                self.emotion,
                self.retention,
                self.characters,
                self.visual,
                self.audio,
                self.cliffhanger,
                self.cta,
            )
            < 70
        )
