"""
DoramaState - Small, serializable, reference-oriented state for LangGraph orchestration.
"""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import uuid
from operator import add
from langgraph.channels import LastValue
from langgraph.graph import add_messages
from typing import Annotated


def merge_dicts(left: dict, right: dict) -> dict:
    """Merge two dictionaries, with right taking precedence."""
    result = left.copy()
    result.update(right)
    return result


def merge_artifact_refs(left: dict, right: dict) -> dict:
    """Merge artifact refs, combining lists for each key."""
    result = {k: list(v) for k, v in left.items()}
    for k, v in right.items():
        if k in result:
            # Combine lists, avoiding duplicates
            # Use string representation for unhashable types
            existing_strs = {str(item) for item in result[k]}
            for item in v:
                if str(item) not in existing_strs:
                    result[k].append(item)
                    existing_strs.add(str(item))
        else:
            result[k] = list(v)
    return result


def merge_stage(left: str, right: str) -> str:
    """Merge stage - use the right (latest) value."""
    return right


def merge_updated_at(left: datetime, right: datetime) -> datetime:
    """Merge updated_at - use the right (latest) value."""
    return right


def merge_list(left: list, right: list) -> list:
    """Merge lists - extend left with right, avoiding duplicates."""
    result = list(left)
    for item in right:
        if item not in result:
            result.append(item)
    return result


def merge_dict_str_str(left: dict[str, str], right: dict[str, str]) -> dict[str, str]:
    """Merge dict[str, str] - right takes precedence."""
    result = left.copy()
    result.update(right)
    return result


def merge_dict_str_any(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """Merge dict[str, Any] - right takes precedence."""
    result = left.copy()
    result.update(right)
    return result


def merge_str(left: str, right: str) -> str:
    """Merge strings - use right (latest) value."""
    return right


def merge_int(left: int, right: int) -> int:
    """Merge ints - use right (latest) value."""
    return right


def merge_float(left: float, right: float) -> float:
    """Merge floats - use right (latest) value."""
    return right


def merge_optional_str(left: Optional[str], right: Optional[str]) -> Optional[str]:
    """Merge optional strings - use right (latest) value."""
    return right


def merge_optional_dict(left: Optional[dict], right: Optional[dict]) -> Optional[dict]:
    """Merge optional dicts - use right (latest) value."""
    return right


class DoramaState(BaseModel):
    """
    Minimal state for the production graph.
    All heavy artifacts are stored in JobStore; state holds only references/IDs.
    """
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    # Project identification - mergeable for parallel nodes
    project_id: Annotated[str, merge_str]
    season_id: Annotated[Optional[str], merge_optional_str] = None
    episode_id: Annotated[Optional[str], merge_optional_str] = None

    # Current pipeline stage - mergeable for parallel nodes
    stage: Annotated[str, merge_stage] = "intake"

    # Artifact references (IDs pointing to JobStore) - mergeable
    artifact_refs: Annotated[dict[str, list[str]], merge_artifact_refs] = Field(default_factory=dict)

    # Quality tracking - mergeable for parallel nodes
    active_quality_issues: Annotated[list[str], merge_list] = Field(default_factory=list)
    retry_budget: Annotated[int, merge_int] = 3

    # Regeneration planning
    regeneration_plan: Annotated[Optional[dict[str, Any]], merge_optional_dict] = None

    # Memory references (for learning/feedback) - mergeable
    memory_refs: Annotated[list[str], merge_list] = Field(default_factory=list)

    # Trace
    trace_id: Annotated[str, merge_str] = Field(default_factory=lambda: f"tr_{uuid.uuid4().hex[:12]}")

    # Human-in-the-loop
    human_approval: Annotated[Optional[dict[str, Any]], merge_optional_dict] = None

    # Metadata - mergeable for parallel nodes
    created_at: Annotated[datetime, merge_updated_at] = Field(default_factory=datetime.utcnow)
    updated_at: Annotated[datetime, merge_updated_at] = Field(default_factory=datetime.utcnow)

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()

    def add_artifact_ref(self, artifact_type: str, artifact_id: str) -> None:
        """Add an artifact reference."""
        if artifact_type not in self.artifact_refs:
            self.artifact_refs[artifact_type] = []
        if artifact_id not in self.artifact_refs[artifact_type]:
            self.artifact_refs[artifact_type].append(artifact_id)
        self.touch()

    def get_latest_artifact(self, artifact_type: str) -> Optional[str]:
        """Get the most recent artifact ID for a type."""
        refs = self.artifact_refs.get(artifact_type, [])
        return refs[-1] if refs else None

    def set_human_approval(self, stage: str, approved: bool, notes: str = "") -> None:
        """Set human approval for a stage."""
        self.human_approval = {
            "stage": stage,
            "approved": approved,
            "notes": notes,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.touch()


class EpisodeProductionState(DoramaState):
    """Extended state for episode-level production."""

    # Episode-specific fields
    episode_number: Annotated[int, merge_int] = 1
    episode_title: Annotated[str, merge_str] = ""
    target_duration_sec: Annotated[float, merge_float] = 90.0
    total_episodes: Annotated[int, merge_int] = 40

    # Blueprint references
    blueprint_id: Annotated[Optional[str], merge_optional_str] = None
    hook_id: Annotated[Optional[str], merge_optional_str] = None

    # Season bible reference (for episode-level access)
    season_bible_ref: Annotated[Optional[str], merge_optional_str] = None

    # Season arc reference
    season_arc: Annotated[Optional[str], merge_optional_str] = None

    # Episode routing state
    episode_states: Annotated[dict[str, Any], merge_dict_str_any] = Field(default_factory=dict)

    # Character/Location state refs
    character_state_refs: Annotated[dict[str, str], merge_dict_str_str] = Field(default_factory=dict)
    location_state_refs: Annotated[dict[str, str], merge_dict_str_str] = Field(default_factory=dict)

    # Beat/Shot tracking
    beats: Annotated[list[dict[str, Any]], merge_list] = Field(default_factory=list)
    shots: Annotated[list[dict[str, Any]], merge_list] = Field(default_factory=list)

    # Render tracking
    shot_renders: Annotated[dict[str, dict[str, str]], merge_dict_str_any] = Field(default_factory=dict)  # shot_id -> {visual, voice, sfx, music}

    # Edit/Caption refs
    edit_timeline_id: Annotated[Optional[str], merge_optional_str] = None
    caption_track_id: Annotated[Optional[str], merge_optional_str] = None

    # Final QC
    final_qc_id: Annotated[Optional[str], merge_optional_str] = None
    final_episode_id: Annotated[Optional[str], merge_optional_str] = None


class SeasonProductionState(DoramaState):
    """Extended state for season-level production."""

    season_number: Annotated[int, merge_int] = 1
    season_arc: Annotated[Optional[str], merge_optional_str] = None
    total_episodes: Annotated[int, merge_int] = 40
    episodes_completed: Annotated[int, merge_int] = 0
    episode_states: Annotated[dict[str, EpisodeProductionState], merge_dict_str_any] = Field(default_factory=dict)
    world_bible_ref: Annotated[Optional[str], merge_optional_str] = None
    season_bible_ref: Annotated[Optional[str], merge_optional_str] = None


# Type alias for the main state used in graph
GraphState = DoramaState | EpisodeProductionState | SeasonProductionState