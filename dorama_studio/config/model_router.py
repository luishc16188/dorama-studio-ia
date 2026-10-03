#!/usr/bin/env python
"""
Model Router Intelligent - Dorama Studio IA.
Selección óptima de modelos usando freellmapi (servidor local 127.0.0.1:31415/v1)
basada en tipo de tarea, prioridad y presupuesto Creative Genome 70/20/10.

INTEGRACIÓN CON CLAUDE Y CODEX:
- freellmapi/claude-sonnet-4-5 → Narrativa alta calidad (Sonnet 4.5)
- freellmapi/claude-opus-4-5 → Máxima calidad narrativa (Opus 4.5)
- freellmapi/claude-haiku-4-5 → Velocidad narrativa (Haiku 4.5)
- freellmapi/deepseek-r1 → Razonamiento/code (DeepSeek R1)
- freellmapi/auto → Enrutador automático
"""

import logging

logger = logging.getLogger(__name__)

# Lista de modelos freellmapi disponibles en servidor local (validados)
FREELLAPI_MODELS = frozenset(
    [
        # Modelos principales para narrativa
        "freellmapi/claude-opus-4-5",
        "freellmapi/claude-sonnet-4-5",
        "freellmapi/claude-haiku-4-5",
        # Modelos de razonamiento/code
        "freellmapi/deepseek-r1",
        "freellmapi/deepseek-v3",
        "freellmapi/deepseek-v3.1",
        # Enrutador automático
        "freellmapi/auto",
        "freellmapi/fusion",
        # Otros modelos de alta calidad disponibles
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
    ]
)


class ModelInfo:
    """Metadatos de un modelo de IA (freellmapi)."""

    def __init__(
        self,
        provider: str,
        model: str,
        task_type: str,
        priority: str,
        cost_per_token: float = 0.0,
        estimated_tokens: int = 4000,
        budget_category: str = "exploration",
    ):
        self.provider = provider
        self.model = model
        self.task_type = task_type
        self.priority = priority
        self.cost_per_token = cost_per_token
        self.estimated_tokens = estimated_tokens
        self.budget_category = budget_category  # "proven", "exploration", "big_bet"

    @property
    def estimated_cost(self) -> float:
        """Costo estimado para la ejecución (freellmapi = gratuito/local)."""
        if self.cost_per_token is None or self.cost_per_token == 0:
            # freellmapi models = local server = cost 0
            return 0.0
        return self.cost_per_token * self.estimated_tokens

    @property
    def full_model_id(self) -> str:
        """ID completo del modelo (provider/model)."""
        return f"{self.provider}/{self.model}"

    @classmethod
    def validate(cls, model_id: str) -> bool:
        """Validar que el modelo existe en freellmapi."""
        return model_id in FREELLAPI_MODELS


