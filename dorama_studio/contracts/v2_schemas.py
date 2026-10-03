"""
Core V2 Contracts - Canonical schemas for DORAMA STUDIO IA V2.
All artifacts must use these contracts for type-safe agent communication.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SchemaVersion(str, Enum):
    V2 = "2.0"


class QualityState(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    PASS = "pass"
    FAIL = "fail"


class DataOrigin(str, Enum):
    OBSERVED = "observed"
    INFERRED = "inferred"
    SYNTHETIC = "synthetic"
    GENERATED = "generated"


class ArtifactType(str, Enum):
    SEASON_BIBLE = "season_bible"
    WORLD_BIBLE = "world_bible"
    LOCATION_BIBLE = "location_bible"
    CHARACTER_BIBLE = "character_bible"
    EPISODE_SPEC = "episode_spec"
    SCRIPT = "script"
    DIRECTOR_PLAN = "director_plan"
    STORYBOARD = "storyboard"
    SHOT_SPEC = "shot_spec"
    PROMPT_AST = "prompt_ast"
    PROVIDER_PAYLOAD = "provider_payload"
    VIDEO_ARTIFACT = "video_artifact"
    VOICE_ARTIFACT = "voice_artifact"
    SFX_ARTIFACT = "sfx_artifact"
    MUSIC_ARTIFACT = "music_artifact"
    EDIT_TIMELINE = "edit_timeline"
    SUBTITLE_TRACK = "subtitle_track"
    QC_REPORT = "qc_report"
    FINAL_EPISODE = "final_episode"
    ANALYTICS_REPORT = "analytics_report"
    CREATIVE_TRACE = "creative_trace"


class BaseArtifact(BaseModel):
    """Base class for all versioned artifacts."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    schema_version: SchemaVersion = SchemaVersion.V2
    artifact_id: str = Field(default_factory=lambda: f"art_{uuid.uuid4().hex[:12]}")
    artifact_type: ArtifactType
    project_id: str
    season_id: str | None = None
    episode_id: str | None = None
    shot_id: str | None = None
    parent_artifact_ids: list[str] = Field(default_factory=list)
    hash: str | None = None
    quality_state: QualityState = QualityState.DRAFT
    data_origin: DataOrigin = DataOrigin.GENERATED
    created_by: str  # agent name
    model_id: str | None = None
    prompt_hash: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================
# EPISODE SPECIFICATION V2
# ============================================================

class EmotionState(BaseModel):
    primary: str
    intensity: float = Field(ge=0, le=1)
    valence: float = Field(ge=-1, le=1)


class ActingSpec(BaseModel):
    facial_intent: str
    gaze_target: str | None = None
    blink_pattern: str | None = None
    breathing: str | None = None
    posture: str | None = None
    gesture: str | None = None
    micro_expression: str | None = None


class CameraSpec(BaseModel):
    shot_type: str
    framing: str
    angle: str
    lens_language: str | None = None
    movement: str | None = None
    eyeline: str | None = None
    depth_layers: list[str] = Field(default_factory=list)


class MotionSpec(BaseModel):
    primary: str
    secondary: list[str] = Field(default_factory=list)
    micro: list[str] = Field(default_factory=list)
    environmental: list[str] = Field(default_factory=list)


class AudioSpec(BaseModel):
    dialogue_ids: list[str] = Field(default_factory=list)
    ambience: list[str] = Field(default_factory=list)
    foley: list[str] = Field(default_factory=list)
    sfx: list[str] = Field(default_factory=list)
    music_state: str = "none"
    silence_window: bool = False


class ContinuitySpec(BaseModel):
    wardrobe_state: str | None = None
    prop_state: dict[str, str] = Field(default_factory=dict)
    physical_state: dict[str, str] = Field(default_factory=dict)
    location_state: str | None = None
    time_state: str | None = None
    blocked_reveals: list[str] = Field(default_factory=list)


class DialogueSpec(BaseModel):
    dialogue_id: str
    speaker_id: str
    text: str
    delivery: str
    start: float
    end: float


class BeatSpec(BaseModel):
    beat_id: str
    start: float
    end: float
    narrative_goal: str
    emotion: EmotionState
    action: str
    dialogue_ids: list[str] = Field(default_factory=list)
    acting: ActingSpec
    camera: CameraSpec
    motion: MotionSpec
    audio: AudioSpec
    information_revealed: list[str] = Field(default_factory=list)
    information_withheld: list[str] = Field(default_factory=list)
    retention_reason: str


class ShotSpec(BaseModel):
    shot_id: str
    beat_id: str
    start: float
    end: float
    characters: list[str] = Field(default_factory=list)
    location_id: str
    visual_prompt_ast_id: str
    acting: ActingSpec
    camera: CameraSpec
    motion: MotionSpec
    continuity: ContinuitySpec
    audio: AudioSpec
    required_reference_ids: list[str] = Field(default_factory=list)
    forbidden_elements: list[str] = Field(default_factory=list)


class QualityReport(BaseModel):
    state: QualityState
    score: float = Field(ge=0, le=100)
    critical_failures: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)


