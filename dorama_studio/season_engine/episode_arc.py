"""
Episode Arc Models - Phase 6
Defines the micro structure for individual episodes within a season.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


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


class EpisodeBeat(BaseModel):
    """A single beat within an episode."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    beat_type: BeatType
    beat_number: int = Field(ge=1, le=9)
    duration_sec: float = Field(default=10.0, ge=5.0, le=15.0)
    start_sec: float = 0.0
    end_sec: float = 10.0

    # Narrative
    narrative_goal: str
    emotional_target: str  # e.g., "shock", "tension", "catharsis"
    information_delta: Literal["reveal", "withhold", "partial", "question"] = "partial"

    # Character & Action
    action: str
    dialogue: str | None = None
    character_ids: list[str] = Field(default_factory=list)

    # Visual
    shot_type: str | None = None  # ECU, CU, MCU, MS, WS, etc.
    camera_movement: str | None = None
    lens: str | None = None
    focus_pull: str | None = None

    # Audio
    ambience: str | None = None
    sfx: list[str] = Field(default_factory=list)
    music_cue: dict[str, Any] | None = None
    silence_drop: bool = False
    sub_bass_stinger: bool = False

    # Continuity
    continuity_blocks: list[str] = Field(default_factory=list)
    information_revealed: list[str] = Field(default_factory=list)
    information_withheld: list[str] = Field(default_factory=list)

    # Retention
    retention_hooks: list[str] = Field(default_factory=list)
    pattern_interrupts: list[str] = Field(default_factory=list)

    # Subversion
    subversion_applied: str | None = None

    def validate_beat(self) -> list[str]:
        """Validate beat completeness. Returns list of issues."""
        issues = []
        if self.duration_sec < 5 or self.duration_sec > 15:
            issues.append(f"Beat duration {self.duration_sec}s outside 5-15s range")
        if not self.narrative_goal:
            issues.append("Missing narrative_goal")
        if not self.emotional_target:
            issues.append("Missing emotional_target")
        if not self.action:
            issues.append("Missing action")
        if self.dialogue and len(self.dialogue.split()) > 10:
            issues.append(f"Dialogue exceeds 10 words: {len(self.dialogue.split())}")
        return issues


class CTAType(str, Enum):
    """Call-to-action types for episode endings."""
    MORAL_DILEMMA = "moral_dilemma"
    REVENGE_CHOICE = "revenge_choice"
    IDENTITY_TEASE = "identity_tease"
    TEAM_WAR = "team_war"
    QUESTION_TRIBAL = "question_tribal"
    PROTECT_LOVED_ONE = "protect_loved_one"
    SACRIFICE_CHOICE = "sacrifice_choice"


class EpisodeArc(BaseModel):
    """Complete arc for a single 90-second episode."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    episode_id: str
    episode_number: int = Field(ge=1, le=40)
    season_id: str

    # Season context
    act_number: int = Field(ge=1, le=4)
    season_arc_ref: str | None = None

    # Episode core
    hook_category: str  # e.g., "visual_shock", "identity_shock", "betrayal"
    core_conflict: str
    twist: str
    cliffhanger: str
    cta_type: CTAType

    # 9 beats
    beats: list[EpisodeBeat] = Field(default_factory=list)

    # Character & Location
    character_ids: list[str] = Field(default_factory=list)
    location_ids: list[str] = Field(default_factory=list)

    # Reveals in this episode
    reveals: list[str] = Field(default_factory=list)  # Reveal IDs from season arc

    # Open loops
    opens_loops: list[str] = Field(default_factory=list)
    closes_loops: list[str] = Field(default_factory=list)

    # Temporal budget
    total_duration_sec: float = 90.0
    temporal_budget_allocated: dict[str, float] = Field(default_factory=dict)

    # Subversion & Quality
    subversion_applied: str | None = None
    quality_score: float = 0.0

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1

    def add_beat(self, beat: EpisodeBeat) -> None:
        """Add a beat and update timing."""
        if self.beats:
            prev = self.beats[-1]
            beat.start_sec = prev.end_sec
            beat.end_sec = beat.start_sec + beat.duration_sec
        else:
            beat.start_sec = 0.0
            beat.end_sec = beat.duration_sec
        beat.beat_number = len(self.beats) + 1
        self.beats.append(beat)
        self._recalc_timing()

    def _recalc_timing(self) -> None:
        """Recalculate all beat timings."""
        current = 0.0
        for i, beat in enumerate(self.beats):
            beat.start_sec = current
            beat.end_sec = current + beat.duration_sec
            beat.beat_number = i + 1
            current = beat.end_sec
        self.total_duration_sec = current

    def validate_episode(self) -> list[str]:
        """Validate episode arc. Returns list of issues."""
        issues = []

        if len(self.beats) != 9:
            issues.append(f"Expected 9 beats, got {len(self.beats)}")

        total_duration = sum(b.duration_sec for b in self.beats)
        if abs(total_duration - 90.0) > 2.0:
            issues.append(f"Total duration {total_duration:.1f}s != 90s (±2s tolerance)")

        # Check beat types in order
        expected_types = list(BeatType)
        for i, beat in enumerate(self.beats):
            if beat.beat_type != expected_types[i]:
                issues.append(f"Beat {i+1}: expected {expected_types[i].value}, got {beat.beat_type.value}")

        # Validate each beat
        for beat in self.beats:
            issues.extend(beat.validate_beat())

        # Check duration allocation
        if self.total_duration_sec != 90.0:
            issues.append(f"Episode total_duration_sec {self.total_duration_sec} != 90.0")

        return issues

    def get_beat(self, beat_type: BeatType) -> EpisodeBeat | None:
        """Get beat by type."""
        for beat in self.beats:
            if beat.beat_type == beat_type:
                return beat
        return None

    def get_retention_hooks(self) -> list[str]:
        """Get all retention hooks across beats."""
        hooks = []
        for beat in self.beats:
            hooks.extend(beat.retention_hooks)
        return hooks
