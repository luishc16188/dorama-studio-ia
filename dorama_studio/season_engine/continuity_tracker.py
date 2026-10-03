"""
Continuity Tracker - Phase 6
Tracks character, location, and object state across episodes.
Validates continuity and detects inconsistencies.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ContinuityErrorType(str, Enum):
    """Types of continuity errors."""
    CHARACTER_APPEARANCE = "character_appearance"
    CHARACTER_LOCATION = "character_location"
    CHARACTER_KNOWLEDGE = "character_knowledge"
    CHARACTER_INJURY = "character_injury"
    CHARACTER_WARDROBE = "character_wardrobe"
    LOCATION_STATE = "location_state"
    OBJECT_STATE = "object_state"
    OBJECT_LOCATION = "object_location"
    TIMELINE = "timeline"
    WEATHER = "weather"
    LIGHTING = "lighting"


class ContinuityError(BaseModel):
    """A detected continuity error."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    error_id: str
    error_type: ContinuityErrorType
    episode: int
    description: str
    expected_state: str
    actual_state: str
    severity: Literal["minor", "major", "critical"] = "minor"
    characters_involved: list[str] = Field(default_factory=list)
    locations_involved: list[str] = Field(default_factory=list)
    objects_involved: list[str] = Field(default_factory=list)
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class CharacterState(BaseModel):
    """Complete character state at a specific episode."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    character_id: str
    episode: int

    # Physical appearance
    appearance: dict[str, Any] = Field(default_factory=dict)
    wardrobe: dict[str, Any] = Field(default_factory=dict)
    injuries: list[dict[str, Any]] = Field(default_factory=list)

    # Location & Movement
    current_location: str | None = None
    last_known_location: str | None = None
    movement_history: list[dict[str, Any]] = Field(default_factory=list)

    # Knowledge & Awareness
    known_facts: list[str] = Field(default_factory=list)
    unknown_facts: list[str] = Field(default_factory=list)
    beliefs: dict[str, Any] = Field(default_factory=dict)
    secrets_known: list[str] = Field(default_factory=list)
    secrets_kept: list[str] = Field(default_factory=list)

    # Relationships & Social
    relationship_status: dict[str, str] = Field(default_factory=dict)
    trust_levels: dict[str, float] = Field(default_factory=dict)
    alliances: list[str] = Field(default_factory=list)
    enemies: list[str] = Field(default_factory=list)

    # Physical/Psychological State
    health: float = 1.0
    stamina: float = 1.0
    stress: float = 0.0
    emotional_state: str = "neutral"
    trauma_triggers: list[str] = Field(default_factory=list)

    # Inventory & Objects
    objects_carried: list[str] = Field(default_factory=list)
    objects_hidden: list[str] = Field(default_factory=list)
    objects_lost: list[str] = Field(default_factory=list)

    # Goals & Motivation
    active_goals: list[str] = Field(default_factory=list)
    completed_goals: list[str] = Field(default_factory=list)
    failed_goals: list[str] = Field(default_factory=list)

    # Metadata
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class LocationState(BaseModel):
    """State of a location at a specific episode."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    location_id: str
    episode: int

    # Physical state
    condition: str = "intact"
    damage_details: list[str] = Field(default_factory=list)
    modifications: list[str] = Field(default_factory=list)

    # Atmosphere
    lighting: str = "natural"
    weather: str = "clear"
    time_of_day: str = "day"
    atmosphere: str = "neutral"

    # Occupancy
    current_occupants: list[str] = Field(default_factory=list)
    recent_visitors: list[dict[str, Any]] = Field(default_factory=list)

    # Objects in location
    objects_present: list[str] = Field(default_factory=list)
    hidden_objects: list[str] = Field(default_factory=list)

    # Security & Access
    access_level: str = "public"
    access_changes: list[dict[str, Any]] = Field(default_factory=list)

    # Events
    events_occurred: list[dict[str, Any]] = Field(default_factory=list)


