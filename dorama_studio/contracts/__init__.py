"""
Contracts package - Data validation layer for all agent transitions
V2 Canonical Contracts
"""

from .character_bible import (
    CharacterAttribute,
    CharacterBible,
    CharacterConsistencyReport,
    ReferenceImage,
)
from .beat import (
    BeatSchema,
    BeatCamera,
    BeatSound,
    FractalStage,
    PatternInterruptType,
    InformationAsymmetryType,
    ShotType,
    CameraAngleType,
    CameraMovementType,
    DialogueDeliveryType,
    MicroExpressionType,
    DialogueEmotionType,
    EpisodeBeats,
    create_beat_template,
    DEFAULT_BEAT_SEQUENCE,
)
from .episode_scorer import (
    AudioScore,
    CharacterScore,
    CliffhangerScore,
    CTAScore,
    EmotionScore,
    EpisodeScore,
    HookScore,
    RetentionScore,
    StoryScore,
    VisualScore,
)
from .trend_signal import (
    SaturationLevel,
    Sentiment,
    TrendSignal,
    ViralPotential,
)
from .v2_schemas import (
    ActingSpec,
    ArtifactType,
    AudioSpec,
    BaseArtifact,
    BeatSpec,
    CameraSpec,
    CharacterIdentity,
    CharacterState,
    ContinuitySpec,
    CreativeTrace,
    DataOrigin,
    DialogueSpec,
    EmotionState,
    # Core artifacts
    EpisodeSpecV2,
    LocationBible,
    LocationState,
    MotionSpec,
    QualityReport,
    QualityState,
    # Enums and base
    SchemaVersion,
    ShotSpec,
)

__all__ = [
    # Episode scoring (legacy)
    "EpisodeScore",
    "HookScore",
    "StoryScore",
    "EmotionScore",
    "RetentionScore",
    "CharacterScore",
    "VisualScore",
    "AudioScore",
    "CliffhangerScore",
    "CTAScore",
    # Trend pipeline (legacy)
    "TrendSignal",
    "ViralPotential",
    "SaturationLevel",
    "Sentiment",
    # Character consistency (legacy)
    "CharacterBible",
    "ReferenceImage",
    "CharacterAttribute",
    "CharacterConsistencyReport",
    # V2 Canonical
    "EpisodeSpecV2",
    "ShotSpec",
    "BeatSpec",
    "CharacterIdentity",
    "CharacterState",
    "LocationBible",
    "LocationState",
    "CreativeTrace",
    "ActingSpec",
    "CameraSpec",
    "MotionSpec",
    "AudioSpec",
    "ContinuitySpec",
    "DialogueSpec",
    "QualityReport",
    "EmotionState",
    "SchemaVersion",
    "QualityState",
    "DataOrigin",
    "ArtifactType",
    "BaseArtifact",
]
