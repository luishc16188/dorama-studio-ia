import logging

# dorama_studio/agents/visual/visual_agent.py
"""
Visual Agent - Transforms storyboard into visual concepts and prompts for video generation.
"""

from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import Storyboard, VisualAgentOutputSchema


class VisualAgent(BaseAgent[Storyboard, VisualAgentOutputSchema]):
    """
    Visual Agent that takes a storyboard and generates visual concepts,
    prompts for video generation, and prepares assets for the keyframe agent.
    """

    InputSchema = Storyboard
    OutputSchema = VisualAgentOutputSchema  # We'll need to create this schema

    def __init__(self):
        super().__init__("VisualAgent")

    def process(self, validated_input: Storyboard) -> VisualAgentOutputSchema:
        """
        Process storyboard to generate visual concepts and generation prompts.

        Args:
            validated_input: Storyboard containing shot details

        Returns:
            VisualAgentOutputSchema with visual prompts and generation parameters
        """
        logger = logging.getLogger(__name__)
        logger.info(f"Processing storyboard for episode {validated_input.episode_num}")

        # In a real implementation, this would:
        # 1. Analyze each shot in the storyboard
        # 2. Generate detailed prompts for video generation models
        # 3. Create negative prompts
        # 4. Set generation parameters (seed, guidance_scale, etc.)
        # 5. Perform character consistency checks

        # For now, we'll create a mock but structured output
        visual_prompts = []
        for shot in validated_input.shots:
            # Generate a visual prompt based on shot details
            prompt = self._generate_visual_prompt(shot)
            negative_prompt = self._generate_negative_prompt(shot)

            visual_prompts.append(
                {
                    "shot_id": shot.shot_id,
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "params": {
                        "aspect_ratio": self._get_aspect_ratio_for_platform(),
                        "seed": abs(hash(shot.shot_id))
                        % 1000000,  # Deterministic but varied
                        "guidance_scale": 7.5,
                    },
                }
            )

        # Create output schema instance
        output = VisualAgentOutputSchema(
            episode_num=validated_input.episode_num,
            visual_prompts=visual_prompts,
            character_consistency_notes=self._generate_character_notes(validated_input),
            generation_ready=True,
        )

        return output

    def _generate_visual_prompt(self, shot) -> str:
        """Generate a detailed visual prompt for a shot."""
        # This would use the shot's narrative_intent, visual_ref_prompt, etc.
        base_prompt = f"{shot.visual_ref_prompt}, {shot.narrative_intent}, {shot.emotional_target}"

        # Add style elements from configuration if available
        if self.config and "visual_style" in self.config:
            base_prompt += f", {self.config['visual_style']}"

        return base_prompt.strip(", ")

    def _generate_negative_prompt(self, shot) -> str:
        """Generate negative prompt to avoid unwanted elements."""
        return "low quality, blurry, distorted, disfigured, bad anatomy, extra limbs"

    def _get_aspect_ratio_for_platform(self) -> str:
        """Get aspect ratio based on target platform from config."""
        if self.config and "platform" in self.config:
            platform = self.config["platform"]
            # In reality, we'd look this up from platforms.yaml
            platform_ratios = {
                "tiktok": "9:16",
                "youtube_shorts": "9:16",
                "instagram_reels": "9:16",
            }
            return platform_ratios.get(platform, "9:16")
        return "9:16"

    def _generate_character_notes(self, storyboard: Storyboard) -> dict[str, Any]:
        """Generate notes for character consistency."""
        # Extract character information from storyboard
        characters_mentioned = set()
        for shot in storyboard.shots:
            characters_mentioned.update(shot.characters)

        return {
            "characters": list(characters_mentioned),
            "consistency_check_points": ["face", "clothing", "hairstyle"],
            "reference_images_needed": len(characters_mentioned) > 0,
        }
