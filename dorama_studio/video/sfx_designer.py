"""
SFX Designer Agent - Specialized in designing narrative sound effects.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from dorama_studio.core.master_writer import Beat, MasterScript


@dataclass
class SFXEvent:
    """Represents a single sound effect event."""

    name: str
    description: str
    time: float  # Seconds from start of scene/episode
    duration: float  # Seconds
    volume: float  # dB (-60 to 0)
    pan: float  # Stereo position (-1 left to 1 right)
    fade_in: float = 0.0  # Seconds
    fade_out: float = 0.0  # Seconds
    eq: dict[str, float] = field(
        default_factory=dict
    )  # Frequency bands: low, mid, high
    reverb: float = 0.0  # Reverb amount (0-1)


class SFXDesigner:
    """
    Specialized in designing narrative sound effects that advance the story.
    """

    def __init__(self):
        # Narrative SFX library organized by function and emotion
        self.narrative_sfx = {
            "revelation": [
                {
                    "name": "paper_whisper",
                    "desc": "Soft paper rustle - secret document or letter",
                    "emotion": "surprise",
                },
                {
                    "name": "glass_tap",
                    "desc": "Light tap on glass - clue discovered or code broken",
                    "emotion": "curiosidad",
                },
                {
                    "name": "lock_click",
                    "desc": "Lock mechanism clicking - access to secret granted",
                    "emotion": "satisfaction",
                },
                {
                    "name": "heartbeat_rise",
                    "desc": "Heartbeat increasing - realization dawning",
                    "emotion": "miedo",
                },
                {
                    "name": "breath_release",
                    "desc": "Sudden exhale - tension released after realization",
                    "emotion": "alivio",
                },
                {
                    "name": "zipper_open",
                    "desc": "Bag or jacket opening - revealing hidden item",
                    "emotion": "intriga",
                },
            ],
            "threat": [
                {
                    "name": "tension_pulse_low",
                    "desc": "Low pulsating tone - impending danger",
                    "emotion": "tension",
                },
                {
                    "name": "footsteps_approach",
                    "desc": "Footsteps getting closer - unseen approaching",
                    "emotion": "miedo",
                },
                {
                    "name": "door_creak",
                    "desc": "Old door creaking - unseen presence in space",
                    "emotion": "miedo",
                },
                {
                    "name": "whisper_echo",
                    "desc": "Distant whisper repeating a name or warning",
                    "emotion": "inquietud",
                },
                {
                    "name": "heartbeat_stop",
                    "desc": "Heartbeat briefly stopping - shock or fright",
                    "emotion": "terror",
                },
                {
                    "name": "radio_static",
                    "desc": "Radio tuning or static - hidden communication",
                    "emotion": "sospecha",
                },
            ],
            "emotion": [
                {
                    "name": "tear_drop",
                    "desc": "Single tear hitting surface - sadness or joy",
                    "emotion": "tristeza",
                },
                {
                    "name": "hug_squeeze",
                    "desc": "Tight embrace - comfort, desperation, or farewell",
                    "emotion": "ternura",
                },
                {
                    "name": "laugh_soft",
                    "desc": "Soft laughter - joy, nervousness, or irony",
                    "emotion": "alegría",
                },
                {
                    "name": "whisper_intimate",
                    "desc": "Close whisper - intimacy, secret, or conspiracy",
                    "emotion": "intimidad",
                },
                {
                    "name": "handshake_firm",
                    "desc": "Firm handshake - agreement, respect, or challenge",
                    "emotion": "respeto",
                },
                {
                    "name": "glass_clink",
                    "desc": "Glasses clinking - celebration or agreement",
                    "emotion": "celebración",
                },
            ],
            "action": [
                {
                    "name": "punch_impact",
                    "desc": "Fist impact - physical confrontation",
                    "emotion": "ira",
                },
                {
                    "name": "glass_break",
                    "desc": "Glass shattering - sudden violence or escape",
                    "emotion": "miedo",
                },
                {
                    "name": "metal_clang",
                    "desc": "Metal hitting metal - confrontation or alarm",
                    "emotion": "alerta",
                },
                {
                    "name": "running_footsteps",
                    "desc": "Rapid footsteps - chase, escape, or pursuit",
                    "emotion": "urgencia",
                },
                {
                    "name": "door_slam",
                    "desc": "Door slamming angrily - frustration or final decision",
                    "emotion": "enojo",
                },
                {
                    "name": "car_accelerate",
                    "desc": "Engine revving and accelerating - escape or pursuit",
                    "emotion": "determinacion",
                },
            ],
            "transition": [
                {
                    "name": "whoosh",
                    "desc": "Fast movement through air - scene change or passage of time",
                    "emotion": "neutral",
                },
                {
                    "name": "sweep",
                    "desc": "Broad audio sweep - transition or mental shift",
                    "emotion": "neutral",
                },
                {
                    "name": "swell",
                    "desc": "Audio swell - emotional buildup or release",
                    "emotion": "variedad",
                },
                {
                    "name": "reverse_cymbal",
                    "desc": "Reversed cymbal - supernatural or magical transition",
                    "emotion": "misterio",
                },
                {
                    "name": "heartbeat_stop_start",
                    "desc": "Heartbeat stopping then restarting - shock to action",
                    "emotion": "sorpresa",
                },
            ],
            "ambience": [
                {
                    "name": "HVAC_hum",
                    "desc": "Background building ventilation",
                    "loop": True,
                },
                {"name": "room_tone", "desc": "Empty room ambient sound", "loop": True},
                {
                    "name": "distant_traffic",
                    "desc": "Faint city traffic in distance",
                    "loop": true,
                },
                {
                    "name": "forest_night",
                    "desc": "Nighttime forest with crickets and wind",
                    "loop": true,
                },
                {
                    "name": "ocean_waves",
                    "desc": "Gentle ocean waves lapping shore",
                    "loop": true,
                },
                {
                    "name": "fire_crackle",
                    "desc": "Fireplace or campfire crackling",
                    "loop": true,
                },
            ],
        }

        # EQ presets for different SFX types
        self.eq_presets = {
            "revelation": {"low": -2, "mid": 0, "high": 3},
            "threat": {"low": 2, "mid": -1, "high": 2},
            "emotion": {"low": 0, "mid": 2, "high": 1},
            "action": {"low": 3, "mid": 1, "high": -1},
            "transition": {"low": -1, "mid": 2, "high": 0},
            "ambience": {"low": 1, "mid": 0, "high": -1},
        }

    def design_sfx_for_beat(
        self, beat: Beat, script: MasterScript, start_time: float
    ) -> list[SFXEvent]:
        """
        Design SFX events for a specific beat based on action, emotion, and context.
        """
        sfx_events = []

        # Use SFX from beat.sound metadata if provided
        if beat.sound and beat.sound.get("sfx"):
            for sfx_name in beat.sound["sfx"]:
                sfx_event = self._create_sfx_event(sfx_name, beat, start_time)
                if sfx_event:
                    sfx_events.append(sfx_event)

        # Add narrative SFX based on action and emotion if not already specified
        if not (beat.sound and beat.sound.get("sfx")):
            narrative_sfx = self._select_narrative_sfx(beat, script)
            for sfx_spec in narrative_sfx:
                sfx_event = self._create_sfx_event_from_spec(sfx_spec, beat, start_time)
                if sfx_event:
                    sfx_events.append(sfx_event)

        # Add ambient SFX if not too many specific SFX
        if len(sfx_events) < 2:
            ambient_sfx = self._select_ambient_sfx(beat, script)
            for sfx_spec in ambient_sfx:
                sfx_event = self._create_sfx_event_from_spec(sfx_spec, beat, start_time)
                if sfx_event:
                    sfx_events.append(sfx_event)

        return sfx_events

    def _create_sfx_event(
        self, sfx_name: str, beat: Beat, start_time: float
    ) -> SFXEvent | None:
        """Create an SFX event from a named effect."""
        # Search in all SFX categories
        for category, sfx_list in self.narrative_sfx.items():
            for sfx_spec in sfx_list:
                if sfx_spec["name"] == sfx_name:
                    return self._create_sfx_event_from_spec(sfx_spec, beat, start_time)
        return None

    def _create_sfx_event_from_spec(
        self, sfx_spec: dict[str, Any], beat: Beat, start_time: float
    ) -> SFXEvent | None:
        """Create SFX event from specification."""
        # Determine timing within the beat
        beat_duration = beat.duration
        event_time = (
            start_time + random.uniform(0.1, beat_duration - 0.1)
            if beat_duration > 0.2
            else start_time
        )

        # Determine duration based on SFX type
        sfx_name = sfx_spec["name"]
        duration_map = {
            "paper_whisper": 0.5,
            "glass_tap": 0.3,
            "lock_click": 0.2,
            "heartbeat_rise": 2.0,
            "breath_release": 1.0,
            "zipper_open": 0.8,
            "tension_pulse_low": 3.0,
            "footsteps_approach": 1.5,
            "door_creak": 1.0,
            "whisper_echo": 1.5,
            "heartbeat_stop": 0.5,
            "radio_static": 2.0,
            "tear_drop": 0.3,
            "hug_squeeze": 1.5,
            "laugh_soft": 1.0,
            "whisper_intimate": 1.2,
            "handshake_firm": 0.8,
            "glass_clink": 0.5,
            "punch_impact": 0.4,
            "glass_break": 1.0,
            "metal_clang": 0.5,
            "running_footsteps": 2.0,
            "door_slam": 0.6,
            "car_accelerate": 2.5,
            "whoosh": 0.8,
            "sweep": 2.0,
            "swell": 3.0,
            "reverse_cymbal": 0.6,
            "heartbeat_stop_start": 1.0,
            "HVAC_hum": 4.0,
            "room_tone": 3.0,
            "distant_traffic": 3.0,
            "forest_night": 4.0,
            "ocean_waves": 3.0,
            "fire_crackle": 2.0,
        }
        duration = duration_map.get(sfx_name, 1.0)

        # Ensure it fits within beat
        if event_time + duration > start_time + beat_duration:
            duration = max(0.1, beat_duration - (event_time - start_time))
            if duration < 0.1:
                return None

        # Determine volume based on SFX importance
        volume_map = {
            "paper_whisper": -18,
            "glass_tap": -16,
            "lock_click": -14,
            "heartbeat_rise": -12,
            "breath_release": -16,
            "zipper_open": -14,
            "tension_pulse_low": -16,
            "footsteps_approach": -14,
            "door_creak": -16,
            "whisper_echo": -18,
            "heartbeat_stop": -14,
            "radio_static": -16,
            "tear_drop": -14,
            "hug_squeeze": -12,
            "laugh_soft": -14,
            "whisper_intimate": -14,
            "handshake_firm": -14,
            "glass_clink": -14,
            "punch_impact": -10,
            "glass_break": -8,
            "metal_clang": -12,
            "running_footsteps": -12,
            "door_slam": -8,
            "car_accelerate": -10,
            "whoosh": -14,
            "sweep": -12,
            "swell": -10,
            "reverse_cymbal": -14,
            "heartbeat_stop_start": -12,
            "HVAC_hum": -24,
            "room_tone": -22,
            "distant_traffic": -20,
            "forest_night": -18,
            "ocean_waves": -20,
            "fire_crackle": -18,
        }
        volume = volume_map.get(sfx_name, -16)

        # Determine pan (stereo position)
        pan_map = {
            "footsteps_approach": lambda: random.uniform(-0.8, 0.8),  # Moving
            "door_creak": lambda: random.uniform(-0.3, 0.3),  # Centered
            "punch_impact": lambda: random.uniform(-0.2, 0.2),
            "glass_break": lambda: random.uniform(-0.4, 0.4),
            "running_footsteps": lambda: random.uniform(-0.9, 0.9),  # Moving across
            "car_accelerate": lambda: random.uniform(-0.7, 0.7),
            "paper_whisper": lambda: random.uniform(-0.2, 0.2),
            "glass_tap": lambda: random.uniform(-0.1, 0.1),
            "lock_click": lambda: random.uniform(-0.1, 0.1),
            "heartbeat_rise": lambda: 0.0,  # Centered
            "tear_drop": lambda: random.uniform(-0.1, 0.1),
            "hug_squeeze": lambda: 0.0,
            "laugh_soft": lambda: random.uniform(-0.2, 0.2),
            "whisper_intimate": lambda: random.uniform(-0.1, 0.1),
            "handshake_firm": lambda: 0.0,
            "glass_clink": lambda: random.uniform(-0.1, 0.1),
        }
        if sfx_name in pan_map:
            pan = pan_map[sfx_name]()
        else:
            pan = random.uniform(-0.3, 0.3)

        # Get EQ preset
        sfx_category = self._get_sfx_category(sfx_name)
        eq = self.eq_presets.get(sfx_category, {"low": 0, "mid": 0, "high": 0})

        # Fade in/out
        fade_in = 0.05 if duration > 0.5 else 0.0
        fade_out = 0.05 if duration > 0.5 else 0.0

        # Reverb
        reverb = (
            0.2 if "room" in sfx_name.lower() or "tone" in sfx_name.lower() else 0.0
        )

        return SFXEvent(
            name=sfx_name,
            description=sfx_spec["desc"],
            time=event_time,
            duration=duration,
            volume=volume,
            pan=pan,
            fade_in=fade_in,
            fade_out=fade_out,
            eq=eq,
            reverb=reverb,
        )

    def _get_sfx_category(self, sfx_name: str) -> str:
        """Get the category of an SFX."""
        for category, sfx_list in self.narrative_sfx.items():
            for sfx in sfx_list:
                if sfx["name"] == sfx_name:
                    return category
        return "ambience"  # Default

    def _select_narrative_sfx(
        self, beat: Beat, script: MasterScript
    ) -> list[dict[str, Any]]:
        """Select narrative SFX based on beat action and emotion."""
        selected_sfx = []

        # Determine primary emotion and action
        emotion = beat.emotion
        action_lower = beat.action.lower()

        # Map emotions to SFX categories
        emotion_to_sfx = {
            "sorpresa": "revelation",
            "miedo": "threat",
            "tristeza": "emotion",
            "enojo": "action",
            "ira": "action",
            "alegría": "emotion",
            "ternura": "emotion",
            "intimidad": "emotion",
            "inquietud": "threat",
            "satisfacción": "revelation",
            "alivio": "emotion",
            "urgencia": "action",
            "alerta": "action",
            "curiosidad": "revelation",
            "tension": "threat",
            "determinacion": "action",
        }

        # Map action keywords to SFX categories
        action_to_sfx = {
            "paper": "revelation",
            "glass": "revelation",
            "lock": "revelation",
            "heartbeat": "threat",
            "breath": "threat",
            "footsteps": "threat",
            "door": "threat",
            "whisper": "threat",
            "zipper": "revelation",
            "punch": "action",
            "impact": "action",
            "metal": "action",
            "running": "action",
            "door": "action",
            "slam": "action",
            "car": "action",
            "accelerate": "action",
            "whoosh": "transition",
            "sweep": "transition",
            "swell": "transition",
            "cymbal": "transition",
            "HVAC": "ambience",
            "room": "ambience",
            "traffic": "ambience",
            "forest": "ambience",
            "ocean": "ambience",
            "fire": "ambience",
        }

        # Get SFX from emotion mapping
        if emotion in emotion_to_sfx:
            category = emotion_to_sfx[emotion]
            if category in self.narrative_sfx:
                selected_sfx.extend(
                    random.sample(
                        self.narrative_sfx[category],
                        min(2, len(self.narrative_sfx[category])),
                    )
                )

        # Get SFX from action keywords
        for keyword, category in action_to_sfx.items():
            if keyword in action_lower:
                if category in self.narrative_sfx:
                    selected_sfx.extend(
                        random.sample(
                            self.narrative_sfx[category],
                            min(1, len(self.narrative_sfx[category])),
                        )
                    )

        # Ensure we have at least one SFX if beat has significant action or emotion
        if not selected_sfx and (
            len(beat.action.split()) > 3 or beat.emotion != "neutral"
        ):
            # Default to a suitable SFX based on emotion
            default_category = emotion_to_sfx.get(emotion, "emotion")
            if default_category in self.narrative_sfx:
                selected_sfx = random.sample(
                    self.narrative_sfx[default_category],
                    min(1, len(self.narrative_sfx[default_category])),
                )

        return selected_sfx

    def _select_ambient_sfx(
        self, beat: Beat, script: MasterScript
    ) -> list[dict[str, Any]]:
        """Select ambient SFX to fill out the soundscape."""
        ambient_sfx = []

        # Add ambient SFX if beat is long enough and doesn't have many specific SFX
        if beat.duration > 3.0:
            # Choose one ambient SFX
            ambient_list = self.narrative_sfx["ambience"]
            selected = random.sample(ambient_list, min(1, len(ambient_list)))
            ambient_sfx.extend(selected)

        return ambient_sfx

    def design_sfx_for_cliffhanger(self, script: MasterScript) -> list[SFXEvent]:
        """Design SFX for the cliffhanger moment."""
        sfx_events = []

        if not hasattr(script, "cliffhanger"):
            return sfx_events

        # Cliffhanger SFX based on type
        cliffhanger_type = (
            script.cliffhanger.type
            if hasattr(script.cliffhanger, "type")
            else "revelacion"
        )

        type_to_sfx = {
            "revelacion": [
                "paper_whisper",
                "glass_tap",
                "lock_click",
                "heartbeat_rise",
            ],
            "amenaza": [
                "tension_pulse_low",
                "footsteps_approach",
                "door_creak",
                "whisper_echo",
            ],
            "decision": [
                "handshake_firm",
                "glass_clink",
                "paper_whisper",
                "zipper_open",
            ],
            "identidad": [
                "mirror_ripple",
                "water_drop",
                "breath_sharp",
                "heartbeat_rise",
            ],
            "traicion": ["phone_dial", "message_sent", "footsteps_away", "door_close"],
            "accion_interrumpida": [
                "running_footsteps_stop",
                "door_slam",
                "glass_break",
                "metal_clang",
            ],
            "respuesta_congelada": [
                "tear_drop",
                "breath_sharp",
                "heartbeat_stop",
                "silence",
            ],
            "reversal": ["metal_clang", "glass_break", "door_slam", "paper_whisper"],
        }

        sfx_names = type_to_sfx.get(cliffhanger_type, ["paper_whisper"])

        start_time = sum(
            beat.duration for beat in script.beats
        )  # Start at end of episode
        for i, sfx_name in enumerate(sfx_names):
            sfx_event = self._create_sfx_event(
                sfx_name,
                Beat(
                    beat_name="CLIFFHANGER_SFX",
                    time_range="0-0s",
                    duration=2.0,
                    action="",
                    dialogue="",
                    subtitle_en="",
                    camera={},
                    sound={},
                    emotion="tension",
                    characters_present=[],
                    pacing="hyper",
                    tension=8,
                    is_info_beat=False,
                    pattern_interrupt=None,
                ),
                start_time + i * 0.5,
            )  # Stagger SFX events

            if sfx_event:
                sfx_events.append(sfx_event)

        return sfx_events


# Convenience function
def design_sfx_for_script(
    script: MasterScript, character_bible: Any | None = None
) -> list[SFXEvent]:
    """Convenience function to design SFX for a script."""
    designer = SFXDesigner()
    all_sfx = []
    start_time = 0.0
    for beat in script.beats:
        beat_sfx = designer.design_sfx_for_beat(beat, script, start_time)
        all_sfx.extend(beat_sfx)
        start_time += beat.duration

    # Add cliffhanger SFX
    cliffhanger_sfx = designer.design_sfx_for_cliffhanger(script)
    all_sfx.extend(cliffhanger_sfx)

    return all_sfx


if __name__ == "__main__":
    # Quick test
    print("SFXDesigner module loaded successfully")
