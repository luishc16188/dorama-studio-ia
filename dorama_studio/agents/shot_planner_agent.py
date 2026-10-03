"""
Shot Planner Agent – Divide la secuencia de beats en shots.
El algoritmo busca parar los beats cuando el recurso visual cambia
(substitución de cámara, actor o acción) y crea un `ShotSpec` por
cada bloque.
"""

from __future__ import annotations

import logging

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.contracts.v2_schemas import BeatSpec, EpisodeSpecV2, ShotSpec

logger = logging.getLogger(__name__)


class ShotPlannerAgent(BaseAgent[EpisodeSpecV2, list[ShotSpec]]):
    """Crea la gramática de shots a partir de beats."""

    def __init__(self):
        super().__init__("ShotPlannerAgent")

    def run(self, input_data: EpisodeSpecV2) -> list[ShotSpec]:
        """Implementación requerida por BaseAgent."""
        return self.process(input_data)

    def _process(self, episode: Any) -> list[ShotSpec]:
        # Handle both EpisodeSpecV2 and dict input
        if isinstance(episode, dict):
            beats = episode.get("beats", [])
        else:
            beats = getattr(episode, "beats", [])

        shots: list[ShotSpec] = []
        current: list[BeatSpec] = []
        for beat in beats:
            # Si la cámara cambia o el beat es un cliffhanger, terminamos
            beat_camera = beat.get("camera", {}) if isinstance(beat, dict) else getattr(beat, "camera", {})
            current_camera = current[-1].get("camera", {}) if current and isinstance(current[-1], dict) else (getattr(current[-1], "camera", {}) if current else {})

            beat_narrative = beat.get("narrative_goal", "") if isinstance(beat, dict) else getattr(beat, "narrative_goal", "")

            if current and (
                beat_camera.get("shot_type") != current_camera.get("shot_type") or
                "cliff" in beat_narrative.lower()
            ):
                shots.append(self._build_shot(current))
                current = []
            current.append(beat)
        if current:
            shots.append(self._build_shot(current))
        return shots

    def _build_shot(self, beats: list[BeatSpec]) -> ShotSpec:
        start = beats[0].start
        end = beats[-1].end
        return ShotSpec(
            shot_id=f"shot_{start:.0f}_{end:.0f}",
            beat_id=beats[0].beat_id,
            start=start,
            end=end,
            characters=[],
            location_id="loc_01",
            visual_prompt_ast_id="prompt1",
            acting=None,
            camera=beats[0].camera,
            motion=beats[0].motion,
            continuity=None,
            audio=beats[0].audio,
            required_reference_ids=[],
            forbidden_elements=[],
        )

# Alias
ShotMaker = ShotPlannerAgent
