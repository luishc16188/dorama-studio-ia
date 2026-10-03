# dorama_studio/agents/audio/voice_director.py
"""
Voice Director Agent - Creates voice direction for characters based on script and emotional context.
"""

import logging

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import (
    Script,
    VoiceDirection,
    VoiceDirectorAgentOutputSchema,
)

logger = logging.getLogger(__name__)


class VoiceDirectorAgent(BaseAgent[Script, VoiceDirectorAgentOutputSchema]):
    """
    Voice Director Agent that takes a script and generates voice directions for characters.
    """

    InputSchema = Script
    OutputSchema = VoiceDirectorAgentOutputSchema

    def __init__(self):
        super().__init__("VoiceDirectorAgent")

    def process(self, validated_input: Script) -> VoiceDirectorAgentOutputSchema:
        """
        Process script to generate voice directions for characters.

        Args:
            validated_input: Script containing scene details

        Returns:
            VoiceDirectorAgentOutputSchema with voice directions
        """
        logger.info(
            f"Processing voice directions for scene {validated_input.scene_number}"
        )

        # In a real implementation, this would:
        # 1. Analyze the script for emotional content and character dialogue
        # 2. Determine appropriate voice characteristics for each character
        # 3. Generate detailed voice direction including emotion, pacing, tone
        # 4. Reference voice profiles from character bible if available

        # For now, we'll create a structured but meaningful output based on script content
        voice_directions = []

        # Simple emotion detection based on keywords in dialogue and action
        dialogue_lower = validated_input.dialogue.lower()
        action_lower = validated_input.action.lower()
        combined_text = f"{dialogue_lower} {action_lower}"

        # Determine primary emotion
        emotion_map = {
            "angry": ["angry", "rage", "fury", "mad", "irritated"],
            "sad": ["sad", "cry", "tears", "depressed", "lonely"],
            "happy": ["happy", "joy", "laugh", "smile", "excited"],
            "fear": ["afraid", "scared", "fear", "terrified", "worried"],
            "surprise": ["surprised", "shocked", "astonished", "amazed"],
            "neutral": ["neutral", "calm", "normal"],
        }

        detected_emotion = "neutral"
        for emotion, keywords in emotion_map.items():
            if any(keyword in combined_text for keyword in keywords):
                detected_emotion = emotion
                break

        # Determine character IDs (simplified - in reality would come from script/character bible)
        character_ids = (
            ["protagonist", "antagonist"]
            if "protagonist" in combined_text or "antagonist" in combined_text
            else ["character_1", "character_2"]
        )

        for char_id in character_ids:
            voice_direction = VoiceDirection(
                character_id=char_id,
                emotion=detected_emotion,
                text=validated_input.dialogue,
                voice_settings={
                    "pitch": self._get_pitch_for_emotion(detected_emotion),
                    "speed": self._get_speed_for_emotion(detected_emotion),
                    "volume": self._get_volume_for_emotion(detected_emotion),
                    "emphasis": self._get_emphasis_for_emotion(
                        detected_emotion, validated_input.dialogue
                    ),
                },
            )
            voice_directions.append(voice_direction)

        # Create output schema instance
        output = VoiceDirectorAgentOutputSchema(voice_directions=voice_directions)

        return output

    def _get_pitch_for_emotion(self, emotion: str) -> float:
        """Get voice pitch modifier based on emotion."""
        pitch_map = {
            "angry": 1.2,
            "sad": 0.8,
            "happy": 1.1,
            "fear": 1.3,
            "surprise": 1.4,
            "neutral": 1.0,
        }
        return pitch_map.get(emotion, 1.0)

    def _get_speed_for_emotion(self, emotion: str) -> float:
        """Get voice speed modifier based on emotion."""
        speed_map = {
            "angry": 1.1,
            "sad": 0.9,
            "happy": 1.2,
            "fear": 1.3,
            "surprise": 1.25,
            "neutral": 1.0,
        }
        return speed_map.get(emotion, 1.0)

    def _get_volume_for_emotion(self, emotion: str) -> float:
        """Get voice volume modifier based on emotion."""
        volume_map = {
            "angry": 1.2,
            "sad": 0.8,
            "happy": 1.0,
            "fear": 0.9,
            "surprise": 1.1,
            "neutral": 1.0,
        }
        return volume_map.get(emotion, 1.0)

    def _get_emphasis_for_emotion(self, emotion: str, dialogue: str) -> list[str]:
        """Get emphasis words based on emotion and script content."""
        # Simple implementation - in reality would use NLP to find key words
        emphasis_words = []
        dialogue_words = dialogue.split()

        # Look for important nouns, verbs, adjectives
        important_indicators = ["!", "?", "important", "key", "crucial", "vital"]
        for word in dialogue_words:
            clean_word = word.strip(".,!?;:")
            if (
                any(indicator in word for indicator in important_indicators)
                or len(clean_word) > 6
            ):
                emphasis_words.append(clean_word)

        return emphasis_words[:3]  # Limit to top 3
