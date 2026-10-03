"""
MicroBeat Schema - Fase 7
Define micro-beats de 2.5s (4 micro-beats por beat de 10s).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class MicroBeatType(str, Enum):
    """Tipos de micro-beats dentro de un beat de 10s."""
    # Hook micro-beats (0-10s)
    VISUAL_SHOCK = "visual_shock"           # 0-2.5s: Imposible visual + sub-bass
    QUESTION_PLANT = "question_plant"       # 2.5-5s: Pregunta intrigante
    PROMISE_SETUP = "promise_setup"         # 5-7.5s: Promesa de payoff
    CHARACTER_INTRO = "character_intro"     # 7.5-10s: Intro protagonista

    # Context micro-beats (10-20s)
    WORLD_RULE = "world_rule"               # 10-12.5s: Regla del mundo
    STATUS_QUO = "status_quo"               # 12.5-15s: Normalidad
    INCITING_HINT = "inciting_hint"         # 15-17.5s: Pista del incidente
    TENSION_BUILD = "tension_build"         # 17.5-20s: Tensión ascendente

    # Problem micro-beats (20-30s)
    INCITING_EVENT = "inciting_event"       # 20-22.5s: Incidente disruptivo
    REACTION_SHOCK = "reaction_shock"       # 22.5-25s: Reacción visceral
    STAKES_CLEAR = "stakes_clear"           # 25-27.5s: Stakes claros
    GOAL_LOCK = "goal_lock"                 # 27.5-30s: Objetivo fijado

    # Escalation micro-beats (30-40s)
    PRESSURE_RISE = "pressure_rise"         # 30-32.5s: Presión sube
    COMPLICATION = "complication"           # 32.5-35s: Complicación
    FAILED_ATTEMPT = "failed_attempt"       # 35-37.5s: Intento fallido
    DESPERATION = "desperation"             # 37.5-40s: Desesperación

    # Twist1 micro-beats (40-50s)
    REVELATION = "revelation"               # 40-42.5s: Revelación cambia todo
    RECONTEXT = "recontext"                 # 42.5-45s: Recontextualización
    NEW_DIRECTION = "new_direction"         # 45-47.5s: Nueva dirección
    SUBVERSION = "subversion"               # 47.5-50s: Tropo subvertido

    # Conflict2 micro-beats (50-60s)
    NEW_THREAT = "new_threat"               # 50-52.5s: Nueva amenaza
    ALLIANCE_TEST = "alliance_test"         # 52.5-55s: Alianza probada
    BETRAYAL_HINT = "betrayal_hint"         # 55-57.5s: Pista de traición
    CORNERED = "cornered"                   # 57.5-60s: Acorralado

    # Revelation micro-beats (60-70s)
    TRUTH_BOMB = "truth_bomb"               # 60-62.5s: Verdad impactante
    EMOTIONAL_PAYOFF = "emotional_payoff"   # 62.5-65s: Catarsis emocional
    CHARACTER_SHIFT = "character_shift"     # 65-67.5s: Cambio personaje
    CLARITY = "clarity"                     # 67.5-70s: Claridad

    # Cliffhanger micro-beats (70-80s)
    IMPOSSIBLE_CHOICE = "impossible_choice" # 70-72.5s: Elección imposible
    VISUAL_PUNCH = "visual_punch"           # 72.5-75s: Visual impactante
    SUB_BASS_DROP = "sub_bass_drop"         # 75-77.5s: Sub-bass drop
    CUT_OFF = "cut_off"                     # 77.5-80s: Corte en medio de frase

    # CTA micro-beats (80-90s)
    TRIBAL_QUESTION = "tribal_question"     # 80-82.5s: Pregunta tribal
    SIDE_CHOICE = "side_choice"             # 82.5-85s: Elegir bando
    LOOP_NEXT = "loop_next"                 # 85-87.5s: Loop a siguiente ep
    BRAND_HOOK = "brand_hook"               # 87.5-90s: Hook de marca


class FractalStage(str, Enum):
    """Etapas de la Fórmula Fractal H→P→Q→E→R→Q2→C"""
    H = "H"      # Hook - Gancho inicial
    P = "P"      # Problem - Problema planteado
    Q = "Q"      # Question - Pregunta intrigante
    E = "E"      # Escalation - Escalada
    R = "R"      # Revelation - Revelación
    Q2 = "Q2"    # Question 2 - Segunda pregunta
    C = "C"      # Cliffhanger - Gancho final


class FractalPattern(str, Enum):
    """Patrones fractales permitidos."""
    STANDARD = "standard"      # H→P→Q→E→R→Q2→C
    INVERTED = "inverted"      # C→Q2→R→E→Q→P→H (para flashbacks)
    LOOPED = "looped"          # H→P→Q→E→R→Q2→C→H (para cliffhangers)
    FRACTURED = "fractured"    # Secuencia no lineal (experimental)


class MicroBeat(BaseModel):
    """Un micro-beat de 2.5 segundos."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    # Identificación
    microbeat_id: str
    parent_beat: str          # Nombre del beat padre (hook, context, problem, etc.)
    sequence_number: int      # 1-4 dentro del beat
    global_sequence: int      # 1-36 en el episodio completo

    # Timing exacto
    start_sec: float          # Ej: 0.0, 2.5, 5.0, 7.5
    end_sec: float            # Ej: 2.5, 5.0, 7.5, 10.0
    duration_sec: float = 2.5

    # Tipo y etapa fractal
    microbeat_type: MicroBeatType
    fractal_stage: FractalStage

    # Contenido narrativo
    action: str               # 1 verbo dominante observable
    dialogue: str             # Máx 10 palabras español latino
    dialogue_delivery: str    # susurro|grito|quebrado|frío|irónico|susurrado_amenazante|voz_quebrada
    micro_expression: str     # labio_tembloroso|mandíbula_apretada|ojos_secos|pupilas_dilatadas|respiración_contenida|ceja_arqueada|sonrisa_tensa

    # Especificaciones técnicas (forenses)
    camera: dict[str, Any] = Field(default_factory=dict)
    # shot_type, angle, movement, lens, focus_pull, composition

    sound: dict[str, Any] = Field(default_factory=dict)
    # ambience, sfx[], music_cue{}, silence_drop, voice

    lighting: str = ""        # Key/fill/back con Kelvin
    color_grade: str = ""     # Esquema + sombras/medios/luces
    texture: str = ""         # 35mm grain, digital clean, etc.

    # Continuity
    continuity_block: str = ""  # Iluminación + Estado Sujeto + Espacio + Objetos Clave
    character_ids: list[str] = Field(default_factory=list)

    # Pattern interrupt (obligatorio cada 2.5s)
    pattern_interrupt: str = ""  # zoom_punch|whip_pan|smash_cut|dead_silence|hard_beat_drop|rack_focus

    # Curiosity loop
    curiosity_loop_planted: str = ""

    # Information asymmetry
    information_asymmetry: Literal[
        "audience_knows_more",
        "audience_knows_less",
        "audience_knows_equal",
        "audience_decides"
    ] = "audience_knows_more"

    # Subversión (solo en Twist1)
    subversion_applied: str = ""

    # Negative prompt (anti-bloat)
    negative_prompt: str = "masterpiece, 4k, 8k, trending, best quality, ultra-detailed, cinematic, beautiful"

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EpisodeMicroBeatPlan(BaseModel):
    """Plan completo de micro-beats para un episodio de 90s."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid", arbitrary_types_allowed=True)

    episode_id: str
    episode_number: int
    total_microbeats: int = 36  # 9 beats × 4 micro-beats

    # Micro-beats organizados por beat padre
    microbeats_by_beat: dict[str, list[MicroBeat]] = Field(default_factory=dict)
    # Lista plana ordenada
    microbeats_sequence: list[MicroBeat] = Field(default_factory=list)

    # Validación fractal
    fractal_sequence_valid: bool = False
    fractal_violations: list[str] = Field(default_factory=list)

    # Quality Gate
    quality_score: float = 0.0
    quality_passed: bool = False
    quality_breakdown: dict[str, Any] = Field(default_factory=dict)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def get_microbeats_for_beat(self, beat_name: str) -> list[MicroBeat]:
        """Obtiene los 4 micro-beats de un beat específico."""
        return self.microbeats_by_beat.get(beat_name.lower(), [])

    def get_microbeat_at_time(self, time_sec: float) -> MicroBeat | None:
        """Obtiene el micro-beat activo en un segundo específico."""
        for mb in self.microbeats_sequence:
            if mb.start_sec <= time_sec < mb.end_sec:
                return mb
        return None

    def validate_fractal_sequence(self) -> bool:
        """Valida que la secuencia fractal H→P→Q→E→R→Q2→C se cumpla."""
        expected_sequence = [
            FractalStage.H, FractalStage.H, FractalStage.H, FractalStage.H,  # Hook (4)
            FractalStage.P, FractalStage.P, FractalStage.P, FractalStage.P,  # Context/Problem
            FractalStage.Q, FractalStage.Q, FractalStage.Q, FractalStage.Q,  # Problem/Escalation
            FractalStage.E, FractalStage.E, FractalStage.E, FractalStage.E,  # Escalation/Twist1
            FractalStage.R, FractalStage.R, FractalStage.R, FractalStage.R,  # Conflict2/Revelation
            FractalStage.Q2, FractalStage.Q2, FractalStage.Q2, FractalStage.Q2,  # Revelation/Cliffhanger
            FractalStage.C, FractalStage.C, FractalStage.C, FractalStage.C,  # Cliffhanger/CTA
        ]

        violations = []
        for i, mb in enumerate(self.microbeats_sequence):
            if i < len(expected_sequence):
                expected = expected_sequence[i]
                if mb.fractal_stage != expected:
                    violations.append(
                        f"Micro-beat {i+1} ({mb.microbeat_type.value}): "
                        f"esperado {expected.value}, encontrado {mb.fractal_stage.value}"
                    )

        self.fractal_violations = violations
        self.fractal_sequence_valid = len(violations) == 0
        return self.fractal_sequence_valid
