"""
Audio Engineer Agent - Generates audio prompts for music, SFX, and voiceover.
Enhanced with DramaBox/OASIZ patterns: Music Drops, 3-Genre Progression, Amplified Foley, Sub-Bass 40Hz.
"""

import logging
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class AudioEngineerAgent(BaseAgent[dict[str, Any], dict[str, Any]]):
    """
    Agent 12: Audio Engineer
    Generates audio prompts for music, SFX, and voiceover.
    Implements:
    - Music Drops (absolute silence 0.5s pre-critical dialogue)
    - 3-Genre Musical Progression within 60-90s
    - Foley Amplification (+6dB for emotional objects: glass, pearls, silk, paper, metal)
    - Sub-Bass 40Hz Stingers on all status reversals/cliffhangers
    """

    InputSchema = None  # We'll use Dict for flexibility
    OutputSchema = None

    def __init__(self, error_memory=None, feedback_loop=None):
        super().__init__("AudioEngineerAgent")
        self.error_memory = error_memory
        self.feedback_loop = feedback_loop

    def _process(self, validated_input: dict[str, Any]) -> dict[str, Any]:
        """
        Process the context to generate audio prompts.
        Expects context to contain 'master_script' or 'breakdown' with beats including sound directives.
        Updates context with 'audio_prompts'.
        """
        try:
            # Handle case where context might be None or not a dict
            if validated_input is None:
                logger.warning(
                    "Audio Engineer received None context, returning empty dict"
                )
                return {"audio_prompts": [], "status": "empty_input"}
            elif not isinstance(validated_input, dict):
                logger.warning(
                    f"Audio Engineer received non-dict context: {type(validated_input)}, converting to dict"
                )
                validated_input = {}

            logger.info(
                f"Audio Engineer agent processing episode {validated_input.get('episode_num', 'unknown')}"
            )

            # Try multiple sources for beats
            master_script = validated_input.get("master_script", {})
            beats = master_script.get("beats", [])

            if not beats:
                breakdown = validated_input.get("breakdown", {})
                beats = breakdown.get("beats", [])

            if not beats:
                logger.warning("No beats found in context for audio engineer")
                beats = []

            audio_prompts = self._generate_audio_prompts(beats)

            return {"audio_prompts": audio_prompts, "status": "completed"}
        except (RuntimeError, ValueError, KeyError) as e:
            logger.error(f"Audio Engineer failed: {e!s}")
            return {"audio_prompts": [], "status": "error"}

    def _generate_audio_prompts(self, beats: list[dict]) -> list[dict]:
        """
        Generate detailed audio prompts for each beat based on DramaBox/OASIZ best practices.
        """
        prompts = []

        for i, beat in enumerate(beats):
            sound_directive = beat.get("sound", {})
            beat_name = beat.get("beat_name", f"beat_{i}")

            prompt = {
                "beat_name": beat_name,
                "beat_index": i,
                "ambience": sound_directive.get("ambience", "room_tone"),
                "sfx_layers": [],
                "music": {
                    "genre": "tension_ambient",
                    "bpm": 80,
                    "action": "sustain",
                    "progression_stage": self._get_progression_stage(i, len(beats)),
                },
                "silence_drop": sound_directive.get("silence_drop", False),
                "sub_bass_stinger": False,
                "voice_processing": "clean",
                "notes": "",
            }

            # Music Drop enforcement
            if sound_directive.get("silence_drop", False):
                prompt["music"]["action"] = "drop_to_silence"
                prompt["silence_duration_sec"] = 0.5
                prompt["notes"] = (
                    "MUSIC DROP: Absolute silence 0.5s before critical revelation"
                )

            # Sub-Bass 40Hz stinger on cliffhangers and status reversals
            if (
                beat_name in ["cliffhanger", "revelation", "twist1"]
                or sound_directive.get("music_cue", {}).get("action") == "stinger"
            ):
                prompt["sub_bass_stinger"] = True
                prompt["sub_bass_freq_hz"] = 40
                prompt["sub_bass_type"] = "stinger_shock"

            # Foley amplification for emotional objects
            action_text = beat.get("action", "").lower()
            dialogue_text = beat.get("dialogue", "").lower()
            combined = f"{action_text} {dialogue_text}"

            ear_candy_map = [
                (
                    "rompi",
                    "glass_break_high_fidelity",
                    "Breaking glass - ear candy +6dB",
                ),
                ("perla", "pearl_scatter_marble", "Pearls on marble - ear candy +6dB"),
                (
                    "pañuelo",
                    "silk_rustle_hq",
                    "Handkerchief silk - amplified foley +4dB",
                ),
                ("seda", "silk_rustle_hq", "Silk fabric - amplified foley +4dB"),
                ("fajo", "paper_rustle_money", "Banknotes - amplified foley +4dB"),
                ("billete", "paper_rustle_money", "Banknotes - amplified foley +4dB"),
                ("patek", "watch_click_luxury", "Patek Philippe - status marker +3dB"),
                ("reloj", "watch_click_luxury", "Luxury watch - status marker +3dB"),
            ]

            for keyword, sfx_file, desc in ear_candy_map:
                if keyword in combined:
                    prompt["sfx_layers"].append(
                        {
                            "file": sfx_file,
                            "description": desc,
                            "volume_db": 6.0,  # +6dB amplification
                            "category": "ear_candy",
                        }
                    )
                    if "silk" in keyword or "pañuelo" in keyword or "seda" in keyword:
                        break
                    if "fajo" in keyword or "billete" in keyword:
                        break
                    if "patek" in keyword or "reloj" in keyword:
                        break

            # Heartbeat sub-bass for tension
            if "heartbeat" in sound_directive.get("sfx", []) or "latido" in combined:
                prompt["sfx_layers"].append(
                    {
                        "file": "heartbeat_40hz",
                        "description": "Heartbeat sub-bass 40Hz tension layer",
                        "volume_db": 3.0,
                        "category": "sub_bass",
                    }
                )

            # Music genre progression (3-stage within episode)
            stage = self._get_progression_stage(i, len(beats))
            prompt["music"]["progression_stage"] = stage
            prompt["music"]["genre"] = self._get_genre_for_stage(stage)
            prompt["music"]["bpm"] = self._get_bpm_for_stage(stage)

            prompts.append(prompt)

        return prompts

    def _get_progression_stage(self, beat_index: int, total_beats: int) -> str:
        """Determine which stage of 3-genre progression this beat belongs to."""
        third = total_beats / 3
        if beat_index < third:
            return "setup_tension"  # Beats 0-2: Tension/Ambient
        elif beat_index < 2 * third:
            return "escalation_drive"  # Beats 3-5: Driving rhythm/Synthwave
        else:
            return "climax_resolution"  # Beats 6-8: Orchestral/Emotional

    def _get_genre_for_stage(self, stage: str) -> str:
        mapping = {
            "setup_tension": "dark_ambient_minimal",
            "escalation_drive": "synthwave_dark_pop",
            "climax_resolution": "orchestral_emotional_epic",
        }
        return mapping.get(stage, "tension_ambient")

    def _get_bpm_for_stage(self, stage: str) -> int:
        mapping = {
            "setup_tension": 72,
            "escalation_drive": 128,
            "climax_resolution": 90,
        }
        return mapping.get(stage, 80)

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the audio engineer agent."""
        return self.process(input_data)


if __name__ == "__main__":
    print("AudioEngineerAgent module loaded successfully with DramaBox/OASIZ patterns")
