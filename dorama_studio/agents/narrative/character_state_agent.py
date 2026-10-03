"""
Character State Agent – Actualiza los estados mutables de los personajes a lo largo de un episodio.
El agente recibe un EpisodeSpecV2 y un conjunto de eventos de la producción
(por ejemplo, decisiones de actuación o cambios de vestuario) y crea o actualiza
objetos CharacterState que se inscriben en la base de datos de CreativePrint.
"""

from __future__ import annotations

import logging

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.contracts.v2_schemas import CharacterState, EpisodeSpecV2

logger = logging.getLogger(__name__)


class CharacterStateAgent(BaseAgent[EpisodeSpecV2, list[CharacterState]]):
    """Genera estados de personajes por episodio y shot."""

    def __init__(self):
        super().__init__("CharacterStateAgent")

    def run(self, input_data: EpisodeSpecV2) -> list[CharacterState]:
        """Implementación requerida por BaseAgent."""
        return self.process(input_data)

    def _process(self, episode: Any) -> list[CharacterState]:
        # Handle both EpisodeSpecV2 and dict input
        if isinstance(episode, dict):
            beats = episode.get("beats", [])
        else:
            beats = getattr(episode, "beats", [])

        states: list[CharacterState] = []
        for beat in beats:
            try:
                # Handle both dict and object beats
                if isinstance(beat, dict):
                    beat_id = beat.get("beat_id", "unknown")
                    chars = beat.get("character_ids", [])
                else:
                    beat_id = getattr(beat, "beat_id", "unknown")
                    chars = getattr(beat, "character_ids", [])

                for cid in chars:
                    state = CharacterState(
                        artifact_id=f"art_{cid}_{beat_id[:8]}",
                        artifact_type="character_bible",
                        project_id=episode.get("project_id", "unknown") if isinstance(episode, dict) else getattr(episode, "project_id", "unknown"),
                        season_id=episode.get("season_id", "unknown") if isinstance(episode, dict) else getattr(episode, "season_id", "unknown"),
                        episode_id=str(episode.get("episode_number", 1)) if isinstance(episode, dict) else str(getattr(episode, "episode_number", 1)),
                        character_id=cid,
                        identity_ref="",  # placeholder, would link to identity artifact
                        wardrobe="",
                        injuries={},
                        wetness=False,
                        blood={},
                        makeup="",
                        fatigue=0.0,
                        props_held=[],
                        location="",
                        emotion="neutral",
                        created_by="CharacterStateAgent",
                    )
                    states.append(state)
            except Exception as e:
                logger.warning("Error generando estado para beat %s: %s", beat_id, e)
        return states


# Alias for backward compatibility
CharacterStateManager = CharacterStateAgent
