"""
Beat Contract - Complete beat specification with all required fields.
Implements the beat contract as defined in the blueprint.
"""

from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field

from pydantic import BaseModel, ConfigDict, Field
from dorama_studio.contracts.v2_schemas import BaseArtifact


class FractalStage(str, Enum):
    """Fractal formula stages: H→P→Q→E→R→Q2→C"""
    HOOK = "H"
    PROMISE = "P"
    QUESTION = "Q"
    ESCALATION = "E"
    REWARD = "R"
    NEW_QUESTION = "Q2"
    CLIFFHANGER = "C"


class PatternInterruptType(str, Enum):
    """Types of pattern interrupts required every ~2.5 seconds."""
    ZOOM_PUNCH = "zoom_punch"
    WHIP_PAN = "whip_pan"
    SMASH_CUT = "smash_cut"
    DEAD_SILENCE = "dead_silence"
    HARD_BEAT_DROP = "hard_beat_drop"
    RACK_FOCUS = "rack_focus"


class InformationAsymmetryType(str, Enum):
    """Types of information asymmetry."""
    AUDIENCE_KNOWS_MORE = "audience_knows_more"
    AUDIENCE_KNOWS_LESS = "audience_knows_less"
    AUDIENCE_KNOWS_EQUAL = "audience_knows_equal"
    AUDIENCE_DECIDES = "audience_decides"


class CameraMovementType(str, Enum):
    """Camera movement types with direction and speed."""
    SLOW_DOLLY_IN = "Slow dolly-in"
    RAPID_TRUCK_LEFT = "Rapid truck-left"
    VIOLENT_CRASH_ZOOM_PUSH_IN = "Violent crash-zoom push-in"
    STATIC_LOCKED_OFF = "Static locked-off"
    STEADICAM = "Steadicam"
    WHIP_PAN = "Whip-pan"
    CRANE_UP = "Crane up"
    SPEED_RAMP = "Speed ramp"
    DOLLY_ZOOM = "Dolly zoom"
    ORBITAL = "Orbital"
    HANDHELD = "Handheld"
    TRACKING = "Tracking"


class CameraAngleType(str, Enum):
    """Camera angle types."""
    EYE_LEVEL = "eye_level"
    LOW_ANGLE = "low_angle"
    HIGH_ANGLE = "high_angle"
    DUTCH_ANGLE = "dutch_angle"
    OVERHEAD = "overhead"
    BIRDSEYE = "birdseye"
    WORMSEYE = "wormseye"
    OTS = "OTS"
    POV = "POV"


class ShotType(str, Enum):
    """Shot types from ECU to EST."""
    ECU = "ECU"  # Extreme Close-Up
    CU = "CU"    # Close-Up
    MCU = "MCU"  # Medium Close-Up
    MS = "MS"    # Medium Shot
    MLS = "MLS"  # Medium Long Shot
    LS = "LS"    # Long Shot
    VLS = "VLS"  # Very Long Shot
    EST = "EST"  # Establishing Shot


class DialogueDeliveryType(str, Enum):
    """Dialogue delivery types."""
    SUSURRO = "susurro"
    GRITO = "grito"
    QUEBRADO = "quebrado"
    FRIO = "frío"
    IRONICO = "irónico"
    SUSURRADO_AMENAZANTE = "susurrado_amenazante"
    VOZ_QUEBRADA = "voz_quebrada"


class MicroExpressionType(str, Enum):
    """Micro-expression types."""
    LABIO_TEMBLOROSO = "labio_tembloroso"
    MANDIBULA_APRETADA = "mandíbula_apretada"
    OJOS_SECOS = "ojos_secos"
    PUPILAS_DILATADAS = "pupilas_dilatadas"
    RESPIRACION_CONTENIDA = "respiración_contenida"
    CEJA_ARQUEADA = "ceja_arqueada"
    SONRISA_TENSA = "sonrisa_tensa"


