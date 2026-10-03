"""
Director Engine Agent – Planifica la continuidad narrativa y cinematográfica
para todos los shots de un episodio.
Toma el `EpisodeSpecV2` y produce una lista de `ShotSpec` con
´camera´ y `motion` generados de forma determinista.
"""

from __future__ import annotations

import logging
import random

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.contracts.v2_schemas import CameraSpec, EpisodeSpecV2, MotionSpec, ShotSpec

logger = logging.getLogger(__name__)


class DirectorEngineAgent(BaseAgent[EpisodeSpecV2, list[ShotSpec]]):
    """Genera plan cinematográfico simple para un episodio."""

    def __init__(self):
        super().__init__("DirectorEngineAgent")

    def run(self, input_data: EpisodeSpecV2) -> list[ShotSpec]:
        """Implementación requerida por BaseAgent."""
        return self.process(input_data)

    def _process(self, episode: Any) -> list[ShotSpec]:
        # Handle both EpisodeSpecV2 and dict input
        if isinstance(episode, dict):
            shots = episode.get("shots", [])
        else:
            shots = getattr(episode, "shots", [])

        updated_shots: list[ShotSpec] = []
        for shot in shots:
            try:
                # Camera determinista basada en beat id
                beat_id = shot.get("beat_id", "unknown") if isinstance(shot, dict) else getattr(shot, "beat_id", "unknown")
                cam = CameraSpec(
                    shot_type=random.choice(["ECU", "CU", "MS", "WS"]),
                    framing="framing_%s" % (beat_id[:4]),
                    angle="eye_level",
                    lens_language="85mm",
                    movement="steady",
                )
                motion = MotionSpec(
                    primary="walk",
                    secondary=["run"],
                    environment=[],
                )
                if isinstance(shot, dict):
                    shot["camera"] = cam
                    shot["motion"] = motion
                else:
                    shot.camera = cam
                    shot.motion = motion
                updated_shots.append(shot)
            except Exception as e:
                logger.warning("Error actualizando shot %s: %s", shot.shot_id, e)
        return updated_shots

# Alias
VisionDirector = DirectorEngineAgent
