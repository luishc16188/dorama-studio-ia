"""
Episode Scorer Agent - Scores episodes based on narrative quality.
"""

import logging
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.agents.schemas.episode_scorer_schemas import (
    EpisodeScorerInput,
    EpisodeScorerOutput,
)

logger = logging.getLogger(__name__)


class EpisodeScorerAgent(BaseAgent[EpisodeScorerInput, EpisodeScorerOutput]):
    """
    Episode Scorer Agent - Scores episodes based on narrative quality.
    """

    InputSchema = EpisodeScorerInput
    OutputSchema = EpisodeScorerOutput

    def __init__(self):
        super().__init__("EpisodeScorerAgent")

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the episode scorer agent."""
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

    def _process(self, validated_input: EpisodeScorerInput) -> EpisodeScorerOutput:
        """
        Process the context to score an episode.

        Args:
            validated_input: Contains 'episode_num', 'episode_package', optional 'score_breakdown'.

        Returns:
            EpisodeScorerOutput with 'episode_score', 'verdict', 'breakdown', 'feedback'.
        """
        try:
            logger.info(
                f"Episode Scorer agent processing episode {validated_input.episode_num}"
            )

            episode_package = validated_input.episode_package
            score_breakdown = validated_input.score_breakdown or {}

            # Simple scoring logic based on episode package fields
            score = 75  # Base score

            # Adjust score based on episode features
            if episode_package.get("hook_category"):
                score += 10
            if episode_package.get("cliffhanger"):
                score += 15
            if episode_package.get("twist"):
                score += 10
            if episode_package.get("romance_intimacy"):
                score += 5

            # Cap score at 100
            score = min(score, 100)

            # Determine verdict
            if score >= 90:
                verdict = "PASS"
            elif score >= 75:
                verdict = "REVIEW"
            else:
                verdict = "REWRITE"

            breakdown = {
                "hook_score": 25,
                "cliffhanger_score": 15,
                "twist_score": 10,
                "romance_score": 5,
                "base_score": 75,
            }

            feedback = []
            if score < 75:
                feedback.append("Consider improving hook and cliffhanger")
            if score < 90:
                feedback.append("Consider adding more twists and romance elements")

            return EpisodeScorerOutput(
                episode_score=score,
                verdict=verdict,
                breakdown=breakdown,
                feedback=feedback,
            )

        except Exception as e:
            logger.error(f"Episode Scorer failed: {e!s}")
            return EpisodeScorerOutput(
                episode_score=0,
                verdict="ERROR",
                breakdown={},
                feedback=[f"Error: {e!s}"],
            )


if __name__ == "__main__":
    print("EpisodeScorerAgent module loaded successfully")
