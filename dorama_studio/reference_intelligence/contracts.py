"""
Pydantic models for Reference Intelligence & Production DNA.
Defines the structured rules extracted from reference videos.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class HookCategory(str, Enum):
    """Categories of viral hooks."""
    IMPOSSIBLE_ROMANCE = "impossible_romance"
    REVENGE = "revenge"
    BETRAYAL = "betrayal"
    IDENTITY_SHOCK = "identity_shock"
    VISUAL_SHOCK = "visual_shock"
    POWER_REVEAL = "power_reveal"
    HUMILIATION = "humiliation"
    MORAL_DILEMMA = "moral_dilemma"
    THREAT = "threat"
    MYSTERY = "mystery"
    PROHIBITION = "prohibition"
    QUESTION = "question"


class HookRule(BaseModel):
    """Rule for generating effective hooks based on reference analysis."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    category: HookCategory
    pattern: str  # e.g., "Character discovers X that changes everything"
    viral_score: float = Field(ge=0.0, le=1.0)  # How viral this hook type is
    optimal_position_sec: float = Field(default=0.5)  # When to deploy (0-3s)
    required_elements: list[str] = Field(default_factory=list)  # What must be present
    subversion_templates: list[str] = Field(default_factory=list)  # How to subvert
    platform_performance: dict[str, float] = Field(default_factory=dict)  # TikTok/Reels/Shorts


class BeatType(str, Enum):
    """Types of beats in the 9-beat structure."""
    HOOK = "hook"              # 0-10s
    CONTEXT = "context"        # 10-20s
    PROBLEM = "problem"        # 20-30s
    ESCALATION = "escalation"  # 30-40s
    TWIST_1 = "twist_1"        # 40-50s
    CONFLICT_2 = "conflict_2"  # 50-60s
    REVELATION = "revelation"  # 60-70s
    CLIFFHANGER = "cliffhanger" # 70-80s
    CTA = "cta"                # 80-90s


class BeatStructure(BaseModel):
    """Structure rules for a specific beat type."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    beat_type: BeatType
    duration_range_sec: tuple[float, float] = Field(default=(8.0, 12.0))
    required_components: list[str] = Field(default_factory=list)  # e.g., ["dialogue", "action", "camera", "sound"]
    emotional_target: str  # e.g., "shock", "tension", "revelation"
    information_delta: str  # "reveal", "withhold", "partial"
    visual_change_required: bool = True
    audio_shift_required: bool = True
    subversion_mandatory: bool = False
    max_dialogue_words: int = 10
    pattern_interrupts: list[str] = Field(default_factory=list)


class VisualMotifType(str, Enum):
    """Types of visual motifs."""
    COLOR_PALETTE = "color_palette"
    LIGHTING_STYLE = "lighting_style"
    CAMERA_GRAMMAR = "camera_grammar"
    COMPOSITION_RULE = "composition_rule"
    TRANSITION_STYLE = "transition_style"
    VFX_SIGNATURE = "vfx_signature"
    MICRO_EXPRESSION = "micro_expression"


class VisualMotif(BaseModel):
    """Visual motif rule extracted from reference."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    motif_type: VisualMotifType
    name: str  # e.g., "Cold Cyan Rim Light"
    description: str
    technical_spec: dict[str, Any] = Field(default_factory=dict)  # Exact parameters
    emotional_effect: str  # e.g., "isolation", "tension", "intimacy"
    beat_applicability: list[str] = Field(default_factory=list)  # Which beats to use
    frequency_per_episode: int = 1
    consistency_level: Literal["strict", "flexible", "reference_only"] = "strict"


class AudioSignatureType(str, Enum):
    """Types of audio signatures."""
    MUSIC_GENRE_PROGRESSION = "music_genre_progression"
    SILENCE_DROP_PATTERN = "silence_drop_pattern"
    SUB_BASS_STINGER = "sub_bass_stinger"
    FOLEY_AMPLIFICATION = "foley_amplification"
    VOICE_PROCESSING = "voice_processing"
    AMBIENCE_LAYERING = "ambience_layering"


class AudioSignature(BaseModel):
    """Audio signature rule extracted from reference."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    signature_type: AudioSignatureType
    name: str
    description: str
    technical_spec: dict[str, Any] = Field(default_factory=dict)
    trigger_conditions: list[str] = Field(default_factory=list)  # When to apply
    beat_targets: list[str] = Field(default_factory=list)  # Which beats
    emotional_purpose: str  # e.g., "tension building", "shock", "intimacy"


class ProductionDNA(BaseModel):
    """Complete production DNA extracted from reference videos."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    source_references: list[str] = Field(default_factory=list)  # Video IDs/URLs
    extracted_at: datetime = Field(default_factory=datetime.utcnow)

    # Core rule sets
    hook_rules: list[HookRule] = Field(default_factory=list)
    beat_structures: list[BeatStructure] = Field(default_factory=list)
    visual_motifs: list[VisualMotif] = Field(default_factory=list)
    audio_signatures: list[AudioSignature] = Field(default_factory=list)

    # Meta-rules
    genre: str
    subgenre: str | None = None
    episode_duration_sec: int = 90
    total_beats: int = 9

    # Quality thresholds
    min_viral_score: float = 0.75
    max_hook_duration_sec: float = 3.0
    silence_drop_before_revelation: bool = True
    sub_bass_on_cliffhanger: bool = True

    # Budget allocation (70/20/10)
    proven_budget: int = 70
    exploration_budget: int = 20
    big_bet_budget: int = 10


class ReferenceAnalysis(BaseModel):
    """Result of analyzing a reference video."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    video_id: str
    video_url: str | None = None
    title: str | None = None
    platform: str | None = None
    duration_sec: float | None = None

    # Extracted components
    hooks_detected: list[dict[str, Any]] = Field(default_factory=list)
    beats_detected: list[dict[str, Any]] = Field(default_factory=list)
    visual_motifs: list[dict[str, Any]] = Field(default_factory=list)
    audio_signatures: list[dict[str, Any]] = Field(default_factory=list)

    # Quality metrics
    viral_potential_score: float = 0.0
    production_quality_score: float = 0.0
    originality_score: float = 0.0

    # Processing metadata
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    analyzer_version: str = "1.0"
    confidence_score: float = 0.0
