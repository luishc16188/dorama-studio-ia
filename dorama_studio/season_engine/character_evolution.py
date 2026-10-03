"""
Character Evolution Planner - Phase 6
Plans and tracks character evolution across a 40-episode season.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .season_arc import SeasonArc


class EvolutionStage(str, Enum):
    """Stages of character evolution."""
    INTRODUCTION = "introduction"      # Ep 1-3: Establish baseline
    INCITING = "inciting"              # Ep 4-6: Inciting incident impacts them
    REACTION = "reaction"              # Ep 7-12: React to events
    TESTING = "testing"                # Ep 13-20: Values tested
    CRISIS = "crisis"                  # Ep 21-28: Dark night of the soul
    TRANSFORMATION = "transformation"  # Ep 29-35: Active change
    INTEGRATION = "integration"        # Ep 36-38: New self stabilized
    RESOLUTION = "resolution"          # Ep 39-40: Final state


class CharacterArc(BaseModel):
    """Complete character arc across a season."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    character_id: str
    character_name: str
    role: Literal["protagonist", "antagonist", "deuteragonist", "tritagonist", "supporting", "foil"]

    # Core psychology
    core_want: str  # What they consciously want
    core_need: str  # What they actually need (unconscious)
    core_lie: str   # The lie they believe about themselves/world
    core_fear: str  # Deepest fear
    core_wound: str # Past trauma that shaped them

    # Evolution tracking
    current_stage: EvolutionStage = EvolutionStage.INTRODUCTION
    stage_episode: int = 1

    # Want vs Need progression
    want_trajectory: list[dict[str, Any]] = Field(default_factory=list)  # episode, want_state
    need_trajectory: list[dict[str, Any]] = Field(default_factory=list)  # episode, need_state

    # Key turning points
    turning_points: list[dict[str, Any]] = Field(default_factory=list)  # episode, event, change

    # Relationships evolution
    relationship_dynamics: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)  # other_char -> [(ep, dynamic)]

    # Competence/agency progression
    agency_level: list[dict[str, Any]] = Field(default_factory=list)  # episode, level 0-1
    competence_level: list[dict[str, Any]] = Field(default_factory=list)  # episode, level 0-1

    # Emotional range
    dominant_emotions: list[dict[str, Any]] = Field(default_factory=list)  # episode, emotion, intensity

    # Final state
    final_want_fulfilled: bool = False
    final_need_met: bool = False
    final_lie_confronted: bool = False

    def advance_stage(self, episode: int, new_stage: EvolutionStage, trigger_event: str) -> None:
        """Advance character to a new evolution stage."""
        self.current_stage = new_stage
        self.stage_episode = episode
        self.turning_points.append({
            "episode": episode,
            "event": trigger_event,
            "new_stage": new_stage.value,
        })

    def update_want(self, episode: int, want_state: str, intensity: float = 1.0) -> None:
        """Update character's want state."""
        self.want_trajectory.append({
            "episode": episode,
            "state": want_state,
            "intensity": intensity,
        })

    def update_need(self, episode: int, need_state: str, progress: float = 0.0) -> None:
        """Update character's need progress."""
        self.need_trajectory.append({
            "episode": episode,
            "state": need_state,
            "progress": progress,
        })

    def add_relationship_dynamic(self, other_char: str, episode: int, dynamic: str, intensity: float = 1.0) -> None:
        """Track relationship dynamic evolution."""
        if other_char not in self.relationship_dynamics:
            self.relationship_dynamics[other_char] = []
        self.relationship_dynamics[other_char].append({
            "episode": episode,
            "dynamic": dynamic,
            "intensity": intensity,
        })

    def update_agency(self, episode: int, level: float) -> None:
        """Update agency level (0-1)."""
        self.agency_level.append({"episode": episode, "level": level})

    def update_competence(self, episode: int, level: float) -> None:
        """Update competence level (0-1)."""
        self.competence_level.append({"episode": episode, "level": level})

    def set_dominant_emotion(self, episode: int, emotion: str, intensity: float) -> None:
        """Set dominant emotion for an episode."""
        self.dominant_emotions.append({
            "episode": episode,
            "emotion": emotion,
            "intensity": intensity,
        })

    def get_stage_for_episode(self, episode: int) -> EvolutionStage:
        """Get the expected stage for an episode."""
        stage_map = {
            range(1, 4): EvolutionStage.INTRODUCTION,
            range(4, 7): EvolutionStage.INCITING,
            range(7, 13): EvolutionStage.REACTION,
            range(13, 21): EvolutionStage.TESTING,
            range(21, 29): EvolutionStage.CRISIS,
            range(29, 36): EvolutionStage.TRANSFORMATION,
            range(36, 39): EvolutionStage.INTEGRATION,
            range(39, 41): EvolutionStage.RESOLUTION,
        }
        for ep_range, stage in stage_map.items():
            if episode in ep_range:
                return stage
        return EvolutionStage.INTRODUCTION

    def validate_arc(self) -> list[str]:
        """Validate character arc completeness."""
        issues = []

        if not self.core_want or not self.core_need:
            issues.append("Missing core_want or core_need")

        if not self.core_lie:
            issues.append("Missing core_lie (character's false belief)")

        if not self.core_fear:
            issues.append("Missing core_fear")

        if len(self.turning_points) < 3:
            issues.append(f"Insufficient turning points: {len(self.turning_points)} (need at least 3)")

        if not self.want_trajectory:
            issues.append("No want trajectory defined")

        if not self.need_trajectory:
            issues.append("No need trajectory defined")

        return issues


