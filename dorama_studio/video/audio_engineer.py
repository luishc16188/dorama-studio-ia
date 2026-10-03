"""
Audio Engineer Agent - Handles audio production: SFX, music, TTS based on script metadata.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from dorama_studio.core.master_writer import Beat, MasterScript


@dataclass
class AudioPrompt:
    """Represents audio generation instructions."""

    sfx_events: list[dict[str, Any]] = field(default_factory=list)
    music_cues: list[dict[str, Any]] = field(default_factory=list)
    tts_segments: list[dict[str, Any]] = field(default_factory=list)
    ambience: str = ""
    overall_mood: str = "neutral"
    duration_seconds: float = 5.0
    sample_rate: int = 44100


class AudioEngineer:
    """
    Generates audio prompts for SFX, music, and TTS based on script metadata.
    """

    def __init__(self):
        # SFX library organized by narrative function
        self.sfx_library = {
            "revelation": [
                {
                    "name": "paper_whisper",
                    "description": "Soft paper rustle - secret revealed",
                },
                {
                    "name": "glass_tap",
                    "description": "Light tap on glass - clue discovered",
                },
                {
                    "name": "lock_click",
                    "description": "Lock mechanism clicking - access granted",
                },
                {
                    "name": "heartbeat_rise",
                    "description": "Heartbeat increasing - realization dawning",
                },
            ],
            "threat": [
                {
                    "name": "tension_pulse_low",
                    "description": "Low pulsating tone - impending danger",
                },
                {
                    "name": "footsteps_approach",
                    "description": "Footsteps getting closer - someone approaching",
                },
                {
                    "name": "door_creak",
                    "description": "Old door creaking - unseen presence",
                },
                {
                    "name": "breath_sharp",
                    "description": "Sharp intake of breath - fear or surprise",
                },
            ],
            "emotion": [
                {
                    "name": "tear_drop",
                    "description": "Single tear hitting surface - sadness",
                },
                {
                    "name": "hug_squeeze",
                    "description": "Tight embrace - comfort or desperation",
                },
                {
                    "name": "laugh_soft",
                    "description": "Soft laughter - joy or nervousness",
                },
                {
                    "name": "whisper_intimate",
                    "description": "Close whisper - intimacy or secret",
                },
            ],
            "action": [
                {
                    "name": "punch_impact",
                    "description": "Fist impact - physical confrontation",
                },
                {
                    "name": "glass_break",
                    "description": "Glass shattering - sudden violence",
                },
                {
                    "name": "metal_clang",
                    "description": "Metal hitting metal - confrontation or alarm",
                },
                {
                    "name": "running_footsteps",
                    "description": "Rapid footsteps - chase or escape",
                },
            ],
            "transition": [
                {
                    "name": "whoosh",
                    "description": "Fast movement through air - scene change",
                },
                {
                    "name": "sweep",
                    "description": "Broad audio sweep - transition or passage of time",
                },
                {
                    "name": "swell",
                    "description": "Audio swell - emotional buildup or release",
                },
            ],
            "ambience": [
                {"name": "HVAC_hum", "description": "Background building ventilation"},
                {"name": "room_tone", "description": "Empty room ambient sound"},
                {
                    "name": "distant_traffic",
                    "description": "Faint city traffic in distance",
                },
                {
                    "name": "forest_night",
                    "description": "Nighttime forest with crickets and wind",
                },
            ],
        }

        # Music emotional mapping
        self.music_emotion_map = {
            "tension": [
                "low_drone",
                "pulsing_bass",
                "high_string_tremolo",
                "dissonant_pad",
            ],
            "sorpresa": ["sting_short", "high_pluck", "sudden_chord", "bright_arp"],
            "miedo": ["dark_pad", "sub_bass_rumble", "dissonant_cluster", "high_whine"],
            "indignacion": [
                "aggressive_rhythm",
                "distorted_guitar",
                "driving_bass",
                "metallic_percussion",
            ],
            "esperanza": [
                "uplifting_arp",
                "warm_pad",
                "glockenspiel_melody",
                "hopeful_strings",
            ],
            "dolor": [
                "solo_cello",
                "mournful_violin",
                "harp_glissando",
                "ambient_choir",
            ],
            "recompensa": [
                "major_chord_progression",
                "bright_strings",
                "plucky_guitar",
                "choir_hallelujah",
            ],
            "nueva_amenaza": [
                "rising_tension",
                "discordant_build",
                "climbing_bass",
                "heartbeat_accelerate",
            ],
            "determinacion": [
                "driving_beat",
                "anthemic_rhythm",
                "pulsing_synth",
                "motivational_gtr",
            ],
            "curiosidad": [
                "mysterious_arp",
                "plucky_bass",
                "curious_melody",
                "inquisitive_piano",
            ],
        }

        # TTS voice characteristics by emotion/character
        self.tts_voice_map = {
            "tension": {"stability": 0.3, "similarity": 0.8, "style": 0.5},
            "sorpresa": {"stability": 0.4, "similarity": 0.7, "style": 0.6},
            "miedo": {"stability": 0.2, "similarity": 0.9, "style": 0.3},
            "indignacion": {"stability": 0.5, "similarity": 0.6, "style": 0.7},
            "esperanza": {"stability": 0.6, "similarity": 0.5, "style": 0.4},
            "dolor": {"stability": 0.3, "similarity": 0.8, "style": 0.2},
            "recompensa": {"stability": 0.7, "similarity": 0.4, "style": 0.6},
            "nueva_amenaza": {"stability": 0.2, "similarity": 0.9, "style": 0.4},
            "determinacion": {"stability": 0.8, "similarity": 0.3, "style": 0.7},
            "curiosidad": {"stability": 0.5, "similarity": 0.5, "style": 0.5},
        }

    def generate_audio_prompt(
        self, script: MasterScript, character_bible: Any | None = None
    ) -> AudioPrompt:
        """
        Generate complete audio prompt for an episode.
        """
        audio_prompt = AudioPrompt()

        # Set overall ambience based on genre and setting
        audio_prompt.ambience = self._select_ambience(script.genre, script.title)

        # Process each beat for audio events
        total_duration = 0.0
        for beat in script.beats:
            beat_audio = self._process_beat_audio(beat, script, total_duration)
            # Combine SFX, music, TTS
            audio_prompt.sfx_events.extend(beat_audio["sfx"])
            audio_prompt.music_cues.extend(beat_audio["music"])
            audio_prompt.tts_segments.extend(beat_audio["tts"])
            total_duration += beat.duration

        # Add overall music theme based on emotional arc
        theme_music = self._generate_theme_music(script)
        audio_prompt.music_cues.extend(theme_music)

        audio_prompt.overall_mood = self._determine_overall_mood(script)
        audio_prompt.duration_seconds = total_duration

        return audio_prompt

    def _select_ambience(self, genre: str, title: str) -> str:
        """Select appropriate ambient sound for the scene."""
        ambience_map = {
            "romance": "room_tone with distant city muffled",
            "thriller": "HVAC_hum with occasional electrical hum",
            "fantasy": "forest_night with faint magical hum",
            "comedy": "room_tone with light background chatter",
        }
        return ambience_map.get(genre, "room_tone")

    def _process_beat_audio(
        self, beat: Beat, script: MasterScript, start_time: float
    ) -> dict[str, list[dict[str, Any]]]:
        """Process audio for a single beat."""
        result = {"sfx": [], "music": [], "tts": []}

        # Add beat-relative timestamps
        beat_start = start_time

        # SFX from beat.sound metadata
        if beat.sound and beat.sound.get("sfx"):
            for sfx_name in beat.sound["sfx"]:
                sfx_event = {
                    "time": beat_start + random.uniform(0.1, beat.duration - 0.1),
                    "name": sfx_name,
                    "duration": random.uniform(0.5, 2.0),
                    "volume": random.uniform(-20, -6),  # dB
                    "pan": random.uniform(-0.5, 0.5),  # stereo position
                }
                result["sfx"].append(sfx_event)

        # Music cue if specified
        if beat.sound and beat.sound.get("music_cue"):
            music_event = {
                "time": beat_start,
                "name": beat.sound["music_cue"],
                "duration": beat.duration * 0.8,  # Music slightly shorter than beat
                "volume": random.uniform(-18, -8),
                "loop": beat.duration > 5.0,  # Loop if beat is long enough
            }
            result["music"].append(music_event)

        # TTS from dialogue
        if beat.dialogue.strip():
            # Simple TTS - in reality would send to TTS engine
            tts_event = {
                "time": beat_start + 0.2,  # Slight delay for natural flow
                "text": beat.dialogue,
                "duration": len(beat.dialogue)
                * 0.1,  # Rough estimate: 0.1s per character
                "voice_settings": self.tts_voice_map.get(
                    beat.emotion, self.tts_voice_map["neutral"]
                ),
                "emotion": beat.emotion,
            }
            result["tts"].append(tts_event)

        # Add emotional music if not already specified
        if not (beat.sound and beat.sound.get("music_cue")):
            # Add background music based on emotion
            music_candidates = self.music_emotion_map.get(beat.emotion, ["ambient_pad"])
            selected_music = random.choice(music_candidates)
            music_event = {
                "time": beat_start,
                "name": selected_music,
                "duration": beat.duration,
                "volume": random.uniform(-22, -12),
                "loop": True,
            }
            result["music"].append(music_event)

        return result

    def _generate_theme_music(self, script: MasterScript) -> list[dict[str, Any]]:
        """Generate recurring theme music based on emotional arc."""
        theme_music = []

        # Determine main emotional theme from arc
        emotions = [beat.emotion for beat in script.beats]
        # Find most common emotion or the climax emotion
        from collections import Counter

        emotion_counts = Counter(emotions)
        main_emotion = (
            emotion_counts.most_common(1)[0][0] if emotion_counts else "esperanza"
        )

        # Create theme music cues
        theme_candidates = self.music_emotion_map.get(main_emotion, ["ambient_pad"])
        theme_name = random.choice(theme_candidates)

        # Theme appears at key moments: beginning, middle, end
        total_duration = sum(beat.duration for beat in script.beats)
        theme_times = [
            0.0,
            total_duration * 0.5,
            total_duration - 10.0,
        ]  # Start, middle, near end

        for i, time_point in enumerate(theme_times):
            if time_point > 0:
                theme_music.append(
                    {
                        "time": max(0, time_point),
                        "name": f"{theme_name}_theme",
                        "duration": 15.0,  # Theme lasts 15 seconds each time
                        "volume": random.uniform(-20, -10),
                        "loop": False,
                    }
                )

        return theme_music

    def _determine_overall_mood(self, script: MasterScript) -> str:
        """Determine overall mood of the episode."""
        emotions = [beat.emotion for beat in script.beats]
        from collections import Counter

        emotion_counts = Counter(emotions)
        # Return most common emotion
        return emotion_counts.most_common(1)[0][0] if emotion_counts else "neutral"

    def mix_audio_timeline(
        self, audio_prompt: AudioPrompt, target_duration: float
    ) -> dict[str, Any]:
        """
        Mix all audio elements into a timeline.
        In real implementation, this would generate actual audio file.
        For now, return a structured representation.
        """
        return {
            "total_duration": target_duration,
            "sample_rate": audio_prompt.sample_rate,
            "sfx_events": sorted(audio_prompt.sfx_events, key=lambda x: x["time"]),
            "music_cues": sorted(audio_prompt.music_cues, key=lambda x: x["time"]),
            "tts_segments": sorted(audio_prompt.tts_segments, key=lambda x: x["time"]),
            "ambience": audio_prompt.ambience,
            "overall_mood": audio_prompt.overall_mood,
        }


# Convenience function
def generate_audio_prompt_from_script(
    script: MasterScript, character_bible: Any | None = None
) -> AudioPrompt:
    """Convenience function to generate audio prompt from a script."""
    engineer = AudioEngineer()
    return engineer.generate_audio_prompt(script, character_biente)


if __name__ == "__main__":
    # Quick test
    print("AudioEngineer module loaded successfully")