class DialogueEmotionType(str, Enum):
    """Dialogue emotion types."""
    SHOCK = "shock"
    TENSION = "tension"
    FEAR = "fear"
    ANGER = "anger"
    REVELATION = "revelation"
    BETRAYAL = "betrayal"
    TRUTH = "truth"
    SUSPENSE = "suspense"
    DECISION = "decision"


class BeatCamera(BaseModel):
    """Camera specification for a beat."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    shot_type: ShotType
    angle: CameraAngleType
    movement: CameraMovementType
    lens: str  # e.g., "85mm prime lens f/1.4"
    focus_pull: str  # e.g., "eyes → hand", "background → foreground"
    composition: str = ""  # rule_of_thirds, look_space, leading_lines, etc.


class BeatSound(BaseModel):
    """Sound specification for a beat."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    ambience: str  # Continuous environment texture
    sfx: List[str] = Field(default_factory=list)  # Foley with cause-effect
    music_cue: Dict[str, Any] = Field(default_factory=dict)  # {"genre": "tension", "bpm": 60, "action": "sub-bass stinger", "function": "tension building"}
    silence_drop: bool = False  # TRUE 0.5s before critical revelations
    voice: str = ""  # Modular structure: [Voice: whispered threatening tempo 0.8s pitch -2st: '¿Qué guardas ahí?']


class BeatSchema(BaseModel):
    """
    Complete beat specification as defined in the blueprint.
    All fields are required unless explicitly optional.
    """
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    # Identity
    beat_id: str
    beat_name: str
    timestamp: str  # e.g., "0-10", "10-20", etc.
    duration_sec: float = 10.0

    # Dialogue
    dialogue: str = Field(..., max_length=120)  # max ~10 words, Spanish latino
    dialogue_delivery: DialogueDeliveryType
    micro_expression: MicroExpressionType
    dialogue_emotion: DialogueEmotionType

    # Action
    action: str  # Single dominant observable verb (no abstract adjectives)

    # Camera
    camera: BeatCamera

    # Sound
    sound: BeatSound

    # Character emotional state
    character_emotion: Dict[str, str] = Field(default_factory=dict)  # {"char_id": "physiological_descriptor"}

    # Required structural elements
    pattern_interrupt: PatternInterruptType
    curiosity_loop_planted: str  # Concrete question left open
    information_asymmetry: InformationAsymmetryType = InformationAsymmetryType.AUDIENCE_KNOWS_MORE

    # Trope subversion (only in Twist1, mandatory)
    subversion_applied: str = ""

    # Fractal formula stage (mandatory sequence: H→P→Q→E→R→Q2→C)
    fractal_stage: FractalStage

    # Continuity block (mandatory for shot N>1)
    continuity_block: str = ""

    # Characters present (mandatory)
    character_ids: List[str] = Field(default_factory=list)

    # Negative prompt for generation
    negative_prompt: str = ""

    # State delta (for continuity)
    state_delta: Optional[Dict[str, Any]] = None

    # Validation rules
    validation_rules: List[str] = Field(default_factory=list)


