"""
MicroBeat Engine - Fase 7
Motor principal que genera y valida micro-beats de 2.5s dentro de beats de 10s.
Implementa Fórmula Fractal H→P→Q→E→R→Q2→C y Quality Gate 100pts (15 dims).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .fractal_engine import FractalEngine
from .microbeat_schema import EpisodeMicroBeatPlan, FractalStage, MicroBeat, MicroBeatType
from .quality_gate import QualityGate


class MicroBeatEngine:
    """
    Motor principal de micro-beats de Fase 7.
    Genera planes de micro-beats para episodios de 90s basados en la estructura de 9 beats.
    """

    def __init__(self):
        self.fractal_engine = FractalEngine()
        self.quality_gate = QualityGate()

    def _process(self, validated_input: Any) -> Any:
        """
        Placeholder _process method for compatibility with agent interface tests.
        In practice, use create_microbeat_plan_from_episode_arc or other specific methods.
        """
        return validated_input

    def __init__(self):
        self.fractal_engine = FractalEngine()
        self.quality_gate = QualityGate()

    def create_microbeat_plan_from_episode_arc(
        self,
        episode_arc: Any,  # EpisodeArc from fase 6
        episode_number: int
    ) -> EpisodeMicroBeatPlan:
        """
        Crea un plan de micro-beats basado en un EpisodeArc existente.

        Args:
            episode_arc: EpisodeArc object from fase 6
            episode_number: Número del episodio (1-40)

        Returns:
            EpisodeMicroBeatPlan con los 36 micro-beats
        """
        plan = EpisodeMicroBeatPlan(
            episode_id=f"e{episode_number:02d}",
            episode_number=episode_number
        )

        # Mapeo de beats de episodio a tipos de micro-beats
        beat_to_microbeat_map = {
            "hook": [
                (MicroBeatType.VISUAL_SHOCK, "0-2.5s", 0.0, 2.5),
                (MicroBeatType.QUESTION_PLANT, "2.5-5s", 2.5, 5.0),
                (MicroBeatType.PROMISE_SETUP, "5-7.5s", 5.0, 7.5),
                (MicroBeatType.CHARACTER_INTRO, "7.5-10s", 7.5, 10.0),
            ],
            "context": [
                (MicroBeatType.WORLD_RULE, "10-12.5s", 10.0, 12.5),
                (MicroBeatType.STATUS_QUO, "12.5-15s", 12.5, 15.0),
                (MicroBeatType.INCITING_HINT, "15-17.5s", 15.0, 17.5),
                (MicroBeatType.TENSION_BUILD, "17.5-20s", 17.5, 20.0),
            ],
            "problem": [
                (MicroBeatType.INCITING_EVENT, "20-22.5s", 20.0, 22.5),
                (MicroBeatType.REACTION_SHOCK, "22.5-25s", 22.5, 25.0),
                (MicroBeatType.STAKES_CLEAR, "25-27.5s", 25.0, 27.5),
                (MicroBeatType.GOAL_LOCK, "27.5-30s", 27.5, 30.0),
            ],
            "escalation": [
                (MicroBeatType.PRESSURE_RISE, "30-32.5s", 30.0, 32.5),
                (MicroBeatType.COMPLICATION, "32.5-35s", 32.5, 35.0),
                (MicroBeatType.FAILED_ATTEMPT, "35-37.5s", 35.0, 37.5),
                (MicroBeatType.DESPERATION, "37.5-40s", 37.5, 40.0),
            ],
            "twist1": [
                (MicroBeatType.REVELATION, "40-42.5s", 40.0, 42.5),
                (MicroBeatType.RECONTEXT, "42.5-45s", 42.5, 45.0),
                (MicroBeatType.NEW_DIRECTION, "45-47.5s", 45.0, 47.5),
                (MicroBeatType.SUBVERSION, "47.5-50s", 47.5, 50.0),
            ],
            "conflict2": [
                (MicroBeatType.NEW_THREAT, "50-52.5s", 50.0, 52.5),
                (MicroBeatType.ALLIANCE_TEST, "52.5-55s", 52.5, 55.0),
                (MicroBeatType.BETRAYAL_HINT, "55-57.5s", 55.0, 57.5),
                (MicroBeatType.CORNERED, "57.5-60s", 57.5, 60.0),
            ],
            "revelation": [
                (MicroBeatType.TRUTH_BOMB, "60-62.5s", 60.0, 62.5),
                (MicroBeatType.EMOTIONAL_PAYOFF, "62.5-65s", 62.5, 65.0),
                (MicroBeatType.CHARACTER_SHIFT, "65-67.5s", 65.0, 67.5),
                (MicroBeatType.CLARITY, "67.5-70s", 67.5, 70.0),
            ],
            "cliffhanger": [
                (MicroBeatType.IMPOSSIBLE_CHOICE, "70-72.5s", 70.0, 72.5),
                (MicroBeatType.VISUAL_PUNCH, "72.5-75s", 72.5, 75.0),
                (MicroBeatType.SUB_BASS_DROP, "75-77.5s", 75.0, 77.5),
                (MicroBeatType.CUT_OFF, "77.5-80s", 77.5, 80.0),
            ],
            "cta": [
                (MicroBeatType.TRIBAL_QUESTION, "80-82.5s", 80.0, 82.5),
                (MicroBeatType.SIDE_CHOICE, "82.5-85s", 82.5, 85.0),
                (MicroBeatType.LOOP_NEXT, "85-87.5s", 85.0, 87.5),
                (MicroBeatType.BRAND_HOOK, "87.5-90s", 87.5, 90.0),
            ]
        }

        # Generar micro-beats para cada beat
        all_microbeats = []
        global_sequence = 1

        for beat_name, microbeat_specs in beat_to_microbeat_map.items():
            beat_microbeats = []
            for i, (mb_type, timestamp, start_sec, end_sec) in enumerate(microbeat_specs):
                # Determinar etapa fractal basada en el beat y posición
                expected_stages = self.fractal_engine.get_expected_stages_for_beat(beat_name)
                fractal_stage = expected_stages[i] if i < len(expected_stages) else FractalStage.H

                microbeat = MicroBeat(
                    microbeat_id=f"mb{episode_number:02d}_{beat_name}_{i+1:02d}",
                    parent_beat=beat_name,
                    sequence_number=i+1,
                    global_sequence=global_sequence,
                    start_sec=start_sec,
                    end_sec=end_sec,
                    duration_sec=2.5,
                    microbeat_type=mb_type,
                    fractal_stage=fractal_stage,
                    # Valores por defecto que pueden ser sobrescritos por LLM o personalización
                    action=f"Character performs dominant observable action for {mb_type.value}",
                    dialogue=f"Sample dialogue for {mb_type.value} in beat {beat_name}",
                    dialogue_delivery="susurro",  # Valor por defecto
                    micro_expression="mandíbula_apretada",  # Valor por defecto
                    camera={},
                    sound={},
                    lighting="",
                    color_grade="",
                    texture="",
                    continuity_block=f"Initial state: Establishing shot for {beat_name}",
                    character_ids=["CHAR_001"],  # Valor por defecto
                    pattern_interrupt="zoom_punch" if i % 2 == 0 else "whip_pan",
                    curiosity_loop_planted=f"What is the true nature of the {beat_name}?",
                    information_asymmetry="audience_knows_more",
                    subversion_applied="",
                    negative_prompt="masterpiece, 4k, 8k, trending, best quality, ultra-detailed, cinematic, beautiful"
                )

                beat_microbeats.append(microbeat)
                all_microbeats.append(microbeat)
                global_sequence += 1

            plan.microbeats_by_beat[beat_name] = beat_microbeats

        plan.microbeats_sequence = all_microbeats

        # Validar secuencia fractal
        plan.validate_fractal_sequence()

        # Aplicar Quality Gate
        plan.quality_score, plan.quality_passed, plan.quality_breakdown = \
            self.quality_gate.evaluate_episode(all_microbeats)

        plan.updated_at = datetime.utcnow()

        return plan

    def validate_microbeat_plan(self, plan: EpisodeMicroBeatPlan) -> dict[str, Any]:
        """
        Valida un plan de micro-beats existente y retorna resultados detallados.

        Args:
            plan: EpisodeMicroBeatPlan to validate

        Returns:
            Diccionario con resultados de validación
        """
        # Validar secuencia fractal
        fractal_valid = plan.validate_fractal_sequence()

        # Aplicar Quality Gate (re-evaluar por si cambió algo)
        quality_score, quality_passed, quality_breakdown = \
            self.quality_gate.evaluate_episode(plan.microbeats_sequence)

        # Actualizar el plan con los nuevos resultados
        plan.quality_score = quality_score
        plan.quality_passed = quality_passed
        plan.quality_breakdown = quality_breakdown
        plan.updated_at = datetime.utcnow()

        return {
            "fractal_sequence_valid": fractal_valid,
            "fractal_violations": plan.fractal_violations,
            "quality_score": quality_score,
            "quality_passed": quality_passed,
            "quality_breakdown": quality_breakdown,
            "total_microbeats": len(plan.microbeats_sequence),
            "expected_microbeats": 36,
            "microbeats_by_beat_count": {
                beat: len(mbs) for beat, mbs in plan.microbeats_by_beat.items()
            }
        }

    def customize_microbeat(
        self,
        plan: EpisodeMicroBeatPlan,
        microbeat_id: str,
        updates: dict[str, Any]
    ) -> bool:
        """
        Personaliza un micro-beat específico en el plan.

        Args:
            plan: EpisodeMicroBeatPlan to modify
            microbeat_id: ID del micro-beat a personalizar
            updates: Diccionario con los campos a actualizar

        Returns:
            True si se encontró y actualizó el micro-beat, False si no
        """
        for mb in plan.microbeats_sequence:
            if mb.microbeat_id == microbeat_id:
                # Actualizar los campos especificados
                for key, value in updates.items():
                    if hasattr(mb, key):
                        setattr(mb, key, value)

                # Re-validar todo el plan ya que un cambio puede afectar múltiples dimensiones
                plan.quality_score, plan.quality_passed, plan.quality_breakdown = \
                    self.quality_gate.evaluate_episode(plan.microbeats_sequence)

                # Re-validar secuencia fractal (aunque cambiar un micro-beat individual
                # probablemente no afecte la secuencia fractal a menos que se cambie fractal_stage)
                plan.validate_fractal_sequence()

                plan.updated_at = datetime.utcnow()
                return True
        return False

    def get_microbeat_at_timestamp(
        self,
        plan: EpisodeMicroBeatPlan,
        time_sec: float
    ) -> MicroBeat | None:
        """
        Obtiene el micro-beat activo en un segundo específico del episodio.

        Args:
            plan: EpisodeMicroBeatPlan to search
            time_sec: Tiempo en segundos (0.0-90.0)

        Returns:
            MicroBeat activo en ese tiempo, o None si está fuera de rango
        """
        if time_sec < 0.0 or time_sec >= 90.0:
            return None

        for mb in plan.microbeats_sequence:
            if mb.start_sec <= time_sec < mb.end_sec:
                return mb
        return None

    def export_plan_for_production(self, plan: EpisodeMicroBeatPlan) -> dict[str, Any]:
        """
        Exporta el plan de micro-beats en formato listo para producción.

        Args:
            plan: EpisodeMicroBeatPlan to export

        Returns:
            Diccionario con todos los datos necesarios para producción
        """
        return {
            "episode_info": {
                "episode_id": plan.episode_id,
                "episode_number": plan.episode_number,
                "total_duration_sec": 90.0,
                "total_microbeats": plan.total_microbeats
            },
            "microbeats": [
                {
                    "microbeat_id": mb.microbeat_id,
                    "parent_beat": mb.parent_beat,
                    "sequence_number": mb.sequence_number,
                    "global_sequence": mb.global_sequence,
                    "timing": {
                        "start_sec": mb.start_sec,
                        "end_sec": mb.end_sec,
                        "duration_sec": mb.duration_sec
                    },
                    "type": {
                        "microbeat_type": mb.microbeat_type.value,
                        "fractal_stage": mb.fractal_stage.value
                    },
                    "content": {
                        "action": mb.action,
                        "dialogue": mb.dialogue,
                        "dialogue_delivery": mb.dialogue_delivery,
                        "micro_expression": mb.micro_expression
                    },
                    "technical": {
                        "camera": mb.camera,
                        "sound": mb.sound,
                        "lighting": mb.lighting,
                        "color_grade": mb.color_grade,
                        "texture": mb.texture
                    },
                    "continuity": {
                        "continuity_block": mb.continuity_block,
                        "character_ids": mb.character_ids,
                        "pattern_interrupt": mb.pattern_interrupt,
                        "curiosity_loop_planted": mb.curiosity_loop_planted,
                        "information_asymmetry": mb.information_asymmetry,
                        "subversion_applied": mb.subversion_applied
                    },
                    "quality": {
                        "negative_prompt": mb.negative_prompt
                    }
                }
                for mb in plan.microbeats_sequence
            ],
            "quality_assessment": {
                "score": plan.quality_score,
                "passed": plan.quality_passed,
                "breakdown": plan.quality_breakdown
            },
            "fractal_validation": {
                "is_valid": plan.fractal_sequence_valid,
                "violations": plan.fractal_violations
            },
            "metadata": {
                "created_at": plan.created_at.isoformat() if plan.created_at else None,
                "updated_at": plan.updated_at.isoformat() if plan.updated_at else None
            }
        }
