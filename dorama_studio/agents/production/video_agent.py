# dorama_studio/agents/production/video_agent.py
"""
Video Agent - Generates video clips from keyframes.
"""

import logging

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import Keyframe, VideoAgentOutputSchema, VideoClip

logger = logging.getLogger(__name__)


class VideoAgent(BaseAgent[list[Keyframe], VideoAgentOutputSchema]):
    """
    Video Agent that takes keyframes and generates video clips.
    """

    InputSchema = list[Keyframe]
    OutputSchema = VideoAgentOutputSchema

    def __init__(self):
        super().__init__("VideoAgent")

    def run(self, input_data) -> VideoAgentOutputSchema:
        """Implementación requerida por BaseAgent."""
        return self.process(input_data)

    def _process(self, validated_input) -> VideoAgentOutputSchema:
        """
        Process keyframes to generate video clips.

        Args:
            validated_input: KeyframeAgentOutputSchema containing keyframes list

        Returns:
            VideoAgentOutputSchema with generated video clips
        """
        # Extract keyframes list from the input schema
        keyframes = (
            validated_input.keyframes
            if hasattr(validated_input, "keyframes")
            else validated_input
        )

        logger.info(f"Generating video clips from {len(keyframes)} keyframes")

        # In a real implementation, this would:
        # 1. Call video generation APIs (Kling, Runway, Veo) with keyframe prompts
        # 2. Handle async generation and polling
        # 3. Download and verify generated clips
        # 4. Return clips with metadata

        # Mock output
        video_clips = []
        for i, kf in enumerate(keyframes):
            video_clips.append(
                VideoClip(
                    clip_id=f"clip_{kf.frame_number}",
                    description=f"Generated video from keyframe {kf.frame_number}",
                    duration=5.0,
                    prompt=kf.prompt,
                )
            )

        output = VideoAgentOutputSchema(video_clips=video_clips)

        return output
