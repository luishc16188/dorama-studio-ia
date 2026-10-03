"""
Model Router - Intelligent model selection based on task type, priority, and Creative Genome 70/20/10 budget.
Supports freellmapi models and provider capability routing.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class VideoModel(str, Enum):
    """Supported video generation models."""
    KLING = "kling"
    RUNWAY_GEN3 = "runway_gen3"
    VEO = "veo"
    SEEDANCE = "seedance"
    HAILUO = "hailuo"
    LUMA = "luma"
    PIKA = "pika"


class TaskType(str, Enum):
    """Types of tasks for model routing."""
    NARRATIVE_MAXIMUM = "narrative_maximum"
    NARRATIVE_HIGH = "narrative_high"
    NARRATIVE_MEDIUM = "narrative_medium"
    NARRATIVE_AUTO = "narrative_auto"
    REASONING_HIGH = "reasoning_high"
    REASONING_MEDIUM = "reasoning_medium"
    FAST_HIGH = "fast_high"
    FAST_MEDIUM = "fast_medium"
    FAST_AUTO = "fast_auto"
    SCORING_HIGH = "scoring_high"
    SCORING_MEDIUM = "scoring_medium"
    IMAGE_KEYFRAMES = "image_keyframes"
    CHARACTER_REFERENCES = "character_references"
    VIDEO_PRIMARY = "video_primary"
    TTS = "tts"
    MUSIC_GENERATION = "music_generation"


@dataclass
class ModelInfo:
    """Metadata about a model for routing decisions."""
    provider: str
    model: str
    task_type: str
    priority: str
    cost_per_token: float = 0.0
    estimated_tokens: int = 4000
    budget_category: str = "exploration"

    @property
    def estimated_cost(self) -> float:
        """Estimated cost for execution (freellmapi = local server = cost 0)."""
        if self.cost_per_token is None or self.cost_per_token == 0:
            return 0.0
        return self.cost_per_token * self.estimated_tokens

    @property
    def full_model_id(self) -> str:
        """Full model ID as provider/model."""
        return f"{self.provider}/{self.model}"


# FreeLLMAPI models available on local server (127.0.0.1:31415/v1)
FREELLAPI_MODELS = frozenset([
    # Narrative models
    "freellmapi/claude-opus-4-5",
    "freellmapi/claude-sonnet-4-5",
    "freellmapi/claude-haiku-4-5",
    # Reasoning/code models
    "freellmapi/deepseek-r1",
    "freellmapi/deepseek-v3",
    "freellmapi/deepseek-v3.1",
    # Auto router
    "freellmapi/auto",
    "freellmapi/fusion",
    # Other high-quality models
    "freellmapi/gemini-3.5-flash",
    "freellmapi/gemini-3.6-flash",
    "freellmapi/gemini-3.7-flash",
    "freellmapi/kimi-k2.5",
    "freellmapi/kimi-k2.6",
    "freellmapi/kimi-k2.7-code",
    "freellmapi/kimi-k3",
    "freellmapi/qwen3-coder-480b",
    "freellmapi/qwen3-coder-next",
    "freellmapi/qwen3.5-397b-a17b",
    "freellmapi/nemotron-3-ultra-550b",
    "freellmapi/gpt-oss-120b",
])

# Creative Genome 70/20/10 budget
CREATIVE_GENOME_BUDGET = {
    "proven": 70,
    "exploration": 20,
    "big_bet": 10,
}

# Model registry with task types and budget categories
MODEL_REGISTRY = {
    "narrative_maximum": ModelInfo(
        provider="freellmapi",
        model="claude-opus-4-5",
        task_type="narrative",
        priority="high",
        cost_per_token=0.0,
        estimated_tokens=4000,
        budget_category="proven",
    ),
    "narrative_high": ModelInfo(
        provider="freellmapi",
        model="claude-sonnet-4-5",
        task_type="narrative",
        priority="high",
        cost_per_token=0.0,
        estimated_tokens=4000,
        budget_category="proven",
    ),
    "narrative_medium": ModelInfo(
        provider="freellmapi",
        model="claude-haiku-4-5",
        task_type="narrative",
        priority="medium",
        cost_per_token=0.0,
        estimated_tokens=4000,
        budget_category="exploration",
    ),
    "narrative_auto": ModelInfo(
        provider="freellmapi",
        model="auto",
        task_type="narrative",
        priority="medium",
        cost_per_token=0.0,
        estimated_tokens=4000,
        budget_category="exploration",
    ),
    "reasoning_high": ModelInfo(
        provider="freellmapi",
        model="deepseek-r1",
        task_type="reasoning",
        priority="high",
        cost_per_token=0.0,
        estimated_tokens=4000,
        budget_category="proven",
    ),
    "reasoning_medium": ModelInfo(
        provider="freellmapi",
        model="deepseek-v3",
        task_type="reasoning",
        priority="medium",
        cost_per_token=0.0,
        estimated_tokens=4000,
        budget_category="exploration",
    ),
    "fast_high": ModelInfo(
        provider="freellmapi",
        model="gemini-3.5-flash",
        task_type="fast",
        priority="high",
        cost_per_token=0.0,
        estimated_tokens=2000,
        budget_category="proven",
    ),
    "fast_medium": ModelInfo(
        provider="freellmapi",
        model="gemini-3.6-flash",
        task_type="fast",
        priority="medium",
        cost_per_token=0.0,
        estimated_tokens=2000,
        budget_category="exploration",
    ),
    "fast_auto": ModelInfo(
        provider="freellmapi",
        model="auto",
        task_type="fast",
        priority="low",
        cost_per_token=0.0,
        estimated_tokens=2000,
        budget_category="big_bet",
    ),
    "scoring_high": ModelInfo(
        provider="freellmapi",
        model="claude-sonnet-4-5",
        task_type="scoring",
        priority="high",
        cost_per_token=0.0,
        estimated_tokens=2048,
        budget_category="proven",
    ),
    "scoring_medium": ModelInfo(
        provider="freellmapi",
        model="claude-haiku-4-5",
        task_type="scoring",
        priority="medium",
        cost_per_token=0.0,
        estimated_tokens=2048,
        budget_category="exploration",
    ),
    "image_keyframes": ModelInfo(
        provider="freellmapi",
        model="gemini-3.5-flash",
        task_type="image_keyframes",
        priority="high",
        cost_per_token=0.0,
        estimated_tokens=1,
        budget_category="big_bet",
    ),
    "character_references": ModelInfo(
        provider="freellmapi",
        model="gemini-3.6-flash",
        task_type="character_references",
        priority="high",
        cost_per_token=0.0,
        estimated_tokens=1,
        budget_category="big_bet",
    ),
    "video_primary": ModelInfo(
        provider="freellmapi",
        model="kimi-k2.7-code",
        task_type="video_primary",
        priority="high",
        cost_per_token=0.0,
        estimated_tokens=1,
        budget_category="big_bet",
    ),
    "tts_primary": ModelInfo(
        provider="freellmapi",
        model="gemini-3.5-flash",
        task_type="tts",
        priority="high",
        cost_per_token=0.0,
        estimated_tokens=180,
        budget_category="proven",
    ),
    "music_primary": ModelInfo(
        provider="freellmapi",
        model="gemini-3.6-flash",
        task_type="music_generation",
        priority="high",
        cost_per_token=0.0,
        estimated_tokens=1,
        budget_category="proven",
    ),
}


class ModelRouter:
    """
    Intelligent model router that selects optimal freellmapi models based on:
    1. Task type and quality requirements
    2. Creative Genome 70/20/10 budget allocation
    3. Priority of execution
    4. Availability on local freellmapi server (127.0.0.1:31415/v1)
    """

    def __init__(self):
        self.budget_remaining = CREATIVE_GENOME_BUDGET.copy()

    @classmethod
    def validate_model(cls, model_id: str) -> bool:
        """Validate that a model exists in freellmapi."""
        return model_id in FREELLAPI_MODELS

    @classmethod
    def get_available_models(cls) -> list[str]:
        """Return list of available freellmapi models."""
        return sorted(FREELLAPI_MODELS)

    @classmethod
    def select_model(
        cls,
        task_type: str,
        priority: str = "medium",
        budget_remaining: dict[str, int] | None = None,
    ) -> ModelInfo | None:
        """
        Select optimal model for a task type.

        Args:
            task_type: Type of task (narrative, reasoning, fast, scoring, etc.)
            priority: Priority level (low, medium, high)
            budget_remaining: Budget remaining per category

        Returns:
            ModelInfo for selected model or None if unavailable
        """
        if budget_remaining is None:
            budget_remaining = CREATIVE_GENOME_BUDGET.copy()

        # Map task_type + priority to registry keys
        search_keys = cls._get_search_keys(task_type, priority)

        for key in search_keys:
            if key not in MODEL_REGISTRY:
                continue

            model = MODEL_REGISTRY[key]
            budget_cat = model.budget_category

            # Validate model exists in freellmapi
            if not cls.validate_model(model.full_model_id):
                logger.warning(f"Model {model.full_model_id} not available in freellmapi, skipping")
                continue

            # Check budget availability
            if budget_remaining.get(budget_cat, 0) > 0:
                budget_remaining[budget_cat] -= 1
                logger.info(
                    f"Selected {model.full_model_id} "
                    f"(category: {budget_cat}, remaining: {budget_remaining})"
                )
                return model
            else:
                logger.debug(f"Budget exhausted for {budget_cat} category, trying next model")

        # Fallback: try any model from search keys regardless of budget
        for key in search_keys:
            if key not in MODEL_REGISTRY:
                continue
            model = MODEL_REGISTRY[key]
            if not cls.validate_model(model.full_model_id):
                continue
            for cat in CREATIVE_GENOME_BUDGET:
                if budget_remaining.get(cat, 0) > 0:
                    budget_remaining[cat] -= 1
                    logger.warning(
                        f"Using {model.full_model_id} from exhausted category {cat}"
                    )
                    return model

        logger.error(f"No models available for task_type={task_type}, priority={priority}")
        return None

    @classmethod
    def _get_search_keys(cls, task_type: str, priority: str) -> list[str]:
        """Get registry keys to search based on task type and priority."""
        search_map = {
            ("narrative", "high"): ["narrative_maximum", "narrative_high", "narrative_auto"],
            ("narrative", "medium"): ["narrative_high", "narrative_medium", "narrative_auto"],
            ("narrative", "low"): ["narrative_medium", "narrative_auto"],
            ("reasoning", "high"): ["reasoning_high"],
            ("reasoning", "medium"): ["reasoning_medium", "fast_auto"],
            ("fast", "high"): ["fast_high", "fast_medium"],
            ("fast", "medium"): ["fast_medium", "fast_auto"],
            ("scoring", "high"): ["scoring_high"],
            ("scoring", "medium"): ["scoring_medium"],
            ("image_keyframes", "high"): ["image_keyframes"],
            ("character_references", "high"): ["character_references"],
            ("video_primary", "high"): ["video_primary"],
            ("tts", "high"): ["tts_primary"],
            ("music_generation", "high"): ["music_primary"],
        }

        return search_map.get((task_type, priority), ["narrative_auto"])

    @classmethod
    def select_model_with_budget(
        cls,
        task_type: str,
        priority: str = "medium",
        current_spend: int = 0,
        total_budget: int = 100,
    ) -> tuple[ModelInfo | None, dict[str, int]]:
        """
        Select model considering current spend vs total budget (70/20/10).
        """
        remaining = total_budget - current_spend
        budget_remaining = {
            "proven": int(remaining * 0.7),
            "exploration": int(remaining * 0.2),
            "big_bet": int(remaining * 0.1),
        }

        selection = cls.select_model(task_type, priority, budget_remaining)

        if selection:
            logger.info(
                f"Model selected: {selection.full_model_id}, budget unchanged (local)"
            )

        return selection, budget_remaining

    @classmethod
    def get_fallback_chain(cls, model_id: str) -> list[str]:
        """Get fallback chain for a model."""
        fallback_map = {
            "freellmapi/claude-opus-4-5": ["freellmapi/claude-sonnet-4-5", "freellmapi/claude-haiku-4-5", "freellmapi/auto"],
            "freellmapi/claude-sonnet-4-5": ["freellmapi/claude-haiku-4-5", "freellmapi/auto"],
            "freellmapi/claude-haiku-4-5": ["freellmapi/auto"],
            "freellmapi/deepseek-r1": ["freellmapi/deepseek-v3", "freellmapi/auto"],
            "freellmapi/gemini-3.5-flash": ["freellmapi/gemini-3.6-flash", "freellmapi/auto"],
        }
        return fallback_map.get(model_id, ["freellmapi/auto"])

    @classmethod
    def get_model_capabilities(cls, model_id: str) -> dict | None:
        """Get capabilities for a specific model."""
        # This would load from config/model_router.py or similar
        return None


# Global instance
model_router = ModelRouter()
