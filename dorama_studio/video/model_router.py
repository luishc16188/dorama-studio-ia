"""
Video Model Router - Semantic routing by shot type (GAP 5 fix)
Replaces static fallback chain with intelligent model selection
"""

from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field


class ShotType(str, Enum):
    """Shot classification for model routing"""

    ROMANCE_INTIMATE = "romance_intimate"  # Close-ups, micro-expressions
    MULTI_CHARACTER = "multi_character"  # 2+ characters interacting
    ACTION_MOVEMENT = "action_movement"  # Running, fighting, dynamic
    DIALOGUE_STATIC = "dialogue_static"  # Talking heads, minimal movement
    AUDIO_NATIVE = "audio_native"  # Lip-sync critical, singing
    ENVIRONMENTAL = "environmental"  # Establishing shots, scenery
    TEMPORAL_CONTINUITY = "temporal_continuity"  # Seamless frame-to-frame
    VISUAL_EFFECTS = "visual_effects"  # Magic, supernatural, VFX
    UNKNOWN = "unknown"


class VideoModel(str, Enum):
    """Available video generation models"""

    KLING = "kling"
    RUNWAY_GEN3 = "runway_gen3"
    VEO = "veo"
    SEEDANCE = "seedance"
    HAILUO = "hailuo"
    LUMA = "luma"
    PIKA = "pika"


class ModelCapability(BaseModel):
    """Model capability profile"""

    model: VideoModel
    strengths: list[ShotType]
    weaknesses: list[ShotType]
    max_duration_sec: int
    cost_per_second: float  # Relative cost
    quality_score: int = Field(ge=0, le=100)  # Overall quality
    latency_sec: float  # Average generation time
    supports_audio: bool = False
    supports_image_to_video: bool = True


# Model capability registry (GAP 5: semantic routing)
MODEL_CAPABILITIES: dict[VideoModel, ModelCapability] = {
    VideoModel.KLING: ModelCapability(
        model=VideoModel.KLING,
        strengths=[
            ShotType.MULTI_CHARACTER,
            ShotType.ACTION_MOVEMENT,
            ShotType.TEMPORAL_CONTINUITY,
        ],
        weaknesses=[ShotType.ROMANCE_INTIMATE, ShotType.AUDIO_NATIVE],
        max_duration_sec=120,
        cost_per_second=1.0,
        quality_score=88,
        latency_sec=45.0,
        supports_image_to_video=True,
    ),
    VideoModel.RUNWAY_GEN3: ModelCapability(
        model=VideoModel.RUNWAY_GEN3,
        strengths=[
            ShotType.ROMANCE_INTIMATE,
            ShotType.DIALOGUE_STATIC,
            ShotType.ENVIRONMENTAL,
        ],
        weaknesses=[ShotType.MULTI_CHARACTER, ShotType.ACTION_MOVEMENT],
        max_duration_sec=60,
        cost_per_second=1.5,
        quality_score=92,
        latency_sec=60.0,
        supports_image_to_video=True,
    ),
    VideoModel.VEO: ModelCapability(
        model=VideoModel.VEO,
        strengths=[
            ShotType.AUDIO_NATIVE,
            ShotType.DIALOGUE_STATIC,
            ShotType.ENVIRONMENTAL,
        ],
        weaknesses=[ShotType.ACTION_MOVEMENT],
        max_duration_sec=60,
        cost_per_second=2.0,
        quality_score=90,
        latency_sec=90.0,
        supports_audio=True,
        supports_image_to_video=True,
    ),
    VideoModel.SEEDANCE: ModelCapability(
        model=VideoModel.SEEDANCE,
        strengths=[
            ShotType.TEMPORAL_CONTINUITY,
            ShotType.ENVIRONMENTAL,
        ],
        weaknesses=[ShotType.ROMANCE_INTIMATE, ShotType.AUDIO_NATIVE],
        max_duration_sec=30,
        cost_per_second=0.8,
        quality_score=82,
        latency_sec=30.0,
        supports_image_to_video=True,
    ),
    VideoModel.HAILUO: ModelCapability(
        model=VideoModel.HAILUO,
        strengths=[
            ShotType.MULTI_CHARACTER,
            ShotType.VISUAL_EFFECTS,
        ],
        weaknesses=[ShotType.ROMANCE_INTIMATE],
        max_duration_sec=60,
        cost_per_second=1.2,
        quality_score=85,
        latency_sec=50.0,
        supports_image_to_video=True,
    ),
    VideoModel.LUMA: ModelCapability(
        model=VideoModel.LUMA,
        strengths=[ShotType.ENVIRONMENTAL, ShotType.VISUAL_EFFECTS],
        weaknesses=[ShotType.MULTI_CHARACTER],
        max_duration_sec=120,
        cost_per_second=1.0,
        quality_score=80,
        latency_sec=60.0,
        supports_image_to_video=True,
    ),
    VideoModel.PIKA: ModelCapability(
        model=VideoModel.PIKA,
        strengths=[ShotType.VISUAL_EFFECTS, ShotType.ROMANCE_INTIMATE],
        weaknesses=[ShotType.MULTI_CHARACTER, ShotType.ACTION_MOVEMENT],
        max_duration_sec=30,
        cost_per_second=0.7,
        quality_score=78,
        latency_sec=25.0,
        supports_image_to_video=True,
    ),
}