class EpisodeSpecV2(BaseArtifact):
    """Master production contract for a ~90 second episode."""
    artifact_type: ArtifactType = ArtifactType.EPISODE_SPEC

    episode_number: int = Field(ge=1)
    title: str
    genre: str
    target_duration_sec: float = Field(gt=0, default=90.0)
    hook_id: str
    blueprint_id: str
    character_state_ref: str
    dialogues: list[DialogueSpec] = Field(default_factory=list)
    beats: list[BeatSpec]
    shots: list[ShotSpec]
    continuity: ContinuitySpec
    quality: QualityReport
    artifact_refs: dict[str, list[str]] = Field(default_factory=dict)


# ============================================================
# CHARACTER STATE (Identity + State separation)
# ============================================================

class CharacterIdentity(BaseModel):
    """Canonical immutable identity."""
    character_id: str
    face_geometry: dict = Field(default_factory=dict)
    eye_geometry: dict = Field(default_factory=dict)
    nose: dict = Field(default_factory=dict)
    mouth: dict = Field(default_factory=dict)
    jaw: dict = Field(default_factory=dict)
    hairline: str = ""
    hair_style: str = ""
    skin: dict = Field(default_factory=dict)
    body_proportions: dict = Field(default_factory=dict)
    voice_timbre: str = ""
    age_appearance: str = ""
    signature_gestures: list[str] = Field(default_factory=list)
    posture: str = ""
    walk_style: str = ""
    reference_images: list[str] = Field(default_factory=list)


class CharacterState(BaseArtifact):
    """Mutable per-episode/shot state."""
    artifact_type: ArtifactType = ArtifactType.CHARACTER_BIBLE

    character_id: str
    identity_ref: str  # ref to CharacterIdentity artifact
    episode_id: str
    shot_id: str | None = None
    wardrobe: str = ""
    injuries: dict = Field(default_factory=dict)
    wetness: bool = False
    blood: dict = Field(default_factory=dict)
    makeup: str = ""
    fatigue: float = Field(ge=0, le=1, default=0)
    props_held: list[str] = Field(default_factory=list)
    location: str = ""
    emotion: str = ""
    knowledge: list[str] = Field(default_factory=list)
    relationships: dict[str, str] = Field(default_factory=dict)
    social_status: str = ""


# ============================================================
# LOCATION STATE
# ============================================================

class LocationBible(BaseArtifact):
    """Canonical location definition."""
    artifact_type: ArtifactType = ArtifactType.LOCATION_BIBLE

    location_id: str
    name: str
    world_id: str
    narrative_function: str
    architecture: str
    materials: list[str] = Field(default_factory=list)
    palette: list[str] = Field(default_factory=list)
    lighting_profile: dict = Field(default_factory=dict)
    time_of_day: str = "day"
    weather_profile: dict = Field(default_factory=dict)
    crowd_density: str = "medium"
    prop_set: list[str] = Field(default_factory=list)
    soundscape: str = ""
    camera_grammar: dict = Field(default_factory=dict)
    character_blocking_zones: list[str] = Field(default_factory=list)
    entrance_points: list[str] = Field(default_factory=list)
    exit_points: list[str] = Field(default_factory=list)
    reference_images: list[str] = Field(default_factory=list)


class LocationState(BaseArtifact):
    """Mutable per-episode/shot location state."""
    artifact_type: ArtifactType = ArtifactType.LOCATION_BIBLE  # same type, state variant

    location_id: str
    bible_ref: str  # ref to LocationBible
    episode_id: str
    shot_id: str | None = None
    weather: str = "clear"
    floor_wet: bool = False
    crowd_level: str = "medium"
    door_open: dict[str, bool] = Field(default_factory=dict)
    vehicle_present: bool = False
    lighting_state: str = "default"
    props: list[str] = Field(default_factory=list)


# ============================================================
# CREATIVE TRACE
# ============================================================

class VideoArtifact(BaseArtifact):
    """Rendered video output for a shot."""
    artifact_type: ArtifactType = ArtifactType.VIDEO_ARTIFACT

    shot_id: str
    duration_sec: float
    codec: str = "h264"
    resolution: str = "1080x1920"
    uri: str  # file:// or s3:// or provider-specific
    meta: dict = Field(default_factory=dict)


class CreativeTrace(BaseArtifact):
    """Immutable trace of every agent decision."""
    artifact_type: ArtifactType = ArtifactType.CREATIVE_TRACE

    trace_id: str = Field(default_factory=lambda: f"tr_{uuid.uuid4().hex[:12]}")
    episode_id: str
    scene_id: str | None = None
    shot_id: str | None = None
    stage: str
    agent: str
    model: str | None = None
    provider: str | None = None
    prompt_hash: str | None = None
    input_artifacts: list[str] = Field(default_factory=list)
    output_artifacts: list[str] = Field(default_factory=list)
    tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    attempt: int = 1
    quality_before: float | None = None
    quality_after: float | None = None
    decision: str
    decision_reason: str
    errors: list[str] = Field(default_factory=list)
    reviewers: list[str] = Field(default_factory=list)


class SubtitleEntry(BaseModel):
    """Individual subtitle entry with timing and formatting."""
    start: float
    end: float
    text: str
    highlight_words: list[dict[str, Any]] = Field(default_factory=list)
    animation: str = ""
    position: dict[str, int] = Field(default_factory=dict)
    style: dict[str, Any] = Field(default_factory=dict)
