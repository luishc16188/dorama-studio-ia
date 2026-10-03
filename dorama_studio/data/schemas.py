from __future__ import annotations

# ==================== DATA SCHEMAS ====================
from typing import Any

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            # Add any custom encoders if needed
        },
    )


class Shot(BaseSchema):
    shot_id: str
    visual_ref_prompt: str
    narrative_intent: str
    emotional_target: str
    characters: list[str] = []


class Storyboard(BaseSchema):
    episode_num: int
    shots: list[Shot]
    title: str | None = None


class Keyframe(BaseSchema):
    frame_number: int
    description: str
    prompt: str


class VideoClip(BaseSchema):
    clip_id: str
    description: str
    duration: float
    prompt: str


class Timeline(BaseSchema):
    clips: list[VideoClip]
    total_duration: float


class VoiceDirection(BaseSchema):
    character_id: str
    emotion: str
    text: str
    voice_settings: dict[str, Any] = {}


class SFXLayer(BaseSchema):
    layer_id: str
    description: str
    sound_file: str
    volume: float = 1.0
    start_time: float
    end_time: float


class MusicTimeline(BaseSchema):
    tracks: list[dict[str, Any]]  # Simplified for now


class SubtitleData(BaseSchema):
    subtitles: list[dict[str, Any]]  # Simplified


class AnalyticsReport(BaseSchema):
    report: dict[str, Any]


class FeedbackInstructions(BaseSchema):
    instructions: list[str]


class StoryArchitecture(BaseSchema):
    act_structure: dict[str, Any]
    character_arcs: list[dict[str, Any]]


class Universe(BaseSchema):
    name: str
    logline: str
    visual_identity: dict[str, Any]
    tone: str
    setting_primary: str
    setting_secondary: list[str]
    rules_of_world: list[str]
    central_secret: str


class Script(BaseSchema):
    scene_number: int
    dialogue: str
    action: str
    # Extended fields for full episode script
    episode_num: int = 1
    total_episodes: int = 20
    scenes: list[Any] = []
    hook_used: Any | None = None
    cliffhanger: Any | None = None
    cta: Any | None = None
    total_duration: float = 90.0


# ==================== ENUMS ====================

from enum import Enum


class Genre(BaseSchema):
    name: str
    description: str
    typical_episodes: int
    typical_duration: int  # in seconds
    tropes: list[str]
    audience_target: str
    key_emotions: list[str]
    visual_style: str
    music_style: str
    pacing: str


class CTAType(str, Enum):
    MORAL_DILEMMA = "moral_dilemma"
    REVENGE_CHOICE = "revenge_choice"
    IDENTITY_TEASE = "identity_tease"
    TEAM_WAR = "team_war"


class HookCategory(str, Enum):
    betrayal = "betrayal"
    humiliation = "humiliation"
    power_reveal = "power_reveal"
    identity_shock = "identity_shock"
    identity = "identity"
    mystery = "mystery"
    revelation = "revelation"
    threat = "threat"
    moral_dilemma = "moral_dilemma"
    visual_shock = "visual_shock"
    prohibition = "prohibition"
    impossible_romance = "impossible_romance"
    revenge = "revenge"
    question = "question"


# ==================== CORE SCHEMAS ====================


class PhysicalTraits(BaseSchema):
    height_cm: int
    build: str
    hair_color: str
    hair_style: str
    eye_color: str
    skin_tone: str
    distinguishing_marks: list[str] = []
    age_apparent: int
    bone_structure: str
    face_shape: str = "oval"


class MicroExpressions(BaseSchema):
    tell: str
    eye_dart: str
    micro_smile: bool
    jaw_clench: bool
    breath_hitch: bool


class VoiceProfile(BaseSchema):
    voice_id: str
    accent: str
    pitch_range: str
    speaking_rate: str
    breathiness: float
    roughness: float
    emotional_range: dict[str, float]


class Wardrobe(BaseSchema):
    signature_style: str
    color_palette: list[str]
    key_items: list[str]
    accessories: list[str]


class ContinuityRules(BaseSchema):
    locked_traits: list[str]
    allowed_variations: dict[str, list[str]]
    drift_tolerance: float
    deform_prohibited: list[str]
    master_reference_prompt: str
    psychological_arc_by_episode: list[dict[str, Any]] = []


