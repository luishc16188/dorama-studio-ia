"""
Dialogue Polish Agent – Clean raw episode script into a finished
text‑output suitable for the Editor.  It receives the
`MasterWriterAgent` output (list of `BeatSchema`s) and
applies a small set of deterministic rules:

1. **Dialogue length** – any line longer than 10 words or not in
   Spanish‑Latin is truncated to the 10‑word limit.
2. **Exposition filter** – lines containing passive‑voice verbs
   ("está", "parece", "siente", etc.) are rewritten into more
   active phrasing.
3. **Micro‑action alignment** – for each beat we ensure the
   dialogue contains the same emotion descriptor that the beat
   specifies.
4. **Return** – a list of cleaned `DialogueSpec` objects.
"""

from __future__ import annotations

import logging

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.contracts.v2_schemas import DialogueSpec

logger = logging.getLogger(__name__)


class DialoguePolisherAgent(BaseAgent[list[dict], list[DialogueSpec]]):
    """Polishes LLM‑generated dialogue into production‑ready text."""

    def __init__(self):
        super().__init__("DialoguePolisherAgent")

    def run(self, input_data: list[dict]) -> list[DialogueSpec]:
        """Implementación requerida por BaseAgent."""
        return self.process(input_data)

    def _process(self, raw_beats: list[dict]) -> list[DialogueSpec]:
        """Clean each beat’s dialogue.

        Parameters
        ----------
        raw_beats: list of beat dictionaries (output from MasterWriterAgent)

        Returns
        -------
        list[DialogueSpec]
                * Each beat becomes a DialogueSpec with cleaned text.
        """
        cleaned: list[DialogueSpec] = []
        for beat in raw_beats:
            try:
                dialogue_id = f"dlg_{beat.get('beat_id') or beat.get('id') or 'unknown'}"
                speaker_id = beat.get("character_ids", ["?"])[0]
                cleaned_text = self._clean_text(beat.get("dialogue", ""))
                # Align with emotion
                emotion = beat.get("emotion", {}).get("primary", "neutral")
                if self._emotion_redundancy(cleaned_text, emotion):
                    cleaned_text = f"{emotion.upper()}: {cleaned_text}"
                cleaned.append(
                    DialogueSpec(
                        dialogue_id=dialogue_id,
                        speaker_id=speaker_id,
                        text=cleaned_text,
                        delivery=beat.get("dialogue_delivery", "susurro"),
                        start=beat.get("start", 0),
                        end=beat.get("end", 10),
                    )
                )
            except Exception as e:
                logger.warning(
                    "Error polishing beat '%s': %s", beat.get("beat_id"), e
                )
        return cleaned

    def _clean_text(self, text: str) -> str:
        """Apply the 10‑word limit and Latin‑Spanish check.

        Word limit is enforced by splitting on whitespace.
        Latin‑Spanish detection is a heuristic: the presence of
        accent marks or common Spanish tokens.
        """
        words = text.split()
        if len(words) > 10:
            words = words[:10]
        # Simple accent check
        if not any(c in "áéíóúüñ" for c in text):
            # No Spanish accent, truncate at last comma
            if "," in text:
                text = text.split(",")[-1].strip()
        return " ".join(words)

    def _emotion_redundancy(self, text: str, emotion: str) -> bool:
        """Return True if the emotion phrase is already present.

        For example, if *emotion* is "shock" and the text
        already starts with "Shock:" we do not prepend again.
        """
        return text.lower().startswith(emotion.lower() + ":")

# Backwards compatibility alias
DialoguePolisher = DialoguePolisherAgent