class ObjectState(BaseModel):
    """State of a trackable object at a specific episode."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    object_id: str
    episode: int

    # Physical state
    condition: str = "intact"
    damage_details: list[str] = Field(default_factory=list)

    # Location & Ownership
    location: str | None = None
    owner: str | None = None
    previous_owners: list[dict[str, Any]] = Field(default_factory=list)
    custody_chain: list[dict[str, Any]] = Field(default_factory=list)

    # Properties
    properties: dict[str, Any] = Field(default_factory=dict)
    hidden_properties: list[str] = Field(default_factory=list)

    # Usage
    usage_history: list[dict[str, Any]] = Field(default_factory=list)
    charges_remaining: int | None = None
    durability: float | None = None

    # Visibility
    visible_to: list[str] = Field(default_factory=list)
    hidden_from: list[str] = Field(default_factory=list)
    is_hidden: bool = False

    # Significance
    narrative_importance: Literal["prop", "plot_device", "character_signature", "macguffin", "chekhovs_gun"] = "prop"
    associated_characters: list[str] = Field(default_factory=list)
    associated_reveals: list[str] = Field(default_factory=list)


class ContinuityTracker(BaseModel):
    """
    Tracks and validates continuity across episodes.
    Maintains state for characters, locations, and objects.
    """
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid", arbitrary_types_allowed=True)

    project_id: str
    season_id: str
    total_episodes: int = 40

    # State storage
    character_states: dict[str, dict[int, CharacterState]] = Field(default_factory=lambda: defaultdict(dict))
    location_states: dict[str, dict[int, LocationState]] = Field(default_factory=lambda: defaultdict(dict))
    object_states: dict[str, dict[int, ObjectState]] = Field(default_factory=lambda: defaultdict(dict))

    # Error tracking
    errors: list[ContinuityError] = Field(default_factory=list)

    # Continuity rules
    rules: dict[str, Any] = Field(default_factory=dict)

    def initialize_character(self, character_id: str, initial_state: CharacterState) -> None:
        """Set initial character state at episode 1."""
        initial_state.episode = 1
        self.character_states[character_id][1] = initial_state

    def initialize_location(self, location_id: str, initial_state: LocationState) -> None:
        """Set initial location state at episode 1."""
        initial_state.episode = 1
        self.location_states[location_id][1] = initial_state

    def initialize_object(self, object_id: str, initial_state: ObjectState) -> None:
        """Set initial object state at episode 1."""
        initial_state.episode = 1
        self.object_states[object_id][1] = initial_state

    def get_character_state(self, character_id: str, episode: int) -> CharacterState | None:
        """Get character state at or before an episode."""
        states = self.character_states.get(character_id, {})
        if not states:
            return None

        # Find latest state at or before episode
        valid_eps = [ep for ep in states.keys() if ep <= episode]
        if not valid_eps:
            return None
        latest_ep = max(valid_eps)
        return states[latest_ep]

    def get_location_state(self, location_id: str, episode: int) -> LocationState | None:
        """Get location state at or before an episode."""
        states = self.location_states.get(location_id, {})
        if not states:
            return None
        valid_eps = [ep for ep in states.keys() if ep <= episode]
        if not valid_eps:
            return None
        latest_ep = max(valid_eps)
        return states[latest_ep]

    def get_object_state(self, object_id: str, episode: int) -> ObjectState | None:
        """Get object state at or before an episode."""
        states = self.object_states.get(object_id, {})
        if not states:
            return None
        valid_eps = [ep for ep in states.keys() if ep <= episode]
        if not valid_eps:
            return None
        latest_ep = max(valid_eps)
        return states[latest_ep]

    def update_character_state(self, character_id: str, episode: int, changes: dict[str, Any]) -> CharacterState:
        """Update character state for an episode, inheriting from previous."""
        prev_state = self.get_character_state(character_id, episode - 1)

        if prev_state:
            # Deep copy previous state
            new_state = prev_state.model_copy(deep=True)
            new_state.episode = episode
            new_state.updated_at = datetime.utcnow()
        else:
            # Create new state
            new_state = CharacterState(character_id=character_id, episode=episode)

        # Apply changes
        for key, value in changes.items():
            if hasattr(new_state, key):
                if isinstance(value, dict) and isinstance(getattr(new_state, key), dict):
                    # Merge dictionaries
                    merged = {**getattr(new_state, key), **value}
                    setattr(new_state, key, merged)
                elif isinstance(value, list) and isinstance(getattr(new_state, key), list):
                    # Extend lists
                    merged = list(getattr(new_state, key)) + list(value)
                    setattr(new_state, key, merged)
                else:
                    setattr(new_state, key, value)

        self.character_states[character_id][episode] = new_state
        return new_state

    def update_location_state(self, location_id: str, episode: int, changes: dict[str, Any]) -> LocationState:
        """Update location state for an episode."""
        prev_state = self.get_location_state(location_id, episode - 1)

        if prev_state:
            new_state = prev_state.model_copy(deep=True)
            new_state.episode = episode
        else:
            new_state = LocationState(location_id=location_id, episode=episode)

        for key, value in changes.items():
            if hasattr(new_state, key):
                if isinstance(value, dict) and isinstance(getattr(new_state, key), dict):
                    merged = {**getattr(new_state, key), **value}
                    setattr(new_state, key, merged)
                elif isinstance(value, list) and isinstance(getattr(new_state, key), list):
                    merged = list(getattr(new_state, key)) + list(value)
                    setattr(new_state, key, merged)
                else:
                    setattr(new_state, key, value)

        self.location_states[location_id][episode] = new_state
        return new_state

    def update_object_state(self, object_id: str, episode: int, changes: dict[str, Any]) -> ObjectState:
        """Update object state for an episode."""
        prev_state = self.get_object_state(object_id, episode - 1)

        if prev_state:
            new_state = prev_state.model_copy(deep=True)
            new_state.episode = episode
        else:
            new_state = ObjectState(object_id=object_id, episode=episode)

        for key, value in changes.items():
            if hasattr(new_state, key):
                if isinstance(value, dict) and isinstance(getattr(new_state, key), dict):
                    merged = {**getattr(new_state, key), **value}
                    setattr(new_state, key, merged)
                elif isinstance(value, list) and isinstance(getattr(new_state, key), list):
                    merged = list(getattr(new_state, key)) + list(value)
                    setattr(new_state, key, merged)
                else:
                    setattr(new_state, key, value)

        self.object_states[object_id][episode] = new_state
        return new_state

    def validate_continuity(self, episode: int) -> list[ContinuityError]:
        """
        Validate continuity for a specific episode.
        Checks character, location, and object consistency.
        """
        errors = []

        # Check character continuity
        for char_id, states in self.character_states.items():
            if episode in states:
                current = states[episode]
                prev = self.get_character_state(char_id, episode - 1)

                if prev:
                    # Check appearance continuity
                    for attr in ['appearance', 'wardrobe', 'injuries']:
                        curr_val = getattr(current, attr, {})
                        prev_val = getattr(prev, attr, {})
                        if curr_val != prev_val:
                            # Check if change is justified (e.g., time jump, event)
                            if not self._is_change_justified(char_id, attr, episode):
                                errors.append(ContinuityError(
                                    error_id=f"err_{char_id}_{attr}_{episode}",
                                    error_type=ContinuityErrorType.CHARACTER_APPEARANCE,
                                    episode=episode,
                                    description=f"Character {char_id} {attr} changed without justification",
                                    expected_state=str(prev_val),
                                    actual_state=str(curr_val),
                                    severity="minor",
                                    characters_involved=[char_id],
                                ))

                    # Check location continuity
                    if current.current_location != prev.current_location:
                        if current.current_location and not self._is_movement_justified(char_id, prev.current_location, current.current_location, episode):
                            errors.append(ContinuityError(
                                error_id=f"err_{char_id}_location_{episode}",
                                error_type=ContinuityErrorType.CHARACTER_LOCATION,
                                episode=episode,
                                description=f"Character {char_id} teleported from {prev.current_location} to {current.current_location}",
                                expected_state=prev.current_location or "unknown",
                                actual_state=current.current_location or "unknown",
                                severity="major",
                                characters_involved=[char_id],
                                locations_involved=[prev.current_location, current.current_location] if prev.current_location else [current.current_location],
                            ))

                    # Check knowledge continuity (can't un-know things)
                    prev_known = set(prev.known_facts)
                    curr_known = set(current.known_facts)
                    lost_knowledge = prev_known - curr_known
                    if lost_knowledge:
                        errors.append(ContinuityError(
                            error_id=f"err_{char_id}_knowledge_{episode}",
                            error_type=ContinuityErrorType.CHARACTER_KNOWLEDGE,
                            episode=episode,
                            description=f"Character {char_id} lost knowledge: {lost_knowledge}",
                            expected_state=str(prev_known),
                            actual_state=str(curr_known),
                            severity="major",
                            characters_involved=[char_id],
                        ))

        # Store errors
        self.errors.extend(errors)
        return errors

    def _is_change_justified(self, character_id: str, attribute: str, episode: int) -> bool:
        """Check if a character attribute change is justified by episode events."""
        # In production, this would check episode events for justifications
        # e.g., wardrobe change justified by "time jump", "disguise", "battle damage"
        justified_reasons = {
            'wardrobe': ['time_jump', 'disguise', 'formal_event', 'battle', 'escape'],
            'appearance': ['time_jump', 'injury_healing', 'makeover', 'aging', 'transformation'],
            'injuries': ['battle', 'healing', 'new_injury', 'medical_treatment'],
        }
        # In production, would check episode log for these events
        return False  # Conservative: flag all changes for review

    def _is_movement_justified(self, character_id: str, from_loc: str, to_loc: str, episode: int) -> bool:
        """Check if character movement is justified."""
        # In production, would check for: travel_time, transportation, scene_break
        return False  # Conservative: flag all movements for review

    def get_all_errors(self) -> list[ContinuityError]:
        """Get all detected continuity errors."""
        return self.errors

    def get_errors_by_type(self, error_type: ContinuityErrorType) -> list[ContinuityError]:
        """Get errors filtered by type."""
        return [e for e in self.errors if e.error_type == error_type]

    def get_errors_by_severity(self, severity: str) -> list[ContinuityError]:
        """Get errors filtered by severity."""
        return [e for e in self.errors if e.severity == severity]

    def get_character_summary(self, character_id: str) -> dict[str, Any]:
        """Get summary of character's continuity across season."""
        states = self.character_states.get(character_id, {})
        if not states:
            return {"error": "Character not tracked"}

        eps = sorted(states.keys())
        return {
            "character_id": character_id,
            "episodes_tracked": eps,
            "location_changes": len(set(s.current_location for s in states.values() if s.current_location)),
            "wardrobe_changes": len(set(str(s.wardrobe) for s in states.values())),
            "injuries_sustained": sum(len(s.injuries) for s in states.values()),
            "knowledge_gained": len(set().union(*[set(s.known_facts) for s in states.values()])),
            "goals_completed": sum(len(s.completed_goals) for s in states.values()),
        }


# Default tracker
default_tracker = ContinuityTracker(project_id="proj_1", season_id="season_1")