class CharacterBibleEntry(BaseSchema):
    id: str
    name: str
    role: str
    archetype: str
    want: str
    need: str
    lie: str
    ghost: str
    secret: str
    moral_line: str = ""
    contradiction: str = ""
    archetype_subversion: str = ""
    physical: PhysicalTraits
    micro_expressions: MicroExpressions
    voice_profile: VoiceProfile
    wardrobe: Wardrobe
    continuity_rules: ContinuityRules


class EpisodeBlueprint(BaseSchema):
    ep: int
    hook_category: HookCategory
    core_conflict: str
    twist: str
    cliffhanger: str
    cta_type: CTAType
    subversion_applied: str = ""


class CliffhangerSpec(BaseSchema):
    type: str
    text: str
    visual_hook: str
    leads_to_next: str


class CTASpec(BaseSchema):
    text: str
    type: str
    leads_to: str
    platform_adapted: dict[str, str] = {}


# ==================== CINEMATIC SPECS ====================


class ShotType(str, Enum):
    ECU = "ECU"
    CU = "CU"
    MCU = "MCU"
    MS = "MS"
    WS = "WS"


class CameraAngle(str, Enum):
    low_angle = "low_angle"
    high_angle = "high_angle"
    eye_level = "eye_level"
    dutch_angle = "dutch_angle"
    overhead = "overhead"


class CameraMovement(str, Enum):
    push_in = "push_in"
    pull_out = "pull_out"
    whip_pan = "whip_pan"
    rack_focus = "rack_focus"
    dolly_in = "dolly_in"
    crane_up = "crane_up"
    orbital = "orbital"
    speed_ramp = "speed_ramp"


class CameraSpec(BaseSchema):
    shot_type: ShotType | str
    angle: CameraAngle | str
    movement: CameraMovement | str
    lens: str
    focus_pull: str = ""


class LightingSpec(BaseSchema):
    key_light: str
    fill_light: str
    backlight: str
    color_temperature: str
    mood: str
    ratio: str = ""
    practical: str = ""


class SoundSpec(BaseSchema):
    ambience: str
    sfx: list[str]
    music_cue: dict[str, Any]
    silence_before: float = 0.0
    silence_drop: bool = False
    frequency_hz: float = 0.0
    file_spec: str = ""
    purpose: str = ""


class SceneBeat(BaseSchema):
    beat_name: str
    time_range: str
    duration: float
    action: str
    camera: CameraSpec
    sound: SoundSpec
    emotion: str


class StoryboardShot(BaseSchema):
    shot_id: str
    beat: str
    duration: float
    shot_type: ShotType | str
    angle: CameraAngle | str
    movement: CameraMovement | str
    action: str
    characters: list[str] = []
    expressions: dict[str, str] = {}
    lighting: LightingSpec
    lens: str = ""
    focus_pull: str = ""
    transition_to_next: str = ""
    visual_ref_prompt: str = ""
    narrative_intent: str = ""
    emotional_target: str = ""
    beat_energy: int = 5
    character_references: dict[str, Any] = {}
    setting: str = ""
    sfx: list[str] = []
    ambience: str = ""
    micro_expressions: dict[str, Any] = {}
    volumetric: dict[str, Any] = {}
    audio_cues: dict[str, Any] = {}
    pattern_interrupts: list[dict[str, Any]] = []
    color_grade: dict[str, Any] = {}
    safe_zones: dict[str, Any] = {}
    shot_intent: str = ""


class MusicTimelineEntry(BaseSchema):
    start_sec: float
    end_sec: float
    track_genre: str
    bpm: int
    volume_db: float
    fade_in: float = 0.0
    fade_out: float = 0.0
    leitmotif: str = ""
    action: str = ""


class SubtitleEntry(BaseSchema):
    start: float
    end: float
    text: str
    highlight_words: list[dict[str, Any]] = []
    animation: str = ""
    position: dict[str, int] = {}
    style: dict[str, Any] = {}


class EditorEffect(BaseSchema):
    timestamp: float
    type: str
    shot: str = ""
    target: str = ""
    from_shot: str = ""
    to_shot: str = ""
    duration_sec: float = 0.0


class EpisodeVerdict(str, Enum):
    PASS = "pass"
    REWRITE = "rewrite"
    HUMAN_REVIEW = "human_review"


