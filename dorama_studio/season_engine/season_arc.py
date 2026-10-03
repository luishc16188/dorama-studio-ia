"""
Season Arc Models - Phase 6
Defines the macro structure for a 40-episode dorama season.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ActType(str, Enum):
    """Types of acts in a season."""
    SETUP = "setup"           # Episodes 1-10: World, characters, inciting incident
    CONFRONTATION = "confrontation"  # Episodes 11-25: Rising action, complications
    CLIMAX = "climax"         # Episodes 26-35: Major revelations, peak tension
    RESOLUTION = "resolution" # Episodes 36-40: Payoffs, closure, setup for S2


class RevealType(str, Enum):
    """Types of major reveals."""
    IDENTITY = "identity"           # True parentage, secret lineage
    BETRAYAL = "betrayal"           # Ally was enemy all along
    POWER_SOURCE = "power_source"   # True nature of power/magic/tech
    CONSPIRACY = "conspiracy"       # Hidden organization pulling strings
    TIME_LOOP = "time_loop"         # Events repeating, causality break
    PARALLEL_WORLD = "parallel_world"  # Alternate reality/timeline
    FAKE_DEATH = "fake_death"       # Character presumed dead is alive
    MEMORY_WIPE = "memory_wipe"     # Character's past was fabricated
    DOUBLE_AGENT = "double_agent"   # Character playing both sides
    PROPHECY_TWIST = "prophecy_twist"  # Prophecy means opposite


class SeasonAct(BaseModel):
    """A single act within the season."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    act_number: int = Field(ge=1, le=4)
    act_type: ActType
    episode_range: tuple[int, int]  # (start_ep, end_ep)
    theme: str
    major_beats: list[str] = Field(default_factory=list)
    character_focus: list[str] = Field(default_factory=list)  # Character IDs
    location_focus: list[str] = Field(default_factory=list)  # Location IDs
    major_reveals: list[str] = Field(default_factory=list)  # Reveal IDs
    emotional_arc: str  # e.g., "hope -> despair -> determination"
    stakes_escalation: str  # How stakes increase in this act


class MajorReveal(BaseModel):
    """A major plot reveal scheduled in the season."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    reveal_id: str
    reveal_type: RevealType
    episode: int = Field(ge=1, le=40)
    description: str
    characters_affected: list[str] = Field(default_factory=list)
    setup_episodes: list[int] = Field(default_factory=list)  # Episodes that foreshadow
    payoff_episodes: list[int] = Field(default_factory=list)  # Episodes that resolve
    impact_level: Literal["personal", "relational", "global"] = "personal"
    foreshadowing_strength: float = Field(default=0.5, ge=0.0, le=1.0)


class SeasonArc(BaseModel):
    """Complete season arc for a 40-episode dorama."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    season_id: str
    season_number: int = 1
    total_episodes: int = 40
    genre: str
    subgenre: str | None = None

    # Core concept
    logline: str
    central_question: str  # The question the season answers
    theme: str  # e.g., "power corrupts but love redeems"

    # Act structure (4 acts x 10 episodes)
    acts: list[SeasonAct] = Field(default_factory=list)

    # Major reveals timeline
    major_reveals: list[MajorReveal] = Field(default_factory=list)

    # Character arcs across season
    character_arcs: dict[str, dict[str, Any]] = Field(default_factory=dict)  # char_id -> arc_summary

    # Open loops tracking
    open_loops: list[dict[str, Any]] = Field(default_factory=list)

    # Mystery map
    mystery_map: dict[str, Any] = Field(default_factory=dict)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1

    def get_act_for_episode(self, episode: int) -> SeasonAct | None:
        """Get the act containing a specific episode."""
        for act in self.acts:
            start, end = act.episode_range
            if start <= episode <= end:
                return act
        return None

    def get_reveals_for_episode(self, episode: int) -> list[MajorReveal]:
        """Get all reveals scheduled for an episode."""
        return [r for r in self.major_reveals if r.episode == episode]

    def get_upcoming_reveals(self, from_episode: int, count: int = 3) -> list[MajorReveal]:
        """Get next N reveals after an episode."""
        upcoming = [r for r in self.major_reveals if r.episode > from_episode]
        upcoming.sort(key=lambda r: r.episode)
        return upcoming[:count]

    def validate_structure(self) -> list[str]:
        """Validate season arc structure. Returns list of issues."""
        issues = []

        if len(self.acts) != 4:
            issues.append(f"Expected 4 acts, got {len(self.acts)}")

        # Check episode coverage
        covered = set()
        for act in self.acts:
            start, end = act.episode_range
            if start > end:
                issues.append(f"Act {act.act_number}: invalid range {start}-{end}")
            for ep in range(start, end + 1):
                if ep in covered:
                    issues.append(f"Episode {ep} covered by multiple acts")
                covered.add(ep)

        missing = set(range(1, self.total_episodes + 1)) - covered
        if missing:
            issues.append(f"Episodes not covered: {sorted(missing)}")

        # Check reveals within episode range
        for reveal in self.major_reveals:
            if not (1 <= reveal.episode <= self.total_episodes):
                issues.append(f"Reveal {reveal.reveal_id}: episode {reveal.episode} out of range")

        return issues
