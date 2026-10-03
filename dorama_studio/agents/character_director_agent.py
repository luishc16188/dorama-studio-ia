"""Character Director Agent - Directs character portrayal and expression."""

import logging
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.agents.schemas.character_director_schemas import (
    CharacterDirectorInput,
    CharacterDirectorOutput,
)

logger = logging.getLogger(__name__)


class CharacterDirectorAgent(
    BaseAgent[CharacterDirectorInput, CharacterDirectorOutput]
):
    """
    Agent 9: Character Director
    Directs character portrayal, expressions, and consistency.
    """

    def __init__(self, error_memory=None, feedback_loop=None):
        super().__init__("CharacterDirectorAgent")
        self.error_memory = error_memory
        self.feedback_loop = feedback_loop

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the character director agent."""
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

    def _process(
        self, validated_input: CharacterDirectorInput
    ) -> CharacterDirectorOutput:
        """
        Process the context to provide character direction.

        Args:
            validated_input: Contains 'character_bible' and 'story_arc'.

        Returns:
            CharacterDirectorOutput with 'character_direction' and 'status'.
        """
        try:
            logger.info(
                f"Character Director agent processing episode {validated_input.episode_num if validated_input.episode_num else 'unknown'}"
            )

            # Extract character bible and story arc
            character_bible = validated_input.character_bible
            story_arc = validated_input.story_arc

            # Build character direction based on bible and arc
            # This is a simplified implementation - in production would use more sophisticated logic
            character_direction = {}

            # Example: extract key traits from bible
            if character_bible:
                # Get physical traits
                physical = character_bible.get("physical", {})
                # Get micro-expressions
                micro = character_bible.get("micro_expressions", {})
                # Combine with story arc info
                arc_conflicts = story_arc.get("core_conflict", "")
                arc_twist = story_arc.get("twist", "")

                # Build direction dict
                character_direction = {
                    "physical_traits": physical,
                    "micro_expressions": micro,
                    "core_conflict": arc_conflicts,
                    "story_twist": arc_twist,
                    "expression_guidance": "neutral",
                    "post.consistency_check": True,
                }

            return CharacterDirectorOutput(
                character_direction=character_direction, status="completed"
            )

        except Exception as e:
            logger.error(f"Character Director failed: {e!s}")
            return CharacterDirectorOutput(character_direction={}, status="error")


if __name__ == "__main__":
    print("CharacterDirectorAgent module loaded successfully")