class ScoreBreakdown(BaseSchema):
    hook: float = 0.0
    dialogue_quality: float = 0.0
    story_structure: float = 0.0
    emotional_damage: float = 0.0
    retention_cadence: float = 0.0
    character_voice: float = 0.0
    visual_potential: float = 0.0
    audio_design: float = 0.0
    cliffhanger: float = 0.0
    cta_tribal: float = 0.0


# ==================== AGENT OUTPUT SCHEMAS ====================


class TrendHunterAgentOutputSchema(BaseSchema):
    top_trends: list[dict[str, Any]]
    emerging_tropes: list[dict[str, Any]]
    saturated_tropes_to_avoid: list[dict[str, Any]]
    audio_trends: list[dict[str, Any]]
    visual_trends: list[dict[str, Any]]
    format_innovations: list[dict[str, Any]]
    recommended_theme_for_season: str


class ViralAnalystAgentOutputSchema(BaseSchema):
    hook_analysis: dict[str, Any]
    structure_analysis: dict[str, Any]
    character_analysis: dict[str, Any]
    visual_analysis: dict[str, Any]
    audio_analysis: dict[str, Any]
    cta_analysis: dict[str, Any]
    outlier_mechanisms: list[dict[str, Any]]
    actionable_insights: list[str]
    viral_ruleset: list[str]


class OriginalityEngineAgentOutputSchema(BaseSchema):
    originality_score: float
    cliche_flags: list[str]
    plagiarism_risk: float
    mutation_budget: float


class StoryArchitectAgentOutputSchema(BaseSchema):
    story_architecture: dict[
        str, Any
    ]  # We'll use the StoryArchitecture schema but as dict for flexibility
    # Alternatively, we could reference the StoryArchitecture schema directly, but we want output schema to be simple.
    # We'll do: story_architecture: StoryArchitecture
    # But note: we are in the same file, so we can reference.
    # However, to avoid circular reference issues, we'll use Dict for now and change later if needed.
    # Let's use the actual schema.
    story_architecture: StoryArchitecture


class MasterWriterAgentOutputSchema(BaseSchema):
    episode_blueprints: list[EpisodeBlueprint]
    scripts: list[Script]


class HookEngineAgentOutputSchema(BaseSchema):
    top_5_hooks: list[dict[str, Any]]
    all_candidates_count: int
    mechanism_coverage: dict[str, int]


class CTAWriterAgentOutputSchema(BaseSchema):
    cta_options: list[dict[str, Any]]
    selected_cta: dict[str, Any]


class EpisodeScorerAgentOutputSchema(BaseSchema):
    episode_score: float
    verdict: EpisodeVerdict
    breakdown: dict[str, Any]  # We'll use ScoreBreakdown but as dict for simplicity
    feedback: list[dict[str, Any]]


class StoryboardAgentOutputSchema(BaseSchema):
    storyboard: Storyboard


class VisualAgentOutputSchema(BaseSchema):
    episode_num: int
    visual_prompts: list[
        dict[str, Any]
    ]  # each element: {shot_id, prompt, negative_prompt, params}
    character_consistency_notes: dict[str, Any]
    generation_ready: bool


class KeyframeAgentOutputSchema(BaseSchema):
    keyframes: list[Keyframe]


class VideoAgentOutputSchema(BaseSchema):
    video_clips: list[VideoClip]


class EditorAgentOutputSchema(BaseSchema):
    timeline: Timeline


class SubtitleAgentOutputSchema(BaseSchema):
    subtitle_data: SubtitleData


class VoiceDirectorAgentOutputSchema(BaseSchema):
    voice_directions: list[VoiceDirection]


class SoundDesignerAgentOutputSchema(BaseSchema):
    sfx_layers: list[SFXLayer]


class MusicSupervisorAgentOutputSchema(BaseSchema):
    music_timeline: MusicTimeline


class PublisherAgentOutputSchema(BaseSchema):
    published_episodes: dict[
        str, dict[str, Any]
    ]  # platform -> episode_id -> publish info


class SEOOptimizerAgentOutputSchema(BaseSchema):
    seo_recommendations: dict[str, Any]


class AnalyticsEngineAgentOutputSchema(BaseSchema):
    analytics_report: AnalyticsReport


class FeedbackLoopAgentOutputSchema(BaseSchema):
    feedback_instructions: FeedbackInstructions


# Update forward references
