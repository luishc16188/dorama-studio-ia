"""Módulo principal que expone EpisodeSpecV2 y funciones auxiliares."""

from .agents.contract import EpisodeSpecV2 as EpisodeSpecV2Schema


def make_default_episode(episode_id: str, title: str) -> EpisodeSpecV2Schema:
    """Crea un episodio con beats vacíos y duración por defecto."""
    return EpisodeSpecV2Schema(
        episode_id=episode_id,
        title=title,
        beats=[],
        duration_seconds=90.0,
        season=1,
        episode_number=1,
    )
