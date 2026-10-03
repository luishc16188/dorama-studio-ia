"""Season Memory + Character State + Continuity for DORAMA STUDIO IA V2.

Provides persistent storage (JSON files) for season-level metadata
and per‑character state, plus helper functions to ensure continuity
across episodes.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# 1️⃣  Helper to obtain a stable file path per season/character
# ---------------------------------------------------------------------------

SEASONS_DIR = Path("season_memory")
SEASONS_DIR.mkdir(exist_ok=True)


def _season_path(season: int) -> Path:
    """Return the JSON file path for a given season number."""
    return SEASONS_DIR / f"season_{season:02d}.json"


def _character_path(season: int, character_name: str) -> Path:
    """Return the JSON file path for a given character within a season."""
    # Normalize the name to avoid illegal filename characters
    safe = "".join(c if c.isalnum() or c in "_-" else "_" for c in character_name)
    return SEASONS_DIR / f"season_{season:02d}_{safe}.json"


# ---------------------------------------------------------------------------
# 2️⃣  Season‑level memory
# ---------------------------------------------------------------------------

class SeasonMemory(BaseModel):
    """Metadata stored for an entire season."""

    season: int
    total_episodes: int = 0
    episodes: dict[str, dict[str, Any]] = {}  # episode_id → basic stats
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    # ---------------------------------------------------------------------
    # Persistence
    # ---------------------------------------------------------------------
    def save(self) -> None:
        """Write the season memory to disk."""
        path = _season_path(self.season)
        path.write_text(self.model_dump_json(indent=2), encoding="utf-8")

    @classmethod
    def load(cls, season: int) -> SeasonMemory | None:
        """Load season memory from disk, or return None if not exists."""
        path = _season_path(season)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**data)


# ---------------------------------------------------------------------------
# 3️⃣  Character‑level state
# ---------------------------------------------------------------------------

class CharacterState(BaseModel):
    """State that is tracked for a single character within a season."""

    name: str
    # Example free‑form fields that can be extended later:
    role: str = "unknown"
    current_episode: str | None = None
    last_seen_beats: list[str] = Field(default_factory=list)
    narrative_arc_progress: float = 0.0  # 0.0 → 1.0
    traits: dict[str, Any] = Field(default_factory=dict)

    # -----------------------------------------------------------------
    # Persistence
    # -----------------------------------------------------------------
    def save(self, season: int) -> None:
        """Persist this character's state for the given season."""
        path = _character_path(season, self.name)
        path.write_text(self.model_dump_json(indent=2), encoding="utf-8")

    @classmethod
    def load(cls, season: int, character_name: str) -> CharacterState | None:
        """Load a character's state, or return None if not present."""
        path = _character_path(season, character_name)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**data)


# ---------------------------------------------------------------------------
# 4️⃣  Convenience helpers
# ---------------------------------------------------------------------------

def add_episode_to_season(season: int, episode_id: str, **kwargs: Any) -> None:
    """Increment the episode counter and store minimal metadata."""
    mem = SeasonMemory.load(season) or SeasonMemory(season=season)
    mem.episodes[episode_id] = kwargs
    mem.total_episodes = len(mem.episodes)
    mem.last_updated = datetime.utcnow()
    mem.save()


def get_character_state(season: int, character_name: str) -> CharacterState:
    """Return the character state, creating a default one if absent."""
    state = CharacterState.load(season, character_name)
    if state is None:
        state = CharacterState(name=character_name)
        state.save(season)
    return state
