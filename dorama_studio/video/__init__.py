"""
Video package - Video animation, audio engineering, SFX design, and model routing.
"""

from .audio_engineer import AudioEngineer, AudioPrompt
from .model_router import (
    MODEL_CAPABILITIES,
    ModelCapability,
    ModelRouter,
    ShotSpec,
    ShotType,
    ShotTypeClassifier,
    VideoModel,
    create_router,
)
from .sfx_designer import SFXDesigner, SFXEvent
from .video_animator import VideoAnimator, VideoPrompt

__all__ = [
    "MODEL_CAPABILITIES",
    "AudioEngineer",
    "AudioPrompt",
    "ModelCapability",
    "ModelRouter",
    "SFXDesigner",
    "SFXEvent",
    "ShotSpec",
    "ShotType",
    "ShotTypeClassifier",
    "VideoAnimator",
    "VideoModel",
    "VideoPrompt",
    "create_router",
]
