"""
Acting & Motion Planner – Define la acción y la animación por beat.
Este agente toma los beats y genera `ActingSpec` y `MotionSpec`
con un conjunto mínimo de parámetros para la simulación.
"""

from __future__ import annotations

import logging

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.contracts.v2_schemas import ActingSpec, BeatSpec

logger = logging.getLogger(__name__)


class ActingMotionPlannerAgent(BaseAgent[list[BeatSpec], list[ActingSpec]]):
    """Plaza la actuación y la animación por beat."""

    def __init__(self):
        super().__init__("ActingMotionPlannerAgent")

    def run(self, input_data: list[BeatSpec]) -> list[ActingSpec]:
        """Implementación requerida por BaseAgent."""
        return self.process(input_data)

    def _process(self, beats: list[Any]) -> list[ActingSpec]:
        actions: list[ActingSpec] = []
        for beat in beats:
            try:
                # Handle both dict and object beats
                if isinstance(beat, dict):
                    action_text = beat.get("action", "")
                    character_ids = beat.get("character_ids", [])
                    beat_id = beat.get("beat_id", "unknown")
                else:
                    action_text = getattr(beat, "action", "")
                    character_ids = getattr(beat, "character_ids", [])
                    beat_id = getattr(beat, "beat_id", "unknown")

                action = ActingSpec(
                    facial_intent=action_text.split()[0] if action_text else "neutral",
                    gaze_target=character_ids[0] if character_ids else None,
                    blink_pattern="regular",
                    breathing="normal",
                    posture="standing",
                    gesture=action_text,
                    micro_expression="",
                )
                actions.append(action)
            except Exception as e:
                logger.warning("Error generando acción para beat %s: %s", beat_id, e)
        return actions

# Alias
Act = ActingMotionPlannerAgent
