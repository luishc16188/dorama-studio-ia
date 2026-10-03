"""
Storyboard Agent - Converts script beats into visual storyboard shots.
Generates shot-by-shot visual breakdown with camera, lighting, and composition details.
"""
import logging
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import (
    CameraAngle,
    CameraMovement,
    LightingSpec,
    Script,
    ShotType,
    SoundSpec,
    Storyboard,
    StoryboardAgentOutputSchema,
    StoryboardShot,
)

logger = logging.getLogger(__name__)


class StoryboardAgent(BaseAgent[Script, StoryboardAgentOutputSchema]):
    """
    Storyboard Agent that takes a script and generates a detailed visual storyboard
    with shot specifications for video generation.
    """

    InputSchema = Script
    OutputSchema = StoryboardAgentOutputSchema

    def __init__(self):
        super().__init__("StoryboardAgent")

    def run(self, input_data: Script) -> dict[str, Any]:
        """Run the storyboard agent."""
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

        # Shot type mapping by emotional beat
        self.beat_shot_map = {
            "HOOK EXPLOSIVO": {"shot_type": ShotType.ECU, "angle": CameraAngle.eye_level, "movement": CameraMovement.push_in},
        "CONTEXTO MÍNIMO": {"shot_type": ShotType.CU, "angle": CameraAngle.high_angle, "movement": 'static'},
        "PROBLEMA INMEDIATO": {"shot_type": ShotType.MCU, "angle": CameraAngle.low_angle, "movement": 'handheld'},
        "ESCALADA": {"shot_type": ShotType.ECU, "angle": CameraAngle.eye_level, "movement": 'slow_zoom'},
        "GIRO / REVELACIÓN": {"shot_type": ShotType.ECU, "angle": CameraAngle.eye_level, "movement": CameraMovement.rack_focus},
        "COMPLICACIÓN": {"shot_type": ShotType.MS, "angle": CameraAngle.low_angle, "movement": 'handheld'},
        "REVERSAL MAYOR": {"shot_type": ShotType.CU, "angle": CameraAngle.eye_level, "movement": CameraMovement.push_in},
        "NUEVA INFORMACIÓN": {"shot_type": ShotType.MCU, "angle": CameraAngle.high_angle, "movement": 'static'},
        "CLIFFHANGER": {"shot_type": ShotType.ECU, "angle": CameraAngle.eye_level, "movement": CameraMovement.push_in},
        }

        # Lens presets by shot type
        self.lens_map = {
            ShotType.ECU: "85mm f/1.4",
            ShotType.CU: "50mm f/1.8",
            ShotType.MCU: "35mm f/2",
            ShotType.MS: "35mm f/2.8",
            ShotType.WS: "24mm f/4",
        }

    def _process(self, validated_input: Script) -> StoryboardAgentOutputSchema:
        """Process script to generate storyboard shots."""
        logger.info(f"Generating storyboard for episode {validated_input.episode_num}")

        shots = []
        beats = self._extract_beats(validated_input)

        for i, beat in enumerate(beats):
            shot = self._create_shot_from_beat(beat, i, validated_input)
            shots.append(shot)

        storyboard = Storyboard(
            episode_num=validated_input.episode_num,
            shots=shots,
            title=validated_input.hook_used.get("title", f"Episode {validated_input.episode_num}") if validated_input.hook_used else f"Episode {validated_input.episode_num}"
        )

        return StoryboardAgentOutputSchema(storyboard=storyboard)

    def _extract_beats(self, script: Script) -> list[dict[str, Any]]:
        """Extract beat information from script."""
        beats = []

        # Use scenes as beats if available
        if script.scenes:
            for scene in script.scenes:
                if isinstance(scene, dict):
                    beats.append(scene)
                else:
                    beats.append({
                        "beat_name": getattr(scene, 'beat_name', 'BEAT'),
                        "action": getattr(scene, 'action', ''),
                        "dialogue": getattr(scene, 'dialogue', ''),
                        "emotion": getattr(scene, 'emotion', 'neutral'),
                        "duration": getattr(scene, 'duration', 10.0),
                        "characters": getattr(scene, 'characters_present', ['protagonist']),
                        "camera": getattr(scene, 'camera', {}),
                        "sound": getattr(scene, 'sound', {}),
                    })
        else:
            # Fallback: create beats from script fields
            beats = [{
                "beat_name": "MAIN",
                "action": script.action,
                "dialogue": script.dialogue,
                "emotion": "neutral",
                "duration": script.total_duration / 9 if script.total_duration > 0 else 10.0,
                "characters": ["protagonist"],
                "camera": {},
                "sound": {},
            }]

        return beats

    def _create_shot_from_beat(self, beat: dict, index: int, script: Script) -> StoryboardShot:
        """Create a storyboard shot from beat data."""
        beat_name = beat.get("beat_name", f"BEAT_{index+1}")
        shot_config = self.beat_shot_map.get(beat_name, {
            "shot_type": ShotType.MCU,
            "angle": CameraAngle.eye_level,
            "movement": 'static'
        })

        shot_type = shot_config["shot_type"]
        characters = beat.get("characters", ["protagonist"])

        # Build visual reference prompt
        visual_ref = self._build_visual_ref_prompt(beat, characters, script)

        # Build narrative intent
        narrative_intent = self._build_narrative_intent(beat, beat_name)

        # Build emotional target
        emotional_target = beat.get("emotion", "neutral")

        # Camera spec
        camera_spec = {
            "shot_type": shot_type,
            "angle": shot_config["angle"],
            "movement": shot_config["movement"],
            "lens": self.lens_map.get(shot_type, "35mm f/2"),
            "focus_pull": self._get_focus_pull(beat, shot_type),
        }

        # Lighting spec
        lighting = LightingSpec(
            key_light="key light",
            fill_light="soft fill",
            backlight="rim light",
            color_temperature="5600K",
            mood=emotional_target,
            ratio="4:1",
            practical="window" if "int" in beat.get("setting", "").lower() else "none"
        )

        # Sound spec
        sound = SoundSpec(
            ambience=beat.get("sound", {}).get("ambience", "room tone"),
            sfx=beat.get("sound", {}).get("sfx", []),
            music_cue=beat.get("sound", {}).get("music_cue", {}),
            silence_before=0.5 if beat_name == "HOOK EXPLOSIVO" else 0.0,
            silence_drop=beat_name in ["GIRO / REVELACIÓN", "REVERSAL MAYOR", "CLIFFHANGER"],
            frequency_hz=40.0 if beat_name == "HOOK EXPLOSIVO" else 0.0,
            file_spec="",
            purpose=beat_name.lower().replace(" ", "_")
        )

        shot = StoryboardShot(
            shot_id=f"shot_{script.episode_num}_{index+1:02d}",
            beat=beat_name,
            duration=beat.get("duration", 10.0),
            shot_type=shot_type,
            angle=shot_config["angle"],
            movement=shot_config["movement"],
            action=beat.get("action", ""),
            characters=characters,
            expressions=self._get_expressions(beat, characters),
            lighting=lighting,
            lens=self.lens_map.get(shot_type, "35mm f/2"),
            focus_pull=camera_spec["focus_pull"],
            transition_to_next=self._get_transition(beat_name, index, len(beats)),
            visual_ref_prompt=visual_ref,
            narrative_intent=narrative_intent,
            emotional_target=emotional_target,
            beat_energy=self._get_beat_energy(beat_name),
            character_references={c: {"id": c} for c in characters},
            setting=beat.get("setting", "unspecified"),
            sfx=beat.get("sound", {}).get("sfx", []),
            ambience=beat.get("sound", {}).get("ambience", "room tone"),
            micro_expressions=self._get_micro_expressions(beat, characters),
            volumetric={},
            audio_cues=sound.dict() if hasattr(sound, 'dict') else {},
            pattern_interrupts=self._get_pattern_interrupts(beat_name),
            color_grade=self._get_color_grade(emotional_target),
            safe_zones={"text": "center_80%", "action": "center_90%"},
            shot_intent=f"{beat_name}: {narrative_intent}"
        )

        return shot

    def _build_visual_ref_prompt(self, beat: dict, characters: list[str], script: Script) -> str:
        """Build visual reference prompt for character consistency."""
        genre = getattr(script, 'genre', 'romance')
        style_base = "cinematic dorama, K-Drama color grade, vertical 9:16"

        char_descriptions = ", ".join([f"{c}: consistent identity, locked facial features" for c in characters])
        action = beat.get("action", "")
        setting = beat.get("setting", "unspecified location")

        return f"{style_base}, {char_descriptions}, {action}, {setting}"

    def _build_narrative_intent(self, beat: dict, beat_name: str) -> str:
        """Build narrative intent description."""
        action = beat.get("action", "")
        return f"Visualize {beat_name.lower()}: {action}"

    def _get_focus_pull(self, beat: dict, shot_type: ShotType) -> str:
        """Determine focus pull based on beat and shot type."""
        if shot_type == ShotType.ECU:
            return "eyes to key object"
        elif shot_type == ShotType.CU:
            return "eyes"
        elif "revelación" in beat.get("beat_name", "").lower():
            return "background to subject"
        return ""

    def _get_expressions(self, beat: dict, characters: list[str]) -> dict[str, str]:
        """Get character expressions for the beat."""
        emotion = beat.get("emotion", "neutral")
        expr_map = {
            "sorpresa": "wide eyes, parted lips",
            "tension": "narrowed eyes, tense jaw",
            "miedo": "dilated pupils, frozen expression",
            "indignacion": "flared nostrils, compressed lips",
            "esperanza": "soft eyes, slight smile",
            "dolor": "tearing up, trembling chin",
            "recompensa": "genuine smile, relaxed",
            "nueva_amenaza": "sharp intake of breath, hardening eyes",
            "determinacion": "set jaw, focused gaze",
            "curiosidad": "head tilt, searching eyes",
        }
        expr = expr_map.get(emotion, "neutral")
        return dict.fromkeys(characters, expr)

    def _get_transition(self, beat_name: str, index: int, total: int) -> str:
        """Get transition to next shot."""
        if index == total - 1:
            return "cut to black"
        transitions = {
            "HOOK EXPLOSIVO": "whip pan",
        "CONTEXTO MÍNIMO": "match cut",
        "PROBLEMA INMEDIATO": "smash cut",
        "ESCALADA": "dolly zoom",
        "GIRO / REVELACIÓN": "rack focus transition",
        "COMPLICACIÓN": "jump cut",
        "REVERSAL MAYOR": "iris out",
        "NUEVA INFORMACIÓN": "dissolve",
        }
        return transitions.get(beat_name, "cut")

    def _get_beat_energy(self, beat_name: str) -> int:
        """Get beat energy level 1-10."""
        energy_map = {
            "HOOK EXPLOSIVO": 10,
        "CONTEXTO MÍNIMO": 4,
        "PROBLEMA INMEDIATO": 7,
        "ESCALADA": 8,
        "GIRO / REVELACIÓN": 9,
        "COMPLICACIÓN": 8,
        "REVERSAL MAYOR": 10,
        "NUEVA INFORMACIÓN": 5,
        "CLIFFHANGER": 10,
        }
        return energy_map.get(beat_name, 5)

    def _get_micro_expressions(self, beat: dict, characters: list[str]) -> dict[str, Any]:
        """Get micro-expression details."""
        emotion = beat.get("emotion", "neutral")
        micro_map = {
            "sorpresa": {"eye_dart": "sudden", "micro_smile": False, "jaw_clench": False, "breath_hitch": True},
            "tension": {"eye_dart": "rapid", "micro_smile": False, "jaw_clench": True, "breath_hitch": False},
            "miedo": {"eye_dart": "frozen", "micro_smile": False, "jaw_clench": True, "breath_hitch": True},
        }
        base = micro_map.get(emotion, {"eye_dart": "normal", "micro_smile": False, "jaw_clench": False, "breath_hitch": False})
        return dict.fromkeys(characters, base)

    def _get_pattern_interrupts(self, beat_name: str) -> list[dict[str, Any]]:
        """Get pattern interrupts for the beat."""
        interrupts = {
            "HOOK EXPLOSIVO": [{"type": "audio_drop", "timing": "0.3s", "description": "Sub-bass + silence"}],
        "GIRO / REVELACIÓN": [{"type": "silence_drop", "timing": "0.2s", "description": "Pre-reveal silence"}],
        "REVERSAL MAYOR": [{"type": "sound_bridge", "timing": "0.5s", "description": "Sting + new rhythm"}],
        "CLIFFHANGER": [{"type": "freeze_frame", "timing": "0.5s", "description": "Hold on revelation"}],
        }
        return interrupts.get(beat_name, [])

    def _get_color_grade(self, emotion: str) -> dict[str, Any]:
        """Get color grade settings for emotion."""
        grades = {
            "sorpresa": {"lift": "cool", "gamma": "neutral", "gain": "warm"},
            "tension": {"lift": "cyan", "gamma": "desat", "gain": "hot"},
            "miedo": {"lift": "blue", "gamma": "dark", "gain": "dim"},
            "esperanza": {"lift": "gold", "gamma": "warm", "gain": "bright"},
            "determinacion": {"lift": "neutral", "gamma": "contrast", "gain": "strong"},
        }
        return grades.get(emotion, {"lift": "neutral", "gamma": "neutral", "gain": "neutral"})
