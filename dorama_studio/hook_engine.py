"""Hook Engine for DORAMA STUDIO IA V2.

Implements the **Hook Engine** – the first of the three narrative‑retention
engines defined in Phase 6.  Its purpose is to generate an compelling
opening hook (the "gancho") for each episode, based on the episode’s
micro‑beats, character state and season context.

The engine is deliberately kept simple (stateless) so that it can be
called from the orchestration graph or from an HTTP endpoint later on.
"""

from __future__ import annotations

from typing import Any

from .memory import get_character_state


class HookEngine:
    """Generates a narrative hook for a given episode.

    The hook is a short textual summary (1‑2 sentences) that can be
    presented to the audience at the very beginning of the episode to
    capture attention and motivate continued viewing.
    """

    @staticmethod
    def generate(
        episode_id: str,
        title: str,
        *,
        character_name: str | None = None,
        n_beats: int = 5,
    ) -> dict[str, Any]:
        """Create a hook dict for the supplied episode.

        Parameters
        ----------
        episode_id: str
            Identifier of the episode (e.g. "s01e003").
        title: str
            Human‑readable title.
        character_name: str | None, optional
            If provided, the hook will reference the character’s current
            situation.
        n_beats: int, default 5
            Number of micro‑beats used as raw material.

        Returns
        -------
        dict with keys:
            - "hook_text": the generated hook sentence.
            - "sources": list of beat IDs that inspired the hook.
        """
        # Pull character state if a name was given
        char_ctx: dict[str, Any] = {}
        if character_name:
            cs = get_character_state(episode_id.split("e")[0][1:], character_name)  # season number
            char_ctx = {
                "name": cs.name,
                "role": cs.role,
                "current_episode": cs.current_episode,
            }

        # Build a minimal description from the beats (we don't have the beats
        # here; in a real implementation they'd be passed in or fetched)
        beat_ids = [f"b{i:02d}" for i in range(1, n_beats + 1)]

        # Simple template-driven hook
        if character_name:
            hook_text = (
                f"En {title}, {character_name} se enfrenta a un giro inesperado "
                f"mientras {char_ctx.get('role', 'cumple su papel')}."
            )
        else:
            hook_text = f"En {title}, ocurre un evento que cambiará todo."

        return {
            "hook_text": hook_text,
            "sources": beat_ids,
            "episode_id": episode_id,
        }
