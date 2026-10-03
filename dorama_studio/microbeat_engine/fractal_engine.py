"""
Fractal Engine - Fase 7
Implementa la Fórmula Fractal H→P→Q→E→R→Q2→C para micro-beats.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from .microbeat_schema import FractalStage


class FractalPattern(str, Enum):
    """Patrones fractales permitidos."""
    STANDARD = "standard"      # H→P→Q→E→R→Q2→C
    INVERTED = "inverted"      # C→Q2→R→E→Q→P→H (para flashbacks)
    LOOPED = "looped"          # H→P→Q→E→R→Q2→C→H (para cliffhangers)
    FRACTURED = "fractured"    # Secuencia no lineal (experimental)


class FractalEngine:
    """
    Motor que asegura que los micro-beats sigan la fórmula fractal.
    Cada beat de 10s contiene 4 micro-beats que deben seguir el patrón.
    """

    # Mapeo de beats padre a etapas fractales esperadas
    BEAT_TO_STAGE_MAP = {
        # Hook (0-10s): H H H H
        "hook": [FractalStage.H, FractalStage.H, FractalStage.H, FractalStage.H],

        # Context (10-20s): P P P P (también puede ser Q Q Q Q para algunos casos)
        "context": [FractalStage.P, FractalStage.P, FractalStage.P, FractalStage.P],

        # Problem (20-30s): Q Q Q Q
        "problem": [FractalStage.Q, FractalStage.Q, FractalStage.Q, FractalStage.Q],

        # Escalation (30-40s): E E E E
        "escalation": [FractalStage.E, FractalStage.E, FractalStage.E, FractalStage.E],

        # Twist1 (40-50s): R R R R
        "twist1": [FractalStage.R, FractalStage.R, FractalStage.R, FractalStage.R],

        # Conflict2 (50-60s): Q2 Q2 Q2 Q2
        "conflict2": [FractalStage.Q2, FractalStage.Q2, FractalStage.Q2, FractalStage.Q2],

        # Revelation (60-70s): R R R R (segunda revelación)
        "revelation": [FractalStage.R, FractalStage.R, FractalStage.R, FractalStage.R],

        # Cliffhanger (70-80s): C C C C
        "cliffhanger": [FractalStage.C, FractalStage.C, FractalStage.C, FractalStage.C],

        # CTA (80-90s): H H H H (reinicia el ciclo)
        "cta": [FractalStage.H, FractalStage.H, FractalStage.H, FractalStage.H],
    }

    @classmethod
    def get_expected_stages_for_beat(cls, beat_name: str) -> list[FractalStage]:
        """
        Obtiene las etapas fractales esperadas para un beat específico.

        Args:
            beat_name: Nombre del beat (hook, context, problem, etc.)

        Returns:
            Lista de 4 etapas fractales esperadas
        """
        beat_key = beat_name.lower().replace(" ", "")
        # Manejar variaciones como "twist_1" -> "twist1"
        beat_key = beat_key.replace("_", "")
        return cls.BEAT_TO_STAGE_MAP.get(beat_key, [FractalStage.H] * 4)

    @classmethod
    def validate_beat_sequence(cls, microbeats: list[Any]) -> tuple[bool, list[str]]:
        """
        Valida que una secuencia de 4 micro-beats siga el patrón fractal correcto.

        Args:
            microbeats: Lista de 4 micro-beats (deben estar ordenados por tiempo)

        Returns:
            Tuple (es_valido, lista_de_errores)
        """
        if len(microbeats) != 4:
            return False, [f"Se esperaban 4 micro-beats, se recibieron {len(microbeats)}"]

        # Asumir que el primer micro-beat indica el beat padre
        parent_beat = getattr(microbeats[0], 'parent_beat', 'unknown')
        expected_stages = cls.get_expected_stages_for_beat(parent_beat)

        errors = []
        for i, (mb, expected_stage) in enumerate(zip(microbeats, expected_stages)):
            actual_stage = getattr(mb, 'fractal_stage', None)
            if actual_stage != expected_stage:
                errors.append(
                    f"Micro-beat {i+1} ({getattr(mb, 'microbeat_type', 'unknown')}): "
                    f"etapa fractal incorrecta. Esperado: {expected_stage.value}, "
                    f"Encontrado: {actual_stage.value if actual_stage else 'None'}"
                )

        return len(errors) == 0, errors

    @classmethod
    def generate_fractal_sequence_for_episode(
        cls,
        total_beats: int = 9,
        pattern: FractalPattern = FractalPattern.STANDARD
    ) -> list[FractalStage]:
        """
        Genera la secuencia fractal completa para un episodio.

        Args:
            total_beats: Número de beats en el episodio (típicamente 9)
            pattern: Patrón fractal a usar

        Returns:
            Lista de etapas fractales (36 elementos para 9 beats)
        """
        if pattern == FractalPattern.STANDARD:
            # Secuencia estándar: H(4) + P(4) + Q(4) + E(4) + R(4) + Q2(4) + R(4) + C(4) + H(4)
            # Nota: Los beats son: Hook, Context, Problem, Escalation, Twist1, Conflict2, Revelation, Cliffhanger, CTA
            beat_sequence = [
                "hook",      # H H H H
                "context",   # P P P P
                "problem",   # Q Q Q Q
                "escalation",# E E E E
                "twist1",    # R R R R
                "conflict2", # Q2 Q2 Q2 Q2
                "revelation",# R R R R
                "cliffhanger",# C C C C
                "cta",       # H H H H
            ]

            sequence = []
            for beat_name in beat_sequence:
                expected = cls.get_expected_stages_for_beat(beat_name)
                sequence.extend(expected)
            return sequence

        elif pattern == FractalPattern.INVERTED:
            # Invertir toda la secuencia
            standard = cls.generate_fractal_sequence_for_episode(total_beats, FractalPattern.STANDARD)
            return list(reversed(standard))

        elif pattern == FractalPattern.LOOPED:
            # Standard + volver al inicio para crear loop
            standard = cls.generate_fractal_sequence_for_episode(total_beats, FractalPattern.STANDARD)
            # Agregar los primeros 4 elementos (H H H H) para conectar con el siguiente episodio
            return standard + standard[:4]

        else:  # FRACTURED
            # Para fracturado, retornamos la estándar pero se manejará diferente en validación
            return cls.generate_fractal_sequence_for_episode(total_beats, FractalPattern.STANDARD)
