"""
Distribution Agent - Packages and optimizes content for platform distribution.
"""

import logging
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.agents.schemas.distribution_schemas import (
    DistributionInput,
    DistributionOutput,
)

logger = logging.getLogger(__name__)


class DistributionAgent(BaseAgent[DistributionInput, DistributionOutput]):
    """
    Agent 14: Distribution Agent
    Packages and optimizes content for platform distribution (TikTok, YouTube, Instagram).
    """

    InputSchema = DistributionInput
    OutputSchema = DistributionOutput

    def __init__(self):
        super().__init__("DistributionAgent")

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the distribution agent."""
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

    def _process(self, validated_input: DistributionInput) -> DistributionOutput:
        """
        Process the context to create distribution packages.

        Args:
            validated_input: Contains 'episode_num', 'video_prompts', 'audio_prompts', 'sfx_cues', 'platform'.

        Returns:
            DistributionOutput with 'distribution_packages' and 'status'.
        """
        try:
            logger.info(
                f"Distribution agent processing episode {validated_input.episode_num}"
            )

            # Generate distribution packages based on platform
            platform = validated_input.platform
            video_prompts = validated_input.video_prompts
            audio_prompts = validated_input.audio_prompts
            sfx_cues = validated_input.sfx_cues

            # Generate platform-specific packages
            packages = []
            if platform == "tiktok":
                packages.append(
                    {
                        "platform": "tiktok",
                        "video_prompt": video_prompts[0] if video_prompts else "",
                        "audio_prompt": audio_prompts[0] if audio_prompts else "",
                        "sfx_cues": sfx_cues[:2] if sfx_cues else [],
                        "publish_time": "2026-09-18T20:30:00-05:00",
                    }
                )
            elif platform == "youtube_short":
                packages.append(
                    {
                        "platform": "youtube_short",
                        "video_prompt": video_prompts[0] if video_prompts else "",
                        "audio_prompt": audio_prompts[0] if audio_prompts else "",
                        "sfx_cues": sfx_cues[:2] if sfx_cues else [],
                        "publish_time": "2026-09-18T22:30:00-05:00",
                    }
                )
            elif platform == "instagram_reels":
                packages.append(
                    {
                        "platform": "instagram_reels",
                        "video_prompt": video_prompts[0] if video_prompts else "",
                        "audio_prompt": audio_prompts[0] if audio_prompts else "",
                        "sfx_cues": sfx_cues[:2] if sfx_cues else [],
                        "publish_time": "2026-09-19T00:30:00-05:00",
                    }
                )

            return DistributionOutput(
                distribution_packages={p["platform"]: p for p in packages},
                status="completed",
                platforms_covered=list(set(p["platform"] for p in packages)),
            )

        except Exception as e:
            logger.error(f"Distribution Agent failed: {e!s}")
            return DistributionOutput(
                distribution_packages={}, status="error", platforms_covered=[]
            )


if __name__ == "__main__":
    print("DistributionAgent module loaded successfully")
