"""
Hook Engine Agent - Generates narrative hooks based on category and strength.
"""

import logging
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.agents.schemas.hook_engine_schemas import (
    HookEngineInput,
    HookEngineOutput,
)

logger = logging.getLogger(__name__)


class HookEngineAgent(BaseAgent[HookEngineInput, HookEngineOutput]):
    """
    Agent 8: Hook Engine
    Generates narrative hooks based on category and strength.
    """

    InputSchema = HookEngineInput
    OutputSchema = HookEngineOutput

    def __init__(self):
        super().__init__("HookEngineAgent")

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the hook engine agent."""
        result = self.process(input_data)
        # Return dict-like object with payload attribute for test compatibility
        class ResultWrapper:
            def __init__(self, payload):
                self.payload = payload
            def get(self, key, default=None):
                if isinstance(self.payload, dict):
                    return self.payload.get(key, default)
                return default
            def __getitem__(self, key):
                if isinstance(self.payload, dict):
                    return self.payload[key]
                raise KeyError(key)
            def __contains__(self, key):
                if isinstance(self.payload, dict):
                    return key in self.payload
                return False
        return ResultWrapper(result)

    def _process(self, validated_input: HookEngineInput) -> HookEngineOutput:
        """
        Process the context to generate a narrative hook.

        Args:
            validated_input: Contains 'episode_num', 'hook_category', 'hook_strength', optional 'context_data'.

        Returns:
            HookEngineOutput with 'hook_text' and 'status'.
        """
        try:
            logger.info(
                f"Hook Engine agent processing episode {validated_input.episode_num}"
            )

            category = validated_input.hook_category
            strength = validated_input.hook_strength

            # Generate hook text based on category
            if category == "betrayal":
                hook_text = "La traición revela sus verdaderos rostros"
            elif category == "humiliation":
                hook_text = "El humillado siempre tiene respuesta"
            elif category == "power_reveal":
                hook_text = "El poder se revela en los momentos más inesperados"
            elif category == "identity_shock":
                hook_text = "El impacto del impacto identitario"
            elif category == "mystery":
                hook_text = "El misterio se esconde en la sombra"
            elif category == "revelation":
                hook_text = "El impacto del impacto identitario"
            else:
                hook_text = "¿Qué sucederá a continuación?"

            # Adjust hook strength
            if strength > 0.7:
                hook_text = f"🔥 {hook_text}"
            elif strength > 0.4:
                hook_text = f"⚡ {hook_text}"
            else:
                hook_text = f"💡 {hook_text}"

            return HookEngineOutput(
                hook_text=hook_text,
                hook_category=category,
                hook_strength=strength,
                generated_at="2026-01-01T00:00:00Z",
            )

        except Exception as e:
            logger.error(f"Hook Engine failed: {e!s}")
            return HookEngineOutput(
                hook_text="",
                hook_category=validated_input.hook_category,
                hook_strength=validated_input.hook_strength,
                generated_at="",
            )


if __name__ == "__main__":
    print("HookEngineAgent module loaded successfully")
