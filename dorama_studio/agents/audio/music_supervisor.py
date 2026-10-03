# dorama_studio/agents/audio/music_supervisor.py
"""
Music Supervisor Agent - Creates music timeline based on script and emotional context.
"""

import logging
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import (
    MusicSupervisorAgentOutputSchema,
    MusicTimeline,
    Script,
)

logger = logging.getLogger(__name__)


class MusicSupervisorAgent(BaseAgent[Script, MusicSupervisorAgentOutputSchema]):
    """
    Music Supervisor Agent that takes a script and generates a music timeline.
    """

    InputSchema = Script
    OutputSchema = MusicSupervisorAgentOutputSchema

    def __init__(self):
        super().__init__("MusicSupervisorAgent")

    def run(self, input_data: Script) -> dict[str, Any]:
        """Run the music supervisor agent."""
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

    def _process(self, validated_input: Script) -> MusicSupervisorAgentOutputSchema:
        """
        Process script to generate music timeline.

        Args:
            validated_input: Script containing scene details

        Returns:
            MusicSupervisorAgentOutputSchema with music timeline
        """
        logger.info(
            f"Processing music supervision for scene {validated_input.scene_number}"
        )

        # In a real implementation, this would:
        # 1. Analyze the script for emotional arc, pacing, and key moments
        # 2. Select appropriate music tracks, genres, and instrumentation
        # 3. Create a timeline with music cues, transitions, and layers
        # 4. Ensure music consistency and thematic coherence

        # For now, we'll create a structured output based on script content
        music_timeline = self._generate_music_timeline(validated_input)

        # Create output schema instance
        output = MusicSupervisorAgentOutputSchema(music_timeline=music_timeline)

        return output

    def _generate_music_timeline(self, script: Script) -> MusicTimeline:
        """Generate a music timeline based on script content."""
        # Determine emotion from script (similar to VoiceDirectorAgent)
        combined_text = f"{script.dialogue} {script.action}".lower()

        emotion_map = {
            "angry": ["angry", "rage", "fury", "mad", "irritated"],
            "sad": ["sad", "cry", "tears", "depressed", "lonely"],
            "happy": ["happy", "joy", "laugh", "smile", "excited"],
            "fear": ["afraid", "scared", "fear", "terrified", "worried"],
            "surprise": ["surprised", "shocked", "astonished", "amazed"],
            "romantic": ["love", "romance", "kiss", "heart", "valentine"],
            "tense": ["tense", "suspense", "mystery", "intrigue", "cliffhanger"],
            "neutral": ["neutral", "calm", "normal"],
        }

        detected_emotion = "neutral"
        for emotion, keywords in emotion_map.items():
            if any(keyword in combined_text for keyword in keywords):
                detected_emotion = emotion
                break

        # Define music genres and characteristics by emotion
        music_style_map = {
            "angry": {
                "genre": "rock",
                "tempo": "fast",
                "instrumentation": ["electric_guitar", "drums", "bass"],
            },
            "sad": {
                "genre": "piano_ballad",
                "tempo": "slow",
                "instrumentation": ["piano", "strings", "soft_pads"],
            },
            "happy": {
                "genre": "pop",
                "tempo": "upbeat",
                "instrumentation": ["synth", "guitar", "drums", "brass"],
            },
            "fear": {
                "genre": "dark_ambient",
                "tempo": "slow",
                "instrumentation": ["low_strings", "drones", "metallic_hits"],
            },
            "surprise": {
                "genre": "orchestral_hit",
                "tempo": "variable",
                "instrumentation": ["full_orchestra", "choir", "timpani"],
            },
            "romantic": {
                "genre": "romantic_ballad",
                "tempo": "medium",
                "instrumentation": ["piano", "strings", "soft_guitar"],
            },
            "tense": {
                "genre": "suspense",
                "tempo": "medium",
                "instrumentation": [
                    "staccato_strings",
                    "pulsing_synth",
                    "minimal_percussion",
                ],
            },
            "neutral": {
                "genre": "ambient",
                "tempo": "medium",
                "instrumentation": ["pads", "soft_plucks", "light_percussion"],
            },
        }

        style = music_style_map.get(detected_emotion, music_style_map["neutral"])

        # Create music tracks (simplified)
        tracks = []

        # Main theme track
        main_track = {
            "track_id": "main_theme",
            "genre": style["genre"],
            "tempo": style["tempo"],
            "instrumentation": style["instrumentation"],
            "mood": detected_emotion,
            "start_time": 0.0,
            "duration": 30.0,  # Assume 30-second scene for simplicity
            "volume_envelope": {"attack": 0.5, "sustain": 1.0, "release": 0.5},
            "variations": [
                {"time": 0.0, "description": "Main theme introduction"},
                {
                    "time": 15.0,
                    "description": "Theme development with added instrumentation",
                },
            ],
        }
        tracks.append(main_track)

        # Optional secondary track for contrast or layering
        if detected_emotion in ["happy", "romantic", "tense"]:
            secondary_track = {
                "track_id": "secondary_layer",
                "genre": "ambient_pad" if detected_emotion != "tense" else "drone",
                "tempo": "slow",
                "instrumentation": ["synth_pad", "textural_elements"],
                "mood": "background",
                "start_time": 5.0,
                "duration": 25.0,
                "volume_envelope": {"attack": 1.0, "sustain": 0.7, "release": 1.0},
            }
            tracks.append(secondary_track)

        # Create music timeline
        timeline = MusicTimeline(tracks=tracks)

        return timeline