class CharacterEvolutionPlanner(BaseModel):
    """
    Plans and coordinates character evolution across a season.
    Ensures arcs interleave properly and relationships evolve naturally.
    """
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid", arbitrary_types_allowed=True)

    season_id: str
    total_episodes: int = 40
    characters: dict[str, CharacterArc] = Field(default_factory=dict)

    # Relationship map
    relationship_matrix: dict[str, dict[str, str]] = Field(default_factory=dict)  # char1 -> char2 -> dynamic

    # Ensemble moments
    ensemble_episodes: list[int] = Field(default_factory=lambda: [1, 10, 20, 30, 40])

    def add_character(self, arc: CharacterArc) -> None:
        """Add a character arc to the planner."""
        self.characters[arc.character_id] = arc

    def get_character(self, character_id: str) -> CharacterArc | None:
        """Get a character arc by ID."""
        return self.characters.get(character_id)

    def plan_arcs(self, season_arc: SeasonArc) -> dict[str, list[dict[str, Any]]]:
        """
        Generate episode-by-episode character evolution plans.
        Returns: character_id -> [{episode, stage, focus, key_beat}]
        """
        plans = {}

        for char_id, arc in self.characters.items():
            char_plan = []
            for ep in range(1, self.total_episodes + 1):
                expected_stage = arc.get_stage_for_episode(ep)
                arc_stage = arc.current_stage

                # Determine focus for this episode
                focus = self._determine_episode_focus(arc, ep, season_arc)

                char_plan.append({
                    "episode": ep,
                    "expected_stage": expected_stage.value,
                    "current_stage": arc_stage.value,
                    "focus": focus,
                    "key_beat": self._get_key_beat_for_episode(arc, ep),
                })

                # Auto-advance stage if needed
                if ep == arc.stage_episode and expected_stage != arc_stage:
                    arc.advance_stage(ep, expected_stage, f"Season arc milestone at episode {ep}")

            plans[char_id] = char_plan

        return plans

    def _determine_episode_focus(self, arc: CharacterArc, episode: int, season_arc: SeasonArc) -> str:
        """Determine character focus for an episode."""
        stage = arc.get_stage_for_episode(episode)

        focus_map = {
            EvolutionStage.INTRODUCTION: "Establish baseline, show core wound/lie",
            EvolutionStage.INCITING: "React to inciting incident, want activated",
            EvolutionStage.REACTION: "React to escalating events, lie reinforced",
            EvolutionStage.TESTING: "Values tested, lie challenged",
            EvolutionStage.CRISIS: "Dark night - lie shattered, rock bottom",
            EvolutionStage.TRANSFORMATION: "Active choice to change, embrace need",
            EvolutionStage.INTEGRATION: "New behavior stabilized, relationships heal",
            EvolutionStage.RESOLUTION: "Final state - want/need resolved",
        }
        return focus_map.get(stage, "")

    def _get_key_beat_for_episode(self, arc: CharacterArc, episode: int) -> str:
        """Get the key character beat for an episode."""
        # Check for turning points
        for tp in arc.turning_points:
            if tp["episode"] == episode:
                return tp["event"]

        # Default beat based on stage
        stage = arc.get_stage_for_episode(episode)
        beat_map = {
            EvolutionStage.INTRODUCTION: "Establishing moment",
            EvolutionStage.INCITING: "Inciting reaction",
            EvolutionStage.REACTION: "Reactive moment",
            EvolutionStage.TESTING: "Test of values",
            EvolutionStage.CRISIS: "Breaking point",
            EvolutionStage.TRANSFORMATION: "Moment of choice",
            EvolutionStage.INTEGRATION: "New behavior shown",
            EvolutionStage.RESOLUTION: "Final resolution",
        }
        return beat_map.get(stage, "Character moment")

    def validate_all_arcs(self) -> dict[str, list[str]]:
        """Validate all character arcs."""
        results = {}
        for char_id, arc in self.characters.items():
            results[char_id] = arc.validate_arc()
        return results

    def get_ensemble_episodes(self) -> list[int]:
        """Get episodes where ensemble interactions peak."""
        return self.ensemble_episodes

    def get_relationship_dynamic(self, char1: str, char2: str, episode: int) -> str | None:
        """Get relationship dynamic between two characters at an episode."""
        key = f"{char1}-{char2}"
        reverse_key = f"{char2}-{char1}"

        for key in [key, reverse_key]:
            if key in self.relationship_matrix:
                dynamics = self.relationship_matrix[key]
                # Find most recent dynamic before or at episode
                for dyn in reversed(dynamics):
                    if dyn["episode"] <= episode:
                        return dyn["dynamic"]
        return None

    def set_relationship_dynamic(self, char1: str, char2: str, episode: int, dynamic: str) -> None:
        """Set relationship dynamic at an episode."""
        key = f"{char1}-{char2}"
        if key not in self.relationship_matrix:
            self.relationship_matrix[key] = []
        self.relationship_matrix[key].append({
            "episode": episode,
            "dynamic": dynamic,
        })
        self.relationship_matrix[key].sort(key=lambda x: x["episode"])


# Default planner
default_planner = CharacterEvolutionPlanner(season_id="season_1")
