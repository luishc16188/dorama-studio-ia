"""
Router Package - Model routing for Dorama Studio IA V2.
"""

from __future__ import annotations

from .model_router import (
    CREATIVE_GENOME_BUDGET,
    MODEL_REGISTRY,
    ModelInfo,
    ModelRouter,
    TaskType,
    VideoModel,
    model_router,
)

__all__ = [
    "ModelRouter",
    "ModelInfo",
    "TaskType",
    "VideoModel",
    "model_router",
    "CREATIVE_GENOME_BUDGET",
    "MODEL_REGISTRY",
]