class ModelRouter:
    """
    Router inteligente que selecciona el modelo óptimo freellmapi basándose en:
    1. Tipo de tarea y requisitos de calidad
    2. Presupuesto Creative Genome 70/20/10
    3. Prioridad de ejecución
    4. Disponibilidad en servidor local (127.0.0.1:31415/v1)
    """

    # Presupuesto Creative Genome 70/20/10
    CREATIVE_GENOME_BUDGET = {
        "proven": 70,  # 70% - modelos comprobados y seguros (Opus, Sonnet)
        "exploration": 20,  # 20% - nuevos pero confiables (Haiku, DeepSeek)
        "big_bet": 10,  # 10% - experimentales/frontier (fusion, auto)
    }

    # Registro de modelos freellmapi por tipo de tarea
    MODEL_REGISTRY = {
        # LLM - Narrative generation (usando modelos freellmapi)
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
        # Fast/Reasoning tasks
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
        # Scoring/Quality gate
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
        # Image generation (via freellmapi - si el servidor lo soporta)
        "image_keyframes": ModelInfo(
            provider="freellmapi",
            model="gemini-3.5-flash",  # multimodal capable
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
        # Video generation (si el servidor local soporta)
        "video_primary": ModelInfo(
            provider="freellmapi",
            model="kimi-k2.7-code",  # capaz de generar prompts de video
            task_type="video_primary",
            priority="high",
            cost_per_token=0.0,
            estimated_tokens=1,
            budget_category="big_bet",
        ),
        # TTS (si servidor local soporta)
        "tts_primary": ModelInfo(
            provider="freellmapi",
            model="gemini-3.5-flash",
            task_type="tts",
            priority="high",
            cost_per_token=0.0,
            estimated_tokens=180,
            budget_category="proven",
        ),
        # Music (si servidor local soporta)
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

    @classmethod
    def validate_model(cls, model_id: str) -> bool:
        """Validar que un modelo está disponible en freellmapi."""
        return ModelInfo.validate(model_id)

    @classmethod
    def get_available_models(cls) -> list:
        """Retornar lista de modelos freellmapi disponibles."""
        return sorted(FREELLAPI_MODELS)

    @classmethod
    def select_model(
        cls,
        task_type: str,
        priority: str = "medium",
        budget_remaining: dict[str, int] | None = None,
    ) -> ModelInfo | None:
        """
        Selecciona el modelo óptimo freellmapi para un tipo de tarea dado.

        Args:
            task_type: Tipo de tarea (narrative, reasoning, fast, scoring,
                       image_keyframes, character_references, video_primary, tts, music_generation)
            priority: Nivel de prioridad (low, medium, high)
            budget_remaining: Diccionario con presupuesto restante {proven, exploration, big_bet}

        Returns:
            ModelInfo del modelo seleccionado o None si no hay disponibles
        """
        if budget_remaining is None:
            budget_remaining = {
                "proven": cls.CREATIVE_GENOME_BUDGET["proven"],
                "exploration": cls.CREATIVE_GENOME_BUDGET["exploration"],
                "big_bet": cls.CREATIVE_GENOME_BUDGET["big_bet"],
            }

        # Determinar la key de búsqueda basándose en task_type y priority
        search_keys = []

        if task_type == "narrative":
            if priority == "high":
                search_keys = ["narrative_maximum", "narrative_high", "narrative_auto"]
            elif priority == "medium":
                search_keys = ["narrative_high", "narrative_medium", "narrative_auto"]
            else:
                search_keys = ["narrative_medium", "narrative_auto"]
        elif task_type == "reasoning":
            if priority == "high":
                search_keys = ["reasoning_high"]
            else:
                search_keys = ["reasoning_medium", "fast_auto"]
        elif task_type == "fast":
            if priority == "high":
                search_keys = ["fast_high", "fast_medium"]
            else:
                search_keys = ["fast_medium", "fast_auto"]
        elif task_type == "scoring":
            if priority == "high":
                search_keys = ["scoring_high"]
            else:
                search_keys = ["scoring_medium"]
        elif task_type == "image_keyframes":
            search_keys = ["image_keyframes"]
        elif task_type == "character_references":
            search_keys = ["character_references"]
        elif task_type == "video_primary":
            search_keys = ["video_primary"]
        elif task_type == "tts":
            search_keys = ["tts_primary"]
        elif task_type == "music_generation":
            search_keys = ["music_primary"]
        else:
            logger.warning(f"Unknown task_type: {task_type}")
            return None

        # Filtrar por disponibilidad de presupuesto y validar modelo
        for key in search_keys:
            if key in cls.MODEL_REGISTRY:
                model = cls.MODEL_REGISTRY[key]
                budget_cat = model.budget_category

                # Verificar que el modelo es válido en freellmapi
                if not cls.validate_model(model.full_model_id):
                    logger.warning(
                        f"Model {model.full_model_id} not available in freellmapi, skipping"
                    )
                    continue

                # Verificar que el presupuesto de esta categoría aún esté disponible
                if budget_remaining.get(budget_cat, 0) > 0:
                    budget_remaining[budget_cat] -= 1
                    logger.info(
                        f"Selected {model.full_model_id} "
                        f"(category: {budget_cat}, remaining: {budget_remaining})"
                    )
                    return model
                else:
                    logger.debug(
                        f"Budget exhausted for {budget_cat} category, trying next model"
                    )

        # Fallback: intentar cualquier modelo disponible
        for key in search_keys:
            if key in cls.MODEL_REGISTRY:
                model = cls.MODEL_REGISTRY[key]
                if not cls.validate_model(model.full_model_id):
                    continue
                for cat in cls.CREATIVE_GENOME_BUDGET:
                    if budget_remaining.get(cat, 0) > 0:
                        budget_remaining[cat] -= 1
                        logger.warning(
                            f"Using {model.full_model_id} from exhausted category {cat}"
                        )
                        return model

        logger.error(
            f"No models available for task_type={task_type}, priority={priority}"
        )
        return None

    @classmethod
    def select_model_with_budget(
        cls,
        task_type: str,
        priority: str = "medium",
        current_spend: int = 0,
        total_budget: int = 100,
    ) -> tuple[ModelInfo | None, dict[str, int]]:
        """
        Selecciona modelo considerando presupuesto actual vs total (70/20/10).
        """
        remaining = total_budget - current_spend
        budget_remaining = {
            "proven": int(remaining * 0.7),
            "exploration": int(remaining * 0.2),
            "big_bet": int(remaining * 0.1),
        }

        selection = cls.select_model(task_type, priority, budget_remaining)

        if selection:
            # freellmapi = cost 0, so no budget reduction needed
            logger.info(
                f"Model selected: {selection.full_model_id}, budget unchanged (local)"
            )

        return selection, budget_remaining


# Instancia global
model_router = ModelRouter()

if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)

    print("=== freellmapi Model Router Tests ===\n")

    # Test 1: Narrative maximum quality
    print("Test 1: Narrative maximum quality")
    model = model_router.select_model("narrative", "high")
    if model:
        print(f"  Selected: {model.full_model_id}")
        print(f"  Task: {model.task_type}, Priority: {model.priority}")
        print(f"  Budget category: {model.budget_category}")
        print(f"  Estimated cost: ${model.estimated_cost:.4f}")

    # Test 2: Narrative medium
    print("\nTest 2: Narrative medium")
    model = model_router.select_model("narrative", "medium")
    if model:
        print(f"  Selected: {model.full_model_id}")

    # Test 3: Reasoning
    print("\nTest 3: Reasoning task")
    model = model_router.select_model("reasoning", "high")
    if model:
        print(f"  Selected: {model.full_model_id}")

    # Test 4: Fast task
    print("\nTest 4: Fast task")
    model = model_router.select_model("fast", "medium")
    if model:
        print(f"  Selected: {model.full_model_id}")

    # Test 5: With budget
    print("\nTest 5: With budget tracking")
    model, budget = model_router.select_model_with_budget(
        "narrative", "high", current_spend=10, total_budget=100
    )
    if model:
        print(f"  Selected: {model.full_model_id}")
        print(f"  Budget remaining: {budget}")

    # Test 6: Validate models
    print("\nTest 6: Validate models")
    print(
        f"  claude-opus-4-5: {model_router.validate_model('freellmapi/claude-opus-4-5')}"
    )
    print(
        f"  claude-sonnet-4-5: {model_router.validate_model('freellmapi/claude-sonnet-4-5')}"
    )
    print(f"  invalid-model: {model_router.validate_model('freellmapi/invalid-model')}")

    # Test 7: List available
    print("\nTest 7: Available models (first 10)")
    models = model_router.get_available_models()[:10]
    for m in models:
        print(f"  {m}")

    print("\n=== All tests completed! ===")
