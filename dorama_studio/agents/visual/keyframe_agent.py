# dorama_studio/agents/visual/keyframe_agent.py
"""
Keyframe Agent - Extracts keyframes from visual concepts for video generation.
"""

import logging

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import (
    Keyframe,
    KeyframeAgentOutputSchema,
    VisualAgentOutputSchema,
)

logger = logging.getLogger(__name__)


class KeyframeAgent(BaseAgent[VisualAgentOutputSchema, KeyframeAgentOutputSchema]):
    """
    Keyframe Agent that takes visual prompts and extracts key frames for video generation.
    """

    InputSchema = VisualAgentOutputSchema
    OutputSchema = KeyframeAgentOutputSchema

    def __init__(self):
        super().__init__("KeyframeAgent")

    def run(self, input_data: VisualAgentOutputSchema) -> KeyframeAgentOutputSchema:
        """Implementación requerida por BaseAgent."""
        return self.process(input_data)

    def _process(
        self, validated_input: VisualAgentOutputSchema
    ) -> KeyframeAgentOutputSchema:
        """
        Process visual prompts to extract key frames.

        Args:
            validated_input: VisualAgentOutputSchema containing visual prompts

        Returns:
            KeyframeAgentOutputSchema with extracted keyframes
        """
        logger.info(
            f"Processing visual prompts for episode {validated_input.episode_num}"
        )

        # In a real implementation, this would:
        # 1. Analyze each visual prompt
        # 2. Determine optimal keyframes for each shot
        # 3. Generate detailed descriptions for each keyframe
        # 4. Ensure visual consistency across keyframes

        # For now, we'll create a mock but structured output
        keyframes = []
        for visual_prompt in validated_input.visual_prompts:
            # Extract key information from visual prompt
            shot_id = visual_prompt.get("shot_id", "unknown")

            # Create keyframes for each shot (typically 2-3 keyframes per shot)
            keyframe_count = min(
                3, len(visual_prompt.get("prompt", "")) // 50 + 1
            )  # Simple heuristic

            for kf_idx in range(keyframe_count):
                keyframe = Keyframe(
                    frame_number=kf_idx + 1,
                    description=f"Keyframe {kf_idx + 1} for shot {shot_id} showing main action",
                    prompt=f"{visual_prompt.get('prompt', '')} keyframe {kf_idx + 1}, detailed, high quality",
                )
                keyframes.append(keyframe)

        # Create output schema instance
        output = KeyframeAgentOutputSchema(keyframes=keyframes)

        return output