@dataclass
class ShotSpec:
    """Shot specification from storyboard"""

    shot_id: str
    description: str
    duration_sec: float
    characters: list[str]  # Character IDs in shot
    dialogue: str | None = None
    action: str | None = None
    mood: str | None = None
    camera: str | None = None
    audio_critical: bool = False


class ShotTypeClassifier:
    """Classifies shot spec into ShotType for routing"""

    def classify(self, shot: ShotSpec) -> ShotType:
        """Classify shot based on semantic analysis"""

        # Audio-native takes priority (lip-sync critical)
        if shot.audio_critical or (shot.dialogue and len(shot.dialogue) > 100):
            return ShotType.AUDIO_NATIVE

        # Multi-character
        if len(shot.characters) >= 2:
            return ShotType.MULTI_CHARACTER

        # Action/movement
        action_keywords = ["run", "fight", "chase", "jump", "fall", "dance", "action"]
        if shot.action and any(kw in shot.action.lower() for kw in action_keywords):
            return ShotType.ACTION_MOVEMENT

        # Romance/intimate
        romance_keywords = [
            "kiss",
            "hug",
            "intimate",
            "romantic",
            "close",
            "touch",
            "gaze",
        ]
        if shot.mood and any(kw in shot.mood.lower() for kw in romance_keywords):
            return ShotType.ROMANCE_INTIMATE
        if shot.action and any(kw in shot.action.lower() for kw in romance_keywords):
            return ShotType.ROMANCE_INTIMATE

        # Dialogue static
        if shot.dialogue and not shot.action:
            return ShotType.DIALOGUE_STATIC

        # Visual effects
        vfx_keywords = ["magic", "supernatural", "glow", "transform", "effect", "power"]
        if (shot.mood and any(kw in shot.mood.lower() for kw in vfx_keywords)) or (
            shot.action and any(kw in shot.action.lower() for kw in vfx_keywords)
        ):
            return ShotType.VISUAL_EFFECTS

        # Environmental
        env_keywords = [
            "landscape",
            "city",
            "room",
            "building",
            "nature",
            "sky",
            "wide",
        ]
        if shot.camera and any(
            kw in shot.camera.lower() for kw in ["wide", "establishing", "aerial"]
        ):
            return ShotType.ENVIRONMENTAL
        if shot.action and any(kw in shot.action.lower() for kw in env_keywords):
            return ShotType.ENVIRONMENTAL

        return ShotType.UNKNOWN


class ModelRouter:
    """
    Routes shot to optimal model based on shot type.
    Implements fallback chain with preference ordering.
    """

    def __init__(
        self,
        fallback_chain: list[VideoModel] | None = None,
        cost_weight: float = 0.3,
        quality_weight: float = 0.7,
    ):
        self.fallback_chain = fallback_chain or [
            VideoModel.KLING,
            VideoModel.RUNWAY_GEN3,
            VideoModel.VEO,
            VideoModel.SEEDANCE,
            VideoModel.HAILUO,
        ]
        self.cost_weight = cost_weight
        self.quality_weight = quality_weight
        self.classifier = ShotTypeClassifier()

    def route(self, shot: ShotSpec) -> VideoModel:
        """Select best model for shot"""
        shot_type = self.classifier.classify(shot)
        return self.route_by_type(shot_type, shot.duration_sec)

    def route_by_type(
        self, shot_type: ShotType, duration_sec: float = 10.0
    ) -> VideoModel:
        """Select best model for shot type with duration constraint"""

        # Score each model for this shot type
        scores = {}
        for model in self.fallback_chain:
            cap = MODEL_CAPABILITIES.get(model)
            if not cap:
                continue

            # Skip if duration exceeds model limit
            if duration_sec > cap.max_duration_sec:
                continue

            # Calculate match score
            match_score = 0.0
            if shot_type in cap.strengths:
                match_score += 100
            elif shot_type in cap.weaknesses:
                match_score -= 50
            else:
                match_score += 20  # Neutral

            # Quality and cost factors
            quality_factor = cap.quality_score
            cost_factor = 100 / (1 + cap.cost_per_second)  # Lower cost = higher score

            total_score = (
                match_score * 0.5
                + quality_factor * self.quality_weight * 50
                + cost_factor * self.cost_weight * 50
            )
            scores[model] = total_score

        if not scores:
            # Fallback to first available
            return self.fallback_chain[0]

        return max(scores, key=scores.get)

    def get_fallback_chain(self, shot: ShotSpec) -> list[VideoModel]:
        """Get ordered fallback chain for shot"""
        primary = self.route(shot)

        # Reorder fallback chain with primary first
        chain = [m for m in self.fallback_chain if m != primary]
        return [primary] + chain

    def get_model_info(self, model: VideoModel) -> ModelCapability | None:
        """Get capability info for model"""
        return MODEL_CAPABILITIES.get(model)


# Convenience function
def create_router(
    api_keys: dict[VideoModel, str] | None = None, **kwargs
) -> ModelRouter:
    """Create router with API key awareness"""
    # Filter fallback chain by available API keys
    if api_keys:
        available = [m for m in ModelRouter().fallback_chain if m in api_keys]
        kwargs["fallback_chain"] = available or list(VideoModel)

    return ModelRouter(**kwargs)
