"""
SFX Designer Agent - Designs sound effects for episodes.
"""

import logging
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.agents.schemas.sfx_designer_schemas import (
    SFXDesignerInput,
    SFXDesignerOutput,
)

logger = logging.getLogger(__name__)


class SFXDesignerAgent(BaseAgent):
    """
    Agent 13: SFX Designer
    Designs sound effects for episodes.
    """

    InputSchema = SFXDesignerInput
    OutputSchema = SFXDesignerOutput

    def __init__(self):
        super().__init__("SFXDesignerAgent")

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the SFX designer agent."""
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

    def _process(self, validated_input: SFXDesignerInput) -> SFXDesignerOutput:
        """
        Process the context to design SFX.

        Args:
            validated_input: Contains 'episode_num', 'master_script', 'audio_direction'.

        Returns:
            SFXDesignerOutput with 'sfx_cues', 'status', 'total_sfx'.
        """
        try:
            logger.info(
                f"SFX Designer agent processing episode {validated_input.episode_num}"
            )

            # Extract inputs
            episode_num = validated_input.episode_num
            master_script = validated_input.master_script
            audio_direction = validated_input.audio_direction

            # Simple SFX design logic based on master script
            sfx_cues = []

            # Add some basic SFX based on common elements in master script
            if master_script.get("has_action", False):
                sfx_cues.append(
                    {
                        "sfx_id": f"sfx_{episode_num}_001",
                        "description": "Impact/Smash",
                        "timing": "00:05:00",
                        "volume": 0.8,
                        "duration": 2.0,
                    }
                )

            if master_script.get("has_dialogue", False):
                sfx_cues.append(
                    {
                        "sfx_id": f"sfx_{episode_num}_002",
                        "description": "Door Creak",
                        "timing": "00:12:30",
                        "volume": 0.6,
                        "duration": 1.5,
                    }
                )

            if master_script.get("has_emotional_scene", False):
                sfx_cues.append(
                    {
                        "sfx_id": f"sfx_{episode_num}_003",
                        "description": "Heartbeat",
                        "timing": "00:20:00",
                        "volume": 0.4,
                        "duration": 5.0,
                        "loop": True,
                    }
                )

            return SFXDesignerOutput(
                sfx_cues=sfx_cues, status="completed", total_sfx=len(sfx_cues)
            )

        except Exception as e:
            logger.error(f"SFX Designer failed: {e!s}")
            return SFXDesignerOutput(sfx_cues=[], status="error", total_sfx=0)


if __name__ == "__main__":
    print("SFXDesignerAgent module loaded successfully")
