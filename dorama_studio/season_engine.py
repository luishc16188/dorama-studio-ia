"""Season Engine + 90-Second Episode Engine for DORAMA STUDIO IA V2.

Implements the **Season Engine** capable of generating a configurable
season (default 30 episodes) and the **MicroBeat Engine** that produces
~90‑second episode specs (EpisodeSpecV2) with a list of micro‑beats.

The module also exports helper functions used by later phases (Hook,
Retention, Director, etc.).
"""

from __future__ import annotations

from .episode_spec_v2 import EpisodeSpecV2, make_default_episode
from .memory import add_episode_to_season

# ---------------------------------------------------------------------------
# 1️⃣  MicroBeat Engine – produces a list of beats for a single episode
# ---------------------------------------------------------------------------

def generate_micro_beats(episode_id: str, title: str, n_beats: int = 5) -> list[Dict[str, Any]]:
    """Generate `n_beats` micro‑beats for the given episode.

    Each beat is a simple dict with an ID, type and description.  In a
    production setup this would be driven by the MicroBeat algorithm,
    but for V2 we provide a deterministic stub.
    """
    beats: list[Dict[str, Any]] = []
    for i in range(1, n_beats + 1):
        beats.append(
            {
                "beat_id": f"{episode_id}_b{i:02d}",
                "type": "beat",
                "description": f"Beat {i} de {title}",
                "duration_seconds": 18.0,  # approx. 90s / 5 beats ≈ 18s cada uno
            }
        )
    return beats


# ---------------------------------------------------------------------------
# 2️⃣  Season Engine – generates a full season of episodes
# ---------------------------------------------------------------------------

class SeasonEngine:
    """Orchestrates the creation of a complete season.

    Responsibilities
    -----------------
    * Decide the number of episodes (default 30).
    * For each episode, call the MicroBeat Engine to obtain beats.
    * Persist the season metadata via `SeasonMemory`.
    * Return a list of `EpisodeSpecV2` instances.
    """

    def __init__(self, season_number: int = 1, episodes: int | None = None) -> None:
        self.season_number: int = season_number
        self.episodes: int = episodes if episodes is not None else 30
        self._episode_specs: list[EpisodeSpecV2] = []

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------
    def build(self) -> list[EpisodeSpecV2]:
        """Build the entire season and return the list of EpisodeSpecV2."""
        self._episode_specs.clear()
        for idx in range(1, self.episodes + 1):
            episode_id = f"s{self.season_number:02d}e{idx:03d}"
            title = f"Episodio {idx} – Temporada {self.season_number}"
            # 1️⃣ generate micro‑beats (approx. 90 s total)
            beats = generate_micro_beats(episode_id, title, n_beats=5)
            # 2️⃣ build the EpisodeSpecV2
            episode = make_default_episode(episode_id, title)
            episode.beats = beats  # type: ignore[assignment]  # override default empty list
            # 3️⃣ persist minimal season memory
            add_episode_to_season(self.season_number, episode_id, title=title, beats_len=len(beats))
            self._episode_specs.append(episode)
        return self._episode_specs

    # -----------------------------------------------------------------
    # Helper to retrieve built episodes
    # -----------------------------------------------------------------
    def get_episodes(self) -> list[EpisodeSpecV2]:
        return list(self._episode_specs)


# ---------------------------------------------------------------------------
# 3️⃣  Module-level convenience function
# ---------------------------------------------------------------------------

def build_season(season_number: int = 1, episodes: int | None = None) -> list[EpisodeSpecV2]:
    """Quick one‑liner to create a season.

    Example
    -------
    >>> episodes = build_season(season_number=2, episodes=10)
    >>> len(episodes)   # 10
    10
    """
    engine = SeasonEngine(season_number=season_number, episodes=episodes)
    return engine.build()
