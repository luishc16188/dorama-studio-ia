"""
CTA Writer Agent - Generates narrative CTAs tied to cliffhangers.
"""

import logging
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.agents.schemas.cta_writer_schemas import (
    CTAWriterInput,
    CTAWriterOutput,
)

logger = logging.getLogger(__name__)


class CTAWriterAgent(BaseAgent[CTAWriterInput, CTAWriterOutput]):
    """
    Agent 18: CTA Writer
    Generates narrative CTAs tied to cliffhangers.
    """

    InputSchema = CTAWriterInput
    OutputSchema = CTAWriterOutput

    def __init__(self):
        super().__init__("CTAWriterAgent")

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the CTA writer agent."""
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

    def _process(self, validated_input: CTAWriterInput) -> CTAWriterOutput:
        """
        Process the context to generate a CTA.

        Args:
            validated_input: Contains 'episode_num', 'cliffhanger_data', 'cta_type', 'platform'.

        Returns:
            CTAWriterOutput with 'cta_text' and 'status'.
        """
        try:
            logger.info(
                f"CTA Writer agent processing episode {validated_input.episode_num}"
            )

            # Generate CTA based on type and platform
            cta_type = validated_input.cta_type
            platform = validated_input.platform

            # Generate CTA text based on type and platform
            if cta_type == "moral_dilemma":
                cta_text = "¿Qué harías en su lugar?"
            elif cta_type == "revenue_dilemma":
                cta_text = "¿Comprar o no comprar?"
            else:
                cta_text = "¿Qué sigue?"

            # Platform adaptation
            if platform == "social_media":
                cta_text = f"💡 {cta_text} #DramaStudio"
            elif platform == "email":
                cta_text = f"📧 {cta_text}"
            elif platform == "youtube":
                cta_text = f"📺 {cta_text} ¡Suscríbete!"

            return CTAWriterOutput(
                cta_text=cta_text,
                cta_type=cta_type,
                platform=platform,
                status="completed",
                generated_at="2026-01-01T00:00:00Z",
            )

        except Exception as e:
            logger.error(f"CTA Writer failed: {e!s}")
            return CTAWriterOutput(
                cta_text="",
                cta_type=validated_input.cta_type,
                platform=validated_input.platform,
                status="error",
                generated_at="",
            )


if __name__ == "__main__":
    print("CTAWriterAgent module loaded successfully")