class EpisodeBeats(BaseModel):
    """Complete set of 9 beats for an episode."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    episode_id: str
    episode_number: int
    beats: List[BeatSchema] = Field(..., min_length=9, max_length=9)
    character_sheets: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    scene_state_log: List[Dict[str, Any]] = Field(default_factory=list)

    def validate_beat_sequence(self) -> tuple[bool, List[str]]:
        """Validate the beat sequence follows H→P→Q→E→R→Q2→C."""
        expected_sequence = [
            FractalStage.HOOK,
            FractalStage.PROMISE,
            FractalStage.QUESTION,
            FractalStage.ESCALATION,
            FractalStage.REWARD,
            FractalStage.NEW_QUESTION,
            FractalStage.CLIFFHANGER
        ]

        errors = []

        # Check we have exactly 9 beats
        if len(self.beats) != 9:
            errors.append(f"Expected 9 beats, got {len(self.beats)}")
            return False, errors

        # Check fractal sequence (first 7 beats must follow H→P→Q→E→R→Q2→C)
        for i, expected_stage in enumerate(expected_sequence):
            if i >= len(self.beats):
                break
            if self.beats[i].fractal_stage != expected_stage:
                errors.append(f"Beat {i+1} has fractal_stage {self.beats[i].fractal_stage}, expected {expected_stage}")

        # Check subversion is applied in Twist1 (beat 5, index 4)
        if len(self.beats) > 4:
            twist1 = self.beats[4]
            if not twist1.subversion_applied or twist1.subversion_applied.strip() == "":
                errors.append("Beat 5 (Twist1) must have subversion_applied specified")

        # Check continuity_block for beats 2-9
        for i in range(1, len(self.beats)):
            if not self.beats[i].continuity_block or self.beats[i].continuity_block.strip() == "":
                errors.append(f"Beat {i+1} missing continuity_block")

        # Check character_ids present in all beats
        for i, beat in enumerate(self.beats):
            if not beat.character_ids:
                errors.append(f"Beat {i+1} missing character_ids")

        # Check pattern_interrupt in all beats
        for i, beat in enumerate(self.beats):
            if not beat.pattern_interrupt:
                errors.append(f"Beat {i+1} missing pattern_interrupt")

        # Check curiosity_loop_planted in all beats
        for i, beat in enumerate(self.beats):
            if not beat.curiosity_loop_planted or beat.curiosity_loop_planted.strip() == "":
                errors.append(f"Beat {i+1} missing curiosity_loop_planted")

        return len(errors) == 0, errors


# Helper function to create a default beat structure
def create_beat_template(
    beat_id: str,
    beat_name: str,
    timestamp: str,
    fractal_stage: FractalStage,
    character_ids: List[str]
) -> BeatSchema:
    """Create a beat template with sensible defaults."""
    return BeatSchema(
        beat_id=beat_id,
        beat_name=beat_name,
        timestamp=timestamp,
        duration_sec=10.0,
        dialogue="",
        dialogue_delivery=DialogueDeliveryType.SUSURRO,
        micro_expression=MicroExpressionType.LABIO_TEMBLOROSO,
        dialogue_emotion=DialogueEmotionType.TENSION,
        action="",
        camera=BeatCamera(
            shot_type=ShotType.MCU,
            angle=CameraAngleType.EYE_LEVEL,
            movement=CameraMovementType.SLOW_DOLLY_IN,
            lens="85mm prime lens f/1.4",
            focus_pull="",
            composition="rule_of_thirds"
        ),
        sound=BeatSound(
            ambience="silence",
            sfx=[],
            music_cue={},
            silence_drop=False,
            voice=""
        ),
        character_emotion={},
        pattern_interrupt=PatternInterruptType.RACK_FOCUS,
        curiosity_loop_planted="",
        information_asymmetry=InformationAsymmetryType.AUDIENCE_KNOWS_MORE,
        subversion_applied="",
        fractal_stage=fractal_stage,
        continuity_block="",
        character_ids=character_ids,
        negative_prompt="",
        state_delta={},
        validation_rules=[]
    )


# Default beat sequence for 90-second episodes
DEFAULT_BEAT_SEQUENCE = [
    {"beat_name": "Hook", "timestamp": "0-10", "fractal_stage": FractalStage.HOOK},
    {"beat_name": "Context", "timestamp": "10-20", "fractal_stage": FractalStage.PROMISE},
    {"beat_name": "Problem", "timestamp": "20-30", "fractal_stage": FractalStage.QUESTION},
    {"beat_name": "Escalation", "timestamp": "30-40", "fractal_stage": FractalStage.ESCALATION},
    {"beat_name": "Twist1", "timestamp": "40-50", "fractal_stage": FractalStage.REWARD},
    {"beat_name": "Conflict2", "timestamp": "50-60", "fractal_stage": FractalStage.NEW_QUESTION},
    {"beat_name": "Revelation", "timestamp": "60-70", "fractal_stage": FractalStage.CLIFFHANGER},
    {"beat_name": "Cliffhanger", "timestamp": "70-80", "fractal_stage": FractalStage.CLIFFHANGER},
    {"beat_name": "CTA", "timestamp": "80-90", "fractal_stage": FractalStage.CLIFFHANGER},
]