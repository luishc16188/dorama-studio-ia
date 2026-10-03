"""
Visual Director Agent - Directs visual style, cinematography, and aesthetics.
"""

import logging
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.agents.schemas.visual_director_schemas import (
    VisualDirectorInput,
    VisualDirectorOutput,
)

logger = logging.getLogger(__name__)


class VisualDirectorAgent(BaseAgent[VisualDirectorInput, VisualDirectorOutput]):
    """
    Agent 10: Visual Director
    Directs visual style, cinematography, and aesthetics.
    """

    def __init__(self):
        super().__init__("VisualDirectorAgent")

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the visual director agent."""
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

    def _process(self, validated_input: VisualDirectorInput) -> VisualDirectorOutput:
        """
        Process the context to provide visual direction.

        Args:
            validated_input: Contains 'universe' and 'visual_requirements'.

        Returns:
            VisualDirectorOutput with 'visual_direction' and 'status'.
        """
        try:
            logger.info(
                f"Visual Director agent processing episode {validated_input.episode_num if validated_input.episode_num else 'unknown'}"
            )

            # Combine universe and visual requirements into visual direction
            visual_direction = {}
            visual_direction.update(validated_input.universe)
            visual_direction.update(validated_input.visual_requirements)

            # Optionally add some default fields if missing
            visual_direction.setdefault("style", "cinematic")
            visual_direction.setdefault("aesthetic", "high_quality")

            return VisualDirectorOutput(
                visual_direction=visual_direction, status="completed"
            )

        except Exception as e:
            logger.error(f"Visual Director failed: {e!s}")
            return VisualDirectorOutput(visual_direction={}, status="error")


if __name__ == "__main__":
    print("VisualDirectorAgent module loaded successfully")
